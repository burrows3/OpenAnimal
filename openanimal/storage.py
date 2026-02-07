"""Persistence helpers for OpenAnimal."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .agent import LifeAgent
from .archive import ArchiveSnapshot
from .memory import Memory, MemoryStore
from .timeline import ExpressionEntry, Timeline
from .config import FEED_MAX_POSTS, STATE_KEYS

DATA_ROOT = Path("data")
ANIMALS_DIR = DATA_ROOT / "animals"
ARCHIVES_DIR = DATA_ROOT / "archives"


def _ensure_dirs() -> None:
    ANIMALS_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVES_DIR.mkdir(parents=True, exist_ok=True)


def save_agent(agent: LifeAgent) -> None:
    _ensure_dirs()
    path = ANIMALS_DIR / f"{agent.animal_id}.json"
    payload = {
        "animal_id": agent.animal_id,
        "created_at": agent.created_at,
        "age_ticks": agent.age_ticks,
        "phase": agent.phase,
        "state": agent.state,
        "pressure": agent.pressure,
        "tolerance": agent.tolerance,
        "last_expression_tick": agent.last_expression_tick,
        "rng_seed": agent.rng_seed,
        "creator": getattr(agent, "creator", ""),
        "species": agent.species,
        "slug": agent.slug,
        "temperament": agent.temperament,
        "encounters": agent.encounters,
        "silent_until_tick": agent.silent_until_tick,
        "missing_until_tick": agent.missing_until_tick,
        "memory": [asdict(mem) for mem in agent.memory.memories],
        "timeline": [asdict(entry) for entry in agent.timeline.expressions],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_agent(animal_id: str) -> LifeAgent:
    path = ANIMALS_DIR / f"{animal_id}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    phase = payload.get("phase", "infant")
    phase_map = {
        "infancy": "infant",
        "early_growth": "juvenile",
        "adolescence": "mature",
        "maturity": "elder",
    }
    phase = phase_map.get(phase, phase)
    state = payload.get("state", {})
    if not all(key in state for key in STATE_KEYS):
        state = {
            "arousal": float(state.get("stress", 0.5)),
            "curiosity": float(state.get("curiosity", 0.5)),
            "fatigue": float(1.0 - float(state.get("energy", 0.5))),
            "social_tolerance": float(1.0 - float(state.get("restlessness", 0.5))),
        }

    species = payload.get("species", "unknown")
    slug = payload.get("slug")
    if not slug:
        slug = f"{species}-{payload['animal_id'][:6]}" if species != "unknown" else payload["animal_id"][:8]

    agent = LifeAgent(
        animal_id=payload["animal_id"],
        created_at=payload["created_at"],
        age_ticks=payload["age_ticks"],
        phase=phase,
        state=state,
        pressure=payload["pressure"],
        tolerance=payload["tolerance"],
        last_expression_tick=payload["last_expression_tick"],
        rng_seed=payload.get("rng_seed", 0),
        creator=payload.get("creator", ""),
        species=species,
        slug=slug,
        temperament=payload.get("temperament", []),
        encounters=payload.get("encounters", {}),
        silent_until_tick=payload.get("silent_until_tick", 0),
        missing_until_tick=payload.get("missing_until_tick", 0),
    )

    agent.memory = MemoryStore(
        memories=[Memory(**mem) for mem in payload.get("memory", [])],
    )
    agent.timeline = Timeline(
        expressions=[ExpressionEntry(**entry) for entry in payload.get("timeline", [])],
    )
    return agent


def list_agents(creator: str | None = None) -> list[str]:
    if not ANIMALS_DIR.exists():
        return []
    ids = [path.stem for path in ANIMALS_DIR.glob("*.json")]
    if creator is None:
        return ids
    out = []
    for animal_id in ids:
        try:
            agent = load_agent(animal_id)
            if getattr(agent, "creator", "") == creator:
                out.append(animal_id)
        except (OSError, json.JSONDecodeError, KeyError):
            continue
    return out


def get_recent_feed(exclude_animal_id: str | None = None, limit: int = 15) -> list[dict]:
    """Recent expressions from all animals (for interaction). Each item: animal_id, tick, sentences."""
    if not ANIMALS_DIR.exists():
        return []
    items: list[tuple[int, str, int, list[str]]] = []  # (tick, animal_id, _, sentences)
    for path in ANIMALS_DIR.glob("*.json"):
        animal_id = path.stem
        if animal_id == exclude_animal_id:
            continue
        try:
            agent = load_agent(animal_id)
            if not agent.timeline.expressions:
                continue
            last = agent.timeline.expressions[-1]
            public_tick = last.public_tick if last.public_tick is not None else last.tick
            items.append((last.tick, animal_id, public_tick, last.sentences))
        except (OSError, json.JSONDecodeError, KeyError):
            continue
    items.sort(key=lambda x: x[0], reverse=True)
    return [
        {"animal_id": aid, "tick": tick, "public_tick": pt, "sentences": s}
        for tick, aid, pt, s in items[:limit]
    ]


def list_public_feed(limit: int | None = None) -> list[dict]:
    if not ANIMALS_DIR.exists():
        return []
    posts: list[dict] = []
    max_tick = 0
    for path in ANIMALS_DIR.glob("*.json"):
        try:
            agent = load_agent(path.stem)
        except (OSError, json.JSONDecodeError, KeyError):
            continue
        max_tick = max(max_tick, agent.age_ticks)
        for entry in agent.timeline.expressions:
            public_tick = entry.public_tick if entry.public_tick is not None else entry.tick
            posts.append(
                {
                    "animal_id": agent.animal_id,
                    "slug": agent.slug,
                    "species": agent.species,
                    "phase": agent.phase,
                    "tick": entry.tick,
                    "public_tick": public_tick,
                    "sentences": entry.sentences,
                    "creator": getattr(agent, "creator", ""),
                }
            )
    posts = [p for p in posts if p["public_tick"] <= max_tick]
    posts.sort(key=lambda p: p["public_tick"], reverse=True)
    limit = limit or FEED_MAX_POSTS
    return posts[:limit]


def find_agent_by_slug(slug: str) -> LifeAgent | None:
    if not slug or not ANIMALS_DIR.exists():
        return None
    for path in ANIMALS_DIR.glob("*.json"):
        try:
            agent = load_agent(path.stem)
        except (OSError, json.JSONDecodeError, KeyError):
            continue
        if agent.slug == slug or agent.animal_id == slug:
            return agent
    return None


def save_archive(animal_id: str, snapshot: ArchiveSnapshot) -> None:
    _ensure_dirs()
    archive_dir = ARCHIVES_DIR / animal_id
    archive_dir.mkdir(parents=True, exist_ok=True)
    path = archive_dir / f"{snapshot.tick}.json"
    path.write_text(json.dumps(asdict(snapshot), indent=2), encoding="utf-8")
