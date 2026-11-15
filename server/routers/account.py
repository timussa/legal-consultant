"""Per-user notifications and interface settings."""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field

from server.db import dumps, now
from server.deps import User, current_user, state
from server.labels import date_label

router = APIRouter(prefix="/api/v1", tags=["account"])

DEFAULT_SETTINGS = {"defaultRole": "lawyer", "notifyUpdates": True, "notifyOutdated": True, "notifyDisputed": True,
                    "isStreaming": True, "isPipelineExpanded": False, "isMotionReduced": False}


class ReadRequest(BaseModel):
    ids: list[str] = Field(default_factory=list, max_length=500)
    all: bool = False


@router.get("/notifications")
def notifications(user: User = Depends(current_user), app=Depends(state)):
    offset = app.settings.utc_offset_hours
    with app.db.connect() as con:
        rows = con.execute("SELECT * FROM notifications WHERE user_id=? ORDER BY id DESC LIMIT 50", (user.id,)).fetchall()
    return [{"id": str(r["id"]), "kind": r["kind"], "title": r["title"], "text": r["text"],
             "dateLabel": date_label(r["created_at"], offset), "isHeadOnly": bool(r["is_head_only"]),
             "target": json.loads(r["target"]) if r["target"] else None, "isRead": r["read_at"] is not None,
             "createdAt": r["created_at"]} for r in rows]


@router.post("/notifications/read", status_code=204)
def notifications_read(body: ReadRequest, user: User = Depends(current_user), app=Depends(state)):
    with app.db.connect(write=True) as con:
        if body.all:
            con.execute("UPDATE notifications SET read_at=? WHERE user_id=? AND read_at IS NULL", (now(), user.id))
        else:
            ids = [int(i) for i in body.ids if i.isdigit()]
            con.executemany("UPDATE notifications SET read_at=? WHERE id=? AND user_id=? AND read_at IS NULL",
                            [(now(), i, user.id) for i in ids])
    return Response(status_code=204)


def stored_settings(con, user: User) -> dict:
    row = con.execute("SELECT data FROM user_settings WHERE user_id=?", (user.id,)).fetchone()
    result = dict(DEFAULT_SETTINGS, defaultRole=user.role)
    if row:
        result.update({k: v for k, v in json.loads(row["data"]).items() if k in DEFAULT_SETTINGS})
    if not user.is_head:
        result["defaultRole"] = "lawyer"
    return result


@router.get("/settings")
def get_settings(user: User = Depends(current_user), app=Depends(state)):
    with app.db.connect() as con:
        return stored_settings(con, user)


@router.put("/settings")
def put_settings(body: dict, user: User = Depends(current_user), app=Depends(state)):
    unknown = set(body) - set(DEFAULT_SETTINGS)
    if unknown:
        raise HTTPException(422, "Неизвестные настройки: " + ", ".join(sorted(unknown)))
    for key, value in body.items():
        expected = type(DEFAULT_SETTINGS[key])
        if not isinstance(value, expected):
            raise HTTPException(422, f"Некорректное значение настройки {key}")
    if body.get("defaultRole") not in (None, "lawyer", "head") or (body.get("defaultRole") == "head" and not user.is_head):
        raise HTTPException(422, "Роль по умолчанию недоступна")
    with app.db.connect(write=True) as con:
        merged = stored_settings(con, user) | body
        con.execute("INSERT INTO user_settings VALUES (?,?,?) ON CONFLICT(user_id) DO UPDATE SET data=excluded.data,"
                    " updated_at=excluded.updated_at", (user.id, dumps(merged), now()))
    return merged
