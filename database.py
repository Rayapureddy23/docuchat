"""
STEP 4 — SQLite database for persistent chat history

Replaces the in-memory chat_history = [] list from your notebook.
Every conversation and every message is saved to a local database file,
so nothing is lost when the app restarts.

Tables:
  conversations  — one row per chat session (id, title, created_at)
  messages       — one row per message    (id, conversation_id, role, content, created_at)
"""

import sqlite3
import datetime
import os

DB_PATH = os.path.join("data", "chat.db")
os.makedirs("data", exist_ok=True)


# ---------------------------------------------------------------------------
# Database setup — create tables if they don't exist
# ---------------------------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            title      TEXT    NOT NULL DEFAULT 'New chat',
            created_at TEXT    NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role            TEXT    NOT NULL,   -- 'user' or 'assistant'
            content         TEXT    NOT NULL,
            created_at      TEXT    NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Conversations
# ---------------------------------------------------------------------------
def create_conversation(title: str = "New chat") -> int:
    """Create a new conversation and return its ID."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.datetime.utcnow().isoformat()
    c.execute("INSERT INTO conversations (title, created_at) VALUES (?, ?)", (title, now))
    conn.commit()
    new_id = c.lastrowid
    conn.close()
    assert new_id is not None
    return new_id


def list_conversations() -> list:
    """Return all conversations newest-first."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, title, created_at FROM conversations ORDER BY created_at DESC")
    rows = [{"id": r[0], "title": r[1], "created_at": r[2]} for r in c.fetchall()]
    conn.close()
    return rows


def rename_conversation(conversation_id: int, new_title: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE conversations SET title = ? WHERE id = ?", (new_title, conversation_id))
    conn.commit()
    conn.close()


def delete_conversation(conversation_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM messages     WHERE conversation_id = ?", (conversation_id,))
    c.execute("DELETE FROM conversations WHERE id = ?",              (conversation_id,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------
def save_message(conversation_id: int, role: str, content: str):
    """Append one message to a conversation."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.datetime.utcnow().isoformat()
    c.execute(
        "INSERT INTO messages (conversation_id, role, content, created_at) VALUES (?, ?, ?, ?)",
        (conversation_id, role, content, now),
    )
    conn.commit()
    conn.close()


def load_messages(conversation_id: int) -> list:
    """
    Return all messages for a conversation as a list of dicts,
    ready to pass directly to the Claude API.
    Format: [{"role": "user"|"assistant", "content": "..."}]
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY created_at ASC",
        (conversation_id,),
    )
    rows = [{"role": r[0], "content": r[1]} for r in c.fetchall()]
    conn.close()
    return rows


def get_message_count(conversation_id: int) -> int:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM messages WHERE conversation_id = ?", (conversation_id,))
    count = c.fetchone()[0]
    conn.close()
    return count


# ---------------------------------------------------------------------------
# Auto-title — rename a conversation after the first question
# ---------------------------------------------------------------------------
def auto_title(conversation_id: int, first_question: str):
    """Set the conversation title to a truncated version of the first question."""
    title = first_question.strip()[:60]
    if len(first_question) > 60:
        title += "..."
    rename_conversation(conversation_id, title)