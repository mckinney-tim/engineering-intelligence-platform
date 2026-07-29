"""
GitHub domain models for the Engineering Intelligence Platform.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class GitHubIssue:
    number: int
    title: str
    body: str
    state: str

    assignee: Optional[str]

    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime]

    html_url: str

    labels: list[str]
