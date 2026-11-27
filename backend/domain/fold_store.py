"""Fold readings key each observation to a physical box and monotone counter."""
from core.errors import DomainError


def readings(conn, box_id, limit=100):
    return conn.execute(
        """
        SELECT * FROM fold_readings WHERE box_id = %s ORDER BY cycle_no DESC LIMIT %s
        """,
        (box_id, limit),
    ).fetchall()


def get(conn, reading_id):
    row = conn.execute("SELECT * FROM fold_readings WHERE id = %s", (reading_id,)).fetchone()
    if row is None:
        raise DomainError(404, "fold reading does not exist")
    return row


def add(conn, box, case_id, submitted, username):
    if submitted["cycle_no"] <= box["fold_count"]:
        raise DomainError(409, "new bench reading must advance the physical fold count")
    row = conn.execute(
        """
        INSERT INTO fold_readings(box_id, case_id, cycle_no, left_set_mm, right_set_mm,
            grip_drift_mm, closure_force_n, crease_crack_mm, bench, recorded_by)
        VALUES (%(box_id)s, %(case_id)s, %(cycle_no)s, %(left_set_mm)s, %(right_set_mm)s,
            %(grip_drift_mm)s, %(closure_force_n)s, %(crease_crack_mm)s, %(bench)s, %(username)s)
        RETURNING *
        """,
        {**submitted, "box_id": box["id"], "case_id": case_id, "username": username},
    ).fetchone()
    conn.execute("UPDATE loop_boxes SET fold_count = %s WHERE id = %s", (row["cycle_no"], box["id"]))
    return row


def bind_job(conn, reading_id, job_id):
    return conn.execute(
        "UPDATE fold_readings SET job_id = %s WHERE id = %s RETURNING *",
        (job_id, reading_id),
    ).fetchone()


def grade(conn, reading_id, score, flags, signature, rows):
    return conn.execute(
        """
        UPDATE fold_readings SET score = %s, flags = %s, baseline_digest = %s,
            baseline_rows = %s, verdict = %s WHERE id = %s RETURNING *
        """,
        (score, flags, signature, rows, "anomalous" if flags else "clear", reading_id),
    ).fetchone()
