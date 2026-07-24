import pandas as pd

from generator.config import (
    WORKBOOK_PATH,
    SHEET_CUSTOMERS,
)

from generator.db import get_connection


def load_customers():

    print("Loading Customers...")

    df = pd.read_excel(
        WORKBOOK_PATH,
        sheet_name=SHEET_CUSTOMERS,
    )

    conn = get_connection()
    cursor = conn.cursor()

    for _, row in df.iterrows():

        cursor.execute(
            """
            INSERT INTO customers
            (
                customer_name,
                industry,
                company_size,
                region,
                customer_tier,
                active,
                onboarding_date
            )
            VALUES
            (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                row["customer_name"],
                row["industry"],
                row["company_size"],
                row["region"],
                row["customer_tier"],
                row["active"],
                row["onboarding_date"],
            ),
        )

    conn.commit()

    cursor.close()
    conn.close()

    print(f"Loaded {len(df)} customers.")
