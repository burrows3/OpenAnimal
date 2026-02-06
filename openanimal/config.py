"""Configuration values for OpenAnimal."""

TICK_SECONDS = 60

PHASE_THRESHOLDS = {
    "infancy": 0,
    "early_growth": 500,
    "adolescence": 2000,
    "maturity": 5000,
}

STATE_KEYS = [
    "energy",
    "alertness",
    "curiosity",
    "stress",
    "comfort",
    "restlessness",
    "familiarity",
]

STATE_DRIFT = {
    "energy": 0.002,
    "alertness": 0.002,
    "curiosity": 0.003,
    "stress": 0.002,
    "comfort": 0.002,
    "restlessness": 0.003,
    "familiarity": 0.001,
}

STATE_BOUNDS = (0.0, 1.0)

# Pressure builds so agents become eligible to express regularly
PRESSURE_BASE_GROWTH = 0.008
PRESSURE_TOLERANCE_BASE = 0.55
PRESSURE_TOLERANCE_VARIANCE = 0.12

# Tuned so agents post often enough to see a live feed (Moltbook-style)
EXPRESSION_BASE_PROB = 0.32
EXPRESSION_COOLDOWN_TICKS = 12

MEMORY_DECAY_RATE = 0.0015
MEMORY_MIN_WEIGHT = 0.05
MEMORY_EARLY_BONUS_TICKS = 500

ARCHIVE_INTERVAL_TICKS = 1200
