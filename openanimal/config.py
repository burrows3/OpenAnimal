"""Configuration values for OpenAnimal."""

TICK_SECONDS = 60

# Species available for new births.
SPECIES = [
    "bird",
    "fox",
    "lizard",
    "owl",
    "snail",
    "turtle",
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

# Pressure builds so agents become eligible to express occasionally
PRESSURE_BASE_GROWTH = 0.004
PRESSURE_TOLERANCE_BASE = 0.62
PRESSURE_TOLERANCE_VARIANCE = 0.15

# Posting is rare; most ticks are silent
EXPRESSION_COOLDOWN_TICKS = 18

# Action selection probabilities per tick
ACTION_PROBS = {
    "silent": 0.70,
    "observe": 0.20,
    "internal": 0.07,
    "express": 0.03,
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
TICK_INTERVAL_MIN = 300
TICK_INTERVAL_MAX = 1800
TICKS_PER_INTERVAL = 1
