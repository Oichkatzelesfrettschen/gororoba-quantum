"""qi_joint_response decodes under an explicit layout, matches the retained Tuna replays and refuses other layouts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import qi_joint_response as joint
from qi_joint_response import TUNA_DESTINATION as LAYOUT

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs/evidence/tuna-projector-geometry/joint-response-analysis.json"
RUNS = {
    "nominal_one": (ROOT / "results/quantum_inspire/runs/20261027T232908Z-tuna-destination-one-response", "one"),
    "nominal_zero_prefix": (ROOT / "results/quantum_inspire/runs/2026-10-27T194754Z-tuna-destination-response", "zero"),
}
COMPARED = ("parity_response_numerators", "parity_endpoint_numerators", "empirical_total_variation_numerator")


def _check(condition: object, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _batches(prepared: str) -> dict[str, str]:
    return {arm: f"prepared-{prepared}-{arm}" for arm in LAYOUT.arms}


@pytest.mark.parametrize("case", sorted(RUNS))
def test_retained_run_replays_through_the_explicit_layout(case: str) -> None:
    """The library reproduces the pinned producer's joint tables and contrasts from the retained bytes."""
    run, prepared = RUNS[case]
    replay = joint.replay_run(run, _batches(prepared), LAYOUT)
    frozen = json.loads(EVIDENCE.read_bytes())["cases"][case]
    for ours, theirs in zip(replay["jobs"], frozen["jobs"], strict=True):
        for key in ("batch", "job", "raw_sha256", "early_classical_bits", "joint_counts", "disagreement_counts"):
            _check(ours[key] == theirs[key], f"{case} {ours['batch']} {key} differs")
        # The library names the raw file relative to the run; the pinned producer named it from the repository root.
        _check(theirs["raw"].endswith("/" + ours["raw"]), f"{case} {ours['batch']} raw path differs")
        _check(ours["parity_numerators"] == theirs["parity_numerators"], f"{case} {ours['batch']} parities differ")
    for key in COMPARED:
        _check(replay[key] == frozen[key], f"{case} {key} differs from the retained analysis")
    _check(replay["parity_response_denominator"] == frozen["parity_response_denominator"], "denominator differs")


def test_uncertainty_matches_the_retained_posthoc_bound() -> None:
    frozen = json.loads(EVIDENCE.read_bytes())["nominal_one_posthoc_uncertainty"]
    _check(joint.uncertainty(LAYOUT.shots, 63) == frozen, "generalized bound differs from the retained one")


def test_decode_on_a_small_fixture() -> None:
    layout = joint.Layout(shots=4, width=4, terminal_qubits=(0, 1), early_bits={"a": (2, 3)}, arms=("a", "a", "a"))
    # rightmost bit is position 0: "1101" has q0=1, q1=0, q2=1, q3=1
    decoded = joint.decode(["1101", "0000", "1111", "0101"], (2, 3), (0, 1), layout)
    _check(sum(decoded["joint_counts"]) == 4, "counts lost shots")
    # Only "1101" disagrees: q1=0 against its early copy q3=1, the second qubit, so mismatch index 2.
    _check(decoded["disagreement_counts"] == [3, 0, 1, 0], f"disagreement {decoded['disagreement_counts']}")
    _check(decoded["parity_numerators"][0] == 4, "mask 0 parity must count every shot")
    tables = joint.marginal_projections(decoded["joint_counts"], 2)
    _check(sum(tables[0]) == 4 and sum(tables[1]) == 4, "projections lost shots")


def test_wrong_width_or_count_is_refused() -> None:
    with pytest.raises(ValueError, match="ordered shots"):
        joint.decode(["0" * 20] * 7, (17, 18, 19), (4, 11, 6), LAYOUT)
    with pytest.raises(ValueError, match="20-bit"):
        joint.decode(["0" * 19] * LAYOUT.shots, (17, 18, 19), (4, 11, 6), LAYOUT)


def test_layout_rejects_inconsistent_definitions() -> None:
    with pytest.raises(ValueError, match="early bits"):
        joint.Layout(shots=1, width=4, terminal_qubits=(0, 1), early_bits={"a": (2,)}, arms=("a", "a", "a"))
    with pytest.raises(ValueError, match="past the width"):
        joint.Layout(shots=1, width=4, terminal_qubits=(0, 9), early_bits={"a": (2, 3)}, arms=("a", "a", "a"))
    with pytest.raises(ValueError, match="every arm"):
        joint.Layout(shots=1, width=4, terminal_qubits=(0,), early_bits={"a": (2,)})


def test_unnamed_arm_is_refused() -> None:
    run, _ = RUNS["nominal_one"]
    with pytest.raises(ValueError, match="exactly the arms"):
        joint.replay_run(run, {"baseline-before": "prepared-one-baseline-before"}, LAYOUT)
