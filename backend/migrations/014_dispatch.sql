CREATE TABLE dispatch_tickets (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ticket text NOT NULL UNIQUE,
    box_id bigint NOT NULL REFERENCES loop_boxes(id),
    reading_id bigint NOT NULL REFERENCES fold_readings(id),
    route_code text NOT NULL,
    issued_by text NOT NULL,
    issued_at timestamptz NOT NULL DEFAULT now(),
    returned_at timestamptz,
    received_by text,
    receiving_note text
);

CREATE UNIQUE INDEX one_outbound_per_box ON dispatch_tickets(box_id) WHERE returned_at IS NULL;
