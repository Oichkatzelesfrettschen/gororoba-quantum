"""Contract for ci/gate_quarantine.py: a quarantine is declared, scoped, and never hides a cited gate."""

from __future__ import annotations

import json
from pathlib import Path

import gate_quarantine
import pytest

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = {
    "gates": [
        {"name": "a", "cmd": "x ci/replay_check.py r -- y"},
        {
            "name": "b",
            "cmd": "x ci/replay_check.py r -- y",
            "quarantine": {"scope": "avx512", "reason": "drift"},
        },
        {"name": "c", "cmd": "true"},
    ]
}


def test_avx512_selection_drops_only_the_quarantined_replay_gate() -> None:
    if gate_quarantine.avx512_replay_gates(MANIFEST) != ["a"]:
        raise AssertionError(gate_quarantine.avx512_replay_gates(MANIFEST))


@pytest.mark.parametrize(
    "declaration",
    [{"scope": "avx512"}, {"scope": "nowhere", "reason": "r"}, {"scope": "avx512", "reason": " "}],
)
def test_a_malformed_quarantine_is_refused(declaration: dict[str, str]) -> None:
    with pytest.raises(ValueError):
        gate_quarantine.quarantined({"gates": [{"name": "g", "cmd": "true", "quarantine": declaration}]})


@pytest.mark.audit
def test_no_claim_cites_a_quarantined_gate() -> None:
    manifest = json.loads((ROOT / "ci/gates.json").read_text(encoding="utf-8"))
    state = json.loads((ROOT / "docs/state/research_state.json").read_text(encoding="utf-8"))
    cited = {gate for claim in state["claims"] for gate in claim.get("gates", {})}
    hidden = sorted(set(gate_quarantine.quarantined(manifest)) & cited)
    if hidden:
        raise AssertionError(f"claims cite quarantined gates: {hidden}")
