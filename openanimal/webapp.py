"""Local web frontend for OpenAnimal."""

from __future__ import annotations

import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .agent import LifeAgent
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

        self._send_bytes(full_path.read_bytes(), content_type)

    def _api_list_animals(self) -> None:
        animals = []
        for animal_id in list_agents():
            agent = load_agent(animal_id)
            animals.append(
                {
                    "animal_id": agent.animal_id,
                    "age_ticks": agent.age_ticks,
                    "phase": agent.phase,
                    "last_expression_tick": agent.last_expression_tick,
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

    def _api_birth(self) -> None:
        agent = LifeAgent.birth()
        save_agent(agent)
        self._send_json({"animal_id": agent.animal_id})

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/"):
            parts = path.strip("/").split("/")
            if parts == ["api", "animals"]:
                self._api_list_animals()
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
        if parsed.path == "/api/animals/birth":
            self._api_birth()
            return

        self._send_json({"error": "not_found"}, status=404)


def _tick_loop(interval: float, ticks_per_interval: int, stop_event: threading.Event) -> None:
    simulator = Simulator()
    while not stop_event.is_set():
        time.sleep(interval)
        simulator.run(ticks=ticks_per_interval)


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    interval = float(os.getenv("OPENANIMAL_TICK_INTERVAL", "10"))
    ticks_per_interval = int(os.getenv("OPENANIMAL_TICKS_PER_INTERVAL", "1"))

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
