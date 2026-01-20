"""Document loaders for processing various file types.

This module provides loaders for PDF and text documents using LangChain.
"""

from pathlib import Path
from typing import List

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document

from src.utils.logging import get_logger

logger = get_logger(__name__)


class DocumentLoader:
    """Main document loader that handles multiple file types."""

    SUPPORTED_EXTENSIONS = {".pdf", ".txt"}

    @classmethod
    def load_document(cls, file_path: str | Path) -> List[Document]:
        """Load a document from the specified file path.

        Args:
            file_path: Path to the document file

        Returns:
            List[Document]: List of LangChain Document objects

        Raises:
            ValueError: If file type is not supported
            FileNotFoundError: If file does not exist
        """
        file_path = Path(file_path)

        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")

        extension = file_path.suffix.lower()
        if extension not in cls.SUPPORTED_EXTENSIONS:
            logger.error(f"Unsupported file type: {extension}")
            raise ValueError(
                f"Unsupported file type: {extension}. "
                f"Supported types: {cls.SUPPORTED_EXTENSIONS}"
            )

        logger.info(f"Loading document: {file_path}")

        if extension == ".pdf":
            return cls._load_pdf(file_path)
        elif extension == ".txt":
            return cls._load_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {extension}")

    @staticmethod
    def _load_pdf(file_path: Path) -> List[Document]:
        """Load a PDF document.

        Args:
            file_path: Path to the PDF file

        Returns:
            List[Document]: List of Document objects, one per page
        """
        try:
            loader = PyPDFLoader(str(file_path))
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} pages from PDF: {file_path.name}")
            return documents
        except Exception as e:
            logger.error(f"Error loading PDF {file_path}: {e}")
            raise

    @staticmethod
    def _load_text(file_path: Path) -> List[Document]:
        """Load a text document.

        Args:
            file_path: Path to the text file

        Returns:
            List[Document]: List containing a single Document object
        """
        try:
            loader = TextLoader(str(file_path), encoding="utf-8")
            documents = loader.load()
            logger.info(f"Loaded text file: {file_path.name}")
            return documents
        except Exception as e:
            logger.error(f"Error loading text file {file_path}: {e}")
            raise


def load_pdf(file_path: str | Path) -> List[Document]:
    """Convenience function to load a PDF document.

    Args:
        file_path: Path to the PDF file

    Returns:
        List[Document]: List of Document objects

    Example:
        >>> docs = load_pdf("data/uploaded/timetable.pdf")
        >>> print(f"Loaded {len(docs)} pages")
    """
    return DocumentLoader._load_pdf(Path(file_path))


def load_text(file_path: str | Path) -> List[Document]:
    """Convenience function to load a text document.

    Args:
        file_path: Path to the text file

    Returns:
        List[Document]: List of Document objects

    Example:
        >>> docs = load_text("data/uploaded/notes.txt")
        >>> print(docs[0].page_content)
    """
    return DocumentLoader._load_text(Path(file_path))
