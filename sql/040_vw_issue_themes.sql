-- =====================================================
-- View: vw_issue_themes
-- One row per Issue / Theme
-- =====================================================

DROP VIEW IF EXISTS vw_issue_themes;

CREATE VIEW vw_issue_themes AS

SELECT

    -- Issue
    i.issue_id,
    i.issue_key,
    i.title,
    i.priority,
    i.status,
    i.weight,
    i.created_date,
    i.closed_date,

    -- Project
    p.project_name,

    -- Customer
    c.customer_name,

    -- Team
    t.team_name,

    -- Assignee
    e.first_name || ' ' || e.last_name AS assignee,

    -- Theme
    th.theme_name

FROM issues i

LEFT JOIN projects p
    ON i.project_id = p.project_id

LEFT JOIN customers c
    ON p.customer_id = c.customer_id

LEFT JOIN employees e
    ON i.assignee_id = e.employee_id

LEFT JOIN teams t
    ON e.team_id = t.team_id

LEFT JOIN issue_themes ith
    ON i.issue_id = ith.issue_id

LEFT JOIN themes th
    ON ith.theme_id = th.theme_id;