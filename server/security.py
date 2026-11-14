"""Password hashing, session tokens and in-memory throttling. Standard library only."""
from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import threading
import time
from collections import defaultdict, deque

SCRYPT_N, SCRYPT_R, SCRYPT_P = 2 ** 14, 8, 1
MIN_PASSWORD_LENGTH = 8


def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P, dklen=32)
    return f"scrypt${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}${_b64(salt)}${_b64(digest)}"


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, n, r, p, salt, digest = stored.split("$")
        if scheme != "scrypt":
            return False
        actual = hashlib.scrypt(password.encode(), salt=_unb64(salt), n=int(n), r=int(r), p=int(p), dklen=32)
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(actual, _unb64(digest))


# Spends the same scrypt cost for unknown logins, so timing does not reveal which logins exist.
_DUMMY_HASH = hash_password(secrets.token_urlsafe(16))


def burn_password_check(password: str) -> None:
    verify_password(password, _DUMMY_HASH)


def password_problem(password: str) -> str | None:
    if len(password) < MIN_PASSWORD_LENGTH:
        return f"Пароль должен содержать не меньше {MIN_PASSWORD_LENGTH} символов"
    if password.isdigit() or password.isalpha():
        return "Пароль должен содержать и буквы, и цифры или символы"
    return None


def new_token() -> str:
    return secrets.token_urlsafe(32)


def token_hash(token: str) -> str:
    # Only the hash is stored: a leaked database does not expose live sessions.
    return hashlib.sha256(token.encode()).hexdigest()


class LoginThrottle:
    """Locks a login and a client address after repeated failures."""

    def __init__(self, max_failures: int, lock_seconds: int):
        self.max_failures = max_failures
        self.lock_seconds = lock_seconds
        self.failures: dict[str, deque] = defaultdict(deque)
        self.lock = threading.Lock()

    def _keys(self, login: str, ip: str):
        return ("login:" + login.lower(), "ip:" + ip)

    def _prune(self, key: str, moment: float) -> deque:
        queue = self.failures[key]
        while queue and moment - queue[0] > self.lock_seconds:
            queue.popleft()
        return queue

    def retry_after(self, login: str, ip: str) -> int:
        moment = time.monotonic()
        with self.lock:
            waits = []
            for key in self._keys(login, ip):
                queue = self._prune(key, moment)
                # An address may try several logins; give it a wider allowance.
                limit = self.max_failures * (4 if key.startswith("ip:") else 1)
                if len(queue) >= limit:
                    waits.append(int(self.lock_seconds - (moment - queue[0])) + 1)
            return max(waits, default=0)

    def failed(self, login: str, ip: str) -> None:
        moment = time.monotonic()
        with self.lock:
            for key in self._keys(login, ip):
                self._prune(key, moment).append(moment)

    def succeeded(self, login: str) -> None:
        with self.lock:
            self.failures.pop("login:" + login.lower(), None)


class RateLimiter:
    """Sliding one-minute window per key, e.g. model requests per user."""

    def __init__(self, per_minute: int):
        self.per_minute = per_minute
        self.hits: dict[str, deque] = defaultdict(deque)
        self.lock = threading.Lock()

    def allow(self, key: str) -> bool:
        if self.per_minute <= 0:
            return True
        moment = time.monotonic()
        with self.lock:
            queue = self.hits[key]
            while queue and moment - queue[0] > 60:
                queue.popleft()
            if len(queue) >= self.per_minute:
                return False
            queue.append(moment)
            return True
