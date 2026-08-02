"""
Core domain models for the Engineering Intelligence Platform.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class EngineeringIssue:
    """
    Canonical issue model used throughout the platform.
    """

    #
    # Identity
    #

    source: str
    external_id: str
    external_url: str

    issue_key: str

    #
    # Core information
    #

    title: str
    description: str

    status: str

    created_date: date
    closed_date: Optional[date]

    #
    # Relationships
    #

    project_name: str
    assignee: Optional[str]

    #
    # Classification
    #

    labels: list[str] = field(default_factory=list)

    issue_type: Optional[str] = None
    priority: Optional[str] = None
    severity: Optional[str] = None

    #
    # Engineering Intelligence
    #

    weight: Optional[int] = None

    complexity: Optional[int] = None

    skills: list[str] = field(default_factory=list)

    themes: list[str] = field(default_factory=list)

    risk: Optional[str] = None

    executive_summary: Optional[str] = None
