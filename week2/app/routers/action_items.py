from __future__ import annotations

from fastapi import APIRouter

from .. import db
from ..schemas import ActionItemResponse, ActionItemUpdate, ExtractRequest, ExtractResponse
from ..services.extract import extract_action_items, extract_action_items_llm

router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post("/extract", response_model=ExtractResponse)
def extract(payload: ExtractRequest) -> ExtractResponse:
    text = payload.text.strip()
    note_id: int | None = None

    if payload.save_note:
        note_id = db.insert_note(text)

    items = extract_action_items(text)
    ids = db.insert_action_items(items, note_id=note_id)
    return ExtractResponse(
        note_id=note_id,
        items=[{"id": i, "text": t} for i, t in zip(ids, items, strict=True)],
    )


@router.post("/extract-llm", response_model=ExtractResponse)
def extract_llm(payload: ExtractRequest) -> ExtractResponse:
    text = payload.text.strip()
    note_id: int | None = None

    if payload.save_note:
        note_id = db.insert_note(text)

    items = extract_action_items_llm(text)
    ids = db.insert_action_items(items, note_id=note_id)
    return ExtractResponse(
        note_id=note_id,
        items=[{"id": i, "text": t} for i, t in zip(ids, items, strict=True)],
    )


@router.get("", response_model=list[ActionItemResponse])
def list_all(note_id: int | None = None) -> list[ActionItemResponse]:
    rows = db.list_action_items(note_id=note_id)
    return [
        ActionItemResponse(
            id=r["id"],
            note_id=r["note_id"],
            text=r["text"],
            done=bool(r["done"]),
            created_at=r["created_at"],
        )
        for r in rows
    ]


@router.post("/{action_item_id}/done", response_model=ActionItemResponse)
def mark_done(action_item_id: int, payload: ActionItemUpdate) -> ActionItemResponse:
    row = db.mark_action_item_done(action_item_id, payload.done)
    return ActionItemResponse(
        id=row["id"],
        note_id=row["note_id"],
        text=row["text"],
        done=bool(row["done"]),
        created_at=row["created_at"],
    )
