#!/usr/bin/env python3
"""
Test script for the enhanced RAG pipeline with GNUcoop website.
This script tests the browser simulation features.
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

def test_gnucoop():
    """Test the RAG pipeline with GNUcoop website."""
    # GNUcoop website that was returning 403
    test_url = "https://www.gnucoop.com/"
    
    print(f"Testing RAG pipeline with {test_url}")
    
    try:
        pipeline = RAGPipeline()
        # Use small limits for testing
        pipeline.run(test_url, max_depth=1, page_limit=5)
        print("GNUcoop pipeline test completed successfully!")
        return True
    except Exception as e:
        print(f"GNUcoop pipeline test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_gnucoop()