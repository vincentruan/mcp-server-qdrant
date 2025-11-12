# Implementation Tasks

## 1. Core Infrastructure Updates
- [x] 1.1 Add new provider types to `EmbeddingProviderType` enum (openai, gemini, ollama, openai-compatible)
- [x] 1.2 Add `EMBEDDING_API_KEY` field to `EmbeddingProviderSettings` with validation
- [x] 1.3 Add `EMBEDDING_BASE_URL` field to `EmbeddingProviderSettings` with validation
- [x] 1.4 Add Pydantic validator to enforce provider-specific configuration requirements
- [x] 1.5 Update pyproject.toml with optional dependencies for cloud providers

## 2. OpenAI Provider Implementation
- [x] 2.1 Create `src/mcp_server_qdrant/embeddings/openai.py` with `OpenAIEmbeddingProvider` class
- [x] 2.2 Implement `embed_documents` using OpenAI async client
- [x] 2.3 Implement `embed_query` using OpenAI async client
- [x] 2.4 Implement `get_vector_name` returning `openai-{model}`
- [x] 2.5 Implement `get_vector_size` by querying model info or using hardcoded dimensions
- [x] 2.6 Add error handling for API key validation and network errors
- [x] 2.7 Update factory to instantiate OpenAI provider when selected

## 3. Google Gemini Provider Implementation
- [x] 3.1 Create `src/mcp_server_qdrant/embeddings/gemini.py` with `GeminiEmbeddingProvider` class
- [x] 3.2 Implement `embed_documents` using Gemini async client
- [x] 3.3 Implement `embed_query` using Gemini async client
- [x] 3.4 Implement `get_vector_name` returning `gemini-{model}`
- [x] 3.5 Implement `get_vector_size` by querying model info or using hardcoded dimensions
- [x] 3.6 Add error handling for API key validation and network errors
- [x] 3.7 Update factory to instantiate Gemini provider when selected

## 4. Ollama Provider Implementation
- [x] 4.1 Create `src/mcp_server_qdrant/embeddings/ollama.py` with `OllamaEmbeddingProvider` class
- [x] 4.2 Implement `embed_documents` using httpx async client
- [x] 4.3 Implement `embed_query` using httpx async client
- [x] 4.4 Implement `get_vector_name` returning `ollama-{model}`
- [x] 4.5 Implement `get_vector_size` by querying Ollama model info endpoint
- [x] 4.6 Add error handling for connection failures and model not found
- [x] 4.7 Update factory to instantiate Ollama provider when selected

## 5. OpenAI-Compatible Provider Implementation
- [x] 5.1 Create `src/mcp_server_qdrant/embeddings/openai_compatible.py` with `OpenAICompatibleProvider` class
- [x] 5.2 Implement using OpenAI SDK with custom base_url parameter
- [x] 5.3 Implement all required methods similar to OpenAI provider
- [x] 5.4 Implement `get_vector_name` returning `compatible-{model}`
- [x] 5.5 Add error handling for authentication and endpoint configuration
- [x] 5.6 Update factory to instantiate OpenAI-compatible provider when selected

## 6. Testing
- [x] 6.1 Write integration tests for OpenAI provider (mock API responses)
- [x] 6.2 Write integration tests for Gemini provider (mock API responses)
- [x] 6.3 Write integration tests for Ollama provider (mock API responses)
- [x] 6.4 Write integration tests for OpenAI-compatible provider (mock API responses)
- [x] 6.5 Write settings validation tests for provider-specific requirements
- [x] 6.6 Write factory tests ensuring correct provider instantiation
- [x] 6.7 Test error handling for missing API keys and invalid base URLs

## 7. Documentation
- [x] 7.1 Update README.md with provider configuration examples for all providers
- [x] 7.2 Add section on vector dimension considerations when switching providers
- [x] 7.3 Document optional dependency installation (e.g., `uv pip install .[openai]`)
- [x] 7.4 Add troubleshooting section for common provider-specific errors
- [x] 7.5 Update CLAUDE.md with new provider architecture details
- [x] 7.6 Add example docker-compose configurations for each provider

## 8. Validation
- [x] 8.1 Run all tests with `pytest --cov=src/mcp_server_qdrant`
- [x] 8.2 Test development server with each provider using MCP inspector
- [x] 8.3 Verify pre-commit hooks pass (ruff, mypy, isort)
- [x] 8.4 Manually test with actual provider APIs to verify end-to-end functionality
- [x] 8.5 Validate that FastEmbed remains the default provider (backward compatibility)
