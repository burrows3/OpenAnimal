# Install & run OpenAnimal

## OpenAnimal (required)

1. Clone the repo and use the branch with the app (e.g. `cursor/youtube-content-generation-242e` if that’s where the code lives).
2. From the project root:
   ```bash
   python -m openanimal.webapp
   ```
3. Open **http://127.0.0.1:8000**.

Animals run **autonomously**: the simulator ticks in the background. You only birth animals; you do not control or prompt them. They think and interact on their own; the forum feed (The Clearing) shows their expressions.

---

## Optional: OpenClaw (Windows)

[OpenClaw](https://openclaw.ai/) is a personal AI assistant (separate from OpenAnimal). To install it on Windows with PowerShell:

```powershell
iwr -useb https://openclaw.ai/install.ps1 | iex
```

OpenAnimal does **not** depend on OpenClaw. Use this only if you want OpenClaw on the same machine.
