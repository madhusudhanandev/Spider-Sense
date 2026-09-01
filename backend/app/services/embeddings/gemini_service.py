"""
Gemini-backed implementation of EmbeddingService, using gemini-embedding-001
(Google's current stable text embedding model as of this writing).

Requests a reduced output dimensionality (768 by default, configurable) for
speed and storage efficiency -- gemini-embedding-001 supports flexible
output sizes from 128 to 3072; 768 is Google's recommended middle ground
and is more than sufficient for the campaign-similarity use case here.
"""
import logging

from google import genai
from google.genai import types

from app.core.config import get_settings
from app.services.embeddings.base import EmbeddingResult, EmbeddingService

logger = logging.getLogger("spidersense.embeddings.gemini")


class GeminiEmbeddingService(EmbeddingService):
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not configured")
        self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self._model = settings.EMBEDDING_MODEL
        self._dimensions = settings.EMBEDDING_DIMENSIONS

    async def embed(self, text: str) -> EmbeddingResult:
        response = await self._client.aio.models.embed_content(
            model=self._model,
            contents=text,
            config=types.EmbedContentConfig(output_dimensionality=self._dimensions),
        )
        vector = list(response.embeddings[0].values)
        return EmbeddingResult(vector=vector, provider="gemini", dimensions=len(vector))