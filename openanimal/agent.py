"""Life agent for OpenAnimal."""

from __future__ import annotations

import random
import time
import uuid
from dataclasses import dataclass, field

from .config import (
    ACTION_PROBS,
    ENCOUNTER_BOOST,
    ENCOUNTER_DECAY,
    EXPRESSION_COOLDOWN_TICKS,
    PHASE_THRESHOLDS,
    PRESSURE_BASE_GROWTH,
    PRESSURE_TOLERANCE_BASE,
    PRESSURE_TOLERANCE_VARIANCE,
    PUBLIC_BACKDATE_PROB,
    PUBLIC_DELAY_MAX,
    PUBLIC_DELAY_MIN,
    RARE_EVENT_DISAPPEAR_PROB,
    RARE_EVENT_MUTATION_PROB,
    RARE_EVENT_PROB,
    RARE_EVENT_SILENCE_PROB,
    RARE_EVENT_SHIFT_PROB,
    SPECIES,
    STATE_BOUNDS,
    STATE_DRIFT,
    STATE_KEYS,
    TEMPERAMENTS,
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
    species: str
    slug: str
    temperament: list[str]
    encounters: dict[str, dict]
    silent_until_tick: int = 0
    missing_until_tick: int = 0
    memory: MemoryStore = field(default_factory=MemoryStore)
    timeline: Timeline = field(default_factory=Timeline)
    rng_seed: int = field(default_factory=lambda: random.randint(0, 1_000_000))
    creator: str = ""

    @classmethod
    def birth(cls, creator: str = "") -> "LifeAgent":
        rng = random.Random()
        state = {key: rng.uniform(0.25, 0.75) for key in STATE_KEYS}
        tolerance = _clamp(
            PRESSURE_TOLERANCE_BASE + rng.uniform(-PRESSURE_TOLERANCE_VARIANCE, PRESSURE_TOLERANCE_VARIANCE),
            (0.35, 0.95),
        )
        species = rng.choice(SPECIES)
        short_id = uuid.uuid4().hex[:6]
        slug = f"{species}-{short_id}"
        temperament = rng.sample(TEMPERAMENTS, k=2)
        return cls(
            animal_id=str(uuid.uuid4()),
            created_at=time.time(),
            age_ticks=0,
            phase="infant",
            state=state,
            pressure=rng.uniform(0.05, 0.25),
            tolerance=tolerance,
            last_expression_tick=0,
            species=species,
            slug=slug,
            temperament=temperament,
            encounters={},
            creator=creator or "",
        )

    def _update_phase(self) -> None:
        if self.age_ticks >= PHASE_THRESHOLDS["elder"]:
            self.phase = "elder"
        elif self.age_ticks >= PHASE_THRESHOLDS["mature"]:
            self.phase = "mature"
        elif self.age_ticks >= PHASE_THRESHOLDS["juvenile"]:
            self.phase = "juvenile"
        else:
            self.phase = "infant"

    def _drift_state(self, world: WorldSignals, rng: random.Random) -> None:
        for key in STATE_KEYS:
            drift = STATE_DRIFT[key] * rng.uniform(-1.0, 1.0)
            self.state[key] = _clamp(self.state[key] + drift, STATE_BOUNDS)

        self.state["arousal"] = _clamp(
            self.state["arousal"] + (0.03 * world.environmental_noise) - (0.02 * self.state["fatigue"]),
            STATE_BOUNDS,
        )
        self.state["curiosity"] = _clamp(
            self.state["curiosity"] + (0.02 * world.light_level) - (0.01 * self.state["fatigue"]),
            STATE_BOUNDS,
        )
        self.state["fatigue"] = _clamp(
            self.state["fatigue"] + (0.02 * world.environmental_noise) - (0.015 * world.light_level),
            STATE_BOUNDS,
        )
        self.state["social_tolerance"] = _clamp(
            self.state["social_tolerance"] + (0.01 * world.light_level) - (0.02 * world.environmental_noise),
            STATE_BOUNDS,
        )

    def _pressure_from_state(self) -> float:
        drive = self.state["arousal"] + self.state["curiosity"]
        inhibition = self.state["fatigue"] + (1.0 - self.state["social_tolerance"])
        return min(1.0, max(0.0, (drive - inhibition + 1.0) / 3.0))

    def _decay_encounters(self) -> None:
        if not self.encounters:
            return
        for other_id in list(self.encounters.keys()):
            self.encounters[other_id]["score"] *= ENCOUNTER_DECAY
            if self.encounters[other_id]["score"] < 0.02:
                self.encounters.pop(other_id, None)

    def _observe_other(self, rng: random.Random, recent_feed: list[dict]) -> None:
        if not recent_feed:
            return
        weights = []
        for entry in recent_feed:
            other_id = entry.get("animal_id") or ""
            score = self.encounters.get(other_id, {}).get("score", 0.1)
            weights.append(max(0.05, score))
        other = rng.choices(recent_feed, weights=weights, k=1)[0]
        other_id = other.get("animal_id") or ""
        if not other_id:
            return
        record = self.encounters.setdefault(other_id, {"score": 0.1, "last_tick": self.age_ticks})
        record["score"] = min(1.0, record["score"] + ENCOUNTER_BOOST)
        record["last_tick"] = self.age_ticks
        if other.get("sentences") and rng.random() < 0.45:
            snippet = rng.choice(other["sentences"])
            self.memory.reinforce(snippet, valence=rng.uniform(-0.2, 0.25), tick=self.age_ticks)
        self.state["social_tolerance"] = _clamp(
            self.state["social_tolerance"] - rng.uniform(0.0, 0.03), STATE_BOUNDS
        )

    def tick(
        self, world: WorldSignals, recent_feed: list[dict] | None = None
    ) -> list[str] | None:
        rng = random.Random(self.rng_seed + self.age_ticks)
        self.age_ticks += 1
        self._update_phase()

        self._drift_state(world, rng)
        self.memory.decay(self.age_ticks)
        self._decay_encounters()

        conflict = self.memory.conflict_score()
        self.pressure = _clamp(
            self.pressure + PRESSURE_BASE_GROWTH + self._pressure_from_state() + conflict * 0.05,
            (0.0, 1.2),
        )

        if self.age_ticks < self.silent_until_tick or self.age_ticks < self.missing_until_tick:
            return None

        if rng.random() < RARE_EVENT_PROB:
            event_roll = rng.random()
            silence_cutoff = RARE_EVENT_SILENCE_PROB
            shift_cutoff = silence_cutoff + RARE_EVENT_SHIFT_PROB
            mutation_cutoff = shift_cutoff + RARE_EVENT_MUTATION_PROB
            disappear_cutoff = mutation_cutoff + RARE_EVENT_DISAPPEAR_PROB
            if event_roll < silence_cutoff:
                self.silent_until_tick = self.age_ticks + rng.randint(12, 80)
            elif event_roll < shift_cutoff:
                replacement = rng.choice(TEMPERAMENTS)
                if replacement not in self.temperament:
                    self.temperament[0] = replacement
            elif event_roll < mutation_cutoff:
                self.state["arousal"] = _clamp(self.state["arousal"] + rng.uniform(0.1, 0.2), STATE_BOUNDS)
                self.tolerance = _clamp(self.tolerance + rng.uniform(-0.1, 0.1), (0.35, 0.95))
            elif event_roll < disappear_cutoff:
                self.missing_until_tick = self.age_ticks + rng.randint(20, 120)

        if self.age_ticks - self.last_expression_tick < EXPRESSION_COOLDOWN_TICKS:
            return None

        roll = rng.random()
        action = "silent"
        if roll < ACTION_PROBS["silent"]:
            action = "silent"
        elif roll < ACTION_PROBS["silent"] + ACTION_PROBS["observe"]:
            action = "observe"
        elif roll < ACTION_PROBS["silent"] + ACTION_PROBS["observe"] + ACTION_PROBS["internal"]:
            action = "internal"
        else:
            action = "express"

        if action == "observe":
            if self.state["social_tolerance"] < 0.25 and rng.random() < 0.6:
                return None
            self._observe_other(rng, recent_feed or [])
            return None
        if action == "internal":
            self.state["fatigue"] = _clamp(self.state["fatigue"] + rng.uniform(0.02, 0.08), STATE_BOUNDS)
            self.state["arousal"] = _clamp(self.state["arousal"] - rng.uniform(0.01, 0.05), STATE_BOUNDS)
            return None
        if action == "silent":
            return None

        if self.pressure >= self.tolerance:
            sentences = generate_expression(
                world,
                self.memory,
                rng,
                recent_from_others=recent_feed or [],
                temperament=self.temperament,
            )
            delay = rng.randint(PUBLIC_DELAY_MIN, PUBLIC_DELAY_MAX)
            if rng.random() < PUBLIC_BACKDATE_PROB:
                delay = -abs(delay)
            public_tick = max(0, self.age_ticks + delay)
            self.timeline.add_expression(self.age_ticks, sentences, public_tick=public_tick)
            self.last_expression_tick = self.age_ticks
            self.pressure = max(0.1, self.pressure - 0.4)

            for sentence in sentences:
                self.memory.reinforce(sentence, valence=rng.uniform(-0.3, 0.3), tick=self.age_ticks)

            return sentences

        return None
