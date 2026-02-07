"""Environment helpers for OpenAnimal."""

from __future__ import annotations

import os
from pathlib import Path

_ENV_LOADED = False
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


def load_env(env_path: Path | None = None) -> None:
    """Load .env into os.environ once (no overwrite)."""
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    _ENV_LOADED = True
    path = env_path or _ENV_PATH
    try:
        if not path.exists():
            return
        content = path.read_text(encoding="utf-8")
    except OSError:
        return
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.lower().startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue
        value = value.strip()
        if value and value[0] == value[-1] and value.startswith(("'", '"')):
            value = value[1:-1]
        os.environ.setdefault(key, value)


def get_env(key: str, default: str = "") -> str:
    load_env()
    return os.environ.get(key, default)


def get_google_client_id() -> str:
    return get_env("OPENANIMAL_GOOGLE_CLIENT_ID", "").strip()


def get_auth_secret() -> str:
    return get_env("OPENANIMAL_AUTH_SECRET", "openanimal-default-secret-change-in-production")


def get_supabase_url() -> str:
    return get_env("OPENANIMAL_SUPABASE_URL", "").strip()


def get_supabase_anon_key() -> str:
    return get_env("OPENANIMAL_SUPABASE_ANON_KEY", "").strip()


def get_supabase_redirect_url() -> str:
    return get_env("OPENANIMAL_SUPABASE_REDIRECT_URL", "").strip()
