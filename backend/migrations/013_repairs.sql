CREATE TABLE repair_entries (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    case_id bigint NOT NULL REFERENCES quarantine_cases(id),
    box_id bigint NOT NULL REFERENCES loop_boxes(id),
    repair_no integer NOT NULL CHECK (repair_no BETWEEN 1 AND 2),
    method text NOT NULL CHECK (method IN ('crease_tape','handle_patch','tab_replace')),
    note text NOT NULL,
    performed_by text NOT NULL,
    performed_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (box_id, repair_no)
);
