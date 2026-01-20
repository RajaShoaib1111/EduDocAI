"""Conversation memory management for maintaining context across messages.

This module provides memory management for chat sessions, allowing the system
to maintain conversation history and context.
"""

from typing import Dict, List, Optional
from datetime import datetime

from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain_openai import ChatOpenAI

from src.config.settings import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)


class SessionMemoryManager:
    """Manages conversation memory for chat sessions."""

    def __init__(
        self,
        session_id: str,
        memory_type: str = "buffer",
        max_token_limit: int = 2000,
    ):
        """Initialize session memory manager.

        Args:
            session_id: Unique identifier for the chat session
            memory_type: Type of memory ("buffer" or "summary")
            max_token_limit: Maximum tokens to keep in memory
        """
        self.session_id = session_id
        self.memory_type = memory_type
        self.max_token_limit = max_token_limit
        self.created_at = datetime.now()

        # Initialize appropriate memory type
        if memory_type == "summary":
            llm = ChatOpenAI(
                model=settings.llm_model,
                temperature=0.0,
                api_key=settings.openai_api_key,
            )
            self.memory = ConversationSummaryMemory(
                llm=llm,
                max_token_limit=max_token_limit,
                return_messages=True,
            )
        else:  # buffer
            self.memory = ConversationBufferMemory(
                max_token_limit=max_token_limit,
                return_messages=True,
            )

        logger.info(
            f"Initialized {memory_type} memory for session {session_id}, "
            f"max_tokens: {max_token_limit}"
        )

    def add_user_message(self, message: str) -> None:
        """Add a user message to memory.

        Args:
            message: User's message content
        """
        self.memory.chat_memory.add_user_message(message)
        logger.debug(f"Added user message to session {self.session_id}")

    def add_ai_message(self, message: str) -> None:
        """Add an AI response to memory.

        Args:
            message: AI's response content
        """
        self.memory.chat_memory.add_ai_message(message)
        logger.debug(f"Added AI message to session {self.session_id}")

    def add_exchange(self, user_message: str, ai_message: str) -> None:
        """Add a complete conversation exchange.

        Args:
            user_message: User's message
            ai_message: AI's response
        """
        self.add_user_message(user_message)
        self.add_ai_message(ai_message)

    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history.

        Returns:
            List of message dictionaries with 'role' and 'content'
        """
        messages = self.memory.chat_memory.messages
        history = []
        for msg in messages:
            if hasattr(msg, 'type'):
                role = 'user' if msg.type == 'human' else 'assistant'
            else:
                role = 'assistant'
            history.append({
                'role': role,
                'content': msg.content if hasattr(msg, 'content') else str(msg)
            })
        return history

    def get_context(self) -> str:
        """Get conversation context as a formatted string.

        Returns:
            Formatted conversation history
        """
        history = self.get_history()
        context_lines = []
        for msg in history:
            role = msg['role'].capitalize()
            context_lines.append(f"{role}: {msg['content']}")
        return "\n".join(context_lines)

    def clear(self) -> None:
        """Clear conversation memory."""
        self.memory.clear()
        logger.info(f"Cleared memory for session {self.session_id}")

    def get_message_count(self) -> int:
        """Get number of messages in memory.

        Returns:
            Number of messages
        """
        return len(self.memory.chat_memory.messages)

    def get_stats(self) -> Dict[str, any]:
        """Get memory statistics.

        Returns:
            Dictionary with memory stats
        """
        return {
            'session_id': self.session_id,
            'memory_type': self.memory_type,
            'message_count': self.get_message_count(),
            'max_token_limit': self.max_token_limit,
            'created_at': self.created_at.isoformat(),
        }


class MultiSessionMemoryManager:
    """Manages memory for multiple concurrent sessions."""

    def __init__(self):
        """Initialize multi-session memory manager."""
        self.sessions: Dict[str, SessionMemoryManager] = {}
        logger.info("Initialized MultiSessionMemoryManager")

    def get_or_create_session(
        self,
        session_id: str,
        memory_type: str = "buffer",
        max_token_limit: int = 2000,
    ) -> SessionMemoryManager:
        """Get existing session or create new one.

        Args:
            session_id: Unique session identifier
            memory_type: Type of memory to create
            max_token_limit: Maximum tokens to keep

        Returns:
            SessionMemoryManager for the session
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionMemoryManager(
                session_id=session_id,
                memory_type=memory_type,
                max_token_limit=max_token_limit,
            )
            logger.info(f"Created new session: {session_id}")
        return self.sessions[session_id]

    def get_session(self, session_id: str) -> Optional[SessionMemoryManager]:
        """Get existing session memory.

        Args:
            session_id: Session identifier

        Returns:
            SessionMemoryManager if exists, None otherwise
        """
        return self.sessions.get(session_id)

    def delete_session(self, session_id: str) -> bool:
        """Delete a session.

        Args:
            session_id: Session to delete

        Returns:
            True if deleted, False if not found
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
            return True
        return False

    def clear_all_sessions(self) -> None:
        """Clear all sessions."""
        count = len(self.sessions)
        self.sessions.clear()
        logger.info(f"Cleared all {count} sessions")

    def get_active_session_count(self) -> int:
        """Get number of active sessions.

        Returns:
            Number of active sessions
        """
        return len(self.sessions)

    def get_all_stats(self) -> List[Dict[str, any]]:
        """Get statistics for all sessions.

        Returns:
            List of session statistics
        """
        return [session.get_stats() for session in self.sessions.values()]


# Global instance for the application
_global_memory_manager: Optional[MultiSessionMemoryManager] = None


def get_memory_manager() -> MultiSessionMemoryManager:
    """Get or create the global memory manager.

    Returns:
        MultiSessionMemoryManager instance
    """
    global _global_memory_manager
    if _global_memory_manager is None:
        _global_memory_manager = MultiSessionMemoryManager()
    return _global_memory_manager
