"""
Apply the complete database schema.

Executes every DDL file in sql/ in order, so a fresh clone can build
the database with no manual steps. 020_sample_queries.sql is excluded
because it contains ad-hoc reporting queries, not schema.
"""

from pathlib import Path

from generator.config import PROJECT_ROOT
from generator.db import get_connection

SQL_DIR = PROJECT_ROOT / "sql"

EXCLUDED_FILES = {"020_sample_queries.sql"}


def apply_schema():

    print("Applying database schema...")

    sql_files = sorted(
        path
        for path in SQL_DIR.glob("*.sql")
        if path.name not in EXCLUDED_FILES
    )

    conn = get_connection()
    cursor = conn.cursor()

    for path in sql_files:

        print(f"   {path.name}")

        cursor.execute(path.read_text())

    conn.commit()

    cursor.close()
    conn.close()

    print("Schema applied.")


if __name__ == "__main__":
    apply_schema()
