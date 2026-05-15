"""AI provider abstraction."""

import hashlib
import json
import math
from typing import Any

from app.core.config import get_settings


class AIClient:
    """Thin wrapper around AI APIs with JSON-oriented helpers."""

    def __init__(self) -> None:
        settings = get_settings()
        self.settings = settings
        self.client = None
        if settings.openai_api_key:
            from openai import AsyncOpenAI

            self.client = AsyncOpenAI(api_key=settings.openai_api_key)

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

    async def embed_text(self, text: str, dimensions: int = 64) -> list[float]:
        """Return embeddings from the provider or a stable local fallback."""
        if self.client is not None:
            response = await self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text[:8000],
            )
            return list(response.data[0].embedding)
        vector = [0.0] * dimensions
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode()).digest()
            idx = int.from_bytes(digest[:2], "big") % dimensions
            vector[idx] += 1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]
