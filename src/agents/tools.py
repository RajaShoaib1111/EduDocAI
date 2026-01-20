"""Custom tools for the educational document agent.

This module provides specialized tools for the ReAct agent to perform
complex reasoning tasks on educational documents.
"""

import csv
import re
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Dict, List, Optional

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from src.retrieval.vector_store import VectorStoreManager
from src.utils.logging import get_logger

logger = get_logger(__name__)


# ============================================================================
# Tool 1: Calculator
# ============================================================================

class CalculatorInput(BaseModel):
    """Input for calculator tool."""
    expression: str = Field(description="Mathematical expression to evaluate (e.g., '15 + 7', '100 / 4')")


def calculator(expression: str) -> str:
    """Safely evaluate mathematical expressions.

    Args:
        expression: Mathematical expression to evaluate

    Returns:
        str: Result of the calculation or error message

    Example:
        >>> calculator("15 + 7")
        "22"
        >>> calculator("100 / 4")
        "25.0"
    """
    try:
        # Clean the expression
        expression = expression.strip()

        # Only allow safe mathematical operations
        allowed_chars = set('0123456789+-*/()., ')
        if not all(c in allowed_chars for c in expression):
            return f"Error: Invalid characters in expression. Only numbers and operators (+, -, *, /) are allowed."

        # Evaluate the expression
        result = eval(expression, {"__builtins__": {}}, {})

        logger.info(f"Calculator: {expression} = {result}")
        return str(result)

    except ZeroDivisionError:
        return "Error: Division by zero"
    except SyntaxError:
        return f"Error: Invalid mathematical expression: {expression}"
    except Exception as e:
        logger.error(f"Calculator error: {e}")
        return f"Error: Could not evaluate expression: {str(e)}"


# ============================================================================
# Tool 2: Schedule Conflict Detector
# ============================================================================

class ConflictDetectorInput(BaseModel):
    """Input for schedule conflict detector."""
    teacher_name: str = Field(description="Name of the teacher to check for conflicts")
    context: str = Field(description="Relevant schedule information from documents")


def detect_schedule_conflicts(teacher_name: str, context: str) -> str:
    """Detect scheduling conflicts for a teacher.

    Analyzes schedule data to find times when a teacher is assigned to
    multiple classes simultaneously.

    Args:
        teacher_name: Name of the teacher to check
        context: Schedule information containing class times and assignments

    Returns:
        str: Description of conflicts found or "No conflicts found"

    Example:
        >>> detect_schedule_conflicts("Muhammad Hammad", schedule_text)
        "Found 2 conflicts:\n1. Monday 9:00 AM: Teaching both O1A and O1B\n..."
    """
    try:
        logger.info(f"Checking conflicts for teacher: {teacher_name}")

        # Parse schedule entries
        # Format: Day, Time, Class, Teacher, Room
        time_pattern = r'(\w+)\s+(\d{1,2}:\d{2}\s+[AP]M)\s*[-:]\s*\d{1,2}:\d{2}\s+[AP]M'

        # Find all mentions of the teacher with time information
        lines = context.split('\n')
        teacher_schedule = []

        for line in lines:
            # Check if line mentions the teacher
            if teacher_name.lower() in line.lower():
                # Try to extract time information
                time_match = re.search(time_pattern, line)
                if time_match:
                    day = time_match.group(1)
                    time = time_match.group(2)

                    # Extract class/section info
                    class_match = re.search(r'(O-?Level|A-?Level|Level-?[IVX]+)\s+Section\s+([A-Z])', line, re.IGNORECASE)
                    if not class_match:
                        class_match = re.search(r'\b([OA]\d[A-Z])\b', line)

                    class_name = class_match.group(0) if class_match else "Unknown Class"

                    teacher_schedule.append({
                        'day': day,
                        'time': time,
                        'class': class_name,
                        'line': line.strip()
                    })

        if not teacher_schedule:
            return f"No schedule information found for {teacher_name}"

        # Check for conflicts (same day and time)
        conflicts = []
        for i, entry1 in enumerate(teacher_schedule):
            for entry2 in teacher_schedule[i+1:]:
                if entry1['day'] == entry2['day'] and entry1['time'] == entry2['time']:
                    conflict_desc = (
                        f"{entry1['day']} {entry1['time']}: "
                        f"Teaching both {entry1['class']} and {entry2['class']}"
                    )
                    if conflict_desc not in conflicts:
                        conflicts.append(conflict_desc)

        if conflicts:
            result = f"Found {len(conflicts)} scheduling conflict(s) for {teacher_name}:\n"
            for i, conflict in enumerate(conflicts, 1):
                result += f"{i}. {conflict}\n"
            logger.info(f"Conflicts detected: {len(conflicts)}")
            return result.strip()
        else:
            logger.info("No conflicts found")
            return f"No scheduling conflicts found for {teacher_name}"

    except Exception as e:
        logger.error(f"Error detecting conflicts: {e}")
        return f"Error analyzing schedule: {str(e)}"


# ============================================================================
# Tool 3: CSV Exporter
# ============================================================================

class CSVExporterInput(BaseModel):
    """Input for CSV exporter."""
    data: str = Field(description="Data to export in text format")
    filename: str = Field(description="Output filename (without .csv extension)")


def export_to_csv(data: str, filename: str = "export") -> str:
    """Export structured data to CSV format.

    Args:
        data: Text data to structure and export
        filename: Name for the output file (without extension)

    Returns:
        str: Path to created CSV file or error message

    Example:
        >>> export_to_csv("Name,Count\\nRaja Shoaib,15\\nSyed Bilal,12", "advisors")
        "CSV exported successfully to: data/exports/advisors.csv"
    """
    try:
        logger.info(f"Exporting data to CSV: {filename}")

        # Create exports directory
        export_dir = Path("data/exports")
        export_dir.mkdir(parents=True, exist_ok=True)

        # Clean filename
        filename = re.sub(r'[^a-zA-Z0-9_-]', '_', filename)
        filepath = export_dir / f"{filename}.csv"

        # Try to parse the data
        # Assume data is either already CSV-like or needs to be structured
        lines = [line.strip() for line in data.split('\n') if line.strip()]

        if not lines:
            return "Error: No data to export"

        # Check if data looks like CSV (has commas)
        if ',' in lines[0]:
            # Data is already CSV-formatted
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                f.write(data)
        else:
            # Try to structure as simple list
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Item', 'Value'])
                for line in lines:
                    # Try to split on common delimiters
                    if ':' in line:
                        parts = line.split(':', 1)
                        writer.writerow([parts[0].strip(), parts[1].strip()])
                    elif '-' in line:
                        parts = line.split('-', 1)
                        writer.writerow([parts[0].strip(), parts[1].strip()])
                    else:
                        writer.writerow([line, ''])

        logger.info(f"CSV exported to: {filepath}")
        return f"CSV exported successfully to: {filepath}"

    except Exception as e:
        logger.error(f"Error exporting CSV: {e}")
        return f"Error exporting to CSV: {str(e)}"


# ============================================================================
# Tool 4: Document Search (using vector store)
# ============================================================================

class DocumentSearchInput(BaseModel):
    """Input for document search tool."""
    query: str = Field(description="Search query to find relevant information")
    document_type: Optional[str] = Field(default=None, description="Filter by document type (timetable, student_list, etc.)")


def create_document_search_tool(vector_store_manager: VectorStoreManager):
    """Create a document search tool with access to the vector store.

    Args:
        vector_store_manager: VectorStoreManager instance with loaded documents

    Returns:
        Tool: LangChain tool for document search
    """
    def search_documents(query: str, document_type: Optional[str] = None) -> str:
        """Search for information in the document collection.

        Args:
            query: What to search for
            document_type: Optional filter by document type

        Returns:
            str: Relevant information found in documents
        """
        try:
            logger.info(f"Searching documents: {query}")

            # Build filter
            filter_dict = {}
            if document_type:
                filter_dict['document_type'] = document_type

            # Search
            results = vector_store_manager.similarity_search(
                query,
                k=4,
                filter=filter_dict if filter_dict else None
            )

            if not results:
                return "No relevant information found in documents."

            # Combine results
            combined = "\n\n".join([
                f"[From {doc.metadata.get('source', 'unknown')}]\n{doc.page_content}"
                for doc in results
            ])

            logger.info(f"Found {len(results)} relevant documents")
            return combined

        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return f"Error searching documents: {str(e)}"

    @tool
    def search_documents_tool(query: str) -> str:
        """Search for information in uploaded educational documents.

        Use this to find facts, schedules, student information, etc.
        Input should be a search query.

        Args:
            query: What to search for

        Returns:
            Relevant information from documents
        """
        return search_documents(query)

    return search_documents_tool


# ============================================================================
# Tool Factory: Create all tools
# ============================================================================

def create_agent_tools(vector_store_manager: VectorStoreManager):
    """Create all tools for the agent.

    Args:
        vector_store_manager: VectorStoreManager with loaded documents

    Returns:
        List of tools for the agent to use
    """
    @tool
    def calculator_tool(expression: str) -> str:
        """Perform mathematical calculations.

        Useful for arithmetic operations like addition, subtraction, multiplication, division.

        Args:
            expression: Mathematical expression (e.g., '15 + 7' or '100 / 4')

        Returns:
            Result of calculation
        """
        return calculator(expression)

    @tool
    def detect_conflicts_tool(teacher_name: str, context: str) -> str:
        """Detect scheduling conflicts for a teacher.

        Finds times when a teacher is assigned to multiple classes simultaneously.

        Args:
            teacher_name: Name of the teacher
            context: Schedule information containing class times and assignments

        Returns:
            Description of conflicts found or "No conflicts found"
        """
        return detect_schedule_conflicts(teacher_name, context)

    @tool
    def export_csv_tool(data: str, filename: str = "export") -> str:
        """Export structured data to CSV format.

        Creates a CSV file from structured data.

        Args:
            data: Text data to export
            filename: Output filename (without .csv extension)

        Returns:
            Path to created CSV file
        """
        return export_to_csv(data, filename)

    tools = [
        calculator_tool,
        detect_conflicts_tool,
        export_csv_tool,
        create_document_search_tool(vector_store_manager),
    ]

    logger.info(f"Created {len(tools)} tools for agent")
    return tools
