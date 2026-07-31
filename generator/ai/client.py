"""
AI client for communicating with supported language models.
"""

from openai import OpenAI

from generator.ai.models import AIResponse
from generator.config import (
    AI_MODEL,
    AI_PROVIDER,
    OPENAI_API_KEY,
)


def complete(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.2,
) -> AIResponse:
    """
    Sends a prompt to the configured AI provider.
    """

    if AI_PROVIDER == "mock":
        return AIResponse(
            provider="mock", model="mock", content="This is a mock AI response."
        )

    if AI_PROVIDER == "openai":

        client = OpenAI(api_key=OPENAI_API_KEY)

        response = client.chat.completions.create(
            model=AI_MODEL,
            temperature=temperature,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        )

        return AIResponse(
            provider="openai",
            model=AI_MODEL,
            content=response.choices[0].message.content.strip(),
        )

    raise ValueError(f"Unsupported AI provider: {AI_PROVIDER}")
