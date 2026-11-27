"""Physical box intake and tracking API."""
from fastapi import APIRouter, Depends, Query

from core.access import allow
from core.db import transaction
from domain import box_ledger, station_board
from domain.contracts import BoxInput, Depot

router = APIRouter(prefix="/boxes", tags=["Box intake"])
staff = allow("admin", "operator")


@router.get("")
def list_boxes(depot: Depot | None = None, limit: int = Query(default=40, ge=1, le=100), _=Depends(allow())):
    with transaction() as conn:
        return station_board.list_boxes(conn, depot, limit)


@router.post("")
def add_box(body: BoxInput, actor=Depends(staff)):
    with transaction() as conn:
        return box_ledger.register(conn, body.model_dump(mode="json"), actor["username"])


@router.get("/{box_id}")
def detail(box_id: int, _=Depends(allow())):
    with transaction() as conn:
        return station_board.summary(conn, box_id)
