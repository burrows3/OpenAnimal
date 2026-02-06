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
    )

    agent.memory = MemoryStore(
        memories=[Memory(**mem) for mem in payload.get("memory", [])],
    )
    agent.timeline = Timeline(
        expressions=[ExpressionEntry(**entry) for entry in payload.get("timeline", [])],
    )
    return agent


def list_agents() -> list[str]:
    if not ANIMALS_DIR.exists():
        return []
    return [path.stem for path in ANIMALS_DIR.glob("*.json")]


def save_archive(animal_id: str, snapshot: ArchiveSnapshot) -> None:
    _ensure_dirs()
    archive_dir = ARCHIVES_DIR / animal_id
    archive_dir.mkdir(parents=True, exist_ok=True)
    path = archive_dir / f"{snapshot.tick}.json"
    path.write_text(json.dumps(asdict(snapshot), indent=2), encoding="utf-8")
