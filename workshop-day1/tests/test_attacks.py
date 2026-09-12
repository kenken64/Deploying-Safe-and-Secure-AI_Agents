"""Proof tests - SOLUTION BUILD.

The lab branch asserted each attack TWICE: it had to LAND against the shipped
build and STOP against the hardened one. Here there is only one build, so only
the second assertion survives - plus the specific claims each control makes.

If one of these fails, this branch has regressed into the lab.
"""
from __future__ import annotations

import pytest

from agent import db, graph, intake
from agent.models import Principal
from agent.telemetry import board
from attacks.catalogue import ATTACKS, ORDER
from attacks.run import run_one

ALICE = Principal(id="CUST-1001", display_name="Alice Tan", role="customer",
                  customer_id="CUST-1001")


@pytest.fixture(autouse=True)
def clean():
    db.reset()
    board.reset()
    graph.SESSIONS.clear()
    yield


@pytest.mark.parametrize("attack_id", ORDER)
def test_every_attack_in_the_catalogue_is_stopped(attack_id):
    assert not run_one(ATTACKS[attack_id], verbose=False)["landed"], (
        f"{attack_id} landed against the solution build")


# --------------------------------------------------------------- the specific claims --
def test_the_data_boundary_stays_green_on_the_opening_breach():
    """Day 1 slide 56: 'Data-boundary light stays GREEN on the cross-tenant attack.'"""
    run_one(ATTACKS["a1"], verbose=False)
    assert board.lights["data_boundary"] == "green"


def test_narrow_tools_make_the_attack_unrepresentable():
    """Day 1 slide 38. Not 'filtered' - unrepresentable. There is no sql argument."""
    from agent import tools
    assert "lookup_orders" not in tools.registry()
    assert "sql" not in tools.registry()["get_order"].parameters["properties"]


def test_there_is_no_vulnerable_implementation_left_to_switch_back_on():
    """The point of this branch. A control with an off switch gets switched off."""
    import config
    from agent import authz, executor, intake as intake_mod, retrieval, tools
    assert not hasattr(config.settings, "on")
    for module in (authz, executor, intake_mod, retrieval, tools):
        leftovers = [n for n in dir(module) if n.startswith("vulnerable_")]
        assert not leftovers, f"{module.__name__} still carries {leftovers}"
    assert not hasattr(db, "vulnerable_query")
    assert not hasattr(tools, "VULNERABLE_TOOLS")


def test_validation_blocks_four_of_five_payloads_and_misses_the_natural_one():
    """Day 1 slide 33. The wrong prediction IS the lesson."""
    outcome = {name: intake.check(p).allowed for name, p in intake.PAYLOADS.items()}
    assert outcome == {"P1-length-bomb": False, "P2-delimiter": False, "P3-base64": False,
                       "P4-override": False, "P5-natural": True}


def test_the_data_layer_has_no_path_that_returns_another_customers_rows():
    """Day 1 slide 50, rule 2. The filter is not optional and not a keyword argument."""
    rows = db.orders_for(ALICE)
    assert rows and all(r["customer_id"] == "CUST-1001" for r in rows)
    assert db.orders_for(ALICE, "ORD-100003") == []      # Ben's order


def test_credentials_never_reach_the_context_window():
    """Day 1 slide 50, rule 1. If it is in state, it is in a checkpoint."""
    graph.chat(ALICE, "Where is my order ORD-100001?")
    blob = " ".join(e.detail for e in board.events)
    for secret in ("OPENROUTER_API_KEY", "sk-", "password", "Bearer "):
        assert secret not in blob


def test_authorization_is_checked_at_the_action_not_at_the_start():
    """Day 1 slide 49. A check at the top is stale by the time the refund fires."""
    from agent import authz
    from agent.models import Denied, Session, ToolCall
    session = Session(id="s", principal=ALICE, thread_id="t")
    authz.check(session, ToolCall("get_order", {"order_id": "ORD-100001"}))    # own order: fine
    with pytest.raises(Denied) as exc:
        authz.check(session, ToolCall("get_order", {"order_id": "ORD-100003"}))
    assert exc.value.level == "resource"
