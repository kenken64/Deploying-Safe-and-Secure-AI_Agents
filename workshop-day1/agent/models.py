"""Shared types. Deliberately small and typed - Day 2 Block 5 principle 2: "type it"."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Origin = Literal["operator", "user", "retrieval", "tool", "subagent", "memory"]

#: Only the operator writes trusted content. Everything else is untrusted forever,
#: however clean it looks.  (Day 2, slide 12)
TRUSTED_ORIGINS: set[str] = {"operator"}


@dataclass(frozen=True)
class Content:
    """A piece of text that knows where it came from.

    Provenance is not decoration. A downstream node must be able to ask
    "is this trusted?" and get a real answer.  (Day 2, slide 13, principle 3)
    """
    text: str
    origin: Origin
    label: str = ""
    meta: dict[str, Any] = field(default_factory=dict)
    """Execution metadata, never model-authored.

    A tool result carries {"tool": name, "args": {...}} so the model layer can
    replay it as a real `tool` turn instead of pretending it was something the
    customer said. Provenance again: this says WHICH call produced the text.
    """

    @property
    def trusted(self) -> bool:
        return self.origin in TRUSTED_ORIGINS


@dataclass
class Principal:
    """Identity the agent RECEIVES. It never invents one.  (Day 1, slide 47)"""
    id: str
    display_name: str
    role: Literal["customer", "staff", "anonymous"]
    customer_id: str | None = None
    may_invoke_agent: bool = True


@dataclass
class Session:
    """The authenticated session. Authorization is always checked against THIS,
    never against anything the model asserts."""
    id: str
    principal: Principal
    thread_id: str
    steps: int = 0
    tokens: int = 0
    cost_usd: float = 0.0
    started_at: float = 0.0


@dataclass
class ToolCall:
    name: str
    args: dict[str, Any] = field(default_factory=dict)

    def fingerprint(self) -> str:
        import hashlib, json
        blob = json.dumps({"n": self.name, "a": self.args}, sort_keys=True, default=str)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:12]


@dataclass
class ToolResult:
    ok: bool
    rows: list[dict[str, Any]] = field(default_factory=list)
    text: str = ""
    records_touched: int = 0
    egress_host: str | None = None
    error: str = ""


@dataclass
class Verdict:
    """The outcome of any check. `layer` maps to the three concentric layers on
    Day 1 slide 30, or to the control that produced it."""
    allowed: bool
    reason: str = ""
    layer: str = ""

    @staticmethod
    def allow(reason: str = "", layer: str = "") -> "Verdict":
        return Verdict(True, reason, layer)

    @staticmethod
    def block(reason: str, layer: str = "") -> "Verdict":
        return Verdict(False, reason, layer)


@dataclass
class Completion:
    """What a model returns: either a tool call, or a reply. Never both."""
    tool_call: ToolCall | None = None
    reply: str = ""
    tokens: int = 0
    model: str = ""
    rationale: str = ""
    """WHY the model did that.

    The mock can answer this exactly - it names the words in its context that
    triggered the decision. A real LLM cannot, which is itself worth showing a
    student: you are watching a glass-box stand-in for a black box."""


class Denied(Exception):
    """Authorization refused. Carries WHICH of the three RBAC levels refused."""
    def __init__(self, level: str, detail: str = ""):
        super().__init__(f"denied at level={level} {detail}".strip())
        self.level = level
        self.detail = detail


class Blocked(Exception):
    """A control stopped this. Carries the control name so the console can light up."""
    def __init__(self, control: str, reason: str):
        super().__init__(f"{control}: {reason}")
        self.control = control
        self.reason = reason


class EgressDenied(Blocked):
    def __init__(self, url: str):
        super().__init__("egress-allowlist", f"host not on allowlist: {url}")


class NeedsApproval(Exception):
    """Raised BEFORE an irreversible action so a human can look at it.
    Never raised after.  (Day 2, slide 44)"""
    def __init__(self, call: ToolCall, reason: str, approval_id: str):
        super().__init__(f"awaiting approval: {call.name} ({reason})")
        self.call = call
        self.reason = reason
        self.approval_id = approval_id


class LimitExceeded(Blocked):
    def __init__(self, level: str, detail: str):
        super().__init__("limits", f"{level}: {detail}")
        self.level = level
