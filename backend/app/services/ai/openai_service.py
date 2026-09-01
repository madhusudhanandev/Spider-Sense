"""
OpenAI-backed implementation of AIAnalysisService.

Uses JSON-mode / structured output so the response is guaranteed-parseable
JSON matching AIAnalysisOutput (section 36 requires strict JSON, never
arbitrary prose). If the call fails or the key is missing, callers should
fall back to MockAIAnalysisService -- see get_ai_service() in factory.py.
"""
import json
import logging

from openai import AsyncOpenAI

from app.core.config import get_settings
from app.services.ai.base import AIAnalysisOutput, AIAnalysisService
from app.services.ai.prompts import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger("spidersense.ai.openai")


class OpenAIAnalysisService(AIAnalysisService):
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._model = settings.OPENAI_MODEL

    async def analyze(
        self,
        *,
        text: str,
        platform: str | None = None,
        language_hint: str | None = None,
        url_facts: list[dict] | None = None,
    ) -> AIAnalysisOutput:
        user_prompt = build_user_prompt(text, platform, language_hint, url_facts)

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                response_format={"type": "json_object"},
                temperature=0.2,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
            )
            raw = response.choices[0].message.content
            data = json.loads(raw)
            return AIAnalysisOutput.model_validate(data)
        except Exception:
            logger.exception("OpenAI analysis failed; caller should fall back to mock service")
            raise
