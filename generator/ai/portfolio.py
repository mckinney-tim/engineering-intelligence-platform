"""
Portfolio-level AI analysis.
"""

import json

from datetime import date

from generator.ai.client import complete
from generator.ai.portfolio_models import PortfolioAnalysis


MAX_DESCRIPTION_CHARS = 220

#
# Above this many issues, a single prompt risks exceeding the OpenAI
# org's tokens-per-minute limit. Beyond the cap, keep the
# highest-weight, most-recent issues (most analytically relevant) and
# tell the model how many were omitted so it doesn't overstate
# coverage.
#
MAX_ISSUES_FOR_PROMPT = 150


def _select_issues_for_prompt(issues):

    if len(issues) <= MAX_ISSUES_FOR_PROMPT:
        return issues, 0

    ranked = sorted(
        issues,
        key=lambda i: (i.weight or 0, i.created_date or date.min),
        reverse=True,
    )

    selected = ranked[:MAX_ISSUES_FOR_PROMPT]

    return selected, len(issues) - len(selected)


def _serialize_issue(issue) -> str:
    """
    Compact one issue into the LLM context. Dates, weight, and AI
    scores give the model real signal for bottleneck and cycle-time
    observations; descriptions are truncated to control token cost.
    """

    description = (issue.description or "").strip()

    if len(description) > MAX_DESCRIPTION_CHARS:
        description = description[:MAX_DESCRIPTION_CHARS] + "..."

    age_days = None

    if issue.created_date:

        end = issue.closed_date or date.today()

        age_days = (end - issue.created_date).days

    lines = [
        f"Issue: {issue.issue_key}",
        f"Title: {issue.title}",
        f"Project: {issue.project_name}",
        f"Assignee: {issue.assignee or 'Unassigned'}",
        f"Type: {issue.issue_type or 'Unknown'}",
        f"Status: {issue.status}",
        f"Priority: {issue.priority}",
        f"Severity: {issue.severity or 'Unknown'}",
        f"Weight: {issue.weight if issue.weight is not None else 'Unknown'}",
        f"Created: {issue.created_date}",
        f"Closed: {issue.closed_date or 'Still open'}",
        f"Age (days): {age_days if age_days is not None else 'Unknown'}",
    ]

    if issue.complexity is not None:
        lines.append(f"AI Complexity (1-10): {issue.complexity}")

    if issue.risk:
        lines.append(f"AI Risk: {issue.risk}")

    if issue.skills:
        lines.append(f"Skills: {', '.join(issue.skills)}")

    if issue.themes:
        lines.append(f"Themes: {', '.join(issue.themes)}")

    lines.append(f"Description:\n{description}")

    return "\n".join(lines)


def _compute_health_metrics(issues):
    """
    Pre-compute the exact proportions the health/risk thresholds key
    off of. LLMs are unreliable at accurately tallying percentages by
    eyeballing a list of issue blocks, even when given explicit
    thresholds — so the real numbers are computed here and handed to
    the model as facts, leaving it only to apply a rule rather than
    first calculate one.
    """

    total = len(issues)

    high_crit = sum(1 for i in issues if i.priority in ("Critical", "High"))

    risk_rated = [i for i in issues if i.risk]
    high_risk = sum(1 for i in risk_rated if i.risk == "High")

    open_issues = [i for i in issues if not i.closed_date]

    #
    # Denominator is TOTAL issues, not open issues. A customer with
    # only a handful of open issues can otherwise show a wildly noisy
    # percentage from 2-3 stragglers even when the portfolio overall
    # is healthy (most work already closed).
    #
    aging_45plus = sum(
        1
        for i in open_issues
        if i.created_date and (date.today() - i.created_date).days > 45
    )

    return {
        "total": total,
        "pct_high_crit": round(100 * high_crit / total, 1),
        "pct_ai_risk_high": (
            round(100 * high_risk / len(risk_rated), 1) if risk_rated else None
        ),
        "pct_open": round(100 * len(open_issues) / total, 1),
        "pct_aging_45plus_of_total": round(100 * aging_45plus / total, 1),
    }


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
- portfolio_health should be Green, Yellow, or Red. The user prompt includes
    a "COMPUTED METRICS" block with the real percentages already calculated
    for you — use those exact numbers, do not re-estimate them yourself from
    the issue list. Apply these thresholds mechanically:
    Red: pct_high_crit > 50, OR pct_ai_risk_high > 35, OR
      pct_aging_45plus_of_total > 25.
    Green: pct_high_crit < 20 AND (pct_ai_risk_high is None or < 15) AND
      pct_aging_45plus_of_total < 10.
    Yellow: everything else. Do not default here out of caution — only use
      Yellow when the computed metrics genuinely fall in between, not as a
      safe middle choice when Red's conditions are already met.
- overall_risk should be Low, Medium, or High, using the same COMPUTED
    METRICS and the same discipline: if portfolio_health is Red, overall_risk
    should virtually always be High, not Medium. If Green, overall_risk
    should virtually always be Low. Don't hedge toward Medium when the
    numbers already crossed a threshold.
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

    selected, omitted = _select_issues_for_prompt(issues)

    metrics = _compute_health_metrics(issues)

    metrics_block = (
        "COMPUTED METRICS (already calculated — use these exact numbers for "
        "portfolio_health and overall_risk, do not re-estimate):\n"
        f"- total issues: {metrics['total']}\n"
        f"- pct_high_crit (Critical or High priority): {metrics['pct_high_crit']}%\n"
        f"- pct_ai_risk_high (AI Risk = High, among issues with an AI risk "
        f"rating): "
        f"{metrics['pct_ai_risk_high']}%\n"
        f"- pct_open (still open): {metrics['pct_open']}%\n"
        f"- pct_aging_45plus_of_total (open issues older than 45 days, as a "
        f"share of ALL issues in this set): {metrics['pct_aging_45plus_of_total']}%"
    )

    user_prompt = metrics_block + "\n\n----------------------\n\n" + "\n\n----------------------\n\n".join(
        _serialize_issue(issue) for issue in selected
    )

    if omitted:
        user_prompt += (
            f"\n\n----------------------\n\n"
            f"Note: {omitted} additional lower-weight, older issues matched "
            f"the filters but are omitted here for length. Base conclusions "
            f"on the {len(selected)} issues above; do not imply full coverage "
            f"of all {len(issues)} matching issues."
        )

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
