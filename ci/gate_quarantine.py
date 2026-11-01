"""Quarantine declarations of ci/gates.json.

A gate that cannot pass in one named audit scope carries ``"quarantine": {"scope": SCOPE, "reason": TEXT}``.
The scope ``avx512`` removes the gate from the AVX-512 byte-replay step of ci/avx512_replay.sh and nothing
else: the gate still runs in every shard. The scope ``all`` adds ``"until": "YYYY-MM-DD"`` and removes the
gate from every ci/run_gates.py selection, pull-request lane and audit alike, while the UTC date is earlier
than ``until``; on that date the gate runs again with no edit, so a time-boxed suspension needs no follow-up
change. ci/audit_report.py lists every quarantine in the tracking issue so the exclusion stays visible. A
gate some claim of docs/state/research_state.json cites cannot be quarantined, because its claim is qualified
until the gate passes; tests/ci/test_gate_quarantine.py enforces that.

Usage: "$PYTHON" ci/gate_quarantine.py avx512-replay-gates
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GATES = ROOT / "ci/gates.json"
SCOPES = ("avx512", "all")
REPLAY_COMMAND = "ci/replay_check.py"


def quarantined(manifest: dict[str, Any]) -> dict[str, dict[str, str]]:
    """Every quarantined gate of the manifest, by name, with its scope and reason."""
    found: dict[str, dict[str, str]] = {}
    for gate in manifest["gates"]:
        if "quarantine" in gate:
            declaration = gate["quarantine"]
            if not isinstance(declaration, dict):
                raise ValueError(f"{gate['name']}: quarantine must be an object")
            keys = {"scope", "reason", "until"} if declaration.get("scope") == "all" else {"scope", "reason"}
            if set(declaration) != keys or declaration["scope"] not in SCOPES or not str(declaration["reason"]).strip():
                raise ValueError(
                    f"{gate['name']}: quarantine needs a scope of {SCOPES}, a reason, and an until date for all"
                )
            found[gate["name"]] = {"scope": declaration["scope"], "reason": declaration["reason"]}
            if "until" in declaration:
                found[gate["name"]]["until"] = until(gate["name"], declaration["until"]).isoformat()
    return found


def until(name: str, value: object) -> date:
    """The resume date of an all-scope quarantine; anything but an ISO date YYYY-MM-DD is refused."""
    try:
        if not isinstance(value, str) or len(value) != 10:
            raise ValueError
        return date.fromisoformat(value)
    except ValueError:
        raise ValueError(f"{name}: quarantine until must be an ISO date YYYY-MM-DD") from None


def today() -> date:
    """The UTC calendar date an all-scope quarantine is compared against."""
    return datetime.now(UTC).date()


def suspended(manifest: dict[str, Any], on: date | None = None) -> dict[str, date]:
    """The gates an all-scope quarantine holds out of every selection on the given UTC date, with resume dates."""
    current = today() if on is None else on
    held = {name: date.fromisoformat(d["until"]) for name, d in quarantined(manifest).items() if d["scope"] == "all"}
    return {name: resume for name, resume in held.items() if current < resume}


def avx512_replay_gates(manifest: dict[str, Any]) -> list[str]:
    """The byte-replay gates ci/avx512_replay.sh runs: those running ci/replay_check.py, less the quarantined."""
    held = {name for name, declaration in quarantined(manifest).items() if declaration["scope"] == "avx512"}
    held |= set(suspended(manifest))
    return [gate["name"] for gate in manifest["gates"] if REPLAY_COMMAND in gate["cmd"] and gate["name"] not in held]


def main(argv: list[str]) -> int:
    if argv != ["avx512-replay-gates"]:
        sys.stderr.write(__doc__ or "")
        return 2
    sys.stdout.write(",".join(avx512_replay_gates(json.loads(GATES.read_text(encoding="utf-8")))) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
