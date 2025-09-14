from typing import List
import logging
import re
from transformers import AutoTokenizer
from src.config.settings import config

logger = logging.getLogger(__name__)


class TextChunker:
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None, model_name: str = None):
        self.chunk_size = chunk_size or config.chunk_size
        self.chunk_overlap = chunk_overlap or config.chunk_overlap
        self.model_name = model_name or config.embedding_model
        
        # Initialize tokenizer
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        except Exception as e:
            logger.warning(f"Failed to load tokenizer for {self.model_name}: {e}. Falling back to character counting.")
            self.tokenizer = None
        
        # Validate parameters
        if self.chunk_overlap >= self.chunk_size:
            logger.warning("Chunk overlap is larger than chunk size. Setting overlap to half of chunk size.")
            self.chunk_overlap = self.chunk_size // 2

    def _get_token_count(self, text: str) -> int:
        """Get the number of tokens in a text string."""
        if self.tokenizer:
            try:
                return len(self.tokenizer.encode(text))
            except Exception as e:
                logger.warning(f"Failed to tokenize text: {e}. Falling back to character counting.")
                return len(text)
        else:
            # Fallback to character counting if tokenizer is not available
            return len(text)

    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks using paragraph-aware approach with fallback to size-based chunking.
        
        First attempts to preserve paragraph boundaries when possible, only splitting paragraphs
        that exceed the chunk size limit (measured in tokens).
        """
        if not text:
            logger.warning("Empty text provided for chunking")
            return []
            
        if self._get_token_count(text) <= self.chunk_size:
            logger.info("Text is smaller than chunk size, returning as single chunk")
            return [text]
            
        # Split text into paragraphs
        paragraphs = self._split_into_paragraphs(text)
        
        # If we couldn't identify paragraphs, fall back to sentence splitting
        if len(paragraphs) <= 1:
            logger.info("No clear paragraph boundaries found, using sentence-based chunking")
            return self._sentence_aware_chunking(text)
            
        # Process paragraphs
        chunks = []
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
                
            # If paragraph is small enough, keep as single chunk
            if self._get_token_count(paragraph) <= self.chunk_size:
                chunks.append(paragraph)
            else:
                # If paragraph is too large, chunk it with overlap
                para_chunks = self._chunk_large_paragraph(paragraph)
                chunks.extend(para_chunks)
                
        logger.info(f"Created {len(chunks)} chunks from {len(paragraphs)} paragraphs")
        return chunks

    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs using double newlines."""
        # Split by double newlines
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]

    def _sentence_aware_chunking(self, text: str) -> List[str]:
        """Fallback method: split text into sentences and then chunk with overlap."""
        # Simple sentence splitting (can be enhanced with NLP libraries)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        if not sentences or len(sentences) == 1:
            # If we can't split into sentences, use character-based chunking
            return self._character_chunking(text)
            
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # Check if adding this sentence would exceed chunk size
            test_chunk = current_chunk + " " + sentence if current_chunk else sentence
            if self._get_token_count(test_chunk) <= self.chunk_size:
                current_chunk = test_chunk
            else:
                # Save current chunk and start new one
                if current_chunk:
                    chunks.append(current_chunk.strip())
                # If sentence itself is larger than chunk size, force split it
                if self._get_token_count(sentence) > self.chunk_size:
                    forced_chunks = self._chunk_large_paragraph(sentence)
                    chunks.extend(forced_chunks)
                    current_chunk = ""
                else:
                    current_chunk = sentence
                    
        # Don't forget the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks

    def _character_chunking(self, text: str) -> List[str]:
        """Original character-based chunking as fallback."""
        chunks = []
        start = 0
        chunk_count = 0
        
        while start < len(text) and chunk_count < 1000:  # Safety check
            end = min(start + self.chunk_size, len(text))
            chunk = text[start:end]
            chunks.append(chunk)
            chunk_count += 1
            
            # Move start position for next chunk (with overlap)
            start = end - self.chunk_overlap
            
            # If we've reached the end or the next chunk would be smaller than the overlap, break
            if end >= len(text) or start >= len(text):
                break
                
        return chunks

    def _chunk_large_paragraph(self, paragraph: str) -> List[str]:
        """Chunk a large paragraph into smaller pieces with overlap, measured in tokens."""
        chunks = []
        start = 0
        chunk_count = 0
        
        # For token-based chunking, we need a different approach
        if self.tokenizer:
            # Tokenize the paragraph
            tokens = self.tokenizer.encode(paragraph)
            
            while start < len(tokens) and chunk_count < 1000:  # Safety check
                end = min(start + self.chunk_size, len(tokens))
                chunk_tokens = tokens[start:end]
                chunk = self.tokenizer.decode(chunk_tokens, skip_special_tokens=True)
                chunks.append(chunk)
                chunk_count += 1
                
                # Move start position for next chunk (with overlap)
                next_start = end - self.chunk_overlap
                start = next_start
                
                # If we've reached the end, break
                if end >= len(tokens):
                    break
        else:
            # Fallback to character-based approach
            while start < len(paragraph) and chunk_count < 1000:  # Safety check
                end = min(start + self.chunk_size, len(paragraph))
                chunk = paragraph[start:end]
                chunks.append(chunk)
                chunk_count += 1
                
                # Move start position for next chunk (with overlap)
                # But ensure we don't start with whitespace
                next_start = end - self.chunk_overlap
                # Skip whitespace at the beginning of the next chunk
                while next_start < len(paragraph) and paragraph[next_start].isspace():
                    next_start += 1
                start = next_start
                
                # If we've reached the end, break
                if end >= len(paragraph):
                    break
                
        return chunks