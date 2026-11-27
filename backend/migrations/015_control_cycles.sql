CREATE TABLE control_cycles (
    sample_code text PRIMARY KEY,
    format text NOT NULL CHECK (format IN ('A40','A60')),
    cycle_no integer NOT NULL CHECK (cycle_no BETWEEN 1 AND 3000),
    left_set_mm double precision NOT NULL CHECK (left_set_mm BETWEEN 0 AND 60),
    right_set_mm double precision NOT NULL CHECK (right_set_mm BETWEEN 0 AND 60),
    grip_drift_mm double precision NOT NULL CHECK (grip_drift_mm BETWEEN 0 AND 40),
    closure_force_n double precision NOT NULL CHECK (closure_force_n BETWEEN 0 AND 200),
    crease_crack_mm double precision NOT NULL CHECK (crease_crack_mm BETWEEN 0 AND 100),
    source text NOT NULL
);

CREATE INDEX control_format ON control_cycles(format, sample_code);
