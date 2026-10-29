"""Exercise joint-response replay against the independently counted acquisitions."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/qi_tuna_joint_response.py"


def test_retained_joint_response_replays_distinct_preparations(tmp_path: Path) -> None:
    """Catch wrong destination decoding, lost correlations, or a changed prefix boundary."""
    output = tmp_path / "joint-response.json"
    process = subprocess.run(
        [sys.executable, str(SCRIPT), "--out", str(output)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if process.returncode != 0:
        raise AssertionError(f"joint-response replay failed: {process.stderr}")
    record = json.loads(output.read_text())
    one = record["cases"]["nominal_one"]
    zero = record["cases"]["nominal_zero_prefix"]
    if one["jobs"][0]["disagreement_counts"] != [805, 233, 1659, 507, 207, 63, 473, 149]:
        raise AssertionError("nominal-one disagreement distribution differs")
    if one["parity_response_numerators"][54] != 366:
        raise AssertionError("nominal-one associator-sign parity contrast differs")
    if zero["parity_response_numerators"][4] != -7894:
        raise AssertionError("nominal-zero early-qubit-6 contrast differs")
    if zero["primary_case_outcome"] != "implementation route unavailable":
        raise AssertionError("the incomplete case must keep its original refusal")


def test_replay_binds_the_frozen_validators_and_input_receipts(tmp_path: Path) -> None:
    """Catch a joint record that cannot identify the validation code and receipts it consumed."""
    import hashlib

    output = tmp_path / "joint-response.json"
    process = subprocess.run(
        [sys.executable, str(SCRIPT), "--out", str(output)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if process.returncode != 0:
        raise AssertionError(process.stderr)
    record = json.loads(output.read_text())
    paths = (
        "scripts/qi_tuna_destination_analysis_receipt.py",
        "scripts/qi_tuna_destination_prefix.py",
        "results/quantum_inspire/runs/20261027T232908Z-tuna-destination-one-response/analysis-serialization-receipt.json",
        "results/quantum_inspire/runs/2026-10-27T194754Z-tuna-destination-response/nominal-zero-prefix-recovery-order.json",
    )
    for path in paths:
        expected = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        if record["validator_inputs"].get(path) != expected:
            raise AssertionError(f"joint replay did not bind {path}")


def test_reencoded_validation_receipt_refuses_before_joint_analysis(tmp_path: Path, monkeypatch: object) -> None:
    """Catch a replay that silently accepts different bytes for the frozen encoding receipt."""
    import shutil

    import pytest
    import qi_tuna_joint_response as joint

    copied_run = tmp_path / "run"
    shutil.copytree(joint.NOMINAL_ONE, copied_run)
    receipt_path = copied_run / "analysis-serialization-receipt.json"
    receipt_path.write_text(json.dumps(json.loads(receipt_path.read_text())))
    monkeypatch.setattr(joint, "NOMINAL_ONE", copied_run)  # type: ignore[attr-defined]
    monkeypatch.setattr(joint, "ROOT", tmp_path)  # type: ignore[attr-defined]
    with pytest.raises(ValueError, match="encoding receipt"):
        joint.analyze()


def test_joint_counts_reject_a_decoder_that_disagrees_with_frozen_marginals() -> None:
    """Catch incorrect six-bit ordering even when the total shot count stays fixed."""
    import pytest
    import qi_tuna_joint_response as joint

    counts = [0] * 64
    counts[0] = counts[9] = 1
    expected = [[1, 0, 0, 1], [2, 0, 0, 0], [2, 0, 0, 0]]
    joint.validate_marginals(counts, expected)
    with pytest.raises(ValueError, match="marginal"):
        joint.validate_marginals(counts, [[0, 0, 0, 2], *expected[1:]])


def test_retained_replay_checks_exact_bytes_and_refuses_overwrite(tmp_path: Path) -> None:
    """Catch altered analysis bytes, an unsafe output overwrite, and optimized-mode drift."""
    retained = ROOT / "docs/evidence/tuna-projector-geometry/joint-response-analysis.json"
    for flags in ([], ["-O"]):
        process = subprocess.run(
            [sys.executable, *flags, str(SCRIPT), "--check", str(retained)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if process.returncode != 0:
            raise AssertionError(f"retained exact replay failed: {process.stderr}")
    candidate = tmp_path / "existing.json"
    candidate.write_bytes(retained.read_bytes())
    original = candidate.read_bytes()
    process = subprocess.run(
        [sys.executable, str(SCRIPT), "--out", str(candidate)], cwd=ROOT, text=True, capture_output=True, check=False
    )
    if process.returncode == 0 or candidate.read_bytes() != original:
        raise AssertionError("exclusive output must refuse an existing file without changing it")
    candidate.write_bytes(original + b" ")
    process = subprocess.run(
        [sys.executable, str(SCRIPT), "--check", str(candidate)], cwd=ROOT, text=True, capture_output=True, check=False
    )
    if process.returncode == 0:
        raise AssertionError("byte-exact check must refuse a reencoded artifact")


def test_all_retained_parities_distances_and_uncertainty_replay_independently() -> None:
    """Catch a wrong parity, denominator, empirical distance or confidence radius."""
    from collections import Counter

    retained = ROOT / "docs/evidence/tuna-projector-geometry/joint-response-analysis.json"
    record = json.loads(retained.read_bytes())
    expected_variation = {"nominal_one": (600, 16384), "nominal_zero_prefix": (7918, 16384)}
    for label, case in record["cases"].items():
        independently_counted = []
        for job in case["jobs"]:
            shots = json.loads((ROOT / job["raw"]).read_bytes())
            expected_early = [19, 17, 18] if job["batch"].endswith("rotated-destinations") else [17, 18, 19]
            if job["early_classical_bits"] != expected_early:
                raise AssertionError("physical-to-classical destination mapping differs")
            columns = expected_early + [4, 11, 6]
            counts = Counter(
                sum(int(shot[19 - column]) << position for position, column in enumerate(columns)) for shot in shots
            )
            independent = [counts[index] for index in range(64)]
            parities = [
                sum(count * (-1 if (index & mask).bit_count() % 2 else 1) for index, count in counts.items())
                for mask in range(64)
            ]
            if independent != job["joint_counts"] or parities != job["parity_numerators"]:
                raise AssertionError("joint counts or Walsh parities differ from independent integer replay")
            independently_counted.append(parities)
        first, middle, last = independently_counted
        if case["parity_response_numerators"] != [2 * middle[i] - first[i] - last[i] for i in range(64)]:
            raise AssertionError("joint parity response numerators differ")
        if case["parity_endpoint_numerators"] != [last[i] - first[i] for i in range(64)]:
            raise AssertionError("joint parity endpoint numerators differ")
        if (case["parity_response_denominator"], case["parity_endpoint_denominator"]) != (8192, 4096):
            raise AssertionError("response or endpoint denominator differs")
        if (case["empirical_total_variation_numerator"], case["empirical_total_variation_denominator"]) != (
            expected_variation[label]
        ):
            raise AssertionError("the empirical total-variation fraction differs")
    if record["nominal_one_posthoc_uncertainty"] != {
        "parity_functions": 63,
        "contrasts_per_function": 2,
        "simultaneous_confidence": "0.99",
        "response_radius_upper": "0.086155685839",
        "endpoint_radius_upper": "0.099484016822",
    }:
        raise AssertionError("the simultaneous confidence contract differs")


@pytest.mark.parametrize(
    "mutation", ["response_denominator", "endpoint_denominator", "tv", "response_radius", "endpoint_radius"]
)
def test_checked_artifact_refuses_numeric_mutations(tmp_path: Path, mutation: str) -> None:
    """A checked receipt rejects changed numeric claims even when the JSON remains valid."""
    retained = ROOT / "docs/evidence/tuna-projector-geometry/joint-response-analysis.json"
    record = json.loads(retained.read_bytes())
    if mutation == "response_denominator":
        record["cases"]["nominal_one"]["parity_response_denominator"] += 1
    elif mutation == "endpoint_denominator":
        record["cases"]["nominal_one"]["parity_endpoint_denominator"] += 1
    elif mutation == "tv":
        record["cases"]["nominal_zero_prefix"]["empirical_total_variation_numerator"] += 1
    elif mutation == "response_radius":
        record["nominal_one_posthoc_uncertainty"]["response_radius_upper"] = "0.08"
    else:
        record["nominal_one_posthoc_uncertainty"]["endpoint_radius_upper"] = "0.09"
    altered = tmp_path / "altered.json"
    altered.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    process = subprocess.run(
        [sys.executable, str(SCRIPT), "--check", str(altered)], cwd=ROOT, text=True, capture_output=True, check=False
    )
    if process.returncode == 0:
        raise AssertionError(f"checked replay accepted {mutation} mutation")
