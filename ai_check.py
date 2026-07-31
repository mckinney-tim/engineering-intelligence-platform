from datetime import date

from generator.ai.service import enrich_issue
from generator.engineering_models import EngineeringIssue

issue = EngineeringIssue(
    source="GitHub",
    external_id="123",
    external_url="https://github.com/mckinney-tim/engineering-intelligence-platform/issues/123",
    issue_key="GH-123",
    title="Improve Kubernetes deployment reliability",
    description="""
Deployments occasionally fail during rolling updates because pods
are not becoming healthy before the next deployment stage begins.
Investigate readiness probes, Helm configuration, and deployment
timeouts.
""",
    status="Open",
    created_date=date.today(),
    closed_date=None,
    project_name="Executive Engineering Dashboard",
    assignee="Tim",
    labels=["backend", "kubernetes"],
    priority="High",
    severity="Major",
    skills=["Kubernetes", "Helm", "CI/CD"],
)

print("=" * 70)
print("Engineering Intelligence Engine")
print("=" * 70)

print("\nSubmitting issue to AI...\n")

analysis = enrich_issue(issue)

print("Executive Summary")
print("-----------------")
print(analysis.executive_summary)

print("\nComplexity")
print("----------")
print(analysis.complexity)

print("\nRisk")
print("----")
print(analysis.risk.value)

print("\nReasoning")
print("---------")
print(analysis.reasoning)
