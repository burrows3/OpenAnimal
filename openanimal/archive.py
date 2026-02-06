"""Archive snapshots for OpenAnimal."""

from __future__ import annotations

from dataclasses import dataclass

from .agent import LifeAgent


@dataclass
class ArchiveSnapshot:
    tick: int
    summary: str
    memory_fragments: list[str]


def create_snapshot(agent: LifeAgent) -> ArchiveSnapshot:
    prominent = [mem.text for mem in agent.memory.most_salient(limit=3)]
    summary = (
        f"Phase: {agent.phase}. "
        f"Energy {agent.state['energy']:.2f}, "
        f"Comfort {agent.state['comfort']:.2f}, "
        f"Stress {agent.state['stress']:.2f}."
    )
    return ArchiveSnapshot(tick=agent.age_ticks, summary=summary, memory_fragments=prominent)
