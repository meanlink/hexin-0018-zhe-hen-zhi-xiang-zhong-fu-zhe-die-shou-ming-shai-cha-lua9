"""Atomic scoring updates the fold record, quarantine and equipment state together."""
from core.errors import DomainError
from domain import anomaly, box_ledger, control_store, fold_store, quarantine_store, station_limits


def reading_result(conn, reading_id):
    initial = fold_store.get(conn, reading_id)
    asset = box_ledger.box(conn, initial["box_id"], lock=True)
    reading = fold_store.get(conn, reading_id)
    box_ledger.require(asset, "rechecking" if reading["case_id"] else "testing")
    if reading["cycle_no"] != asset["fold_count"]:
        raise DomainError(409, "this fold no longer matches the physical box counter")
    samples = control_store.reference(conn, asset["format"])
    score, signature = anomaly.calculate(samples, reading)
    flags = station_limits.measure_flags(asset["format"], reading)
    if score >= anomaly.ANOMALY_SCORE:
        flags.append("shape_outlier")
    graded = fold_store.grade(conn, reading_id, score, flags, signature, len(samples))

    case = None
    if reading["case_id"]:
        case = quarantine_store.get(conn, reading["case_id"])
        next_state = "isolated" if flags else "pending_release"
    elif flags:
        case = quarantine_store.open_case(conn, asset)
        next_state = "isolated"
    else:
        next_state = "eligible"
    box_ledger.change(conn, asset["id"], next_state)
    return {
        "reading_id": reading_id,
        "box_id": asset["id"],
        "score": score,
        "flags": flags,
        "baseline_digest": signature,
        "verdict": graded["verdict"],
        "box_status": next_state,
        "case_id": case["id"] if case else None,
        "rack": case["rack"] if case else None,
    }
