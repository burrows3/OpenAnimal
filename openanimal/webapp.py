"""Local web frontend for OpenAnimal."""

from __future__ import annotations

import html
import json
import os
import random
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .agent import LifeAgent
from .config import TICK_INTERVAL_MAX, TICK_INTERVAL_MIN, TICKS_PER_INTERVAL
from .simulator import Simulator
from .storage import find_agent_by_slug, list_agents, list_public_feed, load_agent, save_agent


STATIC_ROOT = Path(__file__).resolve().parent.parent / "web"


def _describe_activity(agent: LifeAgent) -> str:
    if agent.missing_until_tick and agent.age_ticks < agent.missing_until_tick:
        return "Absent. No trace."
    if not agent.timeline.expressions:
        return "Quiet since birth."
    gap = agent.age_ticks - agent.last_expression_tick
    if gap > 200:
        return "Quiet for a long while."
    if gap > 60:
        return "Quiet recently."
    if gap > 20:
        return "Stirred not long ago."
    return "Active recently."


def _phase_label(phase: str) -> str:
    labels = {
        "infant": "Infant",
        "juvenile": "Juvenile",
        "mature": "Mature",
        "elder": "Elder",
    }
    return labels.get(phase, phase)


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
                    "slug": agent.slug,
                    "species": agent.species,
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

        last_activity = _describe_activity(agent)
        payload = {
            "animal_id": agent.animal_id,
            "slug": agent.slug,
            "species": agent.species,
            "age_ticks": agent.age_ticks,
            "phase": agent.phase,
            "pressure": agent.pressure,
            "state": agent.state,
            "last_expression_tick": agent.last_expression_tick,
            "memory_count": len(agent.memory.memories),
            "expressions_count": len(agent.timeline.expressions),
            "last_activity": last_activity,
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
        posts = list_public_feed()
        self._send_json({"posts": posts})

    def _api_birth(self, body: bytes | None = None) -> None:
        creator = ""
        if body:
            try:
                data = json.loads(body.decode("utf-8"))
                creator = (data.get("creator_id") or "").strip()
            except (ValueError, UnicodeDecodeError):
                self._send_json({"error": "invalid body"}, status=400)
                return
        if not creator:
            cookie = self.headers.get("Cookie", "")
            for part in cookie.split(";"):
                if "=" not in part:
                    continue
                key, value = part.strip().split("=", 1)
                if key == "openanimal_anon_id":
                    creator = value.strip()
                    break
        if not creator:
            creator = f"anon_{uuid.uuid4().hex[:12]}"
        agent = LifeAgent.birth(creator=creator)
        save_agent(agent)
        self._send_json({
            "animal_id": agent.animal_id,
            "creator": agent.creator,
            "slug": agent.slug,
            "species": agent.species,
        })

    def _send_animal_page(self, slug: str) -> None:
        agent = find_agent_by_slug(slug)
        if not agent:
            self._send_json({"error": "not_found"}, status=404)
            return
        activity = _describe_activity(agent)
        host = self.headers.get("Host", "openanimal.co")
        proto = self.headers.get("X-Forwarded-Proto", "https")
        if "localhost" in host or host.startswith("127.0.0.1"):
            proto = "http"
        base_url = f"{proto}://{host}"
        page_url = f"{base_url}/a/{agent.slug}"
        title = f"OpenAnimal · {agent.species.title()}"
        description = f"{_phase_label(agent.phase)} {agent.species}. {activity}"
        og_image = f"{base_url}/assets/logo.svg"
        recent_entries = agent.timeline.expressions[-4:]
        recent_lines = [
            " ".join(entry.sentences).strip()
            for entry in recent_entries
            if entry.sentences
        ]
        recent_html = "\n".join(
            f"<li>{html.escape(line)}</li>" for line in recent_lines
        ) or "<li>Silent.</li>"

        body = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{html.escape(title)}</title>
    <meta name="description" content="{html.escape(description)}" />
    <meta property="og:type" content="website" />
    <meta property="og:title" content="{html.escape(title)}" />
    <meta property="og:description" content="{html.escape(description)}" />
    <meta property="og:url" content="{html.escape(page_url)}" />
    <meta property="og:image" content="{html.escape(og_image)}" />
    <link rel="icon" type="image/svg+xml" href="/assets/favicon.svg" />
    <link rel="stylesheet" href="/styles.css" />
  </head>
  <body>
    <header class="site-header">
      <a href="/" class="logo" aria-label="OpenAnimal">
        <span class="logo-icon" aria-hidden="true">
          <svg width="28" height="28" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="16" cy="16" r="14" fill="#2563eb" />
            <circle cx="16" cy="12" r="4" fill="#fff" />
            <ellipse cx="16" cy="22" rx="6" ry="5" fill="#fff" />
            <circle cx="12" cy="11" r="1" fill="#1e40af" />
            <circle cx="20" cy="11" r="1" fill="#1e40af" />
          </svg>
        </span>
        <span class="logo-text">OpenAnimal</span>
      </a>
      <nav class="header-nav">
        <a href="/" class="nav-link">Back to the clearing</a>
      </nav>
    </header>
    <main>
      <section class="content-section" style="padding-top: 40px;">
        <div class="panel">
          <h2>{html.escape(agent.species.title())}</h2>
          <div class="muted" style="margin-bottom: 12px;">{html.escape(agent.slug)}</div>
          <div><strong>Stage:</strong> {_phase_label(agent.phase)}</div>
          <div><strong>Age:</strong> {agent.age_ticks} ticks</div>
          <div><strong>Last observed:</strong> {html.escape(activity)}</div>
          <div><strong>Temperament:</strong> {html.escape(", ".join(agent.temperament) or "unknown")}</div>
        </div>
        <div class="panel" style="margin-top: 24px;">
          <h3>Recent expressions</h3>
          <ul class="timeline" style="list-style: none; padding-left: 0;">
            {recent_html}
          </ul>
        </div>
      </section>
    </main>
  </body>
</html>"""
        self._send_bytes(body.encode("utf-8"), "text/html; charset=utf-8")

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/"):
            parts = path.strip("/").split("/")
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

        if path.startswith("/a/"):
            slug = path.split("/a/", 1)[-1].strip("/")
            self._send_animal_page(slug)
            return

        self._serve_static(path)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else None
        if parsed.path == "/api/animals/birth":
            self._api_birth(body=body)
            return

        self._send_json({"error": "not_found"}, status=404)


def _tick_loop(interval_min: float, interval_max: float, ticks_per_interval: int, stop_event: threading.Event) -> None:
    simulator = Simulator()
    while not stop_event.is_set():
        interval = random.uniform(interval_min, interval_max)
        time.sleep(interval)
        simulator.run(ticks=ticks_per_interval)


def run(host: str | None = None, port: int | None = None) -> None:
    interval_min = float(os.getenv("OPENANIMAL_TICK_INTERVAL_MIN", str(TICK_INTERVAL_MIN)))
    interval_max = float(os.getenv("OPENANIMAL_TICK_INTERVAL_MAX", str(TICK_INTERVAL_MAX)))
    ticks_per_interval = int(os.getenv("OPENANIMAL_TICKS_PER_INTERVAL", str(TICKS_PER_INTERVAL)))
    if interval_max < interval_min:
        interval_min, interval_max = interval_max, interval_min

    # Render and other hosts set PORT; listen on 0.0.0.0 so external traffic is accepted
    if port is None:
        port = int(os.getenv("PORT", "8000"))
    if host is None:
        host = "0.0.0.0" if os.getenv("PORT") else "127.0.0.1"

    stop_event = threading.Event()
    tick_thread = threading.Thread(
        target=_tick_loop,
        args=(interval_min, interval_max, ticks_per_interval, stop_event),
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
