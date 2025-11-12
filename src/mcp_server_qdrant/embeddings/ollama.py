import httpx

from mcp_server_qdrant.embeddings.base import EmbeddingProvider


class OllamaEmbeddingProvider(EmbeddingProvider):
    """
    Ollama implementation of the embedding provider.
    :param model_name: The name of the Ollama embedding model to use.
    :param base_url: The base URL of the Ollama server.
    """

    def __init__(self, model_name: str, base_url: str):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=30.0)
        self._vector_size: int | None = None

    async def _get_model_info(self) -> dict:
        """Query Ollama API to get model information."""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/show",
                json={"name": self.model_name},
            )
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError:
            raise ConnectionError(
                f"Failed to connect to Ollama at {self.base_url}. "
                "Please check that Ollama is running."
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(
                    f"Model {self.model_name} not found in Ollama. "
                    f"Please ensure the model is pulled with: ollama pull {self.model_name}"
                )
            raise RuntimeError(f"Ollama API error: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to get model info from Ollama: {e}")

    async def embed_documents(self, documents: list[str]) -> list[list[float]]:
        """Embed a list of documents into vectors."""
        embeddings = []
        for doc in documents:
            try:
                response = await self.client.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": self.model_name, "prompt": doc},
                )
                response.raise_for_status()
                result = response.json()
                embeddings.append(result["embedding"])
            except httpx.ConnectError:
                raise ConnectionError(
                    f"Failed to connect to Ollama at {self.base_url}. "
                    "Please check that Ollama is running."
                )
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise ValueError(
                        f"Model {self.model_name} not found in Ollama. "
                        f"Please ensure the model is pulled with: ollama pull {self.model_name}"
                    )
                raise RuntimeError(f"Ollama API error: {e}")
            except Exception as e:
                raise RuntimeError(f"Failed to generate embeddings with Ollama: {e}")
        return embeddings

    async def embed_query(self, query: str) -> list[float]:
        """Embed a query into a vector."""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model_name, "prompt": query},
            )
            response.raise_for_status()
            result = response.json()
            return result["embedding"]
        except httpx.ConnectError:
            raise ConnectionError(
                f"Failed to connect to Ollama at {self.base_url}. "
                "Please check that Ollama is running."
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(
                    f"Model {self.model_name} not found in Ollama. "
                    f"Please ensure the model is pulled with: ollama pull {self.model_name}"
                )
            raise RuntimeError(f"Ollama API error: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to generate embeddings with Ollama: {e}")

    def get_vector_name(self) -> str:
        """
        Return the name of the vector for the Qdrant collection.
        """
        model_name = self.model_name.split("/")[-1].lower()
        return f"ollama-{model_name}"

    def get_vector_size(self) -> int:
        """Get the size of the vector for the Qdrant collection."""
        if self._vector_size is None:
            # Query a test embedding to determine size
            import asyncio

            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an async context, we need to handle this carefully
                # For now, use a default and let it be set on first embedding
                return 768  # Common default
            else:
                test_embedding = loop.run_until_complete(self.embed_query("test"))
                self._vector_size = len(test_embedding)
        return self._vector_size
