"""
Engineering Intelligence Platform

Database connection utilities.
"""

import os

import psycopg2
from dotenv import load_dotenv

from generator.engineering_models import EngineeringIssue

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


def get_issue(conn, issue_id) -> EngineeringIssue | None:
    """
    Load a fully populated EngineeringIssue from the database.
    """

    #
    # Load the issue
    #
    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                i.source,
                i.external_id,
                i.external_url,
                i.issue_key,

                i.title,
                i.description,
                i.status,

                i.created_date,
                i.closed_date,

                p.project_name,

                CASE
                    WHEN e.employee_id IS NULL THEN NULL
                    ELSE e.first_name || ' ' || e.last_name
                END AS assignee,

                i.labels,
                i.issue_type,
                i.priority,
                i.severity,

                i.weight,
                i.complexity,
                i.risk,
                i.executive_summary

            FROM issues i

            JOIN projects p
              ON i.project_id = p.project_id

            LEFT JOIN employees e
              ON i.assignee_id = e.employee_id

            WHERE i.issue_id = %s
            """,
            (issue_id,),
        )

        row = cursor.fetchone()

    if row is None:
        return None

    #
    # Convert labels into a list
    #
    labels = []

    if row[11]:
        labels = [label.strip() for label in row[11].split(",") if label.strip()]

    #
    # Load detected skills
    #
    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                s.skill_name
            FROM issue_skills isk

            JOIN skills s
              ON isk.skill_id = s.skill_id

            WHERE isk.issue_id = %s

            ORDER BY s.skill_name
            """,
            (issue_id,),
        )

        skills = [r[0] for r in cursor.fetchall()]

    #
    # Load detected themes
    #
    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                t.theme_name
            FROM issue_themes ith

            JOIN themes t
              ON ith.theme_id = t.theme_id

            WHERE ith.issue_id = %s

            ORDER BY t.theme_name
            """,
            (issue_id,),
        )

        themes = [r[0] for r in cursor.fetchall()]

    return EngineeringIssue(
        source=row[0],
        external_id=row[1],
        external_url=row[2],
        issue_key=row[3],
        title=row[4],
        description=row[5],
        status=row[6],
        created_date=row[7],
        closed_date=row[8],
        project_name=row[9],
        assignee=row[10],
        labels=labels,
        issue_type=row[12],
        priority=row[13],
        severity=row[14],
        weight=row[15],
        skills=skills,
        themes=themes,
        complexity=row[16],
        risk=row[17],
        executive_summary=row[18],
    )


def update_ai_analysis(conn, issue_id, analysis):
    """
    Persist AI-generated analysis for an issue.
    """

    with conn.cursor() as cursor:

        cursor.execute(
            """
            UPDATE issues
            SET
                executive_summary = %s,
                complexity = %s,
                risk = %s
            WHERE issue_id = %s
            """,
            (
                analysis.executive_summary,
                analysis.complexity,
                analysis.risk.value,
                issue_id,
            ),
        )

    conn.commit()


def get_all_github_issues(conn):
    """
    Returns all GitHub issues as EngineeringIssue objects.
    """

    with conn.cursor() as cursor:

        cursor.execute("""
            SELECT issue_id
            FROM issues
            WHERE source = 'GITHUB'
            ORDER BY issue_key
            """)

        issue_ids = [row[0] for row in cursor.fetchall()]

    issues = []

    for issue_id in issue_ids:

        issue = get_issue(
            conn,
            issue_id,
        )

        if issue:
            issues.append(issue)

    return issues


def get_issues(
    conn,
    customer: list[str] | None = None,
    project: list[str] | None = None,
    status: list[str] | None = None,
    priority: list[str] | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 100,
):
    """
    Returns EngineeringIssue objects matching optional filters.
    """

    sql = """
        SELECT issue_id
        FROM vw_issue_details
        WHERE 1 = 1
    """

    params = []

    if customer:
        sql += " AND customer_name = ANY(%s)"
        params.append(customer)

    if project:
        sql += " AND project_name = ANY(%s)"
        params.append(project)

    if status:
        sql += " AND status = ANY(%s)"
        params.append(status)

    if priority:
        sql += " AND priority = ANY(%s)"
        params.append(priority)

    if start_date:
        sql += " AND created_date >= %s"
        params.append(start_date)

    if end_date:
        sql += " AND created_date <= %s"
        params.append(end_date)

    sql += """
        ORDER BY created_date DESC
        LIMIT %s
    """

    params.append(limit)

    with conn.cursor() as cursor:
        cursor.execute(sql, params)
        ids = [row[0] for row in cursor.fetchall()]

    issues = []

    for issue_id in ids:
        issue = get_issue(conn, issue_id)
        if issue:
            issues.append(issue)

    return issues


if __name__ == "__main__":

    conn = get_connection()

    print("Connected!")
    print(conn.get_dsn_parameters())

    conn.close()
