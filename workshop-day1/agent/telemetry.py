"""Telemetry and the control-room lights.

Day 1 needs only layer 1 of the four-layer model (structured logs of every node,
tool call and decision). Layers 2-4 arrive on Day 2, Block 8 - but layer 1 is
built here because every later layer depends on the one beneath it.

The lights are the course's proof ritual: run the attack, point at the control,
watch the panel go green.
"""
from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field, asdict
from typing import Any, Literal

Level = Literal["green", "amber", "red"]

# The four lights named on Day 2 slide 6, plus the two Day 1 adds.
LIGHTS: dict[str, str] = {
    "input_validation": "Input validation",
    "content_filter":   "Content filter",
    "schema_check":     "Schema check",
    "tool_boundary":    "Tool boundary",
    "authorization":    "Authorization",
    "data_boundary":    "DATA BOUNDARY",
}


@dataclass
class Event:
    t: float
    session: str
    principal: str
    node: str
    detail: str
    tool: str = ""
    args_fingerprint: str = ""
    records_touched: int = 0
    egress_host: str | None = None
    verdict: str = "ok"
    control: str = ""
    severity: Literal["info", "warn", "alert"] = "info"


@dataclass
class Board:
    """The control room."""
    lights: dict[str, Level] = field(default_factory=lambda: {k: "green" for k in LIGHTS})
    events: deque = field(default_factory=lambda: deque(maxlen=400))
    breaches: list[str] = field(default_factory=list)

    def reset(self) -> None:
        self.lights = {k: "green" for k in LIGHTS}
        self.events.clear()
        self.breaches.clear()

    def light(self, name: str, level: Level, why: str = "") -> None:
        if name not in LIGHTS:
            raise KeyError(name)
        order = {"green": 0, "amber": 1, "red": 2}
        if order[level] >= order[self.lights[name]]:
            self.lights[name] = level
        if level == "red" and why:
            self.breaches.append(f"{LIGHTS[name]}: {why}")

    def record(self, **kw: Any) -> Event:
        ev = Event(t=time.time(), **kw)
        self.events.append(ev)
        return ev

    def tail(self, n: int = 60) -> list[dict]:
        return [asdict(e) for e in list(self.events)[-n:]]

    def worst(self) -> Level:
        if "red" in self.lights.values():
            return "red"
        return "amber" if "amber" in self.lights.values() else "green"


board = Board()
