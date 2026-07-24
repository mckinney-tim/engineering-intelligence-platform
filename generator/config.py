"""
Engineering Intelligence Demo

Application configuration settings.
"""

from pathlib import Path

# Project Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKBOOK_PATH = PROJECT_ROOT / "design" / "HD_Systems_Design_Workbook.xlsx"

# Worksheet Names
SHEET_DEPARTMENTS = "02_Departments"
SHEET_TEAMS = "03_Teams"
SHEET_EMPLOYEES = "04_Employees"
SHEET_PRODUCTS = "05_Products"
SHEET_PROJECTS = "06_Projects"
SHEET_CUSTOMERS = "07_Customers"
SHEET_SKILLS = "11_Skills"
SHEET_THEMES = "12_Themes"
SHEET_ISSUES = "13_Issues"
