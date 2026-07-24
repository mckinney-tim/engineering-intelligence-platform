import pandas as pd

from generator.config import (
    WORKBOOK_PATH,
    SHEET_SKILLS,
)

from generator.db import get_connection


def load_skills():

    print("Loading Skills...")

    df = pd.read_excel(
        WORKBOOK_PATH,
        sheet_name=SHEET_SKILLS,
    )

    conn = get_connection()
    cursor = conn.cursor()

    for _, row in df.iterrows():

        cursor.execute(
            """
            INSERT INTO skills
            (
                skill_name,
                category,
                keywords,
                active
            )
            VALUES (%s,%s,%s,%s)
        """,
            (row["Skill"], row["Category"], row["Keywords"], row["Active"]),
        )

    conn.commit()

    cursor.close()
    conn.close()

    print(f"Loaded {len(df)} skills.")
