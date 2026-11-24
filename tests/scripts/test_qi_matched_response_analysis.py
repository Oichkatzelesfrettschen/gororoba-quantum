"""Frozen matched-response analysis: null model, region visibility, covariance, order mutation, refusals."""

import json
import shutil
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
PROPOSAL = ROOT / "results/quantum_inspire/proposals/tuna17-zero-divisor-matched-response-region2-selector-q11"
# Seeds: docs/evidence/anu_qrng/draw-2026-11-22T010305Z.json, indices 4, 5, 6, 7 in order.
TEST_SEEDS = (57531, 54461, 19728, 4799)
IDEAL = {"dark": 0.0, "bright": 1.0, "fixture": 0.5}
BATCH_OFFSET = (0.04, 0.10, 0.06)
REGION_OFFSET = (0.03, 0.08)
ALPHA = ((0.020, 0.030), (0.025, 0.035), (0.030, 0.040))
BETA = ((0.040, 0.050), (0.045, 0.055), (0.050, 0.060))


def _check(condition: object) -> None:
    if not condition:
        raise AssertionError


def _load(shots: int | None = None) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    proposal = json.loads((PROPOSAL / "proposal.json").read_text())
    manifests = {name: json.loads((PROPOSAL / name / "cases.json").read_text()) for name in proposal["batches"]}
    if shots is not None:
        for manifest in manifests.values():
            manifest["shots"] = shots
        proposal["shots_per_job"] = shots
    return proposal, manifests


def _outcomes(q0: float, q1: float, correlation: float, selectors: tuple[int, int]) -> tuple[list[str], list[float]]:
    """Shot strings of the four joint selector outcomes and their probabilities; q is P(read 0)."""
    low, high = max(0.0, q0 + q1 - 1.0), min(q0, q1)
    p00 = min(max(q0 * q1 + correlation * float(np.sqrt(q0 * (1 - q0) * q1 * (1 - q1))), low), high)
    probabilities = [p00, q0 - p00, q1 - p00, 1 - q0 - q1 + p00]
    strings = []
    for first in (0, 1):
        for second in (0, 1):
            bits = ["0"] * 17
            bits[16 - selectors[0]] = str(first)
            bits[16 - selectors[1]] = str(second)
            strings.append("".join(bits))
    return strings, probabilities


def _draw(rng: Any, strings: list[str], probabilities: list[float], shots: int) -> list[str]:
    counts = rng.multinomial(shots, probabilities)
    return [string for string, count in zip(strings, counts, strict=True) for _ in range(int(count))]


def _series(
    rng: Any,
    proposal: dict[str, Any],
    manifests: dict[str, dict[str, Any]],
    visibility: tuple[float, float] = (0.8, 0.8),
    correlation: float = 0.0,
) -> dict[tuple[str, str], list[str]]:
    """Shots under p = batch offset + region offset + visibility x ideal, with per-qubit readout confusion."""
    selectors = (proposal["regions"][0]["roles"]["selector"], proposal["regions"][1]["roles"]["selector"])
    shots: dict[tuple[str, str], list[str]] = {}
    for batch, name in enumerate(proposal["batches"]):
        manifest = manifests[name]
        count = manifest["shots"]
        truth = [
            BATCH_OFFSET[batch] + REGION_OFFSET[region] + visibility[region] * IDEAL[replica["case"]]
            for region, replica in enumerate(manifest["replicas"])
        ]
        raw = [BETA[batch][r] + (1 - ALPHA[batch][r] - BETA[batch][r]) * truth[r] for r in range(2)]
        strings, probabilities = _outcomes(raw[0], raw[1], correlation, selectors)
        shots[name, "witness.cq"] = _draw(rng, strings, probabilities, count)
        # readout-0 reads 1 with probability alpha; readout-1 reads 0 with probability beta.
        strings, probabilities = _outcomes(1 - ALPHA[batch][0], 1 - ALPHA[batch][1], 0.0, selectors)
        shots[name, "readout-0.cq"] = _draw(rng, strings, probabilities, count)
        strings, probabilities = _outcomes(BETA[batch][0], BETA[batch][1], 0.0, selectors)
        shots[name, "readout-1.cq"] = _draw(rng, strings, probabilities, count)
    return shots


def _analyze(
    proposal: dict[str, Any], manifests: dict[str, dict[str, Any]], shots: dict[tuple[str, str], list[str]]
) -> dict[str, Any]:
    from qi_matched_zero_divisor import matched_response_contrast

    from qi_matched_response import analyze_matched_series

    return analyze_matched_series(proposal, manifests, shots, contrast=matched_response_contrast)


def test_common_affine_null_gives_unbiased_residual_below_threshold() -> None:
    proposal, manifests = _load()
    rng = np.random.default_rng(TEST_SEEDS[0])
    first = _analyze(proposal, manifests, _series(rng, proposal, manifests))
    _check(abs(first["contrast"]["z"]) < 3)
    _check(first["decision"]["reject_common_affine"] is False)
    _check(first["raw"]["standard_error"] > 0)
    _check(set(first["half_spacings"]) == {"R1", "R2"})
    _check(set(first["batches"]) == set(proposal["batches"]))
    small_proposal, small_manifests = _load(2048)
    results = [
        _analyze(small_proposal, small_manifests, _series(rng, small_proposal, small_manifests))["contrast"]
        for _ in range(40)
    ]
    mean = np.mean([row["residual"] for row in results])
    error = np.mean([row["standard_error"] for row in results]) / np.sqrt(len(results))
    _check(abs(mean) < 4 * error)


def test_region_visibility_difference_gives_half_difference_residual() -> None:
    proposal, manifests = _load()
    rng = np.random.default_rng(TEST_SEEDS[1])
    result = _analyze(proposal, manifests, _series(rng, proposal, manifests, visibility=(0.7, 0.9)))
    contrast = result["contrast"]
    _check(abs(contrast["residual"] - 0.1) < 4 * contrast["standard_error"])
    _check(result["decision"]["reject_common_affine"] is True)


def test_covariance_is_symmetric_semidefinite_and_matches_same_shot_monte_carlo() -> None:
    proposal, manifests = _load(1024)
    rng = np.random.default_rng(TEST_SEEDS[2])
    values = []
    analytic = []
    for _ in range(2000):
        result = _analyze(proposal, manifests, _series(rng, proposal, manifests, correlation=0.4))
        values.append(result["probabilities_corrected"])
        analytic.append(result["covariance"])
    matrix = np.mean(analytic, axis=0)
    _check(np.allclose(matrix, matrix.T, rtol=0, atol=1e-12))
    _check(float(np.linalg.eigvalsh(matrix).min()) > -1e-12)
    sample = np.cov(np.asarray(values), rowvar=False)
    # Entries (0, 1) and (2, 3) pair the two regions of one witness circuit; other cross-batch entries vanish.
    _check(matrix[0, 1] > 0)
    _check(sample[0, 1] == pytest.approx(matrix[0, 1], rel=0.25))
    _check(sample[2, 3] == pytest.approx(matrix[2, 3], rel=0.25))
    _check(sample[0, 0] == pytest.approx(matrix[0, 0], rel=0.15))
    _check(matrix[0, 2] == 0 and matrix[1, 4] == 0)


def test_swapped_order_is_refused() -> None:
    proposal, manifests = _load()
    shots = _series(np.random.default_rng(TEST_SEEDS[3]), proposal, manifests)
    _check(len(_analyze(proposal, manifests, shots)["order"]) == 6)
    order = proposal["primary_contrast"]["order"]
    order[2], order[4] = order[4], order[2]
    with pytest.raises(ValueError, match="frozen order"):
        _analyze(proposal, manifests, shots)


def _run_directory(tmp_path: Path, mutation: str) -> dict[str, Any]:
    from qi_matched_response import proposal_digests, verify_run_binding
    from qi_records import load_run

    run = tmp_path / "run"
    shutil.copytree(PROPOSAL / "batch-01", run)
    if mutation == "circuit":
        witness = run / "witness.cq"
        data = bytearray(witness.read_bytes())
        data[-5] ^= 1
        witness.write_bytes(bytes(data))
    elif mutation == "manifest":
        manifest = json.loads((run / "cases.json").read_text())
        manifest["shots"] = 8192
        (run / "cases.json").write_text(json.dumps(manifest, indent=1) + "\n")
    return verify_run_binding(proposal_digests(PROPOSAL), "batch-01", load_run(run))


def test_run_binding_accepts_the_proposal_bytes(tmp_path: Path) -> None:
    from qi_matched_response import proposal_digests

    binding = _run_directory(tmp_path, "none")
    _check(binding["circuits"] == proposal_digests(PROPOSAL)["batches"]["batch-01"]["circuits"])
    _check(len(binding["circuits"]) == 3)


@pytest.mark.parametrize("mutation", ["circuit", "manifest"])
def test_run_binding_refuses_changed_circuit_or_manifest(tmp_path: Path, mutation: str) -> None:
    with pytest.raises(ValueError, match="differ"):
        _run_directory(tmp_path, mutation)


@pytest.mark.parametrize(
    "fault",
    ["short-witness", "short-readout", "missing-readout", "missing-batch", "bad-order", "backend", "readout-error"],
)
def test_incomplete_batches_are_refused(fault: str) -> None:
    proposal, manifests = _load(256)
    rng = np.random.default_rng(TEST_SEEDS[0])
    shots = _series(rng, proposal, manifests)
    if fault == "short-witness":
        shots["batch-01", "witness.cq"].pop()
    elif fault == "short-readout":
        shots["batch-02", "readout-1.cq"].pop()
    elif fault == "missing-readout":
        del shots["batch-00", "readout-0.cq"]
    elif fault == "missing-batch":
        manifests.pop("batch-02")
    elif fault == "backend":
        manifests["batch-01"]["backend"] = "qx"
    elif fault == "readout-error":
        selector = proposal["regions"][1]["roles"]["selector"]
        rows = shots["batch-02", "readout-0.cq"]
        shots["batch-02", "readout-0.cq"] = [
            shot[: 16 - selector] + "1" + shot[17 - selector :] if index < len(rows) // 4 else shot
            for index, shot in enumerate(rows)
        ]
    else:
        proposal["primary_contrast"]["order"][0] = "D_R1_b1"
    with pytest.raises(ValueError, match="exceeds" if fault == "readout-error" else None):
        _analyze(proposal, manifests, shots)


def test_series_keeps_one_shot_count_per_circuit() -> None:
    proposal, manifests = _load(256)
    shots = _series(np.random.default_rng(TEST_SEEDS[1]), proposal, manifests)
    _check({len(rows) for rows in shots.values()} == {256})
    _check(Counter(len(row) for rows in shots.values() for row in rows) == {17: 9 * 256})


def test_proposal_directory_with_a_changed_circuit_is_refused(tmp_path: Path) -> None:
    from qi_matched_response import proposal_digests

    copy = tmp_path / "proposal"
    shutil.copytree(PROPOSAL, copy)
    _check(proposal_digests(copy)["proposal.json"])
    witness = copy / "batch-02" / "witness.cq"
    data = bytearray(witness.read_bytes())
    data[-5] ^= 1
    witness.write_bytes(bytes(data))
    with pytest.raises(ValueError, match="differs"):
        proposal_digests(copy)


def test_frozen_digests_equal_the_compiler_receipt() -> None:
    from qi_matched_response import CIRCUIT_SHA256

    receipt = json.loads(
        (ROOT / "docs/evidence/quantum_inspire/matched-zero-divisor-toolchain-region2-selector-q11.json").read_text()
    )
    rows = {row["file"]: row["source_sha256"] for row in receipt["circuits"]}
    _check(
        rows == {f"{batch}/{name}": digest for batch, files in CIRCUIT_SHA256.items() for name, digest in files.items()}
    )


def test_reader_reproduces_the_retained_visibility_floor_selector_probabilities() -> None:
    """The retained raw shots of three Latin batches give the retained selector-zero values with their selectors."""
    from qi_matched_response import _joint_moments

    analysis = json.loads(
        (ROOT / "results/quantum_inspire/zero_divisor_tuna_17_visibility_floor_analysis.json").read_text()
    )
    rows: dict[str, list[dict[str, Any]]] = {}
    for row in analysis["replicas"]:
        rows.setdefault(row["file"], []).append(row)
    runs = sorted((ROOT / "results/quantum_inspire/runs").glob("2026-10-17T05*-zero_divisor_tuna_17-batch-0*"))
    _check(len(runs) == 3)
    for run in runs:
        manifest = json.loads((run / "cases.json").read_text())
        witness = next(row["file"] for row in manifest["circuits"] if row["kind"] == "witness")
        selectors = (rows[witness][0]["roles"]["selector"], rows[witness][1]["roles"]["selector"])
        raw = {
            name: json.loads((run / "raw" / f"{name}.json").read_text())
            for name in (witness, "readout-0.cq", "readout-1.cq")
        }
        moments = {name: _joint_moments(shots, selectors, len(shots), name)[0] for name, shots in raw.items()}
        for index, row in enumerate(rows[witness]):
            _check(abs((1 - moments[witness][index]) - row["p_selector_zero"]) < 1e-12)
            _check(abs(moments["readout-0.cq"][index] - row["selector_e01"]) < 1e-12)
            _check(abs((1 - moments["readout-1.cq"][index]) - row["selector_e10"]) < 1e-12)
