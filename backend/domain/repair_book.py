"""Repair progression preserves the case and each counted attempt."""
from core.errors import DomainError
from domain import box_ledger
from domain.station_limits import MAX_FOLD_COUNT, MAX_REPAIRS


def begin(conn, box, case, changes, username):
    box_ledger.require(box, "isolated")
    if box["repair_count"] >= MAX_REPAIRS:
        raise DomainError(409, "repair allowance exhausted; retire the box")
    if box["fold_count"] >= MAX_FOLD_COUNT:
        raise DomainError(409, "fold counter limit reached; retire the box")
    if case["rack"] is None:
        raise DomainError(409, "assign a quarantine rack before repair")
    params = {
        **changes, "box_id": box["id"], "case_id": case["id"],
        "username": username, "repair_no": box["repair_count"] + 1,
    }
    entry = conn.execute(
        """
        INSERT INTO repair_entries(case_id, box_id, repair_no, method, note, performed_by)
        VALUES (%(case_id)s, %(box_id)s, %(repair_no)s, %(method)s, %(note)s, %(username)s)
        RETURNING *
        """,
        params,
    ).fetchone()
    conn.execute(
        "UPDATE loop_boxes SET status = 'repair', repair_count = %s WHERE id = %s",
        (entry["repair_no"], box["id"]),
    )
    return entry


def history(conn, case_id):
    return conn.execute(
        "SELECT * FROM repair_entries WHERE case_id = %s ORDER BY repair_no", (case_id,)
    ).fetchall()
