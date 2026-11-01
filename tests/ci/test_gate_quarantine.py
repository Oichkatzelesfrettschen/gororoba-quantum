"""Contract for ci/gate_quarantine.py: a quarantine is declared, scoped, and never hides a cited gate."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from unittest.mock import patch

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
    [
        {"scope": "avx512"},
        {"scope": "nowhere", "reason": "r"},
        {"scope": "avx512", "reason": " "},
        {"scope": "all", "reason": "r"},
        {"scope": "all", "reason": "r", "until": "2026-12"},
        {"scope": "all", "reason": "r", "until": "2026-13-01"},
        {"scope": "avx512", "reason": "r", "until": "2026-12-01"},
    ],
)
def test_a_malformed_quarantine_is_refused(declaration: dict[str, str]) -> None:
    # An all-scope quarantine without a valid resume date would hold its gate out forever.
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


PAUSED = {
    "gates": [
        {"name": "kept", "cmd": "x ci/replay_check.py r -- y"},
        {
            "name": "paused",
            "cmd": "x ci/replay_check.py r -- y",
            "quarantine": {"scope": "all", "reason": "owner pause", "until": "2026-12-01"},
        },
    ]
}


@pytest.mark.parametrize(
    ("on", "held"),
    [(date(2026, 11, 30), {"paused": date(2026, 12, 1)}), (date(2026, 12, 1), {}), (date(2027, 1, 1), {})],
)
def test_an_all_scope_quarantine_ends_on_its_until_date(on: date, held: dict[str, date]) -> None:
    if gate_quarantine.suspended(PAUSED, on) != held:
        raise AssertionError(f"on {on}: {gate_quarantine.suspended(PAUSED, on)}, not {held}")


def test_an_all_scope_quarantine_leaves_the_avx512_replay_while_it_holds() -> None:
    with patch.object(gate_quarantine, "today", return_value=date(2026, 11, 1)):
        during = gate_quarantine.avx512_replay_gates(PAUSED)
    with patch.object(gate_quarantine, "today", return_value=date(2026, 12, 1)):
        after = gate_quarantine.avx512_replay_gates(PAUSED)
    if during != ["kept"] or after != ["kept", "paused"]:
        raise AssertionError(f"during {during}, after {after}")
