"""Chainlit application for EduDocAI.

This is the main entry point for the interactive chat interface.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import chainlit as cl

from src.agents.agent import EducationalDocumentAgent
from src.chains.qa_chain import QAChain
from src.chains.routing_chain import QueryRouter, QueryType
from src.config.settings import settings
from src.document_processing.loaders import DocumentLoader
from src.document_processing.metadata import extract_metadata_from_documents
from src.document_processing.splitters import DocumentSplitter
from src.retrieval.vector_store import VectorStoreManager
from src.utils.logging import get_logger

logger = get_logger(__name__)


# Global variables
vector_store_manager: Optional[VectorStoreManager] = None
qa_chain: Optional[QAChain] = None
query_router: Optional[QueryRouter] = None
agent: Optional[EducationalDocumentAgent] = None


@cl.on_chat_start
async def start():
    """Initialize the chat session."""
    global vector_store_manager, qa_chain, query_router, agent

    logger.info("Starting new chat session")

    # Initialize query router
    query_router = QueryRouter()

    # Welcome message
    await cl.Message(
        content=f"""# Welcome to {settings.app_name}! 📚

I'm your AI assistant for educational documents. Here's how I can help:

**Getting Started:**
1. Upload a PDF or text document using the upload button below
2. I'll process and index your document
3. Ask me questions about the content!

**What I can do:**
- Answer questions about uploaded documents
- Find specific information quickly
- Explain concepts from the documents
- Summarize content

**Tips:**
- Start by uploading a document (timetable, student list, syllabus, etc.)
- Ask specific questions for better answers
- You can upload multiple documents

Ready to begin? Upload your first document! 📄
"""
    ).send()

    # Try to load existing vector store
    try:
        vector_store_manager = VectorStoreManager()
        vector_store_manager.load_vector_store()
        qa_chain = QAChain(vector_store_manager)

        # Initialize agent with loaded vector store
        agent = EducationalDocumentAgent(vector_store_manager, verbose=False)

        await cl.Message(
            content="✅ **Loaded existing document collection.** You can ask questions or upload new documents.\n\n"
                    "🤖 **Agent capabilities enabled**: I can now handle complex queries with multi-step reasoning!",
            author="System",
        ).send()

        logger.info("Loaded existing vector store and initialized agent")

    except FileNotFoundError:
        logger.info("No existing vector store found - waiting for document upload")
        await cl.Message(
            content="💡 **No documents loaded yet.** Please upload a document to get started.",
            author="System",
        ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming user messages."""
    global qa_chain, vector_store_manager, query_router, agent

    logger.info(f"Received message: {message.content[:50]}...")

    # Check for file attachments
    if message.elements:
        await handle_file_upload(message.elements)
        return

    # Check if QA chain is available
    if qa_chain is None:
        await cl.Message(
            content="⚠️ **Please upload a document first!** I need documents to answer questions.",
        ).send()
        return

    try:
        # Route the query
        route = None
        if query_router:
            route = query_router.route_query(message.content)
            logger.info(
                f"Query routed as {route.query_type.value} | "
                f"Filter: {route.metadata_filter}"
            )

            # Show routing info in debug mode
            if settings.debug:
                await cl.Message(
                    content=f"🔍 **Query Type:** {route.query_type.value}\n"
                            f"**Reasoning:** {route.reasoning}\n"
                            f"**Filter:** {route.metadata_filter or 'None'}",
                    author="System",
                ).send()

        # Handle different query types
        if route and route.query_type == QueryType.COMPLEX and agent:
            # Use agent for complex queries
            await cl.Message(
                content="🤖 **Using agent for complex reasoning...**",
                author="System",
            ).send()

            # Create a message placeholder
            msg = cl.Message(content="")
            await msg.send()

            # Run agent (note: full streaming not yet implemented for agent)
            result = await agent.ainvoke(message.content, query_type=route.query_type.value)

            # Update message with agent output
            await msg.stream_token(result['output'])
            await msg.update()

            logger.info("Agent completed successfully")

        else:
            # Use basic RAG chain for simple queries
            msg = cl.Message(content="")
            await msg.send()

            # Stream the answer
            async for token in qa_chain.astream(message.content):
                await msg.stream_token(token)

            # Finalize the message
            await msg.update()

            logger.info("Successfully answered question")

    except Exception as e:
        logger.error(f"Error processing question: {e}")
        await cl.Message(
            content=f"❌ **Error:** {str(e)}\n\nPlease try again or upload a new document.",
        ).send()


async def handle_file_upload(files: list):
    """Handle file uploads."""
    global vector_store_manager, qa_chain

    logger.info(f"Received {len(files)} file(s) for upload")

    # Show processing message
    processing_msg = cl.Message(
        content=f"📄 Processing {len(files)} file(s)... This may take a moment.",
        author="System",
    )
    await processing_msg.send()

    try:
        # Create data directory if it doesn't exist
        upload_dir = Path("data/uploaded")
        upload_dir.mkdir(parents=True, exist_ok=True)

        all_chunks = []

        for file in files:
            # Save file to upload directory
            file_path = upload_dir / file.name

            # Read file content based on Chainlit file object attributes
            try:
                # Try to get content from path (most common)
                if hasattr(file, 'path') and file.path:
                    with open(file.path, 'rb') as f:
                        content = f.read()
                # Fallback to content attribute
                elif hasattr(file, 'content') and file.content is not None:
                    content = file.content
                else:
                    logger.error(f"Cannot read file: {file.name} - no valid path or content")
                    await cl.Message(
                        content=f"⚠️ Cannot read file: {file.name}. Please try again.",
                        author="System",
                    ).send()
                    continue

                # Write to upload directory
                with open(file_path, "wb") as f:
                    f.write(content)

            except Exception as e:
                logger.error(f"Error reading file {file.name}: {e}")
                await cl.Message(
                    content=f"⚠️ Error reading file: {file.name}. Error: {str(e)}",
                    author="System",
                ).send()
                continue

            logger.info(f"Processing file: {file.name}")

            # Update progress
            await processing_msg.update()

            # Load document
            documents = DocumentLoader.load_document(file_path)

            # Extract and enrich metadata
            documents = extract_metadata_from_documents(documents, filename=file.name)
            logger.info(f"Extracted metadata for {file.name}")

            # Split into chunks
            splitter = DocumentSplitter()
            chunks = splitter.split_documents(documents)

            all_chunks.extend(chunks)

            logger.info(f"Split {file.name} into {len(chunks)} chunks with metadata")

        # Create or update vector store
        if vector_store_manager is None:
            vector_store_manager = VectorStoreManager()

        if vector_store_manager.vector_store is None:
            # Create new vector store
            vector_store_manager.create_vector_store(all_chunks)
            logger.info("Created new vector store")
        else:
            # Add to existing vector store
            vector_store_manager.add_documents(all_chunks)
            logger.info("Added documents to existing vector store")

        # Create/update QA chain and agent
        qa_chain = QAChain(vector_store_manager)
        agent = EducationalDocumentAgent(vector_store_manager, verbose=False)

        # Success message
        file_names = ", ".join([f.name for f in files])
        await cl.Message(
            content=f"""✅ **Successfully processed {len(files)} file(s)!**

**Files:** {file_names}
**Chunks created:** {len(all_chunks)}

You can now ask questions about your documents! Try asking:
- "What is this document about?"
- "Summarize the main points"
- Or any specific question about the content
""",
            author="System",
        ).send()

        logger.info(f"Successfully processed {len(files)} file(s)")

    except Exception as e:
        logger.error(f"Error processing files: {e}")
        await cl.Message(
            content=f"❌ **Error processing files:** {str(e)}\n\nPlease try again with a different file.",
            author="System",
        ).send()


if __name__ == "__main__":
    # Note: This file should be run with: chainlit run app/chainlit_app.py
    pass
