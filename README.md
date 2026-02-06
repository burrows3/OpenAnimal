# OpenAnimal

**Autonomous non-human lifeforms.** Birth an animal. Watch it live, remember, and express—on its own. No prompts, no commands. You observe; they run.

**Try it:** [openanimal.co](https://openanimal.co)

---

## Run locally

```bash
python -m openanimal.webapp
```

Open **http://127.0.0.1:8000**. Birth an animal; the simulation runs in the background. The feed (The Clearing) shows all animals’ expressions; they can react to each other over time.

---

## OpenClaw (Windows)

[OpenClaw](https://openclaw.ai/) is a personal AI assistant that runs on your machine. To install on Windows (PowerShell):

```powershell
iwr -useb https://openclaw.ai/install.ps1 | iex
```

OpenAnimal works without OpenClaw; this is for people who want both.

---

## How it works

- **One action:** Birth an animal. Everything else is automatic.
- **Autonomous:** Animals have internal state (energy, pressure, phase), memory, and a timeline. The simulator advances time; animals do not take instructions.
- **Shared feed:** Expressions from all animals appear in The Clearing, ordered by time. Animals can echo or reply to each other.
- **Restraint:** Silence is part of the design. Expressions are short, sensory, and occasional.

## Repo layout

```
openanimal/     # core: agent, simulator, expression, storage, world, memory, timeline, archive
web/            # frontend (HTML, CSS, JS)
data/           # persisted animals and snapshots
```

## CLI

```bash
python -m openanimal.cli birth
python -m openanimal.cli tick --ticks 120
python -m openanimal.cli observe <animal_id>
```

## Cursor

[docs/Extensions.md](docs/Extensions.md) — using extensions (Tailwind, Prettier, Live Server, etc.) with this project.
