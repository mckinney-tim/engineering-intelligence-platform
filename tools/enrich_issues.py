"""
Batch AI enrichment.

Enriches every issue that does not yet have AI analysis (complexity,
risk, executive summary). Safe to re-run: already-enriched issues are
skipped, so an interrupted run resumes where it left off.

Usage:
    python tools/enrich_issues.py
"""

import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from generator.ai.service import enrich_issue
from generator.db import get_connection, get_issue, update_ai_analysis

WORKERS = 3

MAX_ATTEMPTS = 5


def enrich_with_retry(issue):
    """
    Retry with exponential backoff so org-level rate limits
    (tokens per minute) slow the run down instead of failing it.
    """

    import time

    for attempt in range(1, MAX_ATTEMPTS + 1):

        try:
            return enrich_issue(issue)

        except Exception as ex:

            if "429" not in str(ex) and "rate_limit" not in str(ex):
                raise

            if attempt == MAX_ATTEMPTS:
                raise

            time.sleep(2 ** attempt)


def pending_issue_ids(conn):

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT issue_id
            FROM issues
            WHERE complexity IS NULL
               OR risk IS NULL
               OR executive_summary IS NULL
            ORDER BY issue_id
            """
        )

        return [row[0] for row in cursor.fetchall()]


def main():

    conn = get_connection()

    ids = pending_issue_ids(conn)

    print(f"Issues pending AI enrichment: {len(ids)}")

    if not ids:
        conn.close()
        return

    issues = {}

    for issue_id in ids:

        issue = get_issue(conn, issue_id)

        if issue:
            issues[issue_id] = issue

    done = 0
    failed = 0

    #
    # LLM calls run in parallel; database writes stay on this thread.
    #
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:

        futures = {
            pool.submit(enrich_with_retry, issue): issue_id
            for issue_id, issue in issues.items()
        }

        for future in as_completed(futures):

            issue_id = futures[future]

            key = issues[issue_id].issue_key

            try:
                analysis = future.result()

            except Exception as ex:
                failed += 1
                print(f"FAILED {key}: {ex}")
                continue

            update_ai_analysis(conn, issue_id, analysis)

            done += 1

            print(
                f"{key}: complexity={analysis.complexity} "
                f"risk={analysis.risk.value} "
                f"({done}/{len(issues)})"
            )

    conn.close()

    print()
    print(f"Enriched {done} issues, {failed} failures.")


if __name__ == "__main__":
    main()
