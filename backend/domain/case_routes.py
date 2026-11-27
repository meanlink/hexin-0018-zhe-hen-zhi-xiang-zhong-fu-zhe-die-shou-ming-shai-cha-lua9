"""Manage scarce isolation space, repair attempts and two-person release."""
from fastapi import APIRouter, Depends

from core.access import allow
from core.db import transaction
from domain import case_actions, quarantine_store, repair_book
from domain.contracts import Depot, NoteInput, RepairInput

router = APIRouter(prefix="/quarantine", tags=["Quarantine and disposition"])
staff = allow("admin", "operator")
lead = allow("admin")


@router.get("")
def board(depot: Depot = Depot.NORTH, _=Depends(allow())):
    with transaction() as conn:
        return quarantine_store.active_board(conn, depot)


@router.get("/{case_id}")
def detail(case_id: int, _=Depends(allow())):
    with transaction() as conn:
        case = quarantine_store.get(conn, case_id)
        return {**case, "repairs": repair_book.history(conn, case_id)}


@router.post("/{case_id}/rack")
def put_away(case_id: int, _=Depends(staff)):
    with transaction() as conn:
        return case_actions.move_to_rack(conn, case_id)


@router.post("/{case_id}/repairs")
def add_repair(case_id: int, body: RepairInput, actor=Depends(staff)):
    with transaction() as conn:
        return case_actions.repair(conn, case_id, body.model_dump(mode="json"), actor["username"])


@router.post("/{case_id}/release")
def release(case_id: int, body: NoteInput, actor=Depends(lead)):
    with transaction() as conn:
        return case_actions.close(conn, case_id, "released", body.note, actor["username"])


@router.post("/{case_id}/retire")
def retire(case_id: int, body: NoteInput, actor=Depends(lead)):
    with transaction() as conn:
        return case_actions.close(conn, case_id, "retired", body.note, actor["username"])
