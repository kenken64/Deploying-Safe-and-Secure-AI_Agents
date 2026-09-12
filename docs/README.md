# Developing Secure AI Agents — Course Notes

Working notes derived from the two decks in `../slides/`:

| Deck | File | Pages |
|---|---|---|
| Day 1 — *The agent will be steered* | `Developing-Secure-AI-Agents-Day1-v1.1.pdf` | 61 |
| Day 2 — *Assume the edge already failed* | `Developing-Secure-AI-Agents-Day2-v1.0.pdf` | 60 |

The runnable labs those decks assume live in [`../workshop-day1/`](../workshop-day1/) and
[`../workshop-day2/`](../workshop-day2/).

These notes exist to let you **teach** the course, not just read it: what each slide is doing,
what to say, when to shut up and let the room be uncomfortable, how the activities are timed,
and what the workshop lab has to provide for the "done when" criteria to be checkable.

## Read in this order

**New to the repo? Read [`../INSTRUCTORS.md`](../INSTRUCTORS.md) before any of these.** It
covers the branches, machine setup, the model decision and the demo scripts; these files
are the teaching content it points into.

| If you are… | Read |
|---|---|
| Lead instructor, first time | `../INSTRUCTORS.md` → `00` → `01` → `02` → `04` |
| Co-instructor / second pair of hands | `00` → `04` → `05` |
| Building on the Kestrel lab + console | `00` → `03` → `05` → `06`, then `../workshop-day1/README.md` |
| Writing the MCQs | `01`, `02` (the "trap" callouts) → `04` (seed bank) |
| A participant wanting the substance | `00` → `03` |

## The files

- **`00-course-overview.md`** — the spine. Thesis, Kestrel, the eight surfaces, the attack
  board, the teaching rituals, both agendas, both sets of learning objectives.
- **`01-day1-the-edge.md`** — Day 1 block by block, with facilitator notes.
- **`02-day2-the-interior.md`** — Day 2 block by block, with facilitator notes.
- **`03-security-reference.md`** — the technical content as a reference: every control the
  course teaches, with illustrative code.
- **`04-facilitator-playbook.md`** — run-of-show, demo prep, timing risks, objections and
  answers, MCQ seed bank.
- **`05-workshop-guide.md`** — both workshops in detail: briefs, phases, proof criteria,
  attack-swap mechanics, assessment rubric.
- **`06-gaps-and-build-list.md`** — what is built (the labs), what is still to do, and
  defects in the decks worth fixing before the next run.

## Conventions

- **Slide references are PDF page numbers** (`D1 p32` = page 32 of the Day 1 PDF). The decks'
  own footer numbers drift from the PDF page count — see `06-gaps-and-build-list.md`.
- **`▸ Deck`** marks content that is on the slides.
- **`▸ Added`** marks something written for these notes — an inference, a recommendation,
  or illustrative code. It is not on any slide. Nothing in the `Added` material should be
  presented as the course's official position without the instructors' say-so.
- Code in `03-security-reference.md` is **all `▸ Added`** unless quoted as a fragment from a
  slide. The decks carry signatures and three-line sketches, not working code.
