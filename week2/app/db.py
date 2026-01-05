from __future__ import annotations

import sqlite3
from contextlib import contextmanager

from .config import get_db_path
from .exceptions import DatabaseError, NotFoundError


@contextmanager
def get_connection():
    """Context manager for database connections."""
    ensure_data_directory_exists()
    connection = None
    try:
        connection = sqlite3.connect(str(get_db_path()))
        connection.row_factory = sqlite3.Row
        yield connection
        connection.commit()
    except sqlite3.Error as e:
        raise DatabaseError(f"Database error: {e}") from e
    finally:
        if connection is not None:
            connection.close()


def ensure_data_directory_exists() -> None:
    """Ensure the data directory exists."""
    get_db_path().parent.mkdir(parents=True, exist_ok=True)


def init_db() -> None:
    """Initialize the database schema."""
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now'))
                );
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS action_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    note_id INTEGER,
                    text TEXT NOT NULL,
                    done INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (note_id) REFERENCES notes(id)
                );
                """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_action_items_note_id 
                ON action_items(note_id)
                """
            )
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to initialize database: {e}") from e


class NoteRepository:
    """Repository for note-related database operations."""

    @staticmethod
    def create(content: str) -> int:
        """Create a new note."""
        try:
            with get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO notes (content) VALUES (?)", (content,))
                return int(cursor.lastrowid)  # type: ignore[arg-type]
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to create note: {e}") from e

    @staticmethod
    def get_by_id(note_id: int) -> sqlite3.Row:
        """Get a note by ID."""
        try:
            with get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "SELECT id, content, created_at FROM notes WHERE id = ?",
                    (note_id,),
                )
                row = cursor.fetchone()
                if row is None:
                    raise NotFoundError(f"Note with id {note_id} not found")
                return row
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to get note: {e}") from e

    @staticmethod
    def list_all() -> list[sqlite3.Row]:
        """List all notes ordered by ID descending."""
        try:
            with get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT id, content, created_at FROM notes ORDER BY id DESC")
                return list(cursor.fetchall())
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to list notes: {e}") from e


class ActionItemRepository:
    """Repository for action item-related database operations."""

    @staticmethod
    def create_many(items: list[str], note_id: int | None = None) -> list[int]:
        """Create multiple action items."""
        if not items:
            return []
        try:
            with get_connection() as connection:
                cursor = connection.cursor()
                ids: list[int] = []
                for item in items:
                    note_id_value: int | None = note_id
                    cursor.execute(
                        "INSERT INTO action_items (note_id, text) VALUES (?, ?)",
                        (note_id_value, item),
                    )
                    ids.append(int(cursor.lastrowid))  # type: ignore[arg-type]
                return ids
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to create action items: {e}") from e

    @staticmethod
    def list_all(note_id: int | None = None) -> list[sqlite3.Row]:
        """List action items, optionally filtered by note ID."""
        try:
            with get_connection() as connection:
                cursor = connection.cursor()
                if note_id is None:
                    cursor.execute(
                        "SELECT id, note_id, text, done, created_at FROM action_items ORDER BY id DESC"
                    )
                else:
                    cursor.execute(
                        "SELECT id, note_id, text, done, created_at FROM action_items WHERE note_id = ? ORDER BY id DESC",
                        (note_id,),
                    )
                return list(cursor.fetchall())
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to list action items: {e}") from e

    @staticmethod
    def update_done_status(action_item_id: int, done: bool) -> sqlite3.Row:
        """Update the done status of an action item."""
        try:
            with get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "UPDATE action_items SET done = ? WHERE id = ?",
                    (1 if done else 0, action_item_id),
                )
                cursor.execute(
                    "SELECT id, note_id, text, done, created_at FROM action_items WHERE id = ?",
                    (action_item_id,),
                )
                row = cursor.fetchone()
                if row is None:
                    raise NotFoundError(f"Action item with id {action_item_id} not found")
                return row
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to update action item: {e}") from e


def insert_note(content: str) -> int:
    """Insert a note into the database (legacy function for backwards compatibility)."""
    return NoteRepository.create(content)


def list_notes() -> list[sqlite3.Row]:
    """List all notes (legacy function for backwards compatibility)."""
    return NoteRepository.list_all()


def get_note(note_id: int) -> sqlite3.Row | None:
    """Get a note by ID (legacy function for backwards compatibility)."""
    try:
        return NoteRepository.get_by_id(note_id)
    except NotFoundError:
        return None


def insert_action_items(items: list[str], note_id: int | None = None) -> list[int]:
    """Insert action items into the database (legacy function for backwards compatibility)."""
    return ActionItemRepository.create_many(items, note_id=note_id)


def list_action_items(note_id: int | None = None) -> list[sqlite3.Row]:
    """List action items (legacy function for backwards compatibility)."""
    return ActionItemRepository.list_all(note_id=note_id)


def mark_action_item_done(action_item_id: int, done: bool) -> None:
    """Mark an action item as done/not done (legacy function for backwards compatibility)."""
    ActionItemRepository.update_done_status(action_item_id, done)
