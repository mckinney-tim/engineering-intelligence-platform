-- ============================================================================
-- Engineering Intelligence Demo
-- File: 001_create_tables.sql
--
-- Purpose:
--     Creates the complete database schema for the Engineering Intelligence
--     Platform proof of concept.
--
-- Author: Timothy McKinney
-- Version: 1.0
-- ============================================================================

-- ============================================================================
-- Drop Existing Tables
-- ============================================================================

DROP TABLE IF EXISTS issue_skills CASCADE;
DROP TABLE IF EXISTS issues CASCADE;
DROP TABLE IF EXISTS skills CASCADE;
DROP TABLE IF EXISTS themes CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS employees CASCADE;
DROP TABLE IF EXISTS teams CASCADE;
DROP TABLE IF EXISTS departments CASCADE;

-- ============================================================================
-- Organization
-- ============================================================================

CREATE TABLE departments
(
    department_id      SERIAL PRIMARY KEY,
    department_name    VARCHAR(100) NOT NULL UNIQUE,
    description        TEXT
);

CREATE TABLE teams
(
    team_id            SERIAL PRIMARY KEY,
    department_id      INTEGER NOT NULL,
    team_name          VARCHAR(100) NOT NULL UNIQUE,
    team_lead          VARCHAR(100),
    mission            TEXT,

    CONSTRAINT fk_team_department
        FOREIGN KEY (department_id)
        REFERENCES departments(department_id)
);

CREATE TABLE employees
(
    employee_id        SERIAL PRIMARY KEY,
    employee_number    VARCHAR(20) UNIQUE,

    first_name         VARCHAR(50) NOT NULL,
    last_name          VARCHAR(50) NOT NULL,

    email              VARCHAR(150) UNIQUE,

    title              VARCHAR(100),

    department_id      INTEGER,
    team_id            INTEGER,
    manager_id         INTEGER,

    hire_date          DATE,

    location           VARCHAR(100),

    status             VARCHAR(25),

    CONSTRAINT fk_employee_department
        FOREIGN KEY (department_id)
        REFERENCES departments(department_id),

    CONSTRAINT fk_employee_team
        FOREIGN KEY (team_id)
        REFERENCES teams(team_id),

    CONSTRAINT fk_employee_manager
        FOREIGN KEY (manager_id)
        REFERENCES employees(employee_id)
);

-- ============================================================================
-- Business
-- ============================================================================

CREATE TABLE products
(
    product_id         SERIAL PRIMARY KEY,

    product_name       VARCHAR(100) NOT NULL UNIQUE,

    description        TEXT,

    owner_team_id      INTEGER,

    CONSTRAINT fk_product_team
        FOREIGN KEY (owner_team_id)
        REFERENCES teams(team_id)
);

CREATE TABLE customers
(
    customer_id        SERIAL PRIMARY KEY,

    customer_name      VARCHAR(150) NOT NULL,

    industry           VARCHAR(100),

    company_size       VARCHAR(50),

    region             VARCHAR(100)
);

CREATE TABLE projects
(
    project_id         SERIAL PRIMARY KEY,

    project_name       VARCHAR(150) NOT NULL,

    product_id         INTEGER,

    customer_id        INTEGER,

    status             VARCHAR(50),

    start_date         DATE,

    target_date        DATE,

    CONSTRAINT fk_project_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id),

    CONSTRAINT fk_project_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);

-- ============================================================================
-- Reference Data
-- ============================================================================

CREATE TABLE themes
(
    theme_id           SERIAL PRIMARY KEY,

    theme_name         VARCHAR(100) NOT NULL UNIQUE,

    description        TEXT
);

CREATE TABLE skills
(
    skill_id           SERIAL PRIMARY KEY,

    skill_name         VARCHAR(100) NOT NULL UNIQUE,

    category           VARCHAR(100),

    keywords           TEXT
);

-- ============================================================================
-- Engineering Data
-- ============================================================================

CREATE TABLE issues
(
    issue_id           SERIAL PRIMARY KEY,

    issue_key          VARCHAR(30) UNIQUE,

    issue_number       INTEGER,

    title              TEXT NOT NULL,

    description        TEXT,

    labels             TEXT,

    issue_type         VARCHAR(50),

    priority           VARCHAR(25),

    severity           VARCHAR(25),

    status             VARCHAR(50),

    epic               VARCHAR(100),

    story_points       INTEGER,

    estimated_hours    NUMERIC(6,2),

    actual_hours       NUMERIC(6,2),

    product_id         INTEGER,

    project_id         INTEGER,

    assignee_id        INTEGER,

    theme_id           INTEGER,

    created_date       DATE,

    closed_date        DATE,

    CONSTRAINT fk_issue_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id),

    CONSTRAINT fk_issue_project
        FOREIGN KEY (project_id)
        REFERENCES projects(project_id),

    CONSTRAINT fk_issue_assignee
        FOREIGN KEY (assignee_id)
        REFERENCES employees(employee_id),

    CONSTRAINT fk_issue_theme
        FOREIGN KEY (theme_id)
        REFERENCES themes(theme_id)
);

-- ============================================================================
-- Derived Data
-- ============================================================================

CREATE TABLE issue_skills
(
    issue_skill_id     SERIAL PRIMARY KEY,

    issue_id           INTEGER NOT NULL,

    skill_id           INTEGER NOT NULL,

    detection_method   VARCHAR(25) NOT NULL,

    confidence         NUMERIC(4,3),

    CONSTRAINT fk_issue_skill_issue
        FOREIGN KEY (issue_id)
        REFERENCES issues(issue_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_issue_skill_skill
        FOREIGN KEY (skill_id)
        REFERENCES skills(skill_id),

    CONSTRAINT uq_issue_skill
        UNIQUE (issue_id, skill_id, detection_method)
);

-- ============================================================================
-- Schema Created Successfully
-- ============================================================================

SELECT 'Engineering Intelligence Demo schema created successfully.' AS status;