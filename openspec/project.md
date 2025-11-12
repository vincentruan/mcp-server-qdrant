# Project Context

## Purpose
This project is a Model Context Protocol (MCP) server implementation for Qdrant, a vector search engine. It provides semantic memory capabilities for LLM applications by enabling them to store and retrieve information using vector embeddings. The server acts as a semantic memory layer on top of the Qdrant database, allowing AI assistants to persistently remember and semantically search information across conversations.

## Tech Stack
- **Python 3.10+**: Primary language
- **FastMCP 2.7.0+**: MCP server framework for exposing tools to AI assistants
- **Qdrant Client 1.12.0+**: Vector database client for semantic search
- **FastEmbed 0.6.0+**: Embedding model provider (currently the only supported provider)
- **Pydantic 2.10.6+**: Settings management and validation
- **pytest & pytest-asyncio**: Testing framework with async support
- **uv**: Package manager for dependency management
- **Docker**: Containerization for deployment
- **pre-commit**: Git hooks for code quality enforcement

## Project Conventions

### Code Style
- **Formatter**: Ruff (with Black profile)
- **Linter**: Ruff with auto-fix enabled
- **Import Sorting**: isort with Black profile
- **Type Checking**: mypy with strict type hints
- **Line Length**: Following Black defaults (88 characters)
- **Naming Conventions**:
  - Classes: PascalCase (e.g., `QdrantMCPServer`, `QdrantConnector`)
  - Functions/methods: snake_case (e.g., `format_entry`, `create_collection`)
  - Constants: UPPER_SNAKE_CASE for environment variables (e.g., `QDRANT_URL`, `COLLECTION_NAME`)
  - Private methods: prefix with underscore (e.g., `_internal_method`)

### Architecture Patterns
- **Factory Pattern**: Used for embedding provider creation (`embeddings/factory.py`)
- **Settings-based Configuration**: All configuration via environment variables using Pydantic `BaseSettings`
- **Abstract Base Classes**: Embedding providers follow abstract interface (`embeddings/base.py`)
- **Dynamic Tool Registration**: MCP tools registered dynamically based on configuration (partial function binding)
- **Filter Wrapping**: Typed filter parameters added dynamically when filterable fields are configured
- **Async-First**: All I/O operations are async (Qdrant client, embedding generation)
- **Separation of Concerns**:
  - `mcp_server.py`: MCP server orchestration
  - `qdrant.py`: Database operations
  - `settings.py`: Configuration management
  - `embeddings/`: Embedding provider abstraction
  - `common/`: Shared utilities (filters, formatting)

### Testing Strategy
- **Framework**: pytest with pytest-asyncio for async test support
- **Integration Tests**: Test against actual Qdrant instances (use `:memory:` for ephemeral testing)
- **Test Organization**:
  - `test_qdrant_integration.py`: QdrantConnector tests
  - `test_fastembed_integration.py`: Embedding provider tests
  - `test_settings.py`: Configuration validation tests
- **Coverage**: Run with `pytest --cov=src/mcp_server_qdrant`
- **Test Naming**: `test_<function_name>` convention
- **Async Testing**: Use `asyncio_mode = "auto"` in pytest.ini

### Git Workflow
- **Main Branch**: `master`
- **Commit Conventions**:
  - Prefix with type: `fix:`, `new:`, `docs:`, `chore:`
  - Use lowercase imperative mood (e.g., "fix: return None if no results where found")
  - Reference PR numbers in commit messages (e.g., `(#83)`)
- **Pre-commit Hooks**: Enforced via pre-commit framework
  - YAML validation
  - End-of-file fixer
  - Trailing whitespace removal
  - AST validation
  - Large file check
  - Ruff formatting and linting
  - isort import sorting
  - mypy type checking
- **PR Strategy**: Feature branches merged to master via pull requests

## Domain Context

### Model Context Protocol (MCP)
MCP is an open protocol enabling seamless integration between LLM applications and external data sources/tools. This server exposes two primary MCP tools:
- `qdrant-store`: Store information with optional metadata
- `qdrant-find`: Semantically search stored information using natural language

### Vector Search & Embeddings
- Uses dense vector embeddings to enable semantic similarity search
- Default model: `sentence-transformers/all-MiniLM-L6-v2`
- Vector dimensions determined by embedding model
- Search results formatted as XML-like structures: `<entry><content>...</content><metadata>...</metadata></entry>`

### Use Cases
1. **Semantic Memory for AI Assistants**: Persistent memory across conversations
2. **Code Search**: Store and retrieve code snippets with natural language descriptions (Cursor/Windsurf integration)
3. **Knowledge Base**: Build searchable knowledge repositories
4. **Context Augmentation**: Provide relevant context to LLMs dynamically

## Important Constraints

### Configuration
- **Environment Variables Only**: Command-line arguments are not supported (migrated away in recent versions)
- **Mutual Exclusivity**: Cannot use both `QDRANT_URL` and `QDRANT_LOCAL_PATH` simultaneously
- **Collection Requirements**: Either set `COLLECTION_NAME` as default or provide per tool call
- **Read-Only Mode**: When enabled, `store` tool is not registered

### Embedding Providers
- Currently only FastEmbed is supported (though architecture allows for extension)
- Embedding model must be compatible with FastEmbed library
- Vector dimensions are fixed once collection is created

### Transport Protocols
- **stdio**: Default, for local MCP clients only
- **sse**: For remote clients (recommended for Cursor/Windsurf)
- **streamable-http**: Newer alternative to SSE for remote clients
- When using SSE/HTTP, must set `FASTMCP_HOST="0.0.0.0"` in Docker for external access

### Performance
- Default search limit: 10 results
- Results may be filtered by metadata when filterable fields are configured
- Payload indexes automatically created for filterable fields

## External Dependencies

### Qdrant Vector Database
- **Purpose**: Core vector storage and search engine
- **Modes**:
  - Remote server (via `QDRANT_URL` + `QDRANT_API_KEY`)
  - Local storage (via `QDRANT_LOCAL_PATH`)
  - In-memory (`:memory:` for testing)
- **Client**: AsyncQdrantClient for async operations
- **Collections**: Auto-created if they don't exist

### FastMCP Framework
- **Purpose**: MCP server implementation framework
- **Features Used**:
  - Dynamic tool registration
  - Multiple transport protocols (stdio, sse, streamable-http)
  - Development mode with inspector UI (port 5173)
  - Environment variable configuration
- **Configuration**: Via `FASTMCP_*` environment variables

### FastEmbed Library
- **Purpose**: Generate embeddings for semantic search
- **Models**: Supports sentence-transformers and other FastEmbed-compatible models
- **Default**: `sentence-transformers/all-MiniLM-L6-v2`
- **API**: Exposes embedding methods for documents and queries

### Client Integrations
- **Claude Desktop**: Via `claude_desktop_config.json` or Smithery
- **Claude Code**: Via `claude mcp add` command
- **VS Code**: Via `.vscode/mcp.json` or one-click install badges
- **Cursor/Windsurf**: Via SSE transport with custom tool descriptions
