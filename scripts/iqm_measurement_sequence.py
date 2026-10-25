"""IQM Garnet case of the measurement-sequence pinching test: does a mid-circuit measurement act as ideal pinching?

Ideal pinching is the nonselective projective measurement in Z, rho -> sum_m |m><m| rho |m><m|. The case drives six
pairwise uncoupled qubits, chosen from the live calibration set (select_qubits), in parallel with N rotations of
THETA/N about X, THETA = 8 pi/9, and reads a final Z measurement. A sign s = +-1 flips every rotation; the four
signed circuits of each (arm, N) run in the order +, -, -, + (docs/notes/iqm/README.md, "Batch order"). Four arms:

- measure: a Z measurement after each rotation, outcomes recorded and never conditioning anything. A pinched qubit's
  Bloch z multiplies by cos(THETA/N) per step, so P0 = (1 + cos(THETA/N)^N)/2: 0.030 at N = 1 and 0.891 at N = 16.
- unitary (N = 16 only): the same rotations back to back with no mid-circuit operation. They compose to one rotation
  of THETA, so the ideal P0 is cos(THETA/2)^2 = 0.030. This is the mutation null. Garnet's compiler keeps the sixteen
  prx pulses separate, 40 ns per layer (results/iqm/cases/measurement-timing-probe), so it stays 16 pulses long.
- delay (every N): each mid-circuit measure replaced by a `delay` of MEASURE_WINDOW_SECONDS. It is the elapsed-time
  control. Idle time dephases the qubit, which is a partial Z measurement of its own, so its P0 rises with N without
  any measurement; the arm quantifies how much of the measure arm's Zeno effect idle dephasing alone produces.
- settle (N = 16 only): the measure arm with a `delay` of SETTLE_SECONDS = 2.0 us after each mid-circuit measure,
  several ring-down times of the readout resonator (docs/notes/ibm_quantum/heron-r2-readout-resonator.md records no
  Garnet figure; docs/notes/quantum_inspire/tuna-17.md, "Readout ring-down results", holds the repository's ring-down
  design). Where a qubit departs below its prediction, the settle gap (measured settle P0 minus the settle
  prediction at the per-step z loss the measure arm implies) within Z_DECIDE standard errors of zero is a match that
  excludes a readout tail as the cause, and at least Z_DECIDE above zero attributes part of the departure to it.
  A readout-induced frequency shift that outlasts the measure enters only during the next prx, at second order in
  delta*tau; for tau <= 100 ns and delta <= 2 pi 100 kHz it moves the N = 16 flip probability by about 2.5e-6 per
  step, so a departure larger than that bound needs this control to be read as measurement-induced.

Readout history. Every circuit, ro0 and ro1 included, waits PRE_READOUT_SECONDS = 2.0 us before its final measure,
the rule of the SETTLE_CYCLES comment in scripts/qi_readout_ringdown_cases.py: photons left in the resonator by a
preceding readout would otherwise bias the final assignment in the measure arm only, which ro0 and ro1 cannot
correct. The N = 1 measure arm against the N = 1 delay arm is the in-job diagnostic of residual readout-history
bias: both ideals are 0.0302, the models agree, and only the measure arm has a measurement before the final one. A
measurement-induced transition at N = 1 also separates the two arms (by about 0.94 eps), so a difference at or above
Z_DECIDE standard errors reads as one or the other, and the eps fit over N tells them apart.

Idle. The circuit-job body takes a native `delay` operation with a duration in seconds, at least that long and
rounded up to hardware granularity (docs/notes/iqm/docs/iqm-client/api/iqm.iqm_client.models.md, operation table and
"Delay"; docs/notes/iqm/os-4.7.md, "Client", lists `delay` in every Target). Garnet's dynamic quantum architecture
lists no `delay` gate; garnet:mock accepted it. MEASURE_WINDOW_SECONDS is the compiled duration of a mid-circuit
measure on Garnet (calibration set be070414), 1.096 us, fixed by two single-circuit QPU probe jobs (see the constant);
garnet:mock compiles 1.772 us. The QPU job's own estimate is checked against the case's predicted schedule in
`analyze`, and a difference above SCHEDULE_TOLERANCE solves the window from the QPU total before any decision (a
garnet:mock analysis reports the ratio and keeps the plan).

Initialization and T1, measured in the job. One active-reset cycle without heralding initializes the qubits. ro0 and
ro1 (prx(pi)) wait as long as every other circuit and read z = +-(1 - 2 p) through the assignment channel and the
wait, with p the initialization excitation after reset; the correction (Zobs - o)/s with o and s from the pair
returns the true z before the wait divided by (1 - 2 p). The T1 series ro1 (t = 0) and t1-004 to t1-150 (prx(pi),
`delay` t, the pre-readout delay, measure) then reads y_t = (z_eq - (z_eq + 1 - 2 p) exp(-t/T1))/(1 - 2 p) =
q (1 - exp(-t/T1)) - exp(-t/T1) with q = z_eq/(1 - 2 p), z_eq the equilibrium z, 1 - 2 times the thermal excitation of
an idle qubit. The series fixes T1 and the single combination q, so the fit assumes no thermal excitation and p enters
only through q. The model predicts the corrected z of an arm as a + b q, with a the chain's response to the initial z
and b its response to the relaxation source (corrected_z); both are recomputed at the fitted T1 and q, so the
calibrated T1 enters only the planning values in prediction.json. A calibrated T1 would put a lift above the ideal of
several departure standard errors at N = 16, and q moves the N = 16 prediction by b/(1 - 2 p), many standard
errors across p = 0 to 0.2 (prediction.json, p_init_sensitivity), so neither can rest on the calibration.

Preregistered decisions, per qubit, from the readout-corrected final P0 pooled over the four signed circuits, with
standard errors that propagate the binomial variances of every circuit group through the joint fit and correction
by the delta method:

- the mutation test passes when the N = 16 contrast measure minus unitary exceeds CONTRAST_MIN = 0.5 by at least
  Z_DECIDE = 3 standard errors;
- the departure test compares the measured N = 16 measure-arm P0 with the ideal-projective prediction at the
  fitted T1 and q (a rotation with the prx depolarizing error, an ideal pinch, then T1 relaxation toward |0> over the
  rotation layer and the measure window; T2 does not enter, because the state is diagonal after every measurement)
  and names one outcome from z = (measured - predicted)/SE, the SE including the T1 and q fit and a systematic of
  PRX_SYSTEMATIC times the calibrated prx error (a randomized-benchmarking average over other sequences):
  `departs_below` (z <= -Z_DECIDE), `exceeds_prediction` (z >= Z_DECIDE) or `consistent`;
- a qubit whose fitted readout scale lies below READOUT_CONTRAST_FLOOR makes no decision;
- the device verdicts (device_verdict) are the decisions: six qubits times about four 3-SE tests give about a 6 %
  chance of one false flag, so a device departs only when at least DEVICE_QUBITS usable qubits return `departs_below`
  or the inverse-variance pooled departure z over the usable qubits is at or below -Z_DECIDE; `exceeds_prediction`
  and the settle `tail_attributed` follow the same rule. The per-qubit verdicts stay descriptive. A shared prx
  underestimate pools coherently across qubits, so a device `departs_below` or `exceeds_prediction` counts as
  attributed to the measurement only if, on every contributing qubit, the unitary arm's N = 16 measured-minus-modeled
  difference lies within Z_DECIDE statistical standard errors (sixteen unmeasured pulses shift the unitary P0 by about
  7.5 times the prx error); otherwise its status is `gate_model_inconsistent`.

Known limit: ro1 puts every qubit in |1> at once, while the measure arm's neighbor states vary from shot to shot, so
state-dependent simultaneous-readout crosstalk is not calibrated. `analyze` reports the largest correlation of each
qubit's final outcome with another's (readout_crosstalk) as a descriptive check; the case adds no circuits for it.

The sweep subcommand (and the self-test at a reduced grid) runs the real analysis over synthetic raw measurements of
model devices off the planning point and requires every qubit to read |departure z| < 1, settle `match` and a passing
mutation test.

Descriptive outputs, deciding nothing: the settle gap, the readout-history diagnostic, the delay arm's measured and
modeled (T1 and T2) P0 per N, the delay minus unitary difference at N = 16, the per-N measure-arm deficit against
the ideal, the fit P0(N) = (1 + ((1 - 2 eps) cos(THETA/N))^N)/2 for eps per qubit (weighted least squares, no
randomness) and the same fit against the relaxed model, and the transition rate between consecutive mid-circuit
outcomes against sin(THETA/(2N))^2.

The case draws no random number; it holds no seed.

Usage: "$PYTHON" scripts/iqm_measurement_sequence.py (build DIR [--calibration-dir DIR] | check DIR
       | analyze RUN_DIR --out FILE [--replay] [--mock] | sweep [--reduced] | --self-test)
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import statistics
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import minimize_scalar

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
from iqm_jobs import CANCEL_MARGIN, CASE_SCHEMA, JOB_SECONDS, dump, run_facts  # noqa: E402
from iqm_platform import sha256  # noqa: E402

from parallel import ordered_map  # noqa: E402

CASE = "measurement-sequence-pinching"
QC = "garnet"
QCS = ["garnet:mock", "garnet"]
JOB = "pinching"
CALIBRATION_DIR = ROOT / "docs/evidence/iqm/qc/garnet/calibration"
EXCERPT = "calibration/excerpt.json"
OPTIONS: dict[str, Any] = {"heralding_mode": "none", "active_reset_cycles": 1}

THETA = 8 * math.pi / 9
STEPS = (1, 2, 4, 8, 16)
TOP_STEPS = 16
SIGNS = (1, -1, -1, 1)
ARMS = ("measure", "delay", "unitary", "settle")
ARM_STEPS = {"measure": STEPS, "delay": STEPS, "unitary": (TOP_STEPS,), "settle": (TOP_STEPS,)}
PINCHED_ARMS = ("measure", "settle")
# Idle after each mid-circuit measure of the settle arm, and before every final measure: several ring-down times of
# a readout resonator whose ring-down is a few hundred ns (the SETTLE_CYCLES rule of qi_readout_ringdown_cases.py).
SETTLE_SECONDS = 2.0e-6
PRE_READOUT_SECONDS = 2.0e-6
# The T1 series: prx(pi), a delay t, the pre-readout delay, measure. ro1 is its t = 0 point. The 100 and 150 us
# points anchor the fit's asymptote, which 60 us does not reach for a T1 of 25 to 60 us.
T1_DELAYS = (4e-6, 10e-6, 20e-6, 40e-6, 60e-6, 100e-6, 150e-6)
QUBIT_COUNT = 6
FINAL_KEY = "f"
# Compiled schedule of Garnet on calibration set be070414: the qpu_execution estimate per shot, the job's
# execution_runtime_estimate_seconds less the fixed 1.6 s over 100 shots, of two single-circuit probe jobs of this
# case's own circuits on QB5, QB7, QB11, QB14, QB17 and QB19, each with the 2 us pre-readout delay
# (results/iqm/cases/measurement-window-qpu-probe):
#   unitary-n16 01a174be-d1f7-75fc-b324-d27d7133409b   7.032 us -> 7.032 - 2.0 = 5.032 us of base and layers
#   measure-n16 01a174be-e68b-776e-8241-8bb3d259ae57  24.568 us -> (24.568 - 7.032)/16 = 1.096 us per measure
# The per-circuit base is the 4.344 us of the retained active-reset pilot job (2026-10-22T212742Z, two circuits
# summing to 8.688 us), which leaves (5.032 - 4.344)/16 = 43 ns per prx layer, consistent with the 40 ns that
# garnet:mock compiles. The mock compiles a different measure window (1.772 us) and base (8.684 us per circuit):
# five mock probes (results/iqm/cases/measurement-timing-probe, jobs 01a1747a-dd17-76ae-abf5-cb2840e5bdbd, -74f4-,
# -9d43-, -d133-, -ab9e-) gave 8.684, 9.324, 37.676, 10.496 and 25.708 us per shot. A timing taken from the mock
# needs a QPU check.
ESTIMATOR_BASE_SECONDS = 4.344e-6
PRX_LAYER_SECONDS = 40e-9
MEASURE_WINDOW_SECONDS = 1.096e-6
MOCK_MEASURE_WINDOW_SECONDS = 1.772e-6
DELAY_SECONDS = MEASURE_WINDOW_SECONDS
# A QPU job whose compiled schedule differs from the predicted one by more than this fraction solves the measure
# window from its own total before any decision.
SCHEDULE_TOLERANCE = 0.01

SHOTS = 3000
# Execution seconds of a retained active-reset Garnet QPU job = its compiled schedule (the record's
# execution_runtime_estimate_seconds less the fixed 1.6 s) + EXECUTION_FIXED_SECONDS
# + EXECUTION_PER_CIRCUIT_SHOT_SECONDS per circuit-shot, a least-squares fit over seven jobs with residuals of at
# most EXECUTION_FIT_RESIDUAL_SECONDS:
#   01a16583-43fc-75e5-82b0-5b192921a4c5  01a16630-b928-72d1-b66e-b7779c623df5  01a16631-2b7c-7668-a276-3341e9d17bdd
#   01a167ac-58d4-74f0-96fe-9af62e1f1dfe  01a167ac-e6f3-711a-a9be-86bb8bfe89f9  01a167ac-ec22-7645-b50d-74b793ed808d
#   01a1707f-6157-75dc-aca8-6f30e5f0280b
# Runtime exceeded execution by 0.04 to 0.411 s on them, and billing is ceil(runtime) with no fixed term.
EXECUTION_FIXED_SECONDS = 0.141
EXECUTION_PER_CIRCUIT_SHOT_SECONDS = 7.967e-6
EXECUTION_FIT_RESIDUAL_SECONDS = 0.17
RUNTIME_OVER_EXECUTION_SECONDS = 0.42
# collect cancels a run once its runtime comes within iqm_jobs.CANCEL_MARGIN of the seconds max_credits buys, so the
# worst-case runtime stays at least RUNTIME_MARGIN_SECONDS below that threshold.
MAX_CREDITS = {"garnet": 5.0, "garnet:mock": 0.0}
PRICE = {"garnet": 0.5, "garnet:mock": 0.0}
RUNTIME_MARGIN_SECONDS = 1.0
GARNET_MAX_CIRCUITS = 100
GARNET_MAX_INSTRUCTIONS = 10000

Z_DECIDE = 3.0
# A qubit whose fitted readout scale lies below this floor makes no decision: correction divides by the scale, so its
# corrected P0 and standard errors diverge as it approaches zero.
READOUT_CONTRAST_FLOOR = 0.5
CONTRAST_MIN = 0.5
# README, "Reset": one active-reset cycle leaves a qubit about 6.8 % excited; only the planning values assume it.
ACTIVE_RESET_EXCITED = 0.068
PLANNING_Q = 1 / (1 - 2 * ACTIVE_RESET_EXCITED)
P_INIT_SENSITIVITY = (0.0, 0.05, 0.1, 0.15, 0.2)
# The prx error enters every prediction and the RB value is an average over other sequences, so its relative one-sigma
# uncertainty is carried as a systematic in every standard error.
PRX_SYSTEMATIC = 1.0
# A device departs when this many usable qubits return the same per-qubit verdict (or the pooled z does).
DEVICE_QUBITS = 2
# Deterministic stand-ins for independent shot orderings of the six qubits in a synthetic run (coprime to 3000).
SHOT_PERMUTATIONS = (7, 11, 13, 17, 19, 23)
WINDOW_GRID = (0.6e-6, 0.8e-6, MEASURE_WINDOW_SECONDS, 1.4e-6, MOCK_MEASURE_WINDOW_SECONDS)
FIT_GRID = [-0.05 + 0.0005 * i for i in range(1001)]
T1_BOUNDS = (1e-6, 1e-3)


def ideal_measure(n: int) -> float:
    """Final P0 of the pinched chain of n rotations of THETA/n."""
    return (1 + math.cos(THETA / n) ** n) / 2


def ideal_delay() -> float:
    """Final P0 of the coherent chain, which composes to one rotation of THETA."""
    return (1 + math.cos(THETA)) / 2


def ideal_arm(arm: str, n: int) -> float:
    return ideal_measure(n) if arm in PINCHED_ARMS else ideal_delay()


def ideal_flip(n: int) -> float:
    """Probability that consecutive mid-circuit outcomes differ: a pinched qubit rotates by THETA/n."""
    return math.sin(THETA / (2 * n)) ** 2


def model_p0(n: int, eps: float) -> float:
    return (1 + math.pow((1 - 2 * eps) * math.cos(THETA / n), n)) / 2


def sign_tag(sign: int) -> str:
    return "p" if sign > 0 else "m"


def group_names(arm: str, n: int) -> list[str]:
    return [f"{arm}-n{n}-s{i}{sign_tag(s)}" for i, s in enumerate(SIGNS)]


def t1_name(delay: float) -> str:
    return f"t1-{round(delay * 1e6):03d}"


T1_NAMES = tuple(t1_name(t) for t in T1_DELAYS)
SERIES_NAMES = ("ro1", *T1_NAMES)
SERIES_DELAYS = (0.0, *T1_DELAYS)
RO_NAMES = ("ro0", "ro1", *T1_NAMES)


def op(name: str, locus: list[str], **args: Any) -> dict[str, Any]:
    return {"name": name, "locus": locus, "args": args}


def prx_layer(qubits: list[str], angle: float) -> list[dict[str, Any]]:
    return [op("prx", [q], angle=angle, phase=0.0) for q in qubits]


def finish(name: str, qubits: list[str], instructions: list[dict[str, Any]]) -> dict[str, Any]:
    """The circuit with its pre-readout delay and final measure."""
    instructions = [
        *instructions,
        op("delay", qubits, duration=PRE_READOUT_SECONDS),
        op("measure", qubits, key=FINAL_KEY),
    ]
    return {"name": name, "instructions": instructions}


def circuit(name: str, qubits: list[str], arm: str, n: int, sign: int, idle: float = DELAY_SECONDS) -> dict[str, Any]:
    """n rotations of sign*THETA/n on every qubit, each followed by a keyed measure (measure, settle arms), a delay
    (delay arm) or nothing (unitary arm); the settle arm adds its idle after the measure."""
    instructions: list[dict[str, Any]] = []
    for step in range(n):
        instructions += prx_layer(qubits, sign * THETA / n)
        if arm in PINCHED_ARMS:
            instructions.append(op("measure", qubits, key=f"m{step}"))
        if arm == "settle":
            instructions.append(op("delay", qubits, duration=SETTLE_SECONDS))
        elif arm == "delay":
            instructions.append(op("delay", qubits, duration=idle))
    return finish(name, qubits, instructions)


def ro_circuit(name: str, qubits: list[str]) -> dict[str, Any]:
    """ro0 reads the initialized state; ro1 and the t1 circuits flip it and wait before the readout."""
    if name == "ro0":
        return finish(name, qubits, [])
    wait = 0.0 if name == "ro1" else T1_DELAYS[T1_NAMES.index(name)]
    instructions = prx_layer(qubits, math.pi)
    if wait:
        instructions.append(op("delay", qubits, duration=wait))
    return finish(name, qubits, instructions)


def circuits_of(qubits: list[str]) -> list[dict[str, Any]]:
    """The job's circuit list: per N the measure group beside the delay group (and at N = 16 the unitary and settle
    groups), then ro0, ro1 and the T1 series."""
    out: list[dict[str, Any]] = []
    for n in STEPS:
        for arm in ARMS:
            if n in ARM_STEPS[arm]:
                out += [circuit(name, qubits, arm, n, s) for name, s in zip(group_names(arm, n), SIGNS, strict=True)]
    out += [ro_circuit(name, qubits) for name in RO_NAMES]
    return out


def qubits_of(c: dict[str, Any]) -> list[str]:
    return list(c["instructions"][-1]["locus"])


def mid_seconds(c: dict[str, Any]) -> float:
    """Time of the operations between the first rotation and the final measure that are not rotations: a measure at
    the compiled window, a delay at its duration."""
    return sum(
        MEASURE_WINDOW_SECONDS if o["name"] == "measure" else o["args"]["duration"]
        for o in c["instructions"][:-1]
        if o["name"] in ("measure", "delay")
    )


def layers_of(c: dict[str, Any]) -> int:
    first = qubits_of(c)[0]
    return sum(1 for o in c["instructions"] if o["name"] == "prx" and o["locus"] == [first])


def mid_measures(c: dict[str, Any]) -> int:
    return sum(1 for o in c["instructions"][:-1] if o["name"] == "measure")


def estimator_shot_seconds(c: dict[str, Any], window: float = MEASURE_WINDOW_SECONDS) -> float:
    """The compiler's qpu_execution estimate per shot: the ro0 shot, the rotation layers, the delays and each
    mid-circuit measure at the window."""
    delays = sum(o["args"]["duration"] for o in c["instructions"][:-1] if o["name"] == "delay")
    return ESTIMATOR_BASE_SECONDS + layers_of(c) * PRX_LAYER_SECONDS + delays + mid_measures(c) * window


def solve_window(circuits: list[dict[str, Any]], shots: int, estimated_seconds: float) -> float:
    """The measure window at which the estimator's total over the circuits equals a job's compiled schedule."""
    fixed = sum(estimator_shot_seconds(c, 0.0) for c in circuits)
    measures = sum(mid_measures(c) for c in circuits)
    return (estimated_seconds / shots - fixed) / measures


def billing(circuits: list[dict[str, Any]], shots: int) -> dict[str, Any]:
    """The predicted execution and worst-case runtime of the job from the fit over retained QPU jobs."""
    schedule = shots * sum(estimator_shot_seconds(c) for c in circuits)
    execution = schedule + EXECUTION_FIXED_SECONDS + EXECUTION_PER_CIRCUIT_SHOT_SECONDS * len(circuits) * shots
    worst = execution + EXECUTION_FIT_RESIDUAL_SECONDS + RUNTIME_OVER_EXECUTION_SECONDS
    threshold = MAX_CREDITS[QC] / PRICE[QC] - CANCEL_MARGIN
    return {
        "shots": shots,
        "circuits": len(circuits),
        "compiled_schedule_seconds": schedule,
        "execution_seconds": execution,
        "worst_case_runtime_seconds": worst,
        "billed_seconds": math.ceil(worst),
        "credits": math.ceil(worst) * PRICE[QC],
        "cancel_threshold_seconds": threshold,
        "cancel_margin_seconds": threshold - worst,
    }


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def select_qubits(
    characterization: dict[str, float], architecture: dict[str, Any], count: int = QUBIT_COUNT
) -> tuple[list[str], dict[str, Any]]:
    """Greedy choice by smallest e01 + e10 among the qubits whose T1 is at least the set's median, skipping any qubit
    that shares a cz coupler with one already chosen."""
    names = list(architecture["qubits"])
    t1 = {q: characterization[f"characterization.model.{q}.t1_time"] for q in names}
    error = {
        q: characterization[f"metrics.ssro.measure.constant.{q}.error_0_to_1"]
        + characterization[f"metrics.ssro.measure.constant.{q}.error_1_to_0"]
        for q in names
    }
    median = statistics.median(t1.values())
    coupled = {
        frozenset(locus) for impl in architecture["gates"]["cz"]["implementations"].values() for locus in impl["loci"]
    }
    chosen: list[str] = []
    for q in sorted((q for q in names if t1[q] >= median), key=lambda q: (error[q], int(q[2:]))):
        if all(frozenset((q, c)) not in coupled for c in chosen):
            chosen.append(q)
        if len(chosen) == count:
            break
    if len(chosen) < count:
        raise ValueError(f"only {len(chosen)} uncoupled qubits with T1 at least the median {median}")
    rule = (
        f"the {count} qubits of smallest e01 + e10 among those with T1 at least the set's median, taken in that order "
        "and skipping any that shares a cz coupler with one already taken"
    )
    return sorted(chosen, key=lambda q: int(q[2:])), {"rule": rule, "median_t1_s": median}


def excerpt_of(calibration_dir: Path) -> dict[str, Any]:
    """The calibration facts the case rests on, from a set, its metrics and its architecture that describe one
    calibration set: the selected qubits with their T1, T2, readout errors and measure timing."""
    paths = {name: calibration_dir / name for name in ("set.json", "metrics.json", "dynamic-quantum-architecture.json")}
    calibration_set, metrics, architecture = (load_json(p) for p in paths.values())
    identity = calibration_set["observation_set_id"]
    if metrics.get("describes_id") != identity or architecture.get("calibration_set_id") != identity:
        raise ValueError(f"{calibration_dir}: the set, metrics and architecture do not all describe set {identity}")
    values = {o["dut_field"]: o["value"] for o in calibration_set["observations"] if not o.get("invalid")}
    characterization = {o["dut_field"]: o["value"] for o in metrics["observations"] if not o.get("invalid")}
    chosen, selection = select_qubits(characterization, architecture)
    per_qubit: dict[str, Any] = {}
    for q in chosen:
        gate = f"gates.measure.constant.{q}"
        per_qubit[q] = {
            "t1_s": characterization[f"characterization.model.{q}.t1_time"],
            "t2_s": characterization[f"characterization.model.{q}.t2_time"],
            "prx_p": 2 * (1 - characterization[f"metrics.rb.prx.drag_crf_sx.{q}.fidelity:par=d2"]),
            "e01": characterization[f"metrics.ssro.measure.constant.{q}.error_0_to_1"],
            "e10": characterization[f"metrics.ssro.measure.constant.{q}.error_1_to_0"],
            "probe_duration_s": values[f"{gate}.duration"],
            "acquisition_delay_s": values[f"{gate}.acquisition_delay"],
            "integration_length_s": values[f"{gate}.integration_length"],
        }
    cz_loci = [
        tuple(locus) for impl in architecture["gates"]["cz"]["implementations"].values() for locus in impl["loci"]
    ]
    coupled = sorted(f"{a}-{b}" for a, b in cz_loci if a in chosen and b in chosen)
    return {
        "schema": "iqm-measurement-sequence-calibration-v2",
        "calibration_set": identity,
        "source_sha256": {name: sha256(p.read_bytes()) for name, p in paths.items()},
        "selection": selection,
        "couplers_among_qubits": coupled,
        "qubits": per_qubit,
    }


def acquisition_ps(excerpt: dict[str, Any]) -> int:
    """The longest acquisition_delay + integration_length of the qubits, rounded up to the 4 ns channel granularity;
    the compiled measure window exceeds it and is not derived from it."""
    longest = max(
        round((q["acquisition_delay_s"] + q["integration_length_s"]) * 1e12) for q in excerpt["qubits"].values()
    )
    return -(-longest // 4000) * 4000


def tau_of(arm: str, window: float, idle: float = DELAY_SECONDS) -> float:
    """Relaxation time per step: the rotation layer plus the measure window, the delay, or nothing."""
    extra = {"measure": window, "settle": window + SETTLE_SECONDS, "delay": idle, "unitary": 0.0}[arm]
    return PRX_LAYER_SECONDS + extra


def bloch_z(
    arm: str,
    n: int,
    t1: float,
    t2: float,
    tau: float,
    eps: float = 0.0,
    z0: float = 1.0,
    gate_p: float = 0.0,
    z_eq: float = 1.0,
) -> float:
    """Bloch z of the chain from z0 with T1 and Ramsey T2 relaxation over tau per step, just before the pre-readout
    delay.

    Each step rotates by THETA/n about X, then pinches (the pinched arms zero the transverse part and lose a
    fraction eps of z to transitions) or leaves the state coherent (delay and unitary arms), then relaxes for tau.
    A pinched arm's state is diagonal, so t2 never reaches its result. The pre-readout delay is not iterated here:
    relaxation over it is affine in z, so ro0 and ro1, which wait as long, calibrate it away exactly (the composite
    of relaxation and assignment is one affine map of the z before the wait). z_eq is the equilibrium z the
    relaxation approaches, 1 - 2 times the thermal excitation of an idle qubit.
    """
    y, z = 0.0, z0
    c, s = math.cos(THETA / n), math.sin(THETA / n)
    for _ in range(n):
        y, z = (y * c - z * s) * (1 - gate_p), (y * s + z * c) * (1 - gate_p)
        if arm in PINCHED_ARMS:
            y = 0.0
            z *= 1 - 2 * eps
        y *= math.exp(-tau / t2)
        z = z_eq - (z_eq - z) * math.exp(-tau / t1)
    return z


def corrected_z(arm: str, n: int, t1: float, t2: float, tau: float, eps: float, gate_p: float, q: float) -> float:
    """The z that ro0/ro1 correction recovers on the relaxing model: a + b q, with a the chain's response to the
    initial z and b its response to the relaxation source, both at unit strength.

    A true z of z0 = 1 - 2 p before the wait is divided by the scale (1 - 2 p) that ro0 and ro1 measure, so the
    initial state enters through q alone, and q = z_eq/(1 - 2 p) is the single combination the T1 series fixes:
    its asymptote is z_eq/(1 - 2 p), whatever the thermal excitation of an idle qubit.
    """
    b = bloch_z(arm, n, t1, t2, tau, eps, 0.0, gate_p)
    return bloch_z(arm, n, t1, t2, tau, eps, 1.0, gate_p) - b + b * q


def model_tables(
    t1: float, t2: float, q: float, window: float, gate_p: float, idle: float = DELAY_SECONDS
) -> dict[str, Any]:
    """P0 per arm and N the readout correction recovers on the ideal-projective, relaxing model, for the series
    parameter q (1/(1 - 2 p) for an initialization excitation p and a cold idle qubit)."""
    t2 = min(t2, 2 * t1)
    return {
        arm: {
            str(n): (1 + corrected_z(arm, n, t1, t2, tau_of(arm, window, idle), 0.0, gate_p, q)) / 2
            for n in ARM_STEPS[arm]
        }
        for arm in ARMS
    }


def implied_loss(z_corrected: float, t1: float, t2: float, window: float, q: float, gate_p: float) -> float:
    """The per-step z loss eps at which the measure arm's modeled corrected z equals z_corrected (bisection)."""
    low, high = -0.05, 0.5
    tau = tau_of("measure", window)
    for _ in range(50):
        middle = (low + high) / 2
        if corrected_z("measure", TOP_STEPS, t1, t2, tau, middle, gate_p, q) > z_corrected:
            low = middle
        else:
            high = middle
    return (low + high) / 2


def var(k: float, n: int) -> float:
    """Binomial variance of k/n, from the Agresti-Coull-shifted proportion so that k = 0 or k = n keeps a spread."""
    p = (k + 1) / (n + 2)
    return p * (1 - p) / n


def fit_t1(y: list[float], weights: list[float]) -> tuple[float, float]:
    """T1 and q = 1/(1 - 2 p) from the corrected series y_k at the delays T1_DELAYS.

    The excited state after the pi pulse survives with (1 - p) exp(-t/T1) and ro0 and ro1 divide the corrected z by
    (1 - 2 p): y_k = (1 - 2 (1 - p) e_k)/(1 - 2 p) = q (1 - e_k) - e_k with e_k = exp(-t_k/T1). At a given T1 the
    weighted least squares for q is closed, and a bounded search over log T1 minimizes the residual.
    """
    delays = np.array(T1_DELAYS)
    ys = np.array(y)
    w = np.array(weights)

    def solve(u: float) -> tuple[float, float]:
        e = np.exp(-delays / math.exp(u))
        q = float(np.sum(w * (1 - e) * (ys + e)) / np.sum(w * (1 - e) ** 2))
        return q, float(np.sum(w * (ys + e - q * (1 - e)) ** 2))

    best = minimize_scalar(
        lambda u: solve(u)[1],
        bounds=(math.log(T1_BOUNDS[0]), math.log(T1_BOUNDS[1])),
        method="bounded",
        options={"xatol": 1e-10},
    )
    return math.exp(float(best.x)), solve(float(best.x))[0]


def propagate_many(
    f: Callable[[list[float]], dict[str, float]], x: list[float], variances: list[float], step: float = 1e-5
) -> tuple[dict[str, float], dict[str, float]]:
    """f(x) and the standard error of each of its outputs from independent input variances, by the delta method with
    central differences."""
    base = f(x)
    totals = dict.fromkeys(base, 0.0)
    for i, v in enumerate(variances):
        up, down = list(x), list(x)
        up[i] += step
        down[i] -= step
        high, low = f(up), f(down)
        for key in totals:
            totals[key] += ((high[key] - low[key]) / (2 * step)) ** 2 * v
    return base, {key: math.sqrt(t) for key, t in totals.items()}


def finite(x: float) -> float | None:
    return x if math.isfinite(x) else None


def fit_eps(points: list[tuple[int, float, float]], law: Callable[[int, float], float] = model_p0) -> dict[str, Any]:
    """Weighted least squares of P0(N) = law(N, eps) over (N, P0, se): grid, golden section, curvature."""

    def chi2(eps: float) -> float:
        return sum(((p - law(n, eps)) / se) ** 2 for n, p, se in points)

    best = min(range(len(FIT_GRID)), key=lambda i: chi2(FIT_GRID[i]))
    low, high = FIT_GRID[max(best - 1, 0)], FIT_GRID[min(best + 1, len(FIT_GRID) - 1)]
    ratio = (math.sqrt(5) - 1) / 2
    for _ in range(100):
        a, b = high - ratio * (high - low), low + ratio * (high - low)
        low, high = (low, b) if chi2(a) < chi2(b) else (a, high)
    eps = (low + high) / 2
    h = 1e-4
    curvature = (chi2(eps + h) - 2 * chi2(eps) + chi2(eps - h)) / h**2
    return {
        "eps": eps,
        "eps_se": finite(math.sqrt(2 / curvature)) if curvature > 0 else None,
        "chi2": chi2(eps),
        "dof": len(points) - 1,
        "at_grid_edge": best in (0, len(FIT_GRID) - 1),
    }


def classify_departure(z: float) -> str:
    """The departure test's three outcomes from z = (measured - predicted)/SE."""
    if z <= -Z_DECIDE:
        return "departs_below"
    if z >= Z_DECIDE:
        return "exceeds_prediction"
    return "consistent"


def decide(contrast: float, contrast_se: float, difference: float, difference_se: float) -> dict[str, Any]:
    """The two preregistered decisions of one qubit: the measure-minus-unitary contrast against CONTRAST_MIN, and the
    measure arm's N = 16 P0 against the ideal-projective prediction (measured minus predicted)."""
    if contrast_se <= 0 or difference_se <= 0:
        raise ValueError("a decision needs positive standard errors")
    z_mutation = (contrast - CONTRAST_MIN) / contrast_se
    z_departure = difference / difference_se
    return {
        "mutation_test": {"z": z_mutation, "passes": z_mutation >= Z_DECIDE},
        "departure": {"z": z_departure, "outcome": classify_departure(z_departure)},
    }


def pooled(counts: dict[str, Any], qubit: str, names: list[str]) -> list[int]:
    total = [0, 0]
    for name in names:
        for i, value in enumerate(counts[name]["final"][qubit]):
            total[i] += value
    return total


def pooled_two_state(counts: dict[str, Any], qubit: str, names: list[str]) -> tuple[int, int]:
    """(ones, shots) of the named circuits."""
    n0, n1 = pooled(counts, qubit, names)
    return n1, n0 + n1


def group_keys() -> list[tuple[str, int]]:
    return [(arm, n) for arm in ARMS for n in ARM_STEPS[arm]]


def observations(counts: dict[str, Any], qubit: str) -> dict[str, tuple[int, int]]:
    """(ones, shots) per circuit group of one qubit: each arm and N pooled over its signed circuits, ro0, ro1 and
    the T1 series."""
    obs = {f"{arm}-{n}": pooled_two_state(counts, qubit, group_names(arm, n)) for arm, n in group_keys()}
    for name in RO_NAMES:
        obs[name] = pooled_two_state(counts, qubit, [name])
    return obs


def quantities(p: dict[str, float], ctx: dict[str, Any]) -> dict[str, float]:
    """Every figure the decisions and reports use, as a function of the P(1) of each circuit group.

    ro0 and ro1 (both after the pre-readout wait) fix the readout offset and the scale, which include the
    initialization excitation; the T1 series then fixes T1 and that excitation; the model tables are recomputed at
    the fitted values, so their uncertainty propagates with the measurement's.
    """
    z0obs, z1obs = 1 - 2 * p["ro0"], 1 - 2 * p["ro1"]
    scale, offset = (z0obs - z1obs) / 2, (z0obs + z1obs) / 2

    def corrected(key: str) -> float:
        return ((1 - 2 * p[key]) - offset) / scale

    t1, q = fit_t1([corrected(name) for name in T1_NAMES], ctx["weights"])
    p_init = (1 - 1 / q) / 2
    window = ctx["window_s"]
    gate_p = p["prx_p"]
    t2 = min(ctx["t2_s"], 2 * t1)
    tables = model_tables(t1, ctx["t2_s"], q, window, gate_p)
    out: dict[str, float] = {"t1_s": t1, "q": q, "p_init": p_init, "scale": scale, "offset": offset}
    for arm, n in group_keys():
        key = f"{arm}-{n}"
        out[f"p0:{key}"] = (1 + corrected(key)) / 2
        out[f"model:{key}"] = tables[arm][str(n)]
        out[f"diff:{key}"] = out[f"p0:{key}"] - out[f"model:{key}"]
    top = str(TOP_STEPS)
    out["contrast"] = out[f"p0:measure-{top}"] - out[f"p0:unitary-{top}"]
    out["dephasing"] = out[f"p0:delay-{top}"] - out[f"p0:unitary-{top}"]
    out["dephasing_modeled"] = out[f"model:delay-{top}"] - out[f"model:unitary-{top}"]
    out["history"] = out["p0:measure-1"] - out["p0:delay-1"]
    out["history_modeled"] = out["model:measure-1"] - out["model:delay-1"]
    loss = implied_loss(2 * out[f"p0:measure-{top}"] - 1, t1, t2, window, q, gate_p)
    settle = corrected_z("settle", TOP_STEPS, t1, t2, tau_of("settle", window), loss, gate_p, q)
    out["implied_loss"] = loss
    out["tail_gap"] = out[f"p0:settle-{top}"] - (1 + settle) / 2
    return out


def evaluate_qubit(item: tuple[str, dict[str, Any], dict[str, Any]]) -> dict[str, Any]:
    """The decisions and descriptive outputs of one qubit from the per-circuit counts and its context: the
    calibrated T2 (for the delay and unitary models), the measure window and the planning P0 tables."""
    qubit, counts, ctx = item
    obs = observations(counts, qubit)
    keys = [*obs, "prx_p"]
    x = [*(k / n for k, n in obs.values()), ctx["prx_p"]]
    variances = [*(var(k, n) for k, n in obs.values()), (PRX_SYSTEMATIC * ctx["prx_p"]) ** 2]
    index = {key: i for i, key in enumerate(keys)}
    scale = x[index["ro1"]] - x[index["ro0"]]
    ctx = {**ctx, "weights": [scale**2 / (4 * variances[index[name]]) for name in T1_NAMES]}
    readout = {"scale": scale, "offset": 1 - x[index["ro0"]] - x[index["ro1"]]}
    if not scale >= READOUT_CONTRAST_FLOOR:
        return {
            "readout": readout,
            "usable": False,
            "reason": f"readout scale {scale:.4f} lies below the {READOUT_CONTRAST_FLOOR} floor",
        }
    value, se = propagate_many(lambda xs: quantities(dict(zip(keys, xs, strict=True)), ctx), x, variances)
    top = str(TOP_STEPS)
    p0: dict[str, dict[str, Any]] = {arm: {} for arm in ARMS}
    for arm, n in group_keys():
        key = f"{arm}-{n}"
        p0[arm][str(n)] = {
            "p0": value[f"p0:{key}"],
            "se": se[f"p0:{key}"],
            "ideal": ideal_arm(arm, n),
            "modeled": value[f"model:{key}"],
            "measured_minus_modeled": value[f"diff:{key}"],
            "measured_minus_modeled_se": se[f"diff:{key}"],
            "planning": ctx["planning"][arm][str(n)],
        }
    # In-job check of the gate model: sixteen unmeasured pulses shift the unitary arm's P0 by about 7.5 times the prx
    # error, and a shared randomized-benchmarking underestimate moves every qubit the same way. The check uses the
    # statistical standard error alone, since the prx systematic would hide the very error it asks about.
    unitary_key = f"unitary-{top}"
    shifted = list(x)
    shifted[index["prx_p"]] += 1e-5
    lowered = list(x)
    lowered[index["prx_p"]] -= 1e-5
    slope = (
        quantities(dict(zip(keys, shifted, strict=True)), ctx)[f"diff:{unitary_key}"]
        - quantities(dict(zip(keys, lowered, strict=True)), ctx)[f"diff:{unitary_key}"]
    ) / 2e-5
    statistical = math.sqrt(max(se[f"diff:{unitary_key}"] ** 2 - (slope * PRX_SYSTEMATIC * ctx["prx_p"]) ** 2, 0.0))
    gate_check = {
        "difference": value[f"diff:{unitary_key}"],
        "se": se[f"diff:{unitary_key}"],
        "statistical_se": statistical,
        "z": value[f"diff:{unitary_key}"] / statistical if statistical > 0 else math.inf,
    }
    key = f"measure-{top}"
    decisions = decide(value["contrast"], se["contrast"], value[f"diff:{key}"], se[f"diff:{key}"])
    gap_z = value["tail_gap"] / se["tail_gap"]
    history_z = value["history"] / se["history"]
    t1, p_init, q = value["t1_s"], value["p_init"], value["q"]
    t2 = min(ctx["t2_s"], 2 * t1)
    tau = tau_of("measure", ctx["window_s"])
    relaxed = fit_eps(
        [(n, value[f"p0:measure-{n}"], se[f"p0:measure-{n}"]) for n in STEPS],
        lambda n, eps: (1 + corrected_z("measure", n, t1, t2, tau, eps, ctx["prx_p"], q)) / 2,
    )
    transitions: dict[str, Any] = {}
    for n in STEPS[1:]:
        flips = sum(counts[name]["flips"][qubit][0] for name in group_names("measure", n))
        pairs = sum(counts[name]["flips"][qubit][1] for name in group_names("measure", n))
        transitions[str(n)] = {"rate": flips / pairs, "se": math.sqrt(var(flips, pairs)), "ideal": ideal_flip(n)}
    return {
        "readout": readout,
        "usable": True,
        "fitted": {
            "t1_s": t1,
            "t1_se": se["t1_s"],
            "q": q,
            "p_init": p_init,
            "p_init_se": se["p_init"],
            "scale": value["scale"],
            "scale_se": se["scale"],
            "offset": value["offset"],
        },
        "p0": p0,
        "contrast_n16": {
            "contrast": value["contrast"],
            "se": se["contrast"],
            "ideal": ideal_measure(TOP_STEPS) - ideal_delay(),
        },
        "departure_n16": {
            "prediction": value[f"model:{key}"],
            "measured": value[f"p0:{key}"],
            "difference": value[f"diff:{key}"],
            "se": se[f"diff:{key}"],
        },
        "decisions": decisions,
        "gate_check_n16": gate_check,
        "settle_n16": {
            "raw_difference": value[f"p0:settle-{top}"] - value[f"p0:measure-{top}"],
            "measure_implied_loss": value["implied_loss"],
            "tail_gap": value["tail_gap"],
            "se": se["tail_gap"],
            "z": gap_z,
            "verdict": "tail_attributed"
            if gap_z >= Z_DECIDE
            else "match"
            if abs(gap_z) < Z_DECIDE
            else "settle_below_measure",
        },
        "readout_history_n1": {
            "measure_minus_delay": value["history"],
            "se": se["history"],
            "modeled": value["history_modeled"],
            "z": history_z,
            "verdict": "bias_detected" if abs(history_z) >= Z_DECIDE else "none",
        },
        "delay_arm": {
            "dephasing_zeno_n16": {
                "measured": value["dephasing"],
                "se": se["dephasing"],
                "modeled": value["dephasing_modeled"],
            }
        },
        "fit": fit_eps([(n, value[f"p0:measure-{n}"], se[f"p0:measure-{n}"]) for n in STEPS]),
        "fit_relaxed": relaxed,
        "transitions": transitions,
    }


def evaluate(counts: dict[str, Any], contexts: dict[str, Any]) -> dict[str, Any]:
    qubits = list(contexts)
    results = ordered_map(evaluate_qubit, [(q, counts, contexts[q]) for q in qubits], min_items=2)
    return dict(zip(qubits, results, strict=True))


def contexts_of(prediction: dict[str, Any], window: float | None = None) -> dict[str, Any]:
    """Per qubit the context evaluate needs from a prediction: the calibrated T2, the window and the planning P0."""
    used = prediction["measure_window_seconds"] if window is None else window
    return {
        q: {"t2_s": row["inputs"]["t2_s"], "prx_p": row["inputs"]["prx_p"], "window_s": used, "planning": row["p0"]}
        for q, row in prediction["qubits"].items()
    }


def tally(circuits: list[dict[str, Any]], results: list[dict[str, Any]]) -> dict[str, Any]:
    """Per circuit name: shots, the final readout's counts of states 0 and 1 per qubit, and for circuits with
    mid-circuit measures the shots whose consecutive mid-circuit outcomes differ, summed over its consecutive pairs,
    per qubit."""
    out: dict[str, Any] = {}
    for c, result in zip(circuits, results, strict=True):
        qubits = qubits_of(c)
        final = result[FINAL_KEY]
        row: dict[str, Any] = {"shots": len(final), "final": {}}
        for position, qubit in enumerate(qubits):
            counts = [0, 0]
            for shot in final:
                if shot[position] not in (0, 1):
                    raise ValueError(f"{c['name']}: outcome {shot[position]} is not a state 0 or 1")
                counts[shot[position]] += 1
            row["final"][qubit] = counts
        mids = [o["args"]["key"] for o in c["instructions"] if o["name"] == "measure" and o["args"]["key"] != FINAL_KEY]
        if len(mids) > 1:
            row["flips"] = {}
            for position, qubit in enumerate(qubits):
                flips = sum(
                    1
                    for a, b in zip(mids, mids[1:], strict=False)
                    for x, y in zip(result[a], result[b], strict=True)
                    if x[position] != y[position]
                )
                row["flips"][qubit] = [flips, len(final) * (len(mids) - 1)]
        out[c["name"]] = row
    return out


def device_model(cal: dict[str, Any], **over: Any) -> dict[str, Any]:
    """A model device from one qubit's calibration, with fields overridden: t1_s, t2_s, p_init, eps (z lost per step
    to measurement transitions), eps_settle (None follows eps), p_thermal (the idle qubit's thermal excitation), prx_p,
    e01, e10 and window_s."""
    model = {
        "t1_s": cal["t1_s"],
        "t2_s": cal["t2_s"],
        "prx_p": cal["prx_p"],
        "e01": cal["e01"],
        "e10": cal["e10"],
        "p_init": ACTIVE_RESET_EXCITED,
        "p_thermal": 0.0,
        "eps": 0.0,
        "eps_settle": None,
        "window_s": MEASURE_WINDOW_SECONDS,
    }
    model.update(over)
    return model


def z_eq(model: dict[str, Any]) -> float:
    """The equilibrium z of a model device's relaxation."""
    return 1 - 2 * model["p_thermal"]


def device_counts(models: dict[str, dict[str, Any]], shots: int = SHOTS) -> dict[str, Any]:
    """Expected counts of a model device, rounded to whole shots: each circuit's true Bloch z from the Bloch model
    (T1, T2, an initialization excitation p_init), relaxed over the pre-readout delay and read through the qubit's
    assignment errors."""
    counts: dict[str, Any] = {}

    def put(name: str, z: dict[str, float], flips: dict[str, float] | None = None, n: int = 0) -> None:
        row: dict[str, Any] = {"shots": shots, "final": {}}
        for q, m in models.items():
            waited = z_eq(m) - (z_eq(m) - z[q]) * math.exp(-PRE_READOUT_SECONDS / m["t1_s"])
            observed = (1 - m["e01"] - m["e10"]) * waited + m["e10"] - m["e01"]
            k0 = round(shots * (1 + observed) / 2)
            row["final"][q] = [k0, shots - k0]
        if flips is not None:
            row["flips"] = {q: [round(shots * (n - 1) * flips[q]), shots * (n - 1)] for q in models}
        counts[name] = row

    for arm, n in group_keys():
        z, flips = {}, {}
        for q, m in models.items():
            eps = m["eps_settle"] if arm == "settle" and m["eps_settle"] is not None else m["eps"]
            z[q] = bloch_z(
                arm,
                n,
                m["t1_s"],
                min(m["t2_s"], 2 * m["t1_s"]),
                tau_of(arm, m["window_s"]),
                eps,
                1 - 2 * m["p_init"],
                m["prx_p"],
                z_eq(m),
            )
            flips[q] = max(0.0, (1 - (1 - 2 * eps) * math.cos(THETA / n)) / 2)
        for name in group_names(arm, n):
            put(name, z, flips if arm in PINCHED_ARMS and n > 1 else None, n)
    put("ro0", {q: 1 - 2 * m["p_init"] for q, m in models.items()})
    for name, delay in zip(SERIES_NAMES, SERIES_DELAYS, strict=True):
        put(
            name,
            {q: z_eq(m) - (z_eq(m) + 1 - 2 * m["p_init"]) * math.exp(-delay / m["t1_s"]) for q, m in models.items()},
        )
    return counts


def planning_tables(excerpt: dict[str, Any]) -> dict[str, Any]:
    return {
        q: model_tables(cal["t1_s"], cal["t2_s"], PLANNING_Q, MEASURE_WINDOW_SECONDS, cal["prx_p"])
        for q, cal in excerpt["qubits"].items()
    }


def predict(excerpt: dict[str, Any], circuits: list[dict[str, Any]]) -> dict[str, Any]:
    """Planning values: every table is computed at the calibrated T1 and T2 and the assumed initialization
    excitation; the analysis recomputes them at the T1 and p it fits in the job."""
    tables = planning_tables(excerpt)
    bill = billing(circuits, SHOTS)
    contexts = {
        q: {"t2_s": cal["t2_s"], "prx_p": cal["prx_p"], "window_s": MEASURE_WINDOW_SECONDS, "planning": tables[q]}
        for q, cal in excerpt["qubits"].items()
    }
    expected = evaluate(device_counts({q: device_model(cal) for q, cal in excerpt["qubits"].items()}), contexts)
    qubits: dict[str, Any] = {}
    for q, cal in excerpt["qubits"].items():
        row = expected[q]
        sensitivity = {
            str(p): model_tables(cal["t1_s"], cal["t2_s"], 1 / (1 - 2 * p), MEASURE_WINDOW_SECONDS, cal["prx_p"])[
                "measure"
            ][str(TOP_STEPS)]
            for p in P_INIT_SENSITIVITY
        }
        spread = max(sensitivity.values()) - min(sensitivity.values())
        windows = {
            f"{w * 1e6:.3f}": {
                arm: model_tables(cal["t1_s"], cal["t2_s"], PLANNING_Q, w, cal["prx_p"])[arm][str(TOP_STEPS)]
                for arm in PINCHED_ARMS
            }
            for w in WINDOW_GRID
        }
        step = 1e-8
        derivative = {
            arm: (
                model_tables(cal["t1_s"], cal["t2_s"], PLANNING_Q, MEASURE_WINDOW_SECONDS + step, cal["prx_p"])[arm][
                    str(TOP_STEPS)
                ]
                - model_tables(cal["t1_s"], cal["t2_s"], PLANNING_Q, MEASURE_WINDOW_SECONDS - step, cal["prx_p"])[arm][
                    str(TOP_STEPS)
                ]
            )
            / (2 * step)
            for arm in PINCHED_ARMS
        }
        qubits[q] = {
            "inputs": {
                "t1_s": cal["t1_s"],
                "t2_s": cal["t2_s"],
                "prx_p": cal["prx_p"],
                "e01": cal["e01"],
                "e10": cal["e10"],
                "e01_plus_e10": cal["e01"] + cal["e10"],
                "measure_window_s": MEASURE_WINDOW_SECONDS,
                "prx_layer_s": PRX_LAYER_SECONDS,
                "delay_s": DELAY_SECONDS,
                "settle_idle_s": SETTLE_SECONDS,
                "pre_readout_s": PRE_READOUT_SECONDS,
                "p_init_assumed": ACTIVE_RESET_EXCITED,
            },
            "p0": tables[q],
            "window_sensitivity": {
                "p0_n16_by_window_us": windows,
                "derivative_per_second_at_planned": derivative,
                "shift_planned_to_mock_window": {
                    arm: windows[f"{MOCK_MEASURE_WINDOW_SECONDS * 1e6:.3f}"][arm]
                    - windows[f"{MEASURE_WINDOW_SECONDS * 1e6:.3f}"][arm]
                    for arm in PINCHED_ARMS
                },
                "measure_shift_over_departure_se": (
                    windows[f"{MOCK_MEASURE_WINDOW_SECONDS * 1e6:.3f}"]["measure"]
                    - windows[f"{MEASURE_WINDOW_SECONDS * 1e6:.3f}"]["measure"]
                )
                / row["departure_n16"]["se"],
            },
            "p_init_sensitivity": {
                "measure_n16_p0": sensitivity,
                "spread": spread,
                "spread_over_departure_se": spread / row["departure_n16"]["se"],
            },
            "expected": {
                "contrast_n16": row["contrast_n16"]["contrast"],
                "contrast_se": row["contrast_n16"]["se"],
                "mutation_z": row["decisions"]["mutation_test"]["z"],
                "departure_se": row["departure_n16"]["se"],
                "t1_se": row["fitted"]["t1_se"],
                "p_init_se": row["fitted"]["p_init_se"],
                "readout_history_se": row["readout_history_n1"]["se"],
                "settle_gap_se": row["settle_n16"]["se"],
                "dephasing_zeno_n16": tables[q]["delay"]["16"] - tables[q]["unitary"]["16"],
            },
        }
    return {
        "calibration_set": excerpt["calibration_set"],
        "selection": {
            **excerpt["selection"],
            "qubits": {
                q: {k: cal[k] for k in ("t1_s", "t2_s", "prx_p", "e01", "e10")} for q, cal in excerpt["qubits"].items()
            },
        },
        "ideal": {
            "measure": {str(n): ideal_measure(n) for n in STEPS},
            "delay_and_unitary": ideal_delay(),
            "contrast_n16": ideal_measure(TOP_STEPS) - ideal_delay(),
        },
        "measure_window_seconds": MEASURE_WINDOW_SECONDS,
        "prx_layer_seconds": PRX_LAYER_SECONDS,
        "acquisition_window_seconds": acquisition_ps(excerpt) / 1e12,
        "timing_source": (
            "Garnet QPU compiler estimates, calibration set be070414, 100 shots, the case's own circuits with the 2 us "
            "pre-readout delay: unitary-n16 7.032 us (job 01a174be-d1f7) and measure-n16 24.568 us (job 01a174be-e68b) "
            "per shot give a measure window of (24.568 - 7.032)/16 = 1.096 us; with the retained pilot job's 4.344 us "
            "per-circuit base the prx layer is (7.032 - 2.0 - 4.344)/16 = 43 ns, taken as the mock's 40 ns. "
            "garnet:mock compiles 1.772 us and 8.684 us per circuit"
        ),
        "estimator_per_shot_seconds_all_circuits": sum(estimator_shot_seconds(c) for c in circuits),
        "billing": bill,
        "billing_fit": {
            "execution_fixed_seconds": EXECUTION_FIXED_SECONDS,
            "execution_per_circuit_shot_seconds": EXECUTION_PER_CIRCUIT_SHOT_SECONDS,
            "residual_seconds": EXECUTION_FIT_RESIDUAL_SECONDS,
            "runtime_over_execution_seconds": RUNTIME_OVER_EXECUTION_SECONDS,
        },
        "planning_note": (
            "These are planning values at the calibrated T1 and T2 and an assumed initialization excitation. The "
            "analysis fits T1 and the excitation in the job and recomputes every prediction at the fitted values."
        ),
        "model": (
            "Bloch iteration from z0 = 1 - 2 p: a rotation of THETA/N per step, then an ideal pinch (measure and "
            "settle arms; T2 does not enter because the state is diagonal) or coherent evolution (delay and unitary "
            "arms), then T1 and Ramsey T2 relaxation over the rotation layer and, per arm, the measure window, the "
            "delay or the settle idle, and over the pre-readout delay; readout through the calibrated errors. The "
            "`expected` figures apply the run's estimator, T1 and p fit included, to the model's expected counts, so "
            "they are the standard errors the analysis reports at the case's shots"
        ),
        "qubits": qubits,
    }


def build_files(excerpt: dict[str, Any]) -> dict[str, str]:
    if excerpt["couplers_among_qubits"]:
        raise ValueError(f"the qubits share couplers {excerpt['couplers_among_qubits']}")
    qubits = sorted(excerpt["qubits"], key=lambda q: int(q[2:]))
    circuits = circuits_of(qubits)
    if len(circuits) > GARNET_MAX_CIRCUITS or any(len(c["instructions"]) > GARNET_MAX_INSTRUCTIONS for c in circuits):
        raise ValueError("the job exceeds Garnet's circuits or instructions per job")
    files = {f"circuits/{c['name']}.json": dump(c) for c in circuits}
    bill = billing(circuits, SHOTS)
    if bill["cancel_margin_seconds"] < RUNTIME_MARGIN_SECONDS or bill["credits"] > MAX_CREDITS[QC]:
        raise ValueError(
            f"worst-case runtime {bill['worst_case_runtime_seconds']:.3f} s leaves "
            f"{bill['cancel_margin_seconds']:.3f} s below the {bill['cancel_threshold_seconds']} s cancel threshold "
            f"({bill['credits']} credits)"
        )
    job = {
        "job": JOB,
        "circuits": [{"file": rel, "sha256": sha256(text.encode())} for rel, text in files.items()],
        "shots": SHOTS,
        # The job compiles against the calibration set the case was planned from, or fails if it is gone.
        "options": {**OPTIONS, "calibration_set_id": {QC: excerpt["calibration_set"]}},
        "expected_seconds": round(bill["execution_seconds"], 3),
        "max_credits": MAX_CREDITS,
    }
    files["prediction.json"] = dump(predict(excerpt, circuits))
    files["cases.json"] = dump(
        {
            "schema": CASE_SCHEMA,
            "case": CASE,
            "question": (
                f"Does a Garnet mid-circuit measurement act as ideal pinching, a nonselective projective measurement "
                f"in Z, on {', '.join(qubits)}, read by the Zeno build-up of N rotations of 8 pi/9 over N against the "
                "same rotations with no measurement, with a delay of the measure duration and a settled readout as "
                "controls, and with T1 and the initialization excitation measured in the job?"
            ),
            "qcs": QCS,
            "jobs": [job],
            "prediction_sha256": sha256(files["prediction.json"].encode()),
        }
    )
    files[EXCERPT] = dump(excerpt)
    return files


def write(directory: Path, calibration_dir: Path) -> None:
    files = build_files(excerpt_of(calibration_dir))
    stale_dir = directory / "circuits"
    for stale in stale_dir.glob("*.json") if stale_dir.exists() else []:
        if stale.relative_to(directory).as_posix() not in files:
            stale.unlink()
    for rel, text in files.items():
        path = directory / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    prediction = json.loads(files["prediction.json"])
    print(
        json.dumps(
            {
                "circuits": len(files) - 3,
                "calibration_set": prediction["calibration_set"],
                "qubits": list(prediction["qubits"]),
                "billing": prediction["billing"],
                "weakest_mutation_z": min(v["expected"]["mutation_z"] for v in prediction["qubits"].values()),
            }
        )
    )


def check(directory: Path) -> None:
    files = build_files(load_json(directory / EXCERPT))
    present = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
    if present != set(files):
        raise ValueError(f"{directory}: files differ from the build: {sorted(present ^ set(files))}")
    for rel, text in files.items():
        if (directory / rel).read_text(encoding="utf-8") != text:
            raise ValueError(f"{directory}/{rel} differs from the build")
    print(f"{directory}: matches the build from its retained calibration excerpt")


def compiled_schedule(
    prediction: dict[str, Any],
    circuits: list[dict[str, Any]],
    shots: int,
    estimate_seconds: float,
    resolve: bool = True,
) -> tuple[dict[str, Any], float]:
    """The preregistered check of a job's compiled schedule against the case's prediction, and the measure window the
    decisions use: the planned one, or the one solved from the job's total when they differ by more than
    SCHEDULE_TOLERANCE and the solution lies within a factor of four of the plan. A garnet:mock job compiles its own
    window, so its analysis (resolve False) reports the ratio and the window it would solve and keeps the plan."""
    predicted = prediction["estimator_per_shot_seconds_all_circuits"] * shots
    estimated = estimate_seconds - JOB_SECONDS
    schedule: dict[str, Any] = {
        "predicted_qpu_execution_seconds": predicted,
        "estimated_qpu_execution_seconds": estimated,
        "ratio": estimated / predicted,
        "tolerance": SCHEDULE_TOLERANCE,
        "window_recomputed": False,
    }
    window = prediction["measure_window_seconds"]
    if abs(estimated / predicted - 1) > SCHEDULE_TOLERANCE and not resolve:
        schedule["solved_window_seconds"] = solve_window(circuits, shots, estimated)
        schedule["window_kept_for_mock"] = True
    elif abs(estimated / predicted - 1) > SCHEDULE_TOLERANCE:
        # The QPU compiled a different schedule than the mock's: solve the measure window from its total and
        # recompute every prediction at that window and the fitted T1 before any decision.
        solved = solve_window(circuits, shots, estimated)
        planned = prediction["measure_window_seconds"]
        schedule["planned_window_seconds"] = planned
        schedule["solved_window_seconds"] = solved
        # The solve assumes the mock's per-circuit base and layer time; a window outside a factor of four of the
        # planned one means that assumption fails (the idle-schedule QPU job's estimate was 0.62 of the mock
        # model's), so the planned window stays and the per-circuit runtime_estimates artifact must settle it.
        if planned / 4 <= solved <= 4 * planned:
            window = solved
            schedule["window_recomputed"] = True
        else:
            schedule["window_rejected"] = True
    schedule["measure_window_seconds_used"] = window
    return schedule, window


def pooled_z(estimates: list[tuple[float, float]]) -> float | None:
    """The inverse-variance pooled estimate over its standard error, from (estimate, se) pairs."""
    weights = [1 / se**2 for _, se in estimates]
    if not weights:
        return None
    return sum(w * e for w, (e, _) in zip(weights, estimates, strict=True)) / math.sqrt(sum(weights))


def device_verdict(qubits: dict[str, Any]) -> dict[str, Any]:
    """The preregistered device-level verdicts. A device departs when at least DEVICE_QUBITS of the usable qubits
    return `departs_below`, or the inverse-variance pooled departure z over the usable qubits is at or below
    -Z_DECIDE; `exceeds_prediction` and the settle `tail_attributed` follow the same rule with the signs of their
    own z. Six qubits times about four 3-SE tests give about a 6 % chance of one false flag, so the per-qubit
    verdicts stay descriptive. The pooling treats the qubits as independent.

    A randomized-benchmarking underestimate of the prx error is shared across qubits and pools coherently, so a device
    departure (either sign) is attributed to the measurement only if, on every qubit that contributes to it (the named
    qubits, or all usable qubits when the pooled z fired), the unitary arm's N = 16 measured-minus-modeled difference
    lies within Z_DECIDE statistical standard errors. Otherwise the status reads `gate_model_inconsistent`, `device`
    stays false and the departure is not attributed.
    """
    usable = {q: r for q, r in qubits.items() if r["usable"]}
    departure = [(r["departure_n16"]["difference"], r["departure_n16"]["se"]) for r in usable.values()]
    tail = [(r["settle_n16"]["tail_gap"], r["settle_n16"]["se"]) for r in usable.values()]
    z_departure, z_tail = pooled_z(departure), pooled_z(tail)
    below = sorted(q for q, r in usable.items() if r["decisions"]["departure"]["outcome"] == "departs_below")
    above = sorted(q for q, r in usable.items() if r["decisions"]["departure"]["outcome"] == "exceeds_prediction")
    tailed = sorted(q for q, r in usable.items() if r["settle_n16"]["verdict"] == "tail_attributed")

    def verdict(named: list[str], z: float | None, sign: int, gate: bool = True) -> dict[str, Any]:
        pooled_fired = z is not None and sign * z >= Z_DECIDE
        fired = len(named) >= DEVICE_QUBITS or pooled_fired
        contributors = sorted(usable) if pooled_fired else named
        inconsistent = gate and any(abs(usable[q]["gate_check_n16"]["z"]) >= Z_DECIDE for q in contributors)
        status = "none" if not fired else "gate_model_inconsistent" if inconsistent else "attributed"
        return {"qubits": named, "pooled_z": z, "status": status, "device": status == "attributed"}

    return {
        "usable_qubits": sorted(usable),
        "departs_below": verdict(below, z_departure, -1),
        "exceeds_prediction": verdict(above, z_departure, 1),
        "settle_tail_attributed": verdict(tailed, z_tail, 1, gate=False),
    }


def readout_crosstalk(circuits: list[dict[str, Any]], measurements: list[dict[str, Any]]) -> dict[str, Any]:
    """Descriptive: the largest absolute correlation of each qubit's final outcome with another qubit's, in ro0,
    ro1 and the N = 16 measure arm. ro1 puts every qubit in |1> at once, while the measure arm's neighbor states vary
    from shot to shot, so state-dependent simultaneous-readout crosstalk is not calibrated; independent qubits read
    out independently, so a correlation beyond the shot noise (about 0.02 at 3000 shots) points at it."""
    wanted = {"ro0", "ro1", *group_names("measure", TOP_STEPS)}
    out: dict[str, float] = {}
    for c, entry in zip(circuits, measurements, strict=True):
        if c["name"] not in wanted:
            continue
        bits = np.array(entry[FINAL_KEY], dtype=float)
        with np.errstate(invalid="ignore", divide="ignore"):
            phi = np.nan_to_num(np.corrcoef(bits, rowvar=False))
        np.fill_diagonal(phi, 0.0)
        for position, qubit in enumerate(qubits_of(c)):
            out[qubit] = max(out.get(qubit, 0.0), float(np.max(np.abs(phi[position]))))
    return {"max_abs_correlation": out, "shot_noise": 1 / math.sqrt(SHOTS)}


def analyze(run_dir: Path, mock: bool = False) -> dict[str, Any]:
    """The preregistered decisions of a garnet run, or with mock the same pipeline over a garnet:mock run.

    Mock outcomes are random bits, so a mock analysis exercises the format, the tally and every guard; its
    numbers decide nothing, and it skips the calibration-set match because the mock compiles against its own set.
    """
    facts = run_facts(run_dir)
    submission = load_json(run_dir / "submission.json")
    record = json.loads((run_dir / "raw/job.json").read_bytes())
    case = load_json(run_dir / "cases.json")
    prediction_bytes = (run_dir / "prediction.json").read_bytes()
    if sha256(prediction_bytes) != case.get("prediction_sha256"):
        raise ValueError(f"{run_dir}/prediction.json is not the prediction cases.json binds")
    if facts["statuses"] != {"completed": 1}:
        raise ValueError(f"{run_dir}: the job is {sorted(facts['statuses'])}; the analysis reads completed jobs")
    # Mock outcomes are random bits and enter only a mock analysis, which decides nothing.
    qc = f"{QC}:mock" if mock else QC
    if submission["qc"] != qc or case.get("case") != CASE:
        raise ValueError(f"{run_dir}: a {case.get('case')} run on {submission['qc']}, not a {CASE} run on {qc}")
    prediction = json.loads(prediction_bytes)
    if not mock and record["compilation"]["calibration_set_id"] != prediction["calibration_set"]:
        raise ValueError(f"{run_dir}: compiled against another calibration set than the case's")
    row = next(r for r in case["jobs"] if r["job"] == submission["job"])
    circuits = [load_json(run_dir / entry["file"]) for entry in row["circuits"]]
    measurements = json.loads((run_dir / "raw/measurements.json").read_bytes())
    counts = tally(circuits, measurements)
    schedule, window = compiled_schedule(
        prediction, circuits, row["shots"], record["compilation"]["execution_runtime_estimate_seconds"], not mock
    )
    artifact = run_dir / "raw/runtime_estimates.json"
    if artifact.exists():
        schedule["runtime_estimates_sha256"] = sha256(artifact.read_bytes())
    metrics = record["metrics"]
    predicted_execution = billing(circuits, row["shots"])
    qubits = evaluate(counts, contexts_of(prediction, window))
    return {
        "schema": "iqm-measurement-sequence-analysis-v2",
        "run": run_dir.name,
        "mock": mock,
        "calibration_set": record["compilation"]["calibration_set_id"],
        "estimate_seconds": record["compilation"]["execution_runtime_estimate_seconds"],
        "runtime_seconds": metrics["runtime_seconds"],
        "billed_seconds": metrics["billed_seconds"],
        "charge": facts["charge"],
        "compiled_schedule": schedule,
        "billing_check": {
            "predicted_execution_seconds": predicted_execution["execution_seconds"],
            "execution_seconds": metrics.get("execution_seconds"),
            "predicted_worst_case_runtime_seconds": predicted_execution["worst_case_runtime_seconds"],
        },
        "readout_crosstalk": readout_crosstalk(circuits, measurements),
        "device": device_verdict(qubits),
        "qubits": qubits,
    }


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def check_structure(circuits: list[dict[str, Any]], qubits: list[str]) -> None:
    expect(len(circuits) == 57 and len({c["name"] for c in circuits}) == 57, f"{len(circuits)} circuits")
    by_name = {c["name"]: c for c in circuits}
    for c in circuits:
        ops = c["instructions"]
        expect(
            qubits_of(c) == qubits and ops[-1] == op("measure", qubits, key=FINAL_KEY), f"{c['name']}: final measure"
        )
        expect(ops[-2] == op("delay", qubits, duration=PRE_READOUT_SECONDS), f"{c['name']}: no pre-readout delay")
    for arm, n in group_keys():
        signs = []
        for name in group_names(arm, n):
            ops = by_name[name]["instructions"]
            prx = [o for o in ops if o["name"] == "prx"]
            expect(len(prx) == len(qubits) * n, f"{name}: {len(prx)} prx")
            signs.append(1 if prx[0]["args"]["angle"] > 0 else -1)
            expect(all(abs(o["args"]["angle"] - signs[-1] * THETA / n) < 1e-15 for o in prx), f"{name}: angles")
            measures = [o for o in ops if o["name"] == "measure"]
            delays = [o for o in ops if o["name"] == "delay"]
            keys = [o["args"]["key"] for o in measures]
            expect(len(set(keys)) == len(keys) and keys[-1] == FINAL_KEY, f"{name}: keys {keys}")
            mid = delays[:-1]
            if arm == "measure":
                expect(len(measures) == n + 1 and not mid, f"{name}: {len(measures)} measures")
            elif arm == "settle":
                expect(len(measures) == n + 1 and len(mid) == n, f"{name}: {len(measures)} measures")
                expect(all(d["args"]["duration"] == SETTLE_SECONDS for d in mid), f"{name}: settle duration")
                width = len(qubits) + 1
                expect(
                    [o["name"] for o in ops[len(qubits) : len(qubits) + 2]] == ["measure", "delay"], f"{name}: order"
                )
                expect(len(ops) == n * (width + 1) + 2, f"{name}: {len(ops)} operations")
            elif arm == "delay":
                expect(len(measures) == 1 and len(mid) == n, f"{name}: {len(mid)} delays")
                expect(all(d["args"]["duration"] == DELAY_SECONDS for d in mid), f"{name}: delay duration")
            else:
                expect(len(measures) == 1 and not mid, f"{name}: a mid-circuit operation in the unitary arm")
                expect(all(o["name"] == "prx" for o in ops[:-2]), f"{name}: not back-to-back rotations")
            expect(all(o["locus"] == qubits for o in measures + delays), f"{name}: locus")
            expect({o["locus"][0] for o in prx} == set(qubits), f"{name}: prx qubits")
        expect(signs == list(SIGNS), f"{arm} N = {n}: sign order {signs}")
    expect([c["name"] for c in circuits[:8]] == group_names("measure", 1) + group_names("delay", 1), "arm order")
    expect([o["name"] for o in by_name["ro0"]["instructions"]] == ["delay", "measure"], "ro0")
    expect([o["name"] for o in by_name["ro1"]["instructions"]] == [*["prx"] * len(qubits), "delay", "measure"], "ro1")
    for name, wait in zip(T1_NAMES, T1_DELAYS, strict=True):
        ops = by_name[name]["instructions"]
        expect(ops[len(qubits)] == op("delay", qubits, duration=wait), f"{name}: wait")
        expect(all(o["args"]["angle"] == math.pi for o in ops[: len(qubits)]), f"{name}: pi pulse")


def check_billing_fit() -> str:
    """The constants EXECUTION_* against the seven retained jobs they were fitted on."""
    ids = (
        "01a16583-43fc-75e5-82b0-5b192921a4c5",
        "01a16630-b928-72d1-b66e-b7779c623df5",
        "01a16631-2b7c-7668-a276-3341e9d17bdd",
        "01a167ac-58d4-74f0-96fe-9af62e1f1dfe",
        "01a167ac-e6f3-711a-a9be-86bb8bfe89f9",
        "01a167ac-ec22-7645-b50d-74b793ed808d",
        "01a1707f-6157-75dc-aca8-6f30e5f0280b",
    )
    rows = []
    for directory in sorted((ROOT / "results/iqm/runs").glob("*-garnet-*")):
        submission = load_json(directory / "submission.json") if (directory / "submission.json").exists() else {}
        if submission.get("job_id") in ids:
            record = json.loads((directory / "raw/job.json").read_bytes())
            case = load_json(directory / "cases.json")
            job = next(r for r in case["jobs"] if r["job"] == submission["job"])
            metrics = record["metrics"]
            schedule = record["compilation"]["execution_runtime_estimate_seconds"] - JOB_SECONDS
            rows.append(
                (
                    schedule,
                    metrics["execution_seconds"],
                    metrics["runtime_seconds"],
                    len(job["circuits"]) * job["shots"],
                )
            )
    expect(len(rows) == len(ids), f"{len(rows)} of the {len(ids)} fitted jobs are retained")
    design = np.array([[1.0, r[3]] for r in rows])
    target = np.array([r[1] - r[0] for r in rows])
    fixed, per = (float(v) for v in np.linalg.lstsq(design, target, rcond=None)[0])
    residual = float(np.max(np.abs(target - design @ np.array([fixed, per]))))
    expect(
        abs(fixed - EXECUTION_FIXED_SECONDS) < 5e-4 and abs(per - EXECUTION_PER_CIRCUIT_SHOT_SECONDS) < 5e-9,
        f"fit {fixed} {per}",
    )
    expect(residual <= EXECUTION_FIT_RESIDUAL_SECONDS, f"residual {residual}")
    expect(max(r[2] - r[1] for r in rows) <= RUNTIME_OVER_EXECUTION_SECONDS, "runtime minus execution")
    return f"{fixed:.3f} s + {per * 1e6:.3f} us per circuit-shot, residual {residual:.3f} s"


def check_selection(values: dict[str, float], architecture: dict[str, Any], count: int) -> None:
    """select_qubits returns count qubits that are uncoupled, at or above the median T1 and not outranked by any
    qubit that no chosen, better-ranked qubit blocks."""
    chosen, info = select_qubits(values, architecture, count)
    coupled = {
        frozenset(locus) for impl in architecture["gates"]["cz"]["implementations"].values() for locus in impl["loci"]
    }

    def error(q: str) -> float:
        return (
            values[f"metrics.ssro.measure.constant.{q}.error_0_to_1"]
            + values[f"metrics.ssro.measure.constant.{q}.error_1_to_0"]
        )

    expect(len(chosen) == count, f"{len(chosen)} qubits chosen")
    expect(all(frozenset(pair) not in coupled for pair in itertools.combinations(chosen, 2)), "a coupled pair")
    expect(
        all(values[f"characterization.model.{q}.t1_time"] >= info["median_t1_s"] for q in chosen),
        "a T1 under the median",
    )
    worst = max(error(q) for q in chosen)
    for q in architecture["qubits"]:
        if q in chosen or values[f"characterization.model.{q}.t1_time"] < info["median_t1_s"] or error(q) >= worst:
            continue
        blockers = [c for c in chosen if frozenset((q, c)) in coupled and error(c) <= error(q)]
        expect(bool(blockers), f"{q} outranks a chosen qubit and no better chosen qubit is coupled to it")


def synthetic_measurements(circuits: list[dict[str, Any]], counts: dict[str, Any], shots: int) -> list[dict[str, Any]]:
    """The raw measurements.json a job would return for expected counts, with no random draw.

    Each key holds `shots` rows of one 0/1 outcome per qubit in locus order. Qubit j reads 1 in the shots whose index i
    satisfies (i * SHOT_PERMUTATIONS[j]) mod shots < ones, so the marginals are exact and the qubits' orderings differ.
    The mid-circuit keys are per-qubit paths that flip between consecutive keys by the Bresenham pattern of the
    expected flip count, so the pair counts are exact and each qubit's path is independent of the others' by
    construction; a feature that reads correlations across qubits sees only the permutations' residue.
    """
    out = []
    index = np.arange(shots)
    for c in circuits:
        qubits = qubits_of(c)
        row = counts[c["name"]]
        mids = [o["args"]["key"] for o in c["instructions"] if o["name"] == "measure" and o["args"]["key"] != FINAL_KEY]
        final = np.zeros((shots, len(qubits)), dtype=int)
        for j, q in enumerate(qubits):
            final[:, j] = ((index * SHOT_PERMUTATIONS[j]) % shots) < row["final"][q][1]
        entry: dict[str, Any] = {FINAL_KEY: final.tolist()}
        if mids:
            paths = np.zeros((shots, len(mids), len(qubits)), dtype=int)
            pairs = shots * (len(mids) - 1)
            for j, q in enumerate(qubits):
                if len(mids) > 1 and "flips" in row:
                    total = row["flips"][q][0]
                    position = np.arange(pairs)
                    flip = ((position + 1) * total) // pairs - (position * total) // pairs
                    paths[:, 1:, j] = np.cumsum(flip.reshape(shots, len(mids) - 1), axis=1) % 2
            for k, key in enumerate(mids):
                entry[key] = paths[:, k, :].tolist()
        out.append(entry)
    return out


def sweep_cases(reduced: bool) -> list[dict[str, Any]]:
    """True devices off the planning point: one axis at a time, then a corner with all four moved. The reduced grid
    keeps the planning point and the corner."""
    base = {"label": "planning", "p_init": ACTIVE_RESET_EXCITED, "p_thermal": 0.0, "t1_scale": 1.0, "prx_scale": 1.0}
    corner = {**base, "label": "corner", "p_init": 0.15, "p_thermal": 0.02, "t1_scale": 0.8, "prx_scale": 2.0}
    if reduced:
        return [base, corner]
    axes = [
        {**base, "label": "p=0", "p_init": 0.0},
        {**base, "label": "p=0.15", "p_init": 0.15},
        {**base, "label": "thermal 0.02", "p_thermal": 0.02},
        {**base, "label": "T1 x0.8", "t1_scale": 0.8},
        {**base, "label": "T1 x1.2", "t1_scale": 1.2},
        {**base, "label": "prx x2", "prx_scale": 2.0},
        {**base, "label": "prx x3", "prx_scale": 3.0, "gate_stress": True},
    ]
    return [base, *axes, corner]


def run_sweep(files: dict[str, str], excerpt: dict[str, Any], cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The real analyze path over a synthetic run directory per true device: readout correction, T1 and p fit,
    prediction recompute and decisions. Each row summarizes one device over its qubits."""
    global run_facts
    job = json.loads(files["cases.json"])["jobs"][0]
    circuits = [json.loads(files[entry["file"]]) for entry in job["circuits"]]
    prediction = json.loads(files["prediction.json"])
    original = run_facts
    run_facts = lambda run_dir: {"statuses": {"completed": 1}, "charge": 0.0}  # noqa: E731
    rows = []
    try:
        for spec in cases:
            models = {
                q: device_model(
                    cal,
                    t1_s=spec["t1_scale"] * cal["t1_s"],
                    p_init=spec["p_init"],
                    p_thermal=spec["p_thermal"],
                    prx_p=spec["prx_scale"] * cal["prx_p"],
                )
                for q, cal in excerpt["qubits"].items()
            }
            measurements = synthetic_measurements(circuits, device_counts(models), job["shots"])
            with tempfile.TemporaryDirectory() as scratch:
                run = Path(scratch)
                (run / "raw").mkdir()
                for rel, text in files.items():
                    (run / rel).parent.mkdir(parents=True, exist_ok=True)
                    (run / rel).write_text(text, encoding="utf-8")
                (run / "submission.json").write_text(dump({"qc": QC, "job": JOB}), encoding="utf-8")
                schedule = prediction["estimator_per_shot_seconds_all_circuits"] * job["shots"]
                record = {
                    "compilation": {
                        "calibration_set_id": prediction["calibration_set"],
                        "execution_runtime_estimate_seconds": JOB_SECONDS + schedule,
                    },
                    "metrics": {"runtime_seconds": 7.0, "billed_seconds": 7.0, "execution_seconds": 6.0},
                }
                (run / "raw/job.json").write_text(json.dumps(record), encoding="utf-8")
                (run / "raw/measurements.json").write_text(json.dumps(measurements), encoding="utf-8")
                result = analyze(run)
            usable = {q: r for q, r in result["qubits"].items() if r["usable"]}
            rows.append(
                {
                    **spec,
                    "usable": len(usable),
                    "departure_z": {q: r["decisions"]["departure"]["z"] for q, r in usable.items()},
                    "settle": {q: r["settle_n16"]["verdict"] for q, r in usable.items()},
                    "mutation_z": {q: r["decisions"]["mutation_test"]["z"] for q, r in usable.items()},
                    "mutation_passes": all(r["decisions"]["mutation_test"]["passes"] for r in usable.values()),
                    "t1_error": {q: r["fitted"]["t1_s"] / models[q]["t1_s"] - 1 for q, r in usable.items()},
                    "device": {
                        k: v["device"] for k, v in result["device"].items() if isinstance(v, dict) and "device" in v
                    },
                    "device_status": {
                        k: v["status"] for k, v in result["device"].items() if isinstance(v, dict) and "status" in v
                    },
                    "pooled_departure_z": result["device"]["departs_below"]["pooled_z"],
                    "gate_check_z": {q: r["gate_check_n16"]["z"] for q, r in usable.items()},
                    "schedule_ratio": result["compiled_schedule"]["ratio"],
                }
            )
    finally:
        run_facts = original
    return rows


def sweep_failures(rows: list[dict[str, Any]], qubits: int = QUBIT_COUNT) -> list[str]:
    """The pass rule: every qubit of every device reads |departure z| < 1, settle `match`, a passing mutation test and
    no device flag. A gate-stress row (a prx error well beyond the systematic) instead needs the device verdict to
    report no attributed departure."""
    failures = []
    for row in rows:
        if row["usable"] != qubits:
            failures.append(f"{row['label']}: {row['usable']} usable qubits")
        if not row.get("gate_stress"):
            for q, z in row["departure_z"].items():
                if abs(z) >= 1:
                    failures.append(f"{row['label']} {q}: departure z {z:.2f}")
            for q, verdict in row["settle"].items():
                if verdict != "match":
                    failures.append(f"{row['label']} {q}: settle {verdict}")
        if not row["mutation_passes"]:
            failures.append(f"{row['label']}: the mutation test fails")
        if any(row["device"].values()):
            failures.append(f"{row['label']}: a device-level flag {row['device']}")
    return failures


def sweep(reduced: bool = False) -> list[dict[str, Any]]:
    """The estimator sweep over the retained case; raises on any failure of the pass rule."""
    excerpt = load_json(ROOT / "results/iqm/cases" / CASE / EXCERPT)
    rows = run_sweep(build_files(excerpt), excerpt, sweep_cases(reduced))
    failures = sweep_failures(rows)
    if failures:
        raise RuntimeError("estimator sweep: " + "; ".join(failures))
    return rows


def self_test(with_sweep: bool = True) -> str:
    excerpt = load_json(ROOT / "results/iqm/cases" / CASE / EXCERPT)
    files = build_files(excerpt)
    expect(files == build_files(excerpt), "the build is not deterministic")
    qubits = sorted(excerpt["qubits"], key=lambda q: int(q[2:]))
    # Exact ideals.
    expect(
        [round(ideal_measure(n), 4) for n in STEPS] == [0.0302, 0.5151, 0.6722, 0.8040, 0.8914],
        f"ideal P0 {[round(ideal_measure(n), 4) for n in STEPS]}",
    )
    expect(round(ideal_delay(), 4) == 0.0302, "the delay and unitary ideal is not 0.0302")
    expect(round(ideal_measure(16) - ideal_delay(), 4) == 0.8612, "the N = 16 contrast ideal is not 0.8612")
    expect(abs(ideal_flip(1) - (1 - math.cos(THETA)) / 2) < 1e-15, "the flip ideal at N = 1")
    points = [(n, model_p0(n, 0.01), 0.005) for n in STEPS]
    expect(abs(fit_eps(points)["eps"] - 0.01) < 1e-6, "the closed-form fit does not recover its own law")
    # Qubit selection: pairwise uncoupled, T1 at least the median, smallest readout error first. The retained
    # calibration admits three such qubits; a synthetic ring of twenty admits six.
    expect(len(qubits) == QUBIT_COUNT and not excerpt["couplers_among_qubits"], f"qubits {qubits}")
    metrics = load_json(CALIBRATION_DIR / "metrics.json")
    architecture = load_json(CALIBRATION_DIR / "dynamic-quantum-architecture.json")
    values = {o["dut_field"]: o["value"] for o in metrics["observations"] if not o.get("invalid")}
    check_selection(values, architecture, 3)
    ring = [f"QB{n}" for n in range(1, 21)]
    synthetic: dict[str, float] = {}
    for n, q in enumerate(ring):
        synthetic[f"characterization.model.{q}.t1_time"] = (20 + 3 * ((7 * n) % 10)) * 1e-6
        synthetic[f"metrics.ssro.measure.constant.{q}.error_0_to_1"] = 0.004 * (1 + (5 * n) % 7)
        synthetic[f"metrics.ssro.measure.constant.{q}.error_1_to_0"] = 0.003 * (1 + (3 * n) % 5)
    loci = [[ring[n], ring[(n + 1) % 20]] for n in range(20)]
    check_selection(
        synthetic, {"qubits": ring, "gates": {"cz": {"implementations": {"x": {"loci": loci}}}}}, QUBIT_COUNT
    )
    # Circuit structure, pre-readout delay, T1 series.
    case = json.loads(files["cases.json"])
    job = case["jobs"][0]
    expect(case["prediction_sha256"] == sha256(files["prediction.json"].encode()), "cases.json lacks the prediction")
    circuits = [json.loads(text) for rel, text in files.items() if rel.startswith("circuits/")]
    check_structure(circuits, qubits)
    prediction = json.loads(files["prediction.json"])
    # Billing: the fit, the worst-case runtime and the cancel margin.
    fit_text = check_billing_fit()
    bill = billing(circuits, SHOTS)
    expect(prediction["billing"] == bill, "prediction.json carries another billing")
    expect(job["max_credits"] == {"garnet": 5.0, "garnet:mock": 0.0}, f"max_credits {job['max_credits']}")
    expect(bill["cancel_margin_seconds"] >= RUNTIME_MARGIN_SECONDS, f"cancel margin {bill['cancel_margin_seconds']}")
    expect(bill["credits"] <= 5.0 and bill["billed_seconds"] <= 10, f"billing {bill}")
    expect(
        abs(job["expected_seconds"] - bill["execution_seconds"]) < 5e-4,
        "expected_seconds is not the predicted execution",
    )
    # The compiled-schedule model reproduces the two QPU probe estimates (microseconds per shot, 100 shots, 2 us
    # pre-readout delay included) to the 0.7 % that the 43 ns against 40 ns layer leaves.
    probes = {
        "unitary-n16": (circuit("u", qubits, "unitary", 16, 1), 7.032),
        "measure-n16": (circuit("m", qubits, "measure", 16, 1), 24.568),
    }
    for label, (probe, microseconds) in probes.items():
        got = estimator_shot_seconds(probe) * 1e6
        expect(abs(got / microseconds - 1) < 0.01, f"{label}: {got}")
    expect(abs((24.568 - 7.032) / 16 - MEASURE_WINDOW_SECONDS * 1e6) < 1e-9, "the window is not the probes' difference")
    total = SHOTS * sum(estimator_shot_seconds(c) for c in circuits)
    expect(abs(solve_window(circuits, SHOTS, total) - MEASURE_WINDOW_SECONDS) < 1e-12, "the window does not solve back")
    expect(
        solve_window(circuits, SHOTS, 1.05 * total) > 1.05 * MEASURE_WINDOW_SECONDS, "a longer schedule solves shorter"
    )
    expect(
        MEASURE_WINDOW_SECONDS > acquisition_ps(excerpt) / 1e12,
        "the measure window is not above the acquisition window",
    )
    # Planted devices: T1 and p differ from the planning values, eps takes both signs.
    contexts = contexts_of(prediction)
    planted = dict(zip(qubits, (0.0, 0.0, 0.015, 0.01, -0.01, 0.0), strict=True))
    models = {
        q: device_model(cal, t1_s=0.8 * cal["t1_s"], p_init=0.12, eps=planted[q], eps_settle=planted[q])
        for q, cal in excerpt["qubits"].items()
    }
    counts = device_counts(models)
    result = evaluate(counts, contexts)
    for q, eps in planted.items():
        row = result[q]
        fitted = row["fitted"]
        truth = models[q]
        expect(
            abs(fitted["t1_s"] - truth["t1_s"]) <= 4 * fitted["t1_se"] + 1e-7,
            f"{q}: T1 {fitted} against {truth['t1_s']}",
        )
        expect(abs(fitted["p_init"] - 0.12) <= 4 * fitted["p_init_se"] + 1e-3, f"{q}: p {fitted}")
        expect(row["decisions"]["mutation_test"]["passes"], f"{q}: the mutation test fails on a pinching device")
        want = "departs_below" if eps > 0 else "exceeds_prediction" if eps < 0 else "consistent"
        expect(row["decisions"]["departure"]["outcome"] == want, f"{q}: departure {row['departure_n16']}")
        relaxed = row["fit_relaxed"]
        expect(
            relaxed["eps_se"] is not None and abs(relaxed["eps"] - eps) <= 4 * relaxed["eps_se"] + 1e-3,
            f"{q}: {relaxed}",
        )
        expect(row["settle_n16"]["verdict"] == "match", f"{q}: settle {row['settle_n16']}")
        expect(row["readout_history_n1"]["verdict"] == "none", f"{q}: history {row['readout_history_n1']}")
        for n in STEPS[1:]:
            rate = row["transitions"][str(n)]["rate"]
            expect(abs(rate - max(0.0, (1 - (1 - 2 * eps) * math.cos(THETA / n)) / 2)) < 1e-3, f"{q}: flips {n}")
        for arm in ("delay", "unitary"):
            for n, value in row["p0"][arm].items():
                expect(abs(value["measured_minus_modeled"]) < 2e-3, f"{q}: {arm} N = {n} departs from its model")
    # A planning-value departure is not a pinching departure: the calibrated T1 and p put the eps = 0 devices far
    # from the planning prediction, and the fitted values do not.
    unplanned = result[qubits[0]]["p0"]["measure"]["16"]
    expect(
        abs(unplanned["p0"] - unplanned["planning"]) > 3 * unplanned["se"],
        "the planning value is not off the planted device",
    )
    # The settle arm reads a readout tail: a device whose measure arm alone loses z per step is attributed to it.
    tail = {
        q: device_model(cal, eps=0.01 if n % 2 else 0.0, eps_settle=0.0)
        for n, (q, cal) in enumerate(excerpt["qubits"].items())
    }
    for n, (q, row) in enumerate(evaluate(device_counts(tail), contexts).items()):
        expect(
            row["settle_n16"]["verdict"] == ("tail_attributed" if n % 2 else "match"), f"{q}: tail {row['settle_n16']}"
        )
    # The readout-history diagnostic: a bias on the N = 1 measure arm alone is detected on that qubit alone.
    biased = json.loads(json.dumps(counts))
    shift = round(0.03 * SHOTS)
    for name in group_names("measure", 1):
        biased[name]["final"][qubits[0]][0] -= shift
        biased[name]["final"][qubits[0]][1] += shift
    for q, row in evaluate(biased, contexts).items():
        want = "bias_detected" if q == qubits[0] else "none"
        expect(row["readout_history_n1"]["verdict"] == want, f"{q}: history {row['readout_history_n1']}")
    # A device without pinching: the measure arm follows the unitary law.
    flat = json.loads(json.dumps(counts))
    for n in STEPS:
        for name, source in zip(group_names("measure", n), group_names("unitary", TOP_STEPS), strict=True):
            flat[name] = {**flat[name], "final": flat[source]["final"]}
    for row in evaluate(flat, contexts).values():
        expect(not row["decisions"]["mutation_test"]["passes"], "the mutation test passes without pinching")
        expect(row["decisions"]["departure"]["outcome"] == "departs_below", "no departure without pinching")
    # The compiled-schedule check: exact, a longer schedule (window solved) and a far shorter one (window kept).
    for factor, solved, rejected in ((1.0, False, False), (1.05, True, False), (0.6, False, True)):
        check, window = compiled_schedule(
            prediction,
            circuits,
            SHOTS,
            JOB_SECONDS + prediction["estimator_per_shot_seconds_all_circuits"] * SHOTS * factor,
        )
        expect(abs(check["ratio"] - factor) < 1e-9, f"ratio {check['ratio']}")
        expect(check["window_recomputed"] == solved and check.get("window_rejected", False) == rejected, f"{check}")
        expect((window > MEASURE_WINDOW_SECONDS) == solved, f"window {window}")

    mock_check, mock_window = compiled_schedule(
        prediction,
        circuits,
        SHOTS,
        JOB_SECONDS + prediction["estimator_per_shot_seconds_all_circuits"] * SHOTS * 1.4,
        False,
    )
    expect(
        mock_window == prediction["measure_window_seconds"] and bool(mock_check.get("window_kept_for_mock")),
        f"a mock job re-solved the window: {mock_check}",
    )

    # The device rule: two qubits, or a pooled z, flags the device; one qubit does not.
    def usable(outcome: str, difference: float, tail: str = "match", gate_z: float = 0.0) -> dict[str, Any]:
        return {
            "usable": True,
            "gate_check_n16": {"z": gate_z},
            "departure_n16": {"difference": difference, "se": 0.01},
            "decisions": {"departure": {"outcome": outcome}},
            "settle_n16": {"tail_gap": 0.0, "se": 0.01, "verdict": tail},
        }

    quiet = {f"QB{n}": usable("consistent", 0.0) for n in range(6)}
    expect(
        not any(v["device"] for v in device_verdict(quiet).values() if isinstance(v, dict) and "device" in v), "quiet"
    )
    one = {**quiet, "QB0": usable("departs_below", -0.031, "tail_attributed")}
    verdict = device_verdict(one)
    expect(not verdict["departs_below"]["device"] and not verdict["settle_tail_attributed"]["device"], f"{verdict}")
    two = {**one, "QB1": usable("departs_below", -0.031, "tail_attributed")}
    verdict = device_verdict(two)
    expect(verdict["departs_below"]["device"] and verdict["settle_tail_attributed"]["device"], f"{verdict}")
    expect(not verdict["exceeds_prediction"]["device"], "exceeds_prediction follows departs_below")
    drift = {f"QB{n}": usable("consistent", -0.015) for n in range(6)}
    expect(device_verdict(drift)["departs_below"]["device"], "a pooled departure at -3.7 sigma is not a flag")
    expect(
        device_verdict({**quiet, "QB0": {"usable": False}})["usable_qubits"] == [f"QB{n}" for n in range(1, 6)],
        "usable",
    )
    # The gate guard: a unitary-arm difference beyond 3 SE on a contributing qubit withholds the attribution.
    inconsistent = device_verdict({**two, "QB1": usable("departs_below", -0.031, "match", gate_z=-3.5)})
    expect(
        inconsistent["departs_below"]["status"] == "gate_model_inconsistent"
        and not inconsistent["departs_below"]["device"],
        f"{inconsistent['departs_below']}",
    )
    expect(
        device_verdict({**two, "QB5": usable("consistent", 0.0, "match", gate_z=4.0)})["departs_below"]["status"]
        == "attributed",
        "a gate difference on a non-contributing qubit blocks a count-rule departure",
    )
    pooled_blocked = device_verdict({**drift, "QB2": usable("consistent", -0.015, "match", gate_z=3.1)})
    expect(pooled_blocked["departs_below"]["status"] == "gate_model_inconsistent", f"{pooled_blocked['departs_below']}")
    expect(
        device_verdict({f"QB{n}": usable("consistent", 0.015, "match", gate_z=3.1) for n in range(6)})[
            "exceeds_prediction"
        ]["status"]
        == "gate_model_inconsistent",
        "exceeds_prediction escapes the gate guard",
    )
    if with_sweep:
        rows = run_sweep(files, excerpt, sweep_cases(True))
        failures = sweep_failures(rows)
        expect(not failures, "; ".join(failures))
    # The decision rules at their thresholds.
    expect(decide(0.5301, 0.01, 0.0, 0.01)["mutation_test"]["passes"], "3.01 standard errors above 0.5 fails")
    expect(not decide(0.5299, 0.01, 0.0, 0.01)["mutation_test"]["passes"], "2.99 standard errors above 0.5 passes")
    for z, outcome in (
        (-3.01, "departs_below"),
        (-2.99, "consistent"),
        (2.99, "consistent"),
        (3.01, "exceeds_prediction"),
    ):
        expect(decide(0.9, 0.01, z * 0.01, 0.01)["departure"]["outcome"] == outcome, f"z = {z} is not {outcome}")
    # Random readout, as a mock returns: every circuit reads each qubit half 0 and half 1, so the readout scale is
    # zero and no qubit decides.
    uniform = device_counts({q: device_model(cal) for q, cal in excerpt["qubits"].items()})
    for row in uniform.values():
        row["final"] = {q: [row["shots"] // 2, row["shots"] - row["shots"] // 2] for q in row["final"]}
    for row in evaluate(uniform, contexts).values():
        expect(not row["usable"] and "decisions" not in row, "a zero readout scale reaches a decision")
    margin = min(v["expected"]["mutation_z"] for v in prediction["qubits"].values())
    return (
        f"measurement sequence pinching: {len(circuits)} circuits on {', '.join(qubits)}, {SHOTS} shots, "
        f"{bill['execution_seconds']:.2f} s predicted execution, {bill['billed_seconds']} s worst-case billed "
        f"({bill['cancel_margin_seconds']:.2f} s below the cancel threshold); billing fit {fit_text}; the ideal laws, "
        f"circuit structure, T1 and p recovery, two-sided departure, settle, history and decision thresholds hold; the "
        f"weakest predicted mutation margin is {margin:.1f} standard errors"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")
    bd = sub.add_parser("build")
    bd.add_argument("directory", type=Path)
    bd.add_argument("--calibration-dir", type=Path, default=CALIBRATION_DIR)
    sub.add_parser("check").add_argument("directory", type=Path)
    sw = sub.add_parser("sweep", help="the estimator sweep over true devices off the planning point")
    sw.add_argument("--reduced", action="store_true", help="the planning point and the corner only")
    an = sub.add_parser("analyze")
    an.add_argument("run_dir", type=Path)
    an.add_argument("--out", type=Path, required=True)
    an.add_argument("--replay", action="store_true")
    an.add_argument("--mock", action="store_true", help="analyze a garnet:mock run; its numbers decide nothing")
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
    elif args.command == "build":
        write(args.directory, args.calibration_dir)
    elif args.command == "check":
        check(args.directory)
    elif args.command == "sweep":
        print(dump(sweep(args.reduced)), end="")
    elif args.command == "analyze":
        text = dump(analyze(args.run_dir, args.mock))
        if args.replay:
            if args.out.read_text(encoding="utf-8") != text:
                raise ValueError(f"{args.out} differs from the recomputation")
            print(f"{args.out}: replays byte for byte")
        else:
            args.out.write_text(text, encoding="utf-8")
    else:
        parser.error("choose a subcommand or --self-test")
    return 0


if __name__ == "__main__":
    sys.exit(main())
