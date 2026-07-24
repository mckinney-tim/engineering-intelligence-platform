-- =====================================================
-- Engineering Intelligence Platform
-- Reporting Views
-- =====================================================

DROP VIEW IF EXISTS vw_issue_intelligence;

CREATE VIEW vw_issue_intelligence AS

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

    -- Employee
    e.first_name || ' ' || e.last_name AS assignee,

    -- Skill
    s.skill_name,
    s.category AS skill_category,

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

LEFT JOIN issue_skills isk
    ON i.issue_id = isk.issue_id

LEFT JOIN skills s
    ON isk.skill_id = s.skill_id

LEFT JOIN issue_themes ith
    ON i.issue_id = ith.issue_id

LEFT JOIN themes th
    ON ith.theme_id = th.theme_id;