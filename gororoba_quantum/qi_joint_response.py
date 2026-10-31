"""Joint early/terminal response of ordered Quantum Inspire shots under an explicit layout.

A destination-control acquisition measures a register twice per shot: early
classical bits written by a mid-circuit measurement and the terminal
measurement of the same physical qubits. Layout names what the decoding
needs: the ordered shot count, the bit width of one shot string, the
terminal qubit positions and, per arm, the early bit positions, which the
rotated arm permutes. decode builds the joint distribution over
(early, terminal) bit pairs, the per-qubit disagreement histogram and every
parity numerator; contrasts forms the integer response and endpoint
contrasts of the three arms; replay_run reads the arms of one retained run
through qi_records and applies both. A shot list of another width or count,
or an arm the layout does not name, is rejected rather than reinterpreted.
The retained Tuna-17 analyses keep their pinned producers
(scripts/qi_tuna_joint_response.py), whose digests their evidence binds.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import ROUND_CEILING, Decimal, localcontext
from pathlib import Path
from typing import Any

import numpy as np

import qi_records
from parallel import ordered_map
from qi_records import require


@dataclass(frozen=True)
class Layout:
    """Bit positions index a shot string from its rightmost character (Qiskit and cQASM outcome order)."""

    shots: int
    width: int
    terminal_qubits: tuple[int, ...]
    early_bits: dict[str, tuple[int, ...]]
    arms: tuple[str, str, str] = ("baseline-before", "rotated-destinations", "baseline-after")

    def __post_init__(self) -> None:
        k = len(self.terminal_qubits)
        require(k > 0 and self.shots > 0 and self.width > 0, "layout needs qubits, shots and a width")
        require(set(self.arms) <= set(self.early_bits), "every arm needs its early bit positions")
        for arm, bits in self.early_bits.items():
            require(len(bits) == k, f"arm {arm} names {len(bits)} early bits for {k} terminal qubits")
            require(all(0 <= b < self.width for b in bits + self.terminal_qubits), f"arm {arm} indexes past the width")


TUNA_DESTINATION = Layout(
    shots=4096,
    width=20,
    terminal_qubits=(4, 11, 6),
    early_bits={
        "baseline-before": (17, 18, 19),
        "rotated-destinations": (19, 17, 18),
        "baseline-after": (17, 18, 19),
    },
)


def _parity_signs(n: int) -> np.ndarray:
    """(-1)^(popcount(coordinate & mask)) over all 2^n coordinates and masks."""
    size = 1 << n
    coordinates = np.arange(size, dtype=np.int64)[:, None]
    masks = np.arange(size, dtype=np.int64)[None, :]
    parity = np.zeros((size, size), dtype=np.int64)
    for position in range(n):
        parity ^= ((coordinates >> position) & 1) * ((masks >> position) & 1)
    return 1 - 2 * parity


def decode(
    shots: Sequence[str], early_bits: Sequence[int], terminal_qubits: Sequence[int], layout: Layout
) -> dict[str, Any]:
    """Joint counts, disagreement counts and parity numerators of one ordered shot list."""
    require(len(shots) == layout.shots, f"joint decoding requires {layout.shots} ordered shots")
    require(
        all(isinstance(s, str) and len(s) == layout.width and not set(s) - {"0", "1"} for s in shots),
        f"joint decoding requires {layout.width}-bit binary strings",
    )
    k = len(terminal_qubits)
    bits = np.array([list(shot[::-1]) for shot in shots], dtype=np.int64)
    early = bits[:, list(early_bits)]
    terminal = bits[:, list(terminal_qubits)]
    weights = 1 << np.arange(2 * k, dtype=np.int64)
    indices = np.concatenate((early, terminal), axis=1) @ weights
    joint = np.bincount(indices, minlength=1 << (2 * k))
    mismatch = (early ^ terminal) @ weights[:k]
    return {
        "early_classical_bits": list(early_bits),
        "joint_counts": joint.tolist(),
        "disagreement_counts": np.bincount(mismatch, minlength=1 << k).tolist(),
        "parity_numerators": (joint @ _parity_signs(2 * k)).tolist(),
    }


def marginal_projections(joint_counts: Sequence[int], qubits: int) -> list[list[int]]:
    """Per-qubit (early, terminal) 2x2 tables, flattened as early*2 + terminal, projected from the joint table."""
    counts = np.asarray(joint_counts, dtype=np.int64)
    require(counts.shape == (1 << (2 * qubits),) and (counts >= 0).all(), "joint counts need 4^k nonnegative integers")
    coordinates = np.arange(counts.size, dtype=np.int64)
    tables = []
    for index in range(qubits):
        cell = 2 * ((coordinates >> index) & 1) + ((coordinates >> (index + qubits)) & 1)
        projected = np.zeros(4, dtype=np.int64)
        np.add.at(projected, cell, counts)
        tables.append(projected.tolist())
    return tables


def contrasts(jobs: Sequence[dict[str, Any]], shots: int) -> dict[str, Any]:
    """Integer response (2 rotated - before - after) and endpoint (after - before) contrasts of the three arms."""
    require(len(jobs) == 3, "contrasts need the before, rotated and after arms")
    before, rotated, after = [np.asarray(job["parity_numerators"], dtype=np.int64) for job in jobs]
    joint_before, joint_rotated, joint_after = [np.asarray(job["joint_counts"], dtype=np.int64) for job in jobs]
    return {
        "parity_response_numerators": (2 * rotated - before - after).tolist(),
        "parity_response_denominator": 2 * shots,
        "parity_endpoint_numerators": (after - before).tolist(),
        "parity_endpoint_denominator": shots,
        "empirical_total_variation_numerator": int(np.abs(2 * joint_rotated - joint_before - joint_after).sum()),
        "empirical_total_variation_denominator": 4 * shots,
    }


def uncertainty(
    shots: int, parity_functions: int, contrasts_per_function: int = 2, miss: str = "0.01"
) -> dict[str, Any]:
    """Hoeffding radii holding every parity function's two contrasts simultaneously with probability 1 - miss."""
    with localcontext() as context:
        context.prec = 60
        logarithm = (Decimal(parity_functions * contrasts_per_function * 2) / Decimal(miss)).ln()
        quantum = Decimal("0.000000000001")
        response = (Decimal(3) * logarithm / shots).sqrt().quantize(quantum, rounding=ROUND_CEILING)
        endpoint = (Decimal(4) * logarithm / shots).sqrt().quantize(quantum, rounding=ROUND_CEILING)
    return {
        "parity_functions": parity_functions,
        "contrasts_per_function": contrasts_per_function,
        "simultaneous_confidence": str(Decimal(1) - Decimal(miss)),
        "response_radius_upper": str(response),
        "endpoint_radius_upper": str(endpoint),
    }


def _arm_job(task: tuple[str, str, str, Layout]) -> dict[str, Any]:
    run, batch, arm, layout = task
    directory = Path(run) / batch
    record = qi_records.load_run(directory)
    acquisition = qi_records.validate_run(record, f"Quantum Inspire batch {batch}")
    require(len(acquisition.jobs) == 1 and acquisition.completed, f"arm {arm} needs one completed job")
    require(
        acquisition.shots == layout.shots, f"arm {arm} ran {acquisition.shots} shots, the layout names {layout.shots}"
    )
    job = acquisition.jobs[0]
    raw = job.raw
    require(raw is not None, f"arm {arm} retained no raw shots")
    decoded = decode(raw or (), layout.early_bits[arm], layout.terminal_qubits, layout)
    return {
        "batch": batch,
        "arm": arm,
        "job": job.job_id,
        "raw": f"{batch}/raw/{job.file}.json",
        "raw_sha256": record["digests"][f"raw/{job.file}.json"],
        **decoded,
    }


def replay_run(run: Path, batches: dict[str, str], layout: Layout) -> dict[str, Any]:
    """Decode the three arms of one retained run (arm -> batch directory) and form their contrasts."""
    require(set(batches) == set(layout.arms), f"batches must name exactly the arms {list(layout.arms)}")
    jobs = ordered_map(_arm_job, [(str(run), batches[arm], arm, layout) for arm in layout.arms])
    return {"jobs": jobs, **contrasts(jobs, layout.shots)}
