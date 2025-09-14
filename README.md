# Website Scraper for RAG

A web scraping pipeline that extracts content from websites, processes it for LLM consumption, generates embeddings using intfloat/multilingual-e5-large-instruct, and stores vectors in pgvector.

## Features
- Configurable web scraping with depth and page limits
- HTML to Markdown transformation
- Multiple chunking strategies:
  - Paragraph-aware chunking (default): Preserves paragraph boundaries
  - First section chunking: Creates chunks from just the first section of content
  - Hierarchical chunking: Merges H1/H2/H3 sections for larger, more meaningful chunks
  - Sentence-aware chunking: Splits content at sentence boundaries
- Token-aware chunking with intelligent overlap handling (250 tokens with 10 token overlap by default)
- Vector embeddings generation using intfloat/multilingual-e5-large-instruct
- PostgreSQL/pgvector storage with langchain_postgres and psycopg3

## Requirements
- Python 3.8+
- PostgreSQL with pgvector extension
- intfloat/multilingual-e5-large-instruct model

## Installation

1. Install PostgreSQL and enable pgvector extension:
   ```bash
   # On Ubuntu/Debian
   sudo apt install postgresql postgresql-contrib
   git clone https://github.com/pgvector/pgvector.git
   cd pgvector
   make
   sudo make install
   
   # On macOS with Homebrew
   brew install postgresql
   brew install pgvector
   
   # Don't forget to enable the extension in your database:
   # CREATE EXTENSION vector;
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   ```bash
   # On Linux/Mac
   source venv/bin/activate
   
   # On Windows
   venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
   This will install all required packages including `markdownify` for HTML to Markdown conversion and `transformers` for token-aware chunking.

## Configuration

Set up your database connection and other settings using environment variables:

```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/rag_db"
export MAX_DEPTH=2
export PAGE_LIMIT=10
export CHUNK_SIZE=500
export CHUNK_OVERLAP=50
```

Or create a `.env` file with these variables.

## Usage

### Command Line Interface
```bash
# Default paragraph-aware chunking
python scraper.py --url "https://example.com" --depth 2 --page-limit 10

# First section chunking (reduced number of chunks)
python scraper.py --url "https://example.com" --depth 2 --page-limit 10 --chunking-strategy first_section

# Hierarchical chunking (merged sections)
python scraper.py --url "https://example.com" --depth 2 --page-limit 10 --chunking-strategy hierarchical

# Sentence-aware chunking
python scraper.py --url "https://example.com" --depth 2 --page-limit 10 --chunking-strategy sentence
```

### Programmatic Usage
```python
from src.pipeline import RAGPipeline

# Default paragraph-aware chunking
pipeline = RAGPipeline()
pipeline.run("https://example.com", max_depth=2, page_limit=10)

# First section chunking (reduced number of chunks)
pipeline_first = RAGPipeline(chunking_strategy="first_section")
pipeline_first.run("https://example.com", max_depth=2, page_limit=10)

# Hierarchical chunking (merged sections)
pipeline_hierarchical = RAGPipeline(chunking_strategy="hierarchical")
pipeline_hierarchical.run("https://example.com", max_depth=2, page_limit=10)
```

### Example Scripts
- `tests/test_pipeline.py`: Simple test with a sample website
- `tests/test_gnucoop.py`: Test with GNUcoop website that was returning 403
- `tests/test_chunking.py`: Test for the chunking functionality
- `tests/test_paragraph_chunking.py`: Test for paragraph-aware chunking
- `tests/test_comprehensive_chunking.py`: Comprehensive test for various chunking scenarios
- `tests/test_token_chunking.py`: Test demonstrating token-based vs character-based chunking
- `tests/test_new_settings.py`: Test demonstrating the new default settings (250 tokens, 10 overlap) with all chunking strategies

To run the tests:
```bash
# Run a specific test
python -m tests.test_pipeline

# Run all tests
python -m unittest discover -s tests

# Run the new settings test
python -m tests.test_new_settings
```

## Project Structure
```
├── README.md
├── requirements.txt
├── scraper.py                # Main entry point
├── example_usage.py          # Example usage
├── .env.example              # Example environment variables
└── src/
    ├── config/
    │   └── settings.py       # Configuration management
    ├── pipeline.py           # Main pipeline orchestrator
    └── utils/
        ├── scraper.py        # Web scraping functionality
        ├── chunker.py        # Text chunking
        ├── embeddings.py     # Embedding generation
        └── vector_store.py   # Vector storage
└── tests/                    # Test scripts
    ├── test_pipeline.py
    ├── test_gnucoop.py
    ├── test_chunking.py
    ├── test_paragraph_chunking.py
    ├── test_comprehensive_chunking.py
    ├── test_token_chunking.py
    └── test_new_settings.py
```

## Configuration Options

| Environment Variable | Default Value | Description |
|---------------------|---------------|-------------|
| DATABASE_URL | postgresql://user:password@localhost:5432/rag_db | PostgreSQL connection string |
| MAX_DEPTH | 2 | Maximum crawling depth |
| PAGE_LIMIT | 10 | Maximum number of pages to scrape |
| CHUNK_SIZE | 250 | Size of text chunks in tokens |
| CHUNK_OVERLAP | 10 | Overlap between chunks in tokens |
| EMBEDDING_MODEL | intfloat/multilingual-e5-large-instruct | Sentence transformer model for embeddings |

## Chunking Strategies

1. **Paragraph-aware chunking (default)**: Preserves natural paragraph boundaries when possible, only splitting paragraphs that exceed the chunk size limit.

2. **First section chunking**: Creates chunks using only the first section of each document (content before the first major heading). This significantly reduces the number of chunks, which can be useful when you have many documents and want to reduce processing time.

3. **Hierarchical chunking**: Merges H1, H2, and H3 sections to create larger, more meaningful chunks. This strategy is useful when you want to preserve the document structure while reducing the number of chunks.

4. **Sentence-aware chunking**: Splits content at sentence boundaries when paragraph boundaries are not suitable.

## Notes

1. The first time you run the pipeline, it will download the embedding model which may take some time.
2. Make sure your PostgreSQL database has the pgvector extension enabled.
3. The pipeline will create a collection named "web_scraping_collection" in your database.
4. Some models have token limits (e.g., 512 tokens). If your chunks exceed this limit, you may see warnings. Consider adjusting the CHUNK_SIZE setting to stay within your model's limits.