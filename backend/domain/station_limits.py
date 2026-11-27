"""Local shop protocol for demo fixtures, separate from ML outlier triage."""
FORMAT_LIMITS = {
    "A40": {"asymmetry_mm": 5, "grip_drift_mm": 7, "closure_min_n": 18, "crease_crack_mm": 9},
    "A60": {"asymmetry_mm": 6, "grip_drift_mm": 8, "closure_min_n": 22, "crease_crack_mm": 11},
}
MAX_REPAIRS = 2
MAX_FOLD_COUNT = 3000


def measure_flags(format_code, row):
    limit = FORMAT_LIMITS[format_code]
    flags = []
    if row["cycle_no"] >= MAX_FOLD_COUNT:
        flags.append("counter_limit")
    if abs(row["left_set_mm"] - row["right_set_mm"]) > limit["asymmetry_mm"]:
        flags.append("asymmetric_crease")
    if row["grip_drift_mm"] > limit["grip_drift_mm"]:
        flags.append("loose_handle")
    if row["closure_force_n"] < limit["closure_min_n"]:
        flags.append("closure_below_shop_minimum")
    if row["crease_crack_mm"] > limit["crease_crack_mm"]:
        flags.append("open_crease")
    return flags
