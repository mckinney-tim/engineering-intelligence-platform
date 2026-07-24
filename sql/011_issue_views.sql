-- =====================================================
-- Engineering Intelligence Platform
-- Issue Detail Views
-- =====================================================

DROP VIEW IF EXISTS vw_issue_details;

CREATE VIEW vw_issue_details AS

SELECT

    i.issue_id,
    i.issue_key,
    i.title,
    i.description,
    i.issue_type,
    i.priority,
    i.severity,
    i.status,
    i.weight,
    i.created_date,
    i.closed_date,

    p.project_name,

    c.customer_name,

    t.team_name,

    e.first_name || ' ' || e.last_name AS assignee

FROM issues i

LEFT JOIN projects p
    ON i.project_id = p.project_id

LEFT JOIN customers c
    ON p.customer_id = c.customer_id

LEFT JOIN employees e
    ON i.assignee_id = e.employee_id

LEFT JOIN teams t
    ON e.team_id = t.team_id;