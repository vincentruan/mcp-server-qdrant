# Embedding Providers Capability

## ADDED Requirements

### Requirement: Multiple Provider Support
The system SHALL support multiple embedding provider backends including FastEmbed, OpenAI, Google Gemini, Ollama, and OpenAI-compatible APIs.

#### Scenario: Provider selection via environment variable
- **WHEN** `EMBEDDING_PROVIDER` is set to a supported provider type
- **THEN** the system instantiates the corresponding embedding provider
- **AND** uses provider-specific configuration parameters

#### Scenario: Default provider
- **WHEN** `EMBEDDING_PROVIDER` is not set
- **THEN** the system defaults to FastEmbed provider
- **AND** maintains backward compatibility with existing configurations

### Requirement: OpenAI Provider
The system SHALL support OpenAI embeddings API when `EMBEDDING_PROVIDER=openai`.

#### Scenario: OpenAI authentication
- **WHEN** `EMBEDDING_PROVIDER=openai`
- **THEN** the system requires `EMBEDDING_API_KEY` to be set
- **AND** raises a validation error if API key is missing

#### Scenario: OpenAI model selection
- **WHEN** `EMBEDDING_MODEL` is set with OpenAI provider
- **THEN** the system uses the specified OpenAI embedding model
- **AND** queries the model to determine vector dimensions

#### Scenario: OpenAI API failures
- **WHEN** OpenAI API returns an authentication error
- **THEN** the system raises an informative error message
- **AND** indicates that the API key may be invalid

### Requirement: Google Gemini Provider
The system SHALL support Google Gemini embeddings API when `EMBEDDING_PROVIDER=gemini`.

#### Scenario: Gemini authentication
- **WHEN** `EMBEDDING_PROVIDER=gemini`
- **THEN** the system requires `EMBEDDING_API_KEY` to be set
- **AND** raises a validation error if API key is missing

#### Scenario: Gemini model selection
- **WHEN** `EMBEDDING_MODEL` is set with Gemini provider
- **THEN** the system uses the specified Gemini embedding model
- **AND** determines vector dimensions from model metadata

#### Scenario: Gemini API failures
- **WHEN** Gemini API returns an error
- **THEN** the system raises an informative error message
- **AND** indicates the specific failure reason

### Requirement: Ollama Provider
The system SHALL support Ollama self-hosted embeddings when `EMBEDDING_PROVIDER=ollama`.

#### Scenario: Ollama base URL configuration
- **WHEN** `EMBEDDING_PROVIDER=ollama`
- **THEN** the system requires `EMBEDDING_BASE_URL` to be set
- **AND** defaults to `http://localhost:11434` if not specified

#### Scenario: Ollama model information
- **WHEN** Ollama provider is initialized
- **THEN** the system queries Ollama API to determine model vector dimensions
- **AND** stores this information for collection creation

#### Scenario: Ollama connection failures
- **WHEN** Ollama API is unreachable at the configured base URL
- **THEN** the system raises an error with connection details
- **AND** suggests checking that Ollama is running

### Requirement: OpenAI-Compatible Provider
The system SHALL support OpenAI-compatible APIs when `EMBEDDING_PROVIDER=openai-compatible`.

#### Scenario: OpenAI-compatible authentication and endpoint
- **WHEN** `EMBEDDING_PROVIDER=openai-compatible`
- **THEN** the system requires both `EMBEDDING_API_KEY` and `EMBEDDING_BASE_URL` to be set
- **AND** raises validation errors if either is missing

#### Scenario: OpenAI-compatible SDK usage
- **WHEN** OpenAI-compatible provider is initialized
- **THEN** the system uses OpenAI SDK with custom `base_url` parameter
- **AND** maintains compatibility with OpenAI-like endpoints (e.g., Azure OpenAI)

#### Scenario: OpenAI-compatible API failures
- **WHEN** the compatible API returns an error
- **THEN** the system raises an informative error message
- **AND** includes both authentication and endpoint configuration in error context

### Requirement: Provider-Specific Configuration Validation
The system SHALL validate configuration parameters based on the selected embedding provider.

#### Scenario: API key required for cloud providers
- **WHEN** provider is one of (openai, gemini, openai-compatible)
- **AND** `EMBEDDING_API_KEY` is not set
- **THEN** the system raises a validation error at startup
- **AND** error message specifies which provider requires the API key

#### Scenario: Base URL required for hosted providers
- **WHEN** provider is one of (ollama, openai-compatible)
- **AND** `EMBEDDING_BASE_URL` is not set (and no default applies)
- **THEN** the system raises a validation error at startup
- **AND** error message specifies the expected base URL format

#### Scenario: FastEmbed requires no authentication
- **WHEN** `EMBEDDING_PROVIDER=fastembed`
- **THEN** the system does not require `EMBEDDING_API_KEY` or `EMBEDDING_BASE_URL`
- **AND** initializes successfully with only `EMBEDDING_MODEL` specified

### Requirement: Vector Naming Consistency
The system SHALL use provider-specific prefixes for vector names in Qdrant collections.

#### Scenario: Provider-specific vector name
- **WHEN** an embedding provider is initialized
- **THEN** `get_vector_name()` returns a name formatted as `{provider}-{model_name}`
- **AND** prevents collection conflicts when switching providers

#### Scenario: FastEmbed vector naming (backward compatibility)
- **WHEN** FastEmbed provider is used
- **THEN** vector name follows existing format `fast-{model_name}`
- **AND** maintains compatibility with existing collections

### Requirement: Async Embedding Operations
The system SHALL use asynchronous HTTP clients for all network-based embedding providers.

#### Scenario: Async document embedding
- **WHEN** `embed_documents()` is called on any provider
- **THEN** the operation is performed asynchronously
- **AND** does not block the event loop

#### Scenario: Async query embedding
- **WHEN** `embed_query()` is called on any provider
- **THEN** the operation is performed asynchronously
- **AND** returns a single embedding vector

### Requirement: Error Handling and User Feedback
The system SHALL provide clear, actionable error messages for embedding provider failures.

#### Scenario: Authentication failure error
- **WHEN** a provider fails due to invalid credentials
- **THEN** the error message includes the provider name
- **AND** suggests checking the API key configuration

#### Scenario: Network failure error
- **WHEN** a provider fails due to network issues
- **THEN** the error message includes the provider name and endpoint
- **AND** suggests checking network connectivity and base URL

#### Scenario: Model not found error
- **WHEN** a provider fails because the specified model doesn't exist
- **THEN** the error message includes the model name and provider
- **AND** suggests checking available models for that provider

### Requirement: Optional Dependencies
The system SHALL support optional installation of provider-specific dependencies.

#### Scenario: FastEmbed always available
- **WHEN** the package is installed without extras
- **THEN** FastEmbed provider is available
- **AND** is the default provider

#### Scenario: Optional provider dependencies
- **WHEN** user wants to use OpenAI provider
- **THEN** they can install with `pip install mcp-server-qdrant[openai]`
- **AND** the openai SDK becomes available

#### Scenario: Missing optional dependency error
- **WHEN** user selects a provider without installing its dependencies
- **THEN** the system raises an import error with installation instructions
- **AND** suggests the correct extras syntax for installation
