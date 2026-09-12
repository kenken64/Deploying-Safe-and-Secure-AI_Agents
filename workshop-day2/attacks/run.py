"""Attack runner - Day 2, SOLUTION BUILD.

    python kestrel.py attack b1             run one attack
    python kestrel.py attack all            the whole interior catalogue

There is no --secure flag here, and no --control: this build has one
configuration - edge and interior both - and every attack in the catalogue is
meant to stop against it. A LANDED result is a regression, and the exit code
says so.
"""
from __future__ import annotations

import argparse
import sys

from config import settings
from agent import db, graph, hitl, limits, memory
from agent.models import Principal
from agent.telemetry import board
from attacks.catalogue import ATTACKS, ORDER, Attack

BAR = "=" * 78
DASH = "-" * 78


def principal_for(customer_id: str) -> Principal:
    row = db.customer(customer_id)
    return Principal(id=customer_id, display_name=row["name"] if row else customer_id,
                     role="customer", customer_id=customer_id)


def _fresh() -> None:
    # Each attack starts from the seeded database. A planted memory or an issued
    # refund from the previous run would otherwise make the next result a lie.
    db.reset()
    board.reset()
    graph.SESSIONS.clear()
    limits.reset()
    hitl.PENDING.clear()
    memory.CHECKPOINTS.clear()


def _why_stopped(attack: Attack) -> str:
    """Name the mechanisms that were standing in this attack's way.

    Worth printing even though they are always on: "it did not land" is only
    evidence if you can say what stopped it. On a real model it can also mean the
    model simply did not manage the attack this run, so the wording does not
    promise more than it knows.
    """
    where = ", ".join(attack.closed_by)
    if settings.llm_provider == "mock":
        return f"stopped by: {where}"
    return (f"stopped. In its way: {where}. With a real model, note that "
            f"{settings.active_model} may also simply not have managed it this "
            f"run - re-run to see.")


def run_one(attack: Attack, verbose: bool = True) -> dict:
    _fresh()
    runner = {"thread_guess": _run_thread_guess,
              "memory_landmine": _run_memory_landmine}.get(attack.runner, _run_chat)
    return runner(attack, verbose)


def _header(attack: Attack) -> None:
    print(BAR)
    print(f"{attack.id.upper()}  {attack.name}")
    print(f"{attack.theme} | surface {attack.surface}: "
          f"{attack.entry_point} -> {attack.stage} -> {attack.impact}")
    print(DASH)


def _panel(result: dict, extra: list[str] | None = None) -> None:
    print(DASH)
    for name, level in result["lights"].items():
        mark = {"green": "[ ok ]", "amber": "[warn]", "red": "[BREACH]"}[level]
        print(f"  {mark:<9} {name}")
    for b in dict.fromkeys(result.get("breaches", [])):
        print(f"  !! {b}")
    for f in result.get("findings", []):
        print(f"  ?? detection: {f}")
    for line in extra or []:
        print(f"  {line}")


def _verdict(attack: Attack, landed: bool) -> None:
    print(DASH)
    print("  ATTACK LANDED" if landed else "  attack stopped")
    if landed:
        print(f"  REGRESSION - this build is meant to stop {attack.id}.")
        print(f"  what should have caught it: {', '.join(attack.closed_by)}")
    else:
        print(f"  {_why_stopped(attack)}")
    print(f"  background: tutorials/{attack.tutorial}.md")
    print(BAR)
    print()


def _run_chat(attack: Attack, verbose: bool) -> dict:
    before_refunds = len(db.refunds())
    result = graph.chat(principal_for(attack.who), attack.message)
    landed = (board.worst() == "red") or (len(db.refunds()) > before_refunds)

    if verbose:
        _header(attack)
        print(f'customer says: "{attack.message}"')
        print(DASH)
        for line in result["transcript"]:
            print(f"  {line['kind']:<10} {line['text'][:150]}")
        extra = []
        if result.get("awaiting"):
            extra.append(f"awaiting human approval: {result['awaiting']['id']}")
        if result.get("limits"):
            extra.append("budget  " + "  ".join(f"{k}={v}" for k, v in result["limits"].items()))
        _panel(result, extra)
        _verdict(attack, landed)
    return {"attack": attack.id, "landed": landed, "lights": result["lights"],
            "transcript": result["transcript"], "awaiting": result.get("awaiting")}


def _run_thread_guess(attack: Attack, verbose: bool) -> dict:
    """b3. Ben has a conversation. Alice guesses the thread id and reads it."""
    from agent.models import Denied
    ben = principal_for("CUST-1002")
    alice = principal_for(attack.who)

    ben_session = graph.new_session(ben)
    graph.chat(ben, "Where is my espresso machine, ORD-100003?", session=ben_session)
    ben_thread = ben_session.thread_id

    guesses = [ben_thread]
    if ben_thread.startswith("thread-"):
        n = int(ben_thread.split("-")[1])
        guesses = [f"thread-{n}", f"thread-{n - 1}", f"thread-{n + 1}"]

    read, refused = [], []
    for g in guesses:
        try:
            history = memory.read_thread(g, alice)
            if history:
                read.append((g, history))
        except Denied as exc:
            refused.append((g, str(exc)))

    landed = bool(read)
    result = {"lights": dict(board.lights), "breaches": list(dict.fromkeys(board.breaches)),
              "findings": list(board.findings)}
    if verbose:
        _header(attack)
        print(f"  Ben's session was stored under thread id: {ben_thread}")
        print(f"  Alice ({alice.id}) tries: {', '.join(guesses)}")
        print(DASH)
        for g, history in read:
            print(f"  READ {g}: {len(history)} checkpoint(s) of Ben's conversation")
            for snap in history[:1]:
                for c in snap["context"][:4]:
                    print(f"        {c[:120]}")
        for g, why in refused:
            print(f"  refused {g}: {why}")
        _panel(result)
        _verdict(attack, landed)
    return {"attack": attack.id, "landed": landed, "lights": result["lights"]}


def _run_memory_landmine(attack: Attack, verbose: bool) -> dict:
    """b4. Session 1 plants it. Session 2 - a brand new conversation - reads it."""
    alice = principal_for(attack.who)
    first = graph.chat(alice, attack.message)
    planted = [m for m in memory.memories() if m["approved"] == 1
               and "always approved" in m["text"].lower()]
    graph.SESSIONS.clear()
    second = graph.chat(alice, attack.follow_up[0])

    landed = bool(planted)
    result = {"lights": dict(board.lights), "breaches": list(dict.fromkeys(board.breaches)),
              "findings": list(board.findings)}
    if verbose:
        _header(attack)
        print(f'session 1 - the customer says: "{attack.message}"')
        for line in first["transcript"]:
            print(f"  {line['kind']:<10} {line['text'][:140]}")
        print(DASH)
        print("  stored memories now:")
        for m in memory.memories()[:4]:
            flag = "APPROVED" if m["approved"] else "pending approval"
            print(f"    [{flag:^16}] kind={m['kind']:<10} {m['text'][:80]}")
        print(DASH)
        print(f'session 2 - a NEW conversation: "{attack.follow_up[0]}"')
        for line in second["transcript"]:
            print(f"  {line['kind']:<10} {line['text'][:140]}")
        _panel(result, ["the memory is read by every future session, for as long as it exists"])
        _verdict(attack, landed)
    return {"attack": attack.id, "landed": landed, "lights": result["lights"]}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="kestrel attack", description=__doc__)
    ap.add_argument("target", nargs="?", default="all", help="attack id (b1..b8) or 'all'")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    print(f"model={settings.active_model}  |  solution build: edge and interior, "
          f"both in the code\n")

    targets = ORDER if args.target == "all" else [args.target.lower()]
    unknown = [t for t in targets if t not in ATTACKS]
    if unknown:
        print(f"unknown attack {unknown[0]!r}. known: {', '.join(ORDER)}")
        return 2

    results = [run_one(ATTACKS[t], verbose=not args.quiet) for t in targets]
    landed = [r["attack"] for r in results if r["landed"]]
    print(DASH)
    print(f"  {len(results) - len(landed)}/{len(results)} attacks stopped.")
    if landed:
        print(f"  REGRESSION - these landed against the solution build: {', '.join(landed)}")
    else:
        print("  Contained, detected, and gated - as this build intends.")
    print(DASH)
    return 1 if landed else 0


if __name__ == "__main__":
    sys.exit(main())
