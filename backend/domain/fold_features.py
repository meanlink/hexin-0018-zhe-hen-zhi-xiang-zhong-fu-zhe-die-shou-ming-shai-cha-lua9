"""Mechanical signals derived from two-sided crease measurements."""
from math import log1p

SIGNALS = (
    "log_fold_count", "average_fold_set_mm", "crease_asymmetry_mm", "grip_drift_mm",
    "closure_force_n", "crease_crack_mm",
)


def features(row):
    left, right = row["left_set_mm"], row["right_set_mm"]
    return [
        log1p(row["cycle_no"]), (left + right) / 2, abs(left - right), row["grip_drift_mm"],
        row["closure_force_n"], row["crease_crack_mm"],
    ]
