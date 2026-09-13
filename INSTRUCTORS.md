# Instructor start-here — the SOLUTION branch

**This branch is the answer key.** It is not the branch you teach from and it is not the
branch you hand out on the morning of day one.

You want [`ollama-real-model-support`](../../tree/ollama-real-model-support) for that, and
its own `INSTRUCTORS.md` — reading order, machine setup, the model decision, and the
scripts for both live demos.

```bash
git switch ollama-real-model-support     # the lab. Teach from here.
git switch ollama-solution               # this. The finished build.
```

This page covers the four things you do with the answer key: **read it, show it, grade
with it, and know what it deliberately does not do.**

---

## 1. What this branch is

Both workshops, finished. Every control that the lab leaves as a runtime toggle is in the
code here, and the vulnerable half of each pair is deleted rather than switched off.

| | `ollama-real-model-support` | this branch |
|---|---|---|
| Day 1 `attack all` | all 7 land | **all 7 stop** |
| Day 2 `attack all` | all 8 land past the edge | **all 8 stop** |
| Tests | 20 + 30 — each attack LANDS, then STOPS | 14 + 22 — each attack STOPS |
| Controls | 18 runtime toggles | 18 mechanisms, in the code |
| `--secure`, `--control`, `--day1-only` | how you turn them on | gone; nothing to turn on |
| `/console` | a switchboard | a panel naming each mechanism and its file, in red |

Run it exactly like the lab:

```bash
cd workshop-day1
python kestrel.py setup      # if this is a fresh clone
python kestrel.py test       # 14 passed
python kestrel.py attack all # 7/7 stopped
```

Or open the repo in a dev container — VS Code with the Dev Containers extension, or GitHub
Codespaces — and pick **Kestrel Goat SOLUTION - Day 1** or **- Day 2**. Either installs
both labs, seeds both databases and forwards port 8000, and the banner it prints says
plainly that this is the answer key rather than the lab, so nobody provisions the wrong
branch on the morning of day one. Config is in [`.devcontainer/`](.devcontainer/).

The container keeps its `.venv` in a named volume, so it never disturbs a virtualenv you
built on your host — you can have the lab checked out and running natively while the
answer key runs in a container.

Both configurations have been built and run end to end (`devcontainer up`, linux/aarch64,
Python 3.12): 14 + 22 tests pass and all 15 attacks stop inside the container.

A **LANDED** result here is a regression, not a lesson. The runner says so and exits
non-zero, so this branch is also the thing to point CI at.

---

## 2. Reading it

One command is the whole answer key:

```bash
git diff ollama-real-model-support..ollama-solution -- workshop-day1/agent workshop-day2/agent
```

180 insertions, 566 deletions — the shape of the answer is *deletion*, and that is worth
saying out loud to the room. Diff against `main` instead and you also pick up the Ollama
work this branch was cut from, which is a separate change.

Where each fix lives:

```bash
python kestrel.py controls   # every mechanism, and the file to read it in
```

The three that carry the most weight, if you only read three:

| Read | Because |
|---|---|
| `agent/db.py` → `orders_for()` | The tenancy filter, below the model. There is no longer a code path that returns another customer's rows — not a guarded one, none. |
| `agent/tools.py` → `TOOLS` | `lookup_orders(sql)` is gone. The cross-tenant query is not filtered; it is **unrepresentable**. |
| `agent/executor.py` → `execute()` | One chokepoint, five steps, no second path to route around it. |

---

## 3. When to show it

| Moment | Show it? |
|---|---|
| Before the workshop | **No.** |
| A team is genuinely stuck mid-phase | One file, on your laptop, at their table. Not the branch. |
| Before the attack swap | **No.** The swap is worthless if both teams have the same answers. |
| At the Day 1 debrief, after the swap | Yes. |
| At the Day 2 debrief | Yes. |
| In the handout afterwards | Yes — this is the version they take back to work. |

Do not put the branch name in the participant handout before the swap. It takes one
person finding it to cost you the exercise.

**How to show it without wrecking your own setup.** You will usually want the lab open at
the same time — theirs to compare against, yours to diff. Two clean ways:

```bash
git worktree add ../kestrel-solution ollama-solution   # both branches, side by side
cd ../kestrel-solution/workshop-day1 && python kestrel.py setup
```

(The worktree is a fresh checkout, so it needs its own `setup` — the `.venv` does not come
with it.) Or open this branch in its own dev container. Its `.venv` lives in a named volume, so a
native lab checkout on the same machine keeps working untouched while the answer key runs
in the container. Either beats switching branches on the one checkout you are demoing
from.

---

## 4. Grading with it

The rubric is in [`docs/05-workshop-guide.md`](docs/05-workshop-guide.md). This branch
makes two parts of it mechanical.

**Does their build actually hold?** Run their repo's own tests, then the catalogue:

```bash
python kestrel.py attack all --secure   # in THEIR checkout
```

**Did they fix it in the right place?** This is the part worth your judgement, and the
diff is the yardstick. A team can turn every light green and still have missed the lesson:

| They wrote | Verdict |
|---|---|
| A tenancy predicate inside the tool | Works today. Ask them what happens when someone adds a second tool. |
| A tenancy filter in the data layer | Right place — the model cannot reach it. |
| A regex rejecting `CUST-` in the SQL string | Filtered the blank cheque; did not remove it. Ask them to beat their own filter. |
| No `sql` parameter at all | Right answer. Unrepresentable beats validated. |
| "Never reveal other customers' data" in the system prompt | Not a control. This is the one to be firm about. |

That last row is the whole course, so it is worth having the sentence ready:

> "That instruction is in the same context window as the attacker's instruction, and the
> model cannot tell which of you wrote it. You have not built a control; you have made a
> request."

---

## 5. The debrief — what to actually say

Fifteen minutes, after the attack swap, both days. The point is not to reveal the answers
— they have mostly found them — it is to name the shape.

**DO** — put the diff on screen. `git diff --stat` first, so they see the numbers before
the code.

**SAY:**

> "Here is every fix in this course, in one diff. Before you read a line of it, look at
> the numbers at the bottom: a hundred and eighty lines added, five hundred and sixty-six
> deleted.
>
> That is not a coincidence and it is not me being clever. Almost every fix in two days
> was **taking something away**. The SQL parameter. The second code path. The `params`
> dict. The field that let untrusted text into a trusted zone.
>
> Nobody gets promoted for deleting a parameter. Do it anyway."

**PAUSE.**

**DO** — open `agent/tools.py` next to the lab version.

**SAY:**

> "Yesterday this tool took a SQL string. Now it takes an order id matching
> `^ORD-\d{6}$`, and the customer id comes from the session — the model never sees it and
> cannot supply it.
>
> Notice what we did *not* do. We did not write a smarter filter on the SQL string. Every
> filter is a bet that you thought of the attack. The tool has no `sql` parameter now, so
> the cross-tenant query is not blocked — there is no way to say it."

**PAUSE.**

**DO** — `python kestrel.py controls`.

**SAY:**

> "One more thing about this branch, and it is the reason it exists as a separate branch
> at all.
>
> In the lab, every one of these was a toggle. Here there is no toggle. Not because
> toggles are untidy — because a control with an off switch is a control that will
> eventually be found switched off. In a config file, in a staging environment, in an
> incident at two in the morning when someone needs the thing to just work.
>
> When you take this back to your own agent: the fix is not a flag. The fix is that the
> unsafe path is not in the codebase."

**Then the close (Day 2):**

> "Assume the model is already compromised. Make sure that assumption isn't catastrophic.
> You have now done both halves of that sentence. Constrain what it can reach — that was
> yesterday. Contain, detect, and keep a human on the irreversible — that was today."

---

## 6. What this branch deliberately does not do

**The tutorials are stale, on purpose.** All seventeen walk you to a *"flip `SECURE_X` and
re-run"* step, and there is no switch here to flip. They describe the journey to this
build, so they live on the lab branch; step 3 of each tutorial page says so, and the
attack catalogue keeps its `SECURE_*` names because those are the vocabulary the slides
and the tutorials use.

**`docs/00`–`06` describe the course, not this build.** They are unchanged and still
correct as teaching notes — but their pre-flight commands assume the lab, where the
demos land. Run both live demos from `ollama-real-model-support`.

**It is still not deployable.** The unscoped SQL and the blank-cheque tool are gone, but
the seeded injection payloads are still in the store, the network calls are simulated, and
nothing here has been through the review a real support agent needs. It is a teaching
model of a support agent. Bind to `127.0.0.1`.

---

## 7. When something breaks

| Symptom | Fix |
|---|---|
| `No .venv yet` | `python kestrel.py setup` |
| `ModuleNotFoundError` | Stale checkout — `git pull`, then `python kestrel.py setup` |
| `python: command not found` (macOS/Linux) | Use `python3` |
| `Address already in use` | `python kestrel.py run --port 8010` |
| An attack **LANDS** | A regression. `python kestrel.py reset`, re-run; if it persists, `git status` — something local changed. |
| `--secure` is not a flag | Correct. There is nothing to secure; it is already the build. |
| A tutorial tells you to flip a control | Expected — see §6. The control is already in the code. |
| Everything is broken | `python kestrel.py reset` reseeds from scratch |
| Dev container: you provisioned the wrong branch | The create banner says which. It reads *"This is the answer key, not the lab"* here. `git switch ollama-real-model-support` and rebuild. |
| Dev container: attacks all stop and you expected them to land | You are on this branch, and that is what it does. The demos live on the lab branch. |
| Dev container: `pip` permission denied | The `.venv` volume came up root-owned and the chown in `.devcontainer/setup.sh` did not run. Rebuild without cache, or `sudo chown -R vscode:vscode workshop-day*/.venv`. |
| Dev container: stale packages after a `requirements.txt` change | The venv volume survives rebuilds by design. `docker volume rm kestrel-day1-venv kestrel-day2-venv`, then rebuild. |
| Dev container: `LLM_PROVIDER=ollama` cannot reach Ollama | Ollama runs on the **host**, not in the container. Check it is listening on all interfaces, not just `127.0.0.1`. |
