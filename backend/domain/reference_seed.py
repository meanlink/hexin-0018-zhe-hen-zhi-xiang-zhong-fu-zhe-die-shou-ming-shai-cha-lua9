"""Repeatable simulated in-service fold histories per stock format."""
import random


def simulated_controls():
    rng = random.Random(617)
    for code, adjustment in (("A40", 0.0), ("A60", 0.55)):
        for index in range(96):
            folds = rng.randint(60, 560)
            set_mm = 2.3 + 0.0038 * folds + adjustment + rng.uniform(-0.4, 0.4)
            yield {
                "sample_code": f"REF-{code}-{index + 1:03d}",
                "format": code,
                "cycle_no": folds,
                "left_set_mm": round(set_mm + rng.uniform(-0.4, 0.4), 3),
                "right_set_mm": round(set_mm + rng.uniform(-0.4, 0.4), 3),
                "grip_drift_mm": round(1.3 + adjustment + rng.uniform(-0.7, 0.7), 3),
                "closure_force_n": round(43 + 7 * adjustment - 0.006 * folds + rng.uniform(-4, 4), 3),
                "crease_crack_mm": round(0.35 + 0.0021 * folds + rng.uniform(-0.4, 0.4), 3),
                "source": "simulated return bench fleet sample v1",
            }
