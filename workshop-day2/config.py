"""Kestrel Goat (Day 2 - the interior) - SOLUTION BUILD, central configuration.

    Day 1 secured the edge. Day 2 assumes all of it was bypassed.

The lab branch made all eighteen controls runtime toggles - the nine Day 1 ones
locked on, the nine interior ones dark until you built them. This branch is where
that exercise ends up: the vulnerable halves are deleted, and CONTAIN, DETECT and
JUDGE are simply how the code works.

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
    # ---- Day 1, the edge -------------------------------------------------------------
    dict(day=1, block=2,  label="Layered intake validation",          lives_in="agent/intake.py",     tutorial="v02-direct-injection"),
    dict(day=1, block=2,  label="Provenance tagging of retrieval",    lives_in="agent/retrieval.py",  tutorial="v03-indirect-injection"),
    dict(day=1, block=3,  label="Narrow typed tools",                 lives_in="agent/tools.py",      tutorial="v05-tool-argument-injection"),
    dict(day=1, block=3,  label="URL allowlist (anti-SSRF)",          lives_in="agent/tools.py",      tutorial="v07-ssrf-egress"),
    dict(day=1, block=3,  label="Tool-result validation",             lives_in="agent/executor.py",   tutorial="v06-tool-result-side-door"),
    dict(day=1, block=3,  label="Tool executor chokepoint",           lives_in="agent/executor.py",   tutorial="v05-tool-argument-injection"),
    dict(day=1, block=4,  label="Action-time RBAC (3 levels)",        lives_in="agent/authz.py",      tutorial="v04-authz-at-action-time"),
    dict(day=1, block=4,  label="Tenancy filter at the data layer",   lives_in="agent/db.py",         tutorial="v01-cross-tenant-leak"),
    dict(day=1, block=4,  label="Credentials out of the context",     lives_in="agent/graph.py",      tutorial="v04-authz-at-action-time"),
    # ---- Day 2, the interior. CONTAIN - DETECT - JUDGE. ------------------------------
    dict(day=2, block=5,  label="Trusted/untrusted state split",      lives_in="agent/state.py",      tutorial="v08-state-poisoning"),
    dict(day=2, block=5,  label="Random thread IDs bound to identity",lives_in="agent/memory.py",     tutorial="v09-thread-id-guessing"),
    dict(day=2, block=5,  label="Memory write governance",            lives_in="agent/memory.py",     tutorial="v10-memory-landmine"),
    dict(day=2, block=6,  label="Quarantine node on sub-agents",      lives_in="agent/quarantine.py", tutorial="v11-trust-inheritance"),
    dict(day=2, block=6,  label="Privilege separation reader/actor",  lives_in="agent/helpers.py",    tutorial="v11-trust-inheritance"),
    dict(day=2, block=7,  label="Output guardrails (says + does)",    lives_in="agent/guardrails.py", tutorial="v12-silent-exfiltration"),
    dict(day=2, block=8,  label="Behavioural observability",          lives_in="agent/telemetry.py",  tutorial="v13-looks-like-normal-traffic"),
    dict(day=2, block=9,  label="Human interrupt before the action",  lives_in="agent/hitl.py",       tutorial="v14-irreversible-action"),
    dict(day=2, block=10, label="Five rate & cost limits",            lives_in="agent/limits.py",     tutorial="v15-cost-exhaustion"),
]


@dataclass
class Settings:
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock")
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    model: str = os.getenv("KESTREL_MODEL", "meta-llama/llama-3.1-8b-instruct")
    openrouter_base: str = os.getenv("OPENROUTER_BASE", "https://openrouter.ai/api/v1")
    # llama3.1:8b lands all eight interior attacks. llama3.2:3b is half the
    # download but will not write the memory in b4 - see the README model table.
    ollama_base: str = os.getenv("OLLAMA_BASE", "http://localhost:11434/v1")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

    db_path: str = os.getenv("KESTREL_DB", "data/kestrel.db")
    checkpoint_path: str = os.getenv("KESTREL_CHECKPOINTS", "data/checkpoints.db")
    max_steps: int = int(os.getenv("KESTREL_MAX_STEPS", "12"))

    # Block 10 - five independent levels. One cap is a cap on one thing only.
    limit_sessions_per_min: int = 5
    limit_steps_per_session: int = 6
    limit_repeat_cycle: int = 3
    limit_tokens_per_session: int = 3_000
    limit_tokens_per_day: int = 30_000
    limit_cost_ceiling_usd: float = 0.25

    # Block 9 - the three-factor test, in a number. Small refund autonomous;
    # large refund interrupted.
    refund_autonomous_ceiling_cents: int = 5_000

    @property
    def active_model(self) -> str:
        if self.llm_provider == "mock":
            return "mock"
        return self.ollama_model if self.llm_provider == "ollama" else self.model

    def snapshot(self) -> dict:
        d = asdict(self)
        d.pop("openrouter_api_key", None)
        return d


settings = Settings()
