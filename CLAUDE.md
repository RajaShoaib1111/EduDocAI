# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EduDoc AI is a RAG-based educational document assistant built with LangChain. It allows natural language querying of administrative documents (timetables, student lists, advisor assignments) and demonstrates agentic workflows for complex multi-step reasoning.

**Primary Goal**: Portfolio project showcasing LLM Engineering skills with production-ready RAG implementation.

## Technology Stack

- **Framework**: LangChain (v0.1+) with LCEL (LangChain Expression Language)
- **LLM**: Anthropic Claude (Sonnet 3.5 or latest) as primary, OpenAI GPT-4 as fallback
- **Embeddings**: OpenAI text-embedding-3-small
- **Vector DB**: ChromaDB (local, embedded)
- **UI**: Chainlit for interactive chat interface
- **Document Processing**: PyPDF2, Unstructured, LangChain document loaders
- **Supporting**: Pydantic, python-dotenv, tiktoken

## Architecture Overview

The system follows a layered architecture:

1. **User Interface Layer**: Chainlit app (`app/chainlit_app.py`)
2. **Application Layer**: Document Processor, Query Router, Agent Executor
3. **LangChain Core**: Chains (LCEL), Agents (ReAct), Memory (Buffer)
4. **Data Layer**: Vector DB (Chroma), Document Store, Metadata Store
5. **External Services**: Anthropic Claude API, OpenAI API

**Key Components**:
- `src/document_processing/`: Document loading, chunking, metadata extraction
- `src/retrieval/`: Vector store operations, embeddings, retrieval strategies
- `src/agents/`: Custom tools (calculator, conflict detector), agent configuration, prompts
- `src/chains/`: Q&A chain, routing chain, summary chain (all using LCEL)
- `src/memory/`: Conversation memory management
- `src/config/`: Settings and configuration with Pydantic
- `data/`: uploaded/, processed/, vector_db/ directories for document persistence

## Development Workflow

### Environment Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (copy .env.example to .env)
# Required: ANTHROPIC_API_KEY, OPENAI_API_KEY
```

### Running the Application

```bash
# Start Chainlit UI
chainlit run app/chainlit_app.py

# Run with specific port
chainlit run app/chainlit_app.py --port 8080
```

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_retrieval.py

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_loaders.py::test_pdf_loader -v
```

### Development Commands

```bash
# Run linter
ruff check src/ app/ tests/

# Format code
black src/ app/ tests/

# Type checking
mypy src/ app/
```

## Code Architecture Patterns

### LangChain LCEL Chain Composition

All chains should be built using LCEL (LangChain Expression Language) for composability:

```python
# Use pipe operator for chain composition
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
```

### Document Processing Pipeline

Documents flow through: Load → Extract Metadata → Chunk → Embed → Store
- Loaders in `document_processing/loaders.py` handle PDF/text extraction
- Splitters in `document_processing/splitters.py` use RecursiveCharacterTextSplitter
- Metadata extraction in `document_processing/metadata.py` identifies document type, grade level, section
- Vector store operations in `retrieval/vector_store.py` handle ChromaDB persistence

### Retrieval Strategy

The system uses a multi-stage retrieval approach:
1. **Metadata Filtering**: Filter by document type, grade, section before semantic search
2. **Semantic Search**: Vector similarity using embeddings
3. **Hybrid Search** (Phase 2): Combine semantic + keyword search
4. **Re-ranking** (Phase 2): Re-score results for relevance

### Agent Architecture

Agents use ReAct pattern (Reasoning + Acting):
- Tools defined in `agents/tools.py`: calculator, schedule_conflict_detector, csv_exporter
- Agent config in `agents/agent.py` specifies available tools
- System prompts in `agents/prompts.py` guide reasoning behavior
- Agents decide when to search vs. compute vs. use tools

### Memory Management

Conversation memory using LangChain's memory classes:
- ConversationBufferMemory for short conversations
- ConversationSummaryMemory for longer conversations
- Session management per user in Chainlit

## Configuration Management

All settings use Pydantic for validation in `src/config/settings.py`:

```python
class Settings(BaseSettings):
    anthropic_api_key: str
    openai_api_key: str
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_results: int = 4
    # ... other settings
```

Load from environment variables using python-dotenv.

## Data Flow for Queries

1. User submits question via Chainlit UI
2. Query Router (`chains/routing_chain.py`) classifies query type
3. Route to appropriate handler:
   - Simple factual → Basic RAG chain
   - Cross-document → Multi-document retrieval
   - Complex reasoning → Agent with tools
4. Retriever fetches relevant chunks from ChromaDB (filtered by metadata)
5. LLM generates answer with retrieved context
6. Response returned with source citations
7. Conversation memory updated

## Sample Query Examples

**Basic (Phase 1)**:
- "How many students are advised by Raja Shoaib?"
- "When does O1A have Science class on Monday?"

**Multi-Document (Phase 2)**:
- "Which students in Level-III A have classes with Syed Bilal Hashmi?"
- "Show me all advisors and how many students they each have"

**Complex Agent (Phase 3)**:
- "Find scheduling conflicts where Muhammad Hammad is teaching two classes at the same time"
- "Generate a CSV report of all O-Level students grouped by section and advisor"

## LangChain Best Practices

- **Use LCEL**: Always use LCEL for chain composition (pipe operator `|`)
- **Enable Streaming**: Set `streaming=True` for LLM to improve UX
- **Monitor Tokens**: Use callbacks to track token usage and costs
- **Cache Embeddings**: Reuse embeddings when possible to reduce API calls
- **Handle Retries**: Implement retry logic for API failures
- **Validate Inputs**: Sanitize user uploads and queries

## Code Quality Standards

- **Type Hints**: Required for all function signatures
- **Docstrings**: Required for all public functions and classes (Google style)
- **Error Handling**: Graceful failures with informative error messages
- **Logging**: Structured logging configured in `utils/logging.py`
- **Testing**: Unit tests for all critical components (loaders, retrievers, chains)

## Security Considerations

- **API Keys**: Never commit API keys; use environment variables only
- **Input Validation**: Sanitize all user uploads in `utils/validators.py`
- **Data Privacy**: Don't log sensitive document content
- **File Upload Limits**: Enforce max file size and allowed file types

## Cost Optimization

- **Token Counting**: Use tiktoken to count tokens before API calls
- **Context Size Limits**: Chunk documents appropriately (default 1000 tokens)
- **Batch Embeddings**: Generate embeddings in batches
- **Model Selection**: Use Claude Sonnet (not Opus) for most queries; Haiku for simple tasks

## Development Phases

The project follows a 4-phase implementation plan:

1. **Phase 1 (Weeks 1-2)**: Basic RAG system with PDF upload and Q&A
2. **Phase 2 (Weeks 3-4)**: Multi-document support with smart routing
3. **Phase 3 (Weeks 5-6)**: Agentic capabilities with custom tools
4. **Phase 4 (Weeks 7-8)**: Production polish (memory, streaming, export)

When implementing features, follow the phase structure outlined in the original planning document.

## Evaluation & Testing

Test queries against these metrics:
- **Retrieval Quality**: Precision@K, MRR (Mean Reciprocal Rank)
- **Answer Quality**: Accuracy, citation accuracy, completeness
- **Performance**: Response time (<2s target), token usage, error rate

Use Jupyter notebooks in `notebooks/` for experiments:
- `01_exploration.ipynb`: Data exploration
- `02_chunking_experiments.ipynb`: Test different chunk sizes
- `03_retrieval_evaluation.ipynb`: Evaluate retrieval quality

## Common Pitfalls to Avoid

- **Don't** create abstractions before they're needed (YAGNI principle)
- **Don't** chunk documents too small (loses context) or too large (irrelevant retrieval)
- **Don't** ignore metadata - it's critical for multi-document filtering
- **Don't** forget source citations - transparency is key
- **Don't** use blocking I/O in Chainlit - always use async
- **Don't** hardcode prompts - keep them in `agents/prompts.py`

## Dependencies Notes

- **LangChain**: Use v0.1+ (not v0.0.x) for latest LCEL features
- **ChromaDB**: Persists to `data/vector_db/` - gitignore this directory
- **Chainlit**: Async-first framework - use `@cl.on_message` decorators
- **Pydantic**: v2 for settings management

## File Organization

- Source code in `src/` using modular design
- Chainlit app entry point in `app/chainlit_app.py`
- Tests mirror source structure in `tests/`
- Data directories in `data/` (gitignored except README)
- Notebooks for experiments in `notebooks/`

## Additional Notes

This is a portfolio project designed to demonstrate LLM engineering skills. Focus on:
- Clean, well-documented code
- Proper use of LangChain patterns
- Demonstrating RAG and agentic reasoning
- Production-quality architecture
- Educational use case that solves real problems
