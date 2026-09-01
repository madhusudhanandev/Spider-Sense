"""
Gemini-backed implementation of AIAnalysisService.

Uses the `google-genai` SDK's structured-JSON output mode so the response
is guaranteed-parseable JSON matching AIAnalysisOutput (section 36 requires
strict JSON, never arbitrary prose) -- the same contract OpenAIAnalysisService
fulfills, so this is a drop-in alternative selected via AI_PROVIDER=gemini.
"""
import json
import logging

from google import genai
from google.genai import types

from app.core.config import get_settings
from app.services.ai.base import AIAnalysisOutput, AIAnalysisService
from app.services.ai.prompts import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger("spidersense.ai.gemini")


class GeminiAnalysisService(AIAnalysisService):
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not configured")
        self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self._model = settings.GEMINI_MODEL

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
            response = await self._client.aio.models.generate_content(
                model=self._model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    temperature=0.2,
                ),
            )
            data = json.loads(response.text)
            return AIAnalysisOutput.model_validate(data)
        except Exception:
            logger.exception("Gemini analysis failed; caller should fall back to mock service")
            raise