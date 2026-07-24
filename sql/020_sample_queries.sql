SELECT
    COUNT(*) AS total_issues,
    COUNT(*) FILTER (WHERE status = 'Open') AS open_issues,
    COUNT(*) FILTER (WHERE status = 'Closed') AS closed_issues,
    SUM(weight) AS total_weight,
    AVG(weight)::numeric(10,2) AS average_weight
FROM issues;

SELECT
    status,
    COUNT(*) AS issue_count
FROM issues
GROUP BY status
ORDER BY issue_count DESC;

SELECT
    priority,
    COUNT(*) AS issue_count
FROM issues
GROUP BY priority
ORDER BY issue_count DESC;

SELECT
    s.skill_name,
    s.category,
    COUNT(*) AS issue_count
FROM issue_skills isk
JOIN skills s
    ON isk.skill_id = s.skill_id
GROUP BY
    s.skill_name,
    s.category
ORDER BY issue_count DESC,
         s.skill_name;

SELECT
    t.theme_name,
    COUNT(*) AS issue_count
FROM issue_themes it
JOIN themes t
    ON it.theme_id = t.theme_id
GROUP BY
    t.theme_name
ORDER BY issue_count DESC;

SELECT
    tm.team_name,
    s.skill_name,
    COUNT(*) AS issue_count
FROM issue_skills isk
JOIN issues i
    ON isk.issue_id = i.issue_id
JOIN employees e
    ON i.assignee_id = e.employee_id
JOIN teams tm
    ON e.team_id = tm.team_id
JOIN skills s
    ON isk.skill_id = s.skill_id
GROUP BY
    tm.team_name,
    s.skill_name
ORDER BY
    tm.team_name,
    issue_count DESC;

SELECT
    c.customer_name,
    s.skill_name,
    COUNT(*) AS issue_count
FROM issue_skills isk
JOIN issues i
    ON isk.issue_id = i.issue_id
JOIN projects p
    ON i.project_id = p.project_id
JOIN customers c
    ON p.customer_id = c.customer_id
JOIN skills s
    ON isk.skill_id = s.skill_id
GROUP BY
    c.customer_name,
    s.skill_name
ORDER BY
    c.customer_name,
    issue_count DESC;

