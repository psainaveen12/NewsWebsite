import hashlib
import hmac
import secrets
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status

from app.config import Settings


_attempts: dict[str, deque[float]] = defaultdict(deque)
LOGIN_WINDOW_SECONDS = 15 * 60
LOGIN_ATTEMPTS = 8


def client_ip(request: Request) -> str:
    return request.headers.get("x-real-ip") or (request.client.host if request.client else "unknown")


def verify_credentials(username: str, password: str, settings: Settings) -> bool:
    username_ok = hmac.compare_digest(
        hashlib.sha256(username.encode()).digest(),
        hashlib.sha256(settings.admin_username.encode()).digest(),
    )
    password_ok = hmac.compare_digest(
        hashlib.sha256(password.encode()).digest(),
        hashlib.sha256(settings.admin_password.encode()).digest(),
    )
    return username_ok and password_ok


def enforce_login_rate_limit(request: Request) -> None:
    now = time.monotonic()
    attempts = _attempts[client_ip(request)]
    while attempts and now - attempts[0] > LOGIN_WINDOW_SECONDS:
        attempts.popleft()
    if len(attempts) >= LOGIN_ATTEMPTS:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Try again later")
    attempts.append(now)


def clear_login_attempts(request: Request) -> None:
    _attempts.pop(client_ip(request), None)


def csrf_token(request: Request) -> str:
    token = request.session.get("csrf")
    if not token:
        token = secrets.token_urlsafe(32)
        request.session["csrf"] = token
    return token


def verify_csrf(request: Request, submitted: str) -> None:
    expected = request.session.get("csrf", "")
    if not expected or not hmac.compare_digest(expected, submitted):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid request token")


def require_admin(request: Request) -> None:
    if request.session.get("admin") is not True:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"})
