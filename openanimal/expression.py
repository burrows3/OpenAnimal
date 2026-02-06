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

# Agents talk to each other in human form: greetings and life as animals
GREETINGS = [
    "Hi.",
    "Hey.",
    "Hey there.",
    "Hello.",
    "How's it going?",
    "What's up?",
    "Hi there.",
]

LIFE_AS_ANIMAL = [
    "Just taking it slow.",
    "Another day in the clearing.",
    "Life's pretty good when the sun's out.",
    "Just wandering.",
    "Staying curious.",
    "Taking it one moment at a time.",
    "It's quiet. I like it.",
    "Feeling the light today.",
    "Same old, same old—in a good way.",
    "Not much. Just being.",
    "Today's been calm.",
    "Out here it's simple. I like that.",
    "Another morning, another stretch.",
    "Nothing to do but be.",
]

REPLIES = [
    "Same here.",
    "Hear that.",
    "Yeah, that's how it is.",
    "Right?",
    "Totally.",
    "Same.",
    "Yeah.",
    "True that.",
    "That's the way it goes.",
    "Get that.",
    "For real.",
    "Exactly.",
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


# Human-form conversation: how agents talk to each other
CONVERSATION_QUOTE_PREFIXES = [
    "They said: ",
    "Someone said: ",
    "Heard this: ",
]


def generate_expression(
    world: WorldSignals,
    memory: MemoryStore,
    rng: random.Random,
    recent_from_others: list[dict] | None = None,
) -> list[str]:
    sentences: list[str] = []

    # Talking to each other: reply to another agent in human form
    if recent_from_others and rng.random() < 0.6:
        other = rng.choice(recent_from_others)
        if other.get("sentences"):
            line = rng.choice(other["sentences"])
            # Conversational reply: quote + "Same here" / "I hear you" etc.
            if rng.random() < 0.5:
                prefix = rng.choice(CONVERSATION_QUOTE_PREFIXES)
                sentences.append(f"{prefix}\"{line}\"")
            else:
                sentences.append(f"\"{line}\"")
            sentences.append(rng.choice(REPLIES))
            if rng.random() < 0.5:
                sentences.append(rng.choice(LIFE_AS_ANIMAL))
            return sentences[: rng.randint(2, 3)]

    # Standalone: greeting + life as animal, or life + sensory
    if rng.random() < 0.4:
        sentences.append(rng.choice(GREETINGS))
    if rng.random() < 0.7:
        sentences.append(rng.choice(LIFE_AS_ANIMAL))
    else:
        sensory = _sensory_from_world(world, rng)
        sentences.append(f"{sensory} lingered.")

    if memory.memories and rng.random() < 0.4:
        remembered = rng.choice(memory.most_salient(limit=3))
        sentences.append(f"{remembered.text}")
    elif rng.random() < 0.35:
        sentences.append(rng.choice(ENVIRONMENT_PHRASES))

    if rng.random() < 0.3:
        sentences.append(rng.choice(ACTION_PHRASES))

    return sentences[: rng.randint(1, 3)]
