"""Timeline presentation for OpenAnimal expressions."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ExpressionEntry:
    tick: int
    sentences: list[str]


@dataclass
class Timeline:
    expressions: list[ExpressionEntry] = field(default_factory=list)

    def add_expression(self, tick: int, sentences: list[str]) -> None:
        self.expressions.append(ExpressionEntry(tick=tick, sentences=sentences))

    def render(self, current_tick: int, silence_marker: str = "...") -> list[str]:
        rendered: list[str] = []
        last_tick = 0
        for entry in self.expressions:
            gap = entry.tick - last_tick
            if gap > 0:
                rendered.append(f"{silence_marker} ({gap} ticks of silence)")
            rendered.extend(entry.sentences)
            last_tick = entry.tick

        final_gap = current_tick - last_tick
        if final_gap > 0:
            rendered.append(f"{silence_marker} ({final_gap} ticks of silence)")
        return rendered
