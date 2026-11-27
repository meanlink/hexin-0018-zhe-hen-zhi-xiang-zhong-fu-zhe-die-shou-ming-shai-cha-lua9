"""Dispatch fold analysis from the shared durable queue."""
from core.errors import DomainError
from domain.evaluate import reading_result


def run(conn, kind, payload):
    if kind == "analyze_fold":
        return reading_result(conn, payload["reading_id"])
    raise DomainError(422, f"unknown fold bench job {kind}")
