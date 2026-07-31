"""
Models used by the AI layer.
"""

from dataclasses import dataclass
from enum import Enum


class RiskLevel(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


@dataclass
class Prompt:
    """
    Represents a prompt sent to an AI provider.
    """

    system: str
    user: str


@dataclass
class AIResponse:
    """
    Raw response returned by an AI provider.
    """

    provider: str
    model: str
    content: str


@dataclass
class AIIssueAnalysis:
    """
    Structured engineering intelligence returned by the AI.
    """

    executive_summary: str
    complexity: int
    risk: RiskLevel
    reasoning: str
