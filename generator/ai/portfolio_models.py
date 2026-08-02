"""
Models for portfolio-level AI analysis.
"""

from dataclasses import dataclass


@dataclass
class PortfolioAnalysis:
    executive_summary: str

    portfolio_health: str
    overall_risk: str

    top_risks: list[str]
    recommendations: list[str]
    emerging_skills: list[str]
    bottlenecks: list[str]

    top_risks_text: str
    recommendations_text: str
    emerging_skills_text: str
    bottlenecks_text: str
