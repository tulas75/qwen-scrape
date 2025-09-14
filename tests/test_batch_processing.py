#!/usr/bin/env python3
"""
Test script for batch processing functionality in the RAG pipeline.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.pipeline import RAGPipeline


class TestBatchProcessing(unittest.TestCase):
    """Test cases for batch processing functionality."""

    @patch('src.utils.scraper.WebScraper.crawl')
    @patch('src.utils.chunker.TextChunker.chunk_text')
    @patch('src.utils.embeddings.EmbeddingGenerator.generate_embeddings')
    @patch('src.utils.vector_store.VectorStore.store_documents')
    def test_batch_processing_small_dataset(self, mock_store, mock_generate, mock_chunk, mock_crawl):
        """Test batch processing with a small dataset that requires multiple batches."""
        # Mock the scraper to return 5 pages
        mock_crawl.return_value = [
            ("Content 1", "http://example.com/1"),
            ("Content 2", "http://example.com/2"),
            ("Content 3", "http://example.com/3"),
            ("Content 4", "http://example.com/4"),
            ("Content 5", "http://example.com/5")
        ]
        
        # Mock the chunker to return 2 chunks per page
        mock_chunk.side_effect = lambda content: [f"Chunk {i}" for i in range(2)]
        
        # Mock the embedder to return embeddings - we need to handle multiple calls
        mock_generate.side_effect = lambda texts: [[0.1 * i] * 10 for i in range(len(texts))]
        
        # Create pipeline and run with batch size of 5
        pipeline = RAGPipeline()
        pipeline.run("http://example.com", max_depth=1, page_limit=5, batch_size=5)
        
        # Verify that store_documents was called twice (10 chunks / 5 batch size = 2 batches)
        self.assertEqual(mock_store.call_count, 2)
        
        # Check the sizes of each batch
        call_args_list = mock_store.call_args_list
        self.assertEqual(len(call_args_list[0][0][0]), 5)  # First batch: 5 chunks
        self.assertEqual(len(call_args_list[1][0][0]), 5)  # Second batch: 5 chunks

    @patch('src.utils.scraper.WebScraper.crawl')
    @patch('src.utils.chunker.TextChunker.chunk_text')
    @patch('src.utils.embeddings.EmbeddingGenerator.generate_embeddings')
    @patch('src.utils.vector_store.VectorStore.store_documents')
    def test_batch_processing_large_dataset(self, mock_store, mock_generate, mock_chunk, mock_crawl):
        """Test batch processing with a larger dataset that requires multiple batches."""
        # Mock the scraper to return 25 pages
        mock_crawl.return_value = [
            (f"Content {i}", f"http://example.com/{i}") for i in range(25)
        ]
        
        # Mock the chunker to return 2 chunks per page
        mock_chunk.side_effect = lambda content: [f"Chunk {i}" for i in range(2)]
        
        # Mock the embedder to return embeddings - we need to handle multiple calls
        mock_generate.side_effect = lambda texts: [[0.1 * i] * 10 for i in range(len(texts))]
        
        # Create pipeline and run with batch size of 20
        pipeline = RAGPipeline()
        pipeline.run("http://example.com", max_depth=1, page_limit=25, batch_size=20)
        
        # Verify that store_documents was called twice (50 chunks / 20 batch size = 3 batches, but the last one has only 10 chunks)
        self.assertEqual(mock_store.call_count, 3)
        
        # Check the sizes of each batch
        call_args_list = mock_store.call_args_list
        self.assertEqual(len(call_args_list[0][0][0]), 20)  # First batch: 20 chunks
        self.assertEqual(len(call_args_list[1][0][0]), 20)  # Second batch: 20 chunks
        self.assertEqual(len(call_args_list[2][0][0]), 10)  # Third batch: 10 chunks

    @patch('src.utils.scraper.WebScraper.crawl')
    @patch('src.utils.chunker.TextChunker.chunk_text')
    @patch('src.utils.embeddings.EmbeddingGenerator.generate_embeddings')
    @patch('src.utils.vector_store.VectorStore.store_documents')
    def test_batch_processing_with_default_config(self, mock_store, mock_generate, mock_chunk, mock_crawl):
        """Test batch processing using the default batch size from configuration."""
        # Mock the scraper to return 150 pages
        mock_crawl.return_value = [
            (f"Content {i}", f"http://example.com/{i}") for i in range(150)
        ]
        
        # Mock the chunker to return 1 chunk per page
        mock_chunk.side_effect = lambda content: ["Chunk"]
        
        # Mock the embedder to return embeddings - we need to handle multiple calls
        mock_generate.side_effect = lambda texts: [[0.1 * i] * 10 for i in range(len(texts))]
        
        # Create pipeline and run with default batch size (100 from config)
        pipeline = RAGPipeline()
        pipeline.run("http://example.com", max_depth=1, page_limit=150)  # No batch_size specified
        
        # Verify that store_documents was called twice (150 chunks / 100 batch size = 2 batches)
        self.assertEqual(mock_store.call_count, 2)
        
        # Check the sizes of each batch
        call_args_list = mock_store.call_args_list
        self.assertEqual(len(call_args_list[0][0][0]), 100)  # First batch: 100 chunks
        self.assertEqual(len(call_args_list[1][0][0]), 50)   # Second batch: 50 chunks


if __name__ == "__main__":
    unittest.main()