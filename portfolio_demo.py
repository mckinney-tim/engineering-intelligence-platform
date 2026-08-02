from generator.ai.portfolio import analyze_portfolio
from generator.db import get_connection, get_issue

conn = get_connection()

issues = []

for issue_id in range(23, 39):
    issue = get_issue(conn, issue_id)
    if issue:
        issues.append(issue)

conn.close()

print()
print("=" * 70)
print("Engineering Intelligence")
print("=" * 70)
print()

print(analyze_portfolio(issues))
