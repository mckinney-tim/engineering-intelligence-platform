"""
Prompt builders for the Engineering Intelligence Engine.
"""

from generator.ai.models import Prompt
from generator.engineering_models import EngineeringIssue


def build_issue_enrichment_prompt(issue: EngineeringIssue) -> Prompt:
    """
    Build a prompt for analyzing a single engineering issue.
    """

    system_prompt = """
You are a senior software engineering manager.

Your job is to analyze engineering work items.

Return ONLY valid JSON.

Do not use markdown.

Do not include explanations outside the JSON.
"""

    user_prompt = f"""
Analyze the following engineering issue.

Issue Key:
{issue.issue_key}

Title:
{issue.title}

Description:
{issue.description}

Project:
{issue.project_name}

Status:
{issue.status}

Priority:
{issue.priority}

Severity:
{issue.severity}

Labels:
{", ".join(issue.labels) if issue.labels else "None"}

Detected Skills:
{", ".join(issue.skills) if issue.skills else "None"}

Return ONLY valid JSON in exactly this format:

{{
  "executive_summary": "...",
  "complexity": 1,
  "risk": "Low",
  "reasoning": "..."
}}

Rules:

- executive_summary should be 2-3 concise sentences.
- complexity is an integer from 1 to 10.
- risk must be exactly one of:
  Low
  Medium
  High
- reasoning should briefly explain the complexity and risk assessment.
"""

    return Prompt(
        system=system_prompt.strip(),
        user=user_prompt.strip(),
    )
