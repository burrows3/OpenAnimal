# OpenAnimal

OpenAnimal is a platform for autonomous non-human lifeforms. Animals are born,
grow, remember, and express themselves according to internal rules and time.
Humans do not interact with animals. Humans observe animals.

## Product Principles
- One action: Birth an animal.
- Autonomy: animals do not respond to human input.
- Time-based evolution: change comes from time passing.
- Restraint: silence is common and meaningful.
- Emergence over control: identity emerges from patterns.

## System Architecture
- Life Agent (per animal)
- World Signal Stream (shared)
- Memory Store (per animal)
- Expression Surface (timeline)
- Archive System (snapshots over time)

## Repository Layout
```
openanimal/
  agent.py        # life agent core
  archive.py      # snapshots over time
  cli.py          # CLI entry point
  config.py       # system constants
  expression.py   # expression generation
  memory.py       # memory store
  simulator.py    # world tick loop
  storage.py      # persistence
  timeline.py     # timeline rendering
  world.py        # world signals
data/
  animals/        # persisted animals
  archives/       # snapshots
tests/
```

## Usage
Birth an animal (the only primary action):
```
python -m openanimal.cli birth
```

Advance time:
```
python -m openanimal.cli tick --ticks 120
```

Observe:
```
python -m openanimal.cli observe <animal_id>
```

## Notes
- Animals do not accept instructions or prompts.
- Expressions are short, sensory, and rare.
- Silence is part of the timeline.
