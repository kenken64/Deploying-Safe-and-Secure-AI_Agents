"""Authorization at action time.  (Day 1, Block 4)

Two rules that the opening breach violated:

    The agent RECEIVES an identity. It never establishes one, and it never
    trusts the model's claim about who is asking.            (slide 47)

    Check at the ACTION, every action, against the SESSION. A check at the top
    of the conversation is stale by the time the refund fires.  (slide 49)

RBAC is not one check, it is three (slide 48):
    1. invoke    - may this person talk to the agent at all?
    2. tool      - which tools does their role unlock?
    3. resource  - which rows may THIS call touch?   <- miss this and you get slide 9
"""
from __future__ import annotations

from config import settings
from agent import db
from agent.models import Denied, Principal, Session, ToolCall

# level 2: which tools each role unlocks
ROLE_TOOLS: dict[str, set[str]] = {
    "anonymous": {"search_help"},
    "customer":  {"search_help", "list_my_orders", "get_order", "lookup_orders",
                  "refund", "cancel_order", "track_shipment",
                  # Day 2: ordinary features that become the interior's attack paths
                  "send_summary", "remember"},
    "staff":     {"search_help", "list_my_orders", "get_order", "lookup_orders",
                  "refund", "cancel_order", "change_email", "apply_discount",
                  "track_shipment", "send_summary"},
}


def resource_owner(call: ToolCall) -> str | None:
    """Whose row is this call about? Returns None when the call is not row-scoped."""
    order_id = call.args.get("order_id")
    if isinstance(order_id, str) and order_id:
        return db.order_owner(order_id)
    cust = call.args.get("customer_id")
    return cust if isinstance(cust, str) else None


def vulnerable_check(session: Session, call: ToolCall) -> None:
    """VULNERABLE: nothing is checked.

    Kestrel runs under ONE service account that can do everything, so any
    successful steering inherits all of it.  (slide 46)
    """
    return None


def secure_check(session: Session, call: ToolCall) -> None:
    """SECURE: all three levels, at the action, against the session."""
    p: Principal = session.principal

    # level 1 - invoke
    if not p.may_invoke_agent:
        raise Denied("invoke", f"{p.id} may not use the agent")

    # level 2 - tool
    if call.name not in ROLE_TOOLS.get(p.role, set()):
        raise Denied("tool", f"role={p.role} may not call {call.name}")

    # level 3 - resource. THE tenancy check. Miss it and you get the opening breach.
    owner = resource_owner(call)
    if owner is not None and p.role != "staff" and owner != p.customer_id:
        raise Denied("resource", f"{p.customer_id} may not touch a row owned by {owner}")

    # A customer may refund their OWN order. Only staff issue an arbitrary credit.
    # (slide 48, level 2 example. The dollar split becomes the HITL gate on Day 2.)
    if call.name == "refund" and p.role == "customer":
        cents = int(call.args.get("amount_cents") or 0)
        if cents > settings.refund_autonomous_ceiling_cents:
            raise Denied("tool", f"refund of {cents}c exceeds the customer ceiling "
                                 f"({settings.refund_autonomous_ceiling_cents}c) - needs staff")


def check(session: Session, call: ToolCall) -> None:
    if settings.on("SECURE_AUTHZ"):
        secure_check(session, call)
    else:
        vulnerable_check(session, call)
