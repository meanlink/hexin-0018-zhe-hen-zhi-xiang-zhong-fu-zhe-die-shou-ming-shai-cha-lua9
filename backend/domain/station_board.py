"""Shop-floor read projections include current fold, isolation and issue evidence."""
from domain.box_ledger import box
from domain.fold_store import readings
from domain.quarantine_store import current


def list_boxes(conn, depot, limit):
    return conn.execute(
        """
        SELECT * FROM loop_boxes WHERE (%s::text IS NULL OR depot = %s)
        ORDER BY id DESC LIMIT %s
        """,
        (depot, depot, limit),
    ).fetchall()


def summary(conn, box_id):
    current_box = box(conn, box_id)
    active = current(conn, box_id)
    last = readings(conn, box_id, 1)
    trip = conn.execute(
        """
        SELECT id, ticket, route_code, issued_at FROM dispatch_tickets
        WHERE box_id = %s AND returned_at IS NULL
        """,
        (box_id,),
    ).fetchone()
    return {"box": current_box, "active_case": active, "latest_fold": last[0] if last else None,
            "outbound_ticket": trip}
