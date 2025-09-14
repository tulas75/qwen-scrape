from typing import List
import logging
from src.config.settings import config

logger = logging.getLogger(__name__)


class TextChunker:
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or config.chunk_size
        self.chunk_overlap = chunk_overlap or config.chunk_overlap
        
        # Validate parameters
        if self.chunk_overlap >= self.chunk_size:
            logger.warning("Chunk overlap is larger than chunk size. Setting overlap to half of chunk size.")
            self.chunk_overlap = self.chunk_size // 2

    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks of specified size with overlap.
        """
        if not text:
            logger.warning("Empty text provided for chunking")
            return []
            
        if len(text) <= self.chunk_size:
            logger.info("Text is smaller than chunk size, returning as single chunk")
            return [text]
            
        chunks = []
        start = 0
        chunk_count = 0
        
        while start < len(text) and chunk_count < 1000:  # Safety check to prevent infinite loops
            end = min(start + self.chunk_size, len(text))
            chunk = text[start:end]
            chunks.append(chunk)
            chunk_count += 1
            
            # Move start position for next chunk (with overlap)
            start = end - self.chunk_overlap
            
            # If overlap is too large or we've reached the end, break
            if start >= len(text) or start <= 0:
                break
                
        logger.info(f"Created {len(chunks)} chunks from text of length {len(text)}")
        return chunks