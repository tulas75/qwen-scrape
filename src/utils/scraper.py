import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Set, List, Tuple
import logging
from src.config.settings import config

logger = logging.getLogger(__name__)


class WebScraper:
    def __init__(self, max_depth: int = None, page_limit: int = None):
        self.max_depth = max_depth or config.max_depth
        self.page_limit = page_limit or config.page_limit
        self.visited_urls: Set[str] = set()
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and is an HTTP/HTTPS link."""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc) and parsed.scheme in ["http", "https"]
        except Exception as e:
            logger.debug(f"Error parsing URL {url}: {str(e)}")
            return False

    def extract_text_from_html(self, html_content: str) -> str:
        """Extract text content from HTML."""
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
                
            # Get text and clean it up
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            logger.error(f"Error extracting text from HTML: {str(e)}")
            return ""

    def get_page_content(self, url: str) -> Tuple[str, str]:
        """Fetch and extract content from a single page."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '')
            if 'text/html' not in content_type:
                logger.warning(f"Skipping non-HTML content at {url}")
                return "", ""
            
            text_content = self.extract_text_from_html(response.text)
            return text_content, response.url
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout fetching {url}")
            return "", ""
        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection error fetching {url}")
            return "", ""
        except requests.exceptions.HTTPError as e:
            logger.warning(f"HTTP error fetching {url}: {e}")
            return "", ""
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {str(e)}")
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
                        response = self.session.get(current_url, timeout=10)
                        if 'text/html' in response.headers.get('content-type', ''):
                            links = self.get_links(current_url, response.text)
                            for link in links:
                                if link not in self.visited_urls:
                                    to_visit.append((link, depth + 1))
                    except Exception as e:
                        logger.error(f"Error getting links from {current_url}: {str(e)}")
                        
        logger.info(f"Finished crawling. Total pages scraped: {len(scraped_content)}")
        return scraped_content