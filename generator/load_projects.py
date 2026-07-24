import pandas as pd

from generator.config import (
    WORKBOOK_PATH,
    SHEET_PROJECTS,
)

from generator.db import (
    get_connection,
    get_customer_id,
    get_product_id,
    get_team_id,
    get_employee_id,
)


def load_projects():

    print("Loading Projects...")

    df = pd.read_excel(
        WORKBOOK_PATH,
        sheet_name=SHEET_PROJECTS,
    )

    conn = get_connection()
    cursor = conn.cursor()

    for _, row in df.iterrows():

        customer_id = get_customer_id(
            cursor,
            row["customer_name"],
        )

        product_id = get_product_id(
            cursor,
            row["product_name"],
        )

        team_id = get_team_id(
            cursor,
            row["owning_team"],
        )

        project_manager_id = get_employee_id(
            cursor,
            row["project_manager"],
        )

        cursor.execute(
            """
            INSERT INTO projects
            (
                project_name,
                customer_id,
                product_id,
                owning_team_id,
                project_manager_id,
                status,
                priority,
                start_date,
                target_date
            )
            VALUES
            (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                row["project_name"],
                customer_id,
                product_id,
                team_id,
                project_manager_id,
                row["status"],
                row["priority"],
                row["start_date"],
                row["target_date"],
            ),
        )

    conn.commit()

    cursor.close()
    conn.close()

    print(f"Loaded {len(df)} projects.")
