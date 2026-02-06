"""Simulation loop for OpenAnimal."""

from __future__ import annotations

from dataclasses import dataclass

from .archive import create_snapshot
from .config import ARCHIVE_INTERVAL_TICKS
from .storage import list_agents, load_agent, save_agent, save_archive
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
            for animal_id in list_agents():
                agent = load_agent(animal_id)
                world_signals = self.world.signals_for_tick(agent.age_ticks)
                output = agent.tick(world_signals)
                if output:
                    expressions += 1
                if agent.age_ticks % ARCHIVE_INTERVAL_TICKS == 0:
                    snapshot = create_snapshot(agent)
                    save_archive(agent.animal_id, snapshot)
                save_agent(agent)
        return SimulationReport(ticks=ticks, expressions=expressions)
