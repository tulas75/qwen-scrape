#!/usr/bin/env python3
"""
Test script to demonstrate chunking with new default settings (250 tokens, 10 overlap).
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.utils.chunker import TextChunker

# Larger sample text for testing
sample_text = """
Welcome to our comprehensive guide on machine learning. This document will introduce you to the fundamental concepts and applications of machine learning in various industries.

# Introduction to Machine Learning

Machine learning is a method of data analysis that automates analytical model building. It is a branch of artificial intelligence based on the idea that systems can learn from data, identify patterns and make decisions with minimal human intervention. Machine learning algorithms build a model based on sample data, known as training data, in order to make predictions or decisions without being explicitly programmed to do so.

## What is Machine Learning?

Machine learning algorithms build a model based on sample data, known as training data, in order to make predictions or decisions without being explicitly programmed to do so. Machine learning algorithms are used in a wide variety of applications, such as in medicine, email filtering, speech recognition, and computer vision, where it is difficult or unfeasible to develop conventional algorithms to perform the needed tasks.

Machine learning is closely related to computational statistics, which focuses on making predictions using computers. The study of mathematical optimization delivers methods, theory and application domains to the field of machine learning. Data mining is a related field of study, focusing on exploratory data analysis through unsupervised learning.

### Types of Machine Learning

There are three main types of machine learning:

1. Supervised Learning: The model is trained on labeled data. Common algorithms include linear regression, logistic regression, decision trees, and support vector machines.

2. Unsupervised Learning: The model finds patterns in unlabeled data. Common algorithms include k-means clustering, hierarchical clustering, and principal component analysis.

3. Reinforcement Learning: The model learns through trial and error using rewards and penalties. This approach is commonly used in robotics, gaming, and navigation systems.

## Applications of Machine Learning

Machine learning has many applications across different industries:

- Healthcare: Disease prediction, drug discovery, medical imaging, personalized treatment plans
- Finance: Fraud detection, algorithmic trading, credit scoring, risk assessment
- Retail: Recommendation systems, inventory management, pricing optimization, customer segmentation
- Transportation: Autonomous vehicles, route optimization, traffic prediction, fleet management
- Manufacturing: Predictive maintenance, quality control, supply chain optimization
- Marketing: Customer behavior analysis, targeted advertising, sentiment analysis

### Deep Learning

Deep learning is a subset of machine learning that uses neural networks with multiple layers. These neural networks attempt to simulate the behavior of the human brain—albeit far from perfectly—in order to 'learn' from large amounts of data. Deep learning models have achieved remarkable success in image recognition, natural language processing, and speech recognition.

Deep learning architectures such as deep neural networks, convolutional neural networks, and recurrent neural networks have been applied to fields like computer vision, automatic speech recognition, natural language processing, and bioinformatics where they have produced results comparable to and in some cases superior to human experts.

## Conclusion

Machine learning is transforming many industries and has become an essential tool for data analysis. As technology advances, we can expect to see even more applications of machine learning in our daily lives. The field continues to evolve rapidly, with new algorithms and techniques being developed regularly to solve increasingly complex problems.
"""

def test_chunking_with_new_settings():
    """Test different chunking strategies with the new default settings."""
    print("Testing chunking strategies with new default settings (250 tokens, 10 overlap):\
")
    
    # Test with default paragraph strategy
    print("1. Paragraph-aware chunking (default):")
    chunker_paragraph = TextChunker(strategy="paragraph")
    chunks_paragraph = chunker_paragraph.chunk_text(sample_text)
    print(f"   Created {len(chunks_paragraph)} chunks")
    for i, chunk in enumerate(chunks_paragraph[:3]):  # Show first 3 chunks
        print(f"   Chunk {i+1}: {chunk[:100]}...")
    if len(chunks_paragraph) > 3:
        print(f"   ... and {len(chunks_paragraph) - 3} more chunks")
    print()
    
    # Test with first section strategy
    print("2. First section chunking:")
    chunker_first = TextChunker(strategy="first_section")
    chunks_first = chunker_first.chunk_text(sample_text)
    print(f"   Created {len(chunks_first)} chunks")
    for i, chunk in enumerate(chunks_first):
        print(f"   Chunk {i+1}: {chunk[:100]}...")
    print()
    
    # Test with hierarchical strategy
    print("3. Hierarchical chunking (merged sections):")
    chunker_hierarchical = TextChunker(strategy="hierarchical")
    chunks_hierarchical = chunker_hierarchical.chunk_text(sample_text)
    print(f"   Created {len(chunks_hierarchical)} chunks")
    for i, chunk in enumerate(chunks_hierarchical[:3]):  # Show first 3 chunks
        print(f"   Chunk {i+1}: {chunk[:100]}...")
    if len(chunks_hierarchical) > 3:
        print(f"   ... and {len(chunks_hierarchical) - 3} more chunks")
    print()
    
    # Test with sentence strategy
    print("4. Sentence-aware chunking:")
    chunker_sentence = TextChunker(strategy="sentence")
    chunks_sentence = chunker_sentence.chunk_text(sample_text)
    print(f"   Created {len(chunks_sentence)} chunks")
    for i, chunk in enumerate(chunks_sentence[:3]):  # Show first 3 chunks
        print(f"   Chunk {i+1}: {chunk[:100]}...")
    if len(chunks_sentence) > 3:
        print(f"   ... and {len(chunks_sentence) - 3} more chunks")

if __name__ == "__main__":
    test_chunking_with_new_settings()