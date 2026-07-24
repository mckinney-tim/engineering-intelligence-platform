"""
Engineering Intelligence Platform

Extract Skills and Themes from Issues.
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
            ON CONFLICT DO NOTHING
            """,
            (
                issue_id,
                match["id"],
                match["keyword"],
            ),
        )


# ------------------------------------------------------------------
# Save Theme Matches
# ------------------------------------------------------------------


def save_theme_matches(cursor, issue_id, matches):

    for match in matches:

        cursor.execute(
            """
            INSERT INTO issue_themes
            (
                issue_id,
                theme_id,
                matched_keyword
            )
            VALUES (%s,%s,%s)
            ON CONFLICT DO NOTHING
            """,
            (
                issue_id,
                match["id"],
                match["keyword"],
            ),
        )


# ------------------------------------------------------------------
# Main Extraction
# ------------------------------------------------------------------


def extract_issue_metadata():

    print("\nExtracting Issue Metadata...")

    conn = get_connection()
    cursor = conn.cursor()

    #
    # Load Issues
    #

    cursor.execute("""
        SELECT
            issue_id,
            issue_key,
            title,
            description,
            labels
        FROM issues
        ORDER BY issue_id
        """)

    issues = cursor.fetchall()

    #
    # Load Skills
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
    # Load Themes
    #

    cursor.execute("""
        SELECT
            theme_id,
            theme_name,
            keywords
        FROM themes
        WHERE active='Y'
        ORDER BY theme_name
        """)

    themes = build_dictionary(cursor.fetchall())

    print(f"Loaded {len(issues)} issues.")
    print(f"Loaded {len(skills)} skills.")
    print(f"Loaded {len(themes)} themes.")

    print()

    total_skill_matches = 0
    total_theme_matches = 0

    #
    # Process each Issue
    #

    for issue in issues:

        issue_id = issue[0]
        issue_key = issue[1]

        title = issue[2] or ""
        description = issue[3] or ""
        labels = issue[4] or ""

        search_text = (f"{title} {description} {labels}").lower()

        matched_skills = match_dictionary(
            search_text,
            skills,
        )

        matched_themes = match_dictionary(
            search_text,
            themes,
        )

        save_skill_matches(
            cursor,
            issue_id,
            matched_skills,
        )

        save_theme_matches(
            cursor,
            issue_id,
            matched_themes,
        )

        total_skill_matches += len(matched_skills)
        total_theme_matches += len(matched_themes)

        print(f"{issue_key}")

        for match in matched_skills:

            print(f"   Skill : {match['name']} ({match['keyword']})")

        for match in matched_themes:

            print(f"   Theme : {match['name']} ({match['keyword']})")

        print()

    conn.commit()

    cursor.close()
    conn.close()

    print("----------------------------------------")
    print("Extraction Complete")
    print("----------------------------------------")
    print(f"Skill Matches : {total_skill_matches}")
    print(f"Theme Matches : {total_theme_matches}")
