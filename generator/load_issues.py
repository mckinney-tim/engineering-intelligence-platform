import pandas as pd

from generator.config import (
    WORKBOOK_PATH,
    SHEET_ISSUES,
)

from generator.db import (
    get_connection,
    get_project_id,
    get_employee_id,
)


def load_issues():

    print("Loading Issues...")

    df = pd.read_excel(
        WORKBOOK_PATH,
        sheet_name=SHEET_ISSUES,
    )

    conn = get_connection()
    cursor = conn.cursor()

    for _, row in df.iterrows():

        project_id = get_project_id(
            cursor,
            row["project_name"],
        )

        assignee_id = get_employee_id(
            cursor,
            row["assignee"],
        )

        created_date = row["created_date"]
        closed_date = row["closed_date"]

        if pd.isna(created_date):
            created_date = None

        if pd.isna(closed_date):
            closed_date = None

        cursor.execute(
            """
            INSERT INTO issues
            (
                issue_key,
                project_id,
                assignee_id,
                title,
                description,
                labels,
                issue_type,
                priority,
                severity,
                status,
                weight,
                created_date,
                closed_date
            )
            VALUES
            (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                row["issue_key"],
                project_id,
                assignee_id,
                row["title"],
                row["description"],
                row["labels"],
                row["issue_type"],
                row["priority"],
                row["severity"],
                row["status"],
                row["weight"],
                created_date,
                closed_date,
            ),
        )

    conn.commit()

    cursor.close()
    conn.close()

    print(f"Loaded {len(df)} issues.")
