"""Query routing chain using LCEL.

This module provides intelligent query routing to determine the best
retrieval strategy based on query complexity and requirements.
"""

from enum import Enum
from typing import Dict, Optional

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from src.config.settings import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)


class QueryType(str, Enum):
    """Types of queries for routing."""

    SIMPLE = "simple"  # Basic factual queries from single document
    CROSS_DOCUMENT = "cross_document"  # Queries requiring multiple documents
    AGGREGATION = "aggregation"  # Queries requiring counting/aggregation
    COMPLEX = "complex"  # Complex reasoning requiring agent


class QueryRoute(BaseModel):
    """Query routing decision."""

    query_type: QueryType = Field(
        description="Type of query for routing purposes"
    )
    reasoning: str = Field(
        description="Brief explanation of why this route was chosen"
    )
    metadata_filter: Optional[Dict[str, str]] = Field(
        default=None,
        description="Suggested metadata filter for retrieval"
    )


# Routing prompt template
ROUTING_TEMPLATE = """You are a query routing assistant for an educational document system. Analyze the user's query and determine the best routing strategy.

Query Types:
1. SIMPLE: Basic factual questions about a single document or entity
   - Example: "When does O1A have Mathematics on Monday?"
   - Example: "What is Raja Shoaib's office location?"

2. CROSS_DOCUMENT: Questions requiring information from multiple documents or entities
   - Example: "Which students in Level-III A have classes with Syed Bilal Hashmi?"
   - Example: "Show me all advisors and their student counts"

3. AGGREGATION: Questions requiring counting, grouping, or statistical analysis
   - Example: "How many students are advised by Raja Shoaib?"
   - Example: "Count all classes taught by Dr. Sarah Khan"

4. COMPLEX: Questions requiring multi-step reasoning or tool use
   - Example: "Find scheduling conflicts where Muhammad Hammad teaches two classes at the same time"
   - Example: "Generate a CSV report of all O-Level students"

Metadata Extraction:
- If the query mentions specific grade levels (O-Level, A-Level, Level-I/II/III), suggest a filter
- If the query mentions specific document types (timetable, student list), suggest a filter
- If the query mentions specific sections (A, B, C), suggest a filter

User Query: {query}

Analyze this query and respond with:
1. Query type (simple, cross_document, aggregation, or complex)
2. Brief reasoning (1-2 sentences)
3. Suggested metadata filter (if applicable, as JSON: {{"key": "value"}})

Response format:
Type: [query_type]
Reasoning: [your reasoning]
Filter: [metadata filter or "none"]
"""


class QueryRouter:
    """Routes queries to appropriate retrieval strategies."""

    def __init__(
        self,
        model: str | None = None,
        temperature: float = 0.0,
    ):
        """Initialize the query router.

        Args:
            model: LLM model name (default: from settings)
            temperature: LLM temperature for routing (default: 0.0 for consistency)
        """
        self.model = model or settings.llm_model
        self.temperature = temperature

        # Initialize LLM for routing
        self.llm = ChatOpenAI(
            model=self.model,
            temperature=self.temperature,
            api_key=settings.openai_api_key,
        )

        # Create routing prompt
        self.routing_prompt = ChatPromptTemplate.from_template(ROUTING_TEMPLATE)

        # Build routing chain using LCEL
        self.routing_chain = (
            self.routing_prompt
            | self.llm
            | StrOutputParser()
        )

        logger.info(f"Initialized QueryRouter with model: {self.model}")

    def route_query(self, query: str) -> QueryRoute:
        """Route a query to the appropriate strategy.

        Args:
            query: User query text

        Returns:
            QueryRoute: Routing decision with query type and metadata filter

        Example:
            >>> router = QueryRouter()
            >>> route = router.route_query("When does O1A have Math on Monday?")
            >>> print(route.query_type)  # QueryType.SIMPLE
            >>> print(route.metadata_filter)  # {"document_type": "timetable"}
        """
        logger.info(f"Routing query: {query[:50]}...")

        try:
            # Get routing decision from LLM
            response = self.routing_chain.invoke({"query": query})

            # Parse the response
            route = self._parse_routing_response(response, query)

            logger.info(
                f"Routed query as {route.query_type.value} | "
                f"Filter: {route.metadata_filter} | "
                f"Reasoning: {route.reasoning}"
            )

            return route

        except Exception as e:
            logger.error(f"Error routing query: {e}")
            # Fallback to simple routing
            logger.warning("Falling back to SIMPLE routing")
            return QueryRoute(
                query_type=QueryType.SIMPLE,
                reasoning="Fallback due to routing error",
                metadata_filter=None,
            )

    def _parse_routing_response(self, response: str, query: str) -> QueryRoute:
        """Parse the LLM routing response.

        Args:
            response: Raw LLM response
            query: Original query for fallback

        Returns:
            QueryRoute: Parsed routing decision
        """
        try:
            lines = response.strip().split("\n")
            query_type_str = None
            reasoning = None
            metadata_filter = None

            for line in lines:
                line = line.strip()
                if line.lower().startswith("type:"):
                    query_type_str = line.split(":", 1)[1].strip().lower()
                elif line.lower().startswith("reasoning:"):
                    reasoning = line.split(":", 1)[1].strip()
                elif line.lower().startswith("filter:"):
                    filter_str = line.split(":", 1)[1].strip()
                    if filter_str and filter_str.lower() != "none":
                        # Try to parse as dict-like string
                        metadata_filter = self._parse_filter_string(filter_str)

            # Map query type string to enum
            query_type = self._map_query_type(query_type_str)

            # Provide default reasoning if none found
            if not reasoning:
                reasoning = f"Classified as {query_type.value} query"

            return QueryRoute(
                query_type=query_type,
                reasoning=reasoning,
                metadata_filter=metadata_filter,
            )

        except Exception as e:
            logger.error(f"Error parsing routing response: {e}")
            logger.debug(f"Raw response: {response}")

            # Fallback: simple heuristic-based routing
            return self._heuristic_route(query)

    def _map_query_type(self, query_type_str: Optional[str]) -> QueryType:
        """Map query type string to enum.

        Args:
            query_type_str: Query type string from LLM

        Returns:
            QueryType: Mapped query type
        """
        if not query_type_str:
            return QueryType.SIMPLE

        query_type_str = query_type_str.lower().strip()

        if "cross" in query_type_str or "multi" in query_type_str:
            return QueryType.CROSS_DOCUMENT
        elif "aggregation" in query_type_str or "count" in query_type_str:
            return QueryType.AGGREGATION
        elif "complex" in query_type_str:
            return QueryType.COMPLEX
        else:
            return QueryType.SIMPLE

    def _parse_filter_string(self, filter_str: str) -> Optional[Dict[str, str]]:
        """Parse metadata filter string to dictionary.

        Args:
            filter_str: Filter string (e.g., '{"document_type": "timetable"}')

        Returns:
            Optional[Dict[str, str]]: Parsed filter or None
        """
        try:
            import json
            # Try to parse as JSON
            if "{" in filter_str:
                filter_dict = json.loads(filter_str)
                return filter_dict
        except:
            pass

        # Try to parse simple key:value format
        try:
            if ":" in filter_str:
                parts = filter_str.split(":", 1)
                key = parts[0].strip().strip('"\'')
                value = parts[1].strip().strip('"\'')
                return {key: value}
        except:
            pass

        return None

    def _heuristic_route(self, query: str) -> QueryRoute:
        """Fallback heuristic-based routing.

        Args:
            query: User query

        Returns:
            QueryRoute: Heuristic routing decision
        """
        query_lower = query.lower()

        # Check for aggregation keywords
        if any(keyword in query_lower for keyword in ["how many", "count", "total", "number of"]):
            return QueryRoute(
                query_type=QueryType.AGGREGATION,
                reasoning="Query contains aggregation keywords",
                metadata_filter=None,
            )

        # Check for cross-document keywords
        if any(keyword in query_lower for keyword in ["all", "which students", "list", "show me"]):
            return QueryRoute(
                query_type=QueryType.CROSS_DOCUMENT,
                reasoning="Query likely requires multiple documents",
                metadata_filter=None,
            )

        # Check for complex keywords
        if any(keyword in query_lower for keyword in ["conflict", "generate", "export", "csv"]):
            return QueryRoute(
                query_type=QueryType.COMPLEX,
                reasoning="Query requires complex reasoning or tools",
                metadata_filter=None,
            )

        # Default to simple
        return QueryRoute(
            query_type=QueryType.SIMPLE,
            reasoning="Simple factual query",
            metadata_filter=None,
        )


def route_query(query: str) -> QueryRoute:
    """Convenience function to route a query.

    Args:
        query: User query

    Returns:
        QueryRoute: Routing decision
    """
    router = QueryRouter()
    return router.route_query(query)
