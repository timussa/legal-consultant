"""Notifications are stored per recipient so read state is personal."""
from __future__ import annotations

import sqlite3

from server.db import dumps, now

KINDS = ("update", "outdated", "disputed")


def notify(con: sqlite3.Connection, user_ids, kind: str, title: str, text: str,
           target: dict | None = None, head_only: bool = False, dedupe_key: str | None = None) -> None:
    assert kind in KINDS
    created = now()
    for user_id in set(user_ids):
        con.execute(
            "INSERT OR IGNORE INTO notifications (user_id, kind, title, text, target, is_head_only, dedupe_key, created_at)"
            " VALUES (?,?,?,?,?,?,?,?)",
            (user_id, kind, title, text, dumps(target) if target else None, int(head_only), dedupe_key, created))


def active_users(con: sqlite3.Connection, role: str | None = None) -> list[int]:
    if role:
        rows = con.execute("SELECT id FROM users WHERE is_active=1 AND role=?", (role,))
    else:
        rows = con.execute("SELECT id FROM users WHERE is_active=1")
    return [r[0] for r in rows]


def dialog_target(dialog_id: str) -> dict:
    return {"name": "dialogs", "params": {"dialogId": dialog_id}}


def document_target(document_id: str, edition_id: str | None = None) -> dict:
    target = {"name": "document", "params": {"documentId": document_id}}
    if edition_id and edition_id != "original":
        target["query"] = {"edition": edition_id}
    return target
