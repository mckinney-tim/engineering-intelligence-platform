from generator.apply_schema import apply_schema
from generator.load_departments import load_departments
from generator.load_teams import load_teams
from generator.load_products import load_products
from generator.load_customers import load_customers
from generator.load_projects import load_projects
from generator.load_issues import load_issues
from generator.load_skills import load_skills
from generator.load_themes import load_themes
from generator.extract_issue_metadata import extract_issue_metadata
from generator.load_employees import (
    load_employees,
    load_employee_managers,
)


def main():
    print("Engineering Intelligence Demo")
    print("-----------------------------")
    apply_schema()

    load_departments()
    load_teams()
    load_products()

    load_employees()
    load_employee_managers()

    load_customers()
    load_projects()

    load_skills()
    load_themes()
    load_issues()

    extract_issue_metadata()


if __name__ == "__main__":
    main()
