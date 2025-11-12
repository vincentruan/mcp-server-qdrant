from mcp_server_qdrant.embeddings.base import EmbeddingProvider

# Model dimensions mapping for common OpenAI embedding models
OPENAI_MODEL_DIMENSIONS = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
    "text-embedding-ada-002": 1536,
}


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """
    OpenAI implementation of the embedding provider.
    :param model_name: The name of the OpenAI embedding model to use.
    :param api_key: The OpenAI API key for authentication.
    """

    def __init__(self, model_name: str, api_key: str):
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ImportError(
                "OpenAI SDK is required for OpenAI provider. "
                "Install it with: pip install mcp-server-qdrant[openai]"
            )

        self.model_name = model_name
        self.client = AsyncOpenAI(api_key=api_key)

    async def embed_documents(self, documents: list[str]) -> list[list[float]]:
        """Embed a list of documents into vectors."""
        try:
            response = await self.client.embeddings.create(
                input=documents, model=self.model_name
            )
            return [embedding.embedding for embedding in response.data]
        except Exception as e:
            if "authentication" in str(e).lower() or "api key" in str(e).lower():
                raise ValueError(f"Invalid API key for OpenAI provider: {e}")
            elif "model" in str(e).lower() and "not found" in str(e).lower():
                raise ValueError(
                    f"Model {self.model_name} not available for OpenAI provider: {e}"
                )
            else:
                raise RuntimeError(f"Failed to generate embeddings with OpenAI: {e}")

    async def embed_query(self, query: str) -> list[float]:
        """Embed a query into a vector."""
        try:
            response = await self.client.embeddings.create(
                input=[query], model=self.model_name
            )
            return response.data[0].embedding
        except Exception as e:
            if "authentication" in str(e).lower() or "api key" in str(e).lower():
                raise ValueError(f"Invalid API key for OpenAI provider: {e}")
            elif "model" in str(e).lower() and "not found" in str(e).lower():
                raise ValueError(
                    f"Model {self.model_name} not available for OpenAI provider: {e}"
                )
            else:
                raise RuntimeError(f"Failed to generate embeddings with OpenAI: {e}")

    def get_vector_name(self) -> str:
        """
        Return the name of the vector for the Qdrant collection.
        """
        model_name = self.model_name.split("/")[-1].lower()
        return f"openai-{model_name}"

    def get_vector_size(self) -> int:
        """Get the size of the vector for the Qdrant collection."""
        # Use hardcoded dimensions for known models
        if self.model_name in OPENAI_MODEL_DIMENSIONS:
            return OPENAI_MODEL_DIMENSIONS[self.model_name]
        # Default to most common dimension
        return 1536
