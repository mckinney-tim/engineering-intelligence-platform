"""
Engineering Intelligence Demo

Load Products from the design workbook into PostgreSQL.
"""

import pandas as pd

from generator.config import (
    WORKBOOK_PATH,
    SHEET_PRODUCTS,
)

from generator.db import (
    get_connection,
    get_team_id,
)


def load_products():

    print("Loading Products...")

    df = pd.read_excel(WORKBOOK_PATH, sheet_name=SHEET_PRODUCTS)

    conn = get_connection()
    cursor = conn.cursor()

    for _, row in df.iterrows():

        owner_team_id = get_team_id(cursor, row["owning_team"])

        cursor.execute(
            """
            INSERT INTO products
            (
                product_name,
                description,
                owner_team_id,
                product_manager_title,
                target_users,
                maturity
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                row["product_name"],
                row["primary_purpose"],
                owner_team_id,
                row["product_manager_title"],
                row["target_users"],
                row["maturity"],
            ),
        )

    conn.commit()

    cursor.close()
    conn.close()

    print(f"Loaded {len(df)} products.")
