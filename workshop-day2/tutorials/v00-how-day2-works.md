# v00 - How Day 2 works (read first)

> Day 1 secured the edge. Today we assume all of it was bypassed.

This is the same Kestrel, the same SQLite store, the same LangGraph - but it **starts
where Day 1 ended**. All nine Day 1 controls are already on and marked `day 1` in the
control room. Turning them off is not today's lesson.

The question has changed:

> not *"how do we keep them out"*
> but *"given that they're in - how much damage, will we notice, and what did we refuse
> to automate."*

---

## Prove the premise first

```
python kestrel.py controls
python kestrel.py attack b1 --day1-only
```

`b1` is the attack you were promised at the end of Day 1. Watch what the console does:

```
  [ ok ]    input_validation      <- green
  [ ok ]    content_filter        <- green
  [ ok ]    schema_check          <- green
  [BREACH]  data_boundary         <- red anyway
```

Every input control passed, because **the payload never went near the chat box.** It was
read by a sub-agent, summarised, and handed to Kestrel as if one of your own components
had written it.

That is why input validation is a cost-raiser and not a wall, and why the rest of the
defence lives inside.

## The shape of the day

| **CONTAIN** | **DETECT** | **JUDGE** |
|---|---|---|
| a breach can't spread | you know it happened | a person on the irreversible |
| State & memory (block 5) | Output guardrails (block 7) | Human-in-the-loop (block 9) |
| Multi-agent trust (block 6) | Observability (block 8) | Rate & cost limits (block 10) |

## The nine controls you build today

| Control | Block | What it does |
|---|---|---|
| `SECURE_STATE_SPLIT` | 5 | trusted and untrusted are different fields, never merged |
| `SECURE_THREAD_IDS` | 5 | random thread ids, bound to identity, ownership checked every access |
| `SECURE_MEMORY_WRITES` | 5 | the model may propose a memory; code and humans decide what sticks |
| `SECURE_QUARANTINE` | 6 | every sub-agent output clears a deterministic boundary |
| `SECURE_PRIV_SEP` | 6 | the agent that reads untrusted content cannot act |
| `SECURE_OUTPUT_GUARD` | 7 | inspect what it says **and** what it is about to do |
| `SECURE_TELEMETRY` | 8 | behavioural baselines - catches the legitimate-looking attack |
| `SECURE_HITL` | 9 | interrupt **before** the irreversible action, with state frozen |
| `SECURE_LIMITS` | 10 | five independent caps, because one cap caps one thing |

## The attacks

```
python kestrel.py attack all --day1-only     all 8 land, past the entire edge
python kestrel.py attack all --secure        all 8 stopped
```

| | Attack | Theme | Closed by | Tutorial |
|---|---|---|---|---|
| `b1` | The attack I promised you | CONTAIN | quarantine + state split + guard + HITL | [v11](v11-trust-inheritance.md) |
| `b2` | Poison once, spread everywhere | CONTAIN | `SECURE_STATE_SPLIT` | [v08](v08-state-poisoning.md) |
| `b3` | Thread-ID guessing | CONTAIN | `SECURE_THREAD_IDS` | [v09](v09-thread-id-guessing.md) |
| `b4` | The memory landmine | CONTAIN | `SECURE_MEMORY_WRITES` | [v10](v10-memory-landmine.md) |
| `b5` | Trust inheritance | CONTAIN | `SECURE_QUARANTINE`, `SECURE_PRIV_SEP` | [v11](v11-trust-inheritance.md) |
| `b6` | Silent exfiltration | DETECT | `SECURE_OUTPUT_GUARD`, `SECURE_TELEMETRY` | [v12](v12-silent-exfiltration.md) |
| `b7` | An irreversible action, nobody on it | JUDGE | `SECURE_HITL` | [v14](v14-irreversible-action.md) |
| `b8` | Economic exhaustion | JUDGE | `SECURE_LIMITS` | [v15](v15-cost-exhaustion.md) |

## What you are aiming for

Not an unbreakable agent. **An agent where a breach is bounded, visible and reversible.**

- **Contained** - it can't spread
- **Detected** - you know it happened
- **Gated** - a human on the irreversible

Anyone who sells you an unbreakable agent is wrong. This is better, and truer.
