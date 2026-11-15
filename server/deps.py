"""Request dependencies: application state, current user, role checks, audit."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request

from server.db import dumps, now
from server.labels import initials


@dataclass(frozen=True)
class User:
    id: int
    login: str
    name: str
    position: str
    role: str
    token_hash: str

    @property
    def is_head(self) -> bool:
        return self.role == "head"

    def public(self) -> dict:
        return {"id": self.id, "login": self.login, "name": self.name, "initials": initials(self.name),
                "position": self.position, "role": self.role}


def state(request: Request):
    return request.app.state


def client_ip(request: Request) -> str:
    return request.client.host if request.client else ""


def read_token(request: Request) -> str | None:
    header = request.headers.get("authorization", "")
    if header.lower().startswith("bearer "):
        return header[7:].strip() or None
    return request.cookies.get(request.app.state.settings.cookie_name) or None


def current_user(request: Request) -> User:
    from server.security import token_hash

    token = read_token(request)
    if not token:
        raise HTTPException(401, "Войдите в систему")
    hashed = token_hash(token)
    app = request.app.state
    with app.db.connect() as con:
        row = con.execute(
            "SELECT u.*, s.expires_at, s.last_seen_at FROM sessions s JOIN users u ON u.id = s.user_id"
            " WHERE s.token_hash = ?", (hashed,)).fetchone()
    if row is None or not row["is_active"] or row["expires_at"] <= now():
        raise HTTPException(401, "Сессия истекла. Войдите снова")
    # Sliding expiry, written at most once a minute per session.
    seen = datetime.fromisoformat(row["last_seen_at"])
    if datetime.now(timezone.utc) - seen > timedelta(minutes=1):
        expires = (datetime.now(timezone.utc) + timedelta(hours=app.settings.session_ttl_hours)).replace(microsecond=0)
        with app.db.connect(write=True) as con:
            con.execute("UPDATE sessions SET last_seen_at=?, expires_at=? WHERE token_hash=?",
                        (now(), expires.isoformat(), hashed))
    return User(row["id"], row["login"], row["name"], row["position"], row["role"], hashed)


def head_user(user: User = Depends(current_user)) -> User:
    if not user.is_head:
        raise HTTPException(403, "Действие доступно только руководителю")
    return user


def audit(con, user_id: int | None, action: str, object_id: str | None = None,
          details: dict | None = None, ip: str = "") -> None:
    con.execute("INSERT INTO audit_log (user_id, action, object_id, details, ip, created_at) VALUES (?,?,?,?,?,?)",
                (user_id, action, object_id, dumps(details) if details else None, ip, now()))
