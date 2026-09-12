"""ONE CHOKEPOINT: the secure tool executor.  (Day 1, slide 41)

    get_order()     ->  1 validate args
    refund()            2 check authz
    cancel()            3 execute
    change_email()      4 validate result
                        5 log

    "One chokepoint you can audit - instead of per-tool discipline you have to trust."

Every tool call goes through here. No exceptions. Day 2 plugs straight into this
file: the output guardrail IS step 4, behavioural telemetry IS step 5.
"""
from __future__ import annotations

import re

from agent import authz, db, directives, tools
from agent.models import (Blocked, Content, Denied, Session, ToolCall, ToolResult)
from agent.telemetry import board


def execute(call: ToolCall, session: Session) -> ToolResult:
    """The five steps, in order, for every call.

    There is no second path. The lab branch kept a `vulnerable_execute` beside
    this one - name a tool, run the tool - and a switch to pick between them;
    a chokepoint you can route around is not a chokepoint.
    """
    registry = tools.registry()

    # step 0 - allowlist the tool NAME itself. Fails safe on anything invented.
    spec = registry.get(call.name)
    if spec is None:
        board.light("tool_boundary", "amber", f"unknown tool {call.name}")
        raise Blocked("executor", f"tool {call.name!r} is not on the registry")

    # step 1 - validate args against the declared schema
    _validate_args(call, spec)

    # step 2 - check authz, HERE, at the action, against the session
    authz.check(session, call)

    # step 3 - execute
    result = spec.fn(call.args, session)

    # step 4 - validate what comes back (surface 4, the side door - slide 40)
    result = _validate_result(result, call)

    # step 5 - log
    board.record(session=session.id, principal=session.principal.id, node="tool",
                 tool=call.name, args_fingerprint=call.fingerprint(),
                 records_touched=result.records_touched, egress_host=result.egress_host,
                 detail=result.text[:200], control="executor")
    _watch_data_boundary(session, call, result)
    _watch_egress(session, call, result)
    _watch_exfiltration(session, call, result)
    return result


def _validate_args(call: ToolCall, spec: tools.ToolSpec) -> None:
    schema = spec.parameters
    props: dict = schema.get("properties", {})
    for key in call.args:
        if key not in props:
            # AMBER, not red. This is the control doing its job: the call never
            # ran. Red means a breach got through, and the attack runner grades
            # on exactly that - a control that reports itself as a breach makes
            # the hardened build look like it is still bleeding.
            board.light("schema_check", "amber",
                        f"undeclared argument {key!r} on {call.name} - call refused")
            raise Blocked("executor", f"undeclared argument {key!r} on {call.name}")
    for key in schema.get("required", []):
        if key not in call.args:
            raise Blocked("executor", f"missing required argument {key!r}")
    for key, value in call.args.items():
        rule = props[key]
        kind = rule.get("type")
        if kind == "string" and not isinstance(value, str):
            raise Blocked("executor", f"{key} must be a string")
        if kind == "integer" and not isinstance(value, int):
            raise Blocked("executor", f"{key} must be an integer")
        if "enum" in rule and value not in rule["enum"]:
            raise Blocked("executor", f"{key}={value!r} not in {rule['enum']}")
        if "pattern" in rule:
            import re
            if not re.match(rule["pattern"], str(value)):
                raise Blocked("executor", f"{key}={value!r} fails {rule['pattern']}")
        if "minimum" in rule and isinstance(value, int) and value < rule["minimum"]:
            raise Blocked("executor", f"{key} below minimum")
        if "maximum" in rule and isinstance(value, int) and value > rule["maximum"]:
            raise Blocked("executor", f"{key} above maximum")


def _validate_result(result: ToolResult, call: ToolCall) -> ToolResult:
    """Step 4. A compromised API is an injection channel (slide 40).

    Whatever comes back is about to become context, and the model will read it as
    if you wrote it. So it gets the same treatment as any other untrusted text.
    """
    found = directives.find(result.text)
    if found:
        board.light("tool_boundary", "amber", f"instruction-shaped tool result from {call.name}")
        board.record(session="-", principal="-", node="tool_result", tool=call.name,
                     detail=f"neutralised directives in tool result: {found}",
                     verdict="sanitised", severity="warn", control="tool-result-check")
        result.text = directives.strip(result.text)
    return result


APPROVED_EGRESS_DOMAINS = {"kestrel.example"}


def _watch_exfiltration(session: Session, call: ToolCall, result: ToolResult) -> None:
    """DATA BOUNDARY, the outbound half.

    Day 1 watched for another customer's rows coming IN. Day 2 watches for this
    customer's data going OUT. Same light, same question - did data cross a
    boundary it had no business crossing - and it fires with or without the
    guardrail, because you cannot fix what the console never showed you.
    """
    if call.name != "send_summary":
        return
    recipient = str(call.args.get("recipient", ""))
    body = str(call.args.get("body", ""))
    domain = recipient.split("@")[-1].lower()
    looks_like_data = bool(re.search(r"ORD-\d{6}|CUST-\d{4}|ships to", body))
    if domain not in APPROVED_EGRESS_DOMAINS and looks_like_data:
        board.light("data_boundary", "red",
                    f"{len(body)} chars of order data sent to {domain} "
                    f"- a valid tool call, a 200 response, and an exfiltration")
        board.record(session=session.id, principal=session.principal.id, node="tool",
                     tool=call.name, egress_host=domain, verdict="exfiltration",
                     severity="alert", detail=f"outbound to {recipient}: {body[:120]}")


def _watch_egress(session: Session, call: ToolCall, result: ToolResult) -> None:
    """Surface 5. Where did this call actually reach?

    With SECURE_EGRESS off the fetch simply succeeds, and nothing anywhere says
    that your agent just read the cloud metadata endpoint on an attacker's behalf.
    """
    host = result.egress_host
    if call.name == "send_summary":
        return                      # an email domain, not a URL host - see _watch_exfiltration
    if not host or host in tools.ALLOWED_HOSTS:
        return
    board.light("tool_boundary", "red", f"egress to unapproved host: {host}")
    board.record(session=session.id, principal=session.principal.id, node="tool",
                 tool=call.name, egress_host=host, verdict="egress", severity="alert",
                 detail=f"{call.name} reached {host}, which is not on the allowlist")


#: Tools that read the orders table. The text fallback below is scoped to these,
#: so a help-centre article that merely mentions an order id cannot trip the light.
ORDER_READS = {"lookup_orders", "get_order", "list_my_orders"}


def _watch_data_boundary(session: Session, call: ToolCall, result: ToolResult) -> None:
    """The light that matters most on Day 1.

    It goes RED the moment data belonging to someone other than the signed-in
    customer is returned - whatever route got it there.

    Two ways to see it, because one is not enough. The rows usually carry a
    customer_id, so the check is exact. But lookup_orders is a blank cheque: a
    real model writes `SELECT ship_to FROM orders WHERE id='ORD-100003'` and the
    row that comes back no longer says whose it is. Same leak, thinner evidence -
    so ownership is resolved against the store as well.
    """
    me = session.principal.customer_id
    if session.principal.role == "staff":
        return

    foreign = [r for r in result.rows if r.get("customer_id") and r["customer_id"] != me]
    owners = {r["customer_id"] for r in foreign}
    count = len(foreign)

    if call.name in ORDER_READS:
        disclosed = {oid: owner for oid, owner in db.owners_in(result.text).items()
                     if owner != me}
        if disclosed:
            owners |= set(disclosed.values())
            count = max(count, len(disclosed))

    if owners:
        ids = ", ".join(sorted(owners))
        what = (f"{count} row(s)" if foreign else "order data")
        board.light("data_boundary", "red", f"{what} belonging to {ids} returned to {me}")
        board.record(session=session.id, principal=session.principal.id, node="tool",
                     tool=call.name, records_touched=count, verdict="cross-tenant",
                     severity="alert", detail=f"data owned by {ids} reached {me}")

