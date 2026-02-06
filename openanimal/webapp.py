"""Local web frontend for OpenAnimal."""

from __future__ import annotations

import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .agent import LifeAgent
from .auth import auth_google, get_user_by_token, login, register
from .env import get_google_client_id
from .simulator import Simulator
from .storage import list_agents, load_agent, save_agent


STATIC_ROOT = Path(__file__).resolve().parent.parent / "web"


class OpenAnimalHandler(BaseHTTPRequestHandler):
    server_version = "OpenAnimalHTTP/0.1"

    def _send_json(self, payload: dict, status: int = 200) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_bytes(self, data: bytes, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _serve_static(self, path: str) -> None:
        if path == "/":
            path = "/index.html"

        safe_path = Path(path.lstrip("/"))
        full_path = (STATIC_ROOT / safe_path).resolve()
        if STATIC_ROOT not in full_path.parents and full_path != STATIC_ROOT:
            self._send_json({"error": "forbidden"}, status=403)
            return

        if not full_path.exists() or not full_path.is_file():
            self._send_json({"error": "not_found"}, status=404)
            return

        content_type = "text/plain; charset=utf-8"
        if full_path.suffix == ".html":
            content_type = "text/html; charset=utf-8"
        elif full_path.suffix == ".css":
            content_type = "text/css; charset=utf-8"
        elif full_path.suffix == ".js":
            content_type = "application/javascript; charset=utf-8"
        elif full_path.suffix == ".svg":
            content_type = "image/svg+xml"

        self._send_bytes(full_path.read_bytes(), content_type)

    def _api_list_animals(self, creator: str | None = None) -> None:
        animals = []
        for animal_id in list_agents(creator=creator):
            agent = load_agent(animal_id)
            animals.append(
                {
                    "animal_id": agent.animal_id,
                    "age_ticks": agent.age_ticks,
                    "phase": agent.phase,
                    "last_expression_tick": agent.last_expression_tick,
                    "creator": getattr(agent, "creator", "") or "",
                }
            )
        self._send_json({"animals": animals})

    def _api_get_animal(self, animal_id: str) -> None:
        try:
            agent = load_agent(animal_id)
        except FileNotFoundError:
            self._send_json({"error": "not_found"}, status=404)
            return

        payload = {
            "animal_id": agent.animal_id,
            "age_ticks": agent.age_ticks,
            "phase": agent.phase,
            "pressure": agent.pressure,
            "state": agent.state,
            "last_expression_tick": agent.last_expression_tick,
            "memory_count": len(agent.memory.memories),
            "expressions_count": len(agent.timeline.expressions),
        }
        self._send_json(payload)

    def _api_get_timeline(self, animal_id: str) -> None:
        try:
            agent = load_agent(animal_id)
        except FileNotFoundError:
            self._send_json({"error": "not_found"}, status=404)
            return

        lines = agent.timeline.render(current_tick=agent.age_ticks)
        self._send_json({"animal_id": agent.animal_id, "age_ticks": agent.age_ticks, "lines": lines})

    def _api_get_feed(self) -> None:
        """Merged feed of all animals' expressions (open network), newest first."""
        posts: list[dict] = []
        for animal_id in list_agents():
            try:
                agent = load_agent(animal_id)
            except (FileNotFoundError, json.JSONDecodeError):
                continue
            creator = getattr(agent, "creator", "") or ""
            for entry in agent.timeline.expressions:
                posts.append(
                    {
                        "animal_id": agent.animal_id,
                        "phase": agent.phase,
                        "tick": entry.tick,
                        "sentences": entry.sentences,
                        "creator": creator,
                    }
                )
        posts.sort(key=lambda p: p["tick"], reverse=True)
        self._send_json({"posts": posts[:200]})

    def _get_bearer_token(self) -> str | None:
        auth = self.headers.get("Authorization") or ""
        if auth.startswith("Bearer "):
            return auth[7:].strip()
        return None

    def _api_auth_register(self, body: bytes | None) -> None:
        if not body:
            self._send_json({"error": "username and password required"}, status=400)
            return
        try:
            data = json.loads(body.decode("utf-8"))
            username = (data.get("username") or "").strip()
            password = data.get("password") or ""
        except (ValueError, UnicodeDecodeError):
            self._send_json({"error": "invalid body"}, status=400)
            return
        result = register(username, password)
        if result[0] is None:
            self._send_json({"error": result[1]}, status=400)
            return
        user_id, token = result
        user = get_user_by_token(token)
        self._send_json({
            "token": token,
            "user_id": user_id,
            "username": user["username"] if user else username,
        })

    def _api_auth_login(self, body: bytes | None) -> None:
        if not body:
            self._send_json({"error": "username and password required"}, status=400)
            return
        try:
            data = json.loads(body.decode("utf-8"))
            username = (data.get("username") or "").strip()
            password = data.get("password") or ""
        except (ValueError, UnicodeDecodeError):
            self._send_json({"error": "invalid body"}, status=400)
            return
        result = login(username, password)
        if result[0] is None:
            self._send_json({"error": result[1]}, status=401)
            return
        token, user_id = result
        user = get_user_by_token(token)
        self._send_json({
            "token": token,
            "user_id": user_id,
            "username": user["username"] if user else username,
        })

    def _api_auth_me(self) -> None:
        token = self._get_bearer_token()
        user = get_user_by_token(token) if token else None
        if not user:
            self._send_json({"error": "not_authenticated"}, status=401)
            return
        self._send_json({"user_id": user["id"], "username": user["username"]})

    def _api_config(self) -> None:
        """Public config for frontend (e.g. Google Client ID for sign-in)."""
        self._send_json({
            "google_client_id": get_google_client_id(),
        })

    def _api_auth_google(self, body: bytes | None = None) -> None:
        if not body:
            self._send_json({"error": "id_token required"}, status=400)
            return
        try:
            data = json.loads(body.decode("utf-8"))
            id_token = (data.get("id_token") or data.get("credential") or "").strip()
        except (ValueError, UnicodeDecodeError):
            self._send_json({"error": "invalid body"}, status=400)
            return
        if not id_token:
            self._send_json({"error": "id_token required"}, status=400)
            return
        result = auth_google(id_token)
        if result[0] is None:
            self._send_json({"error": result[1]}, status=401)
            return
        user_id, token, username = result
        self._send_json({
            "token": token,
            "user_id": user_id,
            "username": username,
        })

    def _api_birth(self, body: bytes | None = None) -> None:
        token = self._get_bearer_token()
        user = get_user_by_token(token) if token else None
        if not user:
            self._send_json({"error": "sign_in_required", "message": "Sign in to birth an animal."}, status=401)
            return
        creator = user["id"]
        agent = LifeAgent.birth(creator=creator)
        save_agent(agent)
        self._send_json({"animal_id": agent.animal_id, "creator": agent.creator})

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/"):
            parts = path.strip("/").split("/")
            if parts == ["api", "auth", "me"]:
                self._api_auth_me()
                return
            if parts == ["api", "config"]:
                self._api_config()
                return
            if parts == ["api", "feed"]:
                self._api_get_feed()
                return
            if parts == ["api", "animals"]:
                qs = parse_qs(parsed.query)
                creator = qs.get("creator", [None])[0] if qs else None
                self._api_list_animals(creator=creator)
                return
            if len(parts) >= 3 and parts[0] == "api" and parts[1] == "animals":
                animal_id = parts[2]
                if len(parts) == 4 and parts[3] == "timeline":
                    self._api_get_timeline(animal_id)
                    return
                if len(parts) == 3:
                    self._api_get_animal(animal_id)
                    return

            self._send_json({"error": "not_found"}, status=404)
            return

        self._serve_static(path)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else None
        if parsed.path == "/api/auth/register":
            self._api_auth_register(body)
            return
        if parsed.path == "/api/auth/login":
            self._api_auth_login(body)
            return
        if parsed.path == "/api/auth/google":
            self._api_auth_google(body)
            return
        if parsed.path == "/api/animals/birth":
            self._api_birth(body=body)
            return

        self._send_json({"error": "not_found"}, status=404)


def _tick_loop(interval: float, ticks_per_interval: int, stop_event: threading.Event) -> None:
    simulator = Simulator()
    while not stop_event.is_set():
        time.sleep(interval)
        simulator.run(ticks=ticks_per_interval)


def run(host: str | None = None, port: int | None = None) -> None:
    # Run multiple ticks per interval so agents post and interact visibly (Moltbook-style feed)
    interval = float(os.getenv("OPENANIMAL_TICK_INTERVAL", "5"))
    ticks_per_interval = int(os.getenv("OPENANIMAL_TICKS_PER_INTERVAL", "6"))

    # Render and other hosts set PORT; listen on 0.0.0.0 so external traffic is accepted
    if port is None:
        port = int(os.getenv("PORT", "8000"))
    if host is None:
        host = "0.0.0.0" if os.getenv("PORT") else "127.0.0.1"

    stop_event = threading.Event()
    tick_thread = threading.Thread(
        target=_tick_loop,
        args=(interval, ticks_per_interval, stop_event),
        daemon=True,
    )
    tick_thread.start()

    server = ThreadingHTTPServer((host, port), OpenAnimalHandler)
    try:
        server.serve_forever()
    finally:
        stop_event.set()
        server.server_close()


if __name__ == "__main__":
    run()
