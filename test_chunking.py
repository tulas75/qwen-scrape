#!/usr/bin/env python3
"""
Test script for the enhanced chunking functionality.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.chunker import TextChunker

def test_paragraph_chunking():
    """Test paragraph-aware chunking with various text formats."""
    
    # Test text with clear paragraphs
    test_text = """This is the first paragraph. It contains some information that should be kept together as a single chunk because it's not too long.

This is the second paragraph. It's also relatively short and should be preserved as a separate chunk.

This is a much longer paragraph that contains significantly more content than the previous paragraphs. It's so long that it will need to be split into multiple chunks according to our chunking strategy. This is to demonstrate how the chunker handles paragraphs that exceed the maximum chunk size limit while still trying to preserve as much semantic meaning as possible. We want to see if the algorithm correctly splits this large paragraph into smaller pieces with appropriate overlap."""
    
    chunker = TextChunker(chunk_size=150, chunk_overlap=20)
    chunks = chunker.chunk_text(test_text)
    
    print("=== Paragraph-Aware Chunking Test ===")
    print(f"Input text length: {len(test_text)} characters")
    print(f"Number of chunks: {len(chunks)}")
    print("\nChunks:")
    for i, chunk in enumerate(chunks):
        print(f"\n--- Chunk {i+1} ---")
        print(repr(chunk))
        print(f"Length: {len(chunk)} characters")

if __name__ == "__main__":
    test_paragraph_chunking()