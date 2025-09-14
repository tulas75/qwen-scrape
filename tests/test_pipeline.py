#!/usr/bin/env python3
"""
Test script for the RAG pipeline.
This script demonstrates how to use the pipeline with a sample website.
"""

import sys
import os
import logging

# Add src directory to path
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, src_path)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from src.pipeline import RAGPipeline

def test_pipeline():
    """Test the RAG pipeline with a sample website."""
    # For testing, we'll use a simple website
    test_url = "https://httpbin.org/html"
    
    print(f"Testing RAG pipeline with {test_url}")
    print("Note: This is a simple test. For a more comprehensive test,")
    print("please use a real website with actual content.")
    
    try:
        pipeline = RAGPipeline()
        # Use small limits for testing
        pipeline.run(test_url, max_depth=1, page_limit=2)
        print("Pipeline test completed successfully!")
    except Exception as e:
        print(f"Pipeline test failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    test_pipeline()