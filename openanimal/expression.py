"""Expression generation for OpenAnimal agents."""

from __future__ import annotations

import random

from .memory import MemoryStore
from .world import WorldSignals


SENSORY_WORDS = [
    "Cold",
    "Warmth",
    "Light",
    "Shadow",
    "Noise",
    "Stillness",
    "Air",
    "Scent",
    "Damp",
    "Dryness",
    "Pressure",
    "Distance",
]

ACTION_PHRASES = [
    "Returned to the same place.",
    "Moved, then stayed.",
    "Waited.",
    "Stayed low.",
    "Shifted position.",
    "Paused for a while.",
    "Left and returned.",
]

ENVIRONMENT_PHRASES = [
    "Light thinned.",
    "Shadow moved.",
    "Noise swelled, then eased.",
    "Stillness held.",
    "Air changed.",
    "Scent changed.",
    "Warmth faded.",
]


def _sensory_from_world(world: WorldSignals, rng: random.Random) -> str:
    if world.light_level < 0.35:
        return rng.choice(["Shadow", "Darkness", "Dim light"])
    if world.light_level > 0.8:
        return rng.choice(["Light", "Bright light", "Warmth"])
    if world.environmental_noise > 0.55:
        return rng.choice(["Noise", "Movement", "Rustle"])
    return rng.choice(SENSORY_WORDS)


def generate_expression(world: WorldSignals, memory: MemoryStore, rng: random.Random) -> list[str]:
    sentences: list[str] = []

    sensory = _sensory_from_world(world, rng)
    sentences.append(f"{sensory} lingered.")

    if memory.memories and rng.random() < 0.5:
        remembered = rng.choice(memory.most_salient(limit=3))
        sentences.append(f"{remembered.text}")
    else:
        sentences.append(rng.choice(ENVIRONMENT_PHRASES))

    if rng.random() < 0.4:
        sentences.append(rng.choice(ACTION_PHRASES))

    return sentences[: rng.randint(1, 3)]
