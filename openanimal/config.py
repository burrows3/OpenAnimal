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
