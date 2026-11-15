"""SQLite storage: connection helper and versioned schema migrations."""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = [
    # 1: users, sessions, dialogs with owners, messages, sources, comments, notifications, audit.
    """
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        login TEXT NOT NULL UNIQUE COLLATE NOCASE,
        name TEXT NOT NULL,
        position TEXT NOT NULL DEFAULT '',
        role TEXT NOT NULL CHECK (role IN ('lawyer', 'head')),
        password_hash TEXT NOT NULL,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        last_login_at TEXT
    );
    CREATE TABLE sessions (
        token_hash TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        created_at TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        last_seen_at TEXT NOT NULL,
        user_agent TEXT NOT NULL DEFAULT '',
        ip TEXT NOT NULL DEFAULT ''
    );
    CREATE INDEX sessions_user ON sessions(user_id);
    CREATE TABLE dialogs (
        id TEXT PRIMARY KEY,
        owner_id INTEGER NOT NULL REFERENCES users(id),
        number INTEGER NOT NULL UNIQUE,
        title TEXT NOT NULL,
        question TEXT NOT NULL,
        document_id TEXT,
        event_date TEXT,
        status TEXT NOT NULL,
        answer TEXT NOT NULL,
        duration_ms INTEGER NOT NULL DEFAULT 0,
        feedback TEXT,
        feedback_at TEXT,
        review TEXT,
        reviewed_by INTEGER REFERENCES users(id),
        reviewed_at TEXT,
        outdated_reason TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        deleted_at TEXT
    );
    CREATE INDEX dialogs_owner ON dialogs(owner_id, updated_at);
    CREATE TABLE messages (
        id INTEGER PRIMARY KEY,
        dialog_id TEXT NOT NULL REFERENCES dialogs(id) ON DELETE CASCADE,
        role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
        text TEXT NOT NULL,
        answer TEXT,
        event_date TEXT,
        duration_ms INTEGER,
        created_at TEXT NOT NULL
    );
    CREATE INDEX messages_dialog ON messages(dialog_id, id);
    CREATE TABLE answer_sources (
        dialog_id TEXT NOT NULL REFERENCES dialogs(id) ON DELETE CASCADE,
        cite INTEGER NOT NULL,
        doc_id TEXT NOT NULL,
        document_id TEXT NOT NULL,
        edition_id TEXT NOT NULL,
        clause_id TEXT NOT NULL,
        PRIMARY KEY (dialog_id, cite)
    );
    CREATE INDEX answer_sources_doc ON answer_sources(document_id, clause_id);
    CREATE TABLE comments (
        id INTEGER PRIMARY KEY,
        document_id TEXT NOT NULL,
        clause_id TEXT NOT NULL,
        user_id INTEGER NOT NULL REFERENCES users(id),
        text TEXT NOT NULL,
        created_at TEXT NOT NULL,
        deleted_at TEXT
    );
    CREATE INDEX comments_doc ON comments(document_id);
    CREATE TABLE notifications (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        kind TEXT NOT NULL CHECK (kind IN ('update', 'outdated', 'disputed', 'review')),
        title TEXT NOT NULL,
        text TEXT NOT NULL,
        target TEXT,
        is_head_only INTEGER NOT NULL DEFAULT 0,
        dedupe_key TEXT,
        created_at TEXT NOT NULL,
        read_at TEXT,
        UNIQUE (user_id, dedupe_key)
    );
    CREATE INDEX notifications_user ON notifications(user_id, id);
    CREATE TABLE kb_documents (
        doc_id TEXT PRIMARY KEY,
        document_id TEXT NOT NULL,
        title TEXT NOT NULL,
        content_hash TEXT NOT NULL,
        first_seen_at TEXT NOT NULL,
        changed_at TEXT,
        removed_at TEXT
    );
    CREATE TABLE user_settings (
        user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
        data TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    CREATE TABLE audit_log (
        id INTEGER PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        action TEXT NOT NULL,
        object_id TEXT,
        details TEXT,
        ip TEXT NOT NULL DEFAULT '',
        created_at TEXT NOT NULL
    );
    CREATE INDEX audit_created ON audit_log(created_at);
    """,
]


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def dumps(value) -> str:
    return json.dumps(value, ensure_ascii=False)


class Database:
    def __init__(self, location: Path):
        self.location = Path(location)
        self.location.parent.mkdir(parents=True, exist_ok=True)

    def _open(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.location, timeout=10, isolation_level=None)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON")
        con.execute("PRAGMA busy_timeout = 10000")
        return con

    @contextmanager
    def connect(self, write: bool = False):
        """One connection per unit of work. write=True takes the write lock up front,
        so read-modify-write sequences (dialog numbers, history) cannot interleave."""
        con = self._open()
        try:
            con.execute("BEGIN IMMEDIATE" if write else "BEGIN")
            try:
                yield con
            except BaseException:
                con.execute("ROLLBACK")
                raise
            con.execute("COMMIT")
        finally:
            con.close()

    def migrate(self) -> None:
        con = self._open()
        try:
            con.execute("PRAGMA journal_mode = WAL")
            version = con.execute("PRAGMA user_version").fetchone()[0]
            if version == 0:
                self._move_legacy(con)
            for index in range(version, len(SCHEMA)):
                con.execute("BEGIN IMMEDIATE")
                for statement in [s for s in SCHEMA[index].split(";") if s.strip()]:
                    con.execute(statement)
                con.execute(f"PRAGMA user_version = {index + 1}")
                con.execute("COMMIT")
        finally:
            con.close()

    @staticmethod
    def _move_legacy(con: sqlite3.Connection) -> None:
        # The first prototype kept unowned dialogs in a different table layout.
        columns = [r[1] for r in con.execute("PRAGMA table_info(dialogs)")]
        if columns and "owner_id" not in columns:
            con.execute("ALTER TABLE dialogs RENAME TO dialogs_legacy")
