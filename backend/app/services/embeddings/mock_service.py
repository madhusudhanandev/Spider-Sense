"""
Deterministic, no-API-key embedding stand-in.

IMPORTANT: this is lexical (word-overlap-based), not semantic. It hashes
each word into a fixed-size vector and sums them, so texts sharing many of
the same words will show up as similar, but it has none of a real
embedding model's understanding of meaning, synonyms, or paraphrasing.
It exists purely so campaign clustering has *something* to run against
without a configured API key -- treat any similarity/clustering result
produced under this mode as a rough demo, not real intelligence.
"""
import hashlib

from app.services.embeddings.base import EmbeddingResult, EmbeddingService


class MockEmbeddingService(EmbeddingService):
    def __init__(self, dimensions: int = 256) -> None:
        self._dimensions = dimensions

    async def embed(self, text: str) -> EmbeddingResult:
        vector = [0.0] * self._dimensions
        words = text.lower().split()
        for word in words:
            digest = hashlib.sha256(word.encode("utf-8")).digest()
            for i in range(self._dimensions):
                # Spread each word's hash bytes across the vector deterministically.
                vector[i] += digest[i % len(digest)] / 255.0 - 0.5

        norm = sum(v * v for v in vector) ** 0.5
        if norm > 0:
            vector = [v / norm for v in vector]

        return EmbeddingResult(vector=vector, provider="mock", dimensions=self._dimensions)