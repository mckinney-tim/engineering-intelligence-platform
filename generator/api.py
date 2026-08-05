"""
Engineering Intelligence API.

Serves portfolio-level AI analysis to Grafana. Results are cached per
filter combination so the dashboard's panels (which all request the
same analysis) share a single LLM call and stay consistent with each
other.
"""

import hashlib
import json
import threading
import time
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI
from fastapi import Query
from fastapi.responses import HTMLResponse, StreamingResponse

from generator.ai.analyst import ANALYSES, stream_analysis
from generator.ai.portfolio import analyze_portfolio
from generator.db import (
    get_connection,
    get_issues,
)

PANEL_HTML = (Path(__file__).parent / "static" / "analyst.html").read_text()
ARCHITECTURE_HTML = (Path(__file__).parent / "static" / "architecture.html").read_text()

app = FastAPI(title="Engineering Intelligence API")


# ------------------------------------------------------------------
# Analysis Cache
#
# The AI dashboard renders one analysis across several panels, and
# each panel issues its own HTTP request. Without a cache that means
# one LLM call per panel per refresh - slow, expensive, and the
# panels can disagree with each other.
# ------------------------------------------------------------------

CACHE_TTL_SECONDS = 15 * 60

_cache: dict[str, tuple[float, dict]] = {}
_cache_lock = threading.Lock()

#
# Single-flight: when several panels request the same analysis at the
# same moment (dashboard load), only the first computes; the rest
# block on the per-key lock and then read the cached result.
#
_key_locks: dict[str, threading.Lock] = {}


def _key_lock(key: str) -> threading.Lock:

    with _cache_lock:
        return _key_locks.setdefault(key, threading.Lock())


def _cache_key(**params) -> str:

    normalized = json.dumps(params, sort_keys=True, default=str)

    return hashlib.sha256(normalized.encode()).hexdigest()


def _cache_get(key: str) -> dict | None:

    with _cache_lock:

        entry = _cache.get(key)

        if entry is None:
            return None

        created, value = entry

        if time.time() - created > CACHE_TTL_SECONDS:
            del _cache[key]
            return None

        return value


def _cache_put(key: str, value: dict):

    with _cache_lock:
        _cache[key] = (time.time(), value)


def _normalize(values):
    """
    Grafana interpolates multi-value variables differently depending
    on context: "{Open,Closed}" in datasource URLs, "Open, Closed" in
    text panels. Accept both, plus repeated query params.
    """

    if not values:
        return None

    if len(values) == 1:

        value = values[0].strip()

        if value.startswith("{") and value.endswith("}"):
            value = value[1:-1]

        if "," in value:
            return [v.strip() for v in value.split(",") if v.strip()]

        return [value] if value else None

    return values


def _load_filtered_issues(
    customer,
    project,
    status,
    priority,
    start_date,
    end_date,
    limit,
):

    conn = get_connection()

    try:

        return get_issues(
            conn,
            customer=_normalize(customer),
            project=_normalize(project),
            status=_normalize(status),
            priority=_normalize(priority),
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )

    finally:

        conn.close()


@app.get("/")
def root():
    return {"status": "Engineering Intelligence API Running"}


# ------------------------------------------------------------------
# AI Analyst Panel
#
# Embedded in Grafana as an iframe. The dashboard passes its filter
# variables and time range in the URL, so the analyst always works
# on the same recordset the surrounding panels display.
# ------------------------------------------------------------------


@app.get("/panel")
def panel():
    return HTMLResponse(PANEL_HTML)


@app.get("/architecture")
def architecture():
    return HTMLResponse(ARCHITECTURE_HTML)


@app.get("/api/v1/analyses")
def analyses():
    return [
        {"id": analysis_id, "label": item["label"]}
        for analysis_id, item in ANALYSES.items()
    ]


@app.get("/api/v1/scope")
def scope(
    customer: list[str] | None = Query(None),
    project: list[str] | None = Query(None),
    status: list[str] | None = Query(None),
    priority: list[str] | None = Query(None),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    limit: int = Query(250),
):

    issues = _load_filtered_issues(
        customer, project, status, priority, start_date, end_date, limit
    )

    return {
        "issue_count": len(issues),
        "limit": limit,
        "truncated": len(issues) >= limit,
    }


@app.get("/api/v1/analyze")
def analyze(
    customer: list[str] | None = Query(None),
    project: list[str] | None = Query(None),
    status: list[str] | None = Query(None),
    priority: list[str] | None = Query(None),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    limit: int = Query(250),
    analysis: str | None = Query(None),
    question: str | None = Query(None),
):

    if question:
        effective_question = question

    elif analysis in ANALYSES:
        effective_question = ANALYSES[analysis]["prompt"]

    else:
        effective_question = ANALYSES["executive"]["prompt"]

    issues = _load_filtered_issues(
        customer, project, status, priority, start_date, end_date, limit
    )

    return StreamingResponse(
        stream_analysis(effective_question, issues),
        media_type="text/plain; charset=utf-8",
    )


@app.get("/api/v1/portfolio")
def portfolio(
    customer: list[str] | None = Query(None),
    project: list[str] | None = Query(None),
    status: list[str] | None = Query(None),
    priority: list[str] | None = Query(None),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    limit: int = Query(250),
    refresh: bool = Query(False),
):

    customer = _normalize(customer)
    project = _normalize(project)
    status = _normalize(status)
    priority = _normalize(priority)

    key = _cache_key(
        customer=customer,
        project=project,
        status=status,
        priority=priority,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )

    if not refresh:

        cached = _cache_get(key)

        if cached is not None:
            return cached

    with _key_lock(key):

        #
        # Another request may have computed this while we waited.
        #
        if not refresh:

            cached = _cache_get(key)

            if cached is not None:
                return cached

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

            analysis = asdict(analyze_portfolio(issues))

            analysis["issue_count"] = len(issues)

        finally:

            conn.close()

        _cache_put(key, analysis)

        return analysis
