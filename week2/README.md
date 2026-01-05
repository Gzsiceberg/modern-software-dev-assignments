# Action Item Extractor

A FastAPI + SQLite application that converts free-form meeting notes and text into structured, actionable items. The application provides both heuristic-based and LLM-powered extraction methods, enabling users to efficiently track tasks and manage their notes.

## Features

- **Dual Extraction Methods**:
  - Heuristic-based extraction: Fast pattern matching for bullets, checkboxes, and action keywords
  - LLM-powered extraction: Intelligent extraction using local Ollama (llama3.1:8b) model

- **Note Management**: Create, view, and store notes with extracted action items
- **Task Tracking**: Mark action items as complete with checkbox functionality
- **RESTful API**: Well-structured API with Pydantic schemas for validation
- **Modern Architecture**: Repository pattern, custom exception handling, and centralized configuration

## Tech Stack

- **Backend**: FastAPI, Python 3.10+
- **Database**: SQLite
- **LLM**: Ollama (llama3.1:8b)
- **Frontend**: Minimal vanilla HTML/JavaScript
- **Package Manager**: uv
- **Testing**: pytest
- **Code Quality**: black, ruff

## Prerequisites

- Python 3.10 or higher
- conda environment (optional)
- Ollama running with the llama3.1:8b model installed
- uv package manager

## Setup

### 1. Activate Conda Environment (Optional)

```bash
conda activate cs146s
```

### 2. Install Ollama and Pull Model

```bash
# Install Ollama (if not already installed)
# Visit https://ollama.com for installation instructions

# Pull the required model
ollama pull llama3.1:8b

# Start Ollama server
ollama serve
```

### 3. Install Dependencies

Dependencies are managed via uv at the repository root:

```bash
cd /path/to/modern-software-dev-assignments
uv sync
```

### 4. Configure Environment (Optional)

Create a `.env` file in the repository root to customize settings:

```env
APP_NAME=Action Item Extractor
DEBUG=False
OLLAMA_MODEL=llama3.1:8b
OLLAMA_HOST=http://localhost:11434
DB_PATH=week2/data/app.db
```

## Running the Application

Start the development server:

```bash
uv run uvicorn week2.app.main:app --reload --host 127.0.0.1 --port 8000
```

The application will be available at `http://127.0.0.1:8000/`

## API Endpoints

### Frontend

#### `GET /`

Serves the web interface.

**Response**: HTML page

### Action Items

#### `POST /action-items/extract`

Extract action items using heuristic-based methods.

**Request Body**:
```json
{
  "text": "Meeting notes with - [ ] task",
  "save_note": true
}
```

**Response**:
```json
{
  "note_id": 1,
  "items": [
    {"id": 1, "text": "task"}
  ]
}
```

#### `POST /action-items/extract-llm`

Extract action items using LLM-powered analysis.

**Request Body**:
```json
{
  "text": "We need to review the PR and fix bugs",
  "save_note": true
}
```

**Response**:
```json
{
  "note_id": 2,
  "items": [
    {"id": 2, "text": "Review the PR"},
    {"id": 3, "text": "Fix bugs"}
  ]
}
```

#### `GET /action-items`

List all action items, optionally filtered by note ID.

**Query Parameters**:
- `note_id` (optional): Filter by note ID

**Response**:
```json
[
  {
    "id": 1,
    "note_id": 1,
    "text": "task",
    "done": false,
    "created_at": "2025-01-05 12:00:00"
  }
]
```

#### `POST /action-items/{action_item_id}/done`

Mark an action item as done or not done.

**Request Body**:
```json
{
  "done": true
}
```

**Response**:
```json
{
  "id": 1,
  "note_id": 1,
  "text": "task",
  "done": true,
  "created_at": "2025-01-05 12:00:00"
}
```

### Notes

#### `POST /notes`

Create a new note.

**Request Body**:
```json
{
  "content": "Meeting notes"
}
```

**Response**:
```json
{
  "id": 1,
  "content": "Meeting notes",
  "created_at": "2025-01-05 12:00:00"
}
```

#### `GET /notes`

List all notes.

**Response**:
```json
[
  {
    "id": 1,
    "content": "Meeting notes",
    "created_at": "2025-01-05 12:00:00"
  }
]
```

#### `GET /notes/{note_id}`

Get a specific note by ID.

**Response**:
```json
{
  "id": 1,
  "content": "Meeting notes",
  "created_at": "2025-01-05 12:00:00"
}
```

## Using the Web Interface

1. Open `http://127.0.0.1:8000/` in your browser
2. Paste your notes or meeting text into the textarea
3. Optionally check "Save as note" to store the original text
4. Click "Extract" for heuristic-based extraction or "Extract LLM" for intelligent extraction
5. Click checkboxes to mark action items as complete
6. Click "List Notes" to view all saved notes

## Running Tests

### Run All Tests

```bash
uv run pytest week2/tests/
```

### Run Tests with Verbose Output

```bash
uv run pytest week2/tests/ -v
```

### Run a Single Test

```bash
uv run pytest week2/tests/test_extract.py::test_extract_bullets_and_checkboxes -v
```

### Run Tests for a Specific File

```bash
uv run pytest week2/tests/test_extract.py
```

## Code Quality

### Format Code

```bash
uv run black .
```

### Fix Linting Issues

```bash
uv run ruff check . --fix
```

### Check for Issues Only

```bash
uv run ruff check .
```

### Check Formatting Without Modifying Files

```bash
uv run black --check .
```

## Project Structure

```
week2/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application setup
│   ├── config.py            # Application configuration
│   ├── exceptions.py        # Custom exception classes
│   ├── db.py               # Database layer and repositories
│   ├── schemas/            # Pydantic schemas for API contracts
│   │   └── __init__.py
│   ├── routers/            # API route handlers
│   │   ├── __init__.py
│   │   ├── action_items.py
│   │   └── notes.py
│   └── services/           # Business logic
│       └── extract.py
├── frontend/
│   └── index.html          # Web interface
├── tests/
│   └── test_extract.py     # Unit tests
├── data/
│   └── app.db             # SQLite database (created on first run)
└── assignment.md          # Project instructions
```

## Development Guidelines

- Follow the code style guidelines in `AGENTS.md`
- Use Pydantic schemas for all API request/response validation
- Use repository pattern for database operations
- Implement proper error handling with custom exceptions
- Run tests and linting before committing changes

## License

This project is part of a course assignment.
