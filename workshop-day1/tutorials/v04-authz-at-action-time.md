# v04 - Authorization at action time

**The action layer** | **Day 1, Block 4** | **Attacks** `a1`, `a2` | **Closed by** `SECURE_AUTHZ`, `SECURE_NO_CREDS_IN_STATE`

The question nobody asks until the incident review: whose authority is the agent acting under?

---

## 1. Run the attack

```
python kestrel.py reset
python kestrel.py attack a1 --control SECURE_TENANCY --control SECURE_TOOLS --control SECURE_EXECUTOR
```

Tenancy is on. Tools are narrow. The executor is in place. And yet:

```
  model      [mock] chose tool get_order(order_id='ORD-100003')
  tool       get_order -> No matching orders.
```

Better - no data leaked. But notice what did **not** happen: nobody refused. No log line
says *"Alice tried to read Ben's order."* You silently returned an empty result, which
means your detection surface is zero and Alice can enumerate all day.

Now add authorization:

```
python kestrel.py attack a1 --secure
```

```
  blocked    get_order refused by authz at level=resource
  [warn]     authorization
```

## 2. The rule that was broken

> **The agent RECEIVES an identity. It never establishes one.**

| Your infrastructure | The agent |
|---|---|
| Authentication happens here. A session identity is **passed in**. | Receives it. Never invents one. |
| | Never trusts the model's claim about who the user is |
| | The model may **request**. Only code decides. |

The opening breach was exactly that failure: *the agent trusted the model's belief about
who was asking.*

## 3. RBAC is three checks, not one

`agent/authz.py`, `secure_check`:

```python
def secure_check(session: Session, call: ToolCall) -> None:
    p = session.principal

    # level 1 - INVOKE: may this person talk to the agent at all?
    if not p.may_invoke_agent:
        raise Denied("invoke", ...)

    # level 2 - TOOL: which tools does their role unlock?
    if call.name not in ROLE_TOOLS.get(p.role, set()):
        raise Denied("tool", ...)

    # level 3 - RESOURCE: which rows may THIS call touch?
    owner = resource_owner(call)
    if owner is not None and p.role != "staff" and owner != p.customer_id:
        raise Denied("resource", ...)          # <- miss this one and you get slide 9
```

Most teams build level 1, often build level 2, and almost never build level 3. Level 3 is
the one that produces cross-tenant incidents.

Notice the refund rule underneath it:

```python
if call.name == "refund" and p.role == "customer":
    if cents > settings.refund_autonomous_ceiling_cents:      # $50
        raise Denied("tool", "... needs staff")
```

**A customer may refund their own order. Only staff issue an arbitrary credit.** Hold on
to the fact that refund splits by amount - it becomes the human-in-the-loop gate on Day 2.

## 4. Timing: check at the action, not at the start

```
conversation starts ---- steering happens ---- model requests the refund ---- ACTION
    check here = STALE                                                   check HERE
```

A conversation can be steered *after* it starts. A check at the top of the session is
stale by the time the refund fires. That is why `authz.check(...)` is **step 2 inside the
executor** (`agent/executor.py`), which runs on every single call - not a decorator on the
entry point, not a middleware at the front door.

Look at the order in `secure_execute` and notice that step 2 comes **before** step 3:

```python
_validate_args(call, spec)     # 1
authz.check(session, call)     # 2   <- before anything happens
result = spec.fn(call.args, session)  # 3
```

## 5. Two rules that bite people

### Rule 1 - credentials never in the context window

Not in the system prompt. Not in state. Not in a tool result.

> If it's in state, it's in a checkpoint - and checkpoints get read.

That is Day 2's subject, and it is the reason this rule exists today. `config.Settings`
drops `openrouter_api_key` from `snapshot()` for exactly this reason, and
`test_credentials_never_reach_the_context_window` asserts it.

### Rule 2 - the tenancy filter is enforced below the model

```
  Model
  Tool layer
  DATA LAYER  <- the filter lives here
```

Covered in `v01`. The point of restating it here: the resource check in `authz` and the
filter in `db` are **not redundant**. The authz check gives you a refusal you can log and
alert on. The data-layer filter is what still holds if someone adds a new tool next month
and forgets to wire the check in.

## 6. Prove it

```
python kestrel.py attack a1 --secure
python kestrel.py attack a2 --secure
python kestrel.py test
```

`test_authorization_is_checked_at_the_action_not_at_the_start` asserts that the same
session is allowed `ORD-100001` and refused `ORD-100003` with `level == "resource"`.

## 7. Activity: who may say yes

Before Day 2, sort Kestrel's actions into four buckets. Argue the disagreements out loud -
**the argument is the learning**, and this sort is the input to tomorrow's human-in-the-loop
design.

| Autonomous | Verified identity | Human approver | Never for an agent |
|---|---|---|---|
| *just do it* | *needs the requesting customer* | *a person signs off* | *not available at all* |

Actions: `refund` · `cancel` · `discount` · `change-email` · `escalate` · `lookup-own` ·
`lookup-any`

Then the uncomfortable question: **every autonomous action is a standing decision to trust
the model.** Which of those decisions has your organisation ever made on purpose?
