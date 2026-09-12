# 05 · Workshop Guide — running both afternoons

Both workshops run on the **Kestrel Goat** labs in [`../workshop-day1/`](../workshop-day1/)
and [`../workshop-day2/`](../workshop-day2/). This file is for whoever is running the room.

`▸ Deck` = from the slides. `▸ Added` = written for these notes.

---

## The discipline, both days: Attack · Control · Proof

```
Run the attack  →  Point at the control  →  Show the proof in the console
```

> *"Exactly how you'll show your own tech lead that a fix works."*

Enforce all three steps in every check-in. A team that says *"we turned it on"* without
re-running the attack has not finished the phase.

**The one rule that is never negotiable (D1 p54):** the fix goes **in code, not in the
system prompt**. If a team adds *"please don't leak data"* to `SYSTEM_PROMPT`, walk them to
the poisoned article and ask who else can write into the model's context.

---

## Before the room arrives `▸ Added`

```bash
cd workshop-day1 && python kestrel.py doctor && python kestrel.py test
cd ../workshop-day2 && python kestrel.py doctor && python kestrel.py test
```

Expect `READY`, `20 passed`, `READY`, `30 passed`. The test suites assert both directions —
that each attack **lands** against the vulnerable build and **stops** against the hardened
one — so a green run means no demo has quietly broken.

Send participants the setup instructions a week ahead. `doctor` is the single command that
tells them whether their laptop is workshop-ready, and it names the fix for whatever it finds.

---

## Team shape `▸ Added`

Teams of three to four (D1 p54). Rotate these roles each phase so nobody just watches:

| Role | Does |
|---|---|
| **Driver** | has the keyboard, makes the edits |
| **Console** | watches `/console`, calls out lights and trace lines |
| **Adversary** | re-runs the attack after every change, tries to make it land again |
| **Scribe** | keeps the team's row on the Attack Board and the findings ledger |

---

# Workshop 1 · Constrain Kestrel's reach

**Slides:** D1 p53–56 · **Clock:** 2:25–3:10 and 3:40–5:15 (140 minutes)

## The brief (D1 p54)

> **INCIDENT TICKET — KESTREL. SUSPENDED, pending security review. Reviewer: you.**
>
> 1. Ship a build where this morning's three attacks fail — **in code, not by adding
>    "please don't leak data" to the system prompt.**
> 2. Prove each fix in the console. Run the attack. Show the panel go green.

## The phases (D1 p55)

| Phase | What you build | Done when (in the console) | Lab |
|---|---|---|---|
| **A** Intake | Structural + content validation on chat text; provenance-tag retrieved content as data, not instruction | Poisoned article produces **no tool call** | `attack a3`, tutorials v02, v03 |
| **B** Tools | Narrow typed tools; everything through the secure executor; parameterised queries | Tool-argument injection **can't be expressed** | `attack a5`, tutorial v05 |
| **C** Authority | Tenancy filter at the data layer; action-time authz against session identity; credentials out of state | **Data-boundary light stays GREEN** | `attack a1`, tutorials v01, v04 |
| **D** Attack swap | Swap machines. Attack your neighbour's build for 15 min, then log findings | Every team has **≥ 3 findings** logged | below |

**C is flagged on the slide as "the one that matters most."** Re-run the morning's opening
attack; the light stays green.

## Suggested time budget `▸ Added`

| | Minutes | Notes |
|---|---|---|
| Setup + brief | 10 | everyone on `doctor` green before phase A |
| A Intake | 30 | |
| B Tools | 35 | the refactor is the slowest phase |
| C Authority | 40 | **protect this one** — cut B before you cut C |
| D Attack swap | 15 | hard stop, timed |
| Walk the board | 10 | |

## Extra attacks in the lab `▸ Added`

The deck names three attacks; the lab ships seven. `a4` (beat the validator), `a6`
(tool-result side door) and `a7` (SSRF) are not on the slides — use them as **stretch work**
for fast teams, or as attack-swap ammunition. `a4` in particular is worth running with the
whole room, because it ends by proving which layer actually caught P5.

## Proof for the room

```bash
python kestrel.py attack all --secure   # 7/7 stopped
python kestrel.py test                  # 20 passed
```

---

# Workshop 2 · Contain the interior

**Slides:** D2 p51–54 · **Clock:** 2:25–3:10 and 3:40–5:15 (140 minutes)

## The brief (D2 p52)

> **INCIDENT TICKET — KESTREL. BREACH CONTAINED? — interior review.**
> The edge was bypassed. That's a given now, not a failure.
>
> Ship a build where the breach **can't spread** (through state or a trusted sub-agent),
> **can't hide** (it shows up in the log and at the output), and **can't touch the
> irreversible** (without a human, and can't run away with your budget).

## The phases (D2 p53)

| Phase | What you build | Done when (in the console) | Lab |
|---|---|---|---|
| **A** State | Trusted/untrusted schema split; provenance tags; thread IDs bound to identity | Poisoned state **can't reach a trusted field**, and a guessed thread ID **bounces** | `attack b2`, `b3`, tutorials v08, v09 |
| **B** Trust | Quarantine node between helpers and Kestrel; split reading from acting | The poisoned-summary path **no longer reaches a real action** | `attack b1`, `b5`, tutorial v11 |
| **C** Detect | Output guardrail on replies **+** tool args; one behavioural log line | Exfil attempt is **logged AND blocked** | `attack b6`, tutorials v12, v13 |
| **D** Judge & cap | Human interrupt before the irreversible action; token budget + cost breaker | Action **pauses**; a looped session **trips the cap** | `attack b7`, `b8`, tutorials v14, v15 |

**A is "the one that closes the morning."** **C requires both halves** — *"seeing it isn't
enough; stopping it isn't enough."* The lab enforces that:
`test_detection_and_blocking_are_both_required` fails if only one fires.

## Suggested time budget `▸ Added`

| | Minutes | Notes |
|---|---|---|
| Setup + brief | 10 | `attack b1 --day1-only` together, so the premise lands |
| A State | 30 | |
| B Trust | 30 | placement of the quarantine node is the whole exercise |
| C Detect | 35 | both halves |
| D Judge & cap | 30 | two builds in one phase — watch the clock |
| Walk the board + hardening list | 15 | |

Phase D contains two distinct pieces of work (HITL and limits). If time is short, do HITL
properly and demonstrate limits from the console rather than building them.

## Proof for the room

```bash
python kestrel.py attack all --secure   # 8/8 stopped
python kestrel.py test                  # 30 passed
```

---

## The attack swap (D1 p55 phase D)

15 minutes, hard-timed. Teams swap machines and attack the neighbouring build.

**Rules `▸ Added`**

1. **No editing the other team's code.** Attack only — chat box, `attack` CLI, `/console`.
2. **A finding needs a repro.** The exact message or command, and what the console did.
3. **Findings are about the build, not the team.** Adjudicate anything that drifts.
4. Log findings on the ledger below; every team needs **three**.

**Where to look first**, when a team is stuck:

- Did they fix `lookup_orders` or delete it? A filtered blank cheque is still a blank cheque.
- Is the tenancy filter in the tool, or in the data layer? A filter in the tool is bypassed
  by the next tool.
- Does authz refuse, or does it silently return nothing? Silence means no detection.
- Is anything still trusting `origin="operator"` on content nobody wrote?
- Day 2: is the quarantine node one edge too late?

### Findings ledger

| # | Team attacked | Attack (exact input/command) | What the console did | Which control was missing | Severity |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

---

## Assessment `▸ Added`

The workshop **is** the practical assessment (D1 p3): *"every fix proven in the console."*
A defensible rubric:

| | Criterion | Evidence |
|---|---|---|
| 40% | **The build holds** | `attack all --secure` stops every attack; `test` passes |
| 25% | **The fix is in the right layer** | tenancy below the model, authz in the executor, quarantine on the right edge — not a prompt, not a regex on the symptom |
| 20% | **Proof discipline** | can run attack → name the control → show the console, unprompted |
| 15% | **Attack swap** | three findings with real repros, and at least one they fixed |

**What does not earn marks:** a passing test suite with the fix written into the system
prompt; a control toggled on without being able to say what the two implementations differ
by; a green console the team cannot reproduce for you.

### A fast way to grade a team's build

```bash
cd <team-folder>
python kestrel.py attack all --secure   # does it hold?
python kestrel.py test                  # do the property tests hold?
git diff                                # is the fix in the layer they claim?
```

---

## Common failure modes in the room `▸ Added`

| What you'll see | What to say |
|---|---|
| Fix written into the system prompt | *"Who else can write into that context? Show me the poisoned article again."* |
| Regex added to block `CUST-1002` | *"That's a denylist. What about CUST-1004? Where does the filter belong?"* |
| Tenancy check added inside the tool | *"Now add a second tool. Did it inherit the check?"* |
| Control toggled, attack not re-run | *"Show me. The proof is the point."* |
| Team stuck on B for 40 minutes | Hand them `SECURE_TOOLS` in the console and move them to C — C is the one that matters most |
| *"It passes because the mock is fake"* | Flip the model switch to `ollama` or `openrouter` and re-run in front of them |
| Day 2: quarantine added after `plan` | *"Read the trace. Where had the content already been?"* |
