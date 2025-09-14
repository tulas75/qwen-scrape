#!/usr/bin/env python3
"""
Example usage of the RAG pipeline.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.pipeline import RAGPipeline

def main():
    # Example usage
    start_url = "https://example.com"  # Replace with your target website
    max_depth = 2  # How deep to crawl
    page_limit = 10  # Maximum number of pages to scrape
    
    print(f"Running RAG pipeline on {start_url}")
    print(f"Max depth: {max_depth}")
    print(f"Page limit: {page_limit}")
    
    # Run the pipeline with different chunking strategies
    print("\n1. Running with paragraph-aware chunking (default):")
    pipeline = RAGPipeline(chunking_strategy="paragraph")
    # pipeline.run(start_url, max_depth, page_limit)
    
    print("\n2. Running with first section chunking (reduced chunks):")
    pipeline_first = RAGPipeline(chunking_strategy="first_section")
    # pipeline_first.run(start_url, max_depth, page_limit)
    
    print("\n3. Running with hierarchical chunking (merged sections):")
    pipeline_hierarchical = RAGPipeline(chunking_strategy="hierarchical")
    # pipeline_hierarchical.run(start_url, max_depth, page_limit)
    
    print("\nPipeline execution completed!")

if __name__ == "__main__":
    main()