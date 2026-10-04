import time

from flask import Response, g, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest


HTTP_REQUESTS_TOTAL = Counter(
    "employee_app_http_requests_total",
    "Total number of HTTP requests handled by the Flask application.",
    ["method", "route", "status"],
)

HTTP_REQUESTS_IN_PROGRESS = Gauge(
    "employee_app_http_requests_in_progress",
    "Number of HTTP requests currently being processed.",
    ["method", "route"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "employee_app_http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ["method", "route"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

EMPLOYEE_OPERATIONS_TOTAL = Counter(
    "employee_app_employee_operations_total",
    "Total number of successful employee create, update, and delete operations.",
    ["operation"],
)

EMPLOYEES_CURRENT = Gauge(
    "employee_app_employees_current",
    "Current number of employees stored in the application database.",
)

DATABASE_UP = Gauge(
    "employee_app_database_up",
    "Whether the application can successfully query its database (1 = up, 0 = down).",
)


def _route_label():
    """Return the Flask route template instead of the raw URL."""
    if request.url_rule is None:
        return "unmatched"
    return request.url_rule.rule


def init_metrics(app):
    """Register Prometheus instrumentation and the /metrics endpoint."""

    # Pre-create the CRUD counter label values so they are visible as 0 even
    # before the first add/edit/delete operation occurs.
    for operation in ("add", "edit", "delete"):
        EMPLOYEE_OPERATIONS_TOTAL.labels(operation=operation)

    @app.before_request
    def prometheus_before_request():
        # Do not measure Prometheus scraping itself.
        if request.path == "/metrics":
            return None

        route = _route_label()
        g.prometheus_start_time = time.perf_counter()
        g.prometheus_method = request.method
        g.prometheus_route = route
        g.prometheus_in_progress = True

        HTTP_REQUESTS_IN_PROGRESS.labels(
            method=request.method,
            route=route,
        ).inc()

        return None

    @app.after_request
    def prometheus_after_request(response):
        start_time = getattr(g, "prometheus_start_time", None)
        if start_time is None:
            return response

        method = g.prometheus_method
        route = g.prometheus_route
        duration = time.perf_counter() - start_time

        HTTP_REQUESTS_TOTAL.labels(
            method=method,
            route=route,
            status=str(response.status_code),
        ).inc()

        HTTP_REQUEST_DURATION_SECONDS.labels(
            method=method,
            route=route,
        ).observe(duration)

        return response

    @app.teardown_request
    def prometheus_teardown_request(_exception):
        if not getattr(g, "prometheus_in_progress", False):
            return

        HTTP_REQUESTS_IN_PROGRESS.labels(
            method=g.prometheus_method,
            route=g.prometheus_route,
        ).dec()
        g.prometheus_in_progress = False

    @app.get("/metrics")
    def metrics():
        # Refresh application/database gauges at scrape time so Prometheus gets
        # the current value rather than a stale value from application startup.
        try:
            from app.models import Employee

            EMPLOYEES_CURRENT.set(Employee.query.count())
            DATABASE_UP.set(1)
        except Exception:
            # Keep /metrics available even if the database has a problem.
            DATABASE_UP.set(0)

        return Response(generate_latest(), content_type=CONTENT_TYPE_LATEST)
