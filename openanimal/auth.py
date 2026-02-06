"""Simple auth for OpenAnimal: users must sign in (Google) before birthing an animal."""

from __future__ import annotations

import hashlib
import json
import secrets
import uuid
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from .storage import DATA_ROOT

USERS_FILE = DATA_ROOT / "users.json"
SESSIONS_FILE = DATA_ROOT / "sessions.json"
# Server secret for hashing; override with OPENANIMAL_AUTH_SECRET in production
AUTH_SECRET = __import__("os").environ.get("OPENANIMAL_AUTH_SECRET", "openanimal-default-secret-change-in-production")
# Google OAuth client ID (required for Google sign-in)
GOOGLE_CLIENT_ID = __import__("os").environ.get("OPENANIMAL_GOOGLE_CLIENT_ID", "").strip()


def _hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((AUTH_SECRET + salt + password).encode()).hexdigest()


def _load_users() -> list[dict]:
    if not USERS_FILE.exists():
        return []
    try:
        data = json.loads(USERS_FILE.read_text(encoding="utf-8"))
        return data.get("users", [])
    except (json.JSONDecodeError, OSError):
        return []


def _save_users(users: list[dict]) -> None:
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    USERS_FILE.write_text(json.dumps({"users": users}, indent=2), encoding="utf-8")


def _load_sessions() -> dict[str, str]:
    if not SESSIONS_FILE.exists():
        return {}
    try:
        data = json.loads(SESSIONS_FILE.read_text(encoding="utf-8"))
        return data.get("tokens", {})
    except (json.JSONDecodeError, OSError):
        return {}


def _save_sessions(tokens: dict[str, str]) -> None:
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    SESSIONS_FILE.write_text(json.dumps({"tokens": tokens}, indent=2), encoding="utf-8")


def register(username: str, password: str) -> tuple[str, str] | tuple[None, str]:
    """Create a user. Returns (user_id, token) or (None, error_message)."""
    username = (username or "").strip()[:64]
    if not username:
        return None, "Username required"
    if not password or len(password) < 4:
        return None, "Password must be at least 4 characters"
    users = _load_users()
    if any(u.get("username", "").lower() == username.lower() for u in users):
        return None, "Username already taken"
    user_id = "user_" + uuid.uuid4().hex[:12]
    salt = secrets.token_hex(16)
    password_hash = _hash_password(password, salt)
    users.append({
        "id": user_id,
        "username": username,
        "salt": salt,
        "password_hash": password_hash,
    })
    _save_users(users)
    token = secrets.token_urlsafe(32)
    sessions = _load_sessions()
    sessions[token] = user_id
    _save_sessions(sessions)
    return user_id, token


def login(username: str, password: str) -> tuple[str, str] | tuple[None, str]:
    """Sign in. Returns (token, user_id) or (None, error_message)."""
    username = (username or "").strip()[:64]
    if not username or not password:
        return None, "Username and password required"
    users = _load_users()
    for u in users:
        if u.get("username", "").lower() == username.lower():
            h = _hash_password(password, u.get("salt", ""))
            if h != u.get("password_hash"):
                return None, "Invalid password"
            user_id = u["id"]
            token = secrets.token_urlsafe(32)
            sessions = _load_sessions()
            sessions[token] = user_id
            _save_sessions(sessions)
            return token, user_id
    return None, "User not found"


def get_user_by_token(token: str) -> dict | None:
    """Return user dict (id, username) if token is valid, else None."""
    if not token:
        return None
    sessions = _load_sessions()
    user_id = sessions.get(token)
    if not user_id:
        return None
    users = _load_users()
    for u in users:
        if u.get("id") == user_id:
            return {"id": user_id, "username": u.get("username", "")}
    return None


def logout(token: str) -> None:
    """Invalidate a session token."""
    if not token:
        return
    sessions = _load_sessions()
    sessions.pop(token, None)
    _save_sessions(sessions)


def _verify_google_id_token(id_token: str) -> dict | None:
    """Verify Google ID token via tokeninfo; return payload (sub, email, name) or None."""
    if not id_token or len(id_token) > 8192:
        return None
    try:
        req = Request(
            "https://oauth2.googleapis.com/tokeninfo?id_token=" + id_token,
            headers={"User-Agent": "OpenAnimal/1.0"},
        )
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if not data.get("sub"):
            return None
        if GOOGLE_CLIENT_ID and data.get("aud") != GOOGLE_CLIENT_ID:
            return None
        return {
            "sub": data.get("sub"),
            "email": (data.get("email") or "").strip()[:256],
            "name": (data.get("name") or data.get("email") or data.get("sub") or "User").strip()[:128],
        }
    except (HTTPError, URLError, json.JSONDecodeError, ValueError, OSError):
        return None


def auth_google(id_token: str) -> tuple[str, str, str] | tuple[None, str]:
    """Verify Google ID token and find or create user. Returns (user_id, token, username) or (None, error)."""
    if not GOOGLE_CLIENT_ID:
        return None, "Google sign-in is not configured."
    payload = _verify_google_id_token(id_token)
    if not payload:
        return None, "Invalid or expired Google sign-in."
    google_sub = payload["sub"]
    email = payload["email"] or ""
    name = payload["name"] or email or google_sub[:16]
    users = _load_users()
    for u in users:
        if u.get("google_id") == google_sub:
            user_id = u["id"]
            token = secrets.token_urlsafe(32)
            sessions = _load_sessions()
            sessions[token] = user_id
            _save_sessions(sessions)
            return user_id, token, u.get("username") or name
    user_id = "user_" + uuid.uuid4().hex[:12]
    users.append({
        "id": user_id,
        "username": name,
        "google_id": google_sub,
        "email": email,
    })
    _save_users(users)
    token = secrets.token_urlsafe(32)
    sessions = _load_sessions()
    sessions[token] = user_id
    _save_sessions(sessions)
    return user_id, token, name
