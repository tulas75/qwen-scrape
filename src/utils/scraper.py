import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Set, List, Tuple
import logging
import random
import time
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

    def crawl(self, start_url: str) -> List[Tuple[str, str]]:
        """
        Crawl website starting from start_url up to max_depth.
        Returns list of (content, url) tuples.
        """
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
                
                # Get links for next level if not at max depth
                if depth < self.max_depth:
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