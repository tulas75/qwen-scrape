from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
import logging
from src.config.settings import config

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or config.embedding_model
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the embedding model."""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model {self.model_name}: {str(e)}")
            raise RuntimeError(f"Failed to load embedding model {self.model_name}: {str(e)}")

    def generate_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """
        Generate embeddings for a list of texts.
        """
        if not texts:
            logger.warning("No texts provided for embedding generation")
            return []
            
        if not self.model:
            self._load_model()
            
        try:
            logger.info(f"Generating embeddings for {len(texts)} texts")
            embeddings = self.model.encode(texts)
            # Convert to list of numpy arrays if it's a 2D array
            if isinstance(embeddings, np.ndarray) and embeddings.ndim == 2:
                result = [embeddings[i] for i in range(len(embeddings))]
            else:
                result = embeddings
            logger.info("Embeddings generated successfully")
            return result
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {str(e)}")
            raise RuntimeError(f"Failed to generate embeddings: {str(e)}")