"""Kestrel Goat (Day 1 - the edge) - SOLUTION BUILD, central configuration.

The lab branch made every control a runtime toggle, with the vulnerable and the
secure implementation sitting side by side so you could read both and flip
between them. This branch is where that exercise ends up: the vulnerable halves
are deleted, and the controls are simply how the code works.

There is nothing to switch on, which is the point - a control with an off switch
is a control someone will find switched off.

`MECHANISMS` below is documentation, not configuration. The console renders it so
the room can see what is holding, and every entry names the file it lives in.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, asdict

#: What protects this build, and where to read it. Descriptive only.
MECHANISMS: list[dict] = [
    dict(block=2, label="Layered intake validation",        lives_in="agent/intake.py",    tutorial="v02-direct-injection"),
    dict(block=2, label="Provenance tagging of retrieval",  lives_in="agent/retrieval.py", tutorial="v03-indirect-injection"),
    dict(block=3, label="Narrow typed tools",               lives_in="agent/tools.py",     tutorial="v05-tool-argument-injection"),
    dict(block=3, label="URL allowlist (anti-SSRF)",        lives_in="agent/tools.py",     tutorial="v07-ssrf-egress"),
    dict(block=3, label="Tool-result validation",           lives_in="agent/executor.py",  tutorial="v06-tool-result-side-door"),
    dict(block=3, label="Tool executor chokepoint",         lives_in="agent/executor.py",  tutorial="v05-tool-argument-injection"),
    dict(block=4, label="Action-time RBAC (3 levels)",      lives_in="agent/authz.py",     tutorial="v04-authz-at-action-time"),
    dict(block=4, label="Tenancy filter at the data layer", lives_in="agent/db.py",        tutorial="v01-cross-tenant-leak"),
    dict(block=4, label="Credentials out of the context",   lives_in="agent/graph.py",     tutorial="v04-authz-at-action-time"),
]


@dataclass
class Settings:
    # --- model -------------------------------------------------------------------------
    # Three providers, all behind one interface. Nothing in the agent knows which.
    #
    # "mock"        deterministic scripted model. No key, no network, no cost, no
    #               download. Every graded proof uses this, because those must
    #               reproduce identically every single time.
    # "ollama"      a REAL small model running on the student's own laptop. Free,
    #               no API key, offline once pulled.
    # "openrouter"  a real hosted model. Cheapest reliable path when laptops are
    #               locked down or underpowered. Costs a dollar or two per class.
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock")
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    model: str = os.getenv("KESTREL_MODEL", "openai/gpt-4.1-nano")
    openrouter_base: str = os.getenv("OPENROUTER_BASE", "https://openrouter.ai/api/v1")

    # Ollama speaks the OpenAI chat-completions API, so it reuses the same client.
    # llama3.1:8b pulls about 5GB and is the one to teach on. llama3.2:3b is half
    # the download and works too. Others that do tool calling: qwen2.5:7b,
    # mistral-nemo.
    ollama_base: str = os.getenv("OLLAMA_BASE", "http://localhost:11434/v1")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

    @property
    def active_model(self) -> str:
        if self.llm_provider == "mock":
            return "mock"
        return self.ollama_model if self.llm_provider == "ollama" else self.model

    # --- runtime -----------------------------------------------------------------------
    db_path: str = os.getenv("KESTREL_DB", "data/kestrel.db")
    checkpoint_path: str = os.getenv("KESTREL_CHECKPOINTS", "data/checkpoints.db")
    max_steps: int = int(os.getenv("KESTREL_MAX_STEPS", "12"))

    # --- limits (block 10) -------------------------------------------------------------
    limit_sessions_per_min: int = 10
    limit_steps_per_session: int = 6
    limit_tokens_per_session: int = 40_000
    limit_tokens_per_day: int = 500_000
    limit_cost_ceiling_usd: float = 1.00

    # --- HITL (block 9) ----------------------------------------------------------------
    refund_autonomous_ceiling_cents: int = 5_000   # $50; above this a human approves

    def snapshot(self) -> dict:
        d = asdict(self)
        d.pop("openrouter_api_key", None)          # never render a key into a template
        return d


settings = Settings()
