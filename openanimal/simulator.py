"""Simulation loop for OpenAnimal."""

from __future__ import annotations

from dataclasses import dataclass
import random

from .archive import create_snapshot
from .config import ARCHIVE_INTERVAL_TICKS, SPECIES
from .agent import LifeAgent
from .storage import get_recent_feed, list_agents, load_agent, save_agent, save_archive
from .world import WorldSignalStream


@dataclass
class SimulationReport:
    ticks: int
    expressions: int


class Simulator:
    def __init__(self, seed: int | None = None) -> None:
        self.world = WorldSignalStream(seed=seed)
        self.rng = random.Random(seed)

    def run(self, ticks: int = 1) -> SimulationReport:
        expressions = 0
        for _ in range(ticks):
            animal_ids = list_agents()
            if not animal_ids:
                continue
            sample_fraction = self.rng.uniform(0.2, 0.6)
            sample_size = max(1, int(len(animal_ids) * sample_fraction))
            if sample_size < len(animal_ids):
                animal_ids = self.rng.sample(animal_ids, k=sample_size)
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
            if self.rng.random() < 0.003:
                parent_id = self.rng.choice(animal_ids)
                parent = load_agent(parent_id)
                child = LifeAgent.birth(creator=parent.creator)
                child.species = self.rng.choice([parent.species] + SPECIES)
                child.slug = f"{child.species}-{child.animal_id[:6]}"
                save_agent(child)
        return SimulationReport(ticks=ticks, expressions=expressions)
