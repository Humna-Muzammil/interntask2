import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path("chat_history.db")

def connect():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(conversation_id) REFERENCES conversations(id)
            )
        """)

def create_conversation(title="New conversation"):
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO conversations(title, created_at) VALUES (?, ?)",
            (title, datetime.now(timezone.utc).isoformat())
        )
        return cur.lastrowid

def list_conversations():
    with connect() as conn:
        return conn.execute(
            "SELECT id, title, created_at FROM conversations ORDER BY id DESC"
        ).fetchall()

def get_messages(conversation_id):
    with connect() as conn:
        return conn.execute(
            "SELECT role, content, created_at FROM messages WHERE conversation_id=? ORDER BY id",
            (conversation_id,)
        ).fetchall()

def add_message(conversation_id, role, content):
    with connect() as conn:
        conn.execute(
            "INSERT INTO messages(conversation_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (conversation_id, role, content, datetime.now(timezone.utc).isoformat())
        )

def rename_conversation(conversation_id, title):
    with connect() as conn:
        conn.execute("UPDATE conversations SET title=? WHERE id=?", (title[:80], conversation_id))
