"""Metadata extraction for educational documents.

This module provides functionality to extract metadata from documents including:
- Document type (timetable, student_list, syllabus, etc.)
- Grade level (O-Level, A-Level, Level-I, Level-II, Level-III)
- Section (A, B, C, etc.)
- Academic year/term
"""

import re
from typing import Dict, List, Optional
from langchain_core.documents import Document

from src.utils.logging import get_logger

logger = get_logger(__name__)


class MetadataExtractor:
    """Extract metadata from educational documents."""

    # Document type patterns
    DOCUMENT_TYPE_PATTERNS = {
        "timetable": [
            r"timetable",
            r"schedule",
            r"class schedule",
            r"teacher roster",
            r"\d+:\d+\s*[AP]M",  # Time patterns
        ],
        "student_list": [
            r"student\s+list",
            r"class\s+roster",
            r"enrollment",
            r"student\s+roll",
        ],
        "syllabus": [
            r"syllabus",
            r"course\s+outline",
            r"curriculum",
            r"learning\s+objectives",
        ],
        "exam_schedule": [
            r"exam\s+schedule",
            r"examination\s+timetable",
            r"test\s+schedule",
            r"midterm",
            r"final\s+exam",
        ],
        "advisor_assignment": [
            r"advisor",
            r"advise[sd]",
            r"guidance\s+counselor",
        ],
    }

    # Grade level patterns
    GRADE_PATTERNS = {
        "O-Level": [r"o-level", r"o\s+level", r"olevel", r"\bO1\b", r"\bO2\b"],
        "A-Level": [r"a-level", r"a\s+level", r"alevel", r"\bA1\b", r"\bA2\b"],
        "Level-I": [r"level-i\b", r"level\s+i\b", r"level\s+1\b"],
        "Level-II": [r"level-ii\b", r"level\s+ii\b", r"level\s+2\b"],
        "Level-III": [r"level-iii\b", r"level\s+iii\b", r"level\s+3\b"],
    }

    # Section patterns
    SECTION_PATTERN = r"section\s+([A-Za-z])|(?:^|\s)([A-Za-z])(?:\s+section)"

    def extract_metadata(
        self, document: Document, filename: Optional[str] = None
    ) -> Dict[str, str]:
        """Extract metadata from a document.

        Args:
            document: The document to extract metadata from
            filename: Optional filename for additional context

        Returns:
            Dictionary containing extracted metadata
        """
        content = document.page_content.lower()
        metadata = {}

        # Extract document type
        doc_type = self._extract_document_type(content, filename)
        if doc_type:
            metadata["document_type"] = doc_type
            logger.debug(f"Extracted document type: {doc_type}")

        # Extract grade levels (can have multiple)
        grade_levels = self._extract_grade_levels(content)
        if grade_levels:
            metadata["grade_levels"] = ",".join(grade_levels)
            logger.debug(f"Extracted grade levels: {grade_levels}")

        # Extract sections
        sections = self._extract_sections(content)
        if sections:
            metadata["sections"] = ",".join(sections)
            logger.debug(f"Extracted sections: {sections}")

        # Extract academic year if present
        academic_year = self._extract_academic_year(content)
        if academic_year:
            metadata["academic_year"] = academic_year
            logger.debug(f"Extracted academic year: {academic_year}")

        logger.info(f"Extracted metadata: {metadata}")
        return metadata

    def _extract_document_type(
        self, content: str, filename: Optional[str] = None
    ) -> Optional[str]:
        """Extract document type from content and filename.

        Args:
            content: Document content (lowercase)
            filename: Optional filename

        Returns:
            Document type or None
        """
        # Check filename first if available
        if filename:
            filename_lower = filename.lower()
            for doc_type, patterns in self.DOCUMENT_TYPE_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, filename_lower):
                        return doc_type

        # Check content
        type_scores = {}
        for doc_type, patterns in self.DOCUMENT_TYPE_PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, content)
                score += len(matches)
            if score > 0:
                type_scores[doc_type] = score

        if type_scores:
            # Return the type with highest score
            return max(type_scores.items(), key=lambda x: x[1])[0]

        return None

    def _extract_grade_levels(self, content: str) -> List[str]:
        """Extract grade levels from content.

        Args:
            content: Document content (lowercase)

        Returns:
            List of grade levels found
        """
        grade_levels = set()

        for grade, patterns in self.GRADE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    grade_levels.add(grade)
                    break  # Only need one match per grade

        return sorted(list(grade_levels))

    def _extract_sections(self, content: str) -> List[str]:
        """Extract sections from content.

        Args:
            content: Document content (lowercase)

        Returns:
            List of sections found (A, B, C, etc.)
        """
        sections = set()

        # Find all section mentions
        matches = re.finditer(self.SECTION_PATTERN, content, re.IGNORECASE)
        for match in matches:
            section = (match.group(1) or match.group(2)).upper()
            if section and section.isalpha() and len(section) == 1:
                sections.add(section)

        # Also look for patterns like "O1A", "Level-III A"
        grade_section_patterns = [
            r"o-?level\s+section\s+([A-Z])",
            r"a-?level\s+section\s+([A-Z])",
            r"level-?[IVX]+\s+section\s+([A-Z])",
            r"\b[OA]\d([A-Z])\b",  # O1A, A2B, etc.
        ]

        for pattern in grade_section_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                section = match.group(1).upper()
                if section.isalpha() and len(section) == 1:
                    sections.add(section)

        return sorted(list(sections))

    def _extract_academic_year(self, content: str) -> Optional[str]:
        """Extract academic year from content.

        Args:
            content: Document content (lowercase)

        Returns:
            Academic year string or None
        """
        # Look for year patterns
        year_patterns = [
            r"academic\s+year\s*:?\s*(\d{4}[-/]\d{4})",
            r"year\s*:?\s*(\d{4}[-/]\d{4})",
            r"(\d{4}[-/]\d{4})\s+academic\s+year",
            r"semester\s+(\d+)\s+(\d{4})",
        ]

        for pattern in year_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def enrich_documents(
        self, documents: List[Document], filename: Optional[str] = None
    ) -> List[Document]:
        """Enrich documents with extracted metadata.

        Args:
            documents: List of documents to enrich
            filename: Optional filename for context

        Returns:
            List of documents with enriched metadata
        """
        if not documents:
            return documents

        # Extract metadata from first document (assumed to be representative)
        # For chunked documents, the metadata applies to all chunks
        extracted_metadata = self.extract_metadata(documents[0], filename)

        # Add extracted metadata to all documents
        enriched_docs = []
        for doc in documents:
            # Merge existing metadata with extracted metadata
            new_metadata = {**doc.metadata, **extracted_metadata}

            # Add source filename if provided
            if filename:
                new_metadata["source"] = filename

            # Create new document with enriched metadata
            enriched_doc = Document(
                page_content=doc.page_content, metadata=new_metadata
            )
            enriched_docs.append(enriched_doc)

        logger.info(
            f"Enriched {len(enriched_docs)} documents with metadata: {extracted_metadata}"
        )
        return enriched_docs


def extract_metadata_from_documents(
    documents: List[Document], filename: Optional[str] = None
) -> List[Document]:
    """Convenience function to extract and enrich document metadata.

    Args:
        documents: List of documents to process
        filename: Optional filename for context

    Returns:
        List of documents with enriched metadata
    """
    extractor = MetadataExtractor()
    return extractor.enrich_documents(documents, filename)
