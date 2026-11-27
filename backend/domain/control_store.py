"""Append-only unlabeled histories from comparable format bins."""
from core.errors import DomainError

MIN_BASELINE = 40


def add(conn, sample, repeat=False):
    row = conn.execute(
        """
        INSERT INTO control_cycles(sample_code, format, cycle_no, left_set_mm, right_set_mm,
            grip_drift_mm, closure_force_n, crease_crack_mm, source)
        VALUES (%(sample_code)s, %(format)s, %(cycle_no)s, %(left_set_mm)s, %(right_set_mm)s,
            %(grip_drift_mm)s, %(closure_force_n)s, %(crease_crack_mm)s, %(source)s)
        ON CONFLICT (sample_code) DO NOTHING RETURNING *
        """,
        sample,
    ).fetchone()
    if row is None and not repeat:
        raise DomainError(409, "reference fold tag already exists")
    return row


def reference(conn, format_code):
    return conn.execute(
        "SELECT * FROM control_cycles WHERE format = %s ORDER BY sample_code",
        (format_code,),
    ).fetchall()


def size(conn, format_code):
    return conn.execute(
        "SELECT count(*) AS samples FROM control_cycles WHERE format = %s",
        (format_code,),
    ).fetchone()["samples"]


def overview(conn):
    return conn.execute(
        """
        SELECT format, count(*) AS samples, min(cycle_no) AS first_cycle, max(cycle_no) AS last_cycle
        FROM control_cycles GROUP BY format ORDER BY format
        """
    ).fetchall()
