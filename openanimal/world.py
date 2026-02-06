"""World signal stream for OpenAnimal."""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass

from .config import TICK_SECONDS


@dataclass
class WorldSignals:
    tick: int
    time_elapsed: float
    circadian: float
    seasonality: float
    light_level: float
    environmental_noise: float
    randomness: float


class WorldSignalStream:
    """Shared, non-human input signals for all animals."""

    def __init__(self, seed: int | None = None, start_time: float | None = None) -> None:
        self._rng = random.Random(seed)
        self._start_time = start_time if start_time is not None else time.time()

    def signals_for_tick(self, tick: int) -> WorldSignals:
        time_elapsed = tick * TICK_SECONDS

        circadian = math.sin(2 * math.pi * (time_elapsed / (24 * 60 * 60)))
        seasonality = math.sin(2 * math.pi * (time_elapsed / (365 * 24 * 60 * 60)))
        light_level = max(0.0, circadian) * 0.8 + 0.2

        environmental_noise = max(0.0, self._rng.gauss(0.35, 0.15))
        randomness = self._rng.random()

        return WorldSignals(
            tick=tick,
            time_elapsed=time_elapsed,
            circadian=circadian,
            seasonality=seasonality,
            light_level=light_level,
            environmental_noise=environmental_noise,
            randomness=randomness,
        )
