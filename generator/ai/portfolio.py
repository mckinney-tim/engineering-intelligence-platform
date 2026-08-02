"""
Portfolio-level AI analysis.
"""

import json

from generator.ai.client import complete
from generator.ai.portfolio_models import PortfolioAnalysis


def analyze_portfolio(issues) -> PortfolioAnalysis:
    """
    Analyze a collection of EngineeringIssue objects.
    """

    #
    # Nothing to analyze
    #
    if len(issues) == 0:

        return PortfolioAnalysis(
            executive_summary="No engineering issues matched the selected filters.",
            portfolio_health="No Data",
            overall_risk="No Data",
            top_risks=[],
            recommendations=[],
            emerging_skills=[],
            bottlenecks=[],
            top_risks_text="",
            recommendations_text="",
            emerging_skills_text="",
            bottlenecks_text="",
        )

    system_prompt = """
You are a Fortune 100 Chief Technology Officer preparing an executive portfolio review for the CEO.
Write concise executive-level observations.
Avoid generic AI language.
Every statement should be supported by the supplied engineering issues.

Analyze ONLY the engineering issues provided.

Do not invent projects, risks, technologies, or recommendations that are not supported by the supplied issues.

Return ONLY valid JSON.

{
  "executive_summary": "",
  "portfolio_health": "",
  "overall_risk": "",
  "top_risks": [],
  "recommendations": [],
  "emerging_skills": [],
  "bottlenecks": []
}

Rules:

- executive_summary should be valid Markdown.
    Structure it like this:
    Write 2–3 concise paragraphs.
    Key Observations
    Finish with 3–5 bullet points highlighting the most important findings.

Do not use tables.
- portfolio_health should be Green, Yellow, or Red.
- overall_risk should be Low, Medium, or High.
- top_risks should contain 3-5 executive-level observations.
- Each item should be a complete sentence of 10-20 words.
- recommendations should contain 3-5 specific, actionable recommendations written as complete sentences.
- emerging_skills should contain 3-5 important technologies or competencies most represented in the engineering portfolio.
- bottlenecks should contain 3-5 concise descriptions of the biggest delivery constraints.
- Do not repeat the same wording between sections.
- Keep every item concise but informative.
- Avoid repeating technologies, projects, or observations in multiple sections unless they are genuinely important.

Return JSON only.
Do not fabricate information that is not supported by the supplied engineering issues.
Base all conclusions on the supplied issues.
""".strip()

    issue_text = []

    for issue in issues:

        issue_text.append(f"""
Issue: {issue.issue_key}

Title: {issue.title}

Status: {issue.status}

Priority: {issue.priority}

Skills: {", ".join(issue.skills)}

Description:
{issue.description}
""".strip())

    user_prompt = "\n\n----------------------\n\n".join(issue_text)

    response = complete(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        expect_json=True,
    )

    data = json.loads(response.content)

    return PortfolioAnalysis(
        executive_summary=data["executive_summary"],
        portfolio_health=data["portfolio_health"],
        overall_risk=data["overall_risk"],
        top_risks=data["top_risks"],
        recommendations=data["recommendations"],
        emerging_skills=data["emerging_skills"],
        bottlenecks=data["bottlenecks"],
        top_risks_text="\n\n".join(f"• {x}" for x in data["top_risks"]),
        recommendations_text="\n\n".join(f"• {x}" for x in data["recommendations"]),
        emerging_skills_text="\n\n".join(f"• {x}" for x in data["emerging_skills"]),
        bottlenecks_text="\n\n".join(f"• {x}" for x in data["bottlenecks"]),
    )
