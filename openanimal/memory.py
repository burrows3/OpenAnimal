"""Memory system for OpenAnimal agents."""

from __future__ import annotations

import math
import uuid
from dataclasses import dataclass, field

from .config import MEMORY_DECAY_RATE, MEMORY_EARLY_BONUS_TICKS, MEMORY_MIN_WEIGHT


@dataclass
class Memory:
    memory_id: str
    text: str
    weight: float
    valence: float
    created_tick: int
    last_tick: int
    usage_count: int = 0


@dataclass
class MemoryStore:
    memories: list[Memory] = field(default_factory=list)

    def reinforce(self, text: str, valence: float, tick: int) -> Memory:
        for memory in self.memories:
            if memory.text == text:
                memory.weight = min(1.0, memory.weight + 0.12)
                memory.valence = max(-1.0, min(1.0, (memory.valence + valence) / 2))
                memory.last_tick = tick
                memory.usage_count += 1
                return memory

        weight = 0.4
        if tick <= MEMORY_EARLY_BONUS_TICKS:
            weight *= 1.3

        new_memory = Memory(
            memory_id=str(uuid.uuid4()),
            text=text,
            weight=min(1.0, weight),
            valence=max(-1.0, min(1.0, valence)),
            created_tick=tick,
            last_tick=tick,
        )
        self.memories.append(new_memory)
        return new_memory

    def decay(self, tick: int) -> None:
        for memory in self.memories:
            delta = max(0, tick - memory.last_tick)
            memory.weight *= math.exp(-MEMORY_DECAY_RATE * delta)

        self.memories = [memory for memory in self.memories if memory.weight >= MEMORY_MIN_WEIGHT]

    def most_salient(self, limit: int = 3) -> list[Memory]:
        return sorted(self.memories, key=lambda item: item.weight, reverse=True)[:limit]

    def conflict_score(self) -> float:
        if len(self.memories) < 2:
            return 0.0

        positives = [m.weight for m in self.memories if m.valence > 0.35]
        negatives = [m.weight for m in self.memories if m.valence < -0.35]
        if not positives or not negatives:
            return 0.0

        return min(1.0, (sum(positives) + sum(negatives)) / 4.0)
