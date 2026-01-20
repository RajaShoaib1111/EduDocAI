"""Q&A chain using LCEL (LangChain Expression Language).

This module provides a RAG chain for question answering over documents.
"""

from typing import Dict, Any

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

from src.config.settings import settings
from src.retrieval.vector_store import VectorStoreManager
from src.utils.logging import get_logger

logger = get_logger(__name__)


# Default prompt template for Q&A
DEFAULT_QA_TEMPLATE = """You are a helpful assistant that answers questions based on the provided context. Answer the question based only on the following context:

Context:
{context}

Question: {question}

Instructions:
- Provide a clear, concise answer based on the context
- If the answer is not in the context, say "I don't have enough information to answer that question."
- Include specific details and examples when available
- Cite sources when possible

Answer:"""


class QAChain:
    """Question-answering chain using RAG with LCEL."""

    def __init__(
        self,
        vector_store_manager: VectorStoreManager,
        model: str | None = None,
        temperature: float | None = None,
        prompt_template: str | None = None,
    ):
        """Initialize the Q&A chain.

        Args:
            vector_store_manager: VectorStoreManager instance with loaded vector store
            model: LLM model name (default: from settings)
            temperature: LLM temperature (default: from settings)
            prompt_template: Custom prompt template (default: DEFAULT_QA_TEMPLATE)
        """
        self.vector_store_manager = vector_store_manager
        self.model = model or settings.llm_model
        self.temperature = temperature if temperature is not None else settings.temperature
        self.prompt_template = prompt_template or DEFAULT_QA_TEMPLATE

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.model,
            temperature=self.temperature,
            openai_api_key=settings.openai_api_key,
            streaming=True,
        )

        # Create prompt
        self.prompt = ChatPromptTemplate.from_template(self.prompt_template)

        # Get retriever
        self.retriever = self.vector_store_manager.as_retriever()

        # Build LCEL chain
        self.chain = self._build_chain()

        logger.info(
            f"Initialized QAChain with model: {self.model}, "
            f"temperature: {self.temperature}"
        )

    def _build_chain(self):
        """Build the LCEL chain for Q&A.

        Returns:
            Runnable: LCEL chain
        """
        # Helper function to format documents
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        # Build chain using LCEL pipe operator
        chain = (
            {
                "context": self.retriever | format_docs,
                "question": RunnablePassthrough(),
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

        return chain

    def invoke(self, question: str) -> str:
        """Run the Q&A chain on a question.

        Args:
            question: User's question

        Returns:
            str: Generated answer

        Example:
            >>> chain = QAChain(vector_store_manager)
            >>> answer = chain.invoke("What is the class schedule for Monday?")
            >>> print(answer)
        """
        try:
            logger.info(f"Processing question: {question[:50]}...")
            answer = self.chain.invoke(question)
            logger.info("Successfully generated answer")
            return answer
        except Exception as e:
            logger.error(f"Error processing question: {e}")
            raise

    async def ainvoke(self, question: str) -> str:
        """Async version of invoke.

        Args:
            question: User's question

        Returns:
            str: Generated answer

        Example:
            >>> chain = QAChain(vector_store_manager)
            >>> answer = await chain.ainvoke("What is the schedule?")
        """
        try:
            logger.info(f"Processing question (async): {question[:50]}...")
            answer = await self.chain.ainvoke(question)
            logger.info("Successfully generated answer")
            return answer
        except Exception as e:
            logger.error(f"Error processing question: {e}")
            raise

    def stream(self, question: str):
        """Stream the answer token by token.

        Args:
            question: User's question

        Yields:
            str: Answer tokens

        Example:
            >>> chain = QAChain(vector_store_manager)
            >>> for token in chain.stream("What is the schedule?"):
            ...     print(token, end="", flush=True)
        """
        try:
            logger.info(f"Streaming answer for: {question[:50]}...")
            for token in self.chain.stream(question):
                yield token
        except Exception as e:
            logger.error(f"Error streaming answer: {e}")
            raise

    async def astream(self, question: str):
        """Async stream the answer token by token.

        Args:
            question: User's question

        Yields:
            str: Answer tokens

        Example:
            >>> chain = QAChain(vector_store_manager)
            >>> async for token in chain.astream("What is the schedule?"):
            ...     print(token, end="", flush=True)
        """
        try:
            logger.info(f"Streaming answer (async) for: {question[:50]}...")
            async for token in self.chain.astream(question):
                yield token
        except Exception as e:
            logger.error(f"Error streaming answer: {e}")
            raise

    def get_source_documents(self, question: str):
        """Get the source documents used for answering a question.

        Args:
            question: User's question

        Returns:
            List[Document]: Source documents

        Example:
            >>> chain = QAChain(vector_store_manager)
            >>> sources = chain.get_source_documents("What is the schedule?")
            >>> for doc in sources:
            ...     print(doc.metadata)
        """
        try:
            logger.info(f"Retrieving source documents for: {question[:50]}...")
            sources = self.retriever.invoke(question)
            logger.info(f"Retrieved {len(sources)} source documents")
            return sources
        except Exception as e:
            logger.error(f"Error retrieving source documents: {e}")
            raise


def create_qa_chain(
    vector_store_manager: VectorStoreManager,
    model: str | None = None,
    temperature: float | None = None,
) -> QAChain:
    """Convenience function to create a Q&A chain.

    Args:
        vector_store_manager: VectorStoreManager instance
        model: LLM model name (default: from settings)
        temperature: LLM temperature (default: from settings)

    Returns:
        QAChain: Configured Q&A chain

    Example:
        >>> manager = VectorStoreManager()
        >>> manager.load_vector_store()
        >>> chain = create_qa_chain(manager)
        >>> answer = chain.invoke("What is the schedule?")
    """
    return QAChain(
        vector_store_manager=vector_store_manager,
        model=model,
        temperature=temperature,
    )
