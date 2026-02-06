"""Simulation loop for OpenAnimal."""

from __future__ import annotations

from dataclasses import dataclass

from .archive import create_snapshot
from .config import ARCHIVE_INTERVAL_TICKS
from .storage import get_recent_feed, list_agents, load_agent, save_agent, save_archive
from .world import WorldSignalStream


@dataclass
class SimulationReport:
    ticks: int
    expressions: int


class Simulator:
    def __init__(self, seed: int | None = None) -> None:
        self.world = WorldSignalStream(seed=seed)

    def run(self, ticks: int = 1) -> SimulationReport:
        expressions = 0
        for _ in range(ticks):
            animal_ids = list_agents()
            for animal_id in animal_ids:
                agent = load_agent(animal_id)
                world_signals = self.world.signals_for_tick(agent.age_ticks)
                # Pass recent expressions from other animals so this one can interact
                recent = get_recent_feed(exclude_animal_id=animal_id, limit=10)
                output = agent.tick(world_signals, recent_feed=recent)
                if output:
                    expressions += 1
                if agent.age_ticks % ARCHIVE_INTERVAL_TICKS == 0:
                    snapshot = create_snapshot(agent)
                    save_archive(agent.animal_id, snapshot)
                save_agent(agent)
        return SimulationReport(ticks=ticks, expressions=expressions)
