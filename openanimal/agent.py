"""Life agent for OpenAnimal."""

from __future__ import annotations

import random
import time
import uuid
from dataclasses import dataclass, field

from .config import (
    EXPRESSION_BASE_PROB,
    EXPRESSION_COOLDOWN_TICKS,
    PHASE_THRESHOLDS,
    PRESSURE_BASE_GROWTH,
    PRESSURE_TOLERANCE_BASE,
    PRESSURE_TOLERANCE_VARIANCE,
    STATE_BOUNDS,
    STATE_DRIFT,
    STATE_KEYS,
)
from .expression import generate_expression
from .memory import MemoryStore
from .timeline import Timeline
from .world import WorldSignals


def _clamp(value: float, bounds: tuple[float, float]) -> float:
    return max(bounds[0], min(bounds[1], value))


@dataclass
class LifeAgent:
    animal_id: str
    created_at: float
    age_ticks: int
    phase: str
    state: dict[str, float]
    pressure: float
    tolerance: float
    last_expression_tick: int
    memory: MemoryStore = field(default_factory=MemoryStore)
    timeline: Timeline = field(default_factory=Timeline)
    rng_seed: int = field(default_factory=lambda: random.randint(0, 1_000_000))
    creator: str = ""

    @classmethod
    def birth(cls, creator: str = "") -> "LifeAgent":
        rng = random.Random()
        state = {key: rng.uniform(0.35, 0.65) for key in STATE_KEYS}
        tolerance = _clamp(
            PRESSURE_TOLERANCE_BASE + rng.uniform(-PRESSURE_TOLERANCE_VARIANCE, PRESSURE_TOLERANCE_VARIANCE),
            (0.4, 0.9),
        )
        return cls(
            animal_id=str(uuid.uuid4()),
            created_at=time.time(),
            age_ticks=0,
            phase="infancy",
            state=state,
            pressure=rng.uniform(0.1, 0.3),
            tolerance=tolerance,
            last_expression_tick=0,
            creator=creator or "",
        )

    def _update_phase(self) -> None:
        if self.age_ticks >= PHASE_THRESHOLDS["maturity"]:
            self.phase = "maturity"
        elif self.age_ticks >= PHASE_THRESHOLDS["adolescence"]:
            self.phase = "adolescence"
        elif self.age_ticks >= PHASE_THRESHOLDS["early_growth"]:
            self.phase = "early_growth"
        else:
            self.phase = "infancy"

    def _drift_state(self, world: WorldSignals, rng: random.Random) -> None:
        for key in STATE_KEYS:
            drift = STATE_DRIFT[key] * rng.uniform(-1.0, 1.0)
            self.state[key] = _clamp(self.state[key] + drift, STATE_BOUNDS)

        self.state["energy"] = _clamp(
            self.state["energy"] + (0.02 * world.light_level) - (0.01 * world.environmental_noise),
            STATE_BOUNDS,
        )
        self.state["alertness"] = _clamp(
            self.state["alertness"] + (0.03 * world.environmental_noise) - (0.01 * world.light_level),
            STATE_BOUNDS,
        )
        self.state["comfort"] = _clamp(
            self.state["comfort"] + (0.01 * world.light_level) - (0.02 * world.environmental_noise),
            STATE_BOUNDS,
        )
        self.state["restlessness"] = _clamp(
            self.state["restlessness"] + (0.02 * world.environmental_noise) - (0.01 * self.state["comfort"]),
            STATE_BOUNDS,
        )

    def _pressure_from_state(self) -> float:
        imbalance = abs(self.state["stress"] - self.state["comfort"]) + abs(
            self.state["restlessness"] - self.state["energy"]
        )
        curiosity_unmet = max(0.0, self.state["curiosity"] - self.state["familiarity"])
        return min(1.0, (imbalance + curiosity_unmet) / 3.0)

    def tick(
        self, world: WorldSignals, recent_feed: list[dict] | None = None
    ) -> list[str] | None:
        rng = random.Random(self.rng_seed + self.age_ticks)
        self.age_ticks += 1
        self._update_phase()

        self._drift_state(world, rng)
        self.memory.decay(self.age_ticks)

        conflict = self.memory.conflict_score()
        self.pressure = _clamp(
            self.pressure + PRESSURE_BASE_GROWTH + self._pressure_from_state() + conflict * 0.08,
            (0.0, 1.2),
        )

        if self.age_ticks - self.last_expression_tick < EXPRESSION_COOLDOWN_TICKS:
            return None

        # Social facilitation: more likely to express when others are active (real animal behavior)
        feed_size = len(recent_feed or [])
        expr_prob = EXPRESSION_BASE_PROB
        if feed_size >= 2:
            expr_prob = min(0.5, expr_prob + 0.08 * feed_size)

        if self.pressure >= self.tolerance and rng.random() < expr_prob:
            sentences = generate_expression(
                world, self.memory, rng, recent_from_others=recent_feed or []
            )
            self.timeline.add_expression(self.age_ticks, sentences)
            self.last_expression_tick = self.age_ticks
            self.pressure = max(0.15, self.pressure - 0.5)

            for sentence in sentences:
                self.memory.reinforce(sentence, valence=rng.uniform(-0.4, 0.4), tick=self.age_ticks)

            return sentences

        return None
