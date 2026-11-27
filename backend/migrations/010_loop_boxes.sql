CREATE TABLE loop_boxes (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    label text NOT NULL UNIQUE,
    format text NOT NULL CHECK (format IN ('A40','A60')),
    depot text NOT NULL CHECK (depot IN ('north','south')),
    fold_count integer NOT NULL CHECK (fold_count BETWEEN 0 AND 3000),
    repair_count integer NOT NULL DEFAULT 0 CHECK (repair_count BETWEEN 0 AND 2),
    status text NOT NULL DEFAULT 'awaiting_test' CHECK (status IN (
        'awaiting_test','testing','eligible','isolated','repair','rechecking',
        'pending_release','dispatched','retired'
    )),
    registered_by text NOT NULL
);
