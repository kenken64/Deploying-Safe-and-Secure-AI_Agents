# Setup - tools for Day 1 and Day 2

Both workshops run from the same machine setup. Install once, both days work.

## The short answer

| Tool | Version | Required? | What it is for |
|---|---|---|---|
| **[Python](https://www.python.org/downloads/)** | 3.10 or newer | **Yes - the only hard requirement** | Runs both labs. |
| **[OpenCode](https://opencode.ai)** + **[Go subscription](https://opencode.ai/go?ref=2QN28RR7HV)** | latest | **Yes** | The agent students use in the workshops, on a real coding model. See below. |
| [Git](https://git-scm.com/downloads) | any | Yes | Clone the repo; switch to `ollama-real-model-support`. |
| [VS Code](https://code.visualstudio.com/) + [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers), **or** [GitHub Codespaces](https://github.com/features/codespaces) | - | Optional path | Zero-install environment. Builds both labs for you. |
| [Docker](https://www.docker.com/get-started/) | any recent | Optional path | For locked-down laptops that cannot install Python. |
| [Ollama](https://ollama.com/download) | any recent | Optional | A real local model (`llama3.1:8b`). Not needed for the default mock. |
| [OpenRouter API key](https://openrouter.ai/keys) | - | Optional | A real hosted model (`openai/gpt-4.1-nano`). ~$1-3 per class. |

The labs' default model is the deterministic **mock**: no API key, no network, no extra
install. Both days run end to end on it.

---

## Student install: OpenCode + Go subscription

Every student installs the OpenCode agent and connects it to a real coding model through
an OpenCode Go subscription ($10/month).

**1. Install OpenCode**

macOS / Linux / WSL:

```bash
curl -fsSL https://opencode.ai/install | bash
```

Windows: install inside [WSL](https://learn.microsoft.com/windows/wsl/install) using the
same command - OpenCode runs best there. Other install methods (npm, bun, brew, paru)
are listed at [opencode.ai](https://opencode.ai).

**2. Subscribe to Go** - **use the course referral link:**

👉 **https://opencode.ai/go?ref=2QN28RR7HV**

Sign in, subscribe, and copy your API key.

**3. Connect OpenCode to Go**

```
opencode          # open the TUI
/connect          # select "OpenCode Go", paste your API key
```

**4. Select the course model**

```
/models           # pick a Kimi model, K2.6 or newer
```

| Choose | Notes |
|---|---|
| `opencode-go/kimi-k2.7-code` | **Recommended** - best Kimi coding model on Go, generous limits |
| `opencode-go/kimi-k2.6` | acceptable minimum |
| `opencode-go/kimi-k3` | newest, but a much lower monthly allowance |

> Any Kimi **K2.6 or higher** works for the course. Do not pick anything older.

---

## Path 1 - native (recommended)

Needs only Python 3.10+. You never activate a virtualenv - every command re-executes
itself inside `.venv`.

```bash
git clone <this repo> && cd Deploying-Safe-and-Secure-AI_Agents
git switch ollama-real-model-support

cd workshop-day1
python kestrel.py setup      # venv + dependencies + seeded SQLite  (~1 min)
python kestrel.py doctor     # checks everything, ends in READY

cd ../workshop-day2
python kestrel.py setup
python kestrel.py doctor
```

> macOS/Linux may need `python3` instead of `python`.
> Debian/Ubuntu: if venv creation fails, `sudo apt install python3-venv`.

`kestrel.py setup` installs these Python packages for you (from
`workshop-day*/requirements.txt`) - you do not install anything by hand:

| Package | Used for |
|---|---|
| fastapi, uvicorn | storefront, chat widget, control room, tutorial server |
| jinja2 | page templates |
| httpx | model provider calls and SSRF gadget |
| pydantic | typed primitives (Content, Principal, ToolCall, ...) |
| langgraph, langgraph-checkpoint-sqlite | the agent graph and its checkpoint store |
| pytest | the proof tests (20 for Day 1, 30 for Day 2) |

## Path 2 - dev container (nothing to install)

Needs **VS Code + Dev Containers extension** or **GitHub Codespaces**.

Open the repo, pick a configuration when offered:

| Configuration | Opens on |
|---|---|
| **Kestrel Goat - Day 1 (the edge)** | `workshop-day1` (default) |
| **Kestrel Goat - Day 2 (the interior)** | `workshop-day2` |

Either one builds Python 3.12, installs **both** labs, seeds both databases, runs
`doctor` on each and forwards port 8000. You never run `setup` yourself, and your host
`.venv` is left alone (the container keeps its own in a named volume).

Do the first build **the day before** the workshop, not at 9am - the first build pulls
a Python image.

## Path 3 - Docker (locked-down laptop)

```bash
cd workshop-day1   # or workshop-day2
docker build -t kestrel-goat-day1 .
docker run --rm -p 8000:8000 kestrel-goat-day1
```

## Optional: a real local model (Ollama)

Only needed if you want to run the attacks against a real LLM. The mock is the default
and is what both live demos use.

```bash
ollama pull llama3.1:8b      # 4.9GB - pull it the week before, not on venue wifi
LLM_PROVIDER=ollama OLLAMA_MODEL=llama3.1:8b python kestrel.py attack a2
```

Use `llama3.1:8b` for Day 2 - it lands the whole interior catalogue. `llama3.2:3b`
(2GB) is the smaller alternative for Day 1.

Inside the dev container: run Ollama on your **host** - the container already points at
`host.docker.internal`.

## Optional: a real hosted model (OpenRouter)

```bash
export OPENROUTER_API_KEY=sk-or-...
LLM_PROVIDER=openrouter KESTREL_MODEL=openai/gpt-4.1-nano python kestrel.py attack a2
```

---

## Verify

```bash
cd workshop-day1 && python kestrel.py reset && python kestrel.py test    # 20 passed
cd ../workshop-day2 && python kestrel.py reset && python kestrel.py test # 30 passed
```

Then `python kestrel.py run` in either lab and open:

| | |
|---|---|
| Storefront | http://127.0.0.1:8000/ |
| Control room | http://127.0.0.1:8000/console |
| Tutorials | http://127.0.0.1:8000/tutorial |

## Troubleshooting

| Symptom | Fix |
|---|---|
| `python: command not found` (macOS/Linux) | use `python3` |
| `No .venv yet` | `python kestrel.py setup` |
| `Address already in use` | `python kestrel.py run --port 8010` |
| Ollama selected but nothing happens | `python kestrel.py doctor` - checks running, pulled, and that the chat endpoint answers |
| Everything is broken | `python kestrel.py reset` reseeds the database |

> **Safety:** both labs are deliberately vulnerable. Run on `127.0.0.1` only; never
> deploy either folder anywhere.
