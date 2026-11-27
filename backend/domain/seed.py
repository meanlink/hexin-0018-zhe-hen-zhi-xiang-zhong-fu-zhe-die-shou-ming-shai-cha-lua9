"""Install baseline controls, racks and incoming demonstration boxes."""
from domain.control_store import add
from domain.reference_seed import simulated_controls


def seed(conn):
    for sample in simulated_controls():
        add(conn, sample, repeat=True)
    conn.execute(
        """
        INSERT INTO inspection_racks(label, depot) VALUES ('N-HOLD-01','north'), ('S-HOLD-01','south')
        ON CONFLICT (label) DO NOTHING
        """
    )
    conn.execute(
        """
        INSERT INTO loop_boxes(label, format, depot, fold_count, registered_by)
        VALUES ('LOOP-N-0408','A40','north',299,'demo-seed'), ('LOOP-N-0414','A40','north',300,'demo-seed'),
            ('LOOP-S-0610','A60','south',300,'demo-seed')
        ON CONFLICT (label) DO NOTHING
        """
    )
