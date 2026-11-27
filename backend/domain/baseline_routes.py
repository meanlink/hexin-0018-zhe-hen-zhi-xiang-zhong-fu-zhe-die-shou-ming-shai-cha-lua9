"""Inspect historical coverage or append an independently checked control fold."""
from fastapi import APIRouter, Depends

from core.access import allow
from core.db import transaction
from domain import control_store, station_limits
from domain.anomaly import ANOMALY_SCORE, MODEL_SPEC
from domain.fold_features import SIGNALS
from domain.contracts import ControlInput

router = APIRouter(prefix="/baseline", tags=["Unlabeled reference history"])


@router.get("")
def baseline(_=Depends(allow())):
    with transaction() as conn:
        return {"model": MODEL_SPEC, "outlier_score_at": ANOMALY_SCORE, "features": SIGNALS,
                "stock_limits": station_limits.FORMAT_LIMITS, "formats": control_store.overview(conn)}


@router.post("/samples")
def add(body: ControlInput, _=Depends(allow("admin"))):
    with transaction() as conn:
        return control_store.add(conn, body.model_dump(mode="json"))
