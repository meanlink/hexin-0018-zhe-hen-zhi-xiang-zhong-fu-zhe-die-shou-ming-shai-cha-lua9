"""Format-specific Isolation Forest with immutable evidence references."""
import hashlib
import json

from sklearn.ensemble import IsolationForest

from core.errors import DomainError
from domain.control_store import MIN_BASELINE
from domain.fold_features import features

MODEL_SPEC = "crease-iforest-v1/trees120/auto/seed617"
ANOMALY_SCORE = 0.58


def calculate(reference, reading):
    if len(reference) < MIN_BASELINE:
        raise DomainError(409, "insufficient historical folds for this box format")
    training = [features(row) for row in reference]
    keyed = [(row["sample_code"], vector) for row, vector in zip(reference, training, strict=True)]
    serialized = json.dumps([MODEL_SPEC, keyed], separators=(",", ":"))
    estimator = IsolationForest(n_estimators=120, contamination="auto", random_state=617, n_jobs=1)
    estimator.fit(training)
    score = float(-estimator.score_samples([features(reading)])[0])
    return score, hashlib.sha256(serialized.encode()).hexdigest()
