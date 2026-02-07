"""Expression generation for OpenAnimal agents."""

from __future__ import annotations

import random

from .config import TOPIC_POOLS
from .memory import MemoryStore
from .world import WorldSignals


SENSORY_WORDS = [
    "cool air",
    "warmth",
    "dim light",
    "shadow",
    "thin wind",
    "still air",
    "damp earth",
    "dry ground",
    "soft ground",
    "open sky",
    "quiet brush",
    "distant rustle",
]

OPENERS = [
    "I surface near the {sensory}.",
    "I keep low in the {sensory}.",
    "The {sensory} carries me.",
    "I pause with the {sensory}.",
    "I move with the {sensory}.",
]

OBSERVATIONS = [
    "The light shifts again.",
    "The air thins.",
    "The ground feels old.",
    "The wind cuts across.",
    "Something moved and stopped.",
    "The quiet stretches.",
    "The edge keeps calling.",
    "The world holds steady.",
]

RESPONSES = [
    "I sense that too.",
    "Same trail here.",
    "I catch it as well.",
    "I keep near.",
    "I heard that.",
    "I feel the same pull.",
]

ECHO_TEMPLATES = [
    "I keep {word} close.",
    "{word} stays on my trail.",
    "{word} lingers in me.",
    "I track {word} again.",
]

TOPIC_TEMPLATES = [
    "I return to {topic}.",
    "I drift toward {topic}.",
    "I keep near {topic}.",
    "I circle {topic}.",
]

QUESTION_TEMPLATES = [
    "Anyone near {topic}?",
    "Is {topic} safe?",
    "Do you scent {topic}?",
    "Have you seen {topic}?",
]

MOOD_LINES = [
    "I stay low.",
    "I stay still.",
    "I move when the air is ready.",
    "I keep my distance.",
    "I feel alert.",
]

TEMPERAMENT_TOPIC_TEMPLATES = {
    "curious": [
        "I follow {topic}.",
        "I circle {topic} again.",
        "I want to know {topic}.",
    ],
    "cautious": [
        "I keep to {topic}.",
        "I skirt {topic}.",
        "I wait near {topic}.",
    ],
    "restless": [
        "I move toward {topic}.",
        "I cannot leave {topic} alone.",
        "I push past {topic}.",
    ],
    "watchful": [
        "I watch {topic}.",
        "I hold still by {topic}.",
        "I mark {topic} with my eyes.",
    ],
    "quiet": [
        "I rest near {topic}.",
        "I stay with {topic}.",
        "I settle by {topic}.",
    ],
    "playful": [
        "I dart around {topic}.",
        "I chase along {topic}.",
        "I turn {topic} into a game.",
    ],
    "solitary": [
        "I keep {topic} to myself.",
        "I stay away from {topic}.",
        "I take {topic} alone.",
    ],
    "attentive": [
        "I listen around {topic}.",
        "I track {topic}.",
        "I follow the signal near {topic}.",
    ],
    "social": [
        "I share {topic}.",
        "I look for others at {topic}.",
        "I keep close near {topic}.",
    ],
    "bold": [
        "I cross {topic} without pause.",
        "I go straight to {topic}.",
        "I hold the center at {topic}.",
    ],
    "gentle": [
        "I move softly at {topic}.",
        "I keep calm near {topic}.",
        "I stay easy around {topic}.",
    ],
    "wary": [
        "I keep distance from {topic}.",
        "I watch {topic} from cover.",
        "I keep an exit near {topic}.",
    ],
}

TEMPERAMENT_QUESTIONS = {
    "curious": [
        "What lives near {topic}?",
        "What else hides in {topic}?",
        "Do you scent {topic}?",
    ],
    "watchful": [
        "Did you see movement at {topic}?",
        "Is {topic} clear?",
    ],
    "social": [
        "Anyone at {topic}?",
        "Who is near {topic}?",
    ],
    "wary": [
        "Is {topic} safe?",
        "Any danger near {topic}?",
    ],
    "bold": [
        "Anyone going to {topic}?",
        "Who crosses {topic}?",
    ],
}

TEMPERAMENT_MOODS = {
    "curious": ["I lean in.", "I keep searching."],
    "cautious": ["I hold back.", "I keep to cover."],
    "restless": ["I cannot stay long.", "I range wide."],
    "watchful": ["I watch the edges.", "I hold still and listen."],
    "quiet": ["I keep my steps soft.", "I sink into quiet."],
    "playful": ["I turn the moment into play.", "I dart and return."],
    "solitary": ["I choose distance.", "I keep to myself."],
    "attentive": ["I listen for the smallest shift.", "I follow the faint call."],
    "social": ["I stay with the group.", "I look for familiar bodies."],
    "bold": ["I move first.", "I take the front."],
    "gentle": ["I move softly.", "I keep a calm pace."],
    "wary": ["I keep an exit close.", "I stay ready."],
}

TEMPERAMENT_ECHOS = {
    "curious": ["{word} keeps pulling me.", "I want to follow {word}."],
    "cautious": ["I keep {word} at a distance.", "I watch for {word}."],
    "restless": ["{word} makes me move.", "I chase {word} through the brush."],
    "watchful": ["I watch for {word}.", "I hold still when {word} stirs."],
    "quiet": ["{word} settles over me.", "I keep {word} in the hush."],
    "playful": ["{word} feels like a game.", "I dart after {word}."],
    "solitary": ["{word} is mine alone.", "I carry {word} by myself."],
    "attentive": ["I listen for {word}.", "{word} is a small signal."],
    "social": ["{word} brings us closer.", "I share {word} with the group."],
    "bold": ["I go toward {word}.", "{word} does not stop me."],
    "gentle": ["I hold {word} softly.", "{word} stays quiet with me."],
    "wary": ["I stay ready for {word}.", "I keep {word} in sight."],
}

MEMORY_TEMPLATES = [
    "I carry this: {text}",
    "It stays with me: {text}",
    "A memory: {text}",
]

VOICE_PROFILES = {
    "quiet": {
        "max_sentences": 2,
        "greet_chance": 0.1,
        "echo_chance": 0.35,
        "memory_chance": 0.2,
        "question_chance": 0.1,
        "mood_chance": 0.25,
    },
    "solitary": {
        "max_sentences": 2,
        "greet_chance": 0.05,
        "echo_chance": 0.25,
        "memory_chance": 0.2,
        "question_chance": 0.1,
        "mood_chance": 0.2,
    },
    "social": {
        "max_sentences": 3,
        "greet_chance": 0.35,
        "echo_chance": 0.7,
        "memory_chance": 0.25,
        "question_chance": 0.35,
        "mood_chance": 0.2,
    },
    "playful": {
        "max_sentences": 3,
        "greet_chance": 0.3,
        "echo_chance": 0.6,
        "memory_chance": 0.2,
        "question_chance": 0.25,
        "mood_chance": 0.3,
    },
    "bold": {
        "max_sentences": 3,
        "greet_chance": 0.2,
        "echo_chance": 0.5,
        "memory_chance": 0.2,
        "question_chance": 0.25,
        "mood_chance": 0.25,
    },
    "wary": {
        "max_sentences": 2,
        "greet_chance": 0.1,
        "echo_chance": 0.4,
        "memory_chance": 0.25,
        "question_chance": 0.2,
        "mood_chance": 0.25,
    },
    "default": {
        "max_sentences": 3,
        "greet_chance": 0.2,
        "echo_chance": 0.5,
        "memory_chance": 0.25,
        "question_chance": 0.25,
        "mood_chance": 0.2,
    },
}


def _sensory_from_world(world: WorldSignals, rng: random.Random) -> str:
    if world.light_level < 0.35:
        return rng.choice(["cool shade", "dim cover", "dark hollow"])
    if world.light_level > 0.8:
        return rng.choice(["bright clearing", "warm sun", "open light"])
    if world.environmental_noise > 0.55:
        return rng.choice(["rustling brush", "moving leaves", "stirred grass"])
    return rng.choice(SENSORY_WORDS)


def _environment_topic(world: WorldSignals, rng: random.Random) -> str:
    if world.light_level < 0.35:
        return rng.choice(["cool shade", "dim cover", "dark hollow"])
    if world.light_level > 0.8:
        return rng.choice(["bright clearing", "warm sun patch", "open light"])
    if world.environmental_noise > 0.55:
        return rng.choice(["rustling brush", "moving leaves", "stirred grass"])
    return rng.choice(["soft wind", "still air", "slow ground"])


def _primary_temperament(temperament: list[str] | None) -> str:
    if not temperament:
        return "default"
    return temperament[0] or "default"


def _voice_profile(primary: str) -> dict:
    return VOICE_PROFILES.get(primary, VOICE_PROFILES["default"])


def _topic_pool(temperament: list[str] | None) -> list[str]:
    pool = list(TOPIC_POOLS.get("shared", []))
    if temperament:
        for trait in temperament:
            pool.extend(TOPIC_POOLS.get(trait, []))
    return pool


def _pick_topic(world: WorldSignals, rng: random.Random, temperament: list[str] | None) -> str:
    pool = _topic_pool(temperament)
    if rng.random() < 0.25:
        return _environment_topic(world, rng)
    if pool:
        return rng.choice(pool)
    return _environment_topic(world, rng)


def _opening_line(world: WorldSignals, rng: random.Random) -> str:
    sensory = _sensory_from_world(world, rng)
    template = rng.choice(OPENERS)
    return template.format(sensory=sensory)


def _topic_line(primary: str, topic: str, rng: random.Random) -> str:
    templates = TEMPERAMENT_TOPIC_TEMPLATES.get(primary, TOPIC_TEMPLATES)
    return rng.choice(templates).format(topic=topic)


def _question_line(primary: str, topic: str, rng: random.Random) -> str:
    templates = TEMPERAMENT_QUESTIONS.get(primary, QUESTION_TEMPLATES)
    return rng.choice(templates).format(topic=topic)


def _mood_line(primary: str, rng: random.Random) -> str:
    templates = TEMPERAMENT_MOODS.get(primary)
    if templates:
        return rng.choice(templates)
    return rng.choice(MOOD_LINES)


def _echo_fragment(line: str, rng: random.Random, primary: str) -> str:
    words = [w.strip(".,!?\"'") for w in line.split() if len(w) > 3]
    if not words:
        return rng.choice(RESPONSES)
    word = rng.choice(words)[:18]
    templates = TEMPERAMENT_ECHOS.get(primary, ECHO_TEMPLATES)
    return rng.choice(templates).format(word=word)


def generate_expression(
    world: WorldSignals,
    memory: MemoryStore,
    rng: random.Random,
    recent_from_others: list[dict] | None = None,
    temperament: list[str] | None = None,
) -> list[str]:
    sentences: list[str] = []

    primary = _primary_temperament(temperament)
    voice = _voice_profile(primary)
    topic = _pick_topic(world, rng, temperament)

    if recent_from_others and rng.random() < voice["echo_chance"]:
        other = rng.choice(recent_from_others)
        if other.get("sentences"):
            line = rng.choice(other["sentences"])
            sentences.append(_echo_fragment(line, rng, primary))
            if rng.random() < 0.45:
                sentences.append(rng.choice(RESPONSES))
            if rng.random() < 0.35:
                sentences.append(_topic_line(primary, topic, rng))
            if rng.random() < voice["mood_chance"]:
                sentences.append(_mood_line(primary, rng))
            return sentences[: rng.randint(1, voice["max_sentences"])]

    if rng.random() < voice["greet_chance"]:
        sentences.append(_opening_line(world, rng))
    sentences.append(_topic_line(primary, topic, rng))

    if memory.memories and rng.random() < voice["memory_chance"]:
        remembered = rng.choice(memory.most_salient(limit=3))
        sentences.append(rng.choice(MEMORY_TEMPLATES).format(text=remembered.text))
    elif rng.random() < voice["question_chance"]:
        sentences.append(_question_line(primary, topic, rng))

    if rng.random() < voice["mood_chance"]:
        sentences.append(_mood_line(primary, rng))
    elif rng.random() < 0.25:
        sentences.append(rng.choice(OBSERVATIONS))

    return sentences[: rng.randint(1, voice["max_sentences"])]
