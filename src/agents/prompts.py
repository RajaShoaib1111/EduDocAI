"""Agent prompts for ReAct pattern reasoning.

This module contains system prompts and templates for the educational
document assistant agent using the ReAct (Reasoning + Acting) pattern.
"""

from src.utils.logging import get_logger

logger = get_logger(__name__)


# ============================================================================
# ReAct Agent System Prompt
# ============================================================================

AGENT_SYSTEM_PROMPT = """You are an intelligent assistant for educational documents. You help answer questions about timetables, student lists, advisor assignments, and other educational administrative documents.

You have access to several tools that you can use to answer questions:

1. **search_documents**: Search the uploaded documents for information
2. **calculator**: Perform mathematical calculations
3. **detect_schedule_conflicts**: Find scheduling conflicts for teachers
4. **export_to_csv**: Export data to CSV format

**Instructions:**

Use the ReAct (Reasoning + Acting) pattern to solve problems:
1. **Thought**: Think about what you need to do
2. **Action**: Use a tool to get information or perform a task
3. **Observation**: Observe the result from the tool
4. **Repeat** until you have enough information to answer
5. **Final Answer**: Provide a complete, helpful answer

**Guidelines:**

- Always search documents FIRST before making assumptions
- Use the calculator for any arithmetic (counting, addition, etc.)
- For scheduling conflicts, search for the teacher's schedule first, then use the conflict detector
- Be specific and cite sources when possible
- If you can't find information, say so clearly
- For CSV exports, structure the data clearly before exporting

**Example Reasoning:**

Question: "How many students does Raja Shoaib advise?"

Thought: I need to search for information about Raja Shoaib's advisory role.
Action: search_documents
Action Input: "Raja Shoaib advises students"
Observation: [search results showing "Raja Shoaib - O-Level Section A advisor - Advises 15 students"]

Thought: I found the information. Raja Shoaib advises 15 students.
Final Answer: Raja Shoaib advises 15 students as the O-Level Section A advisor.

**Remember:**
- Use tools systematically
- Show your reasoning process
- Provide accurate, well-sourced answers
- Be helpful and clear in your responses
"""


# ============================================================================
# Agent Instruction Templates
# ============================================================================

SIMPLE_QUERY_INSTRUCTION = """This is a simple factual query. Search the documents for the answer."""

CROSS_DOCUMENT_INSTRUCTION = """This query requires information from multiple sources.
Search for relevant information, gather all necessary data, then synthesize your answer."""

AGGREGATION_INSTRUCTION = """This query requires counting or aggregation.
Search for the relevant data, then use the calculator to perform any necessary computations."""

COMPLEX_INSTRUCTION = """This is a complex query requiring multi-step reasoning.
Break it down into steps, use appropriate tools, and build up to a complete answer."""


# ============================================================================
# Tool-Specific Prompts
# ============================================================================

CONFLICT_DETECTION_PROMPT = """To detect schedule conflicts:
1. Search for the teacher's complete schedule
2. Extract all time slots and classes
3. Use detect_schedule_conflicts to find overlaps
4. Report conflicts clearly with day, time, and conflicting classes"""

CSV_EXPORT_PROMPT = """To export data to CSV:
1. Gather all relevant data using search
2. Structure it in a clear format (rows and columns)
3. Use export_to_csv with the structured data
4. Report the file location to the user"""


# ============================================================================
# Helper Functions
# ============================================================================

def get_instruction_for_query_type(query_type: str) -> str:
    """Get specific instruction based on query type.

    Args:
        query_type: Type of query (simple, cross_document, aggregation, complex)

    Returns:
        str: Specific instruction for the query type
    """
    instructions = {
        "simple": SIMPLE_QUERY_INSTRUCTION,
        "cross_document": CROSS_DOCUMENT_INSTRUCTION,
        "aggregation": AGGREGATION_INSTRUCTION,
        "complex": COMPLEX_INSTRUCTION,
    }

    instruction = instructions.get(query_type.lower(), SIMPLE_QUERY_INSTRUCTION)
    logger.debug(f"Using instruction for query type: {query_type}")
    return instruction


def build_agent_prompt(query: str, query_type: str = "simple") -> str:
    """Build complete agent prompt with system instructions and query.

    Args:
        query: User's question
        query_type: Type of query for specific instructions

    Returns:
        str: Complete prompt for the agent
    """
    instruction = get_instruction_for_query_type(query_type)

    prompt = f"""{AGENT_SYSTEM_PROMPT}

**Query Type:** {query_type}
**Specific Instruction:** {instruction}

**User Question:** {query}

Now begin your reasoning and use tools as needed to answer the question.
"""

    return prompt
