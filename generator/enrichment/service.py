"""
Engineering Intelligence enrichment pipeline.
"""

from enrichment.skills import enrich as enrich_skills


def enrich(conn, issue_id):

    enrich_skills(
        conn,
        issue_id,
    )
