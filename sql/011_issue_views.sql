-- =====================================================
-- Engineering Intelligence Platform
-- Issue Detail View
-- One row per issue
-- Primary data source for Grafana dashboards
-- =====================================================

DROP VIEW IF EXISTS vw_issue_details;

CREATE VIEW vw_issue_details AS

SELECT

    -- Issue Information
    i.issue_id,
    i.issue_key,
    i.title,
    i.description,
    i.issue_type,
    i.priority,
    i.severity,
    i.status,
    i.weight,
    i.labels,
    i.complexity,
    i.risk,
    i.executive_summary,

    -- Friendly Dates
    i.created_date::date AS created_date,
    i.closed_date::date AS closed_date,

    -- Derived Metric
    CASE
        WHEN i.closed_date IS NULL
            THEN CURRENT_DATE - i.created_date
        ELSE i.closed_date - i.created_date
    END AS issue_age_days,

    -- Project Hierarchy
    c.customer_name,
    p.project_name,

    -- Organization
    t.team_name,

    -- Assignee
    CASE
        WHEN e.employee_id IS NULL THEN 'Unassigned'
        ELSE CONCAT(e.first_name, ' ', e.last_name)
    END AS assignee,

    -- Source Information
    i.source,
    i.external_id,
    i.external_url

FROM issues i

LEFT JOIN projects p
    ON i.project_id = p.project_id

LEFT JOIN customers c
    ON p.customer_id = c.customer_id

LEFT JOIN employees e
    ON i.assignee_id = e.employee_id

LEFT JOIN teams t
    ON e.team_id = t.team_id;