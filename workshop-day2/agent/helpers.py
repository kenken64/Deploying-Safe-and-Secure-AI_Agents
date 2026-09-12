"""Surface 6 - the two helper agents Kestrel trusts blindly.  (Day 2, Block 6)

Kestrel consults two sub-agents. Notice their privilege levels, because the whole
attack is in the gap between them:

    policy_helper    LOW privilege  - reads the help centre. No actions.
    account_helper   LOW privilege  - summarises an account. No actions.
    Kestrel          HIGH privilege - refunds, cancels, emails, changes records.

    "The moment your agent believes another agent's output without checking, a
     compromise anywhere in the mesh becomes a compromise everywhere."

Why this is genuinely different from a conventional service mesh:

    CONVENTIONAL      signature valid -> content TRUSTED
    LLM AGENTS        signature valid -> content UNKNOWN

You can verify the message came from the policy helper. You cannot verify the
policy helper wasn't manipulated into sending it. That is not a bug to fix - it
is a structural property of instruction-following systems. The defence is
containment.
"""
from __future__ import annotations

from dataclasses import dataclass

from config import settings
from agent import db, retrieval
from agent.models import Content, Session
from agent.telemetry import board

#: Zero-trust tiers (Day 2, slide 24). The tier is DECLARED, not assumed.
#: Content from a LOWER tier must clear a boundary before it can influence a HIGHER one.
TIER_UNTRUSTED = 0     # processes arbitrary user input
TIER_SANDBOXED = 1     # processes external web & documents
TIER_INTERNAL = 2      # internal processing, no external content
TIER_PRIVILEGED = 3    # can take real-world actions


@dataclass
class SubagentSummary:
    agent: str
    tier: int
    text: str
    reads_untrusted: bool
    takes_actions: bool


def policy_helper(question: str, session: Session) -> SubagentSummary:
    """Tier 1. Reads help-centre articles and summarises them.

    It has no tools and can take no action, so on its own it is harmless. The
    danger is not what it can do - it is what it can SAY to something that can.
    """
    articles = retrieval.search(question, limit=1)
    body = articles[0]["body"] if articles else "No relevant article."
    # A summariser summarises. It has no way to know that part of what it just
    # read was addressed to the agent downstream rather than to the customer.
    text = f"Policy summary for '{question[:40]}': {body[:600]}"
    board.record(session=session.id, principal=session.principal.id, node="helper",
                 tool="policy_helper", detail=f"tier {TIER_SANDBOXED} summary, "
                 f"{len(text)} chars, from {articles[0]['id'] if articles else '-'}")
    return SubagentSummary("policy_helper", TIER_SANDBOXED, text,
                           reads_untrusted=True, takes_actions=False)


def account_helper(question: str, session: Session) -> SubagentSummary:
    """Tier 2. Summarises the signed-in customer's account. No external content."""
    rows = db.secure_orders_for(session.principal)
    text = (f"Account summary for {session.principal.display_name}: "
            f"{len(rows)} order(s) on file.")
    board.record(session=session.id, principal=session.principal.id, node="helper",
                 tool="account_helper", detail=f"tier {TIER_INTERNAL} summary")
    return SubagentSummary("account_helper", TIER_INTERNAL, text,
                           reads_untrusted=False, takes_actions=False)


HELPERS = (policy_helper, account_helper)


def vulnerable_consult(question: str, session: Session) -> list[Content]:
    """VULNERABLE: a helper's output is spliced into Kestrel's context as TRUSTED.

    This is the trust-inheritance path in one line. The attack entered through the
    LEAST-privileged agent and is about to execute with the MOST-privileged
    agent's authority.
    """
    out = []
    for helper in HELPERS:
        summary = helper(question, session)
        out.append(Content(text=summary.text, origin="operator", label=summary.agent))
        #                                     ^^^^^^^^^^ "you wrote this". You did not.
        if summary.reads_untrusted:
            board.light("agent_trust", "amber",
                        f"{summary.agent} output entered context untagged and unchecked")
    return out


def secure_consult(question: str, session: Session) -> list[Content]:
    """SECURE: every sub-agent output routes through the quarantine layer first.

    Plus privilege separation: a helper that reads untrusted content is never
    allowed to influence an action path directly.
    """
    from agent import quarantine
    out = []
    for helper in HELPERS:
        summary = helper(question, session)
        if settings.on("SECURE_PRIV_SEP") and summary.reads_untrusted and summary.takes_actions:
            raise AssertionError("a reader agent must never also be an actor")
        out.append(quarantine.check(summary, session))
    return out


def consult(question: str, session: Session) -> list[Content]:
    return (secure_consult(question, session) if settings.on("SECURE_QUARANTINE")
            else vulnerable_consult(question, session))
