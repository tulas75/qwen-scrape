import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Set, List, Tuple
import logging
import random
import time
import xml.etree.ElementTree as ET
from markdownify import markdownify as md  # Add markdownify import
from src.config.settings import config

logger = logging.getLogger(__name__)

# More realistic browser headers with Linux user agents to simulate real browser behavior
BROWSER_HEADERS = [
    {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    },
    {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    },
    {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
]


class WebScraper:
    def __init__(self, max_depth: int = None, page_limit: int = None):
        self.max_depth = max_depth or config.max_depth
        self.page_limit = page_limit or config.page_limit
        self.visited_urls: Set[str] = set()
        self.session = requests.Session()
        # Use a random browser header to simulate different browsers
        self.session.headers.update(random.choice(BROWSER_HEADERS))
        # Add common headers to simulate a real browser
        self.session.headers.update({
            "Cache-Control": "max-age=0",
            "Sec-Ch-Ua": '" Not A;Brand";v="99", "Chromium";v="90"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
        })
        # Configure session to handle redirects and retries
        self.session.max_redirects = 10

    def parse_sitemap(self, sitemap_url: str) -> List[str]:
        """
        Parse a sitemap.xml file and extract all URLs.
        
        Args:
            sitemap_url: URL to the sitemap.xml file
            
        Returns:
            List of URLs found in the sitemap
        """
        urls = []
        try:
            logger.info(f"Parsing sitemap: {sitemap_url}")
            response = self.session.get(sitemap_url, timeout=15)
            response.raise_for_status()
            
            # Parse XML content
            root = ET.fromstring(response.content)
            
            # Handle sitemap index files (sitemaps that reference other sitemaps)
            if root.tag.endswith('sitemapindex'):
                sitemap_urls = []
                for sitemap_elem in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap"):
                    loc_elem = sitemap_elem.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
                    if loc_elem is not None and loc_elem.text:
                        sitemap_urls.append(loc_elem.text)
                
                # Recursively parse each sitemap
                for sitemap_url in sitemap_urls:
                    urls.extend(self.parse_sitemap(sitemap_url))
            # Handle regular sitemaps
            elif root.tag.endswith('urlset'):
                for url_elem in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
                    loc_elem = url_elem.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
                    if loc_elem is not None and loc_elem.text:
                        urls.append(loc_elem.text)
            # Handle plain text sitemaps
            elif response.headers.get('content-type', '').startswith('text/plain'):
                # Parse as plain text, one URL per line
                content = response.text.strip()
                urls = [url.strip() for url in content.split('\n') if url.strip()]
            
            logger.info(f"Found {len(urls)} URLs in sitemap")
            return urls
        except ET.ParseError as e:
            logger.error(f"Error parsing sitemap XML: {str(e)}")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching sitemap: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error parsing sitemap: {str(e)}")
            return []

    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and is an HTTP/HTTPS link."""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc) and parsed.scheme in ["http", "https"]
        except Exception as e:
            logger.debug(f"Error parsing URL {url}: {str(e)}")
            return False

    def extract_text_from_html(self, html_content: str) -> str:
        """Convert HTML content to Markdown."""
        try:
            # Convert HTML to Markdown
            markdown_content = md(html_content, heading_style="ATX")
            return markdown_content
        except Exception as e:
            logger.error(f"Error converting HTML to Markdown: {str(e)}")
            return ""

    def get_page_content(self, url: str) -> Tuple[str, str]:
        """Fetch and extract content from a single page."""
        # Add a random delay to simulate human browsing behavior
        delay = random.uniform(1, 3)  # Random delay between 1-3 seconds
        time.sleep(delay)
        
        # Retry mechanism for failed requests
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=15)  # Increased timeout
                response.raise_for_status()
                
                content_type = response.headers.get('content-type', '')
                if 'text/html' not in content_type:
                    logger.warning(f"Skipping non-HTML content at {url}")
                    return "", ""
                
                text_content = self.extract_text_from_html(response.text)
                return text_content, response.url
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout fetching {url} (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error fetching {url} (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
            except requests.exceptions.HTTPError as e:
                logger.warning(f"HTTP error fetching {url}: {e}")
                # If it's a 403 or 429 error, wait longer before retrying
                if response.status_code in [403, 429]:
                    wait_time = 2 ** attempt * 5  # Longer wait for rate limiting
                    logger.info(f"Waiting {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
                if attempt < max_retries - 1:
                    # Rotate user agent on retry
                    self.session.headers.update(random.choice(BROWSER_HEADERS))
                else:
                    return "", ""
            except Exception as e:
                logger.error(f"Unexpected error fetching {url}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return "", ""
        
        return "", ""

    def get_links(self, url: str, html_content: str) -> List[str]:
        """Extract all valid links from a page."""
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            links = []
            
            for link in soup.find_all("a", href=True):
                absolute_url = urljoin(url, link["href"])
                if self.is_valid_url(absolute_url):
                    links.append(absolute_url)
                    
            return links
        except Exception as e:
            logger.error(f"Error extracting links from {url}: {str(e)}")
            return []

    def crawl_with_sitemap(self, sitemap_url: str) -> List[Tuple[str, str]]:
        """
        Crawl website using sitemap.xml for URL discovery.
        
        Args:
            sitemap_url: URL to the sitemap.xml file
            
        Returns:
            List of (content, url) tuples
        """
        # Parse sitemap to get URLs
        urls = self.parse_sitemap(sitemap_url)
        
        if not urls:
            logger.warning("No URLs found in sitemap")
            return []
        
        # Limit URLs based on page_limit
        urls = urls[:self.page_limit]
        
        scraped_content = []
        for url in urls:
            if len(scraped_content) >= self.page_limit:
                break
                
            if url in self.visited_urls:
                continue
                
            self.visited_urls.add(url)
            logger.info(f"Scraping {url} (from sitemap)")
            
            content, final_url = self.get_page_content(url)
            
            if content:
                scraped_content.append((content, final_url))
        
        logger.info(f"Finished sitemap-based crawling. Total pages scraped: {len(scraped_content)}")
        return scraped_content

    def crawl(self, start_url: str, use_sitemap: bool = False) -> List[Tuple[str, str]]:
        """
        Crawl website starting from start_url up to max_depth.
        Returns list of (content, url) tuples.
        """
        # If sitemap is requested, try to use it
        if use_sitemap:
            # Try common sitemap locations
            sitemap_urls = [
                urljoin(start_url, '/sitemap.xml'),
                urljoin(start_url, '/sitemap_index.xml'),
                urljoin(start_url, '/sitemap.txt')
            ]
            
            for sitemap_url in sitemap_urls:
                try:
                    logger.info(f"Trying to use sitemap: {sitemap_url}")
                    response = self.session.head(sitemap_url, timeout=10)
                    if response.status_code == 200:
                        return self.crawl_with_sitemap(sitemap_url)
                except Exception as e:
                    logger.debug(f"Sitemap not found at {sitemap_url}: {str(e)}")
                    continue
            
            logger.warning("No sitemap found, falling back to traditional crawling")
        
        # Traditional crawling approach
        if not self.is_valid_url(start_url):
            raise ValueError(f"Invalid URL: {start_url}")
            
        to_visit = [(start_url, 0)]  # (url, depth)
        scraped_content = []
        
        while to_visit and len(scraped_content) < self.page_limit:
            current_url, depth = to_visit.pop(0)
            
            # Skip if already visited or exceeding depth limit
            if current_url in self.visited_urls or depth > self.max_depth:
                continue
                
            self.visited_urls.add(current_url)
            logger.info(f"Scraping {current_url} at depth {depth}")
            
            content, final_url = self.get_page_content(current_url)
            
            if content:
                scraped_content.append((content, final_url))
                
                # Get links for next level if not at max depth and not using sitemap
                if depth < self.max_depth and not use_sitemap:
                    try:
                        response = self.session.get(current_url, timeout=15)
                        if 'text/html' in response.headers.get('content-type', ''):
                            links = self.get_links(current_url, response.text)
                            for link in links:
                                if link not in self.visited_urls:
                                    to_visit.append((link, depth + 1))
                    except Exception as e:
                        logger.error(f"Error getting links from {current_url}: {str(e)}")
                        
        logger.info(f"Finished crawling. Total pages scraped: {len(scraped_content)}")
        return scraped_content