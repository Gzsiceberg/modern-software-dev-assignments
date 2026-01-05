from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ExtractRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to extract action items from")
    save_note: bool = Field(default=False, description="Whether to save the text as a note")


class NoteCreate(BaseModel):
    content: str = Field(..., min_length=1, description="Note content")


class NoteResponse(BaseModel):
    id: int
    content: str
    created_at: str


class ActionItemResponse(BaseModel):
    id: int
    note_id: int | None
    text: str
    done: bool
    created_at: str


class ExtractResponse(BaseModel):
    note_id: int | None
    items: list[dict[str, Any]]


class ActionItemUpdate(BaseModel):
    done: bool = Field(default=True, description="Mark action item as done or not done")
