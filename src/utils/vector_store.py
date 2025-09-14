from langchain_postgres import PGVector
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from typing import List, Tuple
import logging
import time
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
    def __init__(self, connection_string: str = None, collection_name: str = "web_scraping_collection"):
        self.connection_string = connection_string or config.database_url
        self.collection_name = collection_name
        self.vector_store = None
        self._initialize_store()

    def _get_source_name(self, url: str) -> str:
        """
        Generate a descriptive source name based on the domain of the URL.
        
        Args:
            url: The URL to extract domain from
            
        Returns:
            A descriptive source name like "Gnucoop Website" or "Domain Website"
        """
        from urllib.parse import urlparse
        
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            # Remove 'www.' prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
                
            # Extract the main domain name (first part before any dots)
            domain_parts = domain.split('.')
            if len(domain_parts) >= 2:
                # Take the second level domain (e.g., 'gnucoop' from 'gnucoop.com')
                domain_name = domain_parts[-2].capitalize()
            else:
                # If only one part, use it directly
                domain_name = domain_parts[0].capitalize()
            
            return f'{domain_name} Website'
        except Exception:
            # Fallback to URL if parsing fails
            return url

    def _initialize_store(self):
        """Initialize the PGVector store."""
        try:
            # Use a dummy embeddings object to satisfy the interface
            # We'll provide embeddings manually when adding documents
            dummy_embeddings = DummyEmbeddings()
            
            # Engine arguments for better connection handling
            engine_args = {
                "pool_pre_ping": True,  # Validates connections before use
                "pool_recycle": 300,    # Recycle connections after 5 minutes
                "pool_timeout": 30,     # Timeout for getting connection from pool
                "max_overflow": 10,     # Max overflow connections
                "pool_size": 5          # Number of connections to maintain in pool
            }
            
            self.vector_store = PGVector(
                embeddings=dummy_embeddings,
                connection=self.connection_string,
                collection_name=self.collection_name,
                engine_args=engine_args,
            )
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {str(e)}")
            raise RuntimeError(f"Failed to initialize vector store: {str(e)}")

    def _check_connection(self) -> bool:
        """
        Check if the database connection is still alive.
        Returns True if connection is alive, False otherwise.
        """
        try:
            if not self.vector_store:
                return False
                
            # Try to execute a simple query to check connection health
            # Using the underlying engine to test connection
            if hasattr(self.vector_store, '_engine') and self.vector_store._engine:
                # For connection pool, get a connection and test it
                with self.vector_store._engine.connect() as conn:
                    result = conn.execute("SELECT 1")
                    # Consume the result to ensure the connection is working
                    result.fetchone()
                return True
            return False
        except Exception as e:
            logger.debug(f"Connection check failed: {str(e)}")
            return False

    def _reconnect(self):
        """
        Reinitialize the vector store connection.
        """
        logger.info("Reinitializing database connection")
        try:
            # Clear the existing vector store
            self.vector_store = None
            # Reinitialize the store
            self._initialize_store()
            logger.info("Database connection reinitialized successfully")
        except Exception as e:
            logger.error(f"Failed to reinitialize database connection: {str(e)}")
            raise

    def store_documents(self, documents: List[Tuple[str, str, List[float]]]):
        """
        Store documents with their embeddings in the vector database.
        Each tuple contains: (markdown_content, source_url, embedding)
        """
        if not documents:
            logger.warning("No documents to store")
            return
            
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Check connection health and reconnect if needed
                if not self._check_connection():
                    logger.warning("Database connection lost, attempting to reconnect")
                    self._reconnect()
                
                # Reinitialize if vector_store is None
                if not self.vector_store:
                    self._initialize_store()
                
                # For newer versions of langchain-postgres, we need to use add_embeddings directly
                texts = [content for content, _, _ in documents]
                # Create metadata matching the structure used for images
                metadatas = [
                    {
                        "id": "",  # Will be populated by the database
                        "url": source_url,  # The URL of the chunk
                        "text": content,  # The Markdown content of the chunk
                        "source": self._get_source_name(source_url),  # A descriptive source name based on domain
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
                return  # Success, exit the retry loop
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed to store documents: {str(e)}")
                if attempt < max_retries - 1:
                    # Wait before retrying
                    time.sleep(2 ** attempt)
                    # Reconnect before retrying
                    logger.warning("Attempting to reconnect to database before retry")
                    self._reconnect()
                else:
                    # Last attempt failed, raise the exception
                    raise RuntimeError(f"Failed to store documents after {max_retries} attempts: {str(e)}")
