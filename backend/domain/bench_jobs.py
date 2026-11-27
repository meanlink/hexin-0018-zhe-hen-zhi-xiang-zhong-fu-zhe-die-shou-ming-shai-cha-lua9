"""Bench intake enqueues routine and post-repair inspections with typed provenance."""
from core.errors import DomainError
from core.jobs import enqueue
from domain import box_ledger, control_store, fold_store, quarantine_store


def _queue(conn, reading_id):
    job = enqueue(conn, "analyze_fold", {"reading_id": reading_id})
    reading = fold_store.bind_job(conn, reading_id, job["id"])
    return {"reading": reading, "job": job}


def submit(conn, box_id, fields, username, recheck=False):
    asset = box_ledger.box(conn, box_id, lock=True)
    if recheck:
        box_ledger.require(asset, "repair")
        disposition = quarantine_store.current(conn, box_id)
        case_id = disposition["id"]
        next_state = "rechecking"
    else:
        box_ledger.require(asset, "awaiting_test", "eligible")
        case_id = None
        next_state = "testing"
    if control_store.size(conn, asset["format"]) < control_store.MIN_BASELINE:
        raise DomainError(409, "not enough control folds for the registered format")
    reading = fold_store.add(conn, asset, case_id, fields, username)
    box_ledger.change(conn, box_id, next_state)
    return _queue(conn, reading["id"])


def retry(conn, reading_id):
    initial = fold_store.get(conn, reading_id)
    asset = box_ledger.box(conn, initial["box_id"], lock=True)
    box_ledger.require(asset, "testing", "rechecking")
    record = fold_store.get(conn, reading_id)
    job = conn.execute("SELECT status FROM jobs WHERE id = %s", (record["job_id"],)).fetchone()
    if asset["fold_count"] != record["cycle_no"] or not job or job["status"] != "failed":
        raise DomainError(409, "only the current failed worker request may be retried")
    return _queue(conn, reading_id)
