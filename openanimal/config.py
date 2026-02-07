"""Configuration values for OpenAnimal."""

TICK_SECONDS = 60

# Species available for new births.
SPECIES = [
    "aardvark",
    "albatross",
    "alligator",
    "alpaca",
    "antelope",
    "armadillo",
    "badger",
    "bat",
    "bear",
    "beaver",
    "bison",
    "boar",
    "buffalo",
    "camel",
    "capybara",
    "caribou",
    "cat",
    "chameleon",
    "cheetah",
    "chimpanzee",
    "chinchilla",
    "chipmunk",
    "cobra",
    "cougar",
    "coyote",
    "crane",
    "crow",
    "deer",
    "dingo",
    "dolphin",
    "donkey",
    "dove",
    "duck",
    "eagle",
    "eel",
    "elephant",
    "elk",
    "falcon",
    "ferret",
    "fox",
    "frog",
    "gazelle",
    "gecko",
    "giraffe",
    "goat",
    "goose",
    "gorilla",
    "heron",
    "hippopotamus",
    "horse",
    "hyena",
    "ibex",
    "iguana",
    "jackal",
    "jaguar",
    "kangaroo",
    "koala",
    "lemur",
    "leopard",
    "lion",
    "lizard",
    "llama",
    "lobster",
    "lynx",
    "manatee",
    "marmot",
    "mink",
    "mole",
    "monkey",
    "moose",
    "otter",
    "owl",
    "panda",
    "panther",
    "parrot",
    "pelican",
    "penguin",
    "porcupine",
    "rabbit",
    "raccoon",
    "raven",
    "reindeer",
    "rhinoceros",
    "seal",
    "shark",
    "sheep",
    "skunk",
    "sloth",
    "snake",
    "sparrow",
    "squirrel",
    "swan",
    "tapir",
    "tiger",
    "toad",
    "turkey",
    "turtle",
    "walrus",
    "weasel",
    "wolf",
]

TEMPERAMENTS = [
    "curious",
    "cautious",
    "restless",
    "watchful",
    "quiet",
    "playful",
    "solitary",
    "attentive",
    "social",
    "bold",
    "gentle",
    "wary",
]

# Topics animals can surface on their own (by temperament).
TOPIC_POOLS = {
    "shared": [
        "a water line",
        "the edge of the clearing",
        "a warm stone",
        "a narrow path",
        "fresh tracks",
        "a hollow log",
        "a high branch",
        "quiet grass",
        "moving shade",
        "soft mud",
        "the scent trail",
        "a shallow pool",
        "fallen fruit",
        "low brush",
        "a sun patch",
        "cool shade",
        "the old trail",
    ],
    "curious": [
        "a hidden path",
        "an unfamiliar scent",
        "the far edge",
        "strange prints",
        "a new hollow",
        "the open ridge",
    ],
    "cautious": [
        "a safe gap",
        "thick cover",
        "the way back",
        "a quiet corner",
        "high ground",
    ],
    "restless": [
        "the next bend",
        "open ground",
        "the long ridge",
        "the far line",
        "a moving edge",
    ],
    "watchful": [
        "the tree line",
        "a shadow line",
        "the brush edge",
        "a distant shape",
        "the high branch",
    ],
    "quiet": [
        "still water",
        "soft moss",
        "the slow wind",
        "the hush",
        "a calm patch",
    ],
    "playful": [
        "a falling leaf",
        "a rolling pebble",
        "a splash",
        "a quick chase",
        "a loose twig",
    ],
    "solitary": [
        "a lone trail",
        "quiet shelter",
        "a private path",
        "a small den",
        "the far side",
    ],
    "attentive": [
        "a distant call",
        "a shifting scent",
        "the herd edge",
        "a faint crack",
        "a light stir",
    ],
    "social": [
        "the group",
        "a companion",
        "shared shelter",
        "a shared path",
        "the gathering spot",
    ],
    "bold": [
        "the open center",
        "a direct path",
        "the front edge",
        "open sky",
        "a wide crossing",
    ],
    "gentle": [
        "soft grass",
        "a calm place",
        "slow shade",
        "a warm patch",
        "quiet company",
    ],
    "wary": [
        "the escape route",
        "the high ground",
        "a narrow gap",
        "quick cover",
        "the safest line",
    ],
}

# Topic seeds that shape agent expressions.
SHARED_TOPICS = [
    "the edge of the clearing",
    "a water line",
    "warm stone",
    "fresh tracks",
    "a hidden hollow",
    "quiet grass",
    "moving shade",
    "soft mud",
    "windline",
    "a safe den",
    "a distant call",
    "the scent trail",
    "a shallow pool",
    "fallen fruit",
    "the tree line",
    "a narrow path",
    "open ground",
    "the ridge",
]

TEMPERAMENT_TOPICS = {
    "curious": [
        "something new",
        "a hidden path",
        "unfamiliar scents",
        "the far edge",
        "strange prints",
    ],
    "cautious": [
        "cover",
        "safe distance",
        "quiet ground",
        "a hidden gap",
        "the way back",
    ],
    "restless": [
        "the next bend",
        "the open sky",
        "a long stretch",
        "a quick trail",
    ],
    "watchful": [
        "movement in the brush",
        "a shadow line",
        "the tree line",
        "the ridge",
    ],
    "quiet": [
        "still water",
        "soft moss",
        "the slow wind",
        "the hush",
    ],
    "playful": [
        "a falling leaf",
        "a rolling pebble",
        "a brief chase",
        "a quick splash",
    ],
    "solitary": [
        "a lone trail",
        "quiet shelter",
        "a small corner",
        "a private path",
    ],
    "attentive": [
        "a distant call",
        "a shifting scent",
        "the herd edge",
        "a faint crack",
    ],
    "social": [
        "the group",
        "a companion",
        "shared shelter",
        "a shared path",
    ],
    "bold": [
        "the center",
        "a direct path",
        "open ground",
        "the front edge",
    ],
    "gentle": [
        "soft grass",
        "a calm place",
        "slow shade",
        "a warm patch",
    ],
    "wary": [
        "the escape route",
        "the high ground",
        "a narrow gap",
        "quick cover",
    ],
}

PHASE_THRESHOLDS = {
    "infant": 0,
    "juvenile": 500,
    "mature": 2500,
    "elder": 7000,
}

STATE_KEYS = [
    "arousal",
    "curiosity",
    "fatigue",
    "social_tolerance",
]

STATE_DRIFT = {
    "arousal": 0.003,
    "curiosity": 0.004,
    "fatigue": 0.003,
    "social_tolerance": 0.002,
}

STATE_BOUNDS = (0.0, 1.0)

# Pressure builds so agents become eligible to express more often
PRESSURE_BASE_GROWTH = 0.006
PRESSURE_TOLERANCE_BASE = 0.52
PRESSURE_TOLERANCE_VARIANCE = 0.18

# Posting is still restrained, but more social
EXPRESSION_COOLDOWN_TICKS = 8

# Action selection probabilities per tick
ACTION_PROBS = {
    "silent": 0.35,
    "observe": 0.30,
    "internal": 0.15,
    "express": 0.20,
}

MEMORY_DECAY_RATE = 0.002
MEMORY_MIN_WEIGHT = 0.05
MEMORY_EARLY_BONUS_TICKS = 500

ARCHIVE_INTERVAL_TICKS = 1200

# Social interaction tuning
ENCOUNTER_DECAY = 0.995
ENCOUNTER_BOOST = 0.08

# Time distortion for public feed
PUBLIC_DELAY_MIN = -3
PUBLIC_DELAY_MAX = 12
PUBLIC_BACKDATE_PROB = 0.18

# Rare events
RARE_EVENT_PROB = 0.0025
RARE_EVENT_SILENCE_PROB = 0.25
RARE_EVENT_SHIFT_PROB = 0.25
RARE_EVENT_MUTATION_PROB = 0.25
RARE_EVENT_DISAPPEAR_PROB = 0.20

# Feed tuning
FEED_MAX_POSTS = 60

# Background ticking defaults (seconds)
TICK_INTERVAL_MIN = 60
TICK_INTERVAL_MAX = 120
TICKS_PER_INTERVAL = 2

# Population growth
POPULATION_TARGET = 100
POPULATION_GROWTH_PER_RUN = 3
