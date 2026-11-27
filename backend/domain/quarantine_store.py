"""Hold cases reserve physical rack positions until approved close-out."""
from core.errors import DomainError


def current(conn, box_id):
    return conn.execute(
        "SELECT * FROM quarantine_cases WHERE box_id = %s AND closed_at IS NULL", (box_id,)
    ).fetchone()


def get(conn, case_id):
    row = conn.execute("SELECT * FROM quarantine_cases WHERE id = %s", (case_id,)).fetchone()
    if row is None:
        raise DomainError(404, "quarantine case does not exist")
    return row


def reserve(conn, depot):
    while True:
        available = conn.execute(
            """
            SELECT r.label FROM inspection_racks r
            WHERE r.depot = %s AND NOT EXISTS (
                SELECT 1 FROM quarantine_cases q WHERE q.rack = r.label AND q.closed_at IS NULL
            )
            ORDER BY r.label LIMIT 1 FOR UPDATE OF r SKIP LOCKED
            """,
            (depot,),
        ).fetchone()
        if available is None:
            return None
        # Read again while holding the rack lock in case a different claim
        # committed after the candidate SELECT took its snapshot.
        occupied = conn.execute(
            "SELECT 1 FROM quarantine_cases WHERE rack = %s AND closed_at IS NULL",
            (available["label"],),
        ).fetchone()
        if occupied is None:
            return available

def open_case(conn, box):
    rack = reserve(conn, box["depot"])
    return conn.execute(
        "INSERT INTO quarantine_cases (box_id, depot, rack) VALUES (%s, %s, %s) RETURNING *",
        (box["id"], box["depot"], None if rack is None else rack["label"]),
    ).fetchone()


def place_on_rack(conn, record):
    if record["closed_at"] is not None:
        raise DomainError(409, "closed quarantine cases cannot claim a rack")
    if record["rack"]:
        return record
    rack = reserve(conn, record["depot"])
    if rack is None:
        raise DomainError(409, "all quarantine positions are occupied at this depot")
    return conn.execute(
        "UPDATE quarantine_cases SET rack = %s WHERE id = %s RETURNING *",
        (rack["label"], record["id"]),
    ).fetchone()


def finish(conn, case_id, disposition, note, username):
    return conn.execute(
        """
        UPDATE quarantine_cases SET closed_at = now(), disposition = %s, close_note = %s, closed_by = %s
        WHERE id = %s AND closed_at IS NULL RETURNING *
        """,
        (disposition, note, username, case_id),
    ).fetchone()


def active_board(conn, depot):
    return conn.execute(
        """
        SELECT q.id, b.label AS box, b.status, q.rack, q.opened_at
        FROM quarantine_cases q JOIN loop_boxes b ON b.id = q.box_id
        WHERE q.depot = %s AND q.closed_at IS NULL
        ORDER BY q.rack IS NULL DESC, q.opened_at, q.id
        """,
        (depot,),
    ).fetchall()
