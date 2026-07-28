"""
Synchronize GitHub Issues.

Version 1:
Reads issues from GitHub and displays a summary.
"""

from github_client import get_issues


def main():

    print("=" * 60)
    print("Engineering Intelligence Platform")
    print("GitHub Synchronization")
    print("=" * 60)
    print()

    issues = get_issues()

    # Ignore pull requests
    issues = [issue for issue in issues if "pull_request" not in issue]

    print()
    print(f"Retrieved {len(issues)} issues.\n")

    for issue in issues:

        print(f"#{issue['number']:>3} " f"{issue['state']:<6} " f"{issue['title']}")

    print("\nSynchronization complete.")


if __name__ == "__main__":
    main()
