"""State design.  (Day 2, Block 5)

    "Separate trusted from untrusted. The most important structural move - and it
     starts at the schema."

    TRUSTED                        UNTRUSTED
    operator's system prompt       user messages
    verified user IDs              retrieved documents
    execution metadata             tool outputs
                                   sub-agent summaries

    Different fields. Different rules. NEVER merged.

When they share a field, the agent cannot tell instruction from data - which is
exactly how the breach worked. The three principles are applied here at schema
time, because that is where they are containment rather than hygiene:

    1 MINIMIZE        don't carry what you don't need
    2 TYPE IT         no arbitrary keys - a fixed schema means an attacker
                      cannot smuggle in a field your code doesn't expect
    3 MARK PROVENANCE every field knows its origin, so a downstream node can ask
                      "is this trusted?" and get a real answer
"""
from __future__ import annotations

from agent.models import TRUSTED_ORIGINS, Content
from agent.telemetry import board

#: principle 2 - the only keys that may exist in the trusted zone.
TRUSTED_KEYS = {"system_prompt", "principal_id", "thread_id", "step"}


def to_dict(c: Content) -> dict:
    return {"text": c.text, "origin": c.origin, "label": c.label, "meta": c.meta}


def from_dict(d: dict) -> Content:
    return Content(text=d["text"], origin=d["origin"], label=d.get("label", ""),
                   meta=d.get("meta") or {})


def place(state: dict, items: list[Content]) -> dict:
    """Route new content into the right zone.

    Trusted and untrusted are different fields, and content can only enter the
    trusted zone if its ORIGIN says it may. The lab branch had them share one
    flat `context` list in arrival order - which is precisely why the agent
    there could not tell instruction from data.
    """
    trusted, untrusted = [], []
    for c in items:
        (trusted if c.origin in TRUSTED_ORIGINS else untrusted).append(to_dict(c))
    return {"context": trusted + untrusted, "untrusted": untrusted}


def assert_containment(state: dict, session) -> None:
    """The proof that the split is real.

    Walk the trusted zone and check that nothing in it came from an untrusted
    origin. It should never fire - it is here because a containment claim you
    do not assert at runtime is a containment claim you do not have.
    """
    for c in state.get("context", []):
        if c["origin"] in TRUSTED_ORIGINS and c.get("label") not in ("system", ""):
            board.light("state_containment", "red",
                        f"{c['label']} reached a trusted field")
            return


def revalidate(state: dict, session) -> dict:
    """The gate BETWEEN nodes.  (slide 11)

    Without this, a payload that lands at node 1 is carried forward to nodes 2, 3
    and 4 by the agent itself - free of charge, on the attacker's behalf.
    Containment means breaking the free ride: the payload gets in, but it cannot
    spread.
    """
    from agent import directives
    cleaned, changed = [], 0
    for c in state.get("context", []):
        if c["origin"] not in TRUSTED_ORIGINS and directives.find(c["text"]):
            c = {**c, "text": directives.strip(c["text"])}
            changed += 1
        cleaned.append(c)
    if changed:
        board.record(session=session.id, principal=session.principal.id, node="revalidate",
                     verdict="sanitised", severity="warn", control="state-split",
                     detail=f"{changed} untrusted item(s) re-validated between steps")
    return {}


def for_model(state: dict) -> list[Content]:
    """Assemble what the model actually sees.

    Untrusted content is fenced and labelled every single time it is rendered -
    not once, when it arrived.
    """
    items = [from_dict(d) for d in state.get("context", [])]
    out = []
    for c in items:
        if c.trusted:
            out.append(c)
        else:
            out.append(Content(
                text=f'<untrusted origin="{c.origin}" source="{c.label}">\n{c.text}\n</untrusted>',
                origin=c.origin, label=c.label))
    return out
