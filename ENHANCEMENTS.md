# Enhanced WebScraper with Browser Simulation

## Summary of Changes

We've enhanced the WebScraper to simulate a real browser and avoid being blocked by websites like GNUcoop that were returning 403 Forbidden errors.

## Key Enhancements

1. **Realistic Browser Headers**: 
   - Added multiple browser header profiles with Linux user agents
   - Headers include User-Agent, Accept, Accept-Language, Accept-Encoding, and other browser-specific headers
   - Random header selection to simulate different browsers

2. **Request Delays**:
   - Added random delays between 1-3 seconds between requests
   - Simulates human browsing behavior

3. **Retry Mechanism**:
   - Implemented retry logic with exponential backoff
   - Special handling for 403 and 429 errors with longer wait times
   - Header rotation on retry attempts

4. **Session Management**:
   - Enhanced session configuration with increased timeout (15 seconds)
   - Better redirect handling

5. **Improved Error Handling**:
   - More detailed logging for different error types
   - Graceful handling of various HTTP errors

## Test Results

The enhanced scraper successfully accessed the GNUcoop website (https://www.gnucoop.com/) which was previously returning 403 Forbidden errors. The scraper was able to crawl 5 pages and process them through the entire RAG pipeline.

## Usage

The enhanced scraper is now the default implementation and will be used automatically when running the pipeline:

```bash
python scraper.py --url "https://www.gnucoop.com/" --depth 2 --page-limit 10
```

Or programmatically:

```python
from src.pipeline import RAGPipeline

pipeline = RAGPipeline()
pipeline.run("https://www.gnucoop.com/", max_depth=2, page_limit=10)
```