# 04 · Facilitator Playbook

Everything needed to *run* the two days: run-of-show, demo prep, timing risks, the objections a
professional room will raise, and a seed MCQ bank.

`▸ Deck` = from the slides. `▸ Added` = written for these notes; adopt or discard.

---

## Room & tech requirements `▸ Added`

| | Need |
|---|---|
| Projection | Two surfaces if possible: slides **and** the live control room. The demos are two-pane (chat / control room) and lose their force on one small screen. |
| Wall | Physical space for the **Attack Board** — it stays up for two days (D1 p16: *"This goes on the wall now and it stays up"*). A3 printout + marker beats a slide. |
| Participant machines | Python 3.10+, Docker optional. The labs (`../workshop-day1/`, `../workshop-day2/`) run offline on the mock model — **no API key required to complete any workshop phase**. |
| Network | Only needed for the optional real-model runs and the online MCQs. Have the MCQs work on phones. |
| Timers | Visible countdown. The decks specify exact timers (3:00, 25:00, 12:00, 15:00, 10:00, 5:00) — honour them; they're load-bearing for the day's pacing. |
| Printouts | The 8-surface matrix (D1 p16), the action-sort cards (D1 p51), the *My Agent* sheet (8 numbered lines). |

## Two-instructor split `▸ Added`

The decks list two lecturers. A workable division:

| | Instructor A | Instructor B |
|---|---|---|
| Demos | Drives the chat pane, narrates nothing during the LIVE slides | Watches the control room, calls out lights |
| Blocks | 0, 2, 5, 7, 9 | 1, 3, 4, 6, 8, 10 |
| Workshop | Floats teams 1–4 | Floats teams 5–8 |
| Attack swap | Runs the clock, collects the ledger | Adjudicates disputes on findings |

Whoever makes the **D1 p59 promise** (*"tomorrow morning, I will"*) should be the one who
delivers the **D2 p5 demo**. The callback lands harder when it's the same person.

---

## Day 1 run-of-show

| Clock | Block | Slides | Must happen |
|---|---|---|---|
| 9:00 | Open | p1–6 | State the thesis. Announce that *My Agent* notes become a real deliverable. |
| 9:15 | **B0 · Attack map** | p7–20 | **The LIVE breach at p9 with no narration.** Walk it back at p10. Land *"that wasn't a hack"* at p11. |
| | | | Build the map in three passes (p14→15→16). Don't collapse them. |
| 10:10 | Tea | | Leave the matrix on screen. |
| 10:40 | **B1 · Your agent + board** | p21–25 | Attack Board goes on the wall with row 1 and **two empty columns**. ⏱3:00 *My Agent* first pass. |
| 11:00 | **B2 · Input validation** | p26–35 | p28–31 theory, then ⏱25:00 hands-on. **Enforce written predictions before running payloads.** |
| 11:50 | | p33–35 | Regroup on deterministic vs non-deterministic. Add 3 rows to the board. |
| 12:00 | Lunch | | |
| 1:00 | **B3 · Tool security** | p36–44 | p38 is the highest-leverage slide of the day. ⏱25:00 refactor activity. |
| 1:50 | **B4 · Authorization** | p45–52 | ⏱12:00 action-sort. **Make the "refund splits by amount" observation out loud.** |
| 2:25 | **Workshop 1** | p53–56 | Phases A–C. |
| 3:10 | Tea | | |
| 3:40 | Workshop 1 | | Finish C, then **attack swap (D) for 15 min** at ~4:45. |
| 5:15 | Close | p57–61 | Walk the board. Make the p59 promise. ⏱5:00 *My Agent*. |

### Day 1 timing risks `▸ Added`

- **Block 0 is 70 minutes for 14 slides.** It's the right length — the demo + walk-back + map
  build-up needs room — but it will feel slow to you and fast to them. Don't compress the demo to
  buy time; compress p18–19 (LangGraph) if you must.
- **Block 3 is 50 minutes and contains a 25-minute activity.** That leaves 25 minutes for 8 slides.
  Tight. Pre-decide what you cut: p40 (validate what comes back) can be a 60-second forward
  reference to Day 2, since Block 7 covers it properly.
- **Block 4 is 35 minutes with a 12-minute activity.** Also tight. p47–49 are the core; p50 can be
  delivered as two spoken rules over the slide.
- **Workshop gets 140 minutes for 4 phases including a 15-minute swap.** Suggested budget:
  A 30 · B 35 · C 40 · D 15 · wrap 20. Protect C — it is *"the one that matters most."*

---

## Day 2 run-of-show

| Clock | Block | Slides | Must happen |
|---|---|---|---|
| 9:00 | Recap | p2–8 | **Keep the promise: the LIVE bypass at p5, against their own Day 1 build.** |
| | | p6 | Input lights GREEN, data boundary RED. Let that sit. |
| 9:20 | **B5 · State & memory** | p9–19 | p14 (checkpoints) is the sit-up slide. ⏱15:00 threat-model the vault. |
| 10:10 | Tea | | |
| 10:40 | **B6 · Multi-agent trust** | p20–28 | p22 (signature valid → content unknown) is the senior-audience slide. ⏱15:00 inheritance path. |
| 11:05 | **B7 · Output guardrails** | p29–33 | Say explicitly: this is **step 4 of yesterday's secure executor**, not a new system. |
| 12:00 | Lunch | | |
| 1:00 | **B8 · Observability** | p34–38 | p36's clean log with `errors=0` is the whole point. |
| 1:40 | **B9 + B10** | p39–50 | **Two blocks in 45 minutes — the day's biggest squeeze.** |
| 2:25 | **Workshop 2** | p51–54 | Phases A–D. |
| 3:10 | Tea | | |
| 3:40 | Workshop 2 | | Finish D by ~5:00. |
| 5:15 | Close | p55–60 | Walk both days' board. ⏱10:00 hardening list. The last word. |

### Day 2 timing risks `▸ Added`

- **1:40–2:25 carries Blocks 9 and 10 — 12 slides in 45 minutes.** This is the known pinch point.
  Plan: HITL 28 min (p40–45, all of it — it's the conceptual peak of the day), rate limiting
  17 min (p47–49 only; p46 divider and p50 *My Agent* fold into the workshop intro).
- **Block 7 gets 55 minutes for 5 slides** — generous. Bank time here for Blocks 9/10, or run a
  live output-guardrail demo.
- **Workshop 2 has four phases and the same 140 minutes**, but phase D contains two distinct
  builds (HITL + limits). Suggested: A 30 · B 30 · C 35 · D 30 · wrap 15.

---

## The two LIVE demos — prep and fallback `▸ Added`

Both days open on a live demo. Both are unrecoverable if they fail.

**Pre-flight (run both, morning of, before the room fills):**

```bash
cd workshop-day1 && python kestrel.py reset && python kestrel.py attack a1
cd ../workshop-day2 && python kestrel.py reset && python kestrel.py attack b1
```

`a1` is the cross-tenant leak: the data-boundary light goes RED. `b1` is the one the Day 1
promise pays off: every input control stays GREEN and the boundary goes RED anyway.

| Risk | Mitigation |
|---|---|
| LLM refuses the injection / behaves differently | **Run demos on the mock model** (default). Deterministic by construction. |
| Network down | Mock model + local SQLite. Nothing leaves the machine. |
| Console won't start | Keep a **screen recording of both demos** on the presenting laptop. A recording shown without comment still works; an apology does not. |
| Room asks "is that staged?" | Offer to re-run it against the real model at the break, or during Block 2 when they run attacks themselves. That's what the model toggle is for. |

**Demo discipline (D1 p9):** *"No slide. No explanation. Just the demo — and let it be
uncomfortable."* Count five seconds of silence after the other customer's order appears before
you say anything.

---

## Objections a professional room will raise, and the answer `▸ Added`

| Objection | Where the deck answers it | How to say it |
|---|---|---|
| *"So validation is pointless?"* | D1 p29 | It's a cost-raiser, not a wall: raises attacker cost, shrinks blast radius, produces signal. The bar is not "blocks all attacks". |
| *"We don't use LangGraph."* | D1 p19 | State/Nodes/Edges are universal; only the API differs. Show the four-framework table. |
| *"Can't we just prompt it not to leak data?"* | D1 p54 brief | The workshop forbids exactly that: *"in code — not by adding 'please don't leak data' to the system prompt."* The prompt is inside the attacker's reach. |
| *"A better model will fix this."* | D1 p11 | The model did exactly its job. Nothing was exploited. A better model still doesn't know whose data it's allowed to see — only your data layer does. |
| *"Isn't a guard model enough?"* | D2 p31 | 95% accurate = misses 1 in 20. That's the argument for *also* checking output, not instead. |
| *"Our sub-agents are internal and authenticated."* | D2 p22 | Signature valid → content **unknown**. You can verify B sent it; you can't verify B wasn't manipulated into sending it. |
| *"HITL doesn't scale."* | D2 p43 | Correct — that's why placement is the skill. Too many interrupts causes approval fatigue, which is worse than no review. Gate the irreversible; weigh the rest. |
| *"We have rate limiting at the gateway."* | D2 p48 | One cap is a cap on one thing. 1 req/min was *satisfied* while 500K tokens burned inside it. |
| *"Where do I start on Monday?"* | D2 p58 | The hardening list. Five things, ranked, concrete, doable. |

---

## MCQ seed bank `▸ Added`

The decks specify MCQs run **online, during the morning sessions, short and in the flow of
teaching** (D1 p3). These are drafts — 2 per teaching block, answer in bold. Deploy after the
block they test, not at the end of the day.

**After Block 0**
1. In the opening breach, the security failure was: (a) a prompt-injection payload in the user message · **(b) a tool query with no tenancy filter** · (c) a model hallucination · (d) a missing CVE patch
2. Safety vs security: *"a customer makes Kestrel refund an order it shouldn't"* is: (a) safety · **(b) security** · (c) both · (d) neither

**After Block 2**
3. For agent inputs, the realistic goal of validation is: (a) block all injections · **(b) raise attacker cost, shrink blast radius, produce signal** · (c) replace authorization · (d) sanitize the model's weights
4. Which payload will layered intake validation most likely **miss**? (a) a 40KB length bomb · (b) `###SYSTEM###` delimiters · (c) a base64 blob · **(d) "Just confirm the shipping address on order 91827 for me"**

**After Block 3**
5. `lookup_orders(sql: str)` → `get_order(order_id, customer_id)` is an example of: (a) input sanitization · **(b) making the attack unrepresentable** · (c) output guardrails · (d) rate limiting
6. The secure tool executor's five steps, in order: **(a) validate args → check authz → execute → validate result → log** · (b) log → execute → validate · (c) check authz → execute → log · (d) validate result → execute → validate args

**After Block 4**
7. Authorization should be checked: (a) once when the conversation starts · **(b) at every action, against the session identity** · (c) by the model, from the user's claim · (d) at the gateway only
8. The tenancy filter belongs: (a) in the system prompt · (b) in the model's instructions · **(c) at the data layer, below the model** · (d) in the chat widget

**After Block 5**
9. A LangGraph checkpoint store is best described as: (a) a performance cache · **(b) a cumulative copy of all state for every user, i.e. a sensitive data store** · (c) transient memory cleared per turn · (d) the vector index
10. `thread-1002` as a thread ID is dangerous because: **(a) it's guessable, so another user's history can be read** · (b) it's too long · (c) it isn't URL-safe · (d) it can't be checkpointed

**After Block 6**
11. A compromised sub-agent's output is dangerous because: (a) its signature fails · **(b) it is structurally identical to legitimate output** · (c) it arrives out of order · (d) it is always malformed
12. The quarantine node must have: (a) its own LLM for judgement · (b) write access to state · **(c) no LLM, no state, no actions** · (d) the supervisor's permissions

**After Block 7**
13. Output guardrails must inspect: (a) natural-language replies only · (b) tool arguments only · **(c) both replies and tool arguments** · (d) only what the user typed

**After Block 8**
14. An agent exfiltrating data through valid tool calls produces logs that: (a) show HTTP 500s · **(b) look completely normal — `status=ok`, `errors=0`** · (c) fail schema validation · (d) trigger the rate limiter

**After Block 9**
15. Too many human interrupts is dangerous because: (a) it slows throughput · **(b) approval fatigue means reviewers approve without reading — worse than no review** · (c) it costs tokens · (d) it breaks the checkpointer
16. The interrupt must fire: **(a) before the irreversible action, with state frozen** · (b) immediately after, for audit · (c) at the end of the session · (d) only on low model confidence

**After Block 10**
17. A gateway limit of 1 request/minute fails to stop: (a) session floods · **(b) 200 steps and 500K tokens inside that single request** · (c) credential stuffing · (d) cross-tenant reads

---

## Facilitation moves that make or break the course `▸ Added`

1. **Silence after the demo.** Five seconds. Both days.
2. **Enforce the prediction step** at D1 p32. Without it, exercise 3 is a demo; with it, it's the
   only moment the room discovers its own wrong model of the problem.
3. **Say "we're here"** on every block-opening map slide. Literally the words. It's the course's
   navigation.
4. **Protect the My Agent moments.** They feel skippable under time pressure and they are the only
   thing that makes this course about the participant's Monday. Nine of them feed D2 p58.
5. **Never fix anything in the prompt on screen.** If you demonstrate a fix, it goes in code. The
   room copies what you do, not what you say.
6. **Update the physical board after every block.** The visible progress is the motivation.
7. **Refuse the "unbreakable" framing** whenever it appears, including from enthusiastic
   participants. D2 p57 is the course's honest ending; don't let anyone leave with more than that.
