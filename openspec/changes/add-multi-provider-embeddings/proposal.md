# Add Multi-Provider Embedding Support

## Why

Currently, the MCP server only supports FastEmbed as the embedding provider. This limitation restricts users who want to use other embedding services like OpenAI, Google Gemini, Ollama, or OpenAI-compatible APIs (e.g., Azure OpenAI). Supporting multiple providers enables users to choose embedding services based on their infrastructure, cost considerations, and quality requirements.

## What Changes

- **ADDED**: Support for OpenAI embedding provider with API key authentication
- **ADDED**: Support for Google Gemini embedding provider with API key authentication
- **ADDED**: Support for Ollama embedding provider with configurable base URL
- **ADDED**: Support for OpenAI-compatible embedding providers with API key and base URL
- **ADDED**: Provider-specific configuration settings (`EMBEDDING_API_KEY`, `EMBEDDING_BASE_URL`)
- **MODIFIED**: `EmbeddingProviderSettings` to include provider-specific authentication and endpoint configuration
- **MODIFIED**: `EmbeddingProviderType` enum to include new provider options
- **MODIFIED**: Factory pattern to instantiate appropriate provider based on configuration

## Impact

- **Affected specs**: `embedding-providers` (new capability)
- **Affected code**:
  - `src/mcp_server_qdrant/settings.py` - Add new configuration fields
  - `src/mcp_server_qdrant/embeddings/types.py` - Add new provider types
  - `src/mcp_server_qdrant/embeddings/factory.py` - Add provider instantiation logic
  - `src/mcp_server_qdrant/embeddings/openai.py` - New OpenAI provider implementation
  - `src/mcp_server_qdrant/embeddings/gemini.py` - New Gemini provider implementation
  - `src/mcp_server_qdrant/embeddings/ollama.py` - New Ollama provider implementation
  - `src/mcp_server_qdrant/embeddings/openai_compatible.py` - New OpenAI-compatible provider
- **Breaking changes**: None (default remains FastEmbed)
- **Dependencies**: May require new packages (openai, google-generativeai)
