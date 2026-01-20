"""ReAct agent for complex educational document queries.

This module implements a ReAct (Reasoning + Acting) agent using LangChain
for handling complex multi-step queries.
"""

from typing import Any, Dict, List, Optional

from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

from src.agents.prompts import AGENT_SYSTEM_PROMPT, get_instruction_for_query_type
from src.agents.tools import create_agent_tools
from src.config.settings import settings
from src.retrieval.vector_store import VectorStoreManager
from src.utils.logging import get_logger

logger = get_logger(__name__)




# ============================================================================
# Educational Document Agent
# ============================================================================

class EducationalDocumentAgent:
    """ReAct agent for answering complex questions about educational documents."""

    def __init__(
        self,
        vector_store_manager: VectorStoreManager,
        model: str | None = None,
        temperature: float = 0.0,
        max_iterations: int = 10,
        verbose: bool = True,
    ):
        """Initialize the educational document agent.

        Args:
            vector_store_manager: VectorStoreManager with loaded documents
            model: LLM model name (default: from settings)
            temperature: LLM temperature (default: 0.0 for consistency)
            max_iterations: Maximum agent iterations (default: 10)
            verbose: Enable verbose logging (default: True)
        """
        self.vector_store_manager = vector_store_manager
        self.model = model or settings.llm_model
        self.temperature = temperature
        self.max_iterations = max_iterations
        self.verbose = verbose

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.model,
            temperature=self.temperature,
            api_key=settings.openai_api_key,
        )

        # Create tools
        self.tools = create_agent_tools(vector_store_manager)

        # Create ReAct agent using LangGraph
        self.agent_executor = create_react_agent(
            model=self.llm,
            tools=self.tools,
        )

        logger.info(
            f"Initialized EducationalDocumentAgent with {len(self.tools)} tools, "
            f"model: {self.model}"
        )

    def invoke(
        self,
        query: str,
        query_type: str = "complex",
    ) -> Dict[str, Any]:
        """Run the agent on a query.

        Args:
            query: User's question
            query_type: Type of query for context (default: "complex")

        Returns:
            Dict containing 'output' and 'intermediate_steps'

        Example:
            >>> agent = EducationalDocumentAgent(vector_store_manager)
            >>> result = agent.invoke("Find conflicts for Muhammad Hammad")
            >>> print(result['output'])
        """
        try:
            logger.info(f"Agent processing query (type: {query_type}): {query[:50]}...")

            # Add instruction based on query type
            instruction = get_instruction_for_query_type(query_type)
            enhanced_query = f"{instruction}\n\nQuestion: {query}"

            # Run the agent (LangGraph returns messages)
            result = self.agent_executor.invoke({"messages": [("user", enhanced_query)]})

            # Extract the final message
            messages = result.get("messages", [])
            if messages:
                final_message = messages[-1]
                output = final_message.content if hasattr(final_message, 'content') else str(final_message)
            else:
                output = "No response generated"

            logger.info("Agent completed successfully")
            return {
                "output": output,
                "intermediate_steps": messages[:-1] if len(messages) > 1 else []
            }

        except Exception as e:
            logger.error(f"Error running agent: {e}")
            return {
                "output": f"I encountered an error while processing your question: {str(e)}",
                "intermediate_steps": []
            }

    async def ainvoke(
        self,
        query: str,
        query_type: str = "complex",
    ) -> Dict[str, Any]:
        """Async version of invoke.

        Args:
            query: User's question
            query_type: Type of query for context

        Returns:
            Dict containing 'output' and 'intermediate_steps'
        """
        try:
            logger.info(f"Agent processing query (async, type: {query_type}): {query[:50]}...")

            # Add instruction based on query type
            instruction = get_instruction_for_query_type(query_type)
            enhanced_query = f"{instruction}\n\nQuestion: {query}"

            # Run the agent (LangGraph returns messages)
            result = await self.agent_executor.ainvoke({"messages": [("user", enhanced_query)]})

            # Extract the final message
            messages = result.get("messages", [])
            if messages:
                final_message = messages[-1]
                output = final_message.content if hasattr(final_message, 'content') else str(final_message)
            else:
                output = "No response generated"

            logger.info("Agent completed successfully")
            return {
                "output": output,
                "intermediate_steps": messages[:-1] if len(messages) > 1 else []
            }

        except Exception as e:
            logger.error(f"Error running agent: {e}")
            return {
                "output": f"I encountered an error while processing your question: {str(e)}",
                "intermediate_steps": []
            }

    async def astream(
        self,
        query: str,
        query_type: str = "complex",
    ):
        """Stream agent execution (yields intermediate steps).

        Args:
            query: User's question
            query_type: Type of query for context

        Yields:
            Agent execution events
        """
        try:
            logger.info(f"Agent streaming query (type: {query_type}): {query[:50]}...")

            # Add instruction based on query type
            instruction = get_instruction_for_query_type(query_type)
            enhanced_query = f"{instruction}\n\nQuestion: {query}"

            # Stream the agent execution
            async for event in self.agent_executor.astream({"messages": [("user", enhanced_query)]}):
                yield event

            logger.info("Agent streaming completed")

        except Exception as e:
            logger.error(f"Error streaming agent: {e}")
            yield {
                "output": f"I encountered an error while processing your question: {str(e)}"
            }

    def get_tool_names(self) -> List[str]:
        """Get list of available tool names.

        Returns:
            List[str]: Names of available tools
        """
        return [tool.name for tool in self.tools]

    def get_tool_descriptions(self) -> Dict[str, str]:
        """Get descriptions of all available tools.

        Returns:
            Dict[str, str]: Tool names mapped to descriptions
        """
        return {tool.name: tool.description for tool in self.tools}


# ============================================================================
# Convenience function
# ============================================================================

def create_agent(
    vector_store_manager: VectorStoreManager,
    verbose: bool = True,
) -> EducationalDocumentAgent:
    """Create an educational document agent.

    Args:
        vector_store_manager: VectorStoreManager with loaded documents
        verbose: Enable verbose logging

    Returns:
        EducationalDocumentAgent: Configured agent ready to use
    """
    return EducationalDocumentAgent(
        vector_store_manager=vector_store_manager,
        verbose=verbose,
    )
