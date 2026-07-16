from __future__ import annotations

import hashlib
import secrets
import time
from collections import defaultdict

from fastapi import Request

from app.config import Settings


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def credentials_match(username: str, password: str, settings: Settings) -> bool:
    user_matches = secrets.compare_digest(_digest(username), _digest(settings.admin_username))
    password_matches = secrets.compare_digest(_digest(password), _digest(settings.admin_password))
    return user_matches and password_matches


def is_admin(request: Request) -> bool:
    return request.session.get("admin_authenticated") is True


def authenticate_session(request: Request) -> None:
    request.session.clear()
    request.session["admin_authenticated"] = True
    request.session["csrf_token"] = secrets.token_urlsafe(32)


def clear_session(request: Request) -> None:
    request.session.clear()


def csrf_token(request: Request) -> str:
    token = request.session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        request.session["csrf_token"] = token
    return token


def csrf_is_valid(request: Request, submitted_token: str) -> bool:
    stored_token = request.session.get("csrf_token", "")
    return bool(stored_token) and secrets.compare_digest(stored_token, submitted_token)


class LoginThrottle:
    def __init__(self, maximum_attempts: int = 5, window_seconds: int = 900) -> None:
        self.maximum_attempts = maximum_attempts
        self.window_seconds = window_seconds
        self._attempts: dict[str, list[float]] = defaultdict(list)

    def _active_attempts(self, key: str) -> list[float]:
        cutoff = time.monotonic() - self.window_seconds
        active = [attempt for attempt in self._attempts[key] if attempt >= cutoff]
        self._attempts[key] = active
        return active

    def is_allowed(self, key: str) -> bool:
        return len(self._active_attempts(key)) < self.maximum_attempts

    def record_failure(self, key: str) -> None:
        self._active_attempts(key).append(time.monotonic())

    def clear(self, key: str) -> None:
        self._attempts.pop(key, None)
