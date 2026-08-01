"""
AI enrichment service.
"""

import json

from generator.ai.client import complete
from generator.ai.models import (
    AIResponse,
    AIIssueAnalysis,
    RiskLevel,
)

from generator.ai.prompts import build_issue_enrichment_prompt

from generator.engineering_models import EngineeringIssue


def enrich_issue(issue: EngineeringIssue) -> AIIssueAnalysis:
    """
    Perform AI enrichment for a single EngineeringIssue.
    """

    prompt = build_issue_enrichment_prompt(issue)

    response = complete(
        system_prompt=prompt.system,
        user_prompt=prompt.user,
    )

    return _parse_analysis(response)


def _parse_analysis(response: AIResponse) -> AIIssueAnalysis:
    """
    Convert the AI JSON response into an AIIssueAnalysis.
    """

    try:
        result = json.loads(response.content)

    except json.JSONDecodeError as ex:

        raise ValueError("AI returned invalid JSON.") from ex

    required_fields = (
        "executive_summary",
        "complexity",
        "risk",
        "reasoning",
    )

    for field in required_fields:

        if field not in result:

            raise ValueError(f"Missing AI field: {field}")

    return AIIssueAnalysis(
        executive_summary=result["executive_summary"].strip(),
        complexity=int(result["complexity"]),
        risk=RiskLevel(result["risk"]),
        reasoning=result["reasoning"].strip(),
    )
