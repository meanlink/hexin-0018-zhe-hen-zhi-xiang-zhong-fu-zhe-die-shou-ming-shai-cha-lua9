"""Register physical bench measurements for the background classifier."""
from fastapi import APIRouter, Depends

from core.access import allow
from core.db import transaction
from domain import bench_jobs, box_ledger, fold_store
from domain.contracts import FoldInput

router = APIRouter(tags=["Fold bench"])
staff = allow("admin", "operator")


@router.get("/boxes/{box_id}/folds")
def history(box_id: int, _=Depends(allow())):
    with transaction() as conn:
        box_ledger.box(conn, box_id)
        return fold_store.readings(conn, box_id)


@router.get("/folds/{reading_id}")
def detail(reading_id: int, _=Depends(allow())):
    with transaction() as conn:
        return fold_store.get(conn, reading_id)


@router.post("/boxes/{box_id}/folds")
def bench_fold(box_id: int, body: FoldInput, actor=Depends(staff)):
    with transaction() as conn:
        return bench_jobs.submit(conn, box_id, body.model_dump(), actor["username"])


@router.post("/boxes/{box_id}/rechecks")
def recheck(box_id: int, body: FoldInput, actor=Depends(allow("operator"))):
    with transaction() as conn:
        return bench_jobs.submit(conn, box_id, body.model_dump(), actor["username"], recheck=True)


@router.post("/folds/{reading_id}/retry")
def retry(reading_id: int, _=Depends(staff)):
    with transaction() as conn:
        return bench_jobs.retry(conn, reading_id)
