# Website Scraper for RAG

A web scraping pipeline that extracts content from websites, processes it for LLM consumption, generates embeddings using intfloat/multilingual-e5-large-instruct, and stores vectors in pgvector.

## Features
- Configurable web scraping with depth and page limits
- HTML to Markdown transformation
- Paragraph-aware content chunking with intelligent overlap handling
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
   
   This will install all required packages including `markdownify` for HTML to Markdown conversion.

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
python scraper.py --url "https://example.com" --depth 2 --page-limit 10
```

### Programmatic Usage
```python
from src.pipeline import RAGPipeline

pipeline = RAGPipeline()
pipeline.run("https://example.com", max_depth=2, page_limit=10)
```

### Example Scripts
- `example_usage.py`: Shows how to use the pipeline programmatically
- `test_pipeline.py`: Simple test with a sample website

## Project Structure
```
├── README.md
├── requirements.txt
├── scraper.py                # Main entry point
├── example_usage.py          # Example usage
├── test_pipeline.py          # Test script
└── src/
    ├── config/
    │   └── settings.py       # Configuration management
    ├── pipeline.py           # Main pipeline orchestrator
    └── utils/
        ├── scraper.py        # Web scraping functionality
        ├── chunker.py        # Text chunking
        ├── embeddings.py     # Embedding generation
        └── vector_store.py   # Vector storage
```

## Configuration Options

| Environment Variable | Default Value | Description |
|---------------------|---------------|-------------|
| DATABASE_URL | postgresql://user:password@localhost:5432/rag_db | PostgreSQL connection string |
| MAX_DEPTH | 2 | Maximum crawling depth |
| PAGE_LIMIT | 10 | Maximum number of pages to scrape |
| CHUNK_SIZE | 500 | Size of text chunks in characters |
| CHUNK_OVERLAP | 50 | Overlap between chunks in characters |
| EMBEDDING_MODEL | intfloat/multilingual-e5-large-instruct | Sentence transformer model for embeddings |

## Notes

1. The first time you run the pipeline, it will download the embedding model which may take some time.
2. Make sure your PostgreSQL database has the pgvector extension enabled.
3. The pipeline will create a collection named "web_scraping_collection" in your database.