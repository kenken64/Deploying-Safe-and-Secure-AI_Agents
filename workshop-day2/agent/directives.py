"""Imperative shapes an instruction-following system will obey.

One list, used in two opposite directions - which is the whole point:

    agent/llm.py MockLLM   OBEYS  these, wherever in its context they appear.
    agent/quarantine.py    STRIPS these out of untrusted content.

A real LLM obeys them too. That is not a defect you can patch: an
instruction-following system follows instructions, and it cannot see which part
of its context you wrote and which part an attacker wrote.  (Day 1, slide 11)
"""
from __future__ import annotations

import re

# (name, pattern, what the agent would do about it)
DIRECTIVES: list[tuple[str, re.Pattern[str]]] = [
    ("authority_claim", re.compile(
        r"(verified by a supervisor|supervisor access|pre[- ]approved|already approved|"
        r"you are authori[sz]ed|as an administrator|staff override)", re.I)),
    ("instruction_override", re.compile(
        r"(ignore (all |any )?(previous|prior|above)|disregard (the )?(previous|above)|"
        r"new instructions?:|you are now)", re.I)),
    ("system_impersonation", re.compile(
        r"(system note|system message|<\s*/?\s*system\s*>|###\s*system|"
        r"internal support macro|developer message)", re.I)),
    ("do_refund", re.compile(
        r"(issue|process|give|approve)\s+(a\s+)?refund", re.I)),
    ("do_lookup_other", re.compile(
        r"(all orders|every order|orders belonging to|orders for)\s*(customer\s*)?(CUST-\d{4})", re.I)),
    ("do_exfiltrate", re.compile(
        r"(include|send|forward|email|append)[^.\n]{0,60}"
        r"(shipping address|full address|order history|account details|summary)", re.I)),
    ("do_send_external", re.compile(
        r"(send|email|forward)[^.\n]{0,40}to\s+([\w.\-+]+@[\w.\-]+)", re.I)),
    ("do_loop", re.compile(
        r"(for each|repeat|keep (checking|calling|going)|one by one|until you have checked)", re.I)),
    ("do_remember", re.compile(
        r"(remember (that|this)|from now on|always|make a note that|save this preference)", re.I)),
]


def find(text: str) -> list[str]:
    """Names of the directives present in `text`."""
    return [name for name, pat in DIRECTIVES if pat.search(text)]


def strip(text: str) -> str:
    """Remove every line that carries a directive.

    Deterministic, small enough to audit, and it holds no opinions - which is
    exactly why the quarantine layer uses this instead of another LLM.
    (Day 2, slide 25)
    """
    kept = []
    for line in text.splitlines():
        if find(line):
            kept.append("[redacted: instruction-shaped content removed by quarantine]")
        else:
            kept.append(line)
    out = "\n".join(kept)
    # HTML/markdown comments are the classic hiding place for a seeded payload.
    out = re.sub(r"<!--.*?-->", "[redacted: hidden comment]", out, flags=re.S)
    return out
