"""
Synchronize GitHub Issues.
"""

from db import get_connection, upsert_issue
from github_client import get_issues
from github_transformer import transform_issue
from enrichment.service import enrich


def main():

    print("=" * 60)
    print("Engineering Intelligence Platform")
    print("GitHub Synchronization")
    print("=" * 60)
    print()

    issues = get_issues()

    conn = get_connection()

    try:

        print()

        for github_issue in issues:

            #
            # Transform GitHub -> Engineering model
            #
            engineering_issue = transform_issue(github_issue)

            print(f"Synchronizing {engineering_issue.issue_key}")

            #
            # Save or update the issue
            #
            issue_id = upsert_issue(
                conn,
                engineering_issue,
            )

            #
            # Enrich the issue
            #
            enrich(
                conn,
                issue_id,
            )

    finally:

        conn.close()

    print()
    print("Synchronization complete.")


if __name__ == "__main__":
    main()
