"""Handoffs for the next mover and return intake."""
from fastapi import APIRouter, Depends

from core.access import allow
from core.db import transaction
from domain import trip_ledger
from domain.contracts import DispatchInput, NoteInput

router = APIRouter(tags=["Issue and return tickets"])
staff = allow("admin", "operator")


@router.get("/boxes/{box_id}/dispatches")
def history(box_id: int, _=Depends(allow())):
    with transaction() as conn:
        return trip_ledger.history(conn, box_id)


@router.post("/boxes/{box_id}/dispatches")
def dispatch(box_id: int, body: DispatchInput, actor=Depends(staff)):
    with transaction() as conn:
        return trip_ledger.issue(conn, box_id, body.model_dump(), actor["username"])


@router.get("/dispatches/{ticket_id}")
def detail(ticket_id: int, _=Depends(allow())):
    with transaction() as conn:
        return trip_ledger.get(conn, ticket_id)


@router.post("/dispatches/{ticket_id}/return")
def receive(ticket_id: int, body: NoteInput, actor=Depends(staff)):
    with transaction() as conn:
        return trip_ledger.return_box(conn, ticket_id, body.note, actor["username"])
