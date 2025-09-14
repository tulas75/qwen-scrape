import argparse
import logging
from typing import List, Tuple
import numpy as np
from src.utils.scraper import WebScraper
from src.utils.chunker import TextChunker
from src.utils.embeddings import EmbeddingGenerator
from src.utils.vector_store import VectorStore
from src.config.settings import config

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RAGPipeline:
    def __init__(self):
        self.scraper = WebScraper()
        self.chunker = TextChunker()
        self.embedder = EmbeddingGenerator()
        self.vector_store = VectorStore()

    def run(self, start_url: str, max_depth: int = None, page_limit: int = None) -> None:
        """
        Run the complete RAG pipeline.
        
        Args:
            start_url: The starting URL to scrape
            max_depth: Maximum depth to crawl
            page_limit: Maximum number of pages to scrape
        """
        try:
            # Update scraper settings if provided
            if max_depth is not None:
                self.scraper.max_depth = max_depth
            if page_limit is not None:
                self.scraper.page_limit = page_limit
            
            logger.info(f"Starting web scraping for {start_url}")
            logger.info(f"Max depth: {self.scraper.max_depth}, Page limit: {self.scraper.page_limit}")
            
            # 1. Scrape website
            scraped_data = self.scraper.crawl(start_url)
            logger.info(f"Scraped {len(scraped_data)} pages")
            
            if not scraped_data:
                logger.warning("No content scraped. Exiting pipeline.")
                return
            
            # 2. Transform and chunk content
            logger.info("Chunking content")
            chunked_data = self._chunk_scraped_data(scraped_data)
            logger.info(f"Created {len(chunked_data)} chunks")
            
            if not chunked_data:
                logger.warning("No chunks created. Exiting pipeline.")
                return
            
            # 3. Generate embeddings
            logger.info("Generating embeddings")
            embedded_data = self._generate_embeddings(chunked_data)
            logger.info("Embeddings generated successfully")
            
            # 4. Store in vector database
            logger.info("Storing in vector database")
            self.vector_store.store_documents(embedded_data)
            logger.info("Pipeline completed successfully")
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            raise

    def _chunk_scraped_data(self, scraped_data: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """
        Chunk scraped data using paragraph-aware approach.
        
        Attempts to preserve paragraph boundaries when possible, only splitting paragraphs
        that exceed the chunk size limit. Returns list of (markdown_chunk_content, source_url) tuples.
        """
        chunked_data = []
        for i, (content, url) in enumerate(scraped_data):
            try:
                logger.debug(f"Chunking content from {url} ({i+1}/{len(scraped_data)})")
                chunks = self.chunker.chunk_text(content)
                for chunk in chunks:
                    if chunk.strip():  # Only add non-empty chunks
                        chunked_data.append((chunk, url))
            except Exception as e:
                logger.error(f"Error chunking content from {url}: {str(e)}")
                continue
        return chunked_data

    def _generate_embeddings(self, chunked_data: List[Tuple[str, str]]) -> List[Tuple[str, str, List[float]]]:
        """
        Generate embeddings for chunked data.
        Returns list of (markdown_chunk_content, source_url, embedding) tuples.
        """
        if not chunked_data:
            return []
            
        # Extract just the text content for embedding
        texts = [chunk_content for chunk_content, _ in chunked_data]
        
        # Generate embeddings
        try:
            embeddings = self.embedder.generate_embeddings(texts)
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
            
        # Check if we have the right number of embeddings
        if len(embeddings) != len(chunked_data):
            raise RuntimeError(f"Embedding count mismatch: {len(embeddings)} embeddings for {len(chunked_data)} chunks")
        
        # Combine back with source URLs
        embedded_data = [
            (chunk_content, source_url, embedding.tolist() if isinstance(embedding, np.ndarray) else embedding)
            for (chunk_content, source_url), embedding in zip(chunked_data, embeddings)
        ]
        
        return embedded_data


def main():
    parser = argparse.ArgumentParser(description="Web Scraper for RAG")
    parser.add_argument("--url", required=True, help="Starting URL to scrape")
    parser.add_argument("--depth", type=int, default=config.max_depth, help="Maximum crawling depth")
    parser.add_argument("--page-limit", type=int, default=config.page_limit, help="Maximum number of pages to scrape")
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.depth < 0:
        parser.error("Depth must be non-negative")
    if args.page_limit <= 0:
        parser.error("Page limit must be positive")
    
    pipeline = RAGPipeline()
    pipeline.run(args.url, args.depth, args.page_limit)


if __name__ == "__main__":
    main()