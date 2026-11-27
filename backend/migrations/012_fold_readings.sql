CREATE TABLE fold_readings (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    box_id bigint NOT NULL REFERENCES loop_boxes(id),
    case_id bigint REFERENCES quarantine_cases(id),
    cycle_no integer NOT NULL CHECK (cycle_no BETWEEN 1 AND 3000),
    left_set_mm double precision NOT NULL CHECK (left_set_mm BETWEEN 0 AND 60),
    right_set_mm double precision NOT NULL CHECK (right_set_mm BETWEEN 0 AND 60),
    grip_drift_mm double precision NOT NULL CHECK (grip_drift_mm BETWEEN 0 AND 40),
    closure_force_n double precision NOT NULL CHECK (closure_force_n BETWEEN 0 AND 200),
    crease_crack_mm double precision NOT NULL CHECK (crease_crack_mm BETWEEN 0 AND 100),
    bench text NOT NULL,
    recorded_by text NOT NULL,
    job_id bigint REFERENCES jobs(id) UNIQUE,
    score double precision,
    flags text[] NOT NULL DEFAULT '{}',
    baseline_digest text,
    baseline_rows integer,
    verdict text CHECK (verdict IN ('clear','anomalous')),
    UNIQUE (box_id, cycle_no)
);

CREATE INDEX fold_history ON fold_readings(box_id, cycle_no DESC);
