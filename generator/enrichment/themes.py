"""
Theme enrichment for Engineering Issues.
"""

from generator.enrichment.skills import build_dictionary, match_dictionary


def save_theme_matches(cursor, issue_id, matches):

    #
    # Remove existing matches.
    #
    cursor.execute(
        """
        DELETE FROM issue_themes
        WHERE issue_id = %s
        """,
        (issue_id,),
    )

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
            """,
            (
                issue_id,
                match["id"],
                match["keyword"],
            ),
        )


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
    # Load the theme dictionary
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

    #
    # Match themes
    #
    matches = match_dictionary(
        search_text,
        themes,
    )

    #
    # Save
    #
    save_theme_matches(
        cursor,
        issue_id,
        matches,
    )

    conn.commit()

    print(f"   Themes: {len(matches)}")

    cursor.close()
