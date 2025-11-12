from mcp_server_qdrant.embeddings.base import EmbeddingProvider
from mcp_server_qdrant.embeddings.types import EmbeddingProviderType
from mcp_server_qdrant.settings import EmbeddingProviderSettings


def create_embedding_provider(settings: EmbeddingProviderSettings) -> EmbeddingProvider:
    """
    Create an embedding provider based on the specified type.
    :param settings: The settings for the embedding provider.
    :return: An instance of the specified embedding provider.
    """
    if settings.provider_type == EmbeddingProviderType.FASTEMBED:
        from mcp_server_qdrant.embeddings.fastembed import FastEmbedProvider

        return FastEmbedProvider(settings.model_name)

    elif settings.provider_type == EmbeddingProviderType.OPENAI:
        from mcp_server_qdrant.embeddings.openai import OpenAIEmbeddingProvider

        if not settings.api_key:
            raise ValueError("API key is required for OpenAI provider")
        return OpenAIEmbeddingProvider(settings.model_name, settings.api_key)

    elif settings.provider_type == EmbeddingProviderType.GEMINI:
        from mcp_server_qdrant.embeddings.gemini import GeminiEmbeddingProvider

        if not settings.api_key:
            raise ValueError("API key is required for Gemini provider")
        return GeminiEmbeddingProvider(settings.model_name, settings.api_key)

    elif settings.provider_type == EmbeddingProviderType.OLLAMA:
        from mcp_server_qdrant.embeddings.ollama import OllamaEmbeddingProvider

        if not settings.base_url:
            raise ValueError("Base URL is required for Ollama provider")
        return OllamaEmbeddingProvider(settings.model_name, settings.base_url)

    elif settings.provider_type == EmbeddingProviderType.OPENAI_COMPATIBLE:
        from mcp_server_qdrant.embeddings.openai_compatible import (
            OpenAICompatibleProvider,
        )

        if not settings.api_key or not settings.base_url:
            raise ValueError(
                "Both API key and base URL are required for OpenAI-compatible provider"
            )
        return OpenAICompatibleProvider(
            settings.model_name, settings.api_key, settings.base_url
        )

    else:
        raise ValueError(f"Unsupported embedding provider: {settings.provider_type}")
