"""Persistence helpers for OpenAnimal."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .agent import LifeAgent
from .archive import ArchiveSnapshot
from .memory import Memory, MemoryStore
from .timeline import ExpressionEntry, Timeline

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
        "memory": [asdict(mem) for mem in agent.memory.memories],
        "timeline": [asdict(entry) for entry in agent.timeline.expressions],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_agent(animal_id: str) -> LifeAgent:
    path = ANIMALS_DIR / f"{animal_id}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))

    agent = LifeAgent(
        animal_id=payload["animal_id"],
        created_at=payload["created_at"],
        age_ticks=payload["age_ticks"],
        phase=payload["phase"],
        state=payload["state"],
        pressure=payload["pressure"],
        tolerance=payload["tolerance"],
        last_expression_tick=payload["last_expression_tick"],
        rng_seed=payload.get("rng_seed", 0),
        creator=payload.get("creator", ""),
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
            items.append((last.tick, animal_id, last.tick, last.sentences))
        except (OSError, json.JSONDecodeError, KeyError):
            continue
    items.sort(key=lambda x: x[0], reverse=True)
    return [{"animal_id": aid, "tick": t, "sentences": s} for _, aid, t, s in items[:limit]]


def save_archive(animal_id: str, snapshot: ArchiveSnapshot) -> None:
    _ensure_dirs()
    archive_dir = ARCHIVES_DIR / animal_id
    archive_dir.mkdir(parents=True, exist_ok=True)
    path = archive_dir / f"{snapshot.tick}.json"
    path.write_text(json.dumps(asdict(snapshot), indent=2), encoding="utf-8")
