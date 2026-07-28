"""
GitHub client for the Engineering Intelligence Platform.

Responsible for communicating with the GitHub REST API.
"""

import os
import requests
from dotenv import load_dotenv

from config import GITHUB_OWNER, GITHUB_REPO

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise RuntimeError("GITHUB_TOKEN not found in .env")

BASE_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}


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

    return issues
