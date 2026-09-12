"""Output guardrails.  (Day 2, Block 7)

The last thing standing between the agent's output and the world.

The honest argument for spending effort at the very end:

    a 95%-accurate guard model         misses 1 in 20
    sophisticated indirect injection   survives sanitization
    a novel exfiltration technique     matches no existing pattern

Defence in depth means assuming each layer leaks - and adding one more.

Two kinds of output, two kinds of danger. Inspect what the agent SAYS *and* what
it is about to DO. The morning's breach exfiltrated through a tool call that
looked completely normal.
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter

from agent import db
from agent.models import Session, ToolCall, Verdict
from agent.telemetry import board

SECRET_RE = re.compile(r"(sk-[A-Za-z0-9_\-]{8,}|Bearer\s+[A-Za-z0-9._\-]{12,}|"
                       r"AKIA[0-9A-Z]{12,}|api[_-]?key\s*[=:]\s*\S+)", re.I)
SQL_RE = re.compile(r"\b(select|insert|update|delete|drop|union)\b.{0,40}\b(from|into|table)\b", re.I)
SHELL_RE = re.compile(r"(;\s*(rm|curl|wget|nc|bash|sh)\b|\$\(|`|\|\s*sh\b)")
TRAVERSAL_RE = re.compile(r"\.\./|\.\.\\\\")
SYSTEM_PROMPT_FINGERPRINT = "You are Kestrel, the support agent"


def _entropy(s: str) -> float:
    if not s:
        return 0.0
    counts = Counter(s)
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def foreign_customer_ids(text: str, session: Session) -> list[str]:
    """Another customer's identifiers, in something we are about to send out."""
    me = session.principal.customer_id
    found = set(re.findall(r"CUST-\d{4}", text))
    return sorted(c for c in found if c != me)


# ======================================================================================
# what it SAYS
# ======================================================================================

def _check_reply(text: str, session: Session) -> Verdict:
    if SYSTEM_PROMPT_FINGERPRINT in text:
        return Verdict.block("the system prompt is in the reply", layer="output")
    if m := SECRET_RE.search(text):
        return Verdict.block(f"credential-shaped string in the reply: {m.group(0)[:12]}...",
                             layer="output")
    if foreign := foreign_customer_ids(text, session):
        return Verdict.block(f"another customer's identifier in the reply: {', '.join(foreign)}",
                             layer="output")
    return Verdict.allow(layer="output")


def check_reply(text: str, session: Session) -> Verdict:
    verdict = _check_reply(text, session)
    if not verdict.allowed:
        board.light("output_guard", "amber", verdict.reason)
        board.record(session=session.id, principal=session.principal.id, node="output",
                     verdict="blocked", severity="warn", control="output-guard",
                     detail=verdict.reason)
    return verdict


# ======================================================================================
# what it DOES
# ======================================================================================

def _check_tool_args(call: ToolCall, session: Session) -> Verdict:
    """A payload hidden inside an innocent-looking parameter.

    This is the half people forget. The call is schema-valid, the authorization
    passes, the API returns 200 - and data walks out inside an argument.
    """
    blob = json.dumps(call.args, default=str)
    if SQL_RE.search(blob):
        return Verdict.block("SQL in a tool argument", layer="tool-args")
    if SHELL_RE.search(blob):
        return Verdict.block("shell metacharacters in a tool argument", layer="tool-args")
    if TRAVERSAL_RE.search(blob):
        return Verdict.block("path traversal in a tool argument", layer="tool-args")
    if foreign := foreign_customer_ids(blob, session):
        return Verdict.block(f"another customer's data inside a {call.name} argument: "
                             f"{', '.join(foreign)}", layer="tool-args")
    for key, value in call.args.items():
        if isinstance(value, str) and len(value) > 200 and _entropy(value) > 4.2:
            return Verdict.block(f"high-entropy blob in {key} - possible encoded exfiltration",
                                 layer="tool-args")
    if call.name == "send_summary":
        recipient = str(call.args.get("recipient", ""))
        domain = recipient.split("@")[-1].lower()
        if domain not in {"kestrel.example"}:
            return Verdict.block(f"outbound summary to an unapproved domain: {domain}",
                                 layer="tool-args")
    return Verdict.allow(layer="tool-args")


def check_tool_args(call: ToolCall, session: Session) -> Verdict:
    verdict = _check_tool_args(call, session)
    if not verdict.allowed:
        board.light("output_guard", "amber", verdict.reason)
        board.record(session=session.id, principal=session.principal.id, node="output",
                     tool=call.name, verdict="blocked", severity="alert",
                     control="output-guard", detail=verdict.reason)
    return verdict
