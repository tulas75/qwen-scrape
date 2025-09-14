import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Config:
    # Database settings
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/rag_db")
    
    # Scraping settings
    max_depth: int = int(os.getenv("MAX_DEPTH", "2"))
    page_limit: int = int(os.getenv("PAGE_LIMIT", "10"))
    
    # Model settings
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-large-instruct")
    
    # Processing settings
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "250"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "10"))


# Global config instance
config = Config()