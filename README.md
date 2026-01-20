# EduDocAI

**A RAG-based educational document assistant powered by LangChain and OpenAI.**

EduDocAI allows natural language querying of educational administrative documents (timetables, student lists, advisor assignments) and demonstrates advanced agentic workflows for complex multi-step reasoning.

> **Portfolio Project**: This project showcases production-ready LLM Engineering with RAG implementation, LangChain Expression Language (LCEL), and agentic workflows.

---

## Features

- **Document Upload & Processing**: Upload PDF documents and automatically chunk, embed, and store in vector database
- **Intelligent Q&A**: Ask natural language questions about your documents
- **Multi-Document Reasoning**: Query across multiple documents with smart routing
- **Agentic Capabilities**: Complex reasoning with custom tools (calculator, conflict detector, CSV export)
- **Interactive UI**: Clean Chainlit interface for seamless interaction
- **Production-Ready**: Structured logging, error handling, and configuration management

---

## Technology Stack

| Category | Technology |
|----------|-----------|
| **Framework** | LangChain (v0.1+) with LCEL |
| **LLM** | OpenAI GPT-4o |
| **Embeddings** | OpenAI text-embedding-3-small |
| **Vector DB** | ChromaDB (local, embedded) |
| **UI** | Chainlit |
| **Document Processing** | pypdf, LangChain loaders |
| **Configuration** | Pydantic v2, python-dotenv |

---

## Quick Start

### Prerequisites

- Python 3.12+
- OpenAI API key
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd EduDicAI
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit .env and add your OpenAI API key
   # OPENAI_API_KEY=your_openai_api_key_here
   ```

5. **Run the application**
   ```bash
   chainlit run app/chainlit_app.py
   ```

   The app will open in your browser at `http://localhost:8000`

---

## Project Structure

```
EduDicAI/
├── src/                          # Source code
│   ├── config/                   # Settings and configuration (Pydantic)
│   ├── document_processing/      # Loaders, splitters, metadata extraction
│   ├── retrieval/                # Vector store, embeddings, retrieval strategies
│   ├── agents/                   # Custom tools, agent config, prompts
│   ├── chains/                   # Q&A chain, routing chain (LCEL)
│   ├── memory/                   # Conversation memory management
│   └── utils/                    # Logging, validators, helpers
├── app/                          # Application layer
│   └── chainlit_app.py          # Chainlit UI entry point
├── tests/                        # Unit and integration tests
├── data/                         # Data persistence (gitignored)
│   ├── uploaded/                 # User-uploaded documents
│   ├── processed/                # Processed/chunked documents
│   └── vector_db/                # ChromaDB persistence directory
├── notebooks/                    # Jupyter notebooks for experiments
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development dependencies
├── .env.example                  # Environment variable template
├── PROGRESS.md                   # Implementation progress tracker
└── CLAUDE.md                     # AI assistant guidance
```

---

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_retrieval.py -v
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

### Development Workflow

This project follows a phased implementation approach. Check `PROGRESS.md` for the current development phase and next steps.

**Current Phase**: Phase 0 - Project Setup & Configuration ✅

---

## Usage Examples

### Basic Query
```
Q: "How many students are advised by Raja Shoaib?"
A: Based on the student list, Raja Shoaib advises 15 students in O-Level Section A.
```

### Multi-Document Query
```
Q: "Which students in Level-III A have classes with Syed Bilal Hashmi?"
A: Analyzing the timetable and student list, 12 students from Level-III A attend
   Syed Bilal Hashmi's Mathematics classes on Monday and Wednesday.
```

### Complex Reasoning (with agents)
```
Q: "Find scheduling conflicts where Muhammad Hammad teaches two classes simultaneously"
A: Using the conflict detector tool, I found 2 scheduling conflicts:
   - Monday 9:00 AM: O1A and O1B both scheduled
   - Thursday 2:00 PM: A-Level Physics overlaps with O-Level Chemistry
```

---

## Configuration

All configuration is managed through environment variables. See `.env.example` for available options:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `LLM_MODEL` | OpenAI model for generation | `gpt-4o` |
| `EMBEDDING_MODEL` | OpenAI embedding model | `text-embedding-3-small` |
| `CHUNK_SIZE` | Document chunk size | `1000` |
| `CHUNK_OVERLAP` | Chunk overlap size | `200` |
| `TOP_K_RESULTS` | Number of retrieval results | `4` |
| `MAX_FILE_SIZE_MB` | Max file upload size | `10` |
| `TEMPERATURE` | LLM temperature | `0.0` |

---

## Architecture

EduDocAI follows a layered architecture:

1. **User Interface Layer**: Chainlit chat interface
2. **Application Layer**: Document processor, query router, agent executor
3. **LangChain Core**: LCEL chains, ReAct agents, conversation memory
4. **Data Layer**: ChromaDB vector store, document storage
5. **External Services**: OpenAI API (LLM + embeddings)

### Key Patterns

- **LCEL Chains**: All chains use LangChain Expression Language for composability
- **Metadata Filtering**: Documents filtered by type/grade/section before semantic search
- **ReAct Agents**: Agents use Reasoning + Acting pattern with custom tools
- **Conversation Memory**: Session-based memory management per user

---

## Roadmap

- [x] **Phase 0**: Project setup and configuration
- [ ] **Phase 1**: Basic RAG system with PDF upload and Q&A
- [ ] **Phase 2**: Multi-document support with smart routing
- [ ] **Phase 3**: Agentic capabilities with custom tools
- [ ] **Phase 4**: Production polish (streaming, export, deployment)

See `PROGRESS.md` for detailed implementation tracking.

---

## Contributing

This is a portfolio project for demonstration purposes. If you'd like to suggest improvements:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

---

## License

This project is for educational and portfolio purposes.

---

## Acknowledgments

Built with:
- [LangChain](https://www.langchain.com/) - LLM framework
- [OpenAI](https://openai.com/) - LLM and embeddings
- [Chainlit](https://chainlit.io/) - Chat UI framework
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [Pydantic](https://docs.pydantic.dev/) - Data validation

---

## Contact

For questions or feedback about this portfolio project, please open an issue on GitHub.
