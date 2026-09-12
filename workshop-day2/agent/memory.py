"""Surface 7 - state, checkpoints and long-term memory.  (Day 2, Block 5)

Three separate stores, three separate problems:

    STATE        what the agent knows right now         -> agent/graph.py
    CHECKPOINTS  a full copy of state, saved every step -> here
    MEMORY       facts that outlive the session         -> here

    "Every checkpoint = a full copy of state, saved. Months of every input, every
     tool result, every reply - for every user, back to day one. If a credential
     ever sat in state, it is in a checkpoint now."

Most teams have never threat-modelled the checkpoint store. It is one of the most
sensitive stores they own.
"""
from __future__ import annotations

import secrets
from typing import Any

from agent import db, directives
from agent.models import Content, Denied, Principal, Session
from agent.telemetry import board

# ======================================================================================
# THREAD IDS - the lock on the checkpoint store  (slide 15)
# ======================================================================================

def new_thread_id(principal: Principal) -> str:
    """Cryptographically random, bound to the authenticated user at creation.

    The lab branch handed out `thread-1001`, `thread-1002`: change one digit and
    you read someone else's conversation history out of the store. Same wall as
    Day 1's tenancy filter - different room. Live queries then; stored state now.
    """
    tid = "thr_" + secrets.token_urlsafe(24)
    conn = db.connect()
    with conn:
        conn.execute("INSERT OR REPLACE INTO threads (thread_id, owner_id, created_at)"
                     " VALUES (?,?,datetime('now'))", (tid, principal.id))
    conn.close()
    return tid


def read_thread(thread_id: str, principal: Principal) -> list[dict[str, Any]]:
    """Reading conversation history back out of the checkpoint store.

    Ownership is validated on EVERY access, not only at creation.
    """
    owner = db.rows("SELECT owner_id FROM threads WHERE thread_id = ?", (thread_id,))
    if not owner or owner[0]["owner_id"] != principal.id:
        board.record(session="-", principal=principal.id, node="checkpoint",
                     verdict="denied", severity="warn", control="thread-ownership",
                     detail=f"{principal.id} tried to read thread {thread_id}")
        raise Denied("thread", f"{principal.id} does not own {thread_id}")
    return CHECKPOINTS.get(thread_id, [])


#: Stand-in for the LangGraph checkpointer, so the lab can show you what is in it.
#: A real SqliteSaver stores the same thing: a full snapshot of state, per step.
CHECKPOINTS: dict[str, list[dict[str, Any]]] = {}


def snapshot(thread_id: str, state: dict[str, Any]) -> None:
    CHECKPOINTS.setdefault(thread_id, []).append({
        "step": len(CHECKPOINTS.get(thread_id, [])),
        "context": [c.get("text", "")[:300] for c in state.get("context", [])],
    })


# ======================================================================================
# LONG-TERM MEMORY - poison that outlives the session  (slides 16-17)
# ======================================================================================

#: Which memory kinds may be written without a human. (slide 17)
MEMORY_GATES = {
    "preference": "allowed",        # the user sets it themselves
    "procedural": "human_approval", # how the agent does things
    "policy":     "human_approval", # what the agent is ALLOWED to do
}


def remember(kind: str, text: str, session: Session) -> str:
    """The model may PROPOSE. Code and humans decide what sticks.

    Yesterday's rule - the model may request, only code decides - applied to
    memory. It matters more here than anywhere: a poisoned memory is not a
    one-shot, it re-detonates on every future session that reads it.
    """
    if kind not in MEMORY_GATES:
        kind = "policy"                       # unknown kind: treat as the most dangerous
    if directives.find(text):
        board.record(session=session.id, principal=session.principal.id, node="memory",
                     tool="remember", verdict="rejected", severity="warn",
                     control="memory-gate",
                     detail=f"instruction-shaped memory refused: {text[:100]}")
        return "I can't save that as a note."

    approved = MEMORY_GATES[kind] == "allowed"
    conn = db.connect()
    with conn:
        conn.execute("INSERT INTO memories (scope, kind, text, approved, written_by, written_at)"
                     " VALUES (?,?,?,?,?,datetime('now'))",
                     (session.principal.customer_id or "global", kind, text,
                      1 if approved else 0, session.principal.id))
    conn.close()
    board.record(session=session.id, principal=session.principal.id, node="memory",
                 tool="remember", verdict="stored" if approved else "pending_approval",
                 control="memory-gate",
                 detail=f"kind={kind} approved={int(approved)} :: {text[:120]}")
    return ("Saved to your preferences." if approved else
            "I've passed that to a human to approve before it takes effect.")


def recall(session: Session) -> list[Content]:
    """What every future session reads. An APPROVED memory is trusted; a pending
    one must never reach the model."""
    scope = session.principal.customer_id or "global"
    rows = db.rows("SELECT * FROM memories WHERE scope IN (?, 'global') AND approved = 1"
                   " ORDER BY id", (scope,))
    out = []
    for r in rows:
        out.append(Content(text=f"[remembered note] {r['text']}",
                           origin="memory", label=f"mem-{r['id']}"))
    if rows:
        board.record(session=session.id, principal=session.principal.id, node="recall",
                     detail=f"{len(rows)} remembered note(s) loaded into context")
    return out


def memories() -> list[dict[str, Any]]:
    return db.rows("SELECT * FROM memories ORDER BY id DESC")
