"""
AI client for communicating with supported language models.
"""

import json

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
    expect_json: bool = True,
) -> AIResponse:
    """
    Sends a prompt to the configured AI provider.
    """

    if AI_PROVIDER == "mock":

        #
        # Valid JSON containing the union of every field the
        # enrichment and portfolio parsers expect, so offline
        # development works without an API key.
        #
        mock_content = json.dumps(
            {
                "executive_summary": "Mock executive summary for offline development.",
                "complexity": 5,
                "risk": "Medium",
                "reasoning": "Mock reasoning.",
                "portfolio_health": "Yellow",
                "overall_risk": "Medium",
                "top_risks": ["Mock risk one.", "Mock risk two."],
                "recommendations": ["Mock recommendation."],
                "emerging_skills": ["Mock skill"],
                "bottlenecks": ["Mock bottleneck."],
            }
        )

        return AIResponse(
            provider="mock",
            model="mock",
            content=mock_content,
        )

    if AI_PROVIDER == "openai":

        client = OpenAI(api_key=OPENAI_API_KEY)

        request = {
            "model": AI_MODEL,
            "temperature": temperature,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        }

        if expect_json:
            request["response_format"] = {"type": "json_object"}

        response = client.chat.completions.create(**request)

        return AIResponse(
            provider="openai",
            model=AI_MODEL,
            content=response.choices[0].message.content.strip(),
        )

    raise ValueError(f"Unsupported AI provider: {AI_PROVIDER}")


def stream_complete(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.3,
):
    """
    Streams the completion as text chunks.
    """

    if AI_PROVIDER == "mock":

        import time

        mock_text = (
            "### Mock Analysis\n\n"
            "This is a **mock streaming response** for offline development. "
            "Configure AI_PROVIDER=openai to run real analyses.\n\n"
            "- Mock finding one\n"
            "- Mock finding two\n\n"
            "### Recommended Actions\n\n"
            "- Set an OpenAI API key in .env\n"
        )

        for word in mock_text.split(" "):
            time.sleep(0.02)
            yield word + " "

        return

    if AI_PROVIDER == "openai":

        client = OpenAI(api_key=OPENAI_API_KEY)

        stream = client.chat.completions.create(
            model=AI_MODEL,
            temperature=temperature,
            stream=True,
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

        for chunk in stream:

            delta = chunk.choices[0].delta.content if chunk.choices else None

            if delta:
                yield delta

        return

    raise ValueError(f"Unsupported AI provider: {AI_PROVIDER}")
