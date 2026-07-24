"""
Engineering Intelligence Demo

Load Teams from the design workbook into PostgreSQL.
"""

import pandas as pd

from generator.config import (
    WORKBOOK_PATH,
    SHEET_TEAMS,
)

from generator.db import (
    get_connection,
    get_department_id,
)


def load_teams():

    print("Loading Teams...")

    df = pd.read_excel(WORKBOOK_PATH, sheet_name=SHEET_TEAMS)

    conn = get_connection()
    cursor = conn.cursor()

    for _, row in df.iterrows():

        department_id = get_department_id(cursor, row["department_name"])

        cursor.execute(
            """
            INSERT INTO teams
            (
                department_id,
                team_name,
                team_lead,
                mission
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                department_id,
                row["team_name"],
                row["team_lead_title"],
                row["mission"],
            ),
        )

    conn.commit()

    cursor.close()
    conn.close()

    print(f"Loaded {len(df)} teams.")
