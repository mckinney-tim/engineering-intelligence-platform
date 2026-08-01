"""
Engineering Intelligence enrichment pipeline.
"""

from generator.ai.service import enrich_issue

from generator.db import (
    get_issue,
    update_ai_analysis,
)

from generator.enrichment.skills import enrich as enrich_skills


def enrich(conn, issue_id):
    """
    Execute all enrichment for one issue.
    """

    #
    # Skill enrichment
    #
    enrich_skills(
        conn,
        issue_id,
    )

    #
    # Load the enriched issue
    #
    issue = get_issue(
        conn,
        issue_id,
    )

    if issue is None:
        raise ValueError(f"Issue {issue_id} not found.")

    #
    # AI enrichment
    #
    analysis = enrich_issue(
        issue,
    )

    #
    # Persist AI results
    #
    update_ai_analysis(
        conn,
        issue_id,
        analysis,
    )

    print(f"   AI: Complexity={analysis.complexity} " f"Risk={analysis.risk.value}")
