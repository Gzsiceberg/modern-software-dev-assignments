# AGENTS.md

This file provides guidelines for agentic coding assistants working on this repository.

## Build/Lint/Test Commands

### Running the Server
```bash
uv run uvicorn week2.app.main:app --reload --host 127.0.0.1 --port 8000
```

### Running Tests
```bash
# Run all tests
uv run pytest week2/tests/

# Run tests with verbose output
uv run pytest week2/tests/ -v

# Run a single test
uv run pytest week2/tests/test_extract.py::test_extract_bullets_and_checkboxes -v

# Run tests for a specific test file
uv run pytest week2/tests/test_extract.py
```

### Code Quality Commands
```bash
# Format code (black + ruff auto-fix)
uv run black .
uv run ruff check . --fix

# Lint code (check for issues)
uv run ruff check .

# Check a specific file
uv run ruff check week2/app/services/extract.py

# Check formatting without modifying files
uv run black --check .
```

## Code Style Guidelines

### Imports
- **Always start with**: `from __future__ import annotations`
- Import order: standard library → third-party → local imports
- Imports must be sorted alphabetically (enforced by ruff)
- Group imports with one blank line between groups
- Remove unused imports

```python
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List, Optional

import httpx
from fastapi import APIRouter, HTTPException

from .. import db
from ..services.extract import extract_action_items
```

### Type Annotations
- Use modern Python 3.10+ union syntax: `str | None` instead of `Optional[str]`
- Always specify return types for functions
- Use built-in types when possible: `list[str]`, `dict[str, int]`, etc.
- Import types from `typing` for complex cases: `List`, `Dict`, `Any`

```python
def extract_action_items(text: str) -> list[str]:
    return []

def get_note(note_id: int) -> sqlite3.Row | None:
    pass
```

### Naming Conventions
- **Functions and variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private functions**: `_leading_underscore`
- **Module names**: `snake_case`

```python
MAX_RETRIES = 3
BASE_URL = "https://api.example.com"

class ActionItem:
    pass

def extract_action_items(text: str) -> list[str]:
    pass

def _is_action_line(line: str) -> bool:
    pass
```

### Function Definitions
- Type hints on all parameters and return values
- Docstrings only when adding explanatory comments (inline comments preferred)
- Use descriptive names, not abbreviations
- Default values after type hints

```python
def insert_action_items(items: list[str], note_id: int | None = None) -> list[int]:
    with get_connection() as connection:
        cursor = connection.cursor()
        ids: list[int] = []
        for item in items:
            cursor.execute("INSERT INTO action_items (note_id, text) VALUES (?, ?)", (note_id, item))
            ids.append(int(cursor.lastrowid))
        connection.commit()
        return ids
```

### Error Handling
- Use `HTTPException` for API errors with appropriate status codes
- Validate input and raise 400 Bad Request for missing/invalid data
- Raise 404 Not Found when resources don't exist
- Use descriptive error messages

```python
from fastapi import HTTPException

def create_note(payload: dict[str, Any]) -> dict[str, Any]:
    content = str(payload.get("content", "")).strip()
    if not content:
        raise HTTPException(status_code=400, detail="content is required")
    note_id = db.insert_note(content)
    return {"id": note_id, "content": content}
```

### Database Patterns
- Use context managers (`with get_connection()`) for all database operations
- Use parameterized queries (not f-strings) to prevent SQL injection
- Commit transactions explicitly
- Use `row_factory = sqlite3.Row` for dictionary-like row access

```python
def get_connection() -> sqlite3.Connection:
    ensure_data_directory_exists()
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def list_notes() -> list[sqlite3.Row]:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT id, content, created_at FROM notes ORDER BY id DESC")
        return list(cursor.fetchall())
```

### FastAPI Router Patterns
- Use `APIRouter` with prefix and tags
- Define endpoints with descriptive names
- Use `@router` decorators consistently
- Return type hints for responses

```python
router = APIRouter(prefix="/action-items", tags=["action-items"])

@router.post("/extract")
def extract(payload: dict[str, Any]) -> dict[str, Any]:
    text = str(payload.get("text", "")).strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")
    items = extract_action_items(text)
    return {"items": items}
```

### Code Organization
- Keep functions focused and under 20 lines when possible
- Extract helper functions with `_leading_underscore` prefix
- Use list comprehensions and generator expressions
- Avoid nested loops when possible
- Prefer early returns over deep nesting

### Linting Rules
- Line length: 100 characters
- Ruff rules: E (errors), F (pyflakes), I (isort), UP (pyupgrade), B (bugbear)
- Ignore: E501 (line length - handled by black), B008 (function call in argument defaults)

### Environment
- Use `python-dotenv` for environment variables
- Activate conda environment: `conda activate cs146s`
- Dependencies managed via uv at repository root
- Python version: 3.10+

### Testing
- Use pytest for all tests
- Test files in `week2/tests/` directory
- Test functions start with `test_`
- Use descriptive test names
- Test both success and error cases
- Use `assert` statements for assertions

```python
def test_extract_llm_bullet_list():
    text = """
    Meeting notes:
    - Review the pull request
    - Fix the authentication bug
    """
    items = extract_action_items_llm(text)
    assert len(items) > 0
    assert all(isinstance(item, str) for item in items)
```

## Important Notes

- Always run lint and typecheck after making changes: `uv run black . && uv run ruff check . --fix`
- If lint commands are not found, ask the user for the correct commands
- Never commit secrets (API keys, passwords, tokens)
- Use parameterized queries for all SQL to prevent injection
- Test API endpoints with the running server
- The Ollama model "llama3.1:8b" is available for LLM operations
- SQLite database stored in `week2/data/app.db`
- Frontend served from `week2/frontend/index.html`
