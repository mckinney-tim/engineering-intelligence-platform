from fastapi import FastAPI
from fastapi import Query

from generator.ai.portfolio import analyze_portfolio
from generator.db import (
    get_connection,
    get_issues,
)

app = FastAPI(title="Engineering Intelligence API")


@app.get("/")
def root():
    return {"status": "Engineering Intelligence API Running"}


@app.get("/api/v1/portfolio")
def portfolio(
    customer: list[str] | None = Query(None),
    project: list[str] | None = Query(None),
    status: list[str] | None = Query(None),
    priority: list[str] | None = Query(None),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    limit: int = Query(100),
):

    def normalize(values):
        if not values:
            return None

        # Grafana sometimes sends "{Open,Closed}"
        if len(values) == 1 and values[0].startswith("{"):
            return [v.strip() for v in values[0].strip("{}").split(",") if v.strip()]

        return values

    customer = normalize(customer)
    project = normalize(project)
    status = normalize(status)
    priority = normalize(priority)

    conn = get_connection()

    try:

        issues = get_issues(
            conn,
            customer=customer,
            project=project,
            status=status,
            priority=priority,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )

        analysis = analyze_portfolio(issues)

        return analysis

    finally:

        conn.close()
