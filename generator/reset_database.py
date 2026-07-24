from generator.db import get_connection


def reset_database():

    print("Resetting database...")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        TRUNCATE TABLE
        issue_skills,
        issues,
        projects,
        customers,
        products,
        employees,
        teams,
        departments,
        skills,
        themes
        RESTART IDENTITY CASCADE;
    """)

    conn.commit()

    cursor.close()
    conn.close()

    print("Database reset complete.")
