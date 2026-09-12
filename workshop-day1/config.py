"""Kestrel Goat (Day 1 - the edge) - central configuration.

Every security control in this lab is a runtime toggle. Vulnerable is the DEFAULT:
the app ships broken on purpose, exactly like OWASP NodeGoat ships broken on purpose.

Each toggle selects between two implementations that BOTH live in the source tree:

    vulnerable_check_intake()   <-- what most teams actually shipped
    secure_check_intake()       <-- what the course teaches

Read them side by side. Flip the toggle. Re-run the attack. Watch the light.

Toggles can be set three ways (later wins):
    1. defaults below
    2. environment variables      SECURE_TENANCY=1
    3. the control room UI        POST /api/controls
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field, asdict

# --------------------------------------------------------------------------------------
# The 18 controls, grouped the way the course teaches them.
# key -> (day, block, short label, which tutorial explains it)
# --------------------------------------------------------------------------------------
CONTROLS: dict[str, dict] = {
    # Day 1 — the edge
    "SECURE_INTAKE":            dict(day=1, block=2, label="Layered intake validation",        tutorial="v02-direct-injection"),
    "SECURE_PROVENANCE":        dict(day=1, block=2, label="Provenance tagging of retrieval",  tutorial="v03-indirect-injection"),
    "SECURE_TOOLS":             dict(day=1, block=3, label="Narrow typed tools",               tutorial="v05-tool-argument-injection"),
    "SECURE_EGRESS":            dict(day=1, block=3, label="URL allowlist (anti-SSRF)",        tutorial="v07-ssrf-egress"),
    "SECURE_TOOL_RESULTS":      dict(day=1, block=3, label="Tool-result validation",           tutorial="v06-tool-result-side-door"),
    "SECURE_EXECUTOR":          dict(day=1, block=3, label="Secure tool executor chokepoint",  tutorial="v05-tool-argument-injection"),
    "SECURE_AUTHZ":             dict(day=1, block=4, label="Action-time RBAC (3 levels)",      tutorial="v04-authz-at-action-time"),
    "SECURE_TENANCY":           dict(day=1, block=4, label="Tenancy filter at the data layer", tutorial="v01-cross-tenant-leak"),
    "SECURE_NO_CREDS_IN_STATE": dict(day=1, block=4, label="Credentials out of the context",   tutorial="v04-authz-at-action-time"),
}

# Named profiles, for `make day1-secure` and the console preset buttons.
PROFILES: dict[str, list[str]] = {
    "vulnerable": [],          # how the app ships. Every attack works.
    "secure":     list(CONTROLS),   # the build Workshop 1 asks you to reach.
}


@dataclass
class Settings:
    # --- model -------------------------------------------------------------------------
    # Three providers, all behind one interface. Nothing in the agent knows which.
    #
    # "mock"        deterministic scripted model. No key, no network, no cost, no
    #               download. Every live demo and every graded proof uses this,
    #               because those must reproduce identically every single time.
    # "ollama"      a REAL small model running on the student's own laptop. Free,
    #               no API key, offline once pulled. Best of both worlds for the
    #               "watch a genuine model get steered" moment - if the laptop
    #               can spare ~4GB of RAM.
    # "openrouter"  a real hosted model. Cheapest reliable path when laptops are
    #               locked down or underpowered. Costs a dollar or two per class.
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock")
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    model: str = os.getenv("KESTREL_MODEL", "openai/gpt-4.1-nano")
    openrouter_base: str = os.getenv("OPENROUTER_BASE", "https://openrouter.ai/api/v1")

    # Ollama speaks the OpenAI chat-completions API, so it reuses the same client.
    # llama3.2:3b supports tool calling and pulls in about 2GB. Alternatives that
    # also do tools: qwen2.5:3b, qwen2.5:7b, mistral-nemo.
    ollama_base: str = os.getenv("OLLAMA_BASE", "http://localhost:11434/v1")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

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

    controls: dict[str, bool] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for key in CONTROLS:
            self.controls.setdefault(key, os.getenv(key, "0").lower() in ("1", "true", "yes", "on"))

    # -- toggle plumbing ---------------------------------------------------------------
    def on(self, key: str) -> bool:
        """True when the SECURE implementation of `key` is active."""
        if key not in CONTROLS:
            raise KeyError(f"unknown control {key!r}")
        return self.controls[key]

    def set(self, key: str, value: bool) -> None:
        if key not in CONTROLS:
            raise KeyError(f"unknown control {key!r}")
        self.controls[key] = bool(value)

    def apply_profile(self, name: str) -> None:
        if name not in PROFILES:
            raise KeyError(f"unknown profile {name!r}; try {list(PROFILES)}")
        wanted = set(PROFILES[name])
        for key in CONTROLS:
            self.controls[key] = key in wanted

    def snapshot(self) -> dict:
        d = asdict(self)
        d.pop("openrouter_api_key", None)          # never render a key into a template
        return d


settings = Settings()
