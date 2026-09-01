"""
AIAnalysisService abstraction (section 5, "AI").

The rest of the app must depend only on this interface, never on a specific
provider's SDK. Swapping OpenAI for Anthropic, a local model, etc. later
means writing one new class here and changing one line in
`get_ai_service()` -- nothing else in the codebase should need to change.

Section 36 requirements are encoded directly in `AIAnalysisOutput`: the
model is required to return this exact structured shape, and must NOT
invent technical URL facts (those come only from URLAnalysisService and
are merged in afterwards).
"""
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field


class ExtractedEntity(BaseModel):
    type: str  # matches app.models.enums.IndicatorType values, lowercase-tolerant
    value: str
    confidence: float = 1.0


class TacticFinding(BaseModel):
    name: str  # matches app.models.enums.TacticName values
    confidence: float
    evidence: str


class AIAnalysisOutput(BaseModel):
    """Exact contract the LLM must fill in (section 36)."""

    scam_detected: bool
    confidence: float = Field(ge=0.0, le=1.0)

    scam_category: str  # matches app.models.enums.ScamCategory values

    risk_factors: list[str] = []
    psychological_tactics: list[TacticFinding] = []
    requested_actions: list[str] = []  # matches app.models.enums.RequestedActionType values

    claimed_organization: str | None = None
    language: str | None = None
    entities: list[ExtractedEntity] = []

    summary: str
    explanation: str
    recommended_actions: list[str] = []


class AIAnalysisService(ABC):
    """Provider-agnostic scam-content analyzer."""

    @abstractmethod
    async def analyze(
        self,
        *,
        text: str,
        platform: str | None = None,
        language_hint: str | None = None,
        url_facts: list[dict] | None = None,
    ) -> AIAnalysisOutput:
        """
        Analyze message content and return structured findings.

        `url_facts` (if provided) are pre-computed technical facts from
        URLAnalysisService -- the model interprets them, it never invents
        its own technical verdict about a URL.
        """
        raise NotImplementedError
