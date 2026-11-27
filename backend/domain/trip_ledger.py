"""Issue and return tickets trace the exact fold that permitted a trip."""
from core.errors import DomainError
from domain import box_ledger, fold_store, quarantine_store


def get(conn, ticket_id):
    row = conn.execute("SELECT * FROM dispatch_tickets WHERE id = %s", (ticket_id,)).fetchone()
    if row is None:
        raise DomainError(404, "dispatch ticket does not exist")
    return row


def history(conn, box_id):
    box_ledger.box(conn, box_id)
    return conn.execute(
        "SELECT * FROM dispatch_tickets WHERE box_id = %s ORDER BY id DESC LIMIT 100",
        (box_id,),
    ).fetchall()


def issue(conn, box_id, changes, username):
    box = box_ledger.box(conn, box_id, lock=True)
    box_ledger.require(box, "eligible")
    last = fold_store.readings(conn, box_id, 1)
    if not last or last[0]["verdict"] != "clear" or quarantine_store.current(conn, box_id):
        raise DomainError(409, "there is no current cleared fold for dispatch")
    ticket = conn.execute(
        """
        INSERT INTO dispatch_tickets(ticket, box_id, reading_id, route_code, issued_by)
        VALUES (%(ticket)s, %(box_id)s, %(reading_id)s, %(route_code)s, %(username)s)
        ON CONFLICT (ticket) DO NOTHING RETURNING *
        """,
        {**changes, "box_id": box_id, "reading_id": last[0]["id"], "username": username},
    ).fetchone()
    if ticket is None:
        raise DomainError(409, "dispatch ticket code was already used")
    box_ledger.change(conn, box_id, "dispatched")
    return ticket


def return_box(conn, ticket_id, note, username):
    initial = get(conn, ticket_id)
    box = box_ledger.box(conn, initial["box_id"], lock=True)
    ticket = get(conn, ticket_id)
    if ticket["returned_at"] is not None:
        raise DomainError(409, "trip already returned")
    box_ledger.require(box, "dispatched")
    updated = conn.execute(
        """
        UPDATE dispatch_tickets SET returned_at = now(), receiving_note = %s, received_by = %s
        WHERE id = %s RETURNING *
        """,
        (note, username, ticket_id),
    ).fetchone()
    box_ledger.change(conn, box["id"], "awaiting_test")
    return updated
