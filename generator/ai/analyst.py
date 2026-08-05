"""
Interactive AI Analyst.

Powers the AI Analyst panel in Grafana: a library of preconfigured
analyses plus free-form questions, run against whatever recordset the
dashboard filters have selected, streamed back as markdown.
"""

from generator.ai.client import stream_complete
from generator.ai.portfolio import _select_issues_for_prompt, _serialize_issue

SYSTEM_PROMPT = """
You are a senior director of engineering acting as an analyst for
engineering leadership. You are given a filtered set of engineering
issues from the organization's engineering intelligence platform.

Rules:

- Base every statement on the supplied issues. Never invent projects,
  people, technologies, or metrics that are not in the data.
- Cite issue keys (like EII-112) as evidence for specific claims.
- Write clean, well-structured Markdown: short sections with ###
  headings, bullet points, and bold key phrases. No tables.
- Be direct and specific. Avoid generic filler like "it is important
  to note". Quantify whenever the data allows (counts, days, weights).
- Close with a short "Recommended Actions" section containing 3-5
  concrete next steps unless the question calls for something else.
""".strip()


ANALYSES = {
    "bottleneck": {
        "label": "Bottleneck Analysis",
        "prompt": (
            "Identify what is slowing this organization down in working "
            "through these issues. Look for: projects or teams with long "
            "cycle times (compare created and closed dates), aging open "
            "issues, assignees carrying too much concurrent work, and "
            "clusters of blocked or long-running high-priority work. "
            "Name the single biggest bottleneck first, then secondary ones."
        ),
    },
    "risk": {
        "label": "Risk Assessment",
        "prompt": (
            "Assess delivery and technical risk across these issues. "
            "Which projects and customers carry the most risk right now, "
            "and why? Weigh priority, severity, AI risk ratings, issue "
            "age, and how much high-weight work remains open. Identify "
            "the top 3 risks with evidence and likely business impact."
        ),
    },
    "skills": {
        "label": "Skill Gap & Emerging Skills",
        "prompt": (
            "Analyze the engineering skills these issues demand. Which "
            "skills appear most, which are trending in recent issues, "
            "and where does demand look concentrated on too few people? "
            "Call out emerging technologies the team should invest in "
            "and any skill areas where open work is piling up."
        ),
    },
    "workload": {
        "label": "Team Load Balance",
        "prompt": (
            "Analyze how work is distributed. Which assignees and teams "
            "carry the most open weight? Who looks overloaded and who "
            "has capacity? Consider both issue counts and weights, and "
            "flag any single points of failure where one person owns "
            "most of a critical area."
        ),
    },
    "executive": {
        "label": "Executive Briefing",
        "prompt": (
            "Write a briefing for senior leadership on the state of this "
            "work: overall health, delivery momentum (what is getting "
            "done vs piling up), the most important accomplishments, "
            "and the decisions or investments leadership should consider."
        ),
    },
    "customer": {
        "label": "Customer Health",
        "prompt": (
            "Analyze delivery health from the customer's perspective. "
            "For each customer represented, how is their work trending: "
            "open vs closed, priority mix, aging issues? Which customer "
            "relationships are at risk based on this engineering data, "
            "and which are being served well?"
        ),
    },
}


def build_user_prompt(question: str, issues) -> str:

    selected, omitted = _select_issues_for_prompt(issues)

    issue_block = "\n\n----------------------\n\n".join(
        _serialize_issue(issue) for issue in selected
    )

    prompt = (
        f"Question:\n{question}\n\n"
        f"Engineering issues in the current filter "
        f"({len(issues)} total):\n\n{issue_block}"
    )

    if omitted:
        prompt += (
            f"\n\n----------------------\n\n"
            f"Note: {omitted} additional lower-weight, older issues matched "
            f"the filters but are omitted here for length. Base your answer "
            f"on the {len(selected)} issues above; do not imply full "
            f"coverage of all {len(issues)} matching issues."
        )

    return prompt


def stream_analysis(question: str, issues):
    """
    Yields markdown chunks answering `question` over `issues`.
    """

    if not issues:
        yield (
            "### No Matching Issues\n\n"
            "No engineering issues matched the selected filters. "
            "Widen the time range or clear a filter and try again."
        )
        return

    yield from stream_complete(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=build_user_prompt(question, issues),
        temperature=0.3,
    )
