"""Text splitters for chunking documents.

This module provides text splitting functionality using LangChain's text splitters.
"""

from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config.settings import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)


class DocumentSplitter:
    """Document splitter that chunks documents into smaller pieces."""

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ):
        """Initialize the document splitter.

        Args:
            chunk_size: Size of each chunk in characters (default: from settings)
            chunk_overlap: Overlap between chunks in characters (default: from settings)
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            is_separator_regex=False,
            separators=[
                "\n\n",  # Paragraph breaks
                "\n",    # Line breaks
                ". ",    # Sentence endings
                ", ",    # Clause breaks
                " ",     # Word breaks
                "",      # Character breaks (last resort)
            ],
        )

        logger.info(
            f"Initialized DocumentSplitter with chunk_size={self.chunk_size}, "
            f"chunk_overlap={self.chunk_overlap}"
        )

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into smaller chunks.

        Args:
            documents: List of Document objects to split

        Returns:
            List[Document]: List of chunked Document objects

        Example:
            >>> splitter = DocumentSplitter()
            >>> docs = load_pdf("data/uploaded/timetable.pdf")
            >>> chunks = splitter.split_documents(docs)
            >>> print(f"Split {len(docs)} documents into {len(chunks)} chunks")
        """
        logger.info(f"Splitting {len(documents)} documents...")

        try:
            chunks = self.splitter.split_documents(documents)
            logger.info(
                f"Successfully split {len(documents)} documents into {len(chunks)} chunks"
            )
            return chunks
        except Exception as e:
            logger.error(f"Error splitting documents: {e}")
            raise

    def split_text(self, text: str) -> List[str]:
        """Split a single text string into chunks.

        Args:
            text: Text string to split

        Returns:
            List[str]: List of text chunks

        Example:
            >>> splitter = DocumentSplitter()
            >>> text = "Long text content..."
            >>> chunks = splitter.split_text(text)
        """
        try:
            chunks = self.splitter.split_text(text)
            logger.info(f"Split text into {len(chunks)} chunks")
            return chunks
        except Exception as e:
            logger.error(f"Error splitting text: {e}")
            raise


def split_documents(
    documents: List[Document],
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> List[Document]:
    """Convenience function to split documents into chunks.

    Args:
        documents: List of Document objects to split
        chunk_size: Size of each chunk (default: from settings)
        chunk_overlap: Overlap between chunks (default: from settings)

    Returns:
        List[Document]: List of chunked Document objects

    Example:
        >>> docs = load_pdf("data/uploaded/timetable.pdf")
        >>> chunks = split_documents(docs, chunk_size=500, chunk_overlap=100)
    """
    splitter = DocumentSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_documents(documents)
