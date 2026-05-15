"""AI provider abstraction."""

import json
from typing import Any

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings


class AIClient:
    """Thin wrapper around AI APIs with JSON-oriented helpers."""

    def __init__(self) -> None:
        settings = get_settings()
        self.settings = settings
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    @retry(wait=wait_exponential(min=1, max=20), stop=stop_after_attempt(3))
    async def generate_json(self, prompt: str) -> dict[str, Any]:
        """Generate a JSON object from a prompt, with a deterministic fallback for tests/local dev."""
        if self.client is None:
            return {
                "title": "AI-тренд дня",
                "body_markdown": "🔥 Короткий пост-заглушка для локального режима.\n\nЧто думаете?",
                "image_prompt": "abstract AI trend cover",
                "poll_options": ["Да", "Нет"],
            }
        response = await self.client.chat.completions.create(
            model=self.settings.openai_text_model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        content = response.choices[0].message.content or "{}"
        return dict(json.loads(content))

    async def generate_image_url(self, prompt: str) -> str | None:
        """Generate an image and return a provider URL when configured."""
        if self.client is None:
            return None
        response = await self.client.images.generate(
            model=self.settings.openai_image_model,
            prompt=prompt,
            size="1536x864",
            n=1,
        )
        return response.data[0].url
