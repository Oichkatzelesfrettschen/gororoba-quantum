"""Quarantine declarations of ci/gates.json.

A gate that cannot pass in one named audit scope carries ``"quarantine": {"scope": SCOPE, "reason": TEXT}``.
The scope ``avx512`` removes the gate from the AVX-512 byte-replay step of ci/avx512_replay.sh and nothing
else: the gate still runs in every shard, and ci/audit_report.py lists it in the tracking issue so the
exclusion stays visible. A gate some claim of docs/state/research_state.json cites cannot be quarantined,
because its claim is qualified until the gate passes; tests/ci/test_gate_quarantine.py enforces that.

Usage: "$PYTHON" ci/gate_quarantine.py avx512-replay-gates
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GATES = ROOT / "ci/gates.json"
SCOPES = ("avx512",)
REPLAY_COMMAND = "ci/replay_check.py"


def quarantined(manifest: dict[str, Any]) -> dict[str, dict[str, str]]:
    """Every quarantined gate of the manifest, by name, with its scope and reason."""
    found: dict[str, dict[str, str]] = {}
    for gate in manifest["gates"]:
        if "quarantine" in gate:
            declaration = gate["quarantine"]
            if (
                set(declaration) != {"scope", "reason"}
                or declaration["scope"] not in SCOPES
                or not str(declaration["reason"]).strip()
            ):
                raise ValueError(f"{gate['name']}: quarantine needs a scope of {SCOPES} and a reason")
            found[gate["name"]] = {"scope": declaration["scope"], "reason": declaration["reason"]}
    return found


def avx512_replay_gates(manifest: dict[str, Any]) -> list[str]:
    """The byte-replay gates ci/avx512_replay.sh runs: those running ci/replay_check.py, less the quarantined."""
    held = {name for name, declaration in quarantined(manifest).items() if declaration["scope"] == "avx512"}
    return [gate["name"] for gate in manifest["gates"] if REPLAY_COMMAND in gate["cmd"] and gate["name"] not in held]


def main(argv: list[str]) -> int:
    if argv != ["avx512-replay-gates"]:
        sys.stderr.write(__doc__ or "")
        return 2
    sys.stdout.write(",".join(avx512_replay_gates(json.loads(GATES.read_text(encoding="utf-8")))) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
