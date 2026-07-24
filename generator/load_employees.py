"""
Engineering Intelligence Demo

Load Employees from the design workbook into PostgreSQL.
"""

import pandas as pd

from generator.config import (
    WORKBOOK_PATH,
    SHEET_EMPLOYEES,
)

from generator.db import (
    get_connection,
    get_department_id,
    get_team_id,
    get_employee_id,
)


def load_employees():

    print("Loading Employees...")

    df = pd.read_excel(
        WORKBOOK_PATH,
        sheet_name=SHEET_EMPLOYEES,
    )

    conn = get_connection()
    cursor = conn.cursor()

    for _, row in df.iterrows():

        department_id = get_department_id(
            cursor,
            row["department"],
        )

        team_id = get_team_id(
            cursor,
            row["team"],
        )

        cursor.execute(
            """
            INSERT INTO employees
            (
                employee_number,
                first_name,
                last_name,
                email,
                title,
                role_type,
                department_id,
                team_id,
                hire_date,
                location,
                status
            )
            VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                row["employee_number"],
                row["first_name"],
                row["last_name"],
                row["email"],
                row["title"],
                row["role_type"],
                department_id,
                team_id,
                row["hire_date"],
                row["location"],
                row["status"],
            ),
        )

    conn.commit()

    cursor.close()
    conn.close()

    print(f"Loaded {len(df)} employees.")


def load_employee_managers():

    print("Loading Employee Managers...")

    df = pd.read_excel(
        WORKBOOK_PATH,
        sheet_name=SHEET_EMPLOYEES,
    )

    conn = get_connection()
    cursor = conn.cursor()

    updates = 0

    for _, row in df.iterrows():

        if pd.isna(row["manager"]):
            continue

        manager_number = str(row["manager"]).strip()

        manager_id = get_employee_id(
            cursor,
            manager_number,
        )

        cursor.execute(
            """
            UPDATE employees
            SET manager_id = %s
            WHERE employee_number = %s
            """,
            (
                manager_id,
                row["employee_number"],
            ),
        )

        updates += 1

    conn.commit()

    cursor.close()
    conn.close()

    print(f"Updated {updates} manager relationships.")
