"""
EmbeddingService abstraction -- Phase 4 (embeddings + campaign clustering).

Same pattern as AIAnalysisService/OCRService/SpeechToTextService: an
abstract interface, one or more real implementations, and a factory with a
mock fallback so the app still runs (with degraded, non-semantic behavior)
if no embedding provider is configured.
"""
from abc import ABC, abstractmethod


class EmbeddingResult:
    def __init__(self, vector: list[float], provider: str, dimensions: int):
        self.vector = vector
        self.provider = provider
        self.dimensions = dimensions


class EmbeddingService(ABC):
    @abstractmethod
    async def embed(self, text: str) -> EmbeddingResult:
        raise NotImplementedError


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """
    Pure-Python cosine similarity, no numpy dependency required.

    Returns a value in [-1, 1] (in practice [0, 1] for embeddings from the
    same model, since most embedding spaces don't produce strongly negative
    similarities between unrelated text). Vectors of mismatched length
    return 0.0 rather than raising, since that can legitimately happen if
    the embedding provider or model was changed after some rows were
    already stored.
    """
    if not a or not b or len(a) != len(b):
        return 0.0

    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)