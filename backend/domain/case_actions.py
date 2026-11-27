"""Disposition policy combines recent bench evidence and reviewer identity."""
from core.errors import DomainError
from domain import box_ledger, fold_store, quarantine_store, repair_book


def locked_case(conn, case_id):
    record = quarantine_store.get(conn, case_id)
    box = box_ledger.box(conn, record["box_id"], lock=True)
    case = quarantine_store.get(conn, case_id)
    if case["closed_at"] is not None:
        raise DomainError(409, "quarantine case already closed")
    return box, case


def move_to_rack(conn, case_id):
    _, case = locked_case(conn, case_id)
    return quarantine_store.place_on_rack(conn, case)


def repair(conn, case_id, changes, username):
    box, case = locked_case(conn, case_id)
    return repair_book.begin(conn, box, case, changes, username)


def close(conn, case_id, disposition, note, username):
    box, case = locked_case(conn, case_id)
    if disposition == "released":
        box_ledger.require(box, "pending_release")
        latest = fold_store.readings(conn, box["id"], 1)[0]
        if latest["case_id"] != case_id or latest["verdict"] != "clear":
            raise DomainError(409, "release requires a clear recheck for the current quarantine case")
        if latest["recorded_by"] == username:
            raise DomainError(409, "a second staff member must review the clear recheck")
    else:
        box_ledger.require(box, "isolated", "pending_release")
    row = quarantine_store.finish(conn, case["id"], disposition, note, username)
    box_ledger.change(conn, box["id"], "eligible" if disposition == "released" else "retired")
    return row
