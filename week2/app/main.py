from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from .config import settings
from .db import init_db
from .exceptions import AppError
from .routers import action_items, notes

init_db()

app = FastAPI(title=settings.app_name, debug=settings.debug)


@app.exception_handler(AppError)
async def app_error_handler(request: Any, exc: AppError) -> dict[str, Any]:
    """Handle custom application errors."""
    return {"detail": exc.message, "status": exc.status_code}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Any, exc: RequestValidationError) -> dict[str, Any]:
    """Handle Pydantic validation errors."""
    return {"detail": str(exc), "status": 422}


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Any, exc: StarletteHTTPException) -> dict[str, Any]:
    """Handle HTTP exceptions."""
    return {"detail": exc.detail, "status": exc.status_code}


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    html_path = Path(__file__).resolve().parents[1] / "frontend" / "index.html"
    return html_path.read_text(encoding="utf-8")


app.include_router(notes.router)
app.include_router(action_items.router)


static_dir = Path(__file__).resolve().parents[1] / "frontend"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
