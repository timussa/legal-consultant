"""Team management for the head of the legal department. No self-registration: accounts are issued."""
from __future__ import annotations

import re
import sqlite3
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from server.db import now
from server.deps import User, audit, client_ip, head_user, state
from server.labels import initials
from server.security import hash_password, password_problem

router = APIRouter(prefix="/api/v1/users", tags=["users"])

LOGIN = re.compile(r"^[a-z0-9._-]{3,50}$", re.IGNORECASE)


class NewUser(BaseModel):
    login: str = Field(min_length=3, max_length=50)
    name: str = Field(min_length=2, max_length=120)
    position: str = Field(default="", max_length=120)
    role: Literal["lawyer", "head"] = "lawyer"
    password: str = Field(min_length=1, max_length=200)


class UserPatch(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    position: str | None = Field(default=None, max_length=120)
    role: Literal["lawyer", "head"] | None = None
    isActive: bool | None = None
    password: str | None = Field(default=None, min_length=1, max_length=200)


def record(row) -> dict:
    return {"id": row["id"], "login": row["login"], "name": row["name"], "initials": initials(row["name"]),
            "position": row["position"], "role": row["role"], "isActive": bool(row["is_active"]),
            "createdAt": row["created_at"], "lastLoginAt": row["last_login_at"]}


def create_user(con, login: str, name: str, position: str, role: str, password: str) -> int:
    cursor = con.execute(
        "INSERT INTO users (login, name, position, role, password_hash, created_at) VALUES (?,?,?,?,?,?)",
        (login, name, position, role, hash_password(password), now()))
    return cursor.lastrowid


@router.get("")
def list_users(user: User = Depends(head_user), app=Depends(state)):
    with app.db.connect() as con:
        return [record(r) for r in con.execute("SELECT * FROM users ORDER BY name")]


@router.post("", status_code=201)
def add_user(body: NewUser, request: Request, user: User = Depends(head_user), app=Depends(state)):
    if not LOGIN.match(body.login):
        raise HTTPException(422, "Логин: 3–50 символов, латиница, цифры, точка, дефис или подчёркивание")
    problem = password_problem(body.password)
    if problem:
        raise HTTPException(422, problem)
    try:
        with app.db.connect(write=True) as con:
            new_id = create_user(con, body.login, body.name.strip(), body.position.strip(), body.role, body.password)
            audit(con, user.id, "user_created", str(new_id), {"login": body.login, "role": body.role}, client_ip(request))
            return record(con.execute("SELECT * FROM users WHERE id=?", (new_id,)).fetchone())
    except sqlite3.IntegrityError as exc:
        raise HTTPException(409, "Пользователь с таким логином уже есть") from exc


@router.patch("/{user_id}")
def update_user(user_id: int, body: UserPatch, request: Request, user: User = Depends(head_user), app=Depends(state)):
    if user_id == user.id and (body.role == "lawyer" or body.isActive is False):
        raise HTTPException(422, "Нельзя снять с себя роль руководителя или заблокировать свою учётную запись")
    if body.password is not None:
        problem = password_problem(body.password)
        if problem:
            raise HTTPException(422, problem)
    with app.db.connect(write=True) as con:
        row = con.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        if row is None:
            raise HTTPException(404, "Пользователь не найден")
        changes = {}
        for field, column in (("name", "name"), ("position", "position"), ("role", "role")):
            value = getattr(body, field)
            if value is not None:
                changes[column] = value.strip() if isinstance(value, str) else value
        if body.isActive is not None:
            changes["is_active"] = int(body.isActive)
        if body.password is not None:
            changes["password_hash"] = hash_password(body.password)
        if changes:
            con.execute(f"UPDATE users SET {', '.join(c + '=?' for c in changes)} WHERE id=?", (*changes.values(), user_id))
        if body.password is not None or body.isActive is False or body.role is not None:
            con.execute("DELETE FROM sessions WHERE user_id=?", (user_id,))
        audit(con, user.id, "user_updated", str(user_id),
              {k: v for k, v in changes.items() if k != "password_hash"} | ({"password": "reset"} if body.password else {}),
              client_ip(request))
        return record(con.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone())
