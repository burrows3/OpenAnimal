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

# Non-human fragments, sensory and emotional.
SENSE_PHRASES = [
    "Light thinned.",
    "Shadow moved.",
    "Noise swelled, then eased.",
    "Stillness held.",
    "Air changed.",
    "Scent changed.",
    "Warmth faded.",
    "Coolness gathered.",
    "Edges softened.",
    "Weight shifted.",
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

MOOD_FRAGMENTS = [
    "Soft inside.",
    "Tight inside.",
    "Loose inside.",
    "Restless.",
    "Still.",
    "Vigilant.",
    "Wary.",
    "Curious.",
]


def _sensory_from_world(world: WorldSignals, rng: random.Random) -> str:
    if world.light_level < 0.35:
        return rng.choice(["Shadow", "Darkness", "Dim light"])
    if world.light_level > 0.8:
        return rng.choice(["Light", "Bright light", "Warmth"])
    if world.environmental_noise > 0.55:
        return rng.choice(["Noise", "Movement", "Rustle"])
    return rng.choice(SENSORY_WORDS)


def _echo_fragment(line: str, rng: random.Random) -> str:
    words = [w.strip(".,!?\"'") for w in line.split() if len(w) > 3]
    if not words:
        return rng.choice(MOOD_FRAGMENTS)
    word = rng.choice(words)[:18]
    templates = [
        f"{word}.",
        f"{word} again.",
        f"Echo: {word}.",
    ]
    return rng.choice(templates)


def generate_expression(
    world: WorldSignals,
    memory: MemoryStore,
    rng: random.Random,
    recent_from_others: list[dict] | None = None,
    temperament: list[str] | None = None,
) -> list[str]:
    sentences: list[str] = []

    if recent_from_others and rng.random() < 0.35:
        other = rng.choice(recent_from_others)
        if other.get("sentences"):
            line = rng.choice(other["sentences"])
            sentences.append(_echo_fragment(line, rng))
            if rng.random() < 0.5:
                sentences.append(rng.choice(SENSE_PHRASES))
            return sentences[: rng.randint(1, 2)]

    if rng.random() < 0.45:
        sensory = _sensory_from_world(world, rng)
        sentences.append(f"{sensory} lingered.")
    else:
        sentences.append(rng.choice(SENSE_PHRASES))

    if memory.memories and rng.random() < 0.35:
        remembered = rng.choice(memory.most_salient(limit=3))
        sentences.append(remembered.text)
    elif rng.random() < 0.45:
        sentences.append(rng.choice(MOOD_FRAGMENTS))

    if rng.random() < 0.3:
        sentences.append(rng.choice(ACTION_PHRASES))

    if temperament and rng.random() < 0.2:
        sentences.append(rng.choice(temperament))

    return sentences[: rng.randint(1, 3)]
