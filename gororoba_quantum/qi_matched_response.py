"""Frozen analysis of the Tuna-17 matched zero-divisor response series.

Input: the proposal record, the manifest of each of its three batches and the
collected shots of every circuit. Output: the six readout-corrected
selector-zero probabilities in the order of proposal primary_contrast.order,
their 6 x 6 covariance, and the common-affine contrast built from them.

Covariance construction (delta method on observed frequencies):

- A circuit is one multinomial sample of its shots. Per circuit, the two
  selector bits (one per region) form a joint outcome in {0, 1}^2, and the
  covariance of the two selector read-1 frequencies m1, m2 over n shots is
  [[m1 (1 - m1), f11 - m1 m2], [f11 - m1 m2, m2 (1 - m2)]] / n, where f11 is
  the frequency of both selectors reading 1.
- The witness circuit of a batch carries both regions and one register-wide
  measure, so the two regions of a witness share every shot and their
  covariance is the same-shot term f11 - m1 m2 above, never zero by assumption.
- The readout-0 and readout-1 circuits of a batch are register-wide too. A
  region's corrected estimate is v = (m1 - mw) / (m1 - m0), with mw the witness
  frequency, m0 = e01 the readout-0 frequency and m1 = 1 - e10 the readout-1
  frequency of that region's selector. Each of the two estimates of a batch
  depends on the same two readout circuits, so the gradient of v with respect
  to (mw1, mw2, m0_1, m0_2, m1_1, m1_2) propagates their sampling error into
  both estimates, and the batch covariance is G S G^T with S the block-diagonal
  covariance of the three circuits.
- Batches are separate submissions with separate circuits, so the 6 x 6
  covariance is block-diagonal over batches with one 2 x 2 block per batch.

The raw residual applies the same weights to the uncorrected selector-zero
frequencies with the witness covariance alone. Corrected values may leave
[0, 1]; the delta method is a first-order approximation whose error grows as
the readout contrast m1 - m0 shrinks, and a nonpositive contrast is refused.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

SCHEMA = "qi-matched-response-analysis-v1"
NQUBITS = 17
WITNESS = "witness.cq"
READOUT_ZERO = "readout-0.cq"
READOUT_ONE = "readout-1.cq"
REJECT_Z = 3.0
REJECTION = "abs(z)>=3"
WEIGHTS = (0, 0, -1, 1, 1, -1)
PROPOSAL_SHA256 = "31e9e55a77767afd21ff01bebed55d71db76eae7d421a8c79342a6d050070568"
SELECTORS = (4, 11)
READOUT_ERROR_LIMIT = 0.2
CASES_SHA256 = {
    "batch-00": "c7d7d3cc9d63b906a3c3bfc91f264c4b91bc8d7ab662ac0a6555062747999fe1",
    "batch-01": "c9584d230265692068b86cf0ec56b7ef774b8d43655744c9e68bbc7961f93485",
    "batch-02": "176805b48f052b5e9f68a7c2923600803d9a554abdbfceb2dbcb4da92cbf1fff",
}
CIRCUIT_SHA256 = {
    "batch-00": {
        "readout-0.cq": "7d2ee15155f14726fc71a235da3df2fada6f12d458a5095f023c31e8206efdc3",
        "readout-1.cq": "1ed49e3399392d2e15913d90631fa7088899da51a6644baf1d74671e8673a6ff",
        "witness.cq": "582aacf9ac3bd2aaa29be2ff44b2ac8502663029a6899adc799d0ba3256b037e",
    },
    "batch-01": {
        "readout-0.cq": "7d2ee15155f14726fc71a235da3df2fada6f12d458a5095f023c31e8206efdc3",
        "readout-1.cq": "1ed49e3399392d2e15913d90631fa7088899da51a6644baf1d74671e8673a6ff",
        "witness.cq": "50946fe9d7e5211d841efad20fab79ee163335b7428726a413ba54fbb36d70c2",
    },
    "batch-02": {
        "readout-0.cq": "7d2ee15155f14726fc71a235da3df2fada6f12d458a5095f023c31e8206efdc3",
        "readout-1.cq": "1ed49e3399392d2e15913d90631fa7088899da51a6644baf1d74671e8673a6ff",
        "witness.cq": "2c1f0b172b8834f2ce44fc704c8ecb2f75b89a80520f7d3bd4eb483e49b57232",
    },
}
ORDER = ("D_R1_b0", "B_R2_b0", "B_R1_b1", "F_R2_b1", "F_R1_b2", "D_R2_b2")
CASE_LETTER = {"dark": "D", "bright": "B", "fixture": "F"}
LABEL = re.compile(r"[DBF]_R[12]_b\d+")
DECISION = (
    "The common-affine response with batch offsets and one fixed region offset is rejected when the "
    "corrected residual has abs(z) >= 3. The raw residual is reported beside it. A rejection does not "
    "identify drift, crosstalk or a control-error channel, and a compatible residual leaves "
    "region-dependent visibility and time-dependent region offsets unresolved."
)

Contrast = Callable[[Sequence[float], Sequence[Sequence[float]]], dict[str, float]]
Shots = Mapping[tuple[str, str], Sequence[str] | None]


def _require(condition: object, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _joint_moments(
    shots: Sequence[str] | None, selectors: tuple[int, int], expected: int, name: str
) -> tuple[np.ndarray, np.ndarray]:
    """Read-1 frequencies of the two selectors and their covariance over the shots of one circuit."""
    if shots is None:
        raise ValueError(f"{name} has no collected shots")
    _require(len(shots) == expected, f"{name} holds {len(shots)} shots; the manifest requests {expected}")
    table = np.zeros((2, 2))
    for outcome, count in Counter(shots).items():
        _require(
            isinstance(outcome, str) and len(outcome) == NQUBITS and set(outcome) <= {"0", "1"},
            f"{name} holds a shot that is not a {NQUBITS}-bit string",
        )
        table[int(outcome[NQUBITS - 1 - selectors[0]]), int(outcome[NQUBITS - 1 - selectors[1]])] += count
    frequency = table / expected
    mean = np.array([frequency[1, :].sum(), frequency[:, 1].sum()])
    cross = frequency[1, 1] - mean[0] * mean[1]
    covariance = np.array([[mean[0] * (1 - mean[0]), cross], [cross, mean[1] * (1 - mean[1])]]) / expected
    return mean, covariance


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def proposal_digests(directory: Path) -> dict[str, Any]:
    """sha256 of proposal.json, each batch cases.json and each batch circuit file of a proposal directory."""
    proposal = json.loads((directory / "proposal.json").read_text())
    batches = {}
    for name in proposal["batches"]:
        files = sorted((directory / name).glob("*.cq"))
        batches[name] = {
            "cases.json": _digest(directory / name / "cases.json"),
            "circuits": {path.name: _digest(path) for path in files},
        }
    _require(
        len(batches) == 3 and all(len(row["circuits"]) == 3 for row in batches.values()),
        "the proposal needs three batches of three circuits",
    )
    _require(
        _digest(directory / "proposal.json") == PROPOSAL_SHA256, "proposal.json differs from the approved proposal"
    )
    observed = {name: {"cases.json": row["cases.json"], "circuits": row["circuits"]} for name, row in batches.items()}
    frozen = {name: {"cases.json": CASES_SHA256[name], "circuits": CIRCUIT_SHA256[name]} for name in CASES_SHA256}
    _require(observed == frozen, "a batch manifest or circuit differs from the approved proposal")
    return {"proposal.json": PROPOSAL_SHA256, "batches": batches}


def verify_run_binding(expected: Mapping[str, Any], batch: str, record: Mapping[str, Any]) -> dict[str, Any]:
    """Refuse a loaded run (qi_records.load_run) whose manifest or submitted circuits differ from the proposal."""
    row = expected["batches"].get(batch)
    _require(row is not None, f"{batch}: the proposal has no such batch")
    _require(record.get("cases_sha256") == row["cases.json"], f"{batch}: the run manifest differs from the proposal")
    observed = dict(record["circuits"])
    _require(observed == row["circuits"], f"{batch}: the run circuits differ from the proposal circuits")
    return {"cases.json": record["cases_sha256"], "circuits": observed}


def analyze_matched_series(
    proposal: Mapping[str, Any],
    manifests: Mapping[str, Mapping[str, Any]],
    shots: Shots,
    *,
    contrast: Contrast,
) -> dict[str, Any]:
    """Analyze the three collected batches of one matched-response proposal.

    manifests maps a batch name to the batch cases.json; shots maps
    (batch name, circuit file) to the collected shot strings. contrast is
    scripts/qi_matched_zero_divisor.matched_response_contrast.
    """
    spec = proposal["primary_contrast"]
    order = list(spec["order"])
    _require(tuple(order) == ORDER, "the proposal order differs from the frozen order")
    _require(tuple(spec["weights"]) == WEIGHTS and spec["rejection"] == REJECTION, "proposal contrast differs")
    batches = list(proposal["batches"])
    _require(set(manifests) == set(batches), "the manifests differ from the proposal batches")
    regions = proposal["regions"]
    _require(len(regions) == 2, "the proposal needs exactly two regions")
    selectors = (int(regions[0]["roles"]["selector"]), int(regions[1]["roles"]["selector"]))
    _require(selectors == SELECTORS, "the proposal selectors differ from the frozen selectors")

    position: dict[str, int] = {}
    for index, label in enumerate(order):
        _require(LABEL.fullmatch(label) is not None and label not in position, f"order entry {label!r} is invalid")
        position[label] = index
    _require(len(order) == 6, "the order needs six entries")

    values = np.zeros(6)
    raw_values = np.zeros(6)
    covariance = np.zeros((6, 6))
    raw_covariance = np.zeros((6, 6))
    seen: set[str] = set()
    batch_report: dict[str, Any] = {}
    for name in batches:
        manifest = manifests[name]
        number = re.fullmatch(r"batch-(\d+)", name)
        if number is None or manifest.get("batch") != name:
            raise ValueError(f"{name}: the manifest names another batch")
        _require(
            manifest.get("backend") == proposal["backend"] and manifest.get("shots") == proposal["shots_per_job"],
            f"{name}: the manifest differs from the proposal in backend or shots",
        )
        expected = int(manifest["shots"])
        _require(
            sorted(row["file"] for row in manifest["circuits"]) == sorted((WITNESS, READOUT_ZERO, READOUT_ONE)),
            f"{name}: the manifest does not hold the witness and readout circuits",
        )
        replicas = manifest["replicas"]
        _require(len(replicas) == 2, f"{name}: the manifest needs one replica per region")
        for region, replica in zip(regions, replicas, strict=True):
            _require(
                replica["qubits"] == region["qubits"] and replica["roles"] == region["roles"],
                f"{name}: a replica region differs from the proposal",
            )
        labels = [
            f"{CASE_LETTER[replica['case']]}_R{index + 1}_b{int(number[1])}" for index, replica in enumerate(replicas)
        ]
        _require(all(label in position for label in labels), f"{name}: the order lacks {labels}")
        seen.update(labels)
        mean_witness, cov_witness = _joint_moments(shots.get((name, WITNESS)), selectors, expected, f"{name} {WITNESS}")
        mean_zero, cov_zero = _joint_moments(
            shots.get((name, READOUT_ZERO)), selectors, expected, f"{name} {READOUT_ZERO}"
        )
        mean_one, cov_one = _joint_moments(shots.get((name, READOUT_ONE)), selectors, expected, f"{name} {READOUT_ONE}")
        denominator = mean_one - mean_zero
        _require(bool((denominator > 0).all()), f"{name}: the readout assignment is singular or reversed")
        _require(
            bool((mean_zero + 1 - mean_one <= READOUT_ERROR_LIMIT).all()),
            f"{name}: a selector readout error e01 + e10 exceeds {READOUT_ERROR_LIMIT}",
        )
        corrected = (mean_one - mean_witness) / denominator
        gradient = np.zeros((2, 6))
        for region in range(2):
            gradient[region, region] = -1 / denominator[region]
            gradient[region, 2 + region] = (mean_one[region] - mean_witness[region]) / denominator[region] ** 2
            gradient[region, 4 + region] = (mean_witness[region] - mean_zero[region]) / denominator[region] ** 2
        block = np.zeros((6, 6))
        block[0:2, 0:2], block[2:4, 2:4], block[4:6, 4:6] = cov_witness, cov_zero, cov_one
        corrected_covariance = gradient @ block @ gradient.T
        indices = [position[label] for label in labels]
        for row, index in enumerate(indices):
            values[index] = corrected[row]
            raw_values[index] = 1 - mean_witness[row]
            for column, other in enumerate(indices):
                covariance[index, other] = corrected_covariance[row, column]
                raw_covariance[index, other] = cov_witness[row, column]
        batch_report[name] = {
            "shots": expected,
            "witness_cases": [replica["case"] for replica in replicas],
            "readout_confusion": {
                f"R{region + 1}": {"e01": float(mean_zero[region]), "e10": float(1 - mean_one[region])}
                for region in range(2)
            },
        }
    _require(seen == set(order), "the order differs from the cases the manifests carry")

    half_spacings = {}
    for region in (1, 2):
        weights = np.zeros(6)
        for label, index in position.items():
            if label.startswith(f"B_R{region}_"):
                weights[index] += 0.5
            elif label.startswith(f"D_R{region}_"):
                weights[index] -= 0.5
        half_spacings[f"R{region}"] = {
            "estimate": float(weights @ values),
            "standard_error": math.sqrt(max(float(weights @ covariance @ weights), 0.0)),
        }
    result = contrast(values.tolist(), covariance.tolist())
    raw_result = contrast(raw_values.tolist(), raw_covariance.tolist())
    return {
        "schema": SCHEMA,
        "order": order,
        "weights": list(WEIGHTS),
        "probabilities_corrected": values.tolist(),
        "covariance": covariance.tolist(),
        "contrast": result,
        "raw": {"probabilities": raw_values.tolist(), "covariance": raw_covariance.tolist(), **raw_result},
        "half_spacings": half_spacings,
        "batches": batch_report,
        "decision": {
            "rule": REJECTION,
            "threshold": REJECT_Z,
            "reject_common_affine": abs(result["z"]) >= REJECT_Z,
            "statement": DECISION,
        },
    }
