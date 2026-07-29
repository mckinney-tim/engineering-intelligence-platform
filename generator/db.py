"""
Engineering Intelligence Platform

Database connection utilities.
"""

import os

import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_connection():
    """
    Create and return a PostgreSQL connection.
    """

    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


def get_department_id(cursor, department_name):
    """
    Returns the department_id for the given department name.
    Raises an exception if the department is not found.
    """

    cursor.execute(
        """
        SELECT department_id
        FROM departments
        WHERE department_name = %s
        """,
        (department_name,),
    )

    result = cursor.fetchone()

    if result is None:
        raise ValueError(f"Department not found: {department_name}")

    return result[0]


def get_team_id(cursor, team_name):
    """
    Returns the team_id for the given team name.
    Raises an exception if the team is not found.
    """

    cursor.execute(
        """
        SELECT team_id
        FROM teams
        WHERE team_name = %s
        """,
        (team_name,),
    )

    result = cursor.fetchone()

    if result is None:
        raise ValueError(f"Team not found: {team_name}")

    return result[0]


def get_employee_id(cursor, employee_number):

    cursor.execute(
        """
        SELECT employee_id
        FROM employees
        WHERE employee_number = %s
        """,
        (employee_number,),
    )

    result = cursor.fetchone()

    if result is None:
        raise ValueError(f"Employee not found: {employee_number}")

    return result[0]


def update_manager(cursor, employee_number, manager_id):

    cursor.execute(
        """
        UPDATE employees
        SET manager_id = %s
        WHERE employee_number = %s
        """,
        (
            manager_id,
            employee_number,
        ),
    )


def get_customer_id(cursor, customer_name):

    cursor.execute(
        """
        SELECT customer_id
        FROM customers
        WHERE customer_name = %s
        """,
        (customer_name,),
    )

    result = cursor.fetchone()

    if result is None:
        raise ValueError(f"Customer not found: {customer_name}")

    return result[0]


def get_product_id(cursor, product_name):

    cursor.execute(
        """
        SELECT product_id
        FROM products
        WHERE product_name = %s
        """,
        (product_name,),
    )

    result = cursor.fetchone()

    if result is None:
        raise ValueError(f"Product not found: {product_name}")

    return result[0]


def get_project_id(cursor, project_name):

    cursor.execute(
        """
        SELECT project_id
        FROM projects
        WHERE project_name = %s
        """,
        (project_name,),
    )

    result = cursor.fetchone()

    if result is None:
        raise ValueError(f"Project not found: {project_name}")

    return result[0]


def upsert_issue(conn, issue):
    """
    Insert or update an EngineeringIssue.

    Returns:
        issue_id (int)
    """

    with conn.cursor() as cursor:

        project_id = get_project_id(
            cursor,
            issue.project_name,
        )

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
                closed_date,
                source,
                external_id,
                external_url
            )
            VALUES
            (
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s
            )

            ON CONFLICT (source, external_id)

            DO UPDATE SET

                issue_key = EXCLUDED.issue_key,
                project_id = EXCLUDED.project_id,
                assignee_id = EXCLUDED.assignee_id,
                title = EXCLUDED.title,
                description = EXCLUDED.description,
                labels = EXCLUDED.labels,
                issue_type = EXCLUDED.issue_type,
                priority = EXCLUDED.priority,
                severity = EXCLUDED.severity,
                status = EXCLUDED.status,
                weight = EXCLUDED.weight,
                created_date = EXCLUDED.created_date,
                closed_date = EXCLUDED.closed_date,
                external_url = EXCLUDED.external_url

            RETURNING issue_id
            """,
            (
                issue.issue_key,
                project_id,
                None,  # assignee_id (future enhancement)
                issue.title,
                issue.description,
                issue.labels,
                issue.issue_type,
                issue.priority,
                issue.severity,
                issue.status,
                issue.weight,
                issue.created_date,
                issue.closed_date,
                issue.source,
                issue.external_id,
                issue.external_url,
            ),
        )

        issue_id = cursor.fetchone()[0]

    conn.commit()

    return issue_id


if __name__ == "__main__":

    conn = get_connection()

    print("Connected!")
    print(conn.get_dsn_parameters())

    conn.close()
