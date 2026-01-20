"""Embeddings generation using OpenAI.

This module provides embeddings functionality for converting text to vectors.
"""

from typing import List

from langchain_openai import OpenAIEmbeddings

from src.config.settings import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)


class EmbeddingsManager:
    """Manager for generating embeddings using OpenAI."""

    def __init__(self, model: str | None = None):
        """Initialize the embeddings manager.

        Args:
            model: OpenAI embedding model name (default: from settings)
        """
        self.model = model or settings.embedding_model

        self.embeddings = OpenAIEmbeddings(
            model=self.model,
            openai_api_key=settings.openai_api_key,
        )

        logger.info(f"Initialized EmbeddingsManager with model: {self.model}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of documents.

        Args:
            texts: List of text strings to embed

        Returns:
            List[List[float]]: List of embedding vectors

        Example:
            >>> manager = EmbeddingsManager()
            >>> embeddings = manager.embed_documents(["Text 1", "Text 2"])
            >>> print(f"Generated {len(embeddings)} embeddings")
        """
        try:
            logger.debug(f"Generating embeddings for {len(texts)} documents")
            vectors = self.embeddings.embed_documents(texts)
            logger.info(f"Successfully generated {len(vectors)} embeddings")
            return vectors
        except Exception as e:
            logger.error(f"Error generating document embeddings: {e}")
            raise

    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query text.

        Args:
            text: Query text to embed

        Returns:
            List[float]: Embedding vector

        Example:
            >>> manager = EmbeddingsManager()
            >>> embedding = manager.embed_query("What is the schedule?")
            >>> print(f"Embedding dimension: {len(embedding)}")
        """
        try:
            logger.debug(f"Generating embedding for query: {text[:50]}...")
            vector = self.embeddings.embed_query(text)
            logger.info("Successfully generated query embedding")
            return vector
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            raise

    def get_embeddings_instance(self) -> OpenAIEmbeddings:
        """Get the underlying OpenAI embeddings instance.

        Returns:
            OpenAIEmbeddings: The embeddings instance

        Note:
            This is useful for passing to vector stores that expect an embeddings object.
        """
        return self.embeddings


def get_embeddings(model: str | None = None) -> OpenAIEmbeddings:
    """Convenience function to get an embeddings instance.

    Args:
        model: OpenAI embedding model name (default: from settings)

    Returns:
        OpenAIEmbeddings: Configured embeddings instance

    Example:
        >>> embeddings = get_embeddings()
        >>> vector_store = Chroma(embedding_function=embeddings)
    """
    manager = EmbeddingsManager(model=model)
    return manager.get_embeddings_instance()
