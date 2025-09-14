#!/usr/bin/env python3
"""
Test script to demonstrate the difference between character-based and token-based chunking.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.chunker import TextChunker
from transformers import AutoTokenizer

def compare_chunking_methods():
    """Compare character-based and token-based chunking."""
    
    # Test text
    test_text = """This is a sample paragraph to demonstrate the difference between character-based 
and token-based chunking approaches. The quick brown fox jumps over the lazy dog. 
This sentence contains a mix of short and long words that will tokenize differently 
than they appear as characters. International characters like café, naïve, and résumé 
will also affect tokenization.

This is another paragraph with different content to show how paragraph boundaries 
are handled. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod 
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis 
nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."""

    # Initialize tokenizers
    model_name = "intfloat/multilingual-e5-large-instruct"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # Character-based chunking (simulated)
    char_chunker = TextChunker(chunk_size=100, chunk_overlap=10)
    # Temporarily disable tokenizer to simulate character-based chunking
    char_chunker.tokenizer = None
    
    # Token-based chunking
    token_chunker = TextChunker(chunk_size=100, chunk_overlap=10, model_name=model_name)
    
    print("=== Character-based vs Token-based Chunking Comparison ===\n")
    
    # Compare character-based chunking
    print("1. Character-based chunking (size=100 characters):")
    char_chunks = char_chunker.chunk_text(test_text)
    for i, chunk in enumerate(char_chunks[:3]):  # Show first 3 chunks
        char_count = len(chunk)
        token_count = len(tokenizer.encode(chunk))
        print(f"   Chunk {i+1}: {char_count} characters, {token_count} tokens")
        print(f"   Content: {repr(chunk[:50])}...")
        print()
    
    # Compare token-based chunking
    print("2. Token-based chunking (size=100 tokens):")
    token_chunks = token_chunker.chunk_text(test_text)
    for i, chunk in enumerate(token_chunks[:3]):  # Show first 3 chunks
        char_count = len(chunk)
        token_count = len(tokenizer.encode(chunk))
        print(f"   Chunk {i+1}: {char_count} characters, {token_count} tokens")
        print(f"   Content: {repr(chunk[:50])}...")
        print()
    
    print(f"Character-based chunks: {len(char_chunks)}")
    print(f"Token-based chunks: {len(token_chunks)}")
    print("\nNote: Token-based chunking ensures each chunk is actually the intended")
    print("size for the embedding model, which can vary significantly from character count.")

if __name__ == "__main__":
    compare_chunking_methods()