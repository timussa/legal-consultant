"""Login, logout, current user and password change."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field

from server.db import now
from server.deps import User, audit, client_ip, current_user, state
from server.security import (burn_password_check, hash_password, new_token, password_problem,
                             token_hash, verify_password)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class Login(BaseModel):
    login: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=200)


class PasswordChange(BaseModel):
    currentPassword: str = Field(min_length=1, max_length=200)
    newPassword: str = Field(min_length=1, max_length=200)


def user_payload(row) -> dict:
    return User(row["id"], row["login"], row["name"], row["position"], row["role"], "").public()


@router.post("/login")
def login(body: Login, request: Request, response: Response, app=Depends(state)):
    ip = client_ip(request)
    wait = app.throttle.retry_after(body.login, ip)
    if wait:
        raise HTTPException(429, f"Слишком много неудачных попыток. Повторите через {max(1, wait // 60)} мин.")
    with app.db.connect() as con:
        row = con.execute("SELECT * FROM users WHERE login = ?", (body.login.strip(),)).fetchone()
    if row is None:
        burn_password_check(body.password)
    if row is None or not verify_password(body.password, row["password_hash"]) or not row["is_active"]:
        app.throttle.failed(body.login, ip)
        with app.db.connect(write=True) as con:
            audit(con, row["id"] if row else None, "login_failed", body.login.strip()[:100], ip=ip)
        # One message for every case, so the response does not reveal which logins exist.
        raise HTTPException(401, "Неверный логин или пароль")
    app.throttle.succeeded(body.login)
    token = new_token()
    ttl = timedelta(hours=app.settings.session_ttl_hours)
    expires = (datetime.now(timezone.utc) + ttl).replace(microsecond=0)
    with app.db.connect(write=True) as con:
        con.execute("DELETE FROM sessions WHERE expires_at <= ?", (now(),))
        con.execute("INSERT INTO sessions VALUES (?,?,?,?,?,?,?)",
                    (token_hash(token), row["id"], now(), expires.isoformat(), now(),
                     request.headers.get("user-agent", "")[:300], ip))
        con.execute("UPDATE users SET last_login_at=? WHERE id=?", (now(), row["id"]))
        audit(con, row["id"], "login", ip=ip)
    response.set_cookie(app.settings.cookie_name, token, max_age=int(ttl.total_seconds()), httponly=True,
                        secure=app.settings.cookie_secure, samesite="strict", path="/api")
    return {"token": token, "expiresAt": expires.isoformat(), "user": user_payload(row)}


@router.post("/logout", status_code=204)
def logout(request: Request, user: User = Depends(current_user), app=Depends(state)):
    with app.db.connect(write=True) as con:
        con.execute("DELETE FROM sessions WHERE token_hash=?", (user.token_hash,))
        audit(con, user.id, "logout", ip=client_ip(request))
    response = Response(status_code=204)
    response.delete_cookie(app.settings.cookie_name, path="/api")
    return response


@router.get("/me")
def me(user: User = Depends(current_user)):
    return user.public()


@router.post("/password", status_code=204)
def change_password(body: PasswordChange, request: Request, user: User = Depends(current_user), app=Depends(state)):
    with app.db.connect() as con:
        stored = con.execute("SELECT password_hash FROM users WHERE id=?", (user.id,)).fetchone()[0]
    if not verify_password(body.currentPassword, stored):
        raise HTTPException(422, "Текущий пароль указан неверно")
    problem = password_problem(body.newPassword)
    if problem:
        raise HTTPException(422, problem)
    with app.db.connect(write=True) as con:
        con.execute("UPDATE users SET password_hash=? WHERE id=?", (hash_password(body.newPassword), user.id))
        # Other devices must sign in again with the new password.
        con.execute("DELETE FROM sessions WHERE user_id=? AND token_hash<>?", (user.id, user.token_hash))
        audit(con, user.id, "password_changed", ip=client_ip(request))
    return Response(status_code=204)
