"""
Transforms GitHub domain objects into Engineering Intelligence
domain objects.
"""

from generator.engineering_models import EngineeringIssue
from generator.github_models import GitHubIssue
from generator.config import DEFAULT_PROJECT_NAME


def normalize_status(status: str) -> str:
    mapping = {
        "open": "Open",
        "closed": "Closed",
    }

    return mapping.get(status.lower(), status)


def normalize_priority(labels: list[str]) -> str:
    labels = [label.lower() for label in labels]

    if any("high" in label for label in labels):
        return "High"

    if any("low" in label for label in labels):
        return "Low"

    if any("medium" in label for label in labels):
        return "Medium"

    return "Medium"


def normalize_issue_type(labels: list[str]) -> str:
    labels = [label.lower() for label in labels]

    if "bug" in labels:
        return "Bug"

    if "feature" in labels:
        return "Feature"

    if "epic" in labels:
        return "Epic"

    return "Task"


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
        status=normalize_status(issue.state),
        created_date=issue.created_at.date(),
        closed_date=issue.closed_at.date() if issue.closed_at else None,
        #
        # Relationships
        #
        project_name=DEFAULT_PROJECT_NAME,
        assignee=issue.assignee,
        #
        # Classification
        #
        labels=issue.labels,
        issue_type=normalize_issue_type(issue.labels),
        priority=normalize_priority(issue.labels),
        severity="Medium",
        #
        # Engineering Intelligence
        #
        weight=None,
        complexity=None,
        skills=[],
        themes=[],
        risk=None,
        executive_summary=None,
    )
