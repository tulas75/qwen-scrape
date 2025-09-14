#!/usr/bin/env python3
"""
Comprehensive test script for the enhanced chunking functionality.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.chunker import TextChunker

def test_various_chunking_scenarios():
    """Test various chunking scenarios."""
    
    # Test 1: Markdown with headers and paragraphs
    markdown_text = """# Introduction
This is the first paragraph of the introduction. It contains some information that should be kept together as a single chunk because it's not too long.

This is the second paragraph of the introduction. It's also relatively short and should be preserved as a separate chunk.

## Main Content
This is a much longer paragraph that contains significantly more content than the previous paragraphs. It's so long that it will need to be split into multiple chunks according to our chunking strategy. This is to demonstrate how the chunker handles paragraphs that exceed the maximum chunk size limit while still trying to preserve as much semantic meaning as possible. We want to see if the algorithm correctly splits this large paragraph into smaller pieces with appropriate overlap. This should help us evaluate the effectiveness of our approach to chunking.

### Subsection
Short paragraph here.

Another short paragraph that should remain as its own chunk."""

    # Test 2: Text without clear paragraphs
    plain_text = "This is a continuous text without clear paragraph breaks. It just goes on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on."

    # Test 3: Very short text
    short_text = "This is a very short text."

    chunker = TextChunker(chunk_size=150, chunk_overlap=20)
    
    print("=== Test 1: Markdown with headers and paragraphs ===")
    chunks1 = chunker.chunk_text(markdown_text)
    print(f"Input text length: {len(markdown_text)} characters")
    print(f"Number of chunks: {len(chunks1)}")
    for i, chunk in enumerate(chunks1):
        print(f"\n--- Chunk {i+1} ---")
        print(repr(chunk))
        print(f"Length: {len(chunk)} characters")

    print("\n\n=== Test 2: Plain text without clear paragraphs ===")
    chunks2 = chunker.chunk_text(plain_text)
    print(f"Input text length: {len(plain_text)} characters")
    print(f"Number of chunks: {len(chunks2)}")
    for i, chunk in enumerate(chunks2[:3]):  # Only show first 3 chunks
        print(f"\n--- Chunk {i+1} ---")
        print(repr(chunk))
        print(f"Length: {len(chunk)} characters")
    if len(chunks2) > 3:
        print("... (showing only first 3 chunks)")

    print("\n\n=== Test 3: Very short text ===")
    chunks3 = chunker.chunk_text(short_text)
    print(f"Input text length: {len(short_text)} characters")
    print(f"Number of chunks: {len(chunks3)}")
    for i, chunk in enumerate(chunks3):
        print(f"\n--- Chunk {i+1} ---")
        print(repr(chunk))
        print(f"Length: {len(chunk)} characters")

if __name__ == "__main__":
    test_various_chunking_scenarios()