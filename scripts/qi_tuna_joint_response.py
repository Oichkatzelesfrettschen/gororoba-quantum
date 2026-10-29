"""Replay the six-bit joint responses of the retained Tuna destination controls."""

from __future__ import annotations

import argparse
import json
from decimal import ROUND_CEILING, Decimal, localcontext
from pathlib import Path
from typing import Any

import numpy as np
from qi_tuna_destination_analysis_receipt import receipt as nominal_one_receipt
from qi_tuna_destination_one_analysis import ROOT, SHOTS, digest, json_bytes, ordered_map
from qi_tuna_destination_prefix import replay as nominal_zero_replay

NOMINAL_ONE = ROOT / "results/quantum_inspire/runs/20261027T232908Z-tuna-destination-one-response"
NOMINAL_ZERO = ROOT / "results/quantum_inspire/runs/2026-10-27T194754Z-tuna-destination-response"
PHYSICAL_QUBITS = (4, 11, 6)
ARMS = ("baseline-before", "rotated-destinations", "baseline-after")


def joint_job(task: tuple[Path, str, int]) -> dict[str, Any]:
    """Decode joint outcomes from one validated, retained, ordered shot list."""
    run, batch, job = task
    directory = run / batch
    manifest = json.loads((directory / "cases.json").read_bytes())
    filename = manifest["circuits"][0]["file"]
    raw = directory / "raw" / f"{filename}.json"
    shots = json.loads(raw.read_bytes())
    if (
        not isinstance(shots, list)
        or len(shots) != SHOTS
        or any(type(shot) is not str or len(shot) != 20 or set(shot) - {"0", "1"} for shot in shots)
    ):
        raise ValueError("joint replay requires 4096 ordered 20-bit binary strings")
    bits = np.array([list(shot[::-1]) for shot in shots], dtype=np.int64)
    early_bits = (19, 17, 18) if batch.endswith("rotated-destinations") else (17, 18, 19)
    early = bits[:, early_bits]
    terminal = bits[:, PHYSICAL_QUBITS]
    indices = np.concatenate((early, terminal), axis=1) @ (1 << np.arange(6, dtype=np.int64))
    joint = np.bincount(indices, minlength=64)
    mismatch = (early ^ terminal) @ (1 << np.arange(3, dtype=np.int64))
    mismatch_counts = np.bincount(mismatch, minlength=8)
    coordinates = np.arange(64, dtype=np.int64)[:, None]
    masks = np.arange(64, dtype=np.int64)[None, :]
    parity = np.zeros((64, 64), dtype=np.int64)
    for position in range(6):
        parity ^= ((coordinates >> position) & 1) * ((masks >> position) & 1)
    parity_numerators = joint @ (1 - 2 * parity)
    return {
        "batch": batch,
        "job": job,
        "raw": raw.relative_to(ROOT).as_posix(),
        "raw_sha256": digest(raw),
        "early_classical_bits": list(early_bits),
        "joint_counts": joint.tolist(),
        "disagreement_counts": mismatch_counts.tolist(),
        "parity_numerators": parity_numerators.tolist(),
    }


def validate_marginals(counts: list[int], expected: list[list[int]]) -> None:
    """Require each joint-table projection to equal its frozen early/final table."""
    if len(counts) != 64 or any(type(count) is not int or count < 0 for count in counts):
        raise ValueError("joint counts require 64 nonnegative integers")
    coordinates = np.arange(64, dtype=np.int64)
    observed = []
    for index in range(3):
        cell = 2 * ((coordinates >> index) & 1) + ((coordinates >> (index + 3)) & 1)
        projected = np.zeros(4, dtype=np.int64)
        np.add.at(projected, cell, counts)
        observed.append(projected.tolist())
    if observed != expected:
        raise ValueError("joint marginal projections differ from frozen per-qubit tables")


def analyze_case(run: Path, rows: list[dict[str, Any]], outcome: str) -> dict[str, Any]:
    """Compute exact integer contrasts without combining preparation cases."""
    jobs = ordered_map(joint_job, [(run, row["batch"], row["job"]) for row in rows])
    for job, row in zip(jobs, rows, strict=True):
        validate_marginals(job["joint_counts"], row["joint_counts"])
    before, rotated, after = [np.asarray(row["parity_numerators"], dtype=np.int64) for row in jobs]
    response = 2 * rotated - before - after
    endpoint = after - before
    joint_before, joint_rotated, joint_after = [np.asarray(row["joint_counts"], dtype=np.int64) for row in jobs]
    total_variation_numerator = int(np.abs(2 * joint_rotated - joint_before - joint_after).sum())
    return {
        "primary_case_outcome": outcome,
        "jobs": jobs,
        "parity_response_numerators": response.tolist(),
        "parity_response_denominator": 2 * SHOTS,
        "parity_endpoint_numerators": endpoint.tolist(),
        "parity_endpoint_denominator": SHOTS,
        "empirical_total_variation_numerator": total_variation_numerator,
        "empirical_total_variation_denominator": 4 * SHOTS,
    }


def uncertainty() -> dict[str, str | int]:
    """Bound 63 predetermined parity functions and two contrasts simultaneously."""
    with localcontext() as context:
        context.prec = 60
        logarithm = Decimal(25200).ln()
        response = (Decimal(3) * logarithm / SHOTS).sqrt().quantize(Decimal("0.000000000001"), rounding=ROUND_CEILING)
        endpoint = (Decimal(4) * logarithm / SHOTS).sqrt().quantize(Decimal("0.000000000001"), rounding=ROUND_CEILING)
    return {
        "parity_functions": 63,
        "contrasts_per_function": 2,
        "simultaneous_confidence": "0.99",
        "response_radius_upper": str(response),
        "endpoint_radius_upper": str(endpoint),
    }


def analyze() -> dict[str, Any]:
    """Revalidate the frozen analyses before deriving the joint-response descriptions."""
    one = nominal_one_receipt(NOMINAL_ONE)
    saved_one = (NOMINAL_ONE / "analysis-serialization-receipt.json").read_bytes()
    if json_bytes(one) != saved_one:
        raise ValueError("nominal-one encoding receipt differs from validated acquisition")
    one_report = json.loads((NOMINAL_ONE / "analysis-canonical.json").read_bytes())
    zero = nominal_zero_replay(NOMINAL_ZERO)
    saved_zero = (NOMINAL_ZERO / "nominal-zero-prefix-recovery-order.json").read_bytes()
    if json_bytes(zero) != saved_zero or zero["primary_case_outcome"] != "implementation route unavailable":
        raise ValueError("nominal-zero prefix differs from the retained primary refusal")
    validator_paths = (
        ROOT / "scripts/qi_tuna_destination_analysis_receipt.py",
        ROOT / "scripts/qi_tuna_destination_prefix.py",
        ROOT / "scripts/qi_tuna_readout_destination_analysis.py",
        NOMINAL_ONE / "analysis-serialization-receipt.json",
        NOMINAL_ZERO / "nominal-zero-prefix-recovery-order.json",
    )
    return {
        "schema": "qi-tuna-joint-response-exploration-v1",
        "cases": {
            "nominal_one": analyze_case(NOMINAL_ONE, one_report["jobs"], one["outcome"]),
            "nominal_zero_prefix": analyze_case(NOMINAL_ZERO, zero["jobs"], zero["primary_case_outcome"]),
        },
        "bit_order_low_to_high": ["early_q4", "early_q11", "early_q6", "terminal_q4", "terminal_q11", "terminal_q6"],
        "disagreement_order_low_to_high": ["q4", "q11", "q6"],
        "nominal_one_posthoc_uncertainty": uncertainty(),
        "validator_inputs": {
            **one["frozen_sources"],
            **{path.relative_to(ROOT).as_posix(): digest(path) for path in validator_paths},
        },
        "boundary": (
            "Post-acquisition descriptions of retained binary outcomes; the nominal-zero prefix does not reopen "
            "its unavailable primary endpoint. Parity intervals target realized predictable conditional averages "
            "under the frozen case's chronology and filtration assumptions, not causal effects or populations. "
            "Empirical total variation is an uncorrected histogram statistic without an uncertainty interval."
        ),
        "producer_sha256": digest(Path(__file__)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--out", type=Path)
    operation.add_argument("--check", type=Path)
    arguments = parser.parse_args()
    content = json_bytes(analyze())
    if arguments.check:
        if arguments.check.read_bytes() != content:
            raise SystemExit("retained joint-response analysis differs from exact replay")
    else:
        with arguments.out.open("xb") as destination:
            destination.write(content)
    print("Six retained joint-response distributions replay within their original case boundaries.")


if __name__ == "__main__":
    main()
