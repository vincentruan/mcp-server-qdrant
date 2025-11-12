<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Model Context Protocol (MCP) server implementation for Qdrant, a vector search engine. It provides semantic memory capabilities for LLM applications by enabling them to store and retrieve information using vector embeddings.

The server is built with FastMCP and exposes two primary tools:
- `qdrant-store`: Store information with optional metadata in a Qdrant collection
- `qdrant-find`: Semantically search for stored information using natural language queries

## Development Commands

### Setup
```bash
# Install dependencies (uv is the package manager)
uv sync

# Install pre-commit hooks
pre-commit install
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_qdrant_integration.py

# Run tests with coverage
pytest --cov=src/mcp_server_qdrant
```

### Code Quality
```bash
# Format code with ruff
ruff format .

# Lint code with ruff
ruff check . --fix

# Sort imports with isort
isort . --profile black

# Type check with mypy
mypy src/mcp_server_qdrant

# Run all pre-commit hooks
pre-commit run --all-files
```

### Development Server
```bash
# Run in development mode with MCP inspector (opens browser at localhost:5173)
COLLECTION_NAME=mcp-dev fastmcp dev src/mcp_server_qdrant/server.py

# Run with in-memory Qdrant for testing
QDRANT_URL=":memory:" COLLECTION_NAME="test" fastmcp dev src/mcp_server_qdrant/server.py
```

### Running the Server
```bash
# Run with stdio transport (default)
QDRANT_URL="http://localhost:6333" COLLECTION_NAME="my-collection" uvx mcp-server-qdrant

# Run with SSE transport for remote clients
QDRANT_URL="http://localhost:6333" COLLECTION_NAME="my-collection" uvx mcp-server-qdrant --transport sse

# Run with Docker
docker build -t mcp-server-qdrant .
docker run -p 8000:8000 \
  -e FASTMCP_HOST="0.0.0.0" \
  -e QDRANT_URL="http://localhost:6333" \
  -e COLLECTION_NAME="my-collection" \
  mcp-server-qdrant
```

## Architecture

### Core Components

**QdrantMCPServer** (`src/mcp_server_qdrant/mcp_server.py`)
- Main FastMCP server class that orchestrates the MCP server functionality
- Initializes the Qdrant connector and embedding provider
- Registers MCP tools (`qdrant-store` and `qdrant-find`) with dynamic parameter binding based on settings
- Handles filter wrapping for filterable fields when configured

**QdrantConnector** (`src/mcp_server_qdrant/qdrant.py`)
- Manages the AsyncQdrantClient and database interactions
- Handles collection creation with proper vector configuration
- Implements storage with UUID-based point IDs and metadata support
- Implements semantic search with optional query filters

**Settings** (`src/mcp_server_qdrant/settings.py`)
- Three main setting groups using Pydantic BaseSettings:
  - `ToolSettings`: Customizable descriptions for MCP tools
  - `QdrantSettings`: Qdrant connection, collection, and filter configuration
  - `EmbeddingProviderSettings`: Embedding provider and model selection
- Validates that `QDRANT_URL` and `QDRANT_LOCAL_PATH` are mutually exclusive
- Supports filterable fields with configurable conditions and indexing

**Embedding Provider Abstraction** (`src/mcp_server_qdrant/embeddings/`)
- `base.py`: Abstract base class defining the embedding interface
- `fastembed.py`: FastEmbed implementation (currently the only provider)
- `factory.py`: Factory pattern for creating embedding providers
- Providers expose vector name, size, and embedding methods for documents and queries

### Key Patterns

**Dynamic Tool Registration**
Tools are registered dynamically based on configuration. The server uses `make_partial_function` to bind parameters:
- If a default collection is configured, `collection_name` parameter is hidden from tools
- If filterable fields are configured, `wrap_filters` adds typed filter parameters to the `find` tool
- If read-only mode is enabled, the `store` tool is not registered

**Filter System**
The filter system (`src/mcp_server_qdrant/common/`) supports:
- Field-level filters with typed conditions (==, !=, >, >=, <, <=, any, except)
- Arbitrary JSON filters when `allow_arbitrary_filter=True`
- Automatic payload index creation for filterable fields

**Entry Format**
Search results are formatted as XML-like structures by `format_entry()`:
```
<entry><content>...</content><metadata>...</metadata></entry>
```
This method can be overridden in subclasses for custom formatting.

## Configuration

All configuration is done via environment variables (command-line arguments are no longer supported).

### Required for Remote Qdrant
- `QDRANT_URL`: Qdrant server URL
- `QDRANT_API_KEY`: API key for authentication

### Required for Local Qdrant
- `QDRANT_LOCAL_PATH`: Path to local Qdrant storage directory

### Common Settings
- `COLLECTION_NAME`: Default collection name (if not set, collection name must be provided per tool call)
- `EMBEDDING_MODEL`: Model name (default: `sentence-transformers/all-MiniLM-L6-v2`)
- `QDRANT_SEARCH_LIMIT`: Maximum search results (default: 10)
- `QDRANT_READ_ONLY`: Disable write operations (default: false)

### Tool Customization
Use `TOOL_STORE_DESCRIPTION` and `TOOL_FIND_DESCRIPTION` to customize tool behavior for specific use cases (e.g., code search with Cursor/Windsurf).

## Transport Protocols

The server supports three transport modes via `--transport` flag:
- `stdio`: Standard input/output (default, for local MCP clients)
- `sse`: Server-Sent Events (recommended for remote clients, listens on port 8000)
- `streamable-http`: Streamable HTTP (newer alternative to SSE)

When using SSE or streamable-http, set `FASTMCP_HOST="0.0.0.0"` in Docker to expose the server.

## Testing Strategy

Tests are organized by integration level:
- `test_qdrant_integration.py`: Tests QdrantConnector with actual Qdrant instances
- `test_fastembed_integration.py`: Tests FastEmbed embedding provider
- `test_settings.py`: Tests configuration validation

Tests use pytest-asyncio for async test support. Use `:memory:` for QDRANT_URL to test without a real database.
