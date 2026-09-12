# 06 · What's built, what's left, and defects in the decks

Status as of this build. `▸ Deck` = on the slides. `▸ Added` = written for these notes or
the lab.

---

## What the decks assume exists — and what now does

The slides repeatedly point at a lab and a console (*"run the attack, watch the panel go
green"*, *"lab repo & prompt templates: shared in the workshop"*). All of it is now built.

| Assumed by the deck | Status | Where |
|---|---|---|
| The Kestrel agent, LangGraph, e-commerce domain | **built** | `workshop-day{1,2}/agent/graph.py` |
| The control room with named lights | **built** — 12 lights, live trace, toggles | `/console` |
| *Input validation · Content filter · Schema check · Data boundary* (D2 p6) | **built**, exact names | `agent/telemetry.py` |
| The opening cross-tenant demo (D1 p9) | **built**, deterministic | `attack a1` |
| *"The attack I promised you"* (D2 p5) | **built**, deterministic | `attack b1` |
| Poisoned help-centre article (D1 p32) | **built** — two of them | `KB-004`, `KB-005` |
| Five validator payloads, predict-first (D1 p32) | **built** | `attack a4` |
| `lookup_orders(sql)` → narrow tool refactor (D1 p43) | **built**, both versions in source | `agent/tools.py` |
| The secure tool executor, five steps (D1 p41) | **built** | `agent/executor.py` |
| Tenancy filter below the model (D1 p50) | **built** | `agent/db.py` |
| Checkpoint store to threat-model (D2 p18) | **built**, visible in the console | `agent/memory.py` |
| Two helper agents (D2 p21) | **built**, with declared tiers | `agent/helpers.py` |
| Quarantine node (D2 p25) | **built** — no LLM, no state, no actions | `agent/quarantine.py` |
| HITL interrupt + approver (D2 p44) | **built**, with a frozen call | `agent/hitl.py`, `/console` |
| Five rate/cost limits (D2 p49) | **built** | `agent/limits.py` |
| Step-by-step fix walkthroughs | **built** — 17 tutorials, run-fix-prove in-page | `tutorials/` |
| Proof that each fix works | **built** — 50 tests across both days | `tests/` |

### Beyond the decks `▸ Added`

- **Three model providers** (`mock`, `ollama`, `openrouter`) with a live switch, a visible
  header badge, and a `why` line naming the exact words that steered each decision.
- **`python kestrel.py doctor`** — a per-laptop readiness check for macOS, Windows and Linux.
- **Four extra attacks** the decks don't name: `a4` beat-the-validator end-to-end, `a6`
  tool-result side door, `a7` SSRF, `b3` thread-ID guessing.
- **Tests assert both directions** — each attack must *land* against the vulnerable build
  and *stop* against the hardened one, so a broken demo fails CI rather than the classroom.

---

## Still to do

| | Item | Why it matters | Effort |
|---|---|---|---|
| 1 | **The online MCQs** | The decks specify them (D1 p3) but no platform is chosen. A 17-question seed bank is in `04-facilitator-playbook.md`; it needs to be loaded into whatever tool the room uses, and set to fire *after each block*, not at day's end. | half a day |
| 2 | **Printed Attack Board** | D1 p16: *"This goes on the wall now and it stays up."* Needs an A1/A3 print with the six rows and two empty columns. | 1 hour |
| 3 | **Printed *My Agent* sheet** | Nine prompts across two days, converging on the D2 p58 hardening list. Participants will not keep them on scrap paper. | 1 hour |
| 4 | **Screen recordings of both demos** | The single-point-of-failure mitigation in `04-facilitator-playbook.md`. Record `attack a1 --vulnerable` and `attack b1 --day1-only` on the presenting laptop. | 30 min |
| 5 | **A dry run with real laptops** | `doctor` covers the common cases, but corporate proxies, Windows Store Python, and locked-down execution policies surface only on real machines. | 2 hours |
| 6 | **Decide the Ollama policy** | If students are told to use it, the model must be pulled *before* the day — a 4.9GB download (`llama3.1:8b`, the default) × 20 laptops on venue wifi will not happen live. `llama3.2:3b` halves that but drops a3 and b4; see the model tables in both READMEs. | a decision |

### Optional, if you want them

- A `--team <name>` flag so each team's console is separately addressable during the swap.
- A third helper agent, so the inheritance-path activity has more than one answer.
- A Day 3 idea the decks gesture at but never cover: **supply chain** — the MCP server, the
  tool definition, and the model weights themselves.

---

## Defects in the decks worth fixing before the next run `▸ Added`

Small things, all of them cosmetic or navigational. Listed because they are cheap to fix
and mildly confusing live.

### 1. Two Day 1 section dividers carry no block number

Day 1 numbers its blocks 0, 1, 2 — then **p36 "Tool security"** and **p45 "Authorization at
action time"** appear with no `BLOCK n` label, and Day 2 resumes at `BLOCK 5`. The implied
numbering is Block 3 and Block 4. Add the labels, or the room loses the thread of *"we're
here."*

### 2. Footer slide numbers drift from the actual page count

| Deck | Pages 1–5/6 | From then on |
|---|---|---|
| Day 1 | footer matches | footer = PDF page **− 3** (p7 reads "4", p20 reads "17") |
| Day 2 | footer matches | footer = PDF page **− 2** (p9 reads "7") |

Day 1 p6 is a further outlier — it reads "2", suggesting a slide imported from another deck
without renumbering. Harmless on screen, but it makes *"go back to slide 14"* ambiguous.
**These notes therefore reference PDF page numbers throughout.**

### 3. Two blocks share one 45-minute slot on Day 2

The agenda (D2 p4) puts **Human-in-the-loop** and **Rate limiting & abuse prevention** both
in 1:40–2:25 — twelve slides in 45 minutes. Either split them explicitly in the agenda or
accept that Block 10 is a 15-minute block, and plan which slides go. A suggested split is
in `04-facilitator-playbook.md`.

### 4. Two afternoon blocks are tight against their activities

- **Day 1 Block 3** (Tool security): 50 minutes containing a 25-minute activity → 25 minutes
  for 8 slides.
- **Day 1 Block 4** (Authorization): 35 minutes containing a 12-minute activity.

Both are workable, but pre-decide what you cut. Suggestions are in the playbook.

### 5. The nine *My Agent* moments aren't announced as a deliverable

D2 p58 explicitly maps eight earlier prompts into the final hardening list — but nothing on
Day 1 tells participants their private notes are building toward anything. Say it at D1 p3,
or half the room arrives at p58 with nothing to rank.

### 6. Day 1's board lists four rows; the lab ships seven attacks

Not an error — the extra three (`a4`, `a6`, `a7`) are deliberate stretch material. But if
you want the physical board to match the lab, add the rows.
