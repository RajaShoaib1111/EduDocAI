"""Vector store operations using ChromaDB.

This module provides functionality for storing and retrieving document embeddings.
"""

from pathlib import Path
from typing import List, Optional

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from src.config.settings import settings
from src.retrieval.embeddings import get_embeddings
from src.utils.logging import get_logger

logger = get_logger(__name__)


class VectorStoreManager:
    """Manager for ChromaDB vector store operations."""

    def __init__(
        self,
        collection_name: str = "edudicai",
        persist_directory: str | None = None,
    ):
        """Initialize the vector store manager.

        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory for persisting the vector store
                              (default: from settings)
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory or settings.chroma_persist_directory

        # Ensure persist directory exists
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)

        # Get embeddings instance
        self.embeddings = get_embeddings()

        # Initialize or load existing vector store
        self.vector_store: Optional[Chroma] = None

        logger.info(
            f"Initialized VectorStoreManager with collection: {collection_name}, "
            f"persist_directory: {self.persist_directory}"
        )

    def create_vector_store(self, documents: List[Document]) -> Chroma:
        """Create a new vector store from documents.

        Args:
            documents: List of Document objects to add

        Returns:
            Chroma: The created vector store

        Example:
            >>> manager = VectorStoreManager()
            >>> chunks = split_documents(load_pdf("data/uploaded/doc.pdf"))
            >>> vector_store = manager.create_vector_store(chunks)
        """
        try:
            logger.info(f"Creating vector store with {len(documents)} documents")

            self.vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                collection_name=self.collection_name,
                persist_directory=self.persist_directory,
            )

            logger.info(
                f"Successfully created vector store with {len(documents)} documents"
            )
            return self.vector_store

        except Exception as e:
            logger.error(f"Error creating vector store: {e}")
            raise

    def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to an existing vector store.

        Args:
            documents: List of Document objects to add

        Returns:
            List[str]: List of document IDs

        Example:
            >>> manager = VectorStoreManager()
            >>> manager.load_vector_store()
            >>> ids = manager.add_documents(new_chunks)
        """
        if self.vector_store is None:
            logger.warning("No vector store loaded, creating new one")
            self.create_vector_store(documents)
            return []

        try:
            logger.info(f"Adding {len(documents)} documents to vector store")
            ids = self.vector_store.add_documents(documents)
            logger.info(f"Successfully added {len(ids)} documents")
            return ids

        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise

    def load_vector_store(self) -> Chroma:
        """Load an existing vector store from disk.

        Returns:
            Chroma: The loaded vector store

        Raises:
            FileNotFoundError: If persist directory doesn't exist

        Example:
            >>> manager = VectorStoreManager()
            >>> vector_store = manager.load_vector_store()
        """
        persist_path = Path(self.persist_directory)

        if not persist_path.exists():
            logger.error(f"Persist directory not found: {self.persist_directory}")
            raise FileNotFoundError(
                f"Vector store not found at: {self.persist_directory}. "
                "Please create a vector store first by uploading documents."
            )

        try:
            logger.info(f"Loading vector store from: {self.persist_directory}")

            self.vector_store = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory,
            )

            logger.info("Successfully loaded vector store")
            return self.vector_store

        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            raise

    def similarity_search(
        self,
        query: str,
        k: int | None = None,
    ) -> List[Document]:
        """Search for similar documents using semantic similarity.

        Args:
            query: Query text
            k: Number of results to return (default: from settings)

        Returns:
            List[Document]: List of similar documents

        Example:
            >>> manager = VectorStoreManager()
            >>> manager.load_vector_store()
            >>> results = manager.similarity_search("What is the schedule?", k=4)
        """
        if self.vector_store is None:
            logger.error("No vector store loaded")
            raise ValueError("Vector store not loaded. Call load_vector_store() first.")

        k = k or settings.top_k_results

        try:
            logger.info(f"Performing similarity search for: {query[:50]}...")
            results = self.vector_store.similarity_search(query, k=k)
            logger.info(f"Found {len(results)} similar documents")
            return results

        except Exception as e:
            logger.error(f"Error performing similarity search: {e}")
            raise

    def as_retriever(self, k: int | None = None):
        """Get a retriever interface for the vector store.

        Args:
            k: Number of results to return (default: from settings)

        Returns:
            VectorStoreRetriever: Retriever interface

        Example:
            >>> manager = VectorStoreManager()
            >>> manager.load_vector_store()
            >>> retriever = manager.as_retriever(k=4)
            >>> # Use retriever in LCEL chain
        """
        if self.vector_store is None:
            logger.error("No vector store loaded")
            raise ValueError("Vector store not loaded. Call load_vector_store() first.")

        k = k or settings.top_k_results

        return self.vector_store.as_retriever(
            search_kwargs={"k": k}
        )

    def delete_collection(self) -> None:
        """Delete the vector store collection.

        Warning:
            This operation cannot be undone!

        Example:
            >>> manager = VectorStoreManager()
            >>> manager.delete_collection()
        """
        try:
            if self.vector_store:
                logger.warning(f"Deleting collection: {self.collection_name}")
                self.vector_store.delete_collection()
                self.vector_store = None
                logger.info("Collection deleted successfully")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            raise
