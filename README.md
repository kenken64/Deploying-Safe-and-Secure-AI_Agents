# Developing Secure AI Agents - SOLUTION BUILD

> **This branch is the answer key** for the lab on `ollama-real-model-support`.
>
> Three branches, each building on the last: `main` is the original lab;
> `ollama-real-model-support` is that lab with the Ollama/real-model work; this branch
> is that lab, solved.

A two-day workshop for engineers who are shipping agentic systems, built around **Kestrel
Goat** - on the lab branches, a deliberately vulnerable e-commerce support agent in the tradition of
[OWASP NodeGoat](https://github.com/OWASP/NodeGoat), targeting the vulnerabilities that
only exist once a language model can **act**.

Here both workshops are finished. All eighteen controls are in the code, the
`vulnerable_*` halves are deleted, and the runtime toggles are gone - so every attack in
both catalogues stops, and a LANDED result is a regression rather than a lesson.

> **Assume the model is already compromised. Make sure that assumption isn't catastrophic.**

NUS-ISS · Institute of Systems Science, National University of Singapore

---

## Start here

> **Teaching this course?** You want the lab branch, `ollama-real-model-support`, and its
> `INSTRUCTORS.md`. For what to do with *this* branch - when to show the answer key, how to
> grade with it, and the debrief script - see **[`INSTRUCTORS.md`](INSTRUCTORS.md)**.

| | |
|---|---|
| **[Day 1 - The edge](workshop-day1/)** | *The agent will be steered.* Constrain what it can reach and do. |
| **[Day 2 - The interior](workshop-day2/)** | *Assume the edge already failed.* Contain the blast, detect the rest, keep a human on the irreversible. |
| **[Teaching notes](docs/)** | Slide-by-slide understanding, facilitator playbook, security reference, workshop guide. |
| **[Slides](slides/)** | The two decks the course is taught from. |

Each day is a **self-contained, runnable build** with its own README, its own attacks and
its own proof tests. Day 2 carries Day 1's fixes as well as its own - which is exactly
its premise.

```
python kestrel.py doctor      # check this machine (macOS, Windows, Linux)
python kestrel.py setup       # venv + dependencies + seeded SQLite store
python kestrel.py run         # storefront, chat widget, control room, tutorials
```

Nothing to install beyond **Python 3.10+**. No API key. No network. No `make`, no shell
scripts, no virtualenv activation.

---

## What the two days cover

| | **Day 1 - the edge** | **Day 2 - the interior** |
|---|---|---|
| Premise | The agent will be steered | The edge already failed |
| Surfaces | 1 user messages · 2 retrieved content · 3 tool arguments | 4 tool results · 5 external APIs · 6 other agents · 7 state & memory |
| Question | *How do we keep them out?* | *Given they're in: how much damage, will we notice, what did we refuse to automate?* |
| Controls | intake validation · provenance · narrow typed tools · secure executor · RBAC at three levels · the tenancy filter | state split · thread ids · memory governance · quarantine · privilege separation · output guardrails · behavioural observability · human-in-the-loop · rate & cost limits |
| Attacks | 7, `a1`-`a7` | 8, `b1`-`b8` |
| Tutorials | 8 | 9 |
| Proof tests | 20 | 30 |

### The eight surfaces

Every attack in both days is read the same way: **entry point → execution stage → impact.**

| # | Surface | Entry point | Stage | Impact |
|---|---|---|---|---|
| 1 | User messages | chat input | pre-model | direct injection · data disclosure |
| 2 | Retrieved content | help-centre article | retrieval | indirect injection |
| 3 | Tool args (in) | model-built arguments | tool execution | unscoped query · unintended action |
| 4 | Tool results (out) | API / DB response | post-tool, into state | injection via side door |
| 5 | External APIs | payment, shipping | tool execution | SSRF · downstream abuse |
| 6 | Other agents | helper summaries | sub-agent return | trusted-channel injection |
| 7 | State & memory | saved notes | across turns | persistence · credential exposure |
| 8 | The model itself | weights / behaviour | everywhere | why all the others matter |

---

## How this branch differs from the lab

On the lab branches, every control is a runtime switch between two functions that both
live in the source:

```python
def vulnerable_check(text): ...    # what most teams actually shipped
def secure_check(text):     ...    # what the course teaches

def check(text):
    return secure_check(text) if settings.on("SECURE_INTAKE") else vulnerable_check(text)
```

Here there is one function, and it is the second one. The switch, the profiles, the
`--secure` and `--control` flags and the console's toggle panel are all gone, because a
control with an off switch is a control someone will find switched off.

```
git diff ollama-real-model-support..ollama-solution -- workshop-day1/agent workshop-day2/agent
```

That diff is the whole answer key. Diff against `main` instead and you also pick up the
Ollama work this branch was cut from, which is a separate change.

| | `ollama-real-model-support` | this branch |
|---|---|---|
| Day 1 `attack all` | all 7 land | **all 7 stop** |
| Day 2 `attack all` | all 8 land past the edge | **all 8 stop** |
| tests | 20 + 30, each attack LANDS then STOPS | 14 + 22, each attack STOPS |
| `/console` | a switchboard | a panel naming each mechanism and its file |
| tutorials | the lab itself, toggles and all | kept for reference; their "flip SECURE_X" steps have no switch here |

**The control room** (`/console`) is still the two-pane view the course demos from:
customer chat on the left, lights and trace on the right. On this build the lights stay
green.

---

## The model

Three interchangeable providers behind one interface. **The page header always says which
one is running** - students never have to discover that the model is a stand-in.

| Provider | What it is | Key | Cost | Deterministic |
|---|---|---|---|---|
| `mock` (default) | a scripted stand-in that follows instructions found anywhere in its context | none | free | **yes** |
| `ollama` | a real model on the student's own laptop | none | free | no |
| `openrouter` | a real hosted model (`meta-llama/llama-3.1-8b-instruct`) | yes | ~$1-3 per class | no |

The mock is the default because the vulnerability being taught is not *"the LLM is
gullible"* - it is *"the system has no control that survives a gullible model."* So the
model's steerability is held **constant** and the controls are the **variable**: when a
light goes RED to GREEN, the only thing that changed is your code. That is what makes
*"prove it in the console"* a grade rather than a coin flip, and it is why both live demos
use it.

It is also a **glass box**, which a real LLM is not:

```
  model   [mock] chose tool refund(order_id='ORD-100003', amount_cents=189000)
  why     rule 2 authority-claim + refund; matched authority_claim="supervisor access";
          do_refund="issue a refund"
```

**A mock getting steered proves nothing about real LLMs.** Say so out loud, then flip the
switch in the control room and run the same attack against a real one.

### What a real local model actually does

Measured on Ollama, temperature 0, both catalogues, vulnerable then hardened:

| | `llama3.2:3b` (2GB) | `llama3.1:8b` (4.9GB) |
|---|---|---|
| Day 1 vulnerable | a1 a2 a4 a5 a7 land; **a3, a6 do not** | a1 a2 a3 a4 a5 land; **a6, a7 do not** |
| Day 1 hardened | **7/7 stopped** | **7/7 stopped** |
| Day 2 vulnerable | 7/8 land; **b4 does not** | **8/8 land** |
| Day 2 hardened | **8/8 stopped** | **8/8 stopped** |

Read the disagreement, because it is the lesson:

- **`llama3.1:8b` obeys the poisoned help-centre article (a3) and refuses the naked SSRF
  (a7).** `llama3.2:3b` does the exact opposite. The bigger model is *better* at spotting
  the blatant attack and *more* useful to the subtle one. Neither is a control, and the
  hardened build stops all seven either way - which is the entire point of the course.
- **a6 lands on neither.** It needs the model to look an order up and then fetch the
  tracking URL from the row it got back; both local models stop after the lookup and just
  read the URL out to the customer. Demo a6 on the mock.
- **Use `llama3.1:8b` for Day 2** - it lands the whole interior catalogue.

The hardened build stops everything on both models. Only the *vulnerable* side is
model-dependent, and the runner says so rather than crediting a control that is switched
off:

```
attack stopped
NOT stopped by a control - none of a6's controls are on. llama3.1:8b did not take
the bait this run. Real models are not deterministic: re-run it, or try a larger one.
```

---

## The docs

| | |
|---|---|
| [`docs/00-course-overview.md`](docs/00-course-overview.md) | The spine: thesis, Kestrel, eight surfaces, attack board, teaching rituals, agendas |
| [`docs/01-day1-the-edge.md`](docs/01-day1-the-edge.md) | Day 1 block by block, with facilitator notes |
| [`docs/02-day2-the-interior.md`](docs/02-day2-the-interior.md) | Day 2 block by block, with facilitator notes |
| [`docs/03-security-reference.md`](docs/03-security-reference.md) | Every control, with illustrative code |
| [`docs/04-facilitator-playbook.md`](docs/04-facilitator-playbook.md) | Run-of-show, demo prep, timing risks, objections, MCQ seed bank |
| [`docs/05-workshop-guide.md`](docs/05-workshop-guide.md) | Both workshops: briefs, phases, proof criteria, attack swap, rubric |
| [`docs/06-gaps-and-build-list.md`](docs/06-gaps-and-build-list.md) | What is built, what is left, and deck defects worth fixing |

---

## Safety

On the lab branches both labs are **deliberately vulnerable software**: unscoped SQL, a
blank-cheque tool, an SSRF gadget and an unguarded checkpoint store, all on purpose.
This branch removes those, but it is still a **teaching model** rather than a product -
the seeded prompt-injection payloads are still in the store, the "network" calls are
simulated, and nothing here has been through the review a real support agent needs.

- Run them on `127.0.0.1` only. The Docker images bind `0.0.0.0` **because a container
  requires it** - do not publish the port beyond your own machine.
- Never deploy either folder anywhere, on any branch.
- No real credentials, no real customer data, no real payment or shipping endpoints. The
  seeded customers, orders and API hosts are all fictional `*.example` names.
