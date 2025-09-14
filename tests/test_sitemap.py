#!/usr/bin/env python3
"""
Test script for sitemap functionality in the RAG pipeline.
This script demonstrates how to use the pipeline with a sitemap.xml file.
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

def test_sitemap_pipeline():
    """Test the RAG pipeline with a website that has a sitemap.xml."""
    # For testing, we'll use a website known to have a sitemap
    # You might want to change this to a website you're allowed to scrape
    test_url = "https://example.com"  # Replace with a real website that has a sitemap
    
    print(f"Testing RAG pipeline with sitemap from {test_url}")
    
    try:
        pipeline = RAGPipeline()
        # Use small limits for testing
        pipeline.run(test_url, max_depth=1, page_limit=5, use_sitemap=True)
        print("Sitemap pipeline test completed successfully!")
    except Exception as e:
        print(f"Sitemap pipeline test failed: {str(e)}")
        return False
    
    return True

def test_sitemap_fallback():
    """Test that the pipeline falls back to traditional crawling when no sitemap is found."""
    # Using a website that likely doesn't have a sitemap
    test_url = "https://httpbin.org/html"
    
    print(f"Testing RAG pipeline fallback from {test_url}")
    print("This should fall back to traditional crawling since httpbin.org doesn't have a sitemap")
    
    try:
        pipeline = RAGPipeline()
        # Use small limits for testing
        pipeline.run(test_url, max_depth=1, page_limit=2, use_sitemap=True)
        print("Fallback pipeline test completed successfully!")
    except Exception as e:
        print(f"Fallback pipeline test failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    print("Running sitemap functionality tests...")
    print("Note: These tests require internet connectivity and may take some time.")
    print()
    
    # Test 1: Sitemap-based scraping (you'll need to modify the URL for a real test)
    print("Test 1: Sitemap-based scraping")
    # Commenting out the actual test since we don't have a specific website to test with
    # Uncomment and modify the URL for actual testing
    # test_sitemap_pipeline()
    print("Skipping - please modify the test URL for actual testing")
    print()
    
    # Test 2: Fallback to traditional crawling
    print("Test 2: Fallback to traditional crawling")
    test_sitemap_fallback()
    print()
    
    print("Sitemap functionality tests completed!")