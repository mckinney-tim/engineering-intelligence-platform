import pandas as pd

from generator.config import (
    WORKBOOK_PATH,
    SHEET_THEMES,
)

from generator.db import get_connection


def load_themes():

    print("Loading Themes...")

    df = pd.read_excel(WORKBOOK_PATH, sheet_name=SHEET_THEMES)

    conn = get_connection()
    cursor = conn.cursor()

    for _, row in df.iterrows():

        cursor.execute(
            """
        INSERT INTO themes
        (
            theme_name,
            description,
            keywords,
            active
        )            
        VALUES (%s,%s,%s,%s)
        """,
            (row["Theme"], row["Description"], row["Keywords"], row["Active"]),
        )

    conn.commit()

    cursor.close()
    conn.close()

    print(f"Loaded {len(df)} skills.")
