"""
GitHub client for the Engineering Intelligence Platform.

Responsible for communicating with the GitHub REST API.
"""

import os
from datetime import datetime

import requests
from dotenv import load_dotenv

from generator.config import GITHUB_OWNER, GITHUB_REPO
from generator.github_models import GitHubIssue

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise RuntimeError("GITHUB_TOKEN not found in .env")

BASE_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}


def _parse_datetime(value):
    """
    Convert GitHub datetime strings to Python datetime objects.
    """

    if value is None:
        return None

    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def get_issues(state="all"):
    """
    Retrieve all issues from the configured repository.
    Automatically handles GitHub pagination.
    """

    issues = []
    page = 1

    print("Connecting to GitHub...")

    while True:

        response = requests.get(
            f"{BASE_URL}/issues",
            headers=HEADERS,
            params={
                "state": state,
                "per_page": 100,
                "page": page,
            },
            timeout=30,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"GitHub API Error {response.status_code}\n" f"{response.text}"
            )

        page_data = response.json()

        if not page_data:
            break

        issues.extend(page_data)

        print(f"Retrieved page {page} ({len(page_data)} records)")

        page += 1

    github_issues = []

    for issue in issues:

        # Ignore pull requests
        if "pull_request" in issue:
            continue

        github_issues.append(
            GitHubIssue(
                number=issue["number"],
                title=issue["title"],
                body=issue["body"] or "",
                state=issue["state"],
                assignee=(issue["assignee"]["login"] if issue["assignee"] else None),
                created_at=_parse_datetime(issue["created_at"]),
                updated_at=_parse_datetime(issue["updated_at"]),
                closed_at=_parse_datetime(issue["closed_at"]),
                html_url=issue["html_url"],
                labels=[label["name"] for label in issue["labels"]],
            )
        )

    return github_issues
