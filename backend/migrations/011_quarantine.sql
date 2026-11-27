CREATE TABLE inspection_racks (
    label text PRIMARY KEY,
    depot text NOT NULL CHECK (depot IN ('north','south')),
    UNIQUE (label, depot)
);

CREATE TABLE quarantine_cases (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    box_id bigint NOT NULL REFERENCES loop_boxes(id),
    depot text NOT NULL,
    rack text,
    opened_at timestamptz NOT NULL DEFAULT now(),
    closed_at timestamptz,
    disposition text CHECK (disposition IN ('released','retired')),
    closed_by text,
    close_note text,
    FOREIGN KEY (rack,depot) REFERENCES inspection_racks(label,depot),
    CHECK ((closed_at IS NULL) = (disposition IS NULL))
);

CREATE UNIQUE INDEX one_open_quarantine_per_box ON quarantine_cases(box_id) WHERE closed_at IS NULL;
CREATE UNIQUE INDEX one_open_case_per_rack ON quarantine_cases(rack) WHERE closed_at IS NULL;
