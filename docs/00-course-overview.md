# 00 · Course Overview — the spine of both days

## The thesis, in one sentence

> **Assume the model is already compromised. Make sure that assumption isn't catastrophic.**

Both days are the same sentence, split in half (D2 p59):

- **Day 1 footer:** *Assume the model is already compromised. Constrain what it can reach and do.*
- **Day 2 footer:** *The edge will be breached. Contain the blast, detect the rest, keep a human on the irreversible.*

The closing line of the whole course (D2 p59): *"You don't secure an agent by making the model
trustworthy — you secure it by making the model's untrustworthiness survivable."*

This matters pedagogically. **Nothing in the course tries to make the LLM safe.** Every control
attaches *around* the model: to input, to tools, to state, to identity, to output, to logs, to a
human. If a participant leaves trying to fix this with a better system prompt, the course failed.

---

## The one distinction the course hangs on (D1 p12)

| | **Safety** | **Security** |
|---|---|---|
| Nature | Accidents | Attacks |
| Definition | The agent does the wrong thing on its own | Someone *makes* the agent do the wrong thing |
| Kestrel example | Confidently gives a wrong return policy | A customer makes it refund an order it shouldn't |

**This course is the second one.** Every slide assumes an active adversary.

## Why agents and not chatbots (D1 p13)

| Chatbot | Agent |
|---|---|
| *"I think your return window closed."* | `refund()` · `cancel()` · `change_email()` · `apply_discount()` |
| Worst case: it says something wrong | It **acts** |

> Language → action. That single shift is why agent security is its own subject.

Corollary that runs through both days: **everything it reads is attacker-reachable; everything
it does needs a gate in your code.**

---

## Kestrel — the system under attack

A support agent on an online store, built on **LangGraph**. The participants spend two days
breaking it and repairing it. It is deliberately *"clean, familiar, unthreatening"* (D1 p8).

**It can act:** refund an order · cancel an order · change your account email · apply a discount
(plus order lookup, which is what leaks in the opening demo).

### The graph (D1 p14)

```
                     KESTREL AGENT · LangGraph
  Customer chat  ──▶  Read message                 ──▶  Helper agents × 2
   (the widget)       Consult helper agents             (summaries, trusted)
                      Call a tool                  ──▶  Order + customer DB
  Help-centre    ──▶  Reply to customer                 (tool call → result)
  docs (RAG)
                      ── the model decides the route ──▶ External APIs
                      State & memory                     (payment, shipping)
                      (conversation + saved notes)
```

Reads chat → consults two helpers → queries the databases → takes an action → replies → saves notes.

### The control room

Every demo and every workshop proof is shown on a console with named indicator lights
(D2 p6 names four): **Input validation · Content filter · Schema check · Data boundary**.
The whole course's proof ritual is *"run the attack, watch the panel go green."* See
`06-gaps-and-build-list.md` — this console is the single largest unbuilt dependency.

---

## The eight attack surfaces

One diagram the room keeps coming back to (D1 p15). Numbers are used as shorthand all course.

```
     1 ─▶ Read message                     ◀─ 6  Helper agents × 2
     2 ─▶ Consult helper agents
          Call a tool  ──▶ 3 / 4  ──▶ Order + customer DB
          Reply to customer
          (model decides route)  ── 8 ──   5  External APIs
     7    State & memory
```

### The attack-surface matrix (D1 p16)

Read every attack all course as **entry point → execution stage → impact**.

| # | Surface | Entry point | Execution stage | Impact |
|---|---|---|---|---|
| 1 | User messages | Chat input | Pre-model | Direct injection · data disclosure |
| 2 | Retrieved content | Help-centre article | Retrieval | Indirect injection |
| 3 | Tool args (in) | Model-built arguments | Tool execution | Unscoped query · unintended action |
| 4 | Tool results (out) | API / DB response | Post-tool, into state | Injection via side door |
| 5 | External APIs | Payment, shipping | Tool execution | SSRF · downstream abuse |
| 6 | Other agents | Helper summaries | Sub-agent return | Trusted-channel injection |
| 7 | State & memory | Saved notes | Across turns | Persistence · credential exposure |
| 8 | The model itself | Weights / behaviour | Everywhere | Why all the others matter |

> *"This goes on the wall now and it stays up. Every block: 'we're here.'"*

### How the matrix splits the two days (D1 p17, D2 p7)

| | **Day 1 — the edge** (the ways in) | **Day 2 — the interior** (after the edge fails) |
|---|---|---|
| Surfaces | 1 User messages · 2 Retrieved content · 3 Tool arguments | 4 Tool results · 5 External APIs · 6 Other agents · 7 State & memory |
| Also | | Output guardrails · observability · HITL · rate limits |
| Question | *How do we keep them out?* | *Given they're in: how much damage, will we notice, what did we refuse to automate?* |

Surface 8 (the model) is never "fixed" — it is the reason the other seven need controls.

---

## The framework layer (D1 p18–19)

LangGraph is taught as **three primitives, no more** — every control in two days attaches to one:

| Primitive | What it is | Why an attacker cares |
|---|---|---|
| **State** | Everything the agent knows right now | Surfaces 1, 2, 4 and 7 all flow into it |
| **Nodes** | The steps: read · consult · call a tool · reply | Each node is a place a control goes |
| **Conditional edges** | The routing — *the model often chooses it* | Which means an attacker can influence it |

And explicitly portable (D1 p19) — **State · Nodes · Edges are universal; the API is not**:

| Primitive | LangGraph | Bare tool loop | CrewAI | OpenAI Agents SDK |
|---|---|---|---|---|
| State | TypedDict state | the messages list | task context | thread / session |
| Nodes | node functions | steps in the loop | agents & tasks | agent + tool calls |
| Edges | conditional edges | your `if` statements | process / flow | handoffs |

This slide is load-bearing for a professional audience. Put it in front of anyone who says
*"we don't use LangGraph."*

---

## The Attack Board — the course's progress bar

Introduced D1 p23, walked at D1 p58, walked across both days at D2 p56.

| Attack | Day | Entry point | What stopped it | Fixed |
|---|---|---|---|---|
| Cross-tenant order leak | 1 | User message → unscoped tool call | Tenancy filter at the data layer | ✓ |
| Direct injection | 1 | Chat input | Intake validation + narrow typed tools | ✓ |
| Indirect injection | 1 | Poisoned help-centre article | Provenance tagging — data, not instruction | ✓ |
| Attack-swap findings | 1 | Your neighbour's build | Logged on the ledger | … |
| Bypass via retrieved content | 2 | Retrieval, post-input-gate | Trusted/untrusted split · provenance tags | ✓ |
| Trust inheritance via helper | 2 | Poisoned helper summary | Quarantine node · privilege separation | ✓ |
| Silent exfiltration | 2 | Valid-looking tool call | Output guardrail · behavioural log | ✓ |
| Uncapped loop / cost | 2 | Amplification | Token budget · cost circuit breaker | ✓ |

> *"Fills up as we find attacks. Empties as we fix them. Mostly green by tomorrow evening."*

Keep it physically on the wall. It is the only artefact that shows two days of work at a glance.

---

## The five teaching rituals

Recognise these and you can run any block in either deck.

1. **"We're here"** — every block opens on the same Kestrel map with the surface highlighted
   (D1 p27/37/46, D2 p10/21/30/40). *"You are never lost wondering how a detail connects."*
2. **Demo first, explanation second** — both days open with a LIVE breach and a deliberate
   silence (D1 p9: *"No slide. No explanation. Just the demo — and let it be uncomfortable."*).
3. **Predict before you run** — D1 p32 makes the room write down which payload the validator
   catches *before* running it. *"Your wrong prediction was the lesson."*
4. **My Agent moment** — a recurring private prompt turning Kestrel back on the participant's
   own system. Explicitly *private · nobody shares · never collected*. Nine of them across the
   two days; they accumulate into the final hardening list (D2 p58).
5. **Attack · Control · Proof** — the workshop discipline: run the attack → point at the
   control → show the proof in the console. Framed as *"exactly how you'll show your own
   tech lead that a fix works."*

### The nine My Agent moments (they are a course-long thread)

| # | Day | Slide | Prompt | Feeds |
|---|---|---|---|---|
| 1 | 1 | p24 | Your 8 surfaces — which is largest? Which have you never thought about? | 3:00 timer |
| 2 | 1 | p35 | What enters your agent's context that you don't control? | hardening list |
| 3 | 1 | p52 | What authority does your agent hold — and who granted it? | hardening list |
| 4 | 1 | p60 | Single riskiest surface on your own agent? | 5:00, end of Day 1 |
| 5 | 2 | p19 | What does your agent persist — and for how long? | hardening list |
| 6 | 2 | p28 | Which of your agents trusts another's output without checking? | hardening list |
| 7 | 2 | p33 | What could your agent's output leak that you're not checking for? | hardening list |
| 8 | 2 | p38 | If it were exfiltrating right now through valid tool calls — would you know? | hardening list |
| 9 | 2 | p45 | Which actions can never be undone — and is a human on them? | hardening list |
| ★ | 2 | p58 | **The hardening list** — top five things you change on Monday | 10:00, the deliverable |

D2 p58 explicitly lists where each of the five entries comes from. **Tell the room on Day 1
morning that these notes converge into a real deliverable**, or half of them will skip the first
four and be unable to do p58.

---

## How the course is run (D1 p3)

| Morning | Afternoon | Assessment |
|---|---|---|
| Theory & concepts, each demonstrated on Kestrel | Hands-on workshop, in teams, on your own agent build | MCQ + workshop |
| | Run the morning's attacks, fix them in code | MCQs run online *during* the morning sessions — short, focused, in the flow of teaching. The workshop is the practical assessment: **every fix proven in the console.** |

---

## Learning objectives

### Day 1 — the edge (D1 p4)

1. **Map the surface** — place the eight points where an attacker can reach an agentic system on one diagram.
2. **Break it and fix it** — run direct injection, indirect injection and a cross-tenant leak against a live agent, then close each one in code: layered intake validation, narrow typed tools behind a single secure executor, and authorization enforced below the model.
3. **Prove the fix** — show each fix the way you would to your own tech lead: run the attack, point at the control, watch the console panel go green.

### Day 2 — the interior (D2 p3)

1. **Contain the blast** — split trusted from untrusted state and quarantine what another agent returns, so a breach stays inside the component it landed in.
2. **Detect the rest** — instrument the agent so an attack that looks like ordinary traffic still surfaces; guardrails on what leaves; four layers of logging.
3. **Gate the irreversible** — turn Day 1's action-sort into approval gates that fire *before* the irreversible action, plus rate limits so the worst case is a bill you survive.

---

## Agendas

### Day 1 (D1 p5)

| Time | Topic | Block |
|---|---|---|
| 9:00 – 10:10 | The agent attack map | 0 |
| 10:10 – 10:40 | Tea break | |
| 10:40 – 11:00 | The Attack Board | 1 |
| 11:00 – 12:00 | Input validation | 2 |
| 12:00 – 1:00 | Lunch | |
| 1:00 – 1:50 | Tool security | 3 |
| 1:50 – 2:25 | Authorization | 4 |
| 2:25 – 3:10 | Workshop | W1 |
| 3:10 – 3:40 | Tea break | |
| 3:40 – 5:15 | Workshop | W1 |
| 5:15 – 5:30 | Close | |

### Day 2 (D2 p4) — *"six teaching blocks, one workshop"*

| Time | Topic | Block |
|---|---|---|
| 9:00 – 9:20 | Recap · the attack I promised you yesterday | — |
| 9:20 – 10:10 | State & memory security | 5 |
| 10:10 – 10:40 | Tea break | |
| 10:40 – 11:05 | Multi-agent trust boundaries | 6 |
| 11:05 – 12:00 | Output guardrails | 7 |
| 12:00 – 1:00 | Lunch | |
| 1:00 – 1:40 | Observability & monitoring | 8 |
| 1:40 – 2:25 | Human-in-the-loop **&** Rate limiting & abuse prevention | 9 + 10 |
| 2:25 – 3:10 | Workshop | W2 |
| 3:10 – 3:40 | Tea break | |
| 3:40 – 5:15 | Workshop | W2 |
| 5:15 – 5:30 | Close | |

Timing risks in both agendas are analysed in `04-facilitator-playbook.md`.

## Block map across the two days

| Block | Title | Slides | Surface |
|---|---|---|---|
| 0 | The Agent Attack Map | D1 p7–20 | all |
| 1 | Map your own agent · build the board | D1 p21–25 | all |
| 2 | Input validation | D1 p26–35 | 1 (and 2) |
| 3 | Tool security *(divider carries no block number — see `06`)* | D1 p36–44 | 3 (and 4) |
| 4 | Authorization at action time *(same)* | D1 p45–52 | 3 → action |
| — | Workshop 1 · Constrain Kestrel's reach | D1 p53–56 | |
| — | Close Day 1 | D1 p57–61 | |
| — | Recap · the promised attack | D2 p5–8 | 2/4 |
| 5 | State & memory security | D2 p9–19 | 7 |
| 6 | Multi-agent trust boundaries | D2 p20–28 | 6 |
| 7 | Output guardrails | D2 p29–33 | output |
| 8 | Observability & monitoring | D2 p34–38 | all |
| 9 | Human-in-the-loop | D2 p39–45 | action |
| 10 | Rate limiting & abuse prevention | D2 p46–50 | cost |
| — | Workshop 2 · Contain the interior | D2 p51–54 | |
| — | Close both days | D2 p55–60 | |
