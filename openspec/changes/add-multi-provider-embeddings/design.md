# Design: Multi-Provider Embedding Support

## Context

The current implementation uses FastEmbed exclusively for generating embeddings. FastEmbed is a lightweight, locally-run embedding library that doesn't require API keys or network calls. However, users often need to integrate with cloud-based embedding services that may offer:

- Better embedding quality for specific domains
- Centralized API management and billing
- Compliance with organizational infrastructure requirements
- Integration with existing AI platform subscriptions

Reference implementation from RooCode shows a pattern where:
- Provider selection dynamically determines which configuration fields are shown
- API keys are required for cloud providers (OpenAI, Gemini, OpenAI-compatible)
- Base URLs are required for self-hosted/compatible providers (Ollama, OpenAI-compatible)
- Model selection is provider-specific with vector dimension information

## Goals / Non-Goals

**Goals:**
- Support OpenAI, Google Gemini, Ollama, and OpenAI-compatible embedding providers
- Maintain backward compatibility with FastEmbed as the default
- Validate configuration based on provider type (e.g., API key required for OpenAI)
- Provide clear error messages for misconfiguration
- Use async HTTP clients for all network-based providers

**Non-Goals:**
- Supporting local model fine-tuning
- Automatic provider fallback or load balancing
- Provider-specific features beyond basic embedding generation
- Migration tools for existing collections (vector dimensions are immutable)

## Decisions

### Provider Abstraction
Continue using the existing `EmbeddingProvider` abstract base class. All providers implement:
- `embed_documents(documents: list[str]) -> list[list[float]]`
- `embed_query(query: str) -> list[float]`
- `get_vector_name() -> str`
- `get_vector_size() -> int`

This ensures consistency and allows transparent provider switching.

### Configuration Strategy
Use Pydantic validators in `EmbeddingProviderSettings` to enforce provider-specific requirements:
- OpenAI: requires `EMBEDDING_API_KEY`
- Gemini: requires `EMBEDDING_API_KEY`
- Ollama: requires `EMBEDDING_BASE_URL` (default: `http://localhost:11434`)
- OpenAI-compatible: requires both `EMBEDDING_API_KEY` and `EMBEDDING_BASE_URL`
- FastEmbed: no additional configuration (current behavior)

### HTTP Client Choice
- **OpenAI**: Use official `openai` SDK (async support, automatic retries, good error handling)
- **Gemini**: Use official `google-generativeai` SDK
- **Ollama**: Use `httpx` for direct API calls (no official async SDK available)
- **OpenAI-compatible**: Use `openai` SDK with custom base URL

### Error Handling
Each provider should catch provider-specific exceptions and raise informative errors:
- Authentication failures → "Invalid API key for {provider}"
- Network failures → "Failed to connect to {provider} at {base_url}"
- Model not found → "Model {model_name} not available for {provider}"

### Vector Naming Convention
Each provider should use a consistent naming scheme for Qdrant vector names:
- FastEmbed: `fast-{model_name}` (existing)
- OpenAI: `openai-{model_name}`
- Gemini: `gemini-{model_name}`
- Ollama: `ollama-{model_name}`
- OpenAI-compatible: `compatible-{model_name}`

This prevents collection conflicts when switching providers.

### Alternatives Considered

**Alternative 1: Unified HTTP client wrapper**
- Considered: Create a single HTTP wrapper for all providers
- Rejected: Official SDKs provide better error handling, retries, and API compatibility

**Alternative 2: Plugin architecture with dynamic loading**
- Considered: Load providers dynamically from separate packages
- Rejected: Adds complexity without clear benefit for the initial set of providers

**Alternative 3: Support batch size configuration**
- Considered: Allow users to configure batch sizes for embedding requests
- Deferred: Can be added later if performance profiling shows benefit

## Risks / Trade-offs

### Risk: Dependency bloat
- **Impact**: Adding multiple SDK dependencies increases package size
- **Mitigation**: Make cloud provider SDKs optional dependencies (extras_require)

### Risk: API rate limiting
- **Impact**: Cloud providers may rate limit, causing request failures
- **Mitigation**: Document rate limits in README, provide clear error messages

### Risk: Vector dimension mismatches
- **Impact**: Switching providers with different dimensions breaks existing collections
- **Mitigation**: Document that provider/model changes require re-indexing, validate dimensions on startup

### Trade-off: Configuration complexity
- **Trade-off**: More providers = more configuration options
- **Accepted**: Better to support common use cases than optimize for simplicity

## Migration Plan

### Phase 1: Add core provider implementations
1. Add new provider types to enum
2. Extend settings with validation
3. Implement OpenAI provider
4. Update factory to handle OpenAI

### Phase 2: Add remaining providers
5. Implement Gemini provider
6. Implement Ollama provider
7. Implement OpenAI-compatible provider
8. Update factory for all providers

### Phase 3: Documentation and testing
9. Add integration tests for each provider
10. Update README with provider configuration examples
11. Add troubleshooting guide for common issues

### Rollback Plan
If issues arise, users can revert to `EMBEDDING_PROVIDER=fastembed` with no code changes required.

## Open Questions

1. **Should we support model listing/discovery APIs?**
   - Consideration: Some providers offer model enumeration endpoints
   - Decision needed: Whether to expose this via MCP tools or just documentation

2. **Should we cache embeddings at the provider level?**
   - Consideration: Could reduce API costs for repeated queries
   - Decision needed: Whether caching belongs in provider layer or application layer

3. **Should we support custom headers/authentication schemes?**
   - Consideration: Some enterprise deployments use custom auth
   - Decision needed: Scope to standard API key/bearer token or support custom headers
