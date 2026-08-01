"""
Skill enrichment for Engineering Issues.
"""

from generator.db import get_connection

# ------------------------------------------------------------------
# Build Dictionary
# ------------------------------------------------------------------


def build_dictionary(rows):

    dictionary = []

    for row in rows:

        dictionary.append(
            {
                "id": row[0],
                "name": row[1],
                "keywords": [
                    keyword.strip().lower()
                    for keyword in (row[2] or "").split(",")
                    if keyword.strip()
                ],
            }
        )

    return dictionary


# ------------------------------------------------------------------
# Match Dictionary
# ------------------------------------------------------------------


def match_dictionary(search_text, dictionary):

    matches = []

    for item in dictionary:

        for keyword in item["keywords"]:

            if keyword in search_text:

                matches.append(
                    {
                        "id": item["id"],
                        "name": item["name"],
                        "keyword": keyword,
                    }
                )

                #
                # Don't match the same skill twice.
                #
                break

    return matches


# ------------------------------------------------------------------
# Save Skill Matches
# ------------------------------------------------------------------


def save_skill_matches(cursor, issue_id, matches):

    #
    # Remove existing matches.
    #
    cursor.execute(
        """
        DELETE FROM issue_skills
        WHERE issue_id = %s
        """,
        (issue_id,),
    )

    for match in matches:

        cursor.execute(
            """
            INSERT INTO issue_skills
            (
                issue_id,
                skill_id,
                matched_keyword
            )
            VALUES (%s,%s,%s)
            """,
            (
                issue_id,
                match["id"],
                match["keyword"],
            ),
        )


# ------------------------------------------------------------------
# Enrich One Issue
# ------------------------------------------------------------------


def enrich(conn, issue_id):

    cursor = conn.cursor()

    #
    # Load the issue
    #
    cursor.execute(
        """
        SELECT
            title,
            description,
            labels
        FROM issues
        WHERE issue_id = %s
        """,
        (issue_id,),
    )

    issue = cursor.fetchone()

    if issue is None:
        return

    title = issue[0] or ""
    description = issue[1] or ""
    labels = issue[2] or ""

    search_text = f"{title} {description} {labels}".lower()

    #
    # Load the skill dictionary
    #
    cursor.execute("""
        SELECT
            skill_id,
            skill_name,
            keywords
        FROM skills
        WHERE active='Y'
        ORDER BY skill_name
        """)

    skills = build_dictionary(cursor.fetchall())

    #
    # Match skills
    #
    matches = match_dictionary(
        search_text,
        skills,
    )

    #
    # Save
    #
    save_skill_matches(
        cursor,
        issue_id,
        matches,
    )

    conn.commit()

    print(f"   Skills: {len(matches)}")

    cursor.close()
