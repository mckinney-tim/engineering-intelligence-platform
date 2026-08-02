from generator.github_client import get_issues

issues = get_issues()

print()

for issue in issues:
    print(f"{issue.number:>2}  Assignee: {issue.assignee}")

print()
