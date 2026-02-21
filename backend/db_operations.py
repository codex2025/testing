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

