-- =====================================================
-- View: vw_engineering_intelligence
-- One row per engineering issue with analytical metrics
-- =====================================================

DROP VIEW IF EXISTS vw_engineering_intelligence;

CREATE VIEW vw_engineering_intelligence AS

SELECT

    -- Issue
    i.issue_id,
    i.issue_key,
    i.title,

    -- Business
    c.customer_name,
    p.project_name,

    -- Ownership
    t.team_name,
    e.first_name || ' ' || e.last_name AS assignee,

    -- Metrics
    i.priority,
    i.status,
    i.weight,
    i.created_date,
    i.closed_date,

    -- Intelligence Metrics
    COUNT(DISTINCT isk.skill_id)  AS skill_count,
    COUNT(DISTINCT ith.theme_id)  AS theme_count,

    i.external_url AS issue_url

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

LEFT JOIN issue_themes ith
       ON i.issue_id = ith.issue_id

GROUP BY

    i.issue_id,
    i.issue_key,
    i.title,

    c.customer_name,
    p.project_name,

    t.team_name,
    e.first_name,
    e.last_name,

    i.priority,
    i.status,
    i.weight,
    i.created_date,
    i.closed_date;