import asyncio

from mcp_server_qdrant.embeddings.base import EmbeddingProvider

# Model dimensions mapping for common Gemini embedding models
GEMINI_MODEL_DIMENSIONS = {
    "models/embedding-001": 768,
    "models/text-embedding-004": 768,
    "embedding-001": 768,
    "text-embedding-004": 768,
}


class GeminiEmbeddingProvider(EmbeddingProvider):
    """
    Google Gemini implementation of the embedding provider.
    :param model_name: The name of the Gemini embedding model to use.
    :param api_key: The Google API key for authentication.
    """

    def __init__(self, model_name: str, api_key: str):
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError(
                "Google Generative AI SDK is required for Gemini provider. "
                "Install it with: pip install mcp-server-qdrant[gemini]"
            )

        self.model_name = model_name
        genai.configure(api_key=api_key)
        self.genai = genai

    async def embed_documents(self, documents: list[str]) -> list[list[float]]:
        """Embed a list of documents into vectors."""
        try:
            # Run in thread pool since Gemini SDK is synchronous
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.genai.embed_content(
                    model=self.model_name,
                    content=documents,
                    task_type="retrieval_document",
                ),
            )
            return (
                result["embedding"]
                if isinstance(result["embedding"][0], list)
                else [result["embedding"]]
            )
        except Exception as e:
            if "api key" in str(e).lower() or "authentication" in str(e).lower():
                raise ValueError(f"Invalid API key for Gemini provider: {e}")
            elif "model" in str(e).lower() and "not found" in str(e).lower():
                raise ValueError(
                    f"Model {self.model_name} not available for Gemini provider: {e}"
                )
            else:
                raise RuntimeError(f"Failed to generate embeddings with Gemini: {e}")

    async def embed_query(self, query: str) -> list[float]:
        """Embed a query into a vector."""
        try:
            # Run in thread pool since Gemini SDK is synchronous
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.genai.embed_content(
                    model=self.model_name,
                    content=query,
                    task_type="retrieval_query",
                ),
            )
            return result["embedding"]
        except Exception as e:
            if "api key" in str(e).lower() or "authentication" in str(e).lower():
                raise ValueError(f"Invalid API key for Gemini provider: {e}")
            elif "model" in str(e).lower() and "not found" in str(e).lower():
                raise ValueError(
                    f"Model {self.model_name} not available for Gemini provider: {e}"
                )
            else:
                raise RuntimeError(f"Failed to generate embeddings with Gemini: {e}")

    def get_vector_name(self) -> str:
        """
        Return the name of the vector for the Qdrant collection.
        """
        model_name = self.model_name.split("/")[-1].lower()
        return f"gemini-{model_name}"

    def get_vector_size(self) -> int:
        """Get the size of the vector for the Qdrant collection."""
        # Use hardcoded dimensions for known models
        if self.model_name in GEMINI_MODEL_DIMENSIONS:
            return GEMINI_MODEL_DIMENSIONS[self.model_name]
        # Default to most common Gemini dimension
        return 768
