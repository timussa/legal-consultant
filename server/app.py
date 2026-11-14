"""FastAPI application factory."""
from __future__ import annotations

import logging
import secrets
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from server.config import Settings
from server.db import Database
from server.kb import KnowledgeBase
from server.routers import account, admin, auth, dialogs, documents, overview, users
from server.security import LoginThrottle, RateLimiter, password_problem

log = logging.getLogger("server")

DEMO_ACCOUNTS = [
    ("lawyer", "Анна Корнеева", "Юрист, договорная работа", "lawyer"),
    ("lawyer2", "Ольга Шишкина", "Юрист, корпоративное право", "lawyer"),
    ("head", "Елена Смирнова", "Руководитель юридического отдела", "head"),
]

VALIDATION_MESSAGES = {"question": "Проверьте текст вопроса", "eventDate": "Проверьте дату события",
                       "dialogId": "Некорректный идентификатор диалога", "password": "Проверьте пароль",
                       "login": "Проверьте логин"}


def seed_users(db: Database, settings: Settings) -> None:
    with db.connect(write=True) as con:
        if con.execute("SELECT COUNT(*) FROM users").fetchone()[0]:
            return
        accounts = []
        if settings.bootstrap_users:
            for entry in filter(None, (e.strip() for e in settings.bootstrap_users.split(";"))):
                parts = entry.split(":")
                if len(parts) < 4 or parts[2] not in ("lawyer", "head"):
                    raise ValueError("BOOTSTRAP_USERS: ожидается login:password:role:Имя[:Должность]")
                accounts.append((parts[0], parts[3], parts[4] if len(parts) > 4 else "", parts[2], parts[1]))
        elif settings.demo_users:
            password = settings.demo_password or secrets.token_urlsafe(9)
            if not settings.demo_password:
                log.warning("DEMO_PASSWORD не задан. Пароль демо-учётных записей lawyer, lawyer2, head: %s", password)
            accounts = [(login, name, position, role, password) for login, name, position, role in DEMO_ACCOUNTS]
        from server.routers.users import create_user
        for login, name, position, role, password in accounts:
            problem = password_problem(password)
            if problem:
                raise ValueError(f"Пароль для {login}: {problem}")
            create_user(con, login, name, position, role, password)
        if accounts:
            log.info("created %d user account(s)", len(accounts))


def create_app(engine_factory: Callable[[], object] | None = None, settings: Settings | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        config = settings or Settings.from_env()
        if engine_factory is None:
            from legal_core import Engine
            factory = lambda: Engine(config.kb_path, config.index_dir)  # noqa: E731
        else:
            factory = engine_factory
        db = Database(config.state_db)
        db.migrate()
        seed_users(db, config)
        kb = KnowledgeBase(factory)
        kb.load()
        kb.sync(db)
        app.state.settings = config
        app.state.db = db
        app.state.kb = kb
        app.state.throttle = LoginThrottle(config.login_max_failures, config.login_lock_minutes * 60)
        app.state.limiter = RateLimiter(config.ask_per_minute)
        try:
            yield
        finally:
            kb.close()

    app = FastAPI(title="Юрассистент API", version="2.0", lifespan=lifespan,
                  description="Бэкенд юридического ассистента: авторизация, диалоги, документы, уведомления.")

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException):
        message = exc.detail if isinstance(exc.detail, str) else "Ошибка запроса"
        if exc.status_code == 404 and message == "Not Found":
            message = "Ресурс не найден"
        headers = {"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else None
        return JSONResponse(status_code=exc.status_code, headers=headers,
                            content={"error": {"code": exc.status_code, "message": message}})

    @app.exception_handler(RequestValidationError)
    async def invalid_request(request: Request, exc: RequestValidationError):
        fields = [str(e["loc"][-1]) for e in exc.errors() if e.get("loc")]
        message = next((VALIDATION_MESSAGES[f] for f in fields if f in VALIDATION_MESSAGES), "Проверьте формат запроса")
        return JSONResponse(status_code=422, content={"error": {"code": 422, "message": message, "fields": fields}})

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "same-origin")
        if request.url.path.startswith("/api/"):
            response.headers.setdefault("Cache-Control", "no-store")
        return response

    @app.get("/api/health", tags=["health"])
    def health(request: Request):
        engine = request.app.state.kb.engine
        return {"status": "ok", "documents": len(engine.docs), "chunks": len(engine.chunks),
                "denseSearch": engine.vectors is not None}

    for module in (auth, users, dialogs, documents, overview, account, admin):
        app.include_router(module.router)
    return app
