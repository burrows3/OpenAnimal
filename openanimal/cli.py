"""Command-line entry point for OpenAnimal."""

from __future__ import annotations

import argparse
import json

from .agent import LifeAgent
from .simulator import Simulator
from .storage import list_agents, load_agent, save_agent


def _cmd_birth() -> None:
    agent = LifeAgent.birth()
    save_agent(agent)
    print(agent.animal_id)


def _cmd_list() -> None:
    for animal_id in list_agents():
        print(animal_id)


def _cmd_observe(animal_id: str) -> None:
    agent = load_agent(animal_id)
    rendered = agent.timeline.render(current_tick=agent.age_ticks)
    for line in rendered:
        print(line)


def _cmd_state(animal_id: str) -> None:
    agent = load_agent(animal_id)
    payload = {
        "animal_id": agent.animal_id,
        "age_ticks": agent.age_ticks,
        "phase": agent.phase,
        "state": agent.state,
        "pressure": agent.pressure,
    }
    print(json.dumps(payload, indent=2))


def _cmd_tick(ticks: int) -> None:
    simulator = Simulator()
    report = simulator.run(ticks=ticks)
    print(f"ticks={report.ticks} expressions={report.expressions}")


def main() -> None:
    parser = argparse.ArgumentParser(description="OpenAnimal CLI")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("birth", help="Birth a new animal")
    sub.add_parser("list", help="List animals")

    observe = sub.add_parser("observe", help="Observe an animal timeline")
    observe.add_argument("animal_id")

    state = sub.add_parser("state", help="View animal state summary")
    state.add_argument("animal_id")

    tick = sub.add_parser("tick", help="Advance simulation time")
    tick.add_argument("--ticks", type=int, default=1)

    args = parser.parse_args()

    if args.command == "birth":
        _cmd_birth()
    elif args.command == "list":
        _cmd_list()
    elif args.command == "observe":
        _cmd_observe(args.animal_id)
    elif args.command == "state":
        _cmd_state(args.animal_id)
    elif args.command == "tick":
        _cmd_tick(args.ticks)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
