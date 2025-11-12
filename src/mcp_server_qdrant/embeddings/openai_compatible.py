from mcp_server_qdrant.embeddings.base import EmbeddingProvider


class OpenAICompatibleProvider(EmbeddingProvider):
    """
    OpenAI-compatible API implementation of the embedding provider.
    This provider works with Azure OpenAI and other OpenAI-compatible endpoints.
    :param model_name: The name of the embedding model to use.
    :param api_key: The API key for authentication.
    :param base_url: The base URL of the OpenAI-compatible endpoint.
    """

    def __init__(self, model_name: str, api_key: str, base_url: str):
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ImportError(
                "OpenAI SDK is required for OpenAI-compatible provider. "
                "Install it with: pip install mcp-server-qdrant[openai]"
            )

        self.model_name = model_name
        self.base_url = base_url
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self._vector_size: int | None = None

    async def embed_documents(self, documents: list[str]) -> list[list[float]]:
        """Embed a list of documents into vectors."""
        try:
            response = await self.client.embeddings.create(
                input=documents, model=self.model_name
            )
            embeddings = [embedding.embedding for embedding in response.data]
            # Cache vector size from first response
            if self._vector_size is None and embeddings:
                self._vector_size = len(embeddings[0])
            return embeddings
        except Exception as e:
            if "authentication" in str(e).lower() or "api key" in str(e).lower():
                raise ValueError(
                    f"Invalid API key for OpenAI-compatible provider at {self.base_url}: {e}"
                )
            elif "model" in str(e).lower() and "not found" in str(e).lower():
                raise ValueError(
                    f"Model {self.model_name} not available at {self.base_url}: {e}"
                )
            elif "connection" in str(e).lower():
                raise ConnectionError(
                    f"Failed to connect to OpenAI-compatible endpoint at {self.base_url}: {e}"
                )
            else:
                raise RuntimeError(
                    f"Failed to generate embeddings with OpenAI-compatible provider: {e}"
                )

    async def embed_query(self, query: str) -> list[float]:
        """Embed a query into a vector."""
        try:
            response = await self.client.embeddings.create(
                input=[query], model=self.model_name
            )
            embedding = response.data[0].embedding
            # Cache vector size from first response
            if self._vector_size is None:
                self._vector_size = len(embedding)
            return embedding
        except Exception as e:
            if "authentication" in str(e).lower() or "api key" in str(e).lower():
                raise ValueError(
                    f"Invalid API key for OpenAI-compatible provider at {self.base_url}: {e}"
                )
            elif "model" in str(e).lower() and "not found" in str(e).lower():
                raise ValueError(
                    f"Model {self.model_name} not available at {self.base_url}: {e}"
                )
            elif "connection" in str(e).lower():
                raise ConnectionError(
                    f"Failed to connect to OpenAI-compatible endpoint at {self.base_url}: {e}"
                )
            else:
                raise RuntimeError(
                    f"Failed to generate embeddings with OpenAI-compatible provider: {e}"
                )

    def get_vector_name(self) -> str:
        """
        Return the name of the vector for the Qdrant collection.
        """
        model_name = self.model_name.split("/")[-1].lower()
        return f"compatible-{model_name}"

    def get_vector_size(self) -> int:
        """Get the size of the vector for the Qdrant collection."""
        # If we haven't cached the size yet, return a common default
        # It will be set on the first embedding call
        if self._vector_size is None:
            return 1536  # Most common dimension for OpenAI-compatible endpoints
        return self._vector_size
