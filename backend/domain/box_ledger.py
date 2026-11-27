"""One lock per case-bearing physical box serializes station transitions."""
from core.errors import DomainError


def box(conn, box_id, lock=False):
    sql = "SELECT * FROM loop_boxes WHERE id = %s"
    if lock:
        sql += " FOR UPDATE"
    row = conn.execute(sql, (box_id,)).fetchone()
    if row is None:
        raise DomainError(404, "physical box does not exist")
    return row


def register(conn, spec, username):
    row = conn.execute(
        """
        INSERT INTO loop_boxes(label, format, depot, fold_count, registered_by)
        VALUES (%(label)s, %(format)s, %(depot)s, %(fold_count)s, %(username)s)
        ON CONFLICT (label) DO NOTHING RETURNING *
        """,
        {**spec, "username": username},
    ).fetchone()
    if row is None:
        raise DomainError(409, "box label is already registered")
    return row


def change(conn, box_id, status):
    return conn.execute(
        "UPDATE loop_boxes SET status = %s WHERE id = %s RETURNING *",
        (status, box_id),
    ).fetchone()


def require(row, *states):
    if row["status"] not in states:
        raise DomainError(409, f'box is {row["status"]}; operation requires {", ".join(states)}')
