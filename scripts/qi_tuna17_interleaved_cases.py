"""Tuna-17 follow-up case: interleaved T1 rounds, a single-qubit arm and a q12 Ramsey phase scan, with a QX twin.

The retained characterization series (scripts/qi_tuna17_characterization_cases.py) found a non-exponential
T1 on 15 of 17 qubits, a positive step on the batch that held the three longest delays, and ladder verdicts that
opposed the prediction on eight qubits while all 17 qubits were driven together. This case adds three arms, each its
own series directory:

- interleaved_t1: ROUNDS rounds, each a seeded random order of the delays of T1_ROUND_CYCLES (the six retained delays
  and five more at 1, 2.5, 7.5, 120, 160 and 240 us). The provider holds a hardware batch to three circuits, so a round
  is eleven provider batches, and every provider batch holds the zero-delay circuit (t1-0, X on every qubit: the
  prepared-1 anchor and the delay 0 point), the prepared-0 circuit (readout-0) and one delay circuit, in a seeded random
  order. A level shift common to the three jobs of a batch cancels in the population (p - a0) / (a1 - a0), and the
  replicate of each delay in the other round separates a tail from a job-level scatter.
- single_qubit: for each qubit of SINGLE, one qubit driven and the other sixteen idle: the prepared-1 circuit, T1 at
  SINGLE_T1_CYCLES with both anchors in the batch, and the X90 ladder at SINGLE_LADDER_TURNS.
- q12_phase: a Ramsey circuit X90, Rz(angle), X90 on one qubit, angles on the pi/36 grid in steps of pi/4, on PHASE
  qubits (q12 at two idle waits, the other two without a wait); the fringe offset is the static z rotation between two
  pulses.

Order. Every order comes from one retained QRNG draw (DRAW), consumed in index order, each value once, by a rejection
shuffle; schedule() states the indices each component takes. While DRAW is None the batch directories and schedule.json
do not exist: only the circuit library, the indexes and prediction.json are generated and qrng_request.json records the
draw to take.

Profiles: tuna_17 (17 qubits, 8,192 shots per circuit) and qx (the same texts on 10 qubits at 1,024 shots, with the
qubit map of SINGLE and PHASE). Bit order: qubit 0 is the rightmost character of a shot.

    --write ROOT        write ROOT/characterization_interleaved_{tuna_17,qx}/
    --check ROOT        regenerate and compare every file except CASE.md; prints a skip while DRAW is None
    --request           print the QRNG draw this case waits for
    --local             run the qx profile on the local qxelarator emulator against its noiseless expectation
    --sanity RUN_DIR    after a collection: shots, fixed outcomes, admission and execution-start status
    --analyze OUT RUN_DIR...   per-arm rows and verdicts
    --submit ARM_DIR RUNS_DIR STAMP APPROVAL   submit one series, refusing unless the backend reads idle
    --self-test         design, order, admission, estimator and phase-fit invariants

Usage: "$PYTHON" scripts/qi_tuna17_interleaved_cases.py (--write ROOT | --check ROOT | --request | --local |
       --sanity RUN_DIR | --analyze OUT RUN_DIR... | --submit ARM_DIR RUNS_DIR STAMP APPROVAL | --self-test)
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import time
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import qi_tuna17_characterization_cases as base  # noqa: E402

SCHEMA = "qi-tuna17-interleaved-cases-v1"
ANALYSIS_SCHEMA = "qi-tuna17-interleaved-analysis-v1"
ARMS = ("interleaved_t1", "single_qubit", "q12_phase")
CYCLE_SECONDS = base.CYCLE_SECONDS
BATCH_LIMIT = base.BATCH_LIMIT
# Delays in 20 ns cycles: 1, 2.5, 5, 7.5, 10, 20, 40, 80, 120, 160 and 240 us. The first four and 10 us resolve the fast
# scale the retained residuals suggest; 80 to 240 us bound the slow tail; 5, 10, 20, 40 and 80 us repeat the retained
# set.
T1_ROUND_CYCLES = (50, 125, 250, 375, 500, 1000, 2000, 4000, 6000, 8000, 12000)
ROUNDS = 2
# Arm qubits by profile; the qx entries stand in position for the tuna_17 qubits that the 10-qubit emulator lacks.
SINGLE = {"tuna_17": (5, 7, 14, 0, 4, 10, 11, 16), "qx": (5, 7, 9, 0, 4, 6, 3, 1)}
SINGLE_T1_CYCLES = (250, 1000, 4000)
SINGLE_LADDER_TURNS = (8, 32, 64)
PHASE = {"tuna_17": (12, 8, 4), "qx": (9, 8, 4)}
PHASE_WAIT_CYCLES = 25
PHASE_STEPS = tuple(range(0, 72, 9))
PROFILES: dict[str, dict[str, Any]] = {
    "tuna_17": {"backend": "tuna_17", "backend_type_id": 7, "nqubits": 17, "shots": 8192},
    "qx": {"backend": "QXsinglenodesimulator", "backend_type_id": 1, "nqubits": 10, "shots": 1024},
}
# The retained QRNG draw of this case: None until the draw named by qrng_request() is retained, then its canonical path.
DRAW: str | None = None
DRAW_LENGTH = 256
# Decision thresholds. The probability bound is the retained characterization's; the AICc gain is the usual 4.
LACK_OF_FIT_PROBABILITY = 0.01
AICC_GAIN = 4.0
MIN_READOUT_SPAN = base.MIN_READOUT_SPAN
# Per-qubit label counts are descriptive. The pooled tail verdict reads the AICc gain summed over qubits against this
# threshold, which lies far above the null spread of the sum and below its value on a retained-size tail.
TAIL_STATISTIC_THRESHOLD = 200.0
POOLED_QUBITS = 12
SANITY_WRONG_QUBITS = base.SANITY_WRONG_QUBITS
# Level and window of the phase verdict, in radians: the refit of the q12 term, its half-width and the null bound.
PHASE_TARGET = -0.15
PHASE_HALF_WIDTH = 0.05
PHASE_NULL = 0.05
# A fringe whose cosine amplitude lies below this carries no phase.
MIN_FRINGE_AMPLITUDE = 0.25
# Backend statuses that admit an execution start, and the longest gap between status reads that still covers a start.
START_STATUSES = ("idle", "executing")
MAX_TRACE_GAP_SECONDS = 45.0
TRACE_POLL_SECONDS = 15.0
JOB_SECONDS, SHOT_SECONDS = base.JOB_SECONDS, base.SHOT_SECONDS
RETAINED_ANALYSIS = ROOT / "results/quantum_inspire/characterization_tuna_17_analysis.json"
RETAINED_SHAPE = ROOT / "results/quantum_inspire/characterization_tuna_17_t1_shape_analysis.json"
RETAINED_RUNS = ROOT / "results/quantum_inspire/runs"
RETAINED_RUN_STAMP = "2026-11-16T0401Z-characterization_tuna_17-characterization_tuna_17-batch-0"


def case_directory(root: Path, profile_name: str) -> Path:
    return root / f"characterization_interleaved_{profile_name}"


def rounded(value: float) -> float:
    return float(f"{value:.4g}")


# ---------------------------------------------------------------------------------------------------------------------
# Circuits
# ---------------------------------------------------------------------------------------------------------------------


def all_t1_text(nqubits: int, cycles: int) -> str:
    every = range(nqubits)
    lines = [f"X q[{q}]" for q in every] + ([f"wait({cycles}) q[{q}]" for q in every] if cycles else [])
    return base.circuit(nqubits, lines)


def library(profile_name: str) -> dict[str, dict[str, Any]]:
    """Circuit file name -> text, kind and parameters; kind names the role a circuit plays in an arm."""
    nqubits = PROFILES[profile_name]["nqubits"]
    found: dict[str, dict[str, Any]] = {
        "readout-0.cq": {"text": base.circuit(nqubits, []), "kind": "anchor0", "driven": [], "expected_p1": 0.0}
    }
    for cycles in (0, *T1_ROUND_CYCLES):
        name = f"t1-{cycles}.cq"
        found[name] = {
            "text": all_t1_text(nqubits, cycles),
            "kind": "anchor1" if cycles == 0 else "t1",
            "wait_cycles": cycles,
            "driven": list(range(nqubits)),
            "expected_p1": 1.0,
        }
    for qubit in SINGLE[profile_name]:
        found[f"single-q{qubit}-prep1.cq"] = {
            "text": base.circuit(nqubits, [f"X q[{qubit}]"]),
            "kind": "single_prep1",
            "qubit": qubit,
            "driven": [qubit],
            "expected_p1": 1.0,
        }
        for cycles in SINGLE_T1_CYCLES:
            found[f"single-q{qubit}-t1-{cycles}.cq"] = {
                "text": base.circuit(nqubits, [f"X q[{qubit}]", f"wait({cycles}) q[{qubit}]"]),
                "kind": "single_t1",
                "qubit": qubit,
                "wait_cycles": cycles,
                "driven": [qubit],
                "expected_p1": 1.0,
            }
        for turns in SINGLE_LADDER_TURNS:
            found[f"single-q{qubit}-x90-{turns}.cq"] = {
                "text": base.circuit(nqubits, [f"X90 q[{qubit}]"] * (4 * turns)),
                "kind": "single_x90",
                "qubit": qubit,
                "pulses": 4 * turns,
                "driven": [qubit],
                "expected_p1": 0.0,
            }
    for qubit, wait in ((PHASE[profile_name][0], PHASE_WAIT_CYCLES), *((q, 0) for q in PHASE[profile_name])):
        for step in PHASE_STEPS:
            angle = step * math.pi / 36
            lines = [f"X90 q[{qubit}]"] + ([f"wait({wait}) q[{qubit}]"] if wait else [])
            lines += [f"Rz({angle!r}) q[{qubit}]", f"X90 q[{qubit}]"]
            found[f"ramsey-q{qubit}-w{wait}-s{step:02d}.cq"] = {
                "text": base.circuit(nqubits, lines),
                "kind": "ramsey",
                "qubit": qubit,
                "wait_cycles": wait,
                "step": step,
                "angle": angle,
                "driven": [qubit],
                "expected_p1": (1 + math.cos(angle)) / 2,
            }
    return found


def usage(profile_name: str) -> dict[str, list[str]]:
    """Arm -> circuit names with their multiplicity in the series, in no particular order."""
    names = library(profile_name)
    interleaved: list[str] = []
    for cycles in T1_ROUND_CYCLES:
        interleaved += [f"t1-{cycles}.cq"] * ROUNDS + ["readout-0.cq", "t1-0.cq"] * ROUNDS
    single: list[str] = []
    for qubit in SINGLE[profile_name]:
        single += [f"single-q{qubit}-t1-{c}.cq" for c in SINGLE_T1_CYCLES] + [f"single-q{qubit}-prep1.cq"] * 3
        single += ["readout-0.cq"] * 3 + [f"single-q{qubit}-x90-{t}.cq" for t in SINGLE_LADDER_TURNS]
    phase = [name for name, row in names.items() if row["kind"] == "ramsey"]
    return {"interleaved_t1": interleaved, "single_qubit": single, "q12_phase": phase}


# ---------------------------------------------------------------------------------------------------------------------
# Order from a QRNG draw
# ---------------------------------------------------------------------------------------------------------------------


class Stream:
    """Values of one retained uint16 draw taken in index order; below() rejects the values that would bias a modulus."""

    def __init__(self, values: Sequence[int]) -> None:
        self.values = [int(v) for v in values]
        self.position = 0

    def next(self) -> int:
        if self.position >= len(self.values):
            raise ValueError(f"the draw holds {len(self.values)} values and the order needs more")
        value = self.values[self.position]
        self.position += 1
        return value

    def below(self, bound: int) -> int:
        limit = (65536 // bound) * bound
        while True:
            value = self.next()
            if value < limit:
                return value % bound

    def shuffle(self, items: Sequence[Any]) -> list[Any]:
        """Fisher-Yates from the last position down; one value per position above the first, plus rejected values."""
        out = list(items)
        for last in range(len(out) - 1, 0, -1):
            pick = self.below(last + 1)
            out[last], out[pick] = out[pick], out[last]
        return out


def schedule(profile_name: str, values: Sequence[int]) -> dict[str, Any]:
    """The batches of every arm and the draw indices each component consumed, from one draw read in index order."""
    stream = Stream(values)
    consumed: dict[str, list[int]] = {}

    def mark(name: str, start: int) -> None:
        consumed[name] = [start, stream.position - 1]

    arms: dict[str, list[dict[str, Any]]] = {arm: [] for arm in ARMS}
    for round_index in range(ROUNDS):
        start = stream.position
        order = stream.shuffle(T1_ROUND_CYCLES)
        for cycles in order:
            names = stream.shuffle(["readout-0.cq", "t1-0.cq", f"t1-{cycles}.cq"])
            arms["interleaved_t1"].append({"circuits": names, "round": round_index, "wait_cycles": cycles})
        mark(f"interleaved_t1 round {round_index}", start)
    start = stream.position
    for qubit in stream.shuffle(SINGLE[profile_name]):
        units: list[tuple[str, list[str]]] = [
            (f"t1-{c}", ["readout-0.cq", f"single-q{qubit}-prep1.cq", f"single-q{qubit}-t1-{c}.cq"])
            for c in SINGLE_T1_CYCLES
        ]
        units.append(("x90", [f"single-q{qubit}-x90-{t}.cq" for t in SINGLE_LADDER_TURNS]))
        for unit, names in (units[i] for i in stream.shuffle(range(len(units)))):
            arms["single_qubit"].append({"circuits": stream.shuffle(names), "qubit": qubit, "unit": unit})
    mark("single_qubit", start)
    start = stream.position
    ramsey = [name for name, row in library(profile_name).items() if row["kind"] == "ramsey"]
    order = stream.shuffle(ramsey)
    for first in range(0, len(order), BATCH_LIMIT):
        arms["q12_phase"].append({"circuits": order[first : first + BATCH_LIMIT]})
    mark("q12_phase", start)
    return {"consumed": consumed, "arms": arms}


def draw_values(root: Path = ROOT) -> list[int] | None:
    """The retained draw's values through the seed-source admit function, or None while the draw is not taken."""
    if DRAW is None:
        return None
    from qrng_seeds import read_record  # noqa: PLC0415 - imports the draw adapters

    record = read_record(DRAW, root)
    if record["type"] != "uint16":
        raise ValueError(f"{DRAW} holds {record['type']} values; the order's rejection limit assumes uint16")
    return [int(v) for v in record["values"]]


def qrng_values_needed(profile_name: str) -> int:
    """Values the order consumes when no value is rejected."""
    singles = len(SINGLE[profile_name])
    units = len(SINGLE_T1_CYCLES) + 1
    needed = ROUNDS * (len(T1_ROUND_CYCLES) - 1 + len(T1_ROUND_CYCLES) * 2)
    needed += singles - 1 + singles * ((units - 1) + units * 2)
    return needed + len(usage(profile_name)["q12_phase"]) - 1


def qrng_request() -> dict[str, Any]:
    """The draw that sets the order of the series; made once, cited by the case manifest, owned whole by this case."""
    return {
        "schema": SCHEMA + "-qrng-request",
        "source": "ANU Quantum Numbers (docs/notes/qrng/README.md, first in the fallback order)",
        "command": '"$PYTHON" scripts/anu_qrng.py draw --out docs/evidence/anu_qrng --length 256 --type uint16',
        "values_requested": DRAW_LENGTH,
        "values_needed_without_rejection": qrng_values_needed("tuna_17"),
        "consumption": "index order, each value once; Stream.below rejects a value at or above floor(65536 / n) * n",
        "after_the_draw": "set DRAW in scripts/qi_tuna17_interleaved_cases.py to the retained path and run --write",
        "approval": "none: a free ANU draw (AGENTS.md, Hardware services)",
    }


# ---------------------------------------------------------------------------------------------------------------------
# Linear algebra and the estimator's design
# ---------------------------------------------------------------------------------------------------------------------


def invert(matrix: list[list[float]]) -> list[list[float]]:
    """Gauss-Jordan inverse with partial pivoting; ValueError when a pivot vanishes."""
    size = len(matrix)
    work = [row[:] + [1.0 if i == j else 0.0 for j in range(size)] for i, row in enumerate(matrix)]
    for col in range(size):
        pivot = max(range(col, size), key=lambda r: abs(work[r][col]))
        if abs(work[pivot][col]) < 1e-300:
            raise ValueError("singular matrix")
        work[col], work[pivot] = work[pivot], work[col]
        scale = work[col][col]
        work[col] = [v / scale for v in work[col]]
        for r in range(size):
            if r != col and work[r][col] != 0.0:
                factor = work[r][col]
                work[r] = [a - factor * b for a, b in zip(work[r], work[col], strict=True)]
    return [row[size:] for row in work]


def matrix_rank(rows: list[list[float]], tolerance: float = 1e-9) -> int:
    """Rank by elimination after scaling every column to unit norm."""
    if not rows:
        return 0
    columns = len(rows[0])
    norms = [math.sqrt(sum(row[c] ** 2 for row in rows)) or 1.0 for c in range(columns)]
    work = [[row[c] / norms[c] for c in range(columns)] for row in rows]
    rank = 0
    for col in range(columns):
        pivot = max(range(rank, len(work)), key=lambda r: abs(work[r][col]), default=None)
        if pivot is None or abs(work[pivot][col]) < tolerance:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        for r in range(rank + 1, len(work)):
            factor = work[r][col] / work[rank][col]
            work[r] = [a - factor * b for a, b in zip(work[r], work[rank], strict=True)]
        rank += 1
        if rank == len(work):
            break
    return rank


def covariance(rows: list[tuple[list[float], float]]) -> list[list[float]]:
    """Inverse of the information sum of gradient rows (gradient, variance)."""
    size = len(rows[0][0])
    info = [[0.0] * size for _ in range(size)]
    for gradient, variance in rows:
        for i in range(size):
            for j in range(size):
                info[i][j] += gradient[i] * gradient[j] / variance
    return invert(info)


def decay(shape: str, theta: Sequence[float], t_us: float) -> float:
    """Population at t_us: single (T), plateau (T, plateau c), two_rate (fast T, slow T, slow weight)."""
    if shape == "single":
        return math.exp(-t_us / theta[0])
    if shape == "plateau":
        return (1 - theta[1]) * math.exp(-t_us / theta[0]) + theta[1]
    return (1 - theta[2]) * math.exp(-t_us / theta[0]) + theta[2] * math.exp(-t_us / theta[1])


def decay_gradient(shape: str, theta: Sequence[float], t_us: float) -> list[float]:
    """Derivative of decay() with respect to each natural parameter, by a central difference of relative step 1e-6."""
    out = []
    for index in range(len(theta)):
        step = 1e-6 * max(abs(theta[index]), 1e-3)
        up, down = list(theta), list(theta)
        up[index] += step
        down[index] -= step
        out.append((decay(shape, up, t_us) - decay(shape, down, t_us)) / (2 * step))
    return out


def job_level_variance(zero: Sequence[float], one: Sequence[float], count: int) -> float:
    """Job-specific level variance from the scatter of the span a1 - a0 of anchor pairs, floored at 0.

    A level shift common to the two jobs of a batch cancels in a1 - a0, which is what anchoring does to a population,
    so the scatter of the span beyond its binomial variance (the sum of the two jobs' terms) is the variance of the
    jobs' own levels, two jobs to a pair; zero and one hold one value per pair at count shots.
    """
    if len(zero) < 2 or len(zero) != len(one):
        return 0.0
    spans = [b - a for a, b in zip(zero, one, strict=True)]
    mean = sum(spans) / len(spans)
    sample = sum((s - mean) ** 2 for s in spans) / (len(spans) - 1)
    binomial = sum(
        base.binomial_variance(a, count) + base.binomial_variance(b, count) for a, b in zip(zero, one, strict=True)
    ) / len(spans)
    return max(0.0, sample - binomial) / 2


def expected_errors(
    e01: float, e11: float, truth: dict[str, Any], tau2: float, count: int, rounds: int = ROUNDS
) -> dict[str, Any]:
    """Standard errors the design gives T1 and the plateau of one qubit when the retained plateau model is true.

    Rows are the nonzero delays of T1_ROUND_CYCLES, rounds times; the variance of a population holds the binomial
    terms of the delay job and of the two anchor jobs of its batch and the job-level scatter tau2 on each of the three
    (the shared level that anchoring cancels is not credited, so the figures lean conservative). The free batch levels
    of design_summary() widen the plateau error further; that figure is reported there.
    """
    span = e11 - e01
    shapes = {"single": [truth["single_us"]], "plateau": [truth["plateau_us"], truth["plateau"]]}
    found: dict[str, Any] = {}
    for shape, theta in shapes.items():
        rows = []
        for cycles in T1_ROUND_CYCLES:
            t_us = cycles * CYCLE_SECONDS * 1e6
            x = decay(shape, theta, t_us)
            p = e01 + span * x
            variance = (
                base.binomial_variance(p, count)
                + (1 - x) ** 2 * base.binomial_variance(e01, count)
                + x**2 * base.binomial_variance(e11, count)
                + tau2 * (1 + (1 - x) ** 2 + x**2)
            ) / span**2
            rows += [(decay_gradient(shape, theta, t_us), variance)] * rounds
        cov = covariance(rows)
        found[shape] = [math.sqrt(cov[i][i]) for i in range(len(theta))]
    return {
        "se_single_us": rounded(found["single"][0]),
        "se_plateau_us": rounded(found["plateau"][0]),
        "se_plateau": rounded(found["plateau"][1]),
        "plateau_z": rounded(truth["plateau"] / found["plateau"][1]) if found["plateau"][1] > 0 else None,
    }


def design_matrices(
    e01: float, e11: float, theta: Sequence[float], batches: int, delays: Sequence[int]
) -> tuple[list[list[float]], list[list[float]], list[float]]:
    """Jacobians of the batch-level model with and without anchors, and the row probabilities of the first.

    Parameters with anchors: T, plateau c, e01, e11 and a level shift per batch except the first. Rows: per batch the
    prepared-0 anchor (e01 + s), the prepared-1 anchor (e11 + s) and the delay circuit (e01 + span x + s). Without
    anchors e01 and e11 are known, so the delay rows alone carry T, c and the batch shifts.
    """
    span = e11 - e01
    columns = 4 + batches - 1
    with_anchors: list[list[float]] = []
    probabilities: list[float] = []
    without: list[list[float]] = []
    for b in range(batches):
        shift_column = [0.0] * (batches - 1)
        if b:
            shift_column[b - 1] = 1.0
        t_us = delays[b] * CYCLE_SECONDS * 1e6
        x = decay("plateau", theta, t_us)
        grad = decay_gradient("plateau", theta, t_us)
        with_anchors.append([0.0, 0.0, 1.0, 0.0, *shift_column])
        with_anchors.append([0.0, 0.0, 0.0, 1.0, *shift_column])
        with_anchors.append([span * grad[0], span * grad[1], 1 - x, x, *shift_column])
        probabilities += [e01, e11, e01 + span * x]
        without.append([span * grad[0], span * grad[1], *shift_column])
    if len(with_anchors[0]) != columns:
        raise ValueError("design column count")
    return with_anchors, without, probabilities


def design_summary(e01: float, e11: float, theta: Sequence[float], tau2: float, count: int) -> dict[str, Any]:
    """Identifiability of the plateau from batch levels: ranks with and without anchors and the plateau error with
    every batch level free, for the delays of every round in series order of the first round."""
    delays = [c for _ in range(ROUNDS) for c in T1_ROUND_CYCLES]
    with_anchors, without, probabilities = design_matrices(e01, e11, theta, len(delays), delays)
    rows = [(row, base.binomial_variance(p, count) + tau2) for row, p in zip(with_anchors, probabilities, strict=True)]
    cov = covariance(rows)
    return {
        "batches": len(delays),
        "columns_with_anchors": len(with_anchors[0]),
        "rank_with_anchors": matrix_rank(with_anchors),
        "columns_without_anchors": len(without[0]),
        "rank_without_anchors": matrix_rank(without),
        "se_plateau_with_free_batch_levels": rounded(math.sqrt(cov[1][1])),
        "se_T_us_with_free_batch_levels": rounded(math.sqrt(cov[0][0])),
    }


# ---------------------------------------------------------------------------------------------------------------------
# Retained inputs of the predictions
# ---------------------------------------------------------------------------------------------------------------------


def retained_inputs(
    analysis: Path = RETAINED_ANALYSIS, shape: Path = RETAINED_SHAPE, runs: Path = RETAINED_RUNS
) -> dict[str, Any]:
    """Per-qubit retained readout means, T1 fits, plateau models, ladder rows and the job-level scatter of anchors."""
    rows = json.loads(analysis.read_text(encoding="utf-8"))["qubits"]
    shapes = {row["qubit"]: row for row in json.loads(shape.read_text(encoding="utf-8"))["qubits"]}
    zero_pool: dict[int, list[float]] = {}
    one_pool: dict[int, list[float]] = {}
    counts: dict[str, int] = {}
    for index in range(6):
        run = runs / f"{RETAINED_RUN_STAMP}{index}"
        acquisition, cases, raw = base.read_run(run)
        del acquisition
        for row in cases["circuits"]:
            kind = base.anchor(row)
            if kind is None:
                continue
            pool = one_pool if kind == 1 else zero_pool
            counts[row["file"]] = len(raw[row["file"]])
            for qubit, value in enumerate(base.p1(raw[row["file"]], cases["nqubits"])):
                pool.setdefault(qubit, []).append(value)
    qubits = []
    scatter = []
    for row in rows:
        qubit = row["qubit"]
        pairs = row["readout"]
        e01 = sum(p["p1_given_0"] for p in pairs) / len(pairs)
        e11 = sum(p["p1_given_1"] for p in pairs) / len(pairs)
        models = shapes[qubit]["models"]
        span = e11 - e01
        observed = shapes[qubit]["observed"]
        qubits.append(
            {
                "qubit": qubit,
                "e01": e01,
                "e11": e11,
                "single_us": models["single"]["params"]["T_us"],
                "single_interval_us": models["single"]["interval_scaled"]["T_us"],
                "plateau_us": models["plateau"]["params"]["T_us"],
                "plateau": models["plateau"]["params"]["plateau"],
                "population": {
                    str(c): (observed[i] - e01) / span for i, c in enumerate((0, 250, 500, 1000, 2000, 4000))
                },
                "ladder_p0": row.get("ladder_p0", {}),
            }
        )
        scatter.append(job_level_variance(zero_pool[qubit], one_pool[qubit], min(counts.values())))
    return {"qubits": qubits, "tau2": sum(scatter) / len(scatter), "anchor_jobs": 3, "count": min(counts.values())}


# ---------------------------------------------------------------------------------------------------------------------
# Budget, predictions and generated files
# ---------------------------------------------------------------------------------------------------------------------


def job_seconds(profile: dict[str, Any], row: dict[str, Any]) -> float:
    wait = row.get("wait_cycles", 0) * CYCLE_SECONDS
    return float(JOB_SECONDS + profile["shots"] * (SHOT_SECONDS + wait))


def batch_counts(profile_name: str) -> dict[str, int]:
    use = usage(profile_name)
    return {
        "interleaved_t1": ROUNDS * len(T1_ROUND_CYCLES),
        "single_qubit": len(SINGLE[profile_name]) * (len(SINGLE_T1_CYCLES) + 1),
        "q12_phase": -(-len(use["q12_phase"]) // BATCH_LIMIT),
    }


def budget(profile_name: str) -> dict[str, Any]:
    profile = PROFILES[profile_name]
    rows = library(profile_name)
    per_arm: dict[str, Any] = {}
    for arm, names in usage(profile_name).items():
        seconds = sum(job_seconds(profile, rows[name]) for name in names)
        per_arm[arm] = {
            "batches": batch_counts(profile_name)[arm],
            "jobs": len(names),
            "shots": len(names) * profile["shots"],
            "expected_execution_seconds": round(seconds, 1),
        }
    total = {
        key: round(sum(per_arm[arm][key] for arm in ARMS), 1)
        if "seconds" in key
        else sum(per_arm[a][key] for a in ARMS)
        for key in ("batches", "jobs", "shots", "expected_execution_seconds")
    }
    return {
        "per_arm": per_arm,
        "total": total,
        "seconds_model": "2.6 s per job plus 0.53 ms per shot plus the circuit's wait per shot",
        "credits_expected": 0,
        "retained_characterization": {"batches": 6, "jobs": 14, "shots": 147456, "expected_execution_seconds": 115.8},
    }


def prediction(profile_name: str, retained: dict[str, Any] | None = None) -> dict[str, Any]:
    out: dict[str, Any] = {
        "schema": "qi-tuna17-interleaved-prediction-v1",
        "profile": profile_name,
        "budget": budget(profile_name),
        "noiseless_outcome": {
            "readout-0": "all 0",
            "t1": "all driven qubits 1",
            "x90": "all 0",
            "ramsey": "driven qubit P1 = (1 + cos angle) / 2, phase offset 0",
        },
        "thresholds": {
            "lack_of_fit_probability": LACK_OF_FIT_PROBABILITY,
            "aicc_gain": AICC_GAIN,
            "pooled_qubits": POOLED_QUBITS,
            "phase_target_rad": PHASE_TARGET,
            "phase_half_width_rad": PHASE_HALF_WIDTH,
            "phase_null_rad": PHASE_NULL,
            "min_fringe_amplitude": MIN_FRINGE_AMPLITUDE,
        },
    }
    if retained is None:
        return out
    tau2 = retained["tau2"]
    count = PROFILES[profile_name]["shots"]
    qubits = retained["qubits"]
    interleaved = []
    for row in qubits:
        errors = expected_errors(row["e01"], row["e11"], row, tau2, count)
        interleaved.append({"qubit": row["qubit"], **errors})
    middle = sorted(qubits, key=lambda r: r["plateau_us"])[len(qubits) // 2]
    out["interleaved_t1"] = {
        "job_level_sigma": rounded(math.sqrt(tau2)),
        "job_level_basis": "excess variance of the retained series' three prepared-0 and three prepared-1 anchor jobs",
        "expected_errors": interleaved,
        "design": design_summary(middle["e01"], middle["e11"], (middle["plateau_us"], middle["plateau"]), tau2, count),
        "design_qubit": middle["qubit"],
    }
    single = {row["qubit"]: row for row in qubits}
    out["single_qubit"] = {
        "qubits": [
            {
                "qubit": q,
                "retained_population": {str(c): rounded(single[q]["population"][str(c)]) for c in SINGLE_T1_CYCLES},
                "retained_t1_us": rounded(single[q]["single_us"]),
                "retained_t1_widened_us": [
                    rounded(v) if v is not None else None for v in single[q]["single_interval_us"]
                ],
                "retained_ladder_p0": {k: rounded(v) for k, v in single[q]["ladder_p0"].items() if k != "0"},
                "predicted_ladder": ladder_prediction(single[q]["ladder_p0"]),
            }
            for q in SINGLE["tuna_17"]
        ],
        "ladder_rule": "fails when the retained corrected P(0) falls to 0.25 or below at any of 32, 128, 256 pulses",
    }
    return out


def ladder_prediction(p0: dict[str, float]) -> str:
    """Predicted single-qubit ladder verdict: a retained P(0) of 0.25 or below needs a coherent rotation, which
    dephasing by neighbors does not make (it drives P(0) toward 0.5), so that qubit is predicted to keep failing."""
    return "fails" if min(p0[k] for k in ("32", "128", "256")) <= 0.25 else "clears"


def batch_directory(arm: str, index: int) -> str:
    return f"{arm}/batch-{index:02d}"


def files(profile_name: str, values: Sequence[int] | None, retained: dict[str, Any] | None = None) -> dict[str, str]:
    """Relative path -> text of every generated file of one profile's case directory."""
    profile = PROFILES[profile_name]
    rows = library(profile_name)
    out: dict[str, str] = {f"circuits/{name}": row["text"] for name, row in rows.items()}
    index: dict[str, Any] = {
        "schema": SCHEMA,
        "profile": profile_name,
        "backend": profile["backend"],
        "shots": profile["shots"],
        "cycle_seconds": CYCLE_SECONDS,
        "t1_round_wait_cycles": list(T1_ROUND_CYCLES),
        "rounds": ROUNDS,
        "single_qubits": list(SINGLE[profile_name]),
        "single_t1_wait_cycles": list(SINGLE_T1_CYCLES),
        "single_ladder_pulses": [4 * t for t in SINGLE_LADDER_TURNS],
        "phase_qubits": list(PHASE[profile_name]),
        "phase_wait_cycles": PHASE_WAIT_CYCLES,
        "phase_steps_pi_over_36": list(PHASE_STEPS),
        "batch_limit": BATCH_LIMIT,
        "batches": batch_counts(profile_name),
        "qrng_draw": DRAW,
        "schedule": "schedule.json" if values is not None else "pending: DRAW is None, see qrng_request.json",
    }
    out["cases.json"] = json.dumps(index, indent=1) + "\n"
    out["prediction.json"] = json.dumps(prediction(profile_name, retained), indent=1) + "\n"
    if values is None:
        out["qrng_request.json"] = json.dumps(qrng_request(), indent=1) + "\n"
        return out
    plan = schedule(profile_name, values)
    out["schedule.json"] = json.dumps({"schema": SCHEMA, "qrng_draw": DRAW, **plan}, indent=1) + "\n"
    for arm in ARMS:
        for number, batch in enumerate(plan["arms"][arm]):
            directory = batch_directory(arm, number)
            circuit_rows = []
            for name in batch["circuits"]:
                row = rows[name]
                out[f"{directory}/{name}"] = row["text"]
                params = {k: v for k, v in row.items() if k != "text"}
                circuit_rows.append(
                    {"file": name, **params, "sha256": hashlib.sha256(row["text"].encode()).hexdigest()}
                )
            manifest = {
                "schema": SCHEMA,
                "arm": arm,
                "meta": {k: v for k, v in batch.items() if k != "circuits"},
                "backend": profile["backend"],
                "backend_type_id": profile["backend_type_id"],
                "nqubits": profile["nqubits"],
                "shots": profile["shots"],
                "bit_order": "qubit 0 at the rightmost character",
                "qrng_draw": DRAW,
                "circuits": circuit_rows,
            }
            out[f"{directory}/cases.json"] = json.dumps(manifest, indent=1) + "\n"
    return out


def write(root: Path, draw_root: Path = ROOT, retained: dict[str, Any] | None = None) -> None:
    values = draw_values(draw_root)
    for profile_name in PROFILES:
        for relative, text in files(profile_name, values, retained if profile_name == "tuna_17" else None).items():
            target = case_directory(root, profile_name) / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")


def check(root: Path, draw_root: Path = ROOT, retained: dict[str, Any] | None = None) -> list[str]:
    """Every difference between the generated files and ROOT, CASE.md excepted."""
    values = draw_values(draw_root)
    problems = []
    for profile_name in PROFILES:
        directory = case_directory(root, profile_name)
        wanted = files(profile_name, values, retained if profile_name == "tuna_17" else None)
        for relative, text in wanted.items():
            target = directory / relative
            if not target.is_file() or target.read_text(encoding="utf-8") != text:
                problems.append(f"{target} differs from the generator")
        held = (
            {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
            if directory.is_dir()
            else set()
        )
        problems += [f"{directory / extra} is not generated" for extra in sorted(held - set(wanted) - {"CASE.md"})]
    return problems


# ---------------------------------------------------------------------------------------------------------------------
# Estimator: anchored populations and three decay models by weighted least squares
# ---------------------------------------------------------------------------------------------------------------------


def levenberg(
    residual: Callable[[list[float]], list[float]], start: list[float], iterations: int = 200
) -> tuple[list[float], float]:
    """Levenberg-Marquardt on the sum of squared residuals with a central-difference Jacobian."""
    theta = list(start)
    r = residual(theta)
    cost = sum(v * v for v in r)
    damping = 1e-3
    size = len(theta)
    for _ in range(iterations):
        jac = []
        for index in range(size):
            step = 1e-6
            up, down = theta[:], theta[:]
            up[index] += step
            down[index] -= step
            jac.append([(a - b) / (2 * step) for a, b in zip(residual(up), residual(down), strict=True)])
        jtj = [[sum(a * b for a, b in zip(jac[i], jac[j], strict=True)) for j in range(size)] for i in range(size)]
        jtr = [sum(a * b for a, b in zip(jac[i], r, strict=True)) for i in range(size)]
        moved = False
        for _ in range(40):
            damped = [
                [jtj[i][j] + (damping * (jtj[i][i] + 1e-12) if i == j else 0.0) for j in range(size)]
                for i in range(size)
            ]
            try:
                inverse = invert(damped)
            except ValueError:
                damping *= 4
                continue
            candidate = [theta[i] - sum(inverse[i][j] * jtr[j] for j in range(size)) for i in range(size)]
            trial = residual(candidate)
            trial_cost = sum(v * v for v in trial)
            if trial_cost < cost:
                done = cost - trial_cost < 1e-12 * (1.0 + cost)
                theta, r, cost, moved = candidate, trial, trial_cost, True
                damping = max(damping / 3, 1e-12)
                if done:
                    return theta, cost
                break
            damping *= 4
        if not moved:
            break
    return theta, cost


def bounded_exp(value: float) -> float:
    """exp clamped to the range of the decay times, so a trial step cannot overflow."""
    return math.exp(max(-20.0, min(20.0, value)))


def sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-max(-60.0, min(60.0, value))))


def natural(shape: str, u: Sequence[float]) -> list[float]:
    """Natural parameters of a model from its unconstrained ones."""
    if shape == "single":
        return [bounded_exp(u[0])]
    if shape == "plateau":
        return [bounded_exp(u[0]), sigmoid(u[1])]
    fast = bounded_exp(u[0])
    return [fast, fast * (1.0 + bounded_exp(u[1])), sigmoid(u[2])]


def starts(shape: str) -> list[list[float]]:
    if shape == "single":
        return [[math.log(t)] for t in (5.0, 20.0, 80.0)]
    if shape == "plateau":
        return [[math.log(t), math.log(c / (1 - c))] for t in (8.0, 20.0, 40.0) for c in (0.003, 0.03, 0.2)]
    return [
        [math.log(f), math.log(r - 1.0), math.log(w / (1 - w))]
        for f in (3.0, 8.0, 20.0)
        for r in (4.0, 20.0)
        for w in (0.05, 0.4)
    ]


def fit_shape(points: list[tuple[float, float, float]], shape: str) -> dict[str, Any]:
    """Weighted least squares of one decay shape over (t_us, population, variance) points; lowest of several starts."""

    def residual(u: list[float]) -> list[float]:
        theta = natural(shape, u)
        return [(x - decay(shape, theta, t)) / math.sqrt(v) for t, x, v in points]

    best: tuple[list[float], float] | None = None
    for start in starts(shape):
        found = levenberg(residual, start)
        if best is None or found[1] < best[1]:
            best = found
    if best is None:
        raise ValueError("no start")
    u, chi_square = best
    k = len(u)
    n = len(points)
    theta = natural(shape, u)
    out: dict[str, Any] = {"chi_square": chi_square, "dof": n - k, "k": k, "params": theta}
    out["probability"] = base.chi_square_probability(chi_square, n - k)
    out["aicc"] = chi_square + 2 * k + (2 * k * (k + 1) / (n - k - 1) if n - k - 1 > 0 else math.inf)
    return out


def classify(fits: dict[str, dict[str, Any]], raw_probability: float, replicate_probability: float) -> str:
    """Per-qubit verdict from the anchored fits, the unanchored single fit and the replicate scatter."""
    single, plateau, two_rate = fits["single"], fits["plateau"], fits["two_rate"]
    if single["probability"] >= LACK_OF_FIT_PROBABILITY:
        if replicate_probability < LACK_OF_FIT_PROBABILITY:
            return "unresolved"
        return "level_shift" if raw_probability < LACK_OF_FIT_PROBABILITY else "single_exponential"
    if replicate_probability < LACK_OF_FIT_PROBABILITY:
        return "unresolved"
    accepted = {
        name: fit
        for name, fit in (("tail_plateau", plateau), ("two_rate", two_rate))
        if fit["probability"] >= LACK_OF_FIT_PROBABILITY and single["aicc"] - fit["aicc"] >= AICC_GAIN
    }
    if "two_rate" in accepted and ("tail_plateau" not in accepted or plateau["aicc"] - two_rate["aicc"] >= AICC_GAIN):
        return "two_rate"
    if "tail_plateau" in accepted:
        return "tail_plateau"
    return "unresolved"


def tail_contribution(fits: dict[str, dict[str, Any]], replicate_probability: float) -> float:
    """AICc gain of the lower-AICc tail fit over the single exponential, zero unless the replicates and that fit hold.

    The tail fit counts only where its own lack-of-fit probability and the replicate probability both reach
    LACK_OF_FIT_PROBABILITY, so a gain bought by a misfit or by scattering rounds adds nothing; a negative gain adds 0.
    """
    tail = min((fits["plateau"], fits["two_rate"]), key=lambda fit: fit["aicc"])
    if replicate_probability < LACK_OF_FIT_PROBABILITY or tail["probability"] < LACK_OF_FIT_PROBABILITY:
        return 0.0
    return max(0.0, fits["single"]["aicc"] - tail["aicc"])


def anchored_point(p: float, a0: float, a1: float, count: int, tau2: float) -> tuple[float, float] | None:
    """Population (p - a0) / (a1 - a0) of one batch and its variance; None when the anchors lie too close."""
    span = a1 - a0
    if span <= MIN_READOUT_SPAN:
        return None
    x = (p - a0) / span
    variance = (
        base.binomial_variance(p, count)
        + tau2
        + (1 - x) ** 2 * (base.binomial_variance(a0, count) + tau2)
        + x**2 * (base.binomial_variance(a1, count) + tau2)
    ) / span**2
    return x, variance


def read_batches(runs: list[Path]) -> list[dict[str, Any]]:
    """Run directories through qi_records: manifest rows, shot count and the P1 of every qubit by circuit file."""
    found = []
    for run in runs:
        try:
            _, cases, raw = base.read_run(run)
        except ValueError as refusal:
            raise SystemExit(f"qi_tuna17_interleaved_cases: {refusal}") from refusal
        if "arm" not in cases:
            raise SystemExit(f"qi_tuna17_interleaved_cases: {run.name} names no arm")
        nqubits = cases["nqubits"]
        found.append(
            {
                "run": run.name,
                "arm": cases["arm"],
                "meta": cases.get("meta", {}),
                "shots": cases["shots"],
                "nqubits": nqubits,
                "rows": {row["file"]: row for row in cases["circuits"]},
                "p1": {name: base.p1(shots, nqubits) for name, shots in raw.items()},
            }
        )
    return found


def analyze_interleaved(batches: list[dict[str, Any]]) -> dict[str, Any]:
    """Per-qubit anchored fits of the interleaved T1 batches, the pooled tail statistic and the level-shift scale.

    The pooled verdict tail_confirmed reads tail_statistic, the sum over usable qubits of tail_contribution, against
    TAIL_STATISTIC_THRESHOLD. The per-qubit labels and their counts are descriptive and decide nothing.
    """
    nqubits = batches[0]["nqubits"]
    qubits = []
    for qubit in range(nqubits):
        a0s = [b["p1"]["readout-0.cq"][qubit] for b in batches]
        a1s = [b["p1"]["t1-0.cq"][qubit] for b in batches]
        count = batches[0]["shots"]
        tau2 = job_level_variance(a0s, a1s, count)
        points: list[tuple[float, float, float]] = []
        raw_points: list[tuple[float, float, float]] = []
        by_delay: dict[int, list[tuple[float, float]]] = {}
        mean0, mean1 = sum(a0s) / len(a0s), sum(a1s) / len(a1s)
        usable = mean1 - mean0 > MIN_READOUT_SPAN
        for batch, a0, a1 in zip(batches, a0s, a1s, strict=True):
            delay = next(f for f, row in batch["rows"].items() if row["kind"] == "t1")
            cycles = batch["rows"][delay]["wait_cycles"]
            p = batch["p1"][delay][qubit]
            point = anchored_point(p, a0, a1, count, tau2)
            if point is None or not usable:
                continue
            t_us = cycles * CYCLE_SECONDS * 1e6
            points.append((t_us, point[0], point[1]))
            by_delay.setdefault(cycles, []).append(point)
            x_raw = (p - mean0) / (mean1 - mean0)
            raw_var = (
                base.binomial_variance(p, count)
                + (1 - x_raw) ** 2 * base.binomial_variance(mean0, count * len(batches))
                + x_raw**2 * base.binomial_variance(mean1, count * len(batches))
            ) / (mean1 - mean0) ** 2
            raw_points.append((t_us, x_raw, raw_var))
        row: dict[str, Any] = {
            "qubit": qubit,
            "job_level_sigma": math.sqrt(tau2),
        }
        if len(points) < 6 or not usable:
            row["verdict"] = "unusable"
            qubits.append(row)
            continue
        fits = {shape: fit_shape(points, shape) for shape in ("single", "plateau", "two_rate")}
        raw_fit = fit_shape(raw_points, "single")
        replicate_chi = 0.0
        replicate_dof = 0
        for group in by_delay.values():
            if len(group) >= 2:
                weights = [1.0 / variance for _, variance in group]
                centre = sum(w * x for w, (x, _) in zip(weights, group, strict=True)) / sum(weights)
                replicate_chi += sum(w * (x - centre) ** 2 for w, (x, _) in zip(weights, group, strict=True))
                replicate_dof += len(group) - 1
        replicate_probability = base.chi_square_probability(replicate_chi, replicate_dof)
        row["fits"] = {
            shape: {k: v for k, v in fit.items() if k != "k"} | {"params": [float(p) for p in fit["params"]]}
            for shape, fit in fits.items()
        }
        row["unanchored_single_probability"] = raw_fit["probability"]
        row["replicate_probability"] = replicate_probability
        row["verdict"] = classify(fits, raw_fit["probability"], replicate_probability)
        row["tail_contribution"] = tail_contribution(fits, replicate_probability)
        qubits.append(row)
    verdicts = [row["verdict"] for row in qubits]
    accepted = sum(v in ("single_exponential", "level_shift") for v in verdicts)
    rejected = sum(v in ("tail_plateau", "two_rate") for v in verdicts)
    tail_statistic = sum(row.get("tail_contribution", 0.0) for row in qubits)
    pooled = {
        "single_exponential_accepted": accepted,
        "single_exponential_rejected": rejected,
        "level_shift_explains_misfit": accepted >= POOLED_QUBITS,
        "tail_statistic": tail_statistic,
        "tail_statistic_threshold": TAIL_STATISTIC_THRESHOLD,
        "tail_confirmed": tail_statistic >= TAIL_STATISTIC_THRESHOLD,
    }
    return {"qubits": qubits, "pooled": pooled}


def analyze_single(batches: list[dict[str, Any]], interleaved: dict[str, Any] | None) -> dict[str, Any]:
    """Per-qubit single-drive populations at SINGLE_T1_CYCLES, the ladder verdict and the arm A comparison."""
    by_qubit: dict[int, list[dict[str, Any]]] = {}
    for batch in batches:
        by_qubit.setdefault(batch["meta"]["qubit"], []).append(batch)
    rows = []
    for qubit, group in sorted(by_qubit.items()):
        a0s, a1s, populations = [], [], {}
        for batch in group:
            if "readout-0.cq" in batch["p1"]:
                a0s.append(batch["p1"]["readout-0.cq"][qubit])
                a1s.append(batch["p1"][f"single-q{qubit}-prep1.cq"][qubit])
        count = group[0]["shots"]
        tau2 = job_level_variance(a0s, a1s, count)
        for batch in group:
            for name, row in batch["rows"].items():
                if row["kind"] != "single_t1" or "readout-0.cq" not in batch["rows"]:
                    continue
                a0, a1 = batch["p1"]["readout-0.cq"][qubit], batch["p1"][f"single-q{qubit}-prep1.cq"][qubit]
                point = anchored_point(batch["p1"][name][qubit], a0, a1, count, tau2)
                if point is not None:
                    populations[row["wait_cycles"]] = point
        mean0, mean1 = sum(a0s) / len(a0s), sum(a1s) / len(a1s)
        ladder = {}
        for batch in group:
            for name, row in batch["rows"].items():
                if row["kind"] == "single_x90" and mean1 - mean0 > MIN_READOUT_SPAN:
                    ladder[row["pulses"]] = 1.0 - (batch["p1"][name][qubit] - mean0) / (mean1 - mean0)
        entry: dict[str, Any] = {
            "qubit": qubit,
            "population": {str(c): v[0] for c, v in sorted(populations.items())},
            "ladder_p0": {str(p): v for p, v in sorted(ladder.items())},
        }
        if len(ladder) == len(SINGLE_LADDER_TURNS):
            entry["ladder_clears"] = all(v >= base.LADDER_MIN_P0 for v in ladder.values())
        if interleaved is not None:
            reference = interleaved["populations"].get(qubit, {})
            diffs = {}
            for cycles, (x, variance) in populations.items():
                if cycles in reference:
                    xa, va = reference[cycles]
                    diffs[str(cycles)] = (x - xa) / math.sqrt(variance + va)
            entry["z_against_interleaved"] = diffs
            entry["t1_differs"] = any(abs(z) > 3 for z in diffs.values())
        rows.append(entry)
    pooled = {
        "ladder_clears": sum(bool(r.get("ladder_clears")) for r in rows),
        "ladder_fails": sum(r.get("ladder_clears") is False for r in rows),
        "t1_differs": sum(bool(r.get("t1_differs")) for r in rows),
    }
    pooled["crosstalk_ladder_supported"] = pooled["ladder_clears"] >= 4
    pooled["own_pulse_ladder_supported"] = pooled["ladder_fails"] >= 6
    pooled["neighbor_t1_supported"] = pooled["t1_differs"] >= 5
    pooled["t1_independent_of_neighbors"] = bool(rows) and len(rows) - pooled["t1_differs"] >= 6
    return {"qubits": rows, "pooled": pooled}


def fringe_fit(points: list[tuple[float, float, int]]) -> dict[str, float] | None:
    """P = c + A cos(angle) + B sin(angle) by weighted least squares over (angle, P1, shots); the phase offset is
    atan2(-B, A) in P = c + a cos(angle + phase)."""
    rows = [([1.0, math.cos(t), math.sin(t)], p, base.binomial_variance(p, n)) for t, p, n in points]
    info = [[sum(g[i] * g[j] / v for g, _, v in rows) for j in range(3)] for i in range(3)]
    rhs = [sum(g[i] * p / v for g, p, v in rows) for i in range(3)]
    try:
        cov = invert(info)
    except ValueError:
        return None
    c, a_cos, b_sin = (sum(cov[i][j] * rhs[j] for j in range(3)) for i in range(3))
    amplitude = math.hypot(a_cos, b_sin)
    if amplitude < 1e-12:
        return None
    gradient = [0.0, b_sin / amplitude**2, -a_cos / amplitude**2]
    variance = sum(gradient[i] * cov[i][j] * gradient[j] for i in range(3) for j in range(3))
    chi_square = sum((p - (c + a_cos * g[1] + b_sin * g[2])) ** 2 / v for g, p, v in rows)
    return {
        "phase": math.atan2(-b_sin, a_cos),
        "phase_se": math.sqrt(variance),
        "amplitude": amplitude,
        "offset": c,
        "chi_square": chi_square,
        "dof": len(points) - 3,
    }


def wrap(angle: float) -> float:
    return (angle + math.pi) % (2 * math.pi) - math.pi


def phase_verdict(fit: dict[str, float]) -> str:
    """Class of one fringe against the refit's q12 term: supports_target, null or other.

    A fringe below MIN_FRINGE_AMPLITUDE reads no_fringe; a cosine fit whose chi-square probability lies below
    LACK_OF_FIT_PROBABILITY reads poor_fit before any phase label, since its phase and standard error describe a
    model the points reject.
    """
    if fit["amplitude"] < MIN_FRINGE_AMPLITUDE:
        return "no_fringe"
    if base.chi_square_probability(fit["chi_square"], int(fit["dof"])) < LACK_OF_FIT_PROBABILITY:
        return "poor_fit"
    if abs(fit["phase"] - PHASE_TARGET) <= PHASE_HALF_WIDTH and fit["phase_se"] <= 0.02:
        return "supports_target"
    if abs(fit["phase"] + PHASE_TARGET) <= PHASE_HALF_WIDTH and fit["phase_se"] <= 0.02:
        return "supports_target_opposite_sign"
    if abs(fit["phase"]) + 2 * fit["phase_se"] <= PHASE_NULL:
        return "null"
    return "other"


def analyze_phase(batches: list[dict[str, Any]]) -> dict[str, Any]:
    scans: dict[tuple[int, int], list[tuple[float, float, int]]] = {}
    for batch in batches:
        for name, row in batch["rows"].items():
            if row["kind"] == "ramsey":
                scans.setdefault((row["qubit"], row["wait_cycles"]), []).append(
                    (row["angle"], batch["p1"][name][row["qubit"]], batch["shots"])
                )
    rows = []
    for (qubit, wait), points in sorted(scans.items()):
        fit = fringe_fit(sorted(points))
        entry: dict[str, Any] = {"qubit": qubit, "wait_cycles": wait, "points": len(points)}
        if fit is not None and len(points) >= 5:
            entry.update(fit)
            entry["verdict"] = phase_verdict(fit)
        else:
            entry["verdict"] = "no_fringe"
        rows.append(entry)
    return {"scans": rows}


def analyze(runs: list[Path], prediction_path: Path | None = None) -> dict[str, Any]:
    """Rows and verdicts of every arm among the run directories."""
    batches = read_batches(runs)
    out: dict[str, Any] = {"schema": ANALYSIS_SCHEMA, "runs": [b["run"] for b in batches]}
    grouped = {arm: [b for b in batches if b["arm"] == arm] for arm in ARMS}
    interleaved = None
    if grouped["interleaved_t1"]:
        out["interleaved_t1"] = analyze_interleaved(grouped["interleaved_t1"])
        interleaved = {"populations": interleaved_populations(grouped["interleaved_t1"])}
    if grouped["single_qubit"]:
        out["single_qubit"] = analyze_single(grouped["single_qubit"], interleaved)
    if grouped["q12_phase"]:
        out["q12_phase"] = analyze_phase(grouped["q12_phase"])
    if prediction_path is not None:
        out["prediction"] = prediction_path.name
    return out


def interleaved_populations(batches: list[dict[str, Any]]) -> dict[int, dict[int, tuple[float, float]]]:
    """Qubit -> delay cycles -> mean anchored population and its variance, over the rounds of arm A."""
    found: dict[int, dict[int, tuple[float, float]]] = {}
    count = batches[0]["shots"]
    for qubit in range(batches[0]["nqubits"]):
        a0s = [b["p1"]["readout-0.cq"][qubit] for b in batches]
        a1s = [b["p1"]["t1-0.cq"][qubit] for b in batches]
        tau2 = job_level_variance(a0s, a1s, count)
        gathered: dict[int, list[tuple[float, float]]] = {}
        for batch, a0, a1 in zip(batches, a0s, a1s, strict=True):
            delay = next(f for f, row in batch["rows"].items() if row["kind"] == "t1")
            point = anchored_point(batch["p1"][delay][qubit], a0, a1, count, tau2)
            if point is not None:
                gathered.setdefault(batch["rows"][delay]["wait_cycles"], []).append(point)
        found[qubit] = {
            cycles: (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts) ** 2)
            for cycles, pts in gathered.items()
        }
    return found


# ---------------------------------------------------------------------------------------------------------------------
# Admission, submission with a status trace, sanity and the local twin
# ---------------------------------------------------------------------------------------------------------------------


class AdmissionRefused(RuntimeError):
    """The backend does not read idle, so no batch is created or submitted."""


def utc_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


def status_label(document: Any, backend_type_id: int) -> tuple[str, Any]:
    """(label, own queue length) of one backend type in a qi_status.account() document or a document that holds it.

    The label is idle only when the backend type and every instance of it read exactly idle; the first other reading
    names the label, and a document of another shape, a missing type, a type without instances or a non-text reading
    gives unreadable. This is the fail-closed reading the admission rule applies.
    """
    account = document.get("account", document) if isinstance(document, dict) else None
    if not isinstance(account, dict) or not isinstance(account.get("backend_types"), list):
        return "unreadable", None
    for row in account["backend_types"]:
        if not isinstance(row, dict) or row.get("id") != backend_type_id:
            continue
        instances = row.get("instances")
        if not isinstance(instances, list) or not instances:
            return "unreadable", None
        readings = [row.get("status"), *[i.get("status") if isinstance(i, dict) else None for i in instances]]
        if any(not isinstance(r, str) for r in readings):
            return "unreadable", None
        other = [r for r in readings if r != "idle"]
        queue = (
            (row.get("queue_own") or {}).get("number_of_jobs_in_queue")
            if isinstance(row.get("queue_own"), dict)
            else None
        )
        label = str(other[0]) if other else "idle"
        return label, queue
    return "unreadable", None


def admission(document: Any, backend_type_id: int) -> list[str]:
    """Reasons the series may not submit now; an empty list admits it."""
    label, queue = status_label(document, backend_type_id)
    reasons = []
    if label != "idle":
        reasons.append(f"the backend reads {label}, not idle")
    if queue != 0:
        reasons.append(f"the account's queue on the backend holds {queue!r}, not 0")
    return reasons


def live_status_reader(qi_python: str) -> Callable[[], dict[str, Any]]:
    """Reader of the account's backend status through qi_status.account under the Quantum Inspire interpreter.

    hypothesis: the call needs the stored login only; it has run against no live service in this change.
    """
    snippet = (
        "import json, sys; sys.path.insert(0, 'scripts'); import qi_platform, qi_status; "
        "print(json.dumps(qi_status.account(qi_platform.Client())))"
    )

    def read() -> dict[str, Any]:
        command = [qi_python, "-c", snippet]
        done = subprocess.run(command, capture_output=True, text=True, check=True, timeout=120)  # noqa: S603
        document = json.loads(done.stdout)
        if not isinstance(document, dict):
            raise ValueError("status reader returned a non-object")
        return document

    return read


def trace_row(
    read_status: Callable[[], dict[str, Any]], backend_type_id: int, clock: Callable[[], Any]
) -> dict[str, Any]:
    try:
        label, queue = status_label(read_status(), backend_type_id)
    except Exception as error:  # noqa: BLE001 - a failed read is a row of the trace, not a stop
        label, queue = "unreadable", None
        return {"utc": clock().isoformat(), "status": label, "queue_own": queue, "error": type(error).__name__}
    return {"utc": clock().isoformat(), "status": label, "queue_own": queue}


def execution_start_statuses(run: Path) -> list[dict[str, Any]]:
    """Per job of a collected run: the last status the trace read at or before the job's start, and the gap to it.

    The start is the job's queued_at of results.json, which the retained notes read as the execution start. A start with
    no earlier read, or more than MAX_TRACE_GAP_SECONDS after the last one, reads unobserved.
    """
    trace = json.loads((run / "status-trace.json").read_text(encoding="utf-8"))["rows"]
    stamps = [(datetime.datetime.fromisoformat(r["utc"]), r["status"]) for r in trace]
    out = []
    for entry in json.loads((run / "results.json").read_text(encoding="utf-8"))["jobs"]:
        start = datetime.datetime.fromisoformat(entry["job"]["queued_at"])
        before = [(t, s) for t, s in stamps if t <= start]
        if not before:
            out.append(
                {
                    "file": entry["file"],
                    "started_utc": entry["job"]["queued_at"],
                    "status": "unobserved",
                    "gap_seconds": None,
                }
            )
            continue
        when, status = before[-1]
        gap = (start - when).total_seconds()
        out.append(
            {
                "file": entry["file"],
                "started_utc": entry["job"]["queued_at"],
                "status": status if gap <= MAX_TRACE_GAP_SECONDS else "unobserved",
                "gap_seconds": gap,
            }
        )
    return out


def sanity(run: Path) -> list[str]:
    """Jobs complete with all shots, anchor circuits read their fixed outcome on all but SANITY_WRONG_QUBITS qubits,
    the run holds its admission record and status trace, and no job started while the backend read outside
    START_STATUSES."""
    try:
        acquisition, cases, raw = base.read_run(run)
    except ValueError as error:
        return [str(error)]
    problems = []
    for job in acquisition.jobs:
        if job.status != "completed":
            problems.append(f"{job.file}: job {job.status}")
        elif job.shots_done != cases["shots"]:
            problems.append(f"{job.file}: {job.shots_done} shots done of {cases['shots']}")
    if problems:
        return problems
    for row in cases["circuits"]:
        if row["kind"] not in ("anchor0", "anchor1", "single_prep1"):
            continue
        driven = set(row["driven"])
        wrong = [
            q for q, value in enumerate(base.p1(raw[row["file"]], cases["nqubits"])) if (value > 0.5) != (q in driven)
        ]
        if len(wrong) > SANITY_WRONG_QUBITS:
            problems.append(f"{row['file']}: qubits {wrong} read the wrong side of 0.5")
    receipt = json.loads((run / "submission.json").read_text(encoding="utf-8"))
    if receipt.get("backend_status_at_submit") != "idle":
        problems.append(
            f"{run.name}: submission.json records backend status {receipt.get('backend_status_at_submit')!r} at submit"
        )
    for name in ("admission.json", "status-trace.json"):
        if not (run / name).is_file():
            problems.append(
                f"{run.name}: {name} is missing, so the backend status at submission and start is unrecorded"
            )
    if problems:
        return problems
    for start in execution_start_statuses(run):
        if start["status"] not in START_STATUSES:
            problems.append(f"{start['file']}: execution began while the backend status read {start['status']}")
    return problems


def write_trace(run: Path, rows: list[dict[str, Any]]) -> None:
    """Replace status-trace.json atomically, so a stop between two reads leaves every read so far on disk."""
    document = {"schema": "qi-status-trace-v1", "poll_seconds": TRACE_POLL_SECONDS, "rows": rows}
    temporary = run / "status-trace.json.part"
    temporary.write_text(json.dumps(document, indent=1) + "\n", encoding="utf-8")
    temporary.replace(run / "status-trace.json")


def series_guards(series: Path, runs: Path, stamp: str) -> None:
    """Refuse a second submission of one arm under another stamp and a run directory that differs from its batch."""
    prefix = f"{series.parent.name}-{series.name}-batch-"
    for other in sorted(runs.glob(f"*-{prefix}*")) if runs.is_dir() else []:
        held = other.name.split(f"-{prefix}")[0]
        if held != stamp:
            raise RuntimeError(f"{other} holds this arm under stamp {held}; resume with that stamp")
    for batch_dir in sorted(series.glob("batch-*")):
        run = runs / f"{stamp}-{prefix}{batch_dir.name[len('batch-') :]}"
        if not run.is_dir():
            continue
        for source in sorted(batch_dir.iterdir()):
            copy = run / source.name
            if not copy.is_file() or copy.read_bytes() != source.read_bytes():
                raise RuntimeError(f"{copy} differs from {source}: the arm changed after this copy; use a new stamp")


def submit_series(
    series: Path,
    runs: Path,
    stamp: str,
    approval: str,
    backend_type_id: int,
    *,
    command: Sequence[str],
    read_status: Callable[[], dict[str, Any]],
    run_command: Callable[[list[str]], tuple[int, str]],
    launch: Callable[[list[str]], Any],
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], Any] = utc_now,
    collect_timeout: int = 3600,
    max_refusals: int = 10,
) -> list[str]:
    """Submit and collect the batches of one arm directory in order, one at a time.

    A batch that has no submission receipt is submitted only after read_status() reads idle with an empty queue,
    and that read is repeated before every attempt, including the retries that follow a pause refusal
    (AdmissionRefused otherwise, before any remote write). The submit command is
    command + [submit, RUN, --backend-type-id N, --approval TEXT]; a refusal that names "wait N more seconds" is
    retried after that many seconds, at most max_refusals times. While the collection runs, the status is read every
    TRACE_POLL_SECONDS and appended to status-trace.json after each read; a resumed collection keeps the earlier
    rows. The run directory is STAMP-CASE-ARM-batch-NN. The returned list is the first failed sanity check, or empty.
    """
    series_guards(series, runs, stamp)
    for batch_dir in sorted(series.glob("batch-*")):
        run = runs / f"{stamp}-{series.parent.name}-{series.name}-{batch_dir.name}"
        if (run / "results.json").is_file():
            problems = sanity(run)
            if problems:
                return problems
            continue
        if (run / "submission-state.json").is_file() and not (run / "submission.json").is_file():
            raise RuntimeError(f"{run} holds a submit checkpoint and no receipt; reconcile it before a repeat")
        if not (run / "submission.json").is_file():
            submit = [*command, "submit", str(run), "--backend-type-id", str(backend_type_id), "--approval", approval]
            refused = 0
            while True:
                document = read_status()
                reasons = admission(document, backend_type_id)
                if reasons:
                    raise AdmissionRefused(f"{batch_dir.name}: " + "; ".join(reasons))
                if not run.exists():
                    shutil.copytree(batch_dir, run)
                label, queue = status_label(document, backend_type_id)
                admitted = {
                    "schema": "qi-admission-v1",
                    "utc": clock().isoformat(),
                    "backend_type_id": backend_type_id,
                    "status": label,
                    "queue_own": queue,
                    "attempt": refused + 1,
                }
                (run / "admission.json").write_text(json.dumps(admitted, indent=1) + "\n", encoding="utf-8")
                code, out = run_command(submit)
                if code == 0:
                    break
                words = out.split()
                left = next(
                    (int(w) for w, nxt in zip(words, words[1:], strict=False) if w.isdigit() and nxt == "more"), None
                )
                refused += 1
                if left is None or refused >= max_refusals:
                    raise RuntimeError(f"{batch_dir.name}: submit stopped after {refused} refusal(s): {out[:200]}")
                sleep(left + 1)
        process = launch([*command, "collect", str(run), "--poll", "15", "--timeout", str(collect_timeout)])
        held = run / "status-trace.json"
        rows: list[dict[str, Any]] = json.loads(held.read_text(encoding="utf-8"))["rows"] if held.is_file() else []
        rows.append(trace_row(read_status, backend_type_id, clock))
        write_trace(run, rows)
        while process.poll() is None:
            sleep(TRACE_POLL_SECONDS)
            rows.append(trace_row(read_status, backend_type_id, clock))
            write_trace(run, rows)
        rows.append(trace_row(read_status, backend_type_id, clock))
        write_trace(run, rows)
        if process.returncode != 0:
            raise RuntimeError(f"{batch_dir.name}: collect exited {process.returncode}")
        problems = sanity(run)
        if problems:
            return problems
    return []


LOCAL_ITERATIONS = 2048
LOCAL_SIGMAS = 5.0


def local(execute: Callable[[str, int], dict[str, int] | None] | None = None) -> list[str]:
    """Run every circuit of the qx profile and compare with its noiseless law: one iteration decides a deterministic
    circuit, and a Ramsey circuit's count of ones on its qubit lies within LOCAL_SIGMAS binomial deviations."""
    if execute is None:
        import qxelarator  # noqa: PLC0415 - present in the Quantum Inspire environment only

        def execute(text: str, iterations: int) -> dict[str, int] | None:
            return getattr(qxelarator.execute_string(text, iterations=iterations), "results", None)

    nqubits = PROFILES["qx"]["nqubits"]
    problems = []
    for name, row in library("qx").items():
        deterministic = row["expected_p1"] in (0.0, 1.0)
        iterations = 1 if deterministic else LOCAL_ITERATIONS
        counts = execute(row["text"], iterations)
        if not isinstance(counts, dict) or sum(counts.values()) != iterations:
            problems.append(f"qx {name}: no counts of {iterations} shots")
            continue
        driven = set(row["driven"])
        for qubit in range(nqubits):
            ones = sum(c for shot, c in counts.items() if shot[len(shot) - 1 - qubit] == "1")
            want = row["expected_p1"] if qubit in driven else 0.0
            sigma = math.sqrt(iterations * want * (1 - want))
            if abs(ones - want * iterations) > (0.0 if deterministic or qubit not in driven else LOCAL_SIGMAS * sigma):
                problems.append(
                    f"qx {name}: qubit {qubit} read {ones} ones of {iterations}, want {want * iterations:.1f}"
                )
    return problems


# ---------------------------------------------------------------------------------------------------------------------
# Synthetic series and the self-test
# ---------------------------------------------------------------------------------------------------------------------


def synthetic_values(count: int) -> list[int]:
    """A deterministic uint16 stream for tests of the order; it stands for no QRNG draw."""
    return [int.from_bytes(hashlib.sha256(f"order-fixture-{i}".encode()).digest()[:2], "big") for i in range(count)]


def synthetic_interleaved(
    qubit_models: list[dict[str, Any]], shifts: Sequence[float] | None = None, count: int = 8192
) -> list[dict[str, Any]]:
    """Arm A batches whose P1 follow each qubit's model exactly (quantized to the shot count), in the order that
    schedule() gives synthetic_values; shifts[b] is added to every circuit of batch b."""
    plan = schedule("tuna_17", synthetic_values(2000))["arms"]["interleaved_t1"]
    out = []
    for number, batch in enumerate(plan):
        shift = shifts[number] if shifts is not None else 0.0
        rows = {}
        p1: dict[str, list[float]] = {}
        for name in batch["circuits"]:
            kind = "anchor0" if name == "readout-0.cq" else "anchor1" if name == "t1-0.cq" else "t1"
            cycles = int(name[3:-3]) if name.startswith("t1-") else 0
            rows[name] = {"kind": kind, "wait_cycles": cycles}
            values = []
            for model in qubit_models:
                span = model["e11"] - model["e01"]
                x = {"anchor0": None, "anchor1": 1.0}.get(
                    kind, decay(model["shape"], model["theta"], cycles * CYCLE_SECONDS * 1e6)
                )
                p = model["e01"] if x is None else model["e01"] + span * x
                values.append(round((p + shift) * count) / count)
            p1[name] = values
        out.append(
            {
                "run": f"batch-{number:02d}",
                "arm": "interleaved_t1",
                "meta": {},
                "shots": count,
                "nqubits": len(qubit_models),
                "rows": rows,
                "p1": p1,
            }
        )
    return out


def synthetic_status(label: str, queue: int = 0, instance: str | None = None) -> dict[str, Any]:
    """An account-section document of backend type 7 with the given readings."""
    return {
        "backend_types": [
            {
                "id": 7,
                "status": label,
                "queue_own": {"number_of_jobs_in_queue": queue},
                "instances": [{"status": instance or label}],
            }
        ]
    }


class FakeProcess:
    def __init__(self, polls_before_exit: int = 0) -> None:
        self.remaining = polls_before_exit
        self.returncode = 0

    def poll(self) -> int | None:
        if self.remaining > 0:
            self.remaining -= 1
            return None
        return 0


def self_test() -> list[str]:
    """Design, order, admission, estimator and phase-fit invariants; each failed one is a line of the result."""
    import tempfile  # noqa: PLC0415 - self-test only

    problems: list[str] = []

    def expect(condition: bool, message: str) -> None:
        if not condition:
            problems.append(message)

    # Circuits: the retained delays reuse the retained generator's bytes, every text measures once, angles sit on the
    # grid.
    retained = base.circuits(17)
    rows = library("tuna_17")
    expect(rows["readout-0.cq"]["text"] == retained["readout-0.cq"][0], "readout-0 differs from the retained circuit")
    for cycles in base.T1_CYCLES:
        expect(
            rows[f"t1-{cycles}.cq"]["text"] == retained[f"t1-{cycles}.cq"][0],
            f"t1-{cycles} differs from the retained circuit",
        )
    expect(
        all(r["text"].count("measure") == 1 and "qubit[17] q" in r["text"] for r in rows.values()),
        "a circuit measures twice",
    )
    grid = [r["angle"] / (math.pi / 36) for r in rows.values() if r["kind"] == "ramsey"]
    expect(all(abs(g - round(g)) < 1e-9 for g in grid), "a Ramsey angle leaves the pi/36 grid")
    expect(
        all(q < PROFILES["qx"]["nqubits"] for q in (*SINGLE["qx"], *PHASE["qx"])), "a qx arm qubit exceeds the emulator"
    )
    # Order: one draw, deterministic, within the batch limit, each round a full delay set, anchors in every batch.
    values = synthetic_values(2000)
    for profile_name in PROFILES:
        plan = schedule(profile_name, values)
        again = schedule(profile_name, values)
        expect(plan == again, "the order is not a function of the draw")
        expect(plan != schedule(profile_name, synthetic_values(2001)[1:]), "a different draw gave the same order")
        used = usage(profile_name)
        for arm in ARMS:
            batches = plan["arms"][arm]
            expect(all(len(b["circuits"]) <= BATCH_LIMIT for b in batches), f"{arm}: a batch exceeds the circuit limit")
            expect(
                sorted(n for b in batches for n in b["circuits"]) == sorted(used[arm]),
                f"{arm}: scheduled circuits differ from the usage",
            )
            expect(len(batches) == batch_counts(profile_name)[arm], f"{arm}: batch count differs from batch_counts")
        interleaved = plan["arms"]["interleaved_t1"]
        for round_index in range(ROUNDS):
            members = [b for b in interleaved if b["round"] == round_index]
            expect(
                sorted(b["wait_cycles"] for b in members) == sorted(T1_ROUND_CYCLES),
                f"round {round_index} lacks a delay",
            )
        expect(
            all({"readout-0.cq", "t1-0.cq"} <= set(b["circuits"]) for b in interleaved), "a T1 batch lacks an anchor"
        )
        expect(plan["consumed"]["q12_phase"][1] < len(values), "the order consumed more values than the draw holds")
    expect(Stream([65535, 3]).below(3) == 0, "Stream.below keeps a value that biases the modulus")
    expect(qrng_values_needed("tuna_17") <= DRAW_LENGTH, "the request asks for fewer values than the order needs")
    # Admission: only an idle type with idle instances and an empty queue admits; everything else refuses.
    expect(admission(synthetic_status("idle"), 7) == [], "an idle backend was refused")
    for label in ("calibrating", "executing", "offline"):
        expect(bool(admission(synthetic_status(label), 7)), f"a {label} backend was admitted")
    expect(bool(admission(synthetic_status("idle", instance="calibrating"), 7)), "a calibrating instance was admitted")
    expect(bool(admission(synthetic_status("idle", queue=1), 7)), "a queued account was admitted")
    broken_documents: tuple[Any, ...] = (
        {"error": "x"},
        {},
        [],
        None,
        {"backend_types": []},
        {"backend_types": [{"id": 7, "status": "idle"}]},
    )
    for broken in broken_documents:
        expect(bool(admission(broken, 7)), f"an unreadable document {broken!r} was admitted")
    expect(bool(admission(synthetic_status("idle"), 8)), "an absent backend type was admitted")
    with tempfile.TemporaryDirectory() as scratch:
        series, runs = Path(scratch) / "case" / "arm", Path(scratch) / "runs"
        (series / "batch-00").mkdir(parents=True)
        (series / "batch-00" / "cases.json").write_text("{}", encoding="utf-8")
        calls: list[list[str]] = []

        def fake_run(argv: list[str]) -> tuple[int, str]:
            calls.append(argv)
            return 0, ""

        refused = False
        try:
            submit_series(
                series,
                runs,
                "S",
                "approval",
                7,
                command=["py", "platform"],
                read_status=lambda: synthetic_status("calibrating"),
                run_command=fake_run,
                launch=lambda argv: FakeProcess(),
                sleep=lambda s: None,
            )
        except AdmissionRefused:
            refused = True
        expect(
            refused and not calls and not runs.exists(),
            "a calibrating backend reached the submit command or wrote a run",
        )
        result = submit_series(
            series,
            runs,
            "S",
            "approval",
            7,
            command=["py", "platform"],
            read_status=lambda: synthetic_status("idle"),
            run_command=fake_run,
            launch=lambda argv: FakeProcess(2),
            sleep=lambda s: None,
        )
        run = runs / "S-case-arm-batch-00"
        expect(
            len(calls) == 1 and calls[0][2] == "submit" and calls[0][3] == str(run),
            "an idle backend did not submit once",
        )
        expect(
            (run / "admission.json").is_file() and (run / "status-trace.json").is_file(),
            "admission or trace record missing",
        )
        expect(
            len(json.loads((run / "status-trace.json").read_text(encoding="utf-8"))["rows"]) == 4,
            "the trace lacks its reads",
        )
        expect(bool(result), "a run with no collected results passed sanity")
        # An execution start is covered only by a read at most MAX_TRACE_GAP_SECONDS before it.
        (run / "status-trace.json").write_text(
            json.dumps(
                {
                    "rows": [
                        {"utc": "2026-01-01T00:00:00+00:00", "status": "calibrating"},
                        {"utc": "2026-01-01T00:01:00+00:00", "status": "idle"},
                    ]
                }
            ),
            encoding="utf-8",
        )
        results = {
            "jobs": [
                {"file": f, "job": {"queued_at": t}}
                for f, t in (
                    ("a", "2026-01-01T00:01:10Z"),
                    ("b", "2026-01-01T00:00:30Z"),
                    ("c", "2026-01-01T00:03:00Z"),
                )
            ]
        }
        (run / "results.json").write_text(json.dumps(results), encoding="utf-8")
        found = {r["file"]: r["status"] for r in execution_start_statuses(run)}
        expect(found == {"a": "idle", "b": "calibrating", "c": "unobserved"}, f"execution-start statuses {found}")
    # Design: anchors make the batch levels estimable; without them the delay rows cannot separate level from plateau.
    summary = design_summary(0.027, 0.959, (21.5, 0.02), 0.0045**2, 8192)
    expect(summary["rank_with_anchors"] == summary["columns_with_anchors"], f"anchored design rank {summary}")
    expect(summary["rank_without_anchors"] < summary["columns_without_anchors"], f"unanchored design rank {summary}")
    expect(0 < summary["se_plateau_with_free_batch_levels"] < 0.01, f"plateau error with free levels {summary}")
    # Estimator: exact models recover their class, and a level shift common to a batch is cancelled by its anchors.
    models = [
        {"shape": "single", "theta": [22.0], "e01": 0.03, "e11": 0.96},
        {"shape": "plateau", "theta": [20.0, 0.03], "e01": 0.03, "e11": 0.96},
        {"shape": "two_rate", "theta": [4.0, 60.0, 0.4], "e01": 0.03, "e11": 0.96},
    ]
    shifts = [0.012 * math.sin(b) for b in range(ROUNDS * len(T1_ROUND_CYCLES))]
    classes = [row["verdict"] for row in analyze_interleaved(synthetic_interleaved(models[:1], shifts))["qubits"]]
    expect(classes == ["level_shift"], f"a single exponential under batch shifts read {classes}")
    classes = [row["verdict"] for row in analyze_interleaved(synthetic_interleaved(models[:1]))["qubits"]]
    expect(classes == ["single_exponential"], f"a single exponential read {classes}")
    classes = [row["verdict"] for row in analyze_interleaved(synthetic_interleaved(models[1:2], shifts))["qubits"]]
    expect(classes == ["tail_plateau"], f"a plateau under batch shifts read {classes}")
    classes = [row["verdict"] for row in analyze_interleaved(synthetic_interleaved(models[2:3]))["qubits"]]
    expect(classes == ["two_rate"], f"a two-rate decay read {classes}")
    # Phase: a fringe with a z rotation of PHASE_TARGET recovers it; no amplitude gives no phase.
    angles = [s * math.pi / 36 for s in PHASE_STEPS]
    points = [(a, round((0.03 + 0.46 * (1 + math.cos(a + PHASE_TARGET)) / 1.0) * 8192) / 8192, 8192) for a in angles]
    fit = fringe_fit(points)
    expect(
        fit is not None and abs(fit["phase"] - PHASE_TARGET) < 0.005 and phase_verdict(fit) == "supports_target",
        f"phase fit {fit}",
    )
    flat = fringe_fit([(a, 0.5, 8192) for a in angles])
    expect(flat is None or phase_verdict(flat) == "no_fringe", "a flat fringe carried a phase")
    return problems


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", type=Path, metavar="ROOT")
    group.add_argument("--check", type=Path, metavar="ROOT")
    group.add_argument("--request", action="store_true")
    group.add_argument("--local", action="store_true")
    group.add_argument("--sanity", type=Path, metavar="RUN_DIR")
    group.add_argument("--analyze", nargs="+", type=Path, metavar="PATH", help="OUT followed by the run directories")
    group.add_argument("--submit", nargs=4, metavar=("ARM_DIR", "RUNS_DIR", "STAMP", "APPROVAL"))
    group.add_argument("--self-test", action="store_true")
    parser.add_argument("--prediction", type=Path, help="prediction.json the analysis is read against")
    parser.add_argument("--backend-type-id", type=int, help="backend type of --submit")
    args = parser.parse_args(argv)
    problems: list[str] = []
    if args.request:
        print(json.dumps(qrng_request(), indent=1))
        return 0
    if args.write:
        write(args.write, retained=retained_inputs())
        return 0
    if args.analyze:
        if len(args.analyze) < 2:
            parser.error("--analyze takes OUT and at least one RUN_DIR")
        found = analyze(args.analyze[1:], args.prediction)
        args.analyze[0].write_text(json.dumps(found, indent=1, allow_nan=False) + "\n", encoding="utf-8")
        return 0
    if args.submit:
        qi_python = os.environ.get("QI_PYTHON", "")
        if not qi_python or args.backend_type_id is None:
            parser.error("--submit needs QI_PYTHON in the environment and --backend-type-id")
        arm_dir, runs_dir, stamp, approval = args.submit

        def run_command(argv: list[str]) -> tuple[int, str]:
            done = subprocess.run(argv, capture_output=True, text=True, check=False)  # noqa: S603
            return done.returncode, done.stdout + done.stderr

        try:
            problems = submit_series(
                Path(arm_dir),
                Path(runs_dir),
                stamp,
                approval,
                args.backend_type_id,
                command=[qi_python, str(ROOT / "scripts/qi_platform.py")],
                read_status=live_status_reader(qi_python),
                run_command=run_command,
                launch=lambda argv: subprocess.Popen(argv),  # noqa: S603
            )
        except AdmissionRefused as refusal:
            print(f"qi_tuna17_interleaved_cases: admission refused: {refusal}", file=sys.stderr)
            return 1
    elif args.check:
        problems = check(args.check, retained=retained_inputs())
        if DRAW is None and not problems:
            print(
                "qi_tuna17_interleaved_cases: skip: DRAW is None, so the batch directories and schedule.json wait for "
                "QRNG draw that qrng_request.json names",
                file=sys.stderr,
            )
    elif args.local:
        try:
            problems = local()
        except ModuleNotFoundError:
            print(
                "qi_tuna17_interleaved_cases: not run: qxelarator is absent (Quantum Inspire environment)",
                file=sys.stderr,
            )
            return 3
    elif args.sanity:
        problems = sanity(args.sanity)
    else:
        problems = self_test()
    for problem in problems:
        print(f"qi_tuna17_interleaved_cases: {problem}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
