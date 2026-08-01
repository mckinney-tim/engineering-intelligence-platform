"""
Transforms GitHub domain objects into Engineering Intelligence
domain objects.
"""

from generator.engineering_models import EngineeringIssue
from generator.github_models import GitHubIssue
from generator.config import DEFAULT_PROJECT_NAME


def transform_issue(issue: GitHubIssue) -> EngineeringIssue:
    """
    Transform a GitHub issue into the Engineering Intelligence model.
    """

    return EngineeringIssue(
        #
        # Identity
        #
        source="GITHUB",
        external_id=str(issue.number),
        external_url=issue.html_url,
        issue_key=f"GH-{issue.number}",
        #
        # Core Information
        #
        title=issue.title,
        description=issue.body,
        status=issue.state,
        created_date=issue.created_at.date(),
        closed_date=(issue.closed_at.date() if issue.closed_at else None),
        #
        # Relationships
        #
        project_name=DEFAULT_PROJECT_NAME,
        assignee=issue.assignee,
        #
        # Classification
        #
        labels=issue.labels,
        #
        # Engineering Intelligence
        #
        weight=None,
        skills=[],
        themes=[],
        risk=None,
        executive_summary=None,
    )
