# EduDocAI - Intelligent Educational Document Assistant

<div align="center">

**A production-ready RAG system with agentic capabilities powered by LangChain, LangGraph, and OpenAI**

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-0.1+-green.svg)](https://www.langchain.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-orange.svg)](https://openai.com/)
[![License](https://img.shields.io/badge/License-Portfolio-purple.svg)](LICENSE)

[Features](#features) • [Demo](#demo) • [Quick Start](#quick-start) • [Architecture](#architecture) • [Agentic Capabilities](#agentic-capabilities)

</div>

---

## Overview

**EduDocAI** is an intelligent document assistant designed for educational institutions to query administrative documents (timetables, student lists, advisor assignments) using natural language. This portfolio project demonstrates production-ready LLM engineering with advanced RAG implementation, multi-document intelligence, and agentic workflows.

### Why This Project?

This project showcases:
- **Production-Ready RAG**: Complete document processing pipeline with chunking, embeddings, and vector storage
- **Agentic Workflows**: ReAct pattern with custom tools for multi-step reasoning
- **LangChain Mastery**: LCEL chains, LangGraph agents, and conversation memory
- **Clean Architecture**: Modular design with separation of concerns
- **Best Practices**: Type hints, structured logging, comprehensive testing, and documentation

---

## Features

### Core Capabilities

- **Document Processing Pipeline**
  - PDF and text document upload
  - Intelligent chunking with RecursiveCharacterTextSplitter
  - Automatic metadata extraction (document type, grade level, section)
  - ChromaDB vector storage with persistence

- **Intelligent Retrieval**
  - Semantic search using OpenAI embeddings
  - Metadata-filtered queries for precision
  - Multi-document reasoning
  - Smart query routing (simple/complex/aggregation)

- **Agentic Capabilities** (See [detailed section](#agentic-capabilities))
  - ReAct pattern for multi-step reasoning
  - 4 custom tools: Document Search, Calculator, Conflict Detector, CSV Exporter
  - Autonomous tool selection and orchestration
  - Complex reasoning workflows

- **Conversation Memory**
  - Session-based chat history
  - Buffer and summary memory modes
  - Context-aware follow-up questions

- **Production Features**
  - Chainlit async UI with file upload
  - Real-time response streaming
  - Structured logging with Python logging
  - Pydantic v2 configuration management
  - Comprehensive error handling

---

## Demo

### Sample Queries

**Basic Q&A (Phase 1)**
```
User: How many students does Raja Shoaib advise?
AI: According to the student list, Raja Shoaib advises 15 students in O-Level Section A.
```

**Multi-Document Intelligence (Phase 2)**
```
User: List all Level-III teachers and their subjects
AI: Based on the timetable:
    - Syed Bilal Hashmi: Mathematics (Room 101)
    - Dr. Sarah Ahmed: Physics (Lab 2)
    - Muhammad Hassan: Chemistry (Lab 1)
    - Ayesha Khan: English Literature (Room 205)
```

**Agentic Reasoning (Phase 3)**
```
User: Create a CSV report of all advisors and their student counts
AI: I'll search for advisor information and export it to CSV.

    [Agent uses document_search_tool → export_csv_tool]

    Report created successfully!
    - Raja Shoaib: 15 students
    - Syed Bilal: 12 students

    CSV exported to: data/exports/advisors_report.csv
```

**Conflict Detection**
```
User: Find scheduling conflicts for Muhammad Hammad
AI: [Agent uses document_search_tool → detect_conflicts_tool]

    Found 2 scheduling conflicts:
    1. Monday 9:00 AM: Teaching both O1A and O1B
    2. Thursday 2:00 PM: O-Level Chemistry overlaps with A-Level Physics
```

---

## Technology Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| **LLM Framework** | LangChain 0.1+ | LCEL chains, document processing |
| **Agent Framework** | LangGraph | ReAct agents with custom tools |
| **LLM** | OpenAI GPT-4o | Generation and reasoning |
| **Embeddings** | text-embedding-3-small | Document embeddings |
| **Vector Database** | ChromaDB | Local vector storage |
| **UI Framework** | Chainlit | Async chat interface |
| **Document Processing** | pypdf, LangChain loaders | PDF extraction |
| **Configuration** | Pydantic v2 | Settings management |
| **Environment** | python-dotenv | Environment variables |
| **Testing** | pytest | Unit and integration tests |
| **Code Quality** | black, ruff, mypy | Formatting, linting, type checking |

---

## Quick Start

### Prerequisites

- **Python 3.12+** installed
- **OpenAI API key** ([Get one here](https://platform.openai.com/api-keys))
- **Git** for cloning

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/EduDocAI.git
cd EduDocAI

# 2. Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env

# Edit .env and add your OpenAI API key:
# OPENAI_API_KEY=your_openai_api_key_here

# 5. Run the application
chainlit run app/chainlit_app.py
```

The app will open automatically at **http://localhost:8000**

### First Steps

1. **Upload a document**: Click the upload button and select a PDF or text file
2. **Wait for processing**: The app will chunk, embed, and store your document
3. **Ask questions**: Start querying your documents in natural language
4. **Try complex queries**: Use the agent for multi-step reasoning tasks

---

## Project Structure

```
EduDocAI/
├── src/                              # Source code (modular architecture)
│   ├── config/
│   │   └── settings.py              # Pydantic settings with validation
│   ├── document_processing/
│   │   ├── loaders.py               # PDF and text document loaders
│   │   ├── splitters.py             # RecursiveCharacterTextSplitter
│   │   └── metadata.py              # Metadata extraction engine
│   ├── retrieval/
│   │   ├── embeddings.py            # OpenAI embeddings manager
│   │   └── vector_store.py          # ChromaDB operations
│   ├── chains/
│   │   ├── qa_chain.py              # Q&A chain (LCEL)
│   │   └── routing_chain.py         # Query router with LLM
│   ├── agents/
│   │   ├── tools.py                 # 4 custom tools (search, calc, conflict, export)
│   │   ├── prompts.py               # ReAct system prompts
│   │   └── agent.py                 # LangGraph ReAct agent
│   ├── memory/
│   │   └── conversation_memory.py   # Session-based memory management
│   └── utils/
│       └── logging.py               # Structured logging configuration
├── app/
│   └── chainlit_app.py              # Chainlit UI entry point
├── tests/
│   ├── test_phase1.py               # Basic RAG tests
│   ├── test_phase2.py               # Multi-document tests
│   └── test_phase3.py               # Agent capability tests
├── data/                            # Data directory (gitignored)
│   ├── uploaded/                    # User-uploaded documents
│   ├── vector_db/                   # ChromaDB persistence
│   └── exports/                     # CSV exports from agent
├── requirements.txt                 # Production dependencies
├── requirements-dev.txt             # Development dependencies
├── .env.example                     # Environment variable template
├── PROGRESS.md                      # Implementation progress tracker
└── CLAUDE.md                        # AI assistant guidance
```

---

## Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│              (Chainlit - Async Chat Interface)               │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                  Application Layer                           │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────────┐    │
│  │  Document  │  │    Query    │  │      Agent       │    │
│  │ Processor  │  │   Router    │  │    Executor      │    │
│  └────────────┘  └─────────────┘  └──────────────────┘    │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                  LangChain Core Layer                        │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────────┐    │
│  │    LCEL    │  │   ReAct     │  │  Conversation    │    │
│  │   Chains   │  │   Agents    │  │     Memory       │    │
│  └────────────┘  └─────────────┘  └──────────────────┘    │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                     Data Layer                               │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────────┐    │
│  │  ChromaDB  │  │  Document   │  │    Metadata      │    │
│  │   Vector   │  │   Storage   │  │      Store       │    │
│  │    Store   │  │             │  │                  │    │
│  └────────────┘  └─────────────┘  └──────────────────┘    │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│               External Services Layer                        │
│              (OpenAI API - LLM + Embeddings)                 │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

**Document Upload Flow:**
```
Upload → Load → Extract Metadata → Chunk → Embed → Store in ChromaDB
```

**Query Flow:**
```
User Query → Query Router → Route Decision
                              │
                              ├─→ Simple: Basic RAG Chain → LLM → Response
                              │
                              └─→ Complex: ReAct Agent → Tools → LLM → Response
```

### Key Design Patterns

- **LCEL (LangChain Expression Language)**: All chains use pipe operator for composition
- **ReAct Pattern**: Reasoning + Acting for agent workflows
- **Metadata Filtering**: Filter before semantic search for precision
- **Session Memory**: Per-user conversation context
- **Tool Factory Pattern**: Extensible tool creation

---

## Agentic Capabilities

### ReAct Agent Architecture

The agent uses the **ReAct (Reasoning + Acting)** pattern for multi-step reasoning:

1. **Thought**: Agent reasons about what it needs to do
2. **Action**: Selects and executes appropriate tool
3. **Observation**: Processes tool output
4. **Iteration**: Repeats until sufficient information
5. **Final Answer**: Synthesizes response

### Custom Tools (4 Tools)

#### 1. Document Search Tool
```python
Purpose: Search for information in uploaded documents
Capabilities:
  - Vector similarity search
  - Metadata-aware retrieval
  - Multi-document context extraction

Example: "Find all teachers who teach O-Level students"
```

#### 2. Calculator Tool
```python
Purpose: Perform mathematical calculations
Capabilities:
  - Arithmetic operations (+, -, *, /)
  - Safe expression evaluation
  - Decimal and complex calculations

Example: "Calculate total students across all advisors"
```

#### 3. Schedule Conflict Detector
```python
Purpose: Detect scheduling conflicts for teachers
Capabilities:
  - Parse schedule data (day, time, class, teacher)
  - Identify double-booking conflicts
  - Generate detailed conflict reports

Example: "Find conflicts where teachers are in two places at once"
```

#### 4. CSV Exporter
```python
Purpose: Export structured data to CSV files
Capabilities:
  - Parse text into structured format
  - Create CSV files in data/exports/
  - Handle various data formats

Example: "Export all advisor information to a spreadsheet"
```

### Multi-Step Reasoning Examples

**Example 1: Comparative Analysis with Calculation**
```
Query: "How many more students does Raja Shoaib advise than Syed Bilal?"

Agent Workflow:
  Step 1: search_documents_tool("Raja Shoaib students") → "15 students"
  Step 2: search_documents_tool("Syed Bilal students") → "12 students"
  Step 3: calculator_tool("15 - 12") → "3"
  Step 4: Final Answer: "Raja Shoaib advises 3 more students (15 vs 12)"
```

**Example 2: Report Generation**
```
Query: "Create a CSV report of all advisors and student counts"

Agent Workflow:
  Step 1: search_documents_tool("all advisors student counts")
  Step 2: Format data as CSV structure
  Step 3: export_csv_tool(data, "advisors_report")
  Step 4: Final Answer: Report location + summary
```

### Agentic Capabilities Summary

| Capability | Tools Used | Example Use Case |
|------------|------------|------------------|
| Information Retrieval | document_search | "Find all Level-III teachers" |
| Mathematical Reasoning | calculator + document_search | "Total student count across advisors" |
| Conflict Detection | document_search + detect_conflicts | "Find scheduling conflicts" |
| Data Export | document_search + export_csv | "Create advisor roster CSV" |
| Comparative Analysis | document_search (2x) + calculator | "Compare student counts" |
| Multi-Document Synthesis | document_search (multiple) | "List all teachers by department" |

---

## Configuration

All settings are managed via environment variables. Copy `.env.example` to `.env` and configure:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key | - | Yes |
| `LLM_MODEL` | Model for generation | `gpt-4o` | No |
| `EMBEDDING_MODEL` | Model for embeddings | `text-embedding-3-small` | No |
| `CHUNK_SIZE` | Document chunk size (tokens) | `1000` | No |
| `CHUNK_OVERLAP` | Chunk overlap size | `200` | No |
| `TOP_K_RESULTS` | Retrieval results count | `4` | No |
| `MAX_FILE_SIZE_MB` | Max upload size | `10` | No |
| `TEMPERATURE` | LLM temperature | `0.0` | No |
| `DEBUG` | Debug mode | `false` | No |

---

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific phase tests
python test_phase1.py  # Basic RAG
python test_phase2.py  # Multi-document
python test_phase3.py  # Agent capabilities
```

### Code Quality

```bash
# Format code
black src/ app/ tests/

# Lint code
ruff check src/ app/ tests/

# Type checking
mypy src/ app/
```

### Development Phases

This project was built incrementally across 5 phases:

- **Phase 0**: Project setup, configuration, dependencies ✓
- **Phase 1**: Basic RAG with document upload and Q&A ✓
- **Phase 2**: Multi-document intelligence with metadata ✓
- **Phase 3**: Agentic capabilities with custom tools ✓
- **Phase 4**: Production features (memory, streaming) ✓

See `PROGRESS.md` for detailed implementation tracking (33/33 steps complete).

---

## Implementation Highlights

### 1. LCEL Chain Composition

Clean, composable chains using LangChain Expression Language:

```python
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
```

### 2. Query Routing with LLM

Intelligent query classification for optimal handling:

```python
class QueryType(str, Enum):
    SIMPLE = "simple"              # Basic factual queries
    CROSS_DOCUMENT = "cross_document"  # Multi-doc queries
    AGGREGATION = "aggregation"    # List/summarize queries
    COMPLEX = "complex"            # Multi-step reasoning

# LLM-based router decides which handler to use
route = query_router.route_query(user_question)
```

### 3. LangGraph ReAct Agent

Modern agent implementation with autonomous tool selection:

```python
from langgraph.prebuilt import create_react_agent

agent_executor = create_react_agent(
    model=llm,
    tools=[calculator_tool, document_search_tool, ...]
)
```

### 4. Session-Based Memory

Conversation context management per user:

```python
memory_manager = get_memory_manager()
session = memory_manager.get_or_create_session(session_id)
session.add_exchange(user_msg, ai_response)
history = session.get_history()  # Full conversation context
```

---

## Testing & Validation

### Test Results

**Phase 1 (Basic RAG)**
- Document loading: ✓ 9 chunks created
- Embeddings: ✓ Generated in ~5 seconds
- Q&A accuracy: ✓ 3/3 questions correct
- Response time: ~3-4 seconds per query

**Phase 2 (Multi-Document)**
- Query routing: ✓ 4/4 correctly classified
- Metadata filtering: ✓ Accurate filtering by type/grade/section
- Cross-document queries: ✓ Successfully synthesized information

**Phase 3 (Agent)**
- Tool usage: ✓ All 4 tools working correctly
- Multi-step reasoning: ✓ Calculator → Search → Export workflow
- Conflict detection: ✓ Identified scheduling overlaps
- CSV export: ✓ Created structured reports

**Phase 4 (Memory)**
- Session creation: ✓ Unique session per user
- Context retention: ✓ Follow-up questions work correctly
- Multi-session support: ✓ Isolated conversations

---

## Performance Considerations

- **Embedding Cache**: Vector store persists to disk, avoiding re-embedding
- **Token Optimization**: 1000 token chunks with 200 overlap balances context and cost
- **Async Operations**: Chainlit async handlers for responsive UI
- **Streaming Responses**: Real-time token streaming for better UX
- **Metadata Filtering**: Reduces search space before semantic search

---

## Roadmap & Future Enhancements

**Completed:**
- [x] Basic RAG system with ChromaDB
- [x] Multi-document intelligence
- [x] ReAct agents with custom tools
- [x] Conversation memory
- [x] Query routing

**Future Considerations:**
- [ ] Agent response streaming (LangGraph integration)
- [ ] Enhanced error handling with retries
- [ ] Token usage tracking and monitoring
- [ ] Hybrid search (semantic + keyword)
- [ ] Re-ranking with cross-encoder
- [ ] Deployment configuration (Docker, cloud platforms)

---

## Contributing

This is a portfolio project, but suggestions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is created for educational and portfolio purposes. Feel free to use it as a reference for your own projects.

---

## Acknowledgments

Built with these excellent tools:
- **[LangChain](https://www.langchain.com/)** - LLM application framework
- **[LangGraph](https://www.langchain.com/langgraph)** - Agent framework with graph-based workflows
- **[OpenAI](https://openai.com/)** - GPT-4o and embeddings API
- **[Chainlit](https://chainlit.io/)** - Beautiful async chat UI framework
- **[ChromaDB](https://www.trychroma.com/)** - Efficient vector database
- **[Pydantic](https://docs.pydantic.dev/)** - Data validation and settings management

---

## Contact & Portfolio

**Project Author**: [Your Name]

This project demonstrates:
- Production-ready RAG implementation
- LangChain/LangGraph expertise
- Agentic workflow design
- Clean software architecture
- LLM engineering best practices

For questions or collaboration opportunities, feel free to reach out!

---

<div align="center">

**⭐ If you find this project helpful, please consider giving it a star! ⭐**

[Report Bug](https://github.com/yourusername/EduDocAI/issues) • [Request Feature](https://github.com/yourusername/EduDocAI/issues)

</div>
