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

# Humanlike chatter and observations.
GREETINGS = [
    "Hey.",
    "Hi.",
    "Hello.",
    "Anyone else here?",
    "I noticed you.",
    "I heard something.",
]

CHECK_INS = [
    "I'm feeling restless today.",
    "I'm a little calm right now.",
    "I don't know why, but I'm alert.",
    "I'm drifting through this.",
    "I'm not sure what I'm waiting for.",
]

OBSERVATIONS = [
    "The light keeps changing.",
    "The air feels different.",
    "I keep circling back.",
    "I saw movement and paused.",
    "The quiet got louder somehow.",
    "Everything feels close and far at once.",
]

RESPONSES = [
    "Same here.",
    "I get that.",
    "Yeah, I felt that too.",
    "I hear you.",
    "That makes sense.",
    "I'm with you.",
]

QUESTION_ENDINGS = [
    "Are you okay?",
    "Do you feel that too?",
    "Is that just me?",
    "Did you notice it?",
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
        return rng.choice(RESPONSES)
    word = rng.choice(words)[:18]
    templates = [
        f"I keep thinking about {word}.",
        f"{word} is sticking with me.",
        f"That {word} feeling again.",
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

    if recent_from_others and rng.random() < 0.65:
        other = rng.choice(recent_from_others)
        if other.get("sentences"):
            line = rng.choice(other["sentences"])
            sentences.append(_echo_fragment(line, rng))
            if rng.random() < 0.6:
                sentences.append(rng.choice(RESPONSES))
            if rng.random() < 0.35:
                sentences.append(rng.choice(OBSERVATIONS))
            return sentences[: rng.randint(1, 3)]

    if rng.random() < 0.4:
        sentences.append(rng.choice(GREETINGS))
    if rng.random() < 0.5:
        sentences.append(rng.choice(CHECK_INS))
    else:
        sentences.append(rng.choice(OBSERVATIONS))

    if memory.memories and rng.random() < 0.4:
        remembered = rng.choice(memory.most_salient(limit=3))
        sentences.append(f"I remember: {remembered.text}")
    elif rng.random() < 0.35:
        sentences.append(rng.choice(QUESTION_ENDINGS))

    if temperament and rng.random() < 0.2:
        sentences.append(f"I'm feeling {rng.choice(temperament)}.")

    return sentences[: rng.randint(1, 3)]
