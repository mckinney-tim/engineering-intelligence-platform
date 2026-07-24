"""
Engineering Intelligence Demo

Load Departments from the design workbook into PostgreSQL.
"""

import pandas as pd

from generator.config import (
    WORKBOOK_PATH,
    SHEET_DEPARTMENTS,
)

from generator.db import get_connection


def load_departments():

    print("Loading Departments...")

    df = pd.read_excel(WORKBOOK_PATH, sheet_name=SHEET_DEPARTMENTS)

    conn = get_connection()
    cursor = conn.cursor()

    for _, row in df.iterrows():

        cursor.execute(
            """
            INSERT INTO departments
            (department_name, description)
            VALUES (%s, %s)
            """,
            (row["department_name"], row["description"]),
        )

    conn.commit()

    cursor.close()
    conn.close()

    print(f"Loaded {len(df)} departments.")
