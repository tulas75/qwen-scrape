from langchain_postgres import PGVector
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from typing import List, Tuple
import logging
from src.config.settings import config

logger = logging.getLogger(__name__)


class DummyEmbeddings(Embeddings):
    """A dummy embeddings class that satisfies the interface but isn't actually used."""
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Return dummy embeddings."""
        return [[0.0] * 1536 for _ in texts]  # Return dummy embeddings with 1536 dimensions
    
    def embed_query(self, text: str) -> List[float]:
        """Return a dummy embedding."""
        return [0.0] * 1536  # Return dummy embedding with 1536 dimensions


class VectorStore:
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or config.database_url
        self.vector_store = None
        self._initialize_store()

    def _initialize_store(self):
        """Initialize the PGVector store."""
        try:
            # Use a dummy embeddings object to satisfy the interface
            # We'll provide embeddings manually when adding documents
            dummy_embeddings = DummyEmbeddings()
            self.vector_store = PGVector(
                embeddings=dummy_embeddings,
                connection=self.connection_string,
                collection_name="web_scraping_collection",
            )
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {str(e)}")
            raise RuntimeError(f"Failed to initialize vector store: {str(e)}")

    def store_documents(self, documents: List[Tuple[str, str, List[float]]]):
        """
        Store documents with their embeddings in the vector database.
        Each tuple contains: (markdown_content, source_url, embedding)
        """
        if not documents:
            logger.warning("No documents to store")
            return
            
        if not self.vector_store:
            self._initialize_store()
            
        try:
            # For newer versions of langchain-postgres, we need to use add_embeddings directly
            texts = [content for content, _, _ in documents]
            # Create metadata matching the structure used for images
            metadatas = [
                {
                    "id": "",  # Will be populated by the database
                    "url": source_url,  # The URL of the chunk
                    "text": content,  # The Markdown content of the chunk
                    "source": source_url,  # The source (URL) - for consistency with image structure
                    "mimetype": "text/markdown"  # MIME type for Markdown content
                } 
                for content, source_url, _ in documents
            ]
            embeddings = [emb for _, _, emb in documents]
            
            # Store documents with their embeddings
            self.vector_store.add_embeddings(
                texts=texts,
                embeddings=embeddings,
                metadatas=metadatas
            )
            logger.info(f"Stored {len(documents)} documents in vector store")
        except Exception as e:
            logger.error(f"Failed to store documents: {str(e)}")
            raise RuntimeError(f"Failed to store documents: {str(e)}")
