"""Tuna-17 follow-up case: interleaved T1 rounds, a drive-context crosstalk arm and a q12 Ramsey phase scan.

The case has a QX twin.

The retained characterization series (scripts/qi_tuna17_characterization_cases.py) found a non-exponential
T1 on 15 of 17 qubits, a positive step on the batch that held the three longest delays, and ladder verdicts that
opposed the prediction on eight qubits while all 17 qubits were driven together. This case adds three arms, each its
own series directory:

- interleaved_t1: ROUNDS rounds of the multipliers T1_MULTIPLIERS (0.5 to 12 times each qubit's retained plateau
  T; qubit i waits d(i, m) cycles). The provider holds a hardware batch to three circuits, so a round is six provider
  batches of the prepared-0 anchor, the prepared-1 anchor and one delay circuit, and all three give every qubit a wait
  chain of the batch's longest delay D(m) (delay_text, anchor_text), so the anchors carry the delay circuit's timing.
  The six batches of a round follow a seeded permutation shifted by two per round with seeded swaps inside each pair,
  and the three circuits of a batch rotate through the three slots across rounds. A level shift common to the three
  jobs of a batch cancels in the population (p - a0) / (a1 - a0), and the replicates of a multiplier in the other
  rounds separate a tail from a job-level scatter.
- crosstalk: the drive-context arm of 24 jobs in eight provider batches. The coupler graph splits into classes A =
  CLASS_A and B' = CLASS_B (class B without qubit 2). Six conditions (T1 at 5, 20 and 80 us, the X90 ladder at 32, 128
  and 256 pulses) each run one batch of {A driven, B' driven, all qubits driven}; one batch of context anchors holds
  {readout-0, A prepared in 1, B' prepared in 1}; one batch holds {q1 alone, q2 alone, all qubits} at the 128-pulse
  ladder, the direct test of the q1/q2 pair. A qubit and condition is flagged when its half-drive reading differs from
  its same-batch all-drive reading by more than FLAG_Z standard errors of the difference.
- q12_phase: a Ramsey circuit X90, Rz(angle), X90 on the target qubit of PHASE, six angles k pi/3 in two triads that sum
  to zero in sine and cosine, at two waits, four provider batches of one triad each (waits interleaved 0, 25, 0, 25);
  the fringe offset is the static z rotation between two pulses.

Order. Every order comes from one retained QRNG draw (DRAW), consumed in index order, each value once, by a rejection
shuffle; schedule() states the indices each component takes. While DRAW is None the batch directories, their circuits
and schedule.json do not exist: only the indexes and prediction.json are generated and qrng_request.json records the
draw to take and stays beside the batches once the draw is set.

Profiles: tuna_17 (17 qubits, 8,192 shots per circuit) and qx (the same texts on 10 qubits at 1,024 shots, with the
qubit map of CLASS_A, CLASS_B, PAIR and PHASE). Bit order: qubit 0 is the rightmost character of a shot.

    --write ROOT        write ROOT/characterization_interleaved_{tuna_17,qx}/
    --check ROOT        regenerate and compare every file except CASE.md; prints a skip while DRAW is None
    --request           print the QRNG draw this case waits for
    --local             run the qx profile on the local qxelarator emulator against its noiseless expectation
    --sanity RUN_DIR    after a collection: shots, fixed outcomes, admission and execution-start status
    --analyze OUT RUN_DIR...   per-arm rows and verdicts
    --submit ARM_DIR RUNS_DIR STAMP APPROVAL   submit one series, refusing unless the backend reads idle
    --self-test         design, order, circuit-timing, admission-record, estimator and phase-fit invariants

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
import re
import shutil
import subprocess
import sys
import time
from collections.abc import Callable, Sequence
from pathlib import Path
from statistics import NormalDist
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import qi_tuna17_characterization_cases as base  # noqa: E402

from parallel import ordered_map  # noqa: E402

SCHEMA = "qi-tuna17-interleaved-cases-v1"
ANALYSIS_SCHEMA = "qi-tuna17-interleaved-analysis-v1"
ARMS = ("interleaved_t1", "crosstalk", "q12_phase")
CYCLE_SECONDS = base.CYCLE_SECONDS
BATCH_LIMIT = base.BATCH_LIMIT
# Retained plateau-model decay time T of each qubit in microseconds (characterization_tuna_17_t1_shape_analysis.json,
# models.plateau.params.T_us, six decimals). The delay of qubit i at multiplier m is m * T_i in 20 ns cycles, rounded
# half up; the qx profile uses the first nqubits entries.
PLATEAU_T_US = (
    16.63358,
    19.246782,
    21.269981,
    12.50276,
    22.502119,
    19.957294,
    15.690211,
    26.566297,
    18.974547,
    20.472496,
    29.037806,
    22.206257,
    21.528245,
    23.371224,
    11.090605,
    18.015502,
    21.580612,
)
CYCLES_PER_US = 50
# Multipliers of each qubit's plateau T, 0.5 T to 12 T; the longest delay (q10 at 12 T) is 17,423 cycles.
T1_MULTIPLIERS = (0.5, 1, 2, 4, 8, 12)
ROUNDS = 3
# Coupler-graph classes of the crosstalk arm by profile: class A and class B without qubit 2 (B'). The qx entries stand
# in position for the tuna_17 qubits that the 10-qubit emulator lacks and keep qubits 1 and 2 of the pair.
CLASS_A = {"tuna_17": (0, 4, 5, 6, 10, 11, 12, 16), "qx": (0, 4, 5, 6, 9)}
CLASS_B = {"tuna_17": (1, 3, 7, 8, 9, 13, 14, 15), "qx": (1, 3, 7, 8)}
CROSSTALK_T1_CYCLES = (250, 1000, 4000)
CROSSTALK_LADDER_PULSES = (32, 128, 256)
PAIR = (1, 2)
PAIR_PULSES = 128
# A flag marks |z| above this: the two-sided normal quantile of a Bonferroni level of 0.05 over 102 contrasts. The arm
# forms 96 class contrasts and 2 pair contrasts, so the bound is conservative.
FLAG_Z = 3.49
# Job-level standard deviation of a population in the retained anchors, pooled over 17 qubits (descriptive reading of
# the flag, and the floor of a per-qubit flag sigma: a qubit whose anchors show no excess scatter in 18 pairs still
# carries a job-level term, and a zero estimate would make its flag anti-conservative).
RETAINED_JOB_LEVEL_SIGMA = 0.0034
FLAG_SIGMA_FLOOR = RETAINED_JOB_LEVEL_SIGMA
# Largest per-qubit job-level standard deviation of the retained anchors (qubit 6, 0.01021 from three prepared-0 and
# three prepared-1 jobs): the flag sigma of every qubit when the analysis holds no interleaved arm. With the interleaved
# arm the flag sigma of a qubit is max(sqrt(job_level_variance) of its 18 anchor pairs, FLAG_SIGMA_FLOOR).
FLAG_SIGMA_ALONE = 0.0102
FAMILY_CONTRASTS = 98
VERDICT_WORDS = "drive-and-readout context dependence"
PHASE = {"tuna_17": (12,), "qx": (9,)}
PHASE_WAITS = (0, 25)
# Angles k pi / 3 on the processor's pi/36 grid (steps of 12) in two triads: the sines and cosines of each triad sum to
# zero, so a level shared by the three jobs of a batch is orthogonal to both quadratures of the fringe.
PHASE_STEPS = (0, 12, 24, 36, 48, 60)
PHASE_TRIADS = ((0, 24, 48), (12, 36, 60))
PROFILES: dict[str, dict[str, Any]] = {
    "tuna_17": {
        "backend": "tuna_17",
        "backend_type_id": 7,
        "nqubits": 17,
        "shots": 8192,
        "arm_shots": {"interleaved_t1": 8192, "crosstalk": 8192, "q12_phase": 4096},
    },
    "qx": {
        "backend": "QXsinglenodesimulator",
        "backend_type_id": 1,
        "nqubits": 10,
        "shots": 1024,
        "arm_shots": {"interleaved_t1": 1024, "crosstalk": 1024, "q12_phase": 1024},
    },
}
# The retained QRNG draw of this case: None until the draw named by qrng_request() is retained, then its canonical path.
DRAW: str | None = "docs/evidence/anu_qrng/draw-2026-11-19T164737Z.json"
DRAW_LENGTH = 256
# Decision thresholds. The probability bound is the retained characterization's; the AICc gain is the usual 4.
LACK_OF_FIT_PROBABILITY = 0.01
AICC_GAIN = 4.0
MIN_READOUT_SPAN = base.MIN_READOUT_SPAN
# Per-qubit label counts are descriptive. The pooled tail verdict reads the AICc gain summed over qubits against this
# threshold, which lies far above the null spread of the sum and below its value on a retained-size tail.
TAIL_STATISTIC_THRESHOLD = 200.0
# Below this many usable qubits (all of a chip with fewer) a tail statistic under the threshold reads inconclusive.
MIN_USABLE_QUBITS = 15
DESCRIPTIVE_COUNT_MARK = 12
SANITY_WRONG_QUBITS = base.SANITY_WRONG_QUBITS
# Level and window of the phase verdict, in radians: the refit of the q12 term, its half-width and the null bound.
PHASE_TARGET = -0.15
PHASE_HALF_WIDTH = 0.05
PHASE_NULL = 0.05
PHASE_ZERO_VERDICT = f"zero within {PHASE_NULL} rad"
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


def t1_delays(nqubits: int, multiplier: float) -> list[int]:
    """Qubit i's delay in cycles: the multiplier times its retained plateau T, rounded half up to a whole cycle."""
    return [math.floor(multiplier * PLATEAU_T_US[q] * CYCLES_PER_US + 0.5) for q in range(nqubits)]


def delay_text(nqubits: int, delays: Sequence[int]) -> str:
    """Every qubit waits the longest delay in total: wait(longest - d) before its X, wait(d) after, so the X-to-barrier
    wait of qubit i is its own d(i) whichever way the scheduler places a chain, and the shared barrier follows."""
    longest = max(delays)
    lines: list[str] = []
    for qubit in range(nqubits):
        if longest - delays[qubit]:
            lines.append(f"wait({longest - delays[qubit]}) q[{qubit}]")
        lines.append(f"X q[{qubit}]")
        if delays[qubit]:
            lines.append(f"wait({delays[qubit]}) q[{qubit}]")
    return base.circuit(nqubits, lines)


def anchor_text(nqubits: int, chain: int, *, prepared: bool) -> str:
    """An anchor carries the batch's chain of wait(chain) on every qubit, then X on every qubit when prepared in 1."""
    lines = [f"wait({chain}) q[{q}]" for q in range(nqubits)]
    return base.circuit(nqubits, lines + ([f"X q[{q}]" for q in range(nqubits)] if prepared else []))


def interleaved_circuits(multiplier: float) -> tuple[str, str, str]:
    """The three circuit names of the batch of one multiplier."""
    return f"readout-0-m{multiplier}.cq", f"t1-0-m{multiplier}.cq", f"t1-m{multiplier}.cq"


OPERATION = re.compile(r"(?P<gate>X90|X|Rz|wait)(?:\((?P<arg>[^)]*)\))? q\[(?P<qubit>\d+)\]")


def chain_profile(text: str, nqubits: int) -> dict[int, tuple[int, int | None]]:
    """Per qubit: the sum of its waits and the wait after its last X (None without an X), up to the first barrier.

    The barrier closes every qubit's timing: the measurement follows it, so a wait or an X placed after it adds no
    delay before the readout, and post_barrier_operations() names such a line.
    """
    total = dict.fromkeys(range(nqubits), 0)
    after: dict[int, int | None] = dict.fromkeys(range(nqubits))
    for line in text.splitlines():
        if line.startswith("barrier"):
            break
        if match := re.fullmatch(r"wait\((\d+)\) q\[(\d+)\]", line):
            total[int(match[2])] += int(match[1])
            if after[int(match[2])] is not None:
                after[int(match[2])] += int(match[1])  # type: ignore[operator]
        elif match := re.fullmatch(r"X q\[(\d+)\]", line):
            after[int(match[1])] = 0
    return {q: (total[q], after[q]) for q in range(nqubits)}


def post_barrier_operations(text: str) -> list[str]:
    """The wait, X, X90 and Rz lines that follow the first barrier; the measurement is the only operation there."""
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if line.startswith("barrier")), len(lines))
    return [line for line in lines[start:] if OPERATION.fullmatch(line)]


def operations(text: str, nqubits: int) -> dict[int, list[tuple[str, str | None]]]:
    """Per qubit: the (gate, argument) sequence before the first barrier."""
    found: dict[int, list[tuple[str, str | None]]] = {q: [] for q in range(nqubits)}
    for line in text.splitlines():
        if line.startswith("barrier"):
            break
        if match := OPERATION.fullmatch(line):
            found[int(match["qubit"])].append((match["gate"], match["arg"]))
    return found


def expected_operations(row: dict[str, Any], nqubits: int) -> dict[int, list[tuple[str, str | None]]] | None:
    """The gate sequence each qubit runs before the barrier, by circuit kind; None for a kind that timing_problems
    reads through its chain instead.

    Crosstalk T1 circuits: every driven qubit takes X then wait(wait_cycles) and every other qubit nothing. Ladder
    circuits: every driven qubit takes pulses X90 gates. Context anchors: every driven qubit takes one X. The
    retained readout-0 circuit: no gate. Ramsey circuits: the target qubit takes X90, wait(wait_cycles) when that is
    nonzero, Rz(angle) and X90, and every other qubit nothing, so the scan angle and the wait are the only variables.
    """
    want: dict[int, list[tuple[str, str | None]]] = {q: [] for q in range(nqubits)}
    kind = row["kind"]
    if kind == "anchor0" and "multiplier" not in row:
        return want
    if kind == "xt_t1":
        for q in row["driven"]:
            want[q] = [("X", None), ("wait", str(row["wait_cycles"]))]
    elif kind == "xt_x90":
        for q in row["driven"]:
            want[q] = [("X90", None)] * row["pulses"]
    elif kind == "xt_prep1":
        for q in row["driven"]:
            want[q] = [("X", None)]
    elif kind == "ramsey":
        wait = [("wait", str(row["wait_cycles"]))] if row["wait_cycles"] else []
        want[row["qubit"]] = [("X90", None), *wait, ("Rz", repr(row["angle"])), ("X90", None)]
    else:
        return None
    return want


def same_operations(got: list[tuple[str, str | None]], want: list[tuple[str, str | None]]) -> bool:
    if len(got) != len(want):
        return False
    for (gate, arg), (want_gate, want_arg) in zip(got, want, strict=True):
        if gate != want_gate or (gate == "Rz" and abs(float(arg or "nan") - float(want_arg or "nan")) > 1e-12):
            return False
        if gate != "Rz" and arg != want_arg:
            return False
    return True


def operation_problems(profile_name: str, rows: dict[str, dict[str, Any]] | None = None) -> list[str]:
    """Every crosstalk, anchor, readout and Ramsey circuit runs the gate sequence expected_operations() states."""
    rows = library(profile_name) if rows is None else rows
    nqubits = PROFILES[profile_name]["nqubits"]
    found = []
    for name, row in rows.items():
        want = expected_operations(row, nqubits)
        if want is None:
            continue
        got = operations(row["text"], nqubits)
        found += [
            f"{name}: qubit {q} runs {got[q]}, want {want[q]}"
            for q in range(nqubits)
            if not same_operations(got[q], want[q])
        ]
    return found


def timing_problems(profile_name: str, rows: dict[str, dict[str, Any]] | None = None) -> list[str]:
    """Every T1 circuit gives each qubit a chain of exactly its batch's longest delay and, for a delay circuit, an
    X-to-barrier wait equal to the qubit's own delay; no circuit holds a wait or gate after its barrier; the
    crosstalk, anchor and Ramsey circuits run the gate sequences of operation_problems()."""
    rows = library(profile_name) if rows is None else rows
    nqubits = PROFILES[profile_name]["nqubits"]
    found = operation_problems(profile_name, rows)
    for name, row in rows.items():
        found += [f"{name}: {line!r} follows the barrier" for line in post_barrier_operations(row["text"])]
        if "multiplier" not in row:
            continue
        delays = t1_delays(nqubits, row["multiplier"])
        for qubit, (total, after) in chain_profile(row["text"], nqubits).items():
            if total != max(delays):
                found.append(f"{name}: qubit {qubit} waits {total} cycles in total, the chain is {max(delays)}")
            want = {"anchor0": None, "anchor1": 0, "t1": delays[qubit]}[row["kind"]]
            if after != want:
                found.append(f"{name}: qubit {qubit} waits {after} cycles after its X, want {want}")
    return found


def order_problems(batches: list[dict[str, Any]]) -> list[str]:
    """Blocked order of the T1 batches: every round holds each multiplier once, the six multipliers form three
    unchanged pairs whose block position differs in every round, and each circuit of a multiplier's batch takes each of
    the three slots once across the rounds."""
    found = []
    rounds = sorted({b["round"] for b in batches})
    sequences = {r: [b["multiplier"] for b in batches if b["round"] == r] for r in rounds}
    for r, sequence in sequences.items():
        if sorted(sequence) != sorted(T1_MULTIPLIERS):
            found.append(f"round {r} lacks a multiplier")
    pairs = {r: {frozenset(s[k : k + 2]) for k in range(0, len(s), 2)} for r, s in sequences.items()}
    if len({frozenset(p) for p in pairs.values()}) != 1:
        found.append("the pairs of consecutive multipliers change between rounds")
    for multiplier in T1_MULTIPLIERS:
        blocks = sorted(sequences[r].index(multiplier) // 2 for r in rounds)
        if blocks != list(range(len(T1_MULTIPLIERS) // 2)):
            found.append(f"multiplier {multiplier} occupies the block positions {blocks}")
        for name in interleaved_circuits(multiplier):
            slots = sorted(b["circuits"].index(name) for b in batches if b["multiplier"] == multiplier)
            if slots != list(range(BATCH_LIMIT)):
                found.append(f"{name} occupies the slots {slots}")
    return found


def library(profile_name: str) -> dict[str, dict[str, Any]]:
    """Circuit file name -> text, kind and parameters; kind names the role a circuit plays in an arm."""
    nqubits = PROFILES[profile_name]["nqubits"]
    found: dict[str, dict[str, Any]] = {
        "readout-0.cq": {"text": base.circuit(nqubits, []), "kind": "anchor0", "driven": [], "expected_p1": 0.0}
    }
    for multiplier in T1_MULTIPLIERS:
        delays = t1_delays(nqubits, multiplier)
        chain = max(delays)
        for name, kind, text, expected in (
            (f"readout-0-m{multiplier}.cq", "anchor0", anchor_text(nqubits, chain, prepared=False), 0.0),
            (f"t1-0-m{multiplier}.cq", "anchor1", anchor_text(nqubits, chain, prepared=True), 1.0),
            (f"t1-m{multiplier}.cq", "t1", delay_text(nqubits, delays), 1.0),
        ):
            found[name] = {
                "text": text,
                "kind": kind,
                "multiplier": multiplier,
                "wait_cycles": chain,
                "driven": [] if kind == "anchor0" else list(range(nqubits)),
                "expected_p1": expected,
            }
            if kind == "t1":
                found[name]["delays_cycles"] = delays
    for context, driven in contexts(profile_name).items():
        for cycles in CROSSTALK_T1_CYCLES:
            found[f"xt-t1-{cycles}-{context}.cq"] = {
                "text": driven_t1_text(nqubits, driven, cycles),
                "kind": "xt_t1",
                "context": context,
                "wait_cycles": cycles,
                "driven": list(driven),
                "expected_p1": 1.0,
            }
        for pulses in CROSSTALK_LADDER_PULSES:
            found[f"xt-x90-{pulses}-{context}.cq"] = {
                "text": driven_x90_text(nqubits, driven, pulses),
                "kind": "xt_x90",
                "context": context,
                "pulses": pulses,
                "driven": list(driven),
                "expected_p1": 0.0,
            }
        if context != "all":
            found[f"xt-prep1-{context}.cq"] = {
                "text": base.circuit(nqubits, [f"X q[{q}]" for q in driven]),
                "kind": "xt_prep1",
                "context": context,
                "driven": list(driven),
                "expected_p1": 1.0,
            }
    for qubit in PAIR:
        found[f"xt-x90-{PAIR_PULSES}-q{qubit}.cq"] = {
            "text": driven_x90_text(nqubits, (qubit,), PAIR_PULSES),
            "kind": "xt_x90",
            "context": f"q{qubit}",
            "pulses": PAIR_PULSES,
            "driven": [qubit],
            "expected_p1": 0.0,
        }
    for qubit in PHASE[profile_name]:
        for wait in PHASE_WAITS:
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


def contexts(profile_name: str) -> dict[str, tuple[int, ...]]:
    """Driven qubits of each crosstalk context: class A, class B' and all qubits."""
    return {
        "A": CLASS_A[profile_name],
        "B": CLASS_B[profile_name],
        "all": tuple(range(PROFILES[profile_name]["nqubits"])),
    }


def driven_t1_text(nqubits: int, driven: Sequence[int], cycles: int) -> str:
    """X on the driven qubits, then each waits; the all-qubit text is the retained T1 circuit byte for byte."""
    return base.circuit(nqubits, [f"X q[{q}]" for q in driven] + [f"wait({cycles}) q[{q}]" for q in driven])


def driven_x90_text(nqubits: int, driven: Sequence[int], pulses: int) -> str:
    """The driven qubits take pulses X90 each in pulse-major order, as the retained ladder circuit does."""
    return base.circuit(nqubits, [f"X90 q[{q}]" for _ in range(pulses) for q in driven])


def crosstalk_units() -> list[tuple[str, list[str]]]:
    """The eight provider batches of the crosstalk arm as (unit, circuit names)."""
    units: list[tuple[str, list[str]]] = [
        (f"t1-{cycles}", [f"xt-t1-{cycles}-{c}.cq" for c in ("A", "B", "all")]) for cycles in CROSSTALK_T1_CYCLES
    ]
    units += [
        (f"x90-{pulses}", [f"xt-x90-{pulses}-{c}.cq" for c in ("A", "B", "all")]) for pulses in CROSSTALK_LADDER_PULSES
    ]
    units.append(("anchors", ["readout-0.cq", "xt-prep1-A.cq", "xt-prep1-B.cq"]))
    units.append(
        (
            "pair",
            [
                f"xt-x90-{PAIR_PULSES}-q{PAIR[0]}.cq",
                f"xt-x90-{PAIR_PULSES}-q{PAIR[1]}.cq",
                f"xt-x90-{PAIR_PULSES}-all.cq",
            ],
        )
    )
    return units


def usage(profile_name: str) -> dict[str, list[str]]:
    """Arm -> circuit names with their multiplicity in the series, in no particular order."""
    names = library(profile_name)
    interleaved: list[str] = []
    for multiplier in T1_MULTIPLIERS:
        interleaved += list(interleaved_circuits(multiplier)) * ROUNDS
    crosstalk = [name for _, names in crosstalk_units() for name in names]
    phase = [name for name, row in names.items() if row["kind"] == "ramsey"]
    return {"interleaved_t1": interleaved, "crosstalk": crosstalk, "q12_phase": phase}


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
    start = stream.position
    permutation = stream.shuffle(T1_MULTIPLIERS)
    blocks: list[list[Any]] = []
    for round_index in range(ROUNDS):
        shifted = [permutation[(k + 2 * round_index) % len(permutation)] for k in range(len(permutation))]
        for first in range(0, len(shifted), 2):
            if stream.below(2):
                shifted[first], shifted[first + 1] = shifted[first + 1], shifted[first]
        blocks.append(shifted)
    mark("interleaved_t1 blocks", start)
    start = stream.position
    slots = {m: stream.shuffle(interleaved_circuits(m)) for m in T1_MULTIPLIERS}
    mark("interleaved_t1 slots", start)
    for round_index, sequence in enumerate(blocks):
        for multiplier in sequence:
            order = slots[multiplier]
            turn = round_index % len(order)
            arms["interleaved_t1"].append(
                {
                    "circuits": order[turn:] + order[:turn],
                    "round": round_index,
                    "multiplier": multiplier,
                    "chain_cycles": max(t1_delays(PROFILES[profile_name]["nqubits"], multiplier)),
                }
            )
    start = stream.position
    units = crosstalk_units()
    for index in stream.shuffle(range(len(units))):
        unit, names = units[index]
        arms["crosstalk"].append({"circuits": stream.shuffle(names), "unit": unit})
    mark("crosstalk", start)
    start = stream.position
    leading = {wait: stream.below(len(PHASE_TRIADS)) for wait in PHASE_WAITS}
    qubit = PHASE[profile_name][0]
    for position in range(len(PHASE_WAITS) * len(PHASE_TRIADS)):
        wait = PHASE_WAITS[position % len(PHASE_WAITS)]
        triad = (leading[wait] + position // len(PHASE_WAITS)) % len(PHASE_TRIADS)
        names = [f"ramsey-q{qubit}-w{wait}-s{step:02d}.cq" for step in PHASE_TRIADS[triad]]
        arms["q12_phase"].append({"circuits": stream.shuffle(names), "wait_cycles": wait, "triad": triad})
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
    blocks = len(T1_MULTIPLIERS)
    needed = (blocks - 1) + ROUNDS * (blocks // 2) + blocks * (BATCH_LIMIT - 1)
    units = len(crosstalk_units())
    needed += (units - 1) + units * (BATCH_LIMIT - 1)
    return needed + len(PHASE_WAITS) + len(PHASE_WAITS) * len(PHASE_TRIADS) * (BATCH_LIMIT - 1)


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
    e01: float,
    e11: float,
    truth: dict[str, Any],
    tau2: float,
    count: int,
    delays: Sequence[int],
    rounds: int = ROUNDS,
) -> dict[str, Any]:
    """Standard errors the design gives T1 and the plateau of one qubit when the retained plateau model is true.

    Rows are the qubit's own delays (one per multiplier), rounds times; the variance of a population holds the binomial
    terms of the delay job and of the two anchor jobs of its batch and the job-level scatter tau2 on each of the three
    (the shared level that anchoring cancels is not credited, so the figures lean conservative). The free batch levels
    of design_summary() widen the plateau error further; that figure is reported there.
    """
    span = e11 - e01
    shapes = {"single": [truth["single_us"]], "plateau": [truth["plateau_us"], truth["plateau"]]}
    found: dict[str, Any] = {}
    for shape, theta in shapes.items():
        rows = []
        for cycles in delays:
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


def design_summary(
    e01: float, e11: float, theta: Sequence[float], tau2: float, count: int, qubit_delays: Sequence[int]
) -> dict[str, Any]:
    """Identifiability of the plateau from batch levels: ranks with and without anchors and the plateau error with
    every batch level free, for the qubit's delays (one per multiplier) repeated over the rounds."""
    delays = [c for _ in range(ROUNDS) for c in qubit_delays]
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


def job_seconds(profile: dict[str, Any], row: dict[str, Any], arm: str | None = None) -> float:
    shots = profile["shots"] if arm is None else profile["arm_shots"][arm]
    wait = row.get("wait_cycles", 0) * CYCLE_SECONDS
    return float(JOB_SECONDS + shots * (SHOT_SECONDS + wait))


def batch_counts(profile_name: str) -> dict[str, int]:
    return {
        "interleaved_t1": ROUNDS * len(T1_MULTIPLIERS),
        "crosstalk": len(crosstalk_units()),
        "q12_phase": len(PHASE_WAITS) * len(PHASE_TRIADS),
    }


def budget(profile_name: str) -> dict[str, Any]:
    profile = PROFILES[profile_name]
    rows = library(profile_name)
    per_arm: dict[str, Any] = {}
    for arm, names in usage(profile_name).items():
        seconds = sum(job_seconds(profile, rows[name], arm) for name in names)
        per_arm[arm] = {
            "batches": batch_counts(profile_name)[arm],
            "jobs": len(names),
            "shots": len(names) * profile["arm_shots"][arm],
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
            "tail_statistic_threshold": TAIL_STATISTIC_THRESHOLD,
            "min_usable_qubits": min(MIN_USABLE_QUBITS, PROFILES[profile_name]["nqubits"]),
            "tail_verdict_rule": (
                f"tail_confirmed when tail_statistic >= {TAIL_STATISTIC_THRESHOLD:g}; below it inconclusive when "
                f"fewer than min_usable_qubits qubits are usable, not_confirmed otherwise"
            ),
            "descriptive_count_mark": DESCRIPTIVE_COUNT_MARK,
            "phase_target_rad": PHASE_TARGET,
            "phase_half_width_rad": PHASE_HALF_WIDTH,
            "phase_null_rad": PHASE_NULL,
            "min_fringe_amplitude": MIN_FRINGE_AMPLITUDE,
        },
    }
    out["q12_phase"] = {
        "target_qubit": PHASE[profile_name][0],
        "waits_cycles": list(PHASE_WAITS),
        "angles_pi_over_3": [s // 12 for s in PHASE_STEPS],
        "triads_pi_over_3": [[s // 12 for s in t] for t in PHASE_TRIADS],
        "shots": PROFILES[profile_name]["arm_shots"]["q12_phase"],
        "expected_phase_se_rad": rounded(phase_expected_se(PROFILES[profile_name]["arm_shots"]["q12_phase"])),
    }
    if retained is None:
        return out
    tau2 = retained["tau2"]
    count = PROFILES[profile_name]["arm_shots"]["interleaved_t1"]
    qubits = retained["qubits"]
    interleaved = []
    for row in qubits:
        delays = [t1_delays(len(PLATEAU_T_US), m)[row["qubit"]] for m in T1_MULTIPLIERS]
        errors = expected_errors(row["e01"], row["e11"], row, tau2, count, delays)
        interleaved.append({"qubit": row["qubit"], "delay_cycles": delays, **errors})
    middle = sorted(qubits, key=lambda r: r["plateau_us"])[len(qubits) // 2]
    middle_delays = [t1_delays(len(PLATEAU_T_US), m)[middle["qubit"]] for m in T1_MULTIPLIERS]
    out["interleaved_t1"] = {
        "job_level_sigma": rounded(math.sqrt(tau2)),
        "job_level_basis": "excess variance of the retained series' three prepared-0 and three prepared-1 anchor jobs",
        "expected_errors": interleaved,
        "design": design_summary(
            middle["e01"], middle["e11"], (middle["plateau_us"], middle["plateau"]), tau2, count, middle_delays
        ),
        "design_qubit": middle["qubit"],
    }
    crosstalk_shots = PROFILES[profile_name]["arm_shots"]["crosstalk"]
    out["crosstalk"] = {
        "classes": {"A": list(CLASS_A[profile_name]), "B_prime": list(CLASS_B[profile_name])},
        "conditions": [f"t1-{c}" for c in CROSSTALK_T1_CYCLES] + [f"x90-{p}" for p in CROSSTALK_LADDER_PULSES],
        "flag_z": FLAG_Z,
        "class_contrasts": len(CLASS_A[profile_name] + CLASS_B[profile_name]) * 6,
        "pair_contrasts": len(PAIR),
        "flag_sigma_floor": FLAG_SIGMA_FLOOR,
        "flag_sigma_without_interleaved_arm": FLAG_SIGMA_ALONE,
        "retained_job_level_sigma": RETAINED_JOB_LEVEL_SIGMA,
        "flag_rule": (
            f"a contrast is flagged above {FLAG_Z} standard errors of the difference. With the interleaved arm each "
            f"qubit's job-level deviation is max(sqrt(job_level_variance) of its interleaved anchor pairs, "
            f"{FLAG_SIGMA_FLOOR}); the floor is the retained pooled value and keeps a zero estimate from making the "
            f"flag anti-conservative. Without the interleaved arm every qubit uses {FLAG_SIGMA_ALONE}, the largest "
            f"retained per-qubit value. The q1/q2 pair contrast uses the larger of its two qubits' sigmas. The "
            f"analysis records each qubit's sigma and its source; the reading at {RETAINED_JOB_LEVEL_SIGMA} is "
            f"descriptive"
        ),
        "family_false_flag_rate_at_true_sigma": {
            "true_sigma": FLAG_SIGMA_ALONE,
            "contrasts": FAMILY_CONTRASTS,
            "note": (
                "computed for independent contrasts; the contrasts of one condition batch share one all-qubit job, so "
                "these are not exact familywise rates"
            ),
            "flag_sigma_without_interleaved_arm": {
                f"p={p}": rounded(family_false_flag_rate(p, crosstalk_shots, FLAG_SIGMA_ALONE, FLAG_SIGMA_ALONE))
                for p in (0.5, 0.05, 0.0)
            },
            "flag_sigma_at_floor": {
                f"p={p}": rounded(family_false_flag_rate(p, crosstalk_shots, FLAG_SIGMA_ALONE, FLAG_SIGMA_FLOOR))
                for p in (0.5, 0.05, 0.0)
            },
        },
        "verdict_words": VERDICT_WORDS,
    }
    return out


def batch_directory(arm: str, index: int) -> str:
    return f"{arm}/batch-{index:02d}"


def files(profile_name: str, values: Sequence[int] | None, retained: dict[str, Any] | None = None) -> dict[str, str]:
    """Relative path -> text of every generated file of one profile's case directory.

    A circuit is written only inside a batch directory beside the manifest that lists it, which exists once the draw
    does; before that the directory holds no .cq file, so no circuit lacks a batch manifest
    (qi_toolchain_check.case_files rejects one).
    """
    profile = PROFILES[profile_name]
    rows = library(profile_name)
    out: dict[str, str] = {}
    index: dict[str, Any] = {
        "schema": SCHEMA,
        "profile": profile_name,
        "backend": profile["backend"],
        "shots": profile["arm_shots"],
        "cycle_seconds": CYCLE_SECONDS,
        "t1_multipliers": list(T1_MULTIPLIERS),
        "t1_delay_cycles": {str(m): t1_delays(profile["nqubits"], m) for m in T1_MULTIPLIERS},
        "rounds": ROUNDS,
        "crosstalk_classes": {"A": list(CLASS_A[profile_name]), "B_prime": list(CLASS_B[profile_name])},
        "crosstalk_t1_wait_cycles": list(CROSSTALK_T1_CYCLES),
        "crosstalk_ladder_pulses": list(CROSSTALK_LADDER_PULSES),
        "pair_qubits": list(PAIR),
        "pair_pulses": PAIR_PULSES,
        "phase_qubits": list(PHASE[profile_name]),
        "phase_wait_cycles": list(PHASE_WAITS),
        "phase_triads_pi_over_36": [list(t) for t in PHASE_TRIADS],
        "phase_steps_pi_over_36": list(PHASE_STEPS),
        "batch_limit": BATCH_LIMIT,
        "batches": batch_counts(profile_name),
        "qrng_draw": DRAW,
        "schedule": "schedule.json" if values is not None else "pending: DRAW is None, see qrng_request.json",
    }
    out["cases.json"] = json.dumps(index, indent=1) + "\n"
    out["prediction.json"] = json.dumps(prediction(profile_name, retained), indent=1) + "\n"
    out["qrng_request.json"] = json.dumps(qrng_request(), indent=1) + "\n"
    if values is None:
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
                "shots": profile["arm_shots"][arm],
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


def job_starts(run: Path) -> dict[str, str]:
    """File -> executed start (queued_at of results.json, which the retained notes read as the execution start); empty
    while the run holds no results."""
    path = run / "results.json"
    if not path.is_file():
        return {}
    return {entry["file"]: entry["job"]["queued_at"] for entry in json.loads(path.read_text(encoding="utf-8"))["jobs"]}


def read_batches(runs: list[Path]) -> list[dict[str, Any]]:
    """Run directories through qi_records: manifest rows, shot count, executed starts and the P1 of every qubit by
    circuit file."""
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
                "started": job_starts(run),
                "rows": {row["file"]: row for row in cases["circuits"]},
                "p1": {name: base.p1(shots, nqubits) for name, shots in raw.items()},
            }
        )
    return found


def interleaved_roles(batch: dict[str, Any]) -> tuple[str, str, str]:
    """File names of a batch's prepared-0 anchor, prepared-1 anchor and delay circuit, found by their kinds."""
    by_kind = {row["kind"]: name for name, row in batch["rows"].items()}
    return by_kind["anchor0"], by_kind["anchor1"], by_kind["t1"]


def tail_verdict(tail_statistic: float, usable: int, nqubits: int) -> str:
    """tail_confirmed at or above the threshold; below it inconclusive when fewer than MIN_USABLE_QUBITS qubits (all of
    a smaller chip) are usable, since dropped qubits only lower the sum; not_confirmed otherwise."""
    if tail_statistic >= TAIL_STATISTIC_THRESHOLD:
        return "tail_confirmed"
    if usable < min(MIN_USABLE_QUBITS, nqubits):
        return "inconclusive"
    return "not_confirmed"


class QubitFit:
    """The anchored fits of one qubit over the interleaved batches. An instance holds only its inputs, so it pickles
    for parallel.ordered_map, whose workers start under the spawn method."""

    def __init__(self, batches: list[dict[str, Any]], roles: list[Any]) -> None:
        self.batches = batches
        self.roles = roles

    def __call__(self, qubit: int) -> dict[str, Any]:
        batches, roles = self.batches, self.roles
        a0s = [b["p1"][r[0]][qubit] for b, r in zip(batches, roles, strict=True)]
        a1s = [b["p1"][r[1]][qubit] for b, r in zip(batches, roles, strict=True)]
        count = batches[0]["shots"]
        tau2 = job_level_variance(a0s, a1s, count)
        points: list[tuple[float, float, float]] = []
        raw_points: list[tuple[float, float, float]] = []
        by_delay: dict[Any, list[tuple[float, float]]] = {}
        mean0, mean1 = sum(a0s) / len(a0s), sum(a1s) / len(a1s)
        usable = mean1 - mean0 > MIN_READOUT_SPAN
        for batch, role, a0, a1 in zip(batches, roles, a0s, a1s, strict=True):
            delay = role[2]
            cycles = batch["rows"][delay]["delays_cycles"][qubit]
            p = batch["p1"][delay][qubit]
            point = anchored_point(p, a0, a1, count, tau2)
            if point is None or not usable:
                continue
            t_us = cycles * CYCLE_SECONDS * 1e6
            points.append((t_us, point[0], point[1]))
            by_delay.setdefault(batch["rows"][delay]["multiplier"], []).append(point)
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
            return row
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
        return row


def analyze_interleaved(batches: list[dict[str, Any]]) -> dict[str, Any]:
    """Per-qubit anchored fits of the interleaved T1 batches, the pooled tail statistic and the executed schedule.

    Qubit i reads its own delay of each delay circuit (delays_cycles) and the replicates of a delay are the rounds of
    one multiplier. A qubit whose anchors span too little or whose points number under six reads unusable and adds
    nothing to the tail statistic, a sum of nonnegative gains, so a dropped qubit moves the confirmatory verdict
    toward the null; pooled.unusable_qubits counts them. The pooled verdict tail_confirmed reads tail_statistic, the
    sum over usable qubits of tail_contribution, against TAIL_STATISTIC_THRESHOLD; tail_verdict adds inconclusive for a
    statistic under the threshold with fewer than MIN_USABLE_QUBITS usable qubits. The per-qubit labels and every
    count of them are descriptive and decide nothing.
    jobs lists the round and the executed start (queued_at of results.json) of every job.
    """
    nqubits = batches[0]["nqubits"]
    roles = [interleaved_roles(b) for b in batches]
    qubits = ordered_map(QubitFit(batches, roles), list(range(nqubits)), min_items=2)
    verdicts = [row["verdict"] for row in qubits]
    accepted = sum(v in ("single_exponential", "level_shift") for v in verdicts)
    rejected = sum(v in ("tail_plateau", "two_rate") for v in verdicts)
    tail_statistic = sum(row.get("tail_contribution", 0.0) for row in qubits)
    usable_count = nqubits - verdicts.count("unusable")
    pooled = {
        "descriptive_single_exponential_accepted": accepted,
        "descriptive_single_exponential_rejected": rejected,
        "descriptive_label_count_reaches_mark": accepted >= DESCRIPTIVE_COUNT_MARK,
        "unusable_qubits": verdicts.count("unusable"),
        "usable_qubits": usable_count,
        "min_usable_qubits": min(MIN_USABLE_QUBITS, nqubits),
        "tail_statistic": tail_statistic,
        "tail_statistic_threshold": TAIL_STATISTIC_THRESHOLD,
        "tail_confirmed": tail_statistic >= TAIL_STATISTIC_THRESHOLD,
        "tail_verdict": tail_verdict(tail_statistic, usable_count, nqubits),
    }
    jobs = [
        {
            "run": batch["run"],
            "round": batch["meta"].get("round"),
            "multiplier": batch["meta"].get("multiplier"),
            "file": name,
            "kind": batch["rows"][name]["kind"],
            "started_utc": batch.get("started", {}).get(name),
        }
        for batch in batches
        for name in sorted(batch["rows"])
    ]
    return {"qubits": qubits, "pooled": pooled, "jobs": jobs}


def contrast_z(p_half: float, p_all: float, count: int, sigma: float) -> float:
    """Difference of two readings of one qubit in standard errors of the difference: binomial variance and the job-level
    variance sigma squared on each job; the registered flag reads the qubit's flag_sigmas() value."""
    variance = base.binomial_variance(p_half, count) + base.binomial_variance(p_all, count) + 2 * sigma**2
    return (p_half - p_all) / math.sqrt(variance)


def family_false_flag_rate(
    p: float, count: int, true_sigma: float, flag_sigma: float, contrasts: int = FAMILY_CONTRASTS
) -> float:
    """Probability that at least one of contrasts independent null contrasts exceeds FLAG_Z when the flag's standard
    error uses flag_sigma and the true job-level deviation is true_sigma, for readings near population p."""
    binomial = 2 * p * (1 - p) / count
    scale = FLAG_Z * math.sqrt(binomial + 2 * flag_sigma**2) / math.sqrt(binomial + 2 * true_sigma**2)
    single = 2 * (1 - NormalDist().cdf(scale))
    return 1 - (1 - single) ** contrasts


def flag_sigmas(interleaved: list[dict[str, Any]] | None, nqubits: int) -> list[dict[str, Any]]:
    """Per-qubit flag sigma and its source: max(sqrt(job_level_variance) of the qubit's interleaved anchor pairs,
    FLAG_SIGMA_FLOOR) when the interleaved arm is held, FLAG_SIGMA_ALONE for every qubit otherwise."""
    if not interleaved:
        return [
            {"qubit": q, "sigma": FLAG_SIGMA_ALONE, "source": "retained_largest", "interleaved_estimate": None}
            for q in range(nqubits)
        ]
    roles = [interleaved_roles(b) for b in interleaved]
    out = []
    for qubit in range(nqubits):
        zero = [b["p1"][r[0]][qubit] for b, r in zip(interleaved, roles, strict=True)]
        one = [b["p1"][r[1]][qubit] for b, r in zip(interleaved, roles, strict=True)]
        estimate = math.sqrt(job_level_variance(zero, one, interleaved[0]["shots"]))
        sigma = max(estimate, FLAG_SIGMA_FLOOR)
        source = "interleaved_anchors" if estimate >= FLAG_SIGMA_FLOOR else "retained_pooled_floor"
        out.append({"qubit": qubit, "sigma": sigma, "source": source, "interleaved_estimate": estimate})
    return out


def analyze_crosstalk(batches: list[dict[str, Any]], interleaved: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Half-drive against same-batch all-drive readings per class qubit and condition, and the q1/q2 pair.

    A half-drive batch holds the class A, class B' and all-qubit circuit of one condition; each class qubit contrasts
    its own class circuit with the all-qubit circuit by contrast_z, flagged above FLAG_Z; the sigma of a contrast is the
    qubit's flag_sigmas() entry (the larger of the two for the pair) and each row records it with its source.
    Populations and ladder values P(0) normalize by the context anchors (readout-0 and the class prepared in 1),
    all-drive readings by their qubit's class anchors, so the readout context of the all-drive circuit is not separated
    from the drive (reported residual). The reading is drive-and-readout context dependence: the all-drive circuit
    changes the drive and the readout context together, and the contrast names no mechanism. A contrast without usable
    context anchors keeps its z and flag and lacks the normalized values; pooled.unusable_normalizations counts those
    rows.
    """
    count = batches[0]["shots"]
    sigmas = flag_sigmas(interleaved, batches[0]["nqubits"])
    anchors = next(b for b in batches if b["meta"].get("unit") == "anchors")
    zero = next(anchors["p1"][f] for f, row in anchors["rows"].items() if row["kind"] == "anchor0")
    prepared = {row["context"]: anchors["p1"][f] for f, row in anchors["rows"].items() if row["kind"] == "xt_prep1"}
    classes = {row["context"]: row["driven"] for row in anchors["rows"].values() if row["kind"] == "xt_prep1"}
    rows: list[dict[str, Any]] = []
    pair: list[dict[str, Any]] = []
    for batch in batches:
        unit = batch["meta"].get("unit")
        if unit == "anchors":
            continue
        by_context = {row["context"]: name for name, row in batch["rows"].items()}
        if unit == "pair":
            all_name = by_context["all"]
            pair_sigma = max(sigmas[q]["sigma"] for q in PAIR)
            for qubit in PAIR:
                alone = batch["p1"][by_context[f"q{qubit}"]][qubit]
                every = batch["p1"][all_name][qubit]
                pair.append(
                    {
                        "qubit": qubit,
                        "alone": alone,
                        "all_driven": every,
                        "flag_sigma": pair_sigma,
                        "sigma_source": "larger of the pair's qubits: "
                        + ", ".join(f"q{q} {sigmas[q]['source']}" for q in PAIR),
                        "z": contrast_z(alone, every, count, pair_sigma),
                        "flagged": abs(contrast_z(alone, every, count, pair_sigma)) > FLAG_Z,
                        "z_at_retained_sigma": contrast_z(alone, every, count, RETAINED_JOB_LEVEL_SIGMA),
                    }
                )
            other = PAIR[1]
            pair.append(
                {
                    "qubit": other,
                    "reading_with_only_partner_driven": batch["p1"][by_context[f"q{PAIR[0]}"]][other],
                }
            )
            continue
        ladder = unit.startswith("x90")
        for context in ("A", "B"):
            for qubit in classes[context]:
                a0, a1 = zero[qubit], prepared[context][qubit]
                half = batch["p1"][by_context[context]][qubit]
                every = batch["p1"][by_context["all"]][qubit]
                z = contrast_z(half, every, count, sigmas[qubit]["sigma"])
                span = a1 - a0
                row = {
                    "unit": unit,
                    "context": context,
                    "qubit": qubit,
                    "flag_sigma": sigmas[qubit]["sigma"],
                    "sigma_source": sigmas[qubit]["source"],
                    "z": z,
                    "flagged": abs(z) > FLAG_Z,
                    "z_at_retained_sigma": contrast_z(half, every, count, RETAINED_JOB_LEVEL_SIGMA),
                }
                if span > MIN_READOUT_SPAN:
                    sign = -1.0 if ladder else 1.0
                    row["half_value"] = (1.0 if ladder else 0.0) + sign * (half - a0) / span
                    row["all_value"] = (1.0 if ladder else 0.0) + sign * (every - a0) / span
                rows.append(row)
    flagged = sum(r["flagged"] for r in rows) + sum(bool(p.get("flagged")) for p in pair)
    contrasts = len(rows) + sum("z" in p for p in pair)
    descriptive = sum(abs(r["z_at_retained_sigma"]) > FLAG_Z for r in rows) + sum(
        abs(p["z_at_retained_sigma"]) > FLAG_Z for p in pair if "z_at_retained_sigma" in p
    )
    return {
        "rows": rows,
        "pair": pair,
        "pooled": {
            "contrasts_formed": contrasts,
            "flag_z": FLAG_Z,
            "flagged": flagged,
            "descriptive_flagged_at_retained_sigma": descriptive,
            "flag_sigma_by_qubit": sigmas,
            "unusable_normalizations": sum("half_value" not in r for r in rows),
            "reading": VERDICT_WORDS if flagged else f"no {VERDICT_WORDS} at the flag",
        },
    }


def interleaved_fit(points: list[tuple[float, float, float]]) -> tuple[str, dict[str, Any]]:
    """The lower-AICc tail fit that classify() would accept (lack of fit probability and an AICc gain of AICC_GAIN over
    the single exponential), else the single exponential."""
    fits = {shape: fit_shape(points, shape) for shape in ("single", "plateau", "two_rate")}
    accepted = {
        name: fit
        for name, fit in fits.items()
        if name != "single"
        and fit["probability"] >= LACK_OF_FIT_PROBABILITY
        and fits["single"]["aicc"] - fit["aicc"] >= AICC_GAIN
    }
    shape = min(accepted, key=lambda name: accepted[name]["aicc"]) if accepted else "single"
    return shape, fits[shape]


def fit_prediction(
    shape: str, fit: dict[str, Any], points: list[tuple[float, float, float]], t_us: float
) -> tuple[float, float]:
    """Fitted population at t_us and its variance: the gradient of decay() at the fitted parameters through the
    covariance of the weighted fit (the inverse information of the points)."""
    theta = fit["params"]
    cov = covariance([(decay_gradient(shape, theta, t), variance) for t, _, variance in points])
    gradient = decay_gradient(shape, theta, t_us)
    variance = sum(gradient[i] * cov[i][j] * gradient[j] for i in range(len(gradient)) for j in range(len(gradient)))
    return decay(shape, theta, t_us), max(0.0, variance)


class InterleavedQubitFit:
    """The interleaved fit of one qubit for staggered_comparison, or None below six anchored points. An instance holds
    only its inputs, so it pickles for parallel.ordered_map."""

    def __init__(self, interleaved: list[dict[str, Any]], roles: list[Any]) -> None:
        self.interleaved = interleaved
        self.roles = roles

    def __call__(self, qubit: int) -> tuple[str, dict[str, Any], list[tuple[float, float, float]]] | None:
        interleaved, roles = self.interleaved, self.roles
        a0s = [b["p1"][r[0]][qubit] for b, r in zip(interleaved, roles, strict=True)]
        a1s = [b["p1"][r[1]][qubit] for b, r in zip(interleaved, roles, strict=True)]
        tau2 = job_level_variance(a0s, a1s, interleaved[0]["shots"])
        points: list[tuple[float, float, float]] = []
        for batch, role, a0, a1 in zip(interleaved, roles, a0s, a1s, strict=True):
            row = batch["rows"][role[2]]
            point = anchored_point(batch["p1"][role[2]][qubit], a0, a1, interleaved[0]["shots"], tau2)
            if point is not None:
                points.append((row["delays_cycles"][qubit] * CYCLE_SECONDS * 1e6, point[0], point[1]))
        if len(points) < 6:
            return None
        shape, fit = interleaved_fit(points)
        return shape, fit, points


def staggered_comparison(interleaved: list[dict[str, Any]], crosstalk: list[dict[str, Any]]) -> dict[str, Any]:
    """Descriptive: the all-drive crosstalk T1 readings against the interleaved arm's own fit at the same wait.

    The all-drive circuit excites every qubit together; the interleaved circuit staggers the X of each qubit so that
    every X-to-barrier wait ends at one barrier. Per qubit and crosstalk wait (5, 20 and 80 us), the all-drive
    population normalized by the qubit's class anchors is compared with the qubit's interleaved fit (interleaved_fit())
    evaluated at that wait, not with a raw point at the nearest delay, which differs in delay and so measures decay.
    The difference is in standard errors of the difference: the all-drive point's variance (its qubit's flag sigma for
    the job level) plus the fit's prediction variance; within_fitted_range marks a wait inside the qubit's delay span.
    A qubit outside both classes has no class anchor and is omitted, as is a qubit with fewer than six points. No
    verdict reads this.
    """
    anchors = next(b for b in crosstalk if b["meta"].get("unit") == "anchors")
    zero = next(anchors["p1"][f] for f, row in anchors["rows"].items() if row["kind"] == "anchor0")
    prepared = {row["context"]: anchors["p1"][f] for f, row in anchors["rows"].items() if row["kind"] == "xt_prep1"}
    context_of = {
        q: row["context"] for row in anchors["rows"].values() if row["kind"] == "xt_prep1" for q in row["driven"]
    }
    count = crosstalk[0]["shots"]
    sigmas = flag_sigmas(interleaved, interleaved[0]["nqubits"])
    roles = [interleaved_roles(b) for b in interleaved]
    results = ordered_map(InterleavedQubitFit(interleaved, roles), list(range(interleaved[0]["nqubits"])), min_items=2)
    fitted = {qubit: result for qubit, result in enumerate(results) if result is not None}
    rows: list[dict[str, Any]] = []
    for batch in sorted((b for b in crosstalk if str(b["meta"].get("unit")).startswith("t1-")), key=lambda b: b["run"]):
        name = next(f for f, row in batch["rows"].items() if row["context"] == "all")
        cycles = batch["rows"][name]["wait_cycles"]
        t_us = cycles * CYCLE_SECONDS * 1e6
        for qubit, context in sorted(context_of.items()):
            if qubit not in fitted:
                continue
            point = anchored_point(
                batch["p1"][name][qubit], zero[qubit], prepared[context][qubit], count, sigmas[qubit]["sigma"] ** 2
            )
            if point is None:
                continue
            shape, fit, points = fitted[qubit]
            value, fit_variance = fit_prediction(shape, fit, points, t_us)
            difference = point[0] - value
            rows.append(
                {
                    "qubit": qubit,
                    "crosstalk_wait_us": t_us,
                    "all_drive_value": point[0],
                    "interleaved_fit_shape": shape,
                    "interleaved_fit_value": value,
                    "interleaved_fit_se": math.sqrt(fit_variance),
                    "within_fitted_range": min(p[0] for p in points) <= t_us <= max(p[0] for p in points),
                    "difference": difference,
                    "difference_in_se": difference / math.sqrt(point[1] + fit_variance),
                }
            )
    return {
        "rows": rows,
        "pooled": {
            "rows": len(rows),
            "mean_difference": sum(r["difference"] for r in rows) / len(rows) if rows else None,
            "mean_difference_in_se": sum(r["difference_in_se"] for r in rows) / len(rows) if rows else None,
        },
    }


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


def triad_problems(triads: Sequence[Sequence[int]]) -> list[str]:
    """Each triad of pi/36 steps has sines and cosines that sum to zero, so a level shared by its three jobs does not
    move either fringe quadrature."""
    found = []
    for triad in triads:
        angles = [s * math.pi / 36 for s in triad]
        if abs(sum(math.cos(a) for a in angles)) > 1e-9 or abs(sum(math.sin(a) for a in angles)) > 1e-9:
            found.append(f"triad {tuple(triad)} has a nonzero quadrature sum")
    return found


def phase_expected_se(shots: int, amplitude: float = 0.45) -> float:
    """Standard error of the fitted phase for exact points of a fringe of the given cosine amplitude at PHASE_STEPS."""
    angles = [s * math.pi / 36 for s in PHASE_STEPS]
    fit = fringe_fit([(a, 0.5 + amplitude * math.cos(a + PHASE_TARGET), shots) for a in angles])
    if fit is None:
        raise ValueError("no fringe")
    return fit["phase_se"]


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
    return {
        "scans": rows,
        "detuning": phase_detuning(rows),
        "unusable_scans": sum(r["verdict"] == "no_fringe" for r in rows),
    }


def phase_detuning(scans: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Per qubit the static z rotation that accrues over the wait: the fringe offset at the long wait minus the
    offset at the zero wait, wrapped to (-pi, pi], its standard error from the two fits, the detuning in rad per
    microsecond and the registered verdict 'zero within 0.05 rad' when the difference and twice its error lie inside
    PHASE_NULL.
    A qubit whose either fringe reads no_fringe or poor_fit is unresolved."""
    short, long = min(PHASE_WAITS), max(PHASE_WAITS)
    found = []
    for qubit in sorted({s["qubit"] for s in scans}):
        by_wait = {s["wait_cycles"]: s for s in scans if s["qubit"] == qubit}
        entry: dict[str, Any] = {"qubit": qubit, "wait_cycles": [short, long]}
        pair = [by_wait.get(short), by_wait.get(long)]
        first, second = pair
        if first is None or second is None or {first["verdict"], second["verdict"]} & {"no_fringe", "poor_fit"}:
            entry["verdict"] = "unresolved"
        else:
            difference = wrap(second["phase"] - first["phase"])
            error = math.hypot(first["phase_se"], second["phase_se"])
            entry |= {
                "phase_difference": difference,
                "phase_difference_se": error,
                "detuning_rad_per_us": difference / ((long - short) * CYCLE_SECONDS * 1e6),
                "verdict": PHASE_ZERO_VERDICT
                if abs(difference) + 2 * error <= PHASE_NULL
                else f"not {PHASE_ZERO_VERDICT}",
            }
        found.append(entry)
    return found


def analyze(runs: list[Path], prediction_path: Path | None = None) -> dict[str, Any]:
    """Rows and verdicts of every arm among the run directories."""
    batches = read_batches(runs)
    out: dict[str, Any] = {"schema": ANALYSIS_SCHEMA, "runs": [b["run"] for b in batches]}
    grouped = {arm: [b for b in batches if b["arm"] == arm] for arm in ARMS}
    if grouped["interleaved_t1"]:
        out["interleaved_t1"] = analyze_interleaved(grouped["interleaved_t1"])
    if grouped["crosstalk"]:
        out["crosstalk"] = analyze_crosstalk(grouped["crosstalk"], grouped["interleaved_t1"] or None)
    if grouped["interleaved_t1"] and grouped["crosstalk"]:
        out["simultaneous_versus_staggered"] = staggered_comparison(grouped["interleaved_t1"], grouped["crosstalk"])
    if grouped["q12_phase"]:
        out["q12_phase"] = analyze_phase(grouped["q12_phase"])
    if prediction_path is not None:
        out["prediction"] = prediction_path.name
    return out


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


def utc_stamp(value: Any) -> bool:
    """True for an ISO 8601 text with a zero UTC offset, the form clock().isoformat() writes for utc_now()."""
    if not isinstance(value, str):
        return False
    try:
        stamp = datetime.datetime.fromisoformat(value)
    except ValueError:
        return False
    return stamp.utcoffset() == datetime.timedelta(0)


def whole_number(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def admission_record_problems(document: Any, backend_type_id: int) -> list[str]:
    """Fields of admission.json that submit_series writes: schema, the series' backend type, status idle, own queue 0,
    a positive attempt number and a UTC stamp."""
    if not isinstance(document, dict):
        return ["the record is not an object"]
    found = []
    if document.get("schema") != "qi-admission-v1":
        found.append(f"schema is {document.get('schema')!r}, want 'qi-admission-v1'")
    if not whole_number(document.get("backend_type_id")) or document["backend_type_id"] != backend_type_id:
        found.append(f"backend_type_id is {document.get('backend_type_id')!r}, want {backend_type_id}")
    if document.get("status") != "idle":
        found.append(f"status is {document.get('status')!r}, want 'idle'")
    if not whole_number(document.get("queue_own")) or document["queue_own"] != 0:
        found.append(f"queue_own is {document.get('queue_own')!r}, want 0")
    if not whole_number(document.get("attempt")) or document["attempt"] < 1:
        found.append(f"attempt is {document.get('attempt')!r}, want a positive integer")
    if not utc_stamp(document.get("utc")):
        found.append(f"utc is {document.get('utc')!r}, want an ISO 8601 UTC stamp")
    return found


def trace_record_problems(document: Any) -> list[str]:
    """Fields of status-trace.json that write_trace and trace_row write: schema, a poll interval that keeps the trace
    gaps within MAX_TRACE_GAP_SECONDS, and at least one row of a UTC stamp, a status text and an own-queue reading."""
    if not isinstance(document, dict):
        return ["the record is not an object"]
    found = []
    if document.get("schema") != "qi-status-trace-v1":
        found.append(f"schema is {document.get('schema')!r}, want 'qi-status-trace-v1'")
    poll = document.get("poll_seconds")
    if isinstance(poll, bool) or not isinstance(poll, (int, float)) or not 0 < poll <= MAX_TRACE_GAP_SECONDS:
        found.append(f"poll_seconds is {poll!r}, want a number in (0, {MAX_TRACE_GAP_SECONDS}]")
    rows = document.get("rows")
    if not isinstance(rows, list) or not rows:
        return [*found, "rows is not a non-empty list"]
    for number, row in enumerate(rows):
        if not isinstance(row, dict):
            found.append(f"row {number} is not an object")
            continue
        if not utc_stamp(row.get("utc")):
            found.append(f"row {number}: utc is {row.get('utc')!r}, want an ISO 8601 UTC stamp")
        if not isinstance(row.get("status"), str) or not row["status"]:
            found.append(f"row {number}: status is {row.get('status')!r}, want a non-empty text")
        if "queue_own" not in row or not (row["queue_own"] is None or whole_number(row["queue_own"])):
            found.append(f"row {number}: queue_own is {row.get('queue_own')!r}, want a whole number or null")
    return found


def sanity(run: Path) -> list[str]:
    """Jobs complete with all shots, anchor circuits read their fixed outcome on all but SANITY_WRONG_QUBITS qubits,
    the run holds its admission record and status trace with every field valid (admission_record_problems,
    trace_record_problems), and no job started while the backend read outside START_STATUSES."""
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
        if row["kind"] not in ("anchor0", "anchor1", "xt_prep1"):
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
    for name, validate in (
        ("admission.json", lambda document: admission_record_problems(document, cases["backend_type_id"])),
        ("status-trace.json", trace_record_problems),
    ):
        if not (run / name).is_file():
            problems.append(
                f"{run.name}: {name} is missing, so the backend status at submission and start is unrecorded"
            )
            continue
        try:
            document = json.loads((run / name).read_text(encoding="utf-8"))
        except ValueError as error:
            problems.append(f"{run.name}: {name} is not JSON: {error}")
            continue
        problems += [f"{run.name}: {name}: {found}" for found in validate(document)]
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


def append_trace_row(run: Path, row: dict[str, Any]) -> None:
    """Append one status read to status-trace.json and keep the rows already on disk."""
    held = run / "status-trace.json"
    rows: list[dict[str, Any]] = json.loads(held.read_text(encoding="utf-8"))["rows"] if held.is_file() else []
    write_trace(run, [*rows, row])


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
    retried after that many seconds, at most max_refusals times. The status read that admits a submission is the
    first row of status-trace.json and is written before the submit command enqueues the batch, because a job can
    start before the first read that follows the submission. While the collection runs, the status is read every
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
                append_trace_row(run, {"utc": admitted["utc"], "status": label, "queue_own": queue})
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
    schedule() gives synthetic_values; shifts[b] is added to every circuit of batch b. Qubit i reads its own delay of
    the circuit."""
    plan = schedule("tuna_17", synthetic_values(2000))["arms"]["interleaved_t1"]
    rows_by_name = library("tuna_17")
    out = []
    for number, batch in enumerate(plan):
        shift = shifts[number] if shifts is not None else 0.0
        rows = {}
        p1: dict[str, list[float]] = {}
        for name in batch["circuits"]:
            source = rows_by_name[name]
            rows[name] = {
                key: source[key] for key in ("kind", "wait_cycles", "multiplier", "delays_cycles") if key in source
            }
            values = []
            for index, model in enumerate(qubit_models):
                span = model["e11"] - model["e01"]
                if source["kind"] == "anchor0":
                    p = model["e01"]
                elif source["kind"] == "anchor1":
                    p = model["e11"]
                else:
                    t_us = source["delays_cycles"][index] * CYCLE_SECONDS * 1e6
                    p = model["e01"] + span * decay(model["shape"], model["theta"], t_us)
                values.append(round((p + shift) * count) / count)
            p1[name] = values
        out.append(
            {
                "run": f"batch-{number:02d}",
                "arm": "interleaved_t1",
                "meta": {k: v for k, v in batch.items() if k != "circuits"},
                "shots": count,
                "nqubits": len(qubit_models),
                "rows": rows,
                "p1": p1,
            }
        )
    return out


def synthetic_crosstalk(shift_qubit: int | None = None, shift: float = 0.0, count: int = 8192) -> list[dict[str, Any]]:
    """Crosstalk batches in the order schedule() gives synthetic_values with fixed readings: anchors 0.03 and 0.96, a
    driven qubit of a T1 circuit 0.495, of a ladder circuit 0.05, an idle qubit 0.03; shift is added to shift_qubit in
    the class circuits (contexts A and B) of the T1 and ladder kinds."""
    rows_by_name = library("tuna_17")
    out = []
    for number, batch in enumerate(schedule("tuna_17", synthetic_values(2000))["arms"]["crosstalk"]):
        rows = {}
        p1: dict[str, list[float]] = {}
        for name in batch["circuits"]:
            source = rows_by_name[name]
            rows[name] = {k: source[k] for k in ("kind", "context", "driven", "pulses", "wait_cycles") if k in source}
            values = []
            for qubit in range(PROFILES["tuna_17"]["nqubits"]):
                driven = qubit in source["driven"]
                if source["kind"] == "xt_prep1":
                    p = 0.96 if driven else 0.03
                elif source["kind"] == "xt_t1":
                    p = 0.495 if driven else 0.03
                elif source["kind"] == "xt_x90":
                    p = 0.05 if driven else 0.03
                else:
                    p = 0.03
                if qubit == shift_qubit and source.get("context") in ("A", "B") and source["kind"] != "xt_prep1":
                    p += shift
                values.append(round(p * count) / count)
            p1[name] = values
        out.append(
            {
                "run": f"batch-{number:02d}",
                "arm": "crosstalk",
                "meta": {"unit": batch["unit"]},
                "shots": count,
                "nqubits": PROFILES["tuna_17"]["nqubits"],
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

    # Circuits: every text measures once, each qubit's waits sum to its batch chain, the X-to-barrier wait is the
    # qubit's own delay, and angles sit on the grid.
    rows = library("tuna_17")
    expect(
        all(r["text"].count("measure") == 1 and "qubit[17] q" in r["text"] for r in rows.values()),
        "a circuit measures twice",
    )
    expect(max(t1_delays(17, 12)) == 17423, "the longest delay moved")
    for profile_name in PROFILES:
        problems += timing_problems(profile_name)
    grid = [r["angle"] / (math.pi / 36) for r in rows.values() if r["kind"] == "ramsey"]
    expect(all(abs(g - round(g)) < 1e-9 for g in grid), "a Ramsey angle leaves the pi/36 grid")
    expect(
        all(q < PROFILES["qx"]["nqubits"] for q in (*CLASS_A["qx"], *CLASS_B["qx"], *PAIR, *PHASE["qx"])),
        "a qx arm qubit exceeds the emulator",
    )
    # Order: one draw, deterministic, within the batch limit, blocked rounds, anchors in every batch.
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
        problems += order_problems(plan["arms"]["interleaved_t1"])
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
            len(json.loads((run / "status-trace.json").read_text(encoding="utf-8"))["rows"]) == 5,
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
    delays = [t1_delays(17, m)[9] for m in T1_MULTIPLIERS]
    summary = design_summary(0.027, 0.959, (PLATEAU_T_US[9], 0.02), 0.0045**2, 8192, delays)
    expect(summary["rank_with_anchors"] == summary["columns_with_anchors"], f"anchored design rank {summary}")
    expect(summary["rank_without_anchors"] < summary["columns_without_anchors"], f"unanchored design rank {summary}")
    expect(0 < summary["se_plateau_with_free_batch_levels"] < 0.01, f"plateau error with free levels {summary}")
    # Estimator: exact models recover their class, and a level shift common to a batch is cancelled by its anchors.
    models = [
        {"shape": "single", "theta": [22.0], "e01": 0.03, "e11": 0.96},
        {"shape": "plateau", "theta": [20.0, 0.03], "e01": 0.03, "e11": 0.96},
        {"shape": "two_rate", "theta": [4.0, 60.0, 0.4], "e01": 0.03, "e11": 0.96},
    ]
    shifts = [0.012 * math.sin(b) for b in range(ROUNDS * len(T1_MULTIPLIERS))]
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
    # Crosstalk: classes are disjoint and omit qubit 2, the flag bound is the Bonferroni quantile, the flag fires on a
    # contrast just above it and not just below, and the analysis flags a shifted class reading and nothing else.
    for profile_name in PROFILES:
        a, b = set(CLASS_A[profile_name]), set(CLASS_B[profile_name])
        expect(not a & b and PAIR[1] not in a | b, f"{profile_name}: class sets overlap or hold qubit {PAIR[1]}")
    expect(
        len(CLASS_A["tuna_17"]) == 8 and len(CLASS_B["tuna_17"]) == 8, "the tuna_17 classes are not eight qubits each"
    )
    expect(abs(NormalDist().inv_cdf(1 - 0.05 / 204) - FLAG_Z) < 0.005, "FLAG_Z is not the Bonferroni quantile")
    se = math.sqrt(2 * 0.25 / 8192 + 2 * FLAG_SIGMA_ALONE**2)
    expect(
        abs(contrast_z(0.5 + 3.6 * se, 0.5, 8192, FLAG_SIGMA_ALONE))
        > FLAG_Z
        > abs(contrast_z(0.5 + 3.3 * se, 0.5, 8192, FLAG_SIGMA_ALONE)),
        "flag",
    )
    exact = synthetic_interleaved([{"shape": "single", "theta": [22.0], "e01": 0.03, "e11": 0.96}] * 17)
    floors = flag_sigmas(exact, 17)
    expect(
        all(s["sigma"] == FLAG_SIGMA_FLOOR and s["source"] == "retained_pooled_floor" for s in floors)
        and all(s["sigma"] == FLAG_SIGMA_ALONE for s in flag_sigmas(None, 17)),
        "the flag sigma floor or the constant without the interleaved arm",
    )
    expect(
        [
            tail_verdict(250.0, 17, 17),
            tail_verdict(100.0, 14, 17),
            tail_verdict(100.0, 15, 17),
            tail_verdict(250.0, 3, 17),
        ]
        == ["tail_confirmed", "inconclusive", "not_confirmed", "tail_confirmed"],
        "the tail verdict outcomes",
    )
    quiet = analyze_crosstalk(synthetic_crosstalk())
    expect(
        quiet["pooled"]["flagged"] == 0 and quiet["pooled"]["contrasts_formed"] == 98,
        f"an unshifted crosstalk series read {quiet['pooled']}",
    )
    loud = analyze_crosstalk(synthetic_crosstalk(shift_qubit=5, shift=0.08))
    flagged = [r for r in loud["rows"] if r["flagged"]]
    expect(
        len(flagged) == 6 and all(r["qubit"] == 5 for r in flagged), f"a shifted class reading flagged {len(flagged)}"
    )
    expect(not triad_problems(PHASE_TRIADS), "a phase triad has a nonzero quadrature sum")
    expect(bool(triad_problems(((0, 12, 24), (36, 48, 60)))), "a non-triad split passed the quadrature check")
    stamp = "2026-01-01T00:00:00+00:00"
    good_admission = {
        "schema": "qi-admission-v1",
        "utc": stamp,
        "backend_type_id": 7,
        "status": "idle",
        "queue_own": 0,
        "attempt": 1,
    }
    expect(not admission_record_problems(good_admission, 7), "a valid admission record failed")
    expect(bool(admission_record_problems({}, 7)), "an empty admission record passed")
    good_trace = {
        "schema": "qi-status-trace-v1",
        "poll_seconds": 15.0,
        "rows": [{"utc": stamp, "status": "idle", "queue_own": 0}],
    }
    expect(not trace_record_problems(good_trace), "a valid status trace failed")
    expect(bool(trace_record_problems({"rows": [{}]})), "an empty status trace passed")
    expect(bool(post_barrier_operations("barrier q\nwait(5) q[0]\nb = measure q\n")), "a post-barrier wait passed")
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
