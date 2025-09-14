from langchain_postgres import PGVector
from langchain_postgres.vectorstores import PGVectorStore
from langchain_core.documents import Document
from typing import List, Tuple
import logging
from src.config.settings import config

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or config.database_url
        self.vector_store = None
        self._initialize_store()

    def _initialize_store(self):
        """Initialize the PGVector store."""
        try:
            self.vector_store = PGVector(
                embeddings=None,  # We'll provide embeddings manually
                connection=self.connection_string,
                collection_name="web_scraping_collection",
            )
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {str(e)}")
            raise RuntimeError(f"Failed to initialize vector store: {str(e)}")

    def store_documents(self, documents: List[Tuple[str, str, List[float]]]):
        """
        Store documents with their embeddings in the vector database.
        Each tuple contains: (content, source_url, embedding)
        """
        if not documents:
            logger.warning("No documents to store")
            return
            
        if not self.vector_store:
            self._initialize_store()
            
        try:
            # Convert to Langchain Document format
            langchain_docs = [
                Document(
                    page_content=content,
                    metadata={"source": source_url}
                )
                for content, source_url, _ in documents
            ]
            
            # Store documents with their embeddings
            self.vector_store.add_documents(langchain_docs, embeddings=[emb for _, _, emb in documents])
            logger.info(f"Stored {len(documents)} documents in vector store")
        except Exception as e:
            logger.error(f"Failed to store documents: {str(e)}")
            raise RuntimeError(f"Failed to store documents: {str(e)}")