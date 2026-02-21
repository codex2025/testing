"""
Database operations module

This module provides a lightweight SQLite integration for storing support
requests. It currently exposes helpers to obtain a connection and to
initialize the database schema.

TODO:
- Add CRUD helpers for requests
- Add connection pooling or switch to a proper DB for production
"""

import os
import sqlite3
import datetime

DB_FILENAME = 'database.db'
DB_PATH = os.path.join(os.path.dirname(__file__), DB_FILENAME)


def get_db_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Return a sqlite3.Connection with Row factory for dict-like access.

    Args:
        db_path: path to the SQLite database file.

    Raises:
        sqlite3.Error on connection problems.
    """
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Error opening database '{db_path}': {e}")
        raise


def init_db(db_path: str = DB_PATH) -> None:
    """Initialize the database and create the `requests` table if needed.

    The table schema includes fields required for tracking and simple
    AI analysis placeholders.
    """
    print(f"Initializing database at: {db_path}")
    conn = None
    try:
        conn = get_db_connection(db_path)
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT DEFAULT 'Uncategorized',
                summary TEXT DEFAULT 'AI Analyzing...',
                suggested_response TEXT DEFAULT 'Pending AI analysis',
                agent_resolved BOOLEAN DEFAULT 0,
                timestamp TEXT NOT NULL,
                status TEXT DEFAULT 'New'
            )
            """
        )
        conn.commit()
        print("Database initialized: 'requests' table ready.")
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
        raise
    finally:
        if conn:
            conn.close()


def insert_request(subject: str, description: str, *, category: str = None,
                   summary: str = None, suggested_response: str = None,
                   agent_resolved: bool = False, status: str = 'New',
                   db_path: str = DB_PATH) -> int:
    """Insert a support request and return the new row id.

    This is a convenience helper used by the application when storing
    incoming requests.
    """
    conn = get_db_connection(db_path)
    try:
        timestamp = datetime.datetime.utcnow().isoformat()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO requests (subject, description, category, summary, suggested_response, agent_resolved, timestamp, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                subject,
                description,
                category or 'Uncategorized',
                summary or 'AI Analyzing...',
                suggested_response or 'Pending AI analysis',
                int(bool(agent_resolved)),
                timestamp,
                status,
            ),
        )
        conn.commit()
        rowid = cur.lastrowid
        print(f"Inserted request id={rowid}")
        return rowid
    except sqlite3.Error as e:
        print(f"Error inserting request: {e}")
        raise
    finally:
        conn.close()


def insert_initial_request(subject: str, description: str, *, db_path: str = DB_PATH):
    """Validate, sanitize and insert a new support request.

    Returns (True, request_id) on success or (False, error_message) on failure.
    """
    # Basic validation
    if not isinstance(subject, str) or not isinstance(description, str):
        return False, 'Subject and description must be strings.'

    subject_clean = subject.strip()
    description_clean = description.strip()

    if not subject_clean:
        return False, 'Subject is required.'
    if not description_clean:
        return False, 'Description is required.'
    if len(subject_clean) < 5 or len(subject_clean) > 100:
        return False, 'Subject must be between 5 and 100 characters.'
    if len(description_clean) < 20 or len(description_clean) > 1000:
        return False, 'Description must be between 20 and 1000 characters.'

    # Perform insertion with parameterized query
    try:
        conn = get_db_connection(db_path)
        cur = conn.cursor()
        timestamp = datetime.datetime.now().isoformat()
        cur.execute(
            """
            INSERT INTO requests (subject, description, category, summary, suggested_response, agent_resolved, timestamp, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                subject_clean,
                description_clean,
                'Uncategorized',
                'AI Analyzing...',
                'Pending AI analysis',
                0,
                timestamp,
                'New',
            ),
        )
        conn.commit()
        request_id = cur.lastrowid
        print(f"insert_initial_request: inserted id={request_id}")
        return True, request_id
    except sqlite3.Error as e:
        print(f"insert_initial_request error: {e}")
        return False, f"Database error: {e}"
    finally:
        try:
            conn.close()
        except Exception:
            pass


def update_request_with_ai_results(request_id: int, summary: str = None, suggested_response: str = None,
                                   agent_resolved: bool = False, status: str = 'Analyzed',
                                   db_path: str = DB_PATH):
    """Update a request record with AI analysis results.

    Returns (True, rows_updated) on success or (False, error_message) on failure.
    """
    if not isinstance(request_id, int) or request_id <= 0:
        return False, 'Invalid request_id.'

    try:
        conn = get_db_connection(db_path)
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE requests
            SET summary = COALESCE(?, summary),
                suggested_response = COALESCE(?, suggested_response),
                agent_resolved = ?,
                status = ?
            WHERE id = ?
            """,
            (summary, suggested_response, int(bool(agent_resolved)), status, request_id),
        )
        conn.commit()
        rows = cur.rowcount
        print(f"update_request_with_ai_results: request_id={request_id}, rows_updated={rows}")
        if rows == 0:
            return False, 'No matching request found.'
        return True, rows
    except sqlite3.Error as e:
        print(f"update_request_with_ai_results error: {e}")
        return False, f"Database error: {e}"
    finally:
        try:
            conn.close()
        except Exception:
            pass

