"""
Engineering Intelligence enrichment pipeline.
"""

from ai.service import enrich_issue

from db import (
    get_issue,
    update_ai_analysis,
)

from enrichment.skills import enrich as enrich_skills


def enrich(conn, issue_id):
    """
    Run all enrichment steps for an issue.
    """

    #
    # Detect skills
    #
    enrich_skills(
        conn,
        issue_id,
    )

    #
    # Load the issue
    #
    issue = get_issue(
        conn,
        issue_id,
    )

    if issue is None:
        return

    #
    # AI analysis
    #
    analysis = enrich_issue(
        issue,
    )

    #
    # Save AI results
    #
    update_ai_analysis(
        conn,
        issue_id,
        analysis,
    )

    print(f"   AI: Complexity {analysis.complexity}, " f"Risk {analysis.risk.value}")
