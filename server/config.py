"""Backend settings from environment variables. Read once per app instance."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, "").strip() or default


def _flag(name: str, default: bool) -> bool:
    return _env(name, "true" if default else "false").lower() in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class Settings:
    state_db: Path
    kb_path: Path
    index_dir: Path
    session_ttl_hours: int
    cookie_name: str
    cookie_secure: bool
    demo_users: bool
    demo_password: str
    bootstrap_users: str
    login_max_failures: int
    login_lock_minutes: int
    ask_per_minute: int
    utc_offset_hours: int
    allow_uploads: bool

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            state_db=Path(_env("STATE_DB", str(BASE / "data/state.sqlite"))),
            kb_path=Path(_env("KB_PATH", str(BASE / "data/raw"))),
            index_dir=Path(_env("INDEX_DIR", str(BASE / "data/index"))),
            session_ttl_hours=int(_env("SESSION_TTL_HOURS", "12")),
            cookie_name=_env("SESSION_COOKIE", "legal_session"),
            cookie_secure=_flag("COOKIE_SECURE", False),
            demo_users=_flag("DEMO_USERS", True),
            demo_password=_env("DEMO_PASSWORD"),
            bootstrap_users=_env("BOOTSTRAP_USERS"),
            login_max_failures=int(_env("LOGIN_MAX_FAILURES", "5")),
            login_lock_minutes=int(_env("LOGIN_LOCK_MINUTES", "15")),
            ask_per_minute=int(_env("ASK_PER_MINUTE", "20")),
            utc_offset_hours=int(_env("APP_UTC_OFFSET_HOURS", "3")),
            allow_uploads=_flag("ALLOW_KB_UPLOADS", True),
        )
