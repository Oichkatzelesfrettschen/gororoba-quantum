"""IQM Garnet facts the circuit-job predictions rest on: the idle schedule and every qubit's pulse over-rotation.

Schedule. The iqm_sim-based predictions (iqm_cancellation_probe.py, iqm_signed_probe.py, iqm_signed_resolve.py)
apply idle T1/T2 relaxation over an ALAP schedule, while the iqm-pulse TimeBox default is ASAP
(docs/notes/iqm/docs/iqm-pulse/using_builder.md) and a circuit job body names no strategy. The job API returns
measurements, counts, runtime estimates and sweep results, not the compiled schedule
(docs/notes/iqm/README.md, endpoint table), so the strategy is measured. An idle circuit drives one train qubit B
with n pi pulses (an identity for even n), gives every qubit that shares no coupler with B one pi pulse, and reads
all qubits in one joint measure. ASAP places those pulses at the start, so each pulsed qubit waits n pulse lengths
in |1> and relaxes by exp(-n t_prx / T1); ALAP places them just before the measure, so the readings do not depend
on n. Two train qubits at opposite corners of the lattice (IDLE_TRAIN_QUBITS) leave every qubit pulsed in at least
one layout.

Over-rotation. iqm_signed_resolve.py measured prx trains on its TRAIN_QUBITS with a readout pair on its control
qubit only, so a train's over-rotation was not separable from that qubit's readout offset and scale. The isolated
block gives each TRAIN_QUBITS qubit its own ro0, ro1 and trains, as that probe drove them; the parallel block runs
the readout pair and the trains on every qubit at once. iqm_cancellation_probe.fit_train fits each train jointly
with its readout pair. One shot reads every qubit, so the parallel block maps all qubits for the shots of one.

All-zeros heralding over every qubit would keep few shots, so the job runs one active-reset cycle without
heralding; each readout pair's bare measure carries the reset's initialization error in its e01.

Preregistered decisions (Z_RESOLVE standard errors):

- H1, per pulsed qubit and nonzero train length: the observed contrast z(n) - z(0) lies Z_RESOLVE above the
  midpoint of the ASAP and ALAP predictions, toward ASAP (asap), Z_RESOLVE below it (alap), or between
  (unresolved). The schedule verdict is the common reading of every arm, mixed when arms resolve to both, and
  unresolved otherwise.
- H2, per isolated train qubit: the joint fit is linear when its chi-square survival is at least TRAIN_P_MIN; it
  reports eps and its standard error. Where iqm_signed_resolve.COHERENT attributes an over-rotation to the qubit,
  that value is consistent when it lies within Z_RESOLVE standard errors of eps and excluded otherwise.

Descriptive outputs, deciding nothing: the parallel over-rotation map, the parallel minus isolated eps of each
TRAIN_QUBITS qubit, and under an asap verdict each pulsed qubit's apparent T1 from its readout-corrected decay.

Emerald. --qc emerald builds the Emerald case (results/iqm/proposals/idle-schedule-train-readout-emerald/CASE.md):
twelve chosen qubits, train qubits QB20 and QB26, the 24 ns prx of Emerald's drag_crf_sx implementation,
4000 shots and no isolated train block. Garnet stays the default and its build is unchanged byte for byte.

Emerald successor. --qc emerald-t1 builds idle-schedule-t1-emerald: the Emerald circuits and four delay circuits
(T1_DELAYS) that read every measured qubit's T1 in the same job, so H2 separates a per-pulse timing gap from a
T1 calibration error (evaluate, "t1_delay" and "h2_gap"); --live reads the computer's current calibration.

Third length. --qc emerald-third builds idle-schedule-third-length-emerald from a calibration folder read beforehand
(build --calibration-from DIR; --live reads it from the service): the successor's circuits plus idle trains of 250
and 2000 pulses. Its prediction carries the line g(N) = a + b / N through the retained run's 500 and 1000 pulse gaps
(line_of) and the analysis reports the decision "h3_line" (line_decision): the deviation of the gap at 250 and at 2000
pulses from the line through the same job's gaps at 500 and 1000, with its covariance, and on-line, off-line,
anchors-moved or unidentifiable per subject. "power" records what the case resolves.

Usage: "$PYTHON" scripts/iqm_idle_schedule_probe.py (build DIR [--live | --calibration-from DIR] [--qc QC] |
       check DIR [--qc QC] | study CASE_DIR --out FILE | power CASE_DIR --out FILE |
       analyze RUN_DIR --out FILE [--replay] | --self-test)
"""

from __future__ import annotations

import argparse
import dataclasses
import functools
import itertools
import json
import math
import shutil
import sys
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import RGate
from qiskit_aer import AerSimulator
from scipy.integrate import quad
from scipy.stats import ncx2, norm

ROOT = Path(__file__).resolve().parent.parent
# The (ones, shots) of every name@qubit; the model devices of planted_counts carry fractional counts.
Counts = dict[str, tuple[Any, Any]]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import iqm_sim  # noqa: E402
from iqm_cancellation_probe import AMPLIFY_K, chi2_survival_3, fetch_calibration, fit_train, read, z_of  # noqa: E402
from iqm_jobs import CASE_SCHEMA, JOB_SECONDS, dump  # noqa: E402
from iqm_platform import sha256  # noqa: E402
from iqm_signed_probe import ACTIVE_SHOT_SECONDS, DURATIONS, relaxed, target_of  # noqa: E402
from iqm_signed_resolve import COHERENT, TRAIN_QUBITS  # noqa: E402

import iqm_records  # noqa: E402
from parallel import ordered_map  # noqa: E402

CASE = "idle-schedule-train-readout"
QC = "garnet"
QCS = ["garnet:mock", "garnet"]
OPTIONS: dict[str, Any] = {"heralding_mode": "none", "active_reset_cycles": 1}
CALIBRATION_FILES = ("metrics.json", "dynamic-quantum-architecture.json")
SHOTS = 4500
# The owner's approved charge for the job. Billing is ceil(runtime); collect cancels a run within 1.0 s of the
# seconds this buys (iqm_jobs.CANCEL_MARGIN), so the shot schedule plus JOB_SECONDS stays at least
# PLAN_HEADROOM below them, which covers the +1.39 s the retained runtimes ran above their estimates.
MAX_CREDITS = {"garnet": 4.0, "garnet:mock": 0.0}
PRICE = {"garnet": 0.5, "garnet:mock": 0.0}
PLAN_HEADROOM = 2.0
IDLE_TRAIN_QUBITS = ("QB1", "QB20")
IDLE_PULSES = (0, 500, 1000)
Z_RESOLVE = 3.0
TRAIN_P_MIN = 0.001
# The successor's T1 fit keeps delay points at least this many standard errors above zero population, and its
# common-gap test rejects at this chi-square survival.
T1_POINT_SE = 3.0
GAP_P_REJECT = 0.01
# A qubit enters H2 only when its delay fit's chi-square survival is at least T1_FIT_P_MIN and its readout pair leaves
# a positive contrast; the primary verdict needs every pulsed qubit of the case and reads unidentifiable otherwise. H2
# reads its readout correction from the bare pair par-ro0, par-ro1 and not from the train fit, which failed its
# linearity test on 7 of 20 Garnet qubits (results/iqm/idle_schedule_probe_analysis.json).
T1_FIT_P_MIN = 0.001
# The third-length decision pools a subject's qubits over the ones whose own arms and delay fit pass their gates; a
# subject with fewer qubits at a tested length is unidentifiable. The cohort keeps 7 of the 11 retained qubits, and an
# arm enters only when its population lies this many standard errors above zero.
LINE_MIN_COHORT = 7
LINE_ARM_SE = T1_POINT_SE
# The delta method holds the delay fit's weights and the pooling weights fixed. Central differences of the production
# estimators, whose weights follow the data, read the error of a delay-fit rate and of a pooled anchor gap within this
# fraction of it (decision_self_test measures the model device); the within-job deviation vanishes under the line,
# where a change of weights moves nothing, and its derivatives match to 1e-3.
FIXED_WEIGHT_TOLERANCE = 0.10
# The successor's calibration study (study()) draws its binomial replicates from this seed: draw
# docs/evidence/anu_qrng/draw-2026-11-21T184244Z.json, index 0.
CALIBRATION_STUDY_SEED = 50182
STUDY_REPLICATES = 400
STUDY_TRUE_GAPS = (0.0, 14e-9)


@dataclasses.dataclass(frozen=True)
class Profile:
    """The quantum computer a case is built for: its cohort, train qubits, prx length, shots and approved charge."""

    qc: str
    case: str
    question: str
    shots: int
    prx_seconds: float
    train: tuple[str, ...]
    qubits: tuple[str, ...] | None
    max_credits: dict[str, float]
    price: dict[str, float]
    isolated: bool
    delays: tuple[float, ...] = ()
    # Train lengths of every idle layout; 0 is the baseline each other length is read against.
    pulses: tuple[int, ...] = IDLE_PULSES
    # A retained analysis and its run directory, whose counts fix the line g(N) = a + b / N through the gaps at the
    # two anchor lengths, and the subjects (name, qubits, minimum qubits; no qubits means every qubit with a gap at
    # both anchors) the third lengths test it on.
    line_source: str | None = None
    line_run: str | None = None
    line_anchors: tuple[int, int] = (500, 1000)
    line_subjects: tuple[tuple[str, tuple[str, ...], int], ...] = ()

    @property
    def qcs(self) -> list[str]:
        return [f"{self.qc}:mock", self.qc]


GARNET = Profile(
    qc=QC,
    case=CASE,
    question=(
        "Does Garnet schedule a circuit job's gates as soon or as late as possible, read by whether pulsed "
        "qubits relax while an uncoupled qubit runs an identity train, and what over-rotation does every "
        "qubit's prx carry when fitted with its own readout, driven alone and all at once?"
    ),
    shots=SHOTS,
    prx_seconds=DURATIONS["r"],
    train=IDLE_TRAIN_QUBITS,
    qubits=None,
    max_credits=MAX_CREDITS,
    price=PRICE,
    isolated=True,
)
# Emerald's 24 ns prx is its drag_crf_sx implementation's duration in the retained static architecture.
EMERALD = Profile(
    qc="emerald",
    case="idle-schedule-train-readout-emerald",
    question=(
        "Does Emerald schedule a circuit job's gates as soon or as late as possible, read by whether pulsed "
        "qubits relax while an uncoupled qubit runs an identity train, and is the decay beyond the schedule's "
        "prediction one common per-pulse gap or varies by qubit?"
    ),
    shots=4000,
    prx_seconds=24e-9,
    train=("QB20", "QB26"),
    qubits=tuple(f"QB{n}" for n in (5, 10, 14, 18, 20, 24, 26, 30, 34, 37, 42, 44)),
    max_credits={"emerald": 4.5, "emerald:mock": 0.0},
    price={"emerald": 0.75, "emerald:mock": 0.0},
    isolated=False,
)
# The successor reads each measured qubit's T1 in the same job: every qubit gets one prx(pi), then an explicit delay
# instruction on all twelve (IQM's circuit delay, duration in seconds, rounded up to the hardware's step), then the
# joint measure. The pulse train of an idle layout waits N (d + g) for a per-pulse gap g; a delay waits its stated
# duration plus one offset shared by every delay, which the decay's amplitude absorbs. The slope therefore gives T1
# independently of g, and the 1000-pulse arm then gives g itself (evaluate, "h2_gap").
T1_DELAYS = (8e-6, 16e-6, 32e-6, 64e-6)
EMERALD_T1 = dataclasses.replace(
    EMERALD,
    case="idle-schedule-t1-emerald",
    question=(
        "Does Emerald schedule a circuit job's gates as soon or as late as possible, and is the decay beyond the "
        "schedule's prediction a per-pulse timing gap common to the qubits, read against each qubit's T1 measured "
        "by delay circuits in the same job?"
    ),
    max_credits={"emerald": 12.0, "emerald:mock": 0.0},
    delays=T1_DELAYS,
)
# The third-length case tests the line the retained Emerald run's 500 and 1000 pulse means fix: trains of 250 and 2000
# pulses, with the anchor lengths repeated in the same job. The circuits keep the successor's structure: both layouts,
# the readout pair, the parallel trains and the four delay circuits.
THIRD_LENGTHS = (0, 250, 500, 1000, 2000)
EMERALD_THIRD = dataclasses.replace(
    EMERALD_T1,
    case="idle-schedule-third-length-emerald",
    question=(
        "Does the per-pulse gap of Emerald's idle trains follow g(N) = a + b / N, the line through the 500 and 1000 "
        "pulse gaps of the retained run, at train lengths of 250 and 2000 pulses?"
    ),
    max_credits={"emerald": 9.0, "emerald:mock": 0.0},
    pulses=THIRD_LENGTHS,
    line_source="results/iqm/idle_schedule_t1_emerald_analysis.json",
    line_run="results/iqm/runs/2026-11-21T205643Z-emerald-idle-schedule-t1-emerald-probe",
    line_subjects=(("cohort", (), LINE_MIN_COHORT), ("QB24", ("QB24",), 1)),
)
PROFILES = {"garnet": GARNET, "emerald": EMERALD, "emerald-t1": EMERALD_T1, "emerald-third": EMERALD_THIRD}
# Draw docs/evidence/anu_qrng/draw-2026-10-25T001615Z.json, indices 0 and 1 (allocations.json).
SYNTHETIC_SEEDS = (36215, 40623)
# The model device's readout per qubit, (P(1|0), P(0|1)), unlike every qubit's calibrated readout.
SYNTHETIC_READOUT = {"QB6": (0.04, 0.10), "QB11": (0.07, 0.05)}
SYNTHETIC_DEFAULT = (0.02, 0.06)


def prx(qubit: str, angle: float) -> dict[str, Any]:
    return {"name": "prx", "locus": [qubit], "args": {"angle": angle, "phase": 0.0}}


def measure(qubits: list[str]) -> dict[str, Any]:
    return {"name": "measure", "locus": qubits, "args": {"key": "c"}}


def delay(qubits: list[str], seconds: float) -> dict[str, Any]:
    return {"name": "delay", "locus": qubits, "args": {"duration": seconds}}


def delay_name(seconds: float) -> str:
    return f"t1-{round(seconds * 1e6)}us"


def train_pulses(k: int) -> int:
    return 4 * k + 1


def ordered(qubits: Any) -> list[str]:
    return sorted(qubits, key=lambda q: int(q[2:]))


def pulsed_qubits(
    train_qubit: str, calibration: iqm_sim.Calibration, within: tuple[str, ...] | None = None
) -> list[str]:
    """Every qubit of the cohort (the calibration's, unless given) that shares no coupler with the train qubit."""
    return ordered(
        q
        for q in (within or calibration.qubits)
        if q != train_qubit and frozenset((q, train_qubit)) not in calibration.cz
    )


def circuits_of(calibration: iqm_sim.Calibration, profile: Profile = GARNET) -> list[dict[str, Any]]:
    every = ordered(profile.qubits or calibration.qubits)
    circuits: list[dict[str, Any]] = []
    for b in profile.train:
        pulsed = pulsed_qubits(b, calibration, profile.qubits)
        for n in profile.pulses:
            instructions = [*(prx(q, math.pi) for q in pulsed), *(prx(b, math.pi) for _ in range(n))]
            circuits.append({"name": f"idle-{b}-{n}", "instructions": [*instructions, measure(every)]})
    circuits.append({"name": "par-ro0", "instructions": [measure(every)]})
    circuits.append({"name": "par-ro1", "instructions": [*(prx(q, math.pi) for q in every), measure(every)]})
    for k in AMPLIFY_K:
        pulses = [prx(q, math.pi / 2) for _ in range(train_pulses(k)) for q in every]
        circuits.append({"name": f"par-amp-{k}", "instructions": [*pulses, measure(every)]})
    for qubit in TRAIN_QUBITS if profile.isolated else ():
        circuits.append({"name": f"ro0-{qubit}", "instructions": [measure([qubit])]})
        circuits.append({"name": f"ro1-{qubit}", "instructions": [prx(qubit, math.pi), measure([qubit])]})
        for k in AMPLIFY_K:
            pulses = [prx(qubit, math.pi / 2) for _ in range(train_pulses(k))]
            circuits.append({"name": f"amp-{qubit}-{k}", "instructions": [*pulses, measure([qubit])]})
    for seconds in profile.delays:
        instructions = [*(prx(q, math.pi) for q in every), delay(every, seconds), measure(every)]
        circuits.append({"name": delay_name(seconds), "instructions": instructions})
    return circuits


def measured(circuit: dict[str, Any]) -> list[str]:
    return [q for op in circuit["instructions"] if op["name"] == "measure" for q in op["locus"]]


def marginal(circuit: dict[str, Any], qubit: str) -> dict[str, Any]:
    """The instructions that reach one qubit's reading: its own gates and, for timing, those of the qubit with the
    most gates, read in one joint measure. Gates without a coupler act on their qubits alone, and the noise model is
    per qubit, so this marginal reads as the qubit does in the full circuit."""
    counts: dict[str, int] = {}
    for op in circuit["instructions"]:
        if op["name"] == "prx":
            counts[op["locus"][0]] = counts.get(op["locus"][0], 0) + 1
    timing = max(sorted(counts), key=lambda q: counts[q]) if counts else qubit
    keep = [qubit] if timing == qubit else [qubit, timing]
    ops = []
    for op in circuit["instructions"]:
        if op["name"] == "prx" and op["locus"][0] in keep:
            ops.append(op)
        elif op["name"] == "delay" and any(q in keep for q in op["locus"]):
            ops.append({**op, "locus": [q for q in op["locus"] if q in keep]})
    return {"name": f"{circuit['name']}@{qubit}", "instructions": [*ops, measure(keep)]}


def exact(item: tuple[dict[str, Any], str, str, dict[str, float], float]) -> float:
    """Exact <Z> of a circuit's first measured qubit before readout: the calibration's gate noise, idle T1/T2 over
    the given schedule and prx angles scaled by 1 + eps on the named qubits.

    A joint measure is one instruction on the device, so a barrier over its locus aligns its readouts here.
    """
    circuit, calibration_dir, method, over, prx_seconds = item
    calibration = iqm_sim.Calibration.from_directory(Path(calibration_dir))
    index = {q: n for n, q in enumerate(calibration.qubits)}
    model = QuantumCircuit(len(calibration.qubits), 1)
    first = None
    for op in circuit["instructions"]:
        locus = [index[q] for q in op["locus"]]
        if op["name"] == "prx":
            scale = 1 + over.get(op["locus"][0], 0.0)
            model.append(RGate(op["args"]["angle"] * scale, op["args"]["phase"]), locus)
        elif op["name"] == "delay":
            model.delay(op["args"]["duration"], locus, unit="s")
        elif op["name"] == "measure":
            model.barrier(*locus)
            first = locus[0]
            model.measure(locus[0], 0)
        else:
            raise ValueError(f"{circuit['name']}: {op['name']} has no model here")
    if first is None:
        raise ValueError(f"{circuit['name']} measures no qubit")
    target, _ = target_of(calibration, prx_seconds)
    scheduled = relaxed(calibration, transpile(model, target=target, optimization_level=0, scheduling_method=method))
    out = QuantumCircuit(*scheduled.qregs, *scheduled.cregs)
    for instruction in scheduled.data:
        if instruction.operation.name != "measure":
            out.append(instruction.operation, instruction.qubits)
    out.save_probabilities([first])
    simulator = AerSimulator(method="density_matrix", noise_model=calibration.noise_model())
    p = simulator.run(out).result().data()["probabilities"]
    return float(p[0] - p[1])


def readings(
    circuits: list[dict[str, Any]],
    calibration_dir: Path,
    method: str,
    over: dict[str, float],
    prx_seconds: float = DURATIONS["r"],
) -> dict[str, float]:
    """True <Z> of every measured qubit of every circuit, keyed name@qubit."""
    keys = [(c, q) for c in circuits for q in measured(c)]
    values = ordered_map(exact, [(marginal(c, q), str(calibration_dir), method, over, prx_seconds) for c, q in keys])
    return {f"{c['name']}@{q}": value for (c, q), value in zip(keys, values, strict=True)}


def build_from(calibration_dir: Path, profile: Profile = GARNET) -> tuple[dict[str, str], dict[str, Any]]:
    calibration = iqm_sim.Calibration.from_directory(calibration_dir)
    circuits = circuits_of(calibration, profile)
    shots, qc = profile.shots, profile.qc
    files = {f"circuits/{c['name']}.json": dump(c) for c in circuits}
    no_error: dict[str, float] = {}
    true = {
        method: readings(circuits, calibration_dir, method, no_error, profile.prx_seconds)
        for method in ("asap", "alap")
    }
    z = {
        method: {key: read(value, *calibration.readout(key.split("@")[1])) for key, value in values.items()}
        for method, values in true.items()
    }
    idle: dict[str, Any] = {}
    for b in profile.train:
        rows = {}
        for qubit in pulsed_qubits(b, calibration, profile.qubits):
            contrasts = []
            for n in profile.pulses[1:]:
                name, base = f"idle-{b}-{n}@{qubit}", f"idle-{b}-0@{qubit}"
                asap = z["asap"][name] - z["asap"][base]
                alap = z["alap"][name] - z["alap"][base]
                se = math.hypot(*(math.sqrt(max(1 - z["alap"][m] ** 2, 1 / shots) / shots) for m in (name, base)))
                contrasts.append({"pulses": n, "asap": asap, "alap": alap, "separation_se": abs(asap - alap) / se})
            rows[qubit] = {
                "t1_seconds": calibration.values[f"characterization.model.{qubit}.t1_time"],
                "contrasts": contrasts,
            }
        idle[b] = rows
    shot = len(circuits) * ACTIVE_SHOT_SECONDS + sum(
        n * profile.prx_seconds for _ in profile.train for n in profile.pulses
    )
    if profile.delays:
        shot += sum(profile.delays)
    expected = round(shots * shot, 3)
    budget = profile.max_credits[qc] / profile.price[qc]
    if JOB_SECONDS + expected > budget - PLAN_HEADROOM:
        raise ValueError(f"{expected} s of shots plus {JOB_SECONDS} s leave less than {PLAN_HEADROOM} s of {budget} s")
    job = {
        "job": "probe",
        "circuits": [{"file": rel, "sha256": sha256(text.encode())} for rel, text in files.items()],
        "shots": shots,
        # The job compiles against the calibration set the prediction was made from, or fails if it is gone.
        "options": {**OPTIONS, "calibration_set_id": {qc: calibration.set_id}},
        "expected_seconds": expected,
        "max_credits": profile.max_credits,
    }
    prediction = {
        "calibration_set": calibration.set_id,
        "prx_seconds": profile.prx_seconds,
        "idle": idle,
        "z": z,
        "coherent_attribution": {q: COHERENT[q] for q in TRAIN_QUBITS if q in COHERENT and profile.isolated},
        "model": (
            "iqm_sim depolarizing PRX with unheralded readout, idle T1/T2 over ASAP and over ALAP schedules with the "
            "joint measure aligned, exact density matrix per measured qubit"
        ),
    }
    if profile.delays:
        prediction["t1_delays"] = {delay_name(s): s for s in profile.delays}
    if profile.line_source:
        prediction["line"] = line_of(profile)
    files["prediction.json"] = dump(prediction)
    files["cases.json"] = dump(
        {
            "schema": CASE_SCHEMA,
            "case": profile.case,
            "question": profile.question,
            "qcs": profile.qcs,
            "jobs": [job],
            # The approval digest of cases.json covers the prediction the analysis decides against.
            "prediction_sha256": sha256(files["prediction.json"].encode()),
        }
    )
    return files, prediction


def calibration_set_of(folder: Path) -> str:
    """The calibration set a folder's two files both describe; a folder whose metrics and architecture name different
    sets, or whose metrics name none, is refused."""
    architecture = json.loads((folder / "dynamic-quantum-architecture.json").read_text(encoding="utf-8"))
    metrics = json.loads((folder / "metrics.json").read_text(encoding="utf-8"))
    described = metrics.get("describes_id", metrics.get("calibration_set_id"))
    if described is None or described != architecture["calibration_set_id"]:
        raise ValueError(
            f"{folder}: metrics describe set {described}, the architecture is {architecture['calibration_set_id']}"
        )
    return str(described)


def write(directory: Path, live: bool = False, profile: Profile = GARNET, calibration_from: Path | None = None) -> None:
    """Build the case; --live reads the quantum computer's current calibration, calibration_from copies the two files
    of a folder that holds one calibration set (a read made beforehand), otherwise the retained snapshot's copy."""
    calibration_dir = directory / "calibration"
    calibration_dir.mkdir(parents=True, exist_ok=True)
    if live:
        fetch_calibration(calibration_dir, profile.qc)
    else:
        source = calibration_from or iqm_sim.EVIDENCE / profile.qc / "calibration"
        if calibration_from:
            calibration_set_of(calibration_from)
        for name in CALIBRATION_FILES:
            shutil.copyfile(source / name, calibration_dir / name)
    files, prediction = build_from(calibration_dir, profile)
    for stale in (directory / "circuits").glob("*.json") if (directory / "circuits").exists() else []:
        if stale.relative_to(directory).as_posix() not in files:
            stale.unlink()
    for rel, text in files.items():
        path = directory / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    weakest = min(
        c["separation_se"] for rows in prediction["idle"].values() for r in rows.values() for c in r["contrasts"]
    )
    print(json.dumps({"circuits": len(files) - 2, "weakest_separation_se": weakest}))


def check(directory: Path, profile: Profile = GARNET) -> None:
    files, _ = build_from(directory / "calibration", profile)
    present = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
    expected = set(files) | {f"calibration/{name}" for name in CALIBRATION_FILES}
    if present != expected:
        raise ValueError(f"{directory}: files differ from the build: {sorted(present ^ expected)}")
    for rel, text in files.items():
        if (directory / rel).read_text(encoding="utf-8") != text:
            raise ValueError(f"{directory}/{rel} differs from the build")
    print(f"{directory}: matches the build from its retained calibration")


def tally(circuits: list[dict[str, Any]], results: list[dict[str, Any]]) -> dict[str, tuple[int, int]]:
    """(ones, shots) per name@qubit; each shot holds one bit per qubit of the measure's locus, in its order."""
    out: dict[str, tuple[int, int]] = {}
    for circuit, result in zip(circuits, results, strict=True):
        shots = result["c"]
        for position, qubit in enumerate(measured(circuit)):
            out[f"{circuit['name']}@{qubit}"] = (sum(shot[position] for shot in shots), len(shots))
    return out


def fit(item: tuple[dict[str, tuple[int, int]], str, str, str]) -> dict[str, Any]:
    """The joint train fit of one qubit, from (counts, train prefix, readout prefix, qubit)."""
    counts, amp, ro, qubit = item
    eps, se, chi2, e01, e10 = fit_train(
        [train_pulses(k) for k in AMPLIFY_K],
        [z_of(counts, f"{amp}-{k}@{qubit}") for k in AMPLIFY_K],
        z_of(counts, f"{ro}0{'' if ro == 'par-ro' else '-' + qubit}@{qubit}"),
        z_of(counts, f"{ro}1{'' if ro == 'par-ro' else '-' + qubit}@{qubit}"),
    )
    linear = math.isfinite(chi2) and chi2_survival_3(chi2) >= TRAIN_P_MIN
    return {"eps": eps, "eps_se": se, "chi2": chi2, "e01": e01, "e10": e10, "linear": linear}


def evaluate(counts: dict[str, tuple[int, int]], prediction: dict[str, Any]) -> dict[str, Any]:
    """The preregistered decisions H1 and H2 and the descriptive outputs from per name@qubit (ones, shots)."""
    qubits = ordered({key.split("@")[1] for key in counts if key.startswith("par-ro0@")})
    items = [(counts, "par-amp", "par-ro", q) for q in qubits]
    train = [q for q in TRAIN_QUBITS if f"ro0-{q}@{q}" in counts]
    items += [(counts, "amp-" + q, "ro", q) for q in train]
    fits = ordered_map(fit, items)
    parallel = dict(zip(qubits, fits[: len(qubits)], strict=True))
    isolated_fits = dict(zip(train, fits[len(qubits) :], strict=True))
    arms: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for b, rows in prediction["idle"].items():
        arms[b] = {}
        for qubit, row in rows.items():
            arms[b][qubit] = []
            z0, se0, _ = z_of(counts, f"idle-{b}-0@{qubit}")
            for contrast in row["contrasts"]:
                z, se_z, _ = z_of(counts, f"idle-{b}-{contrast['pulses']}@{qubit}")
                observed, se = z - z0, math.hypot(se_z, se0)
                toward = math.copysign(1.0, contrast["asap"] - contrast["alap"])
                score = toward * (observed - (contrast["asap"] + contrast["alap"]) / 2) / se
                verdict = "asap" if score >= Z_RESOLVE else "alap" if score <= -Z_RESOLVE else "unresolved"
                arm = {**contrast, "observed": observed, "se": se, "score": score, "verdict": verdict}
                # The excited population before and after the wait, read through the parallel readout pair.
                e01, e10 = parallel[qubit]["e01"], parallel[qubit]["e10"]
                before, after = (((1 - value) / 2 - e01) / (1 - e01 - e10) for value in (z0, z))
                wait = contrast["pulses"] * prediction["prx_seconds"]
                arm["apparent_t1_seconds"] = wait / math.log(before / after) if 0 < after < before else None
                if "t1_delays" in prediction:
                    # The decay rate ln(before / after) / wait through the bare readout pair (readout_pair), which
                    # stands whether or not the over-rotation model fits the qubit's trains.
                    r01, r10 = readout_pair(counts, qubit)
                    pair = 1 - r01 - r10
                    up, down = (((1 - value) / 2 - r01) / pair for value in (z0, z)) if pair > 0 else (0.0, 0.0)
                    if pair > 0 and 0 < down < up:
                        arm["apparent_rate_per_second"] = math.log(up / down) / wait
                        arm["apparent_rate_se"] = math.hypot(se0 / (2 * pair) / up, se_z / (2 * pair) / down) / wait
                arms[b][qubit].append(arm)
    readings_ = {arm["verdict"] for layout in arms.values() for rows in layout.values() for arm in rows}
    resolved = readings_ - {"unresolved"}
    schedule = "mixed" if len(resolved) > 1 else readings_.pop() if len(readings_) == 1 else "unresolved"
    isolated: dict[str, Any] = {}
    for qubit in train:
        row = isolated_fits[qubit]
        attributed = prediction["coherent_attribution"].get(qubit)
        if attributed is not None and row["linear"]:
            distance = abs(row["eps"] - attributed) / row["eps_se"]
            row["attribution"] = {
                "value": attributed,
                "z": distance,
                "verdict": "consistent" if distance < Z_RESOLVE else "excluded",
            }
        if parallel[qubit]["linear"] and row["linear"]:
            shift = parallel[qubit]["eps"] - row["eps"]
            row["parallel_minus_isolated"] = {"eps": shift, "se": math.hypot(parallel[qubit]["eps_se"], row["eps_se"])}
        isolated[qubit] = row
    report: dict[str, Any] = {
        "h1_schedule": {"verdict": schedule, "arms": arms},
        "h2_isolated_trains": isolated,
        "parallel_trains": parallel,
    }
    if "t1_delays" in prediction:
        pairs = {q: readout_pair(counts, q) for q in qubits}
        t1 = {q: t1_fit(counts, q, {"e01": pairs[q][0], "e10": pairs[q][1]}, prediction["t1_delays"]) for q in qubits}
        calibrated = {q: row["t1_seconds"] for rows in prediction["idle"].values() for q, row in rows.items()}
        for qubit, fitted in t1.items():
            if fitted.get("t1_seconds") is not None and qubit in calibrated:
                # Descriptive: the delay-measured T1 per requested delay second over the calibration copy's T1.
                fitted["over_calibrated"] = fitted["t1_seconds"] / calibrated[qubit]
        report["t1_delay"] = t1
        valid = {q for q in qubits if 1 - sum(pairs[q]) > 0 and usable_t1(t1[q])}
        report["h2_gap"] = gap_test(arms, t1, prediction["prx_seconds"], schedule, set(calibrated), valid)
        if "line" in prediction:
            report["h3_line"] = line_decision(counts, prediction, arms, t1)
    return report


def readout_pair(counts: dict[str, tuple[int, int]], qubit: str) -> tuple[float, float]:
    """(P(1|0), P(0|1)) of one qubit from the bare readout pair par-ro0 and par-ro1 of the parallel block."""
    z0, _, _ = z_of(counts, f"par-ro0@{qubit}")
    z1, _, _ = z_of(counts, f"par-ro1@{qubit}")
    return (1 - z0) / 2, (1 + z1) / 2


def usable_t1(fitted: dict[str, Any]) -> bool:
    """A delay fit that gives a rate and whose chi-square survival is at least T1_FIT_P_MIN."""
    from scipy.stats import chi2 as chi2_law

    if fitted.get("t1_seconds") is None:
        return False
    dof = fitted["dof"]
    return dof < 1 or float(chi2_law.sf(fitted["chi2"], dof)) >= T1_FIT_P_MIN


def t1_fit(
    counts: dict[str, tuple[int, int]], qubit: str, readout: dict[str, Any], delays: dict[str, float]
) -> dict[str, Any]:
    """One qubit's T1 from its delay circuits: the excited population through the parallel readout pair, fitted as
    A exp(-t / T1) by weighted least squares on its logarithm over the points at least T1_POINT_SE standard errors
    above zero. The fit uses the delay circuits alone, so the offset a delay instruction adds is common to its
    points and enters A only."""
    e01, e10 = readout["e01"], readout["e10"]
    scale = 1 - e01 - e10
    if scale <= 0:
        # A readout pair without contrast carries no population; the qubit is excluded from H2.
        return {"t1_seconds": None, "points": 0}
    points = []
    for name, seconds in delays.items():
        z, se, _ = z_of(counts, f"{name}@{qubit}")
        p, se_p = ((1 - z) / 2 - e01) / scale, se / (2 * scale)
        if p > T1_POINT_SE * se_p:
            points.append((seconds, math.log(p), se_p / p))
    if len(points) < 3:
        return {"t1_seconds": None, "points": len(points)}
    t = np.array([x[0] for x in points])
    y = np.array([x[1] for x in points])
    w = np.array([1 / x[2] ** 2 for x in points])
    design = np.stack([np.ones_like(t), -t], axis=1)
    normal = design.T @ (design * w[:, None])
    coef = np.linalg.solve(normal, design.T @ (w * y))
    cov = np.linalg.inv(normal)
    rate, rate_se = float(coef[1]), math.sqrt(float(cov[1, 1]))
    chi2 = float(np.sum(w * (y - design @ coef) ** 2))
    if rate <= 0:
        return {"t1_seconds": None, "points": len(points), "rate_per_second": rate, "chi2": chi2}
    return {
        "t1_seconds": 1 / rate,
        "t1_se_seconds": rate_se / rate**2,
        "rate_per_second": rate,
        "rate_se": rate_se,
        "amplitude": math.exp(float(coef[0])),
        "chi2": chi2,
        "dof": len(points) - 2,
        "points": len(points),
    }


def gap_test(
    arms: dict[str, dict[str, list[dict[str, Any]]]],
    t1: dict[str, dict[str, Any]],
    prx_seconds: float,
    schedule: str,
    registered: set[str],
    valid: set[str],
) -> dict[str, Any]:
    """H2 of the successor: the per-pulse gap g of each pulsed qubit from its longest train, g = d (k / k_T1 - 1)
    with k the train's decay rate per second of nominal pulse time and k_T1 the qubit's delay-measured rate; a common
    g is rejected when the chi-square of the qubits' g about their weighted mean has survival below GAP_P_REJECT.
    The shorter train repeats the estimate as a stationarity check. Under any schedule but asap the trains carry no
    decay to read and the test reports unidentifiable; so does a case in which a registered pulsed qubit lacks a valid
    readout fit, a usable delay fit or a decay rate on every train, since the preregistered test covers all of them.
    T1 here is per requested delay second: a delay realized as a t + b with a != 1 scales it, and no reading of this
    job detects a."""
    from scipy.stats import chi2 as chi2_law

    if schedule != "asap":
        return {"verdict": "unidentifiable", "schedule": schedule}
    lengths = {arm["pulses"] for layout in arms.values() for row in layout.values() for arm in row}
    rated = {
        q
        for q in valid
        if all("apparent_rate_per_second" in arm for layout in arms.values() for arm in layout.get(q, []))
        and any(q in layout for layout in arms.values())
    }
    excluded = sorted(registered - rated, key=lambda q: int(q[2:]))
    by_count: dict[int, dict[str, dict[str, float]]] = {}
    for layout in arms.values():
        for qubit, row in layout.items():
            if qubit not in rated:
                continue
            for arm in row:
                if "apparent_rate_per_second" not in arm:
                    continue
                # Pool a qubit's layouts by inverse variance of the train's rate; its T1 is shared by both.
                held = by_count.setdefault(arm["pulses"], {}).setdefault(qubit, {"w": 0.0, "wk": 0.0})
                weight = 1 / arm["apparent_rate_se"] ** 2
                held["w"] += weight
                held["wk"] += weight * arm["apparent_rate_per_second"]
    out: dict[str, Any] = {}
    for pulses, pooled in sorted(by_count.items()):
        gaps = {}
        for qubit, held in pooled.items():
            k, se_k = held["wk"] / held["w"], 1 / math.sqrt(held["w"])
            k1, se_k1 = t1[qubit]["rate_per_second"], t1[qubit]["rate_se"]
            gap = prx_seconds * (k / k1 - 1)
            se = prx_seconds * math.hypot(se_k / k1, k * se_k1 / k1**2)
            gaps[qubit] = {"gap_seconds": gap, "se_seconds": se}
        weights = {q: 1 / g["se_seconds"] ** 2 for q, g in gaps.items()}
        mean = sum(weights[q] * g["gap_seconds"] for q, g in gaps.items()) / sum(weights.values())
        chi2 = sum(weights[q] * (g["gap_seconds"] - mean) ** 2 for q, g in gaps.items())
        dof = len(gaps) - 1
        survival = float(chi2_law.sf(chi2, dof)) if dof > 0 else None
        out[str(pulses)] = {
            "gaps": gaps,
            "mean_seconds": mean,
            "mean_se_seconds": 1 / math.sqrt(sum(weights.values())),
            "chi2": chi2,
            "dof": dof,
            "survival": survival,
        }
    longest = out.get(str(max(lengths))) if by_count and lengths else None
    if excluded or longest is None or longest["survival"] is None:
        return {"verdict": "unidentifiable", "schedule": schedule, "excluded": excluded, "trains": out}
    verdict = "common" if longest["survival"] >= GAP_P_REJECT else "per-qubit"
    report: dict[str, Any] = {"verdict": verdict, "schedule": schedule, "excluded": excluded, "trains": out}
    counts = sorted(by_count)
    if len(counts) > 1:
        # The stationary gap model predicts one mean at every train length; a difference beyond Z_RESOLVE combined
        # standard errors falsifies it. Both means cover the same qubits and share each qubit's T1 and readout, so
        # the combined error is not the difference's; study() measures the test's false-alarm rate.
        short, long_ = out[str(counts[0])], out[str(counts[-1])]
        z = (long_["mean_seconds"] - short["mean_seconds"]) / math.hypot(
            long_["mean_se_seconds"], short["mean_se_seconds"]
        )
        report["stationarity"] = {"z": z, "verdict": "stationary" if abs(z) <= Z_RESOLVE else "falsified"}
    return report


# The third-length decision. Every quantity below is a smooth function of independent binomial counts (one per circuit
# and measured qubit), so a Dual carries each value with its first-order response to those counts; the covariance of any
# two values is then the delta method, sum over counts of (d value1 / d count) (d value2 / d count) Var(count).
READOUT_PREFIX = "par-ro"


class Dual:
    """A value with its derivative with respect to every count it depends on (forward-mode differentiation).

    A count is the proportion p of one-readings of one circuit on one qubit, keyed by its name@qubit, with the binomial
    variance max(p (1 - p), 1 / (4 n)) / n that z_one uses. Cov(f, g) = sum_k f.grad[k] g.grad[k] Var(p_k)."""

    __slots__ = ("grad", "value")

    def __init__(self, value: float, grad: dict[str, float] | None = None) -> None:
        self.value = value
        self.grad: dict[str, float] = grad if grad is not None else {}

    @staticmethod
    def lift(other: Dual | float) -> Dual:
        return other if isinstance(other, Dual) else Dual(float(other))

    def __add__(self, other: Dual | float) -> Dual:
        o = Dual.lift(other)
        return Dual(self.value + o.value, linear(self, 1.0, o, 1.0))

    def __radd__(self, other: float) -> Dual:
        return self + other

    def __sub__(self, other: Dual | float) -> Dual:
        o = Dual.lift(other)
        return Dual(self.value - o.value, linear(self, 1.0, o, -1.0))

    def __rsub__(self, other: float) -> Dual:
        return Dual.lift(other) - self

    def __neg__(self) -> Dual:
        return Dual(-self.value, {k: -v for k, v in self.grad.items()})

    def __mul__(self, other: Dual | float) -> Dual:
        o = Dual.lift(other)
        return Dual(self.value * o.value, linear(self, o.value, o, self.value))

    def __rmul__(self, other: float) -> Dual:
        return self * other

    def __truediv__(self, other: Dual | float) -> Dual:
        o = Dual.lift(other)
        inverse = 1.0 / o.value
        return Dual(self.value * inverse, linear(self, inverse, o, -self.value * inverse * inverse))


def linear(a: Dual, ca: float, b: Dual, cb: float) -> dict[str, float]:
    out = {k: ca * v for k, v in a.grad.items()}
    for k, v in b.grad.items():
        out[k] = out.get(k, 0.0) + cb * v
    return out


def combo(terms: list[tuple[float, Dual]]) -> Dual:
    """The sum of c * f over (c, f) in terms."""
    grad: dict[str, float] = {}
    for c, f in terms:
        for k, v in f.grad.items():
            grad[k] = grad.get(k, 0.0) + c * v
    return Dual(sum(c * f.value for c, f in terms), grad)


def dlog(x: Dual) -> Dual:
    return Dual(math.log(x.value), {k: v / x.value for k, v in x.grad.items()})


def proportion(counts: Counts, name: str) -> Dual:
    ones, shots = counts[name]
    return Dual(ones / shots, {name: 1.0})


def shot_variance(counts: Counts, name: str) -> float:
    ones, shots = counts[name]
    p = ones / shots
    return max(p * (1 - p), 0.25 / shots) / shots


def shared_only(key: str) -> bool:
    return not key.startswith(READOUT_PREFIX)


def variance(f: Dual, counts: Counts, keep: Any = None) -> float:
    return sum(g * g * shot_variance(counts, k) for k, g in f.grad.items() if keep is None or keep(k))


def covariance(f: Dual, g: Dual, counts: Counts, keep: Any = None) -> float:
    return sum(
        v * g.grad[k] * shot_variance(counts, k) for k, v in f.grad.items() if k in g.grad and (keep is None or keep(k))
    )


@dataclasses.dataclass
class Prep:
    """One pulsed qubit of a run: its delay-measured T1 rate k1 and, per layout, the log of the readout-corrected
    excited population ln(p - r) after each train length (None where the arm is gated out)."""

    k1: Dual | None
    usable: bool
    cells: dict[str, dict[int, Dual | None]]
    asap: dict[str, dict[int, bool]]


def rate_dual(counts: Counts, qubit: str, delays: dict[str, float]) -> Dual | None:
    """The T1 rate of t1_fit as a Dual: the weighted least-squares slope of ln((p_j - r) / (s - r)) against minus the
    delay, on the points t1_fit keeps, with the weights it uses held fixed. r and s are the bare readout pair's
    one-fractions par-ro0 and par-ro1, so the rate carries their shot variance, which t1_fit's rate_se leaves out."""
    r, s = proportion(counts, f"par-ro0@{qubit}"), proportion(counts, f"par-ro1@{qubit}")
    scale = s - r
    if scale.value <= 0:
        return None
    seconds, logs, weights = [], [], []
    for name, delay_seconds in delays.items():
        key = f"{name}@{qubit}"
        population = (proportion(counts, key) - r) / scale
        se = math.sqrt(shot_variance(counts, key)) / scale.value
        if population.value > T1_POINT_SE * se:
            seconds.append(delay_seconds)
            logs.append(dlog(population))
            weights.append((population.value / se) ** 2)
    if len(logs) < 3:
        return None
    t, w = np.array(seconds), np.array(weights)
    design = np.stack([np.ones_like(t), -t], axis=1)
    row = (np.linalg.inv(design.T @ (design * w[:, None])) @ design.T * w)[1]
    rate = combo([(float(c), y) for c, y in zip(row, logs, strict=True)])
    return rate if rate.value > 0 else None


def prepare_all(
    counts: Counts,
    prediction: dict[str, Any],
    arms: dict[str, dict[str, list[dict[str, Any]]]] | None,
    t1: dict[str, dict[str, Any]] | None,
) -> dict[str, Prep]:
    """Every pulsed qubit's Prep. A qubit is usable when its delay fit passes usable_t1 (when t1 is given) and gives a
    rate; an arm is gated out unless its population exceeds LINE_ARM_SE standard errors of itself and r (the logarithm
    has no first-order error otherwise) and, when arms are given, its own schedule verdict is asap."""
    out: dict[str, Prep] = {}
    for qubit in ordered({q for rows in prediction["idle"].values() for q in rows}):
        k1 = rate_dual(counts, qubit, prediction["t1_delays"])
        usable = k1 is not None and (t1 is None or usable_t1(t1[qubit]))
        cells: dict[str, dict[int, Dual | None]] = {}
        asap: dict[str, dict[int, bool]] = {}
        r = proportion(counts, f"par-ro0@{qubit}")
        for b, rows in prediction["idle"].items():
            if qubit not in rows:
                continue
            lengths = [0, *(c["pulses"] for c in rows[qubit]["contrasts"])]
            cells[b], asap[b] = {}, {}
            for n in lengths:
                key = f"idle-{b}-{n}@{qubit}"
                population = proportion(counts, key) - r if key in counts else None
                gated = (
                    population is None
                    or population.value <= 0
                    or (n > 0 and population.value <= LINE_ARM_SE * math.sqrt(variance(population, counts)))
                )
                cells[b][n] = None if gated or population is None else dlog(population)
                verdicts = {a["pulses"]: a["verdict"] for a in (arms or {}).get(b, {}).get(qubit, [])}
                asap[b][n] = arms is None or n == 0 or verdicts.get(n) == "asap"
        out[qubit] = Prep(k1, usable, cells, asap)
    return out


def contrast_of(n: int, anchors: tuple[int, int] | list[int]) -> dict[int, float]:
    """The coefficients c of the contrast g(n) - alpha g(a) - (1 - alpha) g(b): the deviation of the gap at n from the
    line through the gaps at the anchors a and b, with c summing to zero and sum c / N zero."""
    a, b = anchors
    alpha = (1 / n - 1 / b) / (1 / a - 1 / b)
    return {n: 1.0, a: -alpha, b: -(1 - alpha)}


def pair_gap(prep: Prep, b: str, near: int, far: int, d: float) -> Dual | None:
    """The per-pulse gap of layout b between train lengths near and far,
    g = (ln up_near - ln up_far) / (k1 (far - near)) - d with up the readout-corrected excited population; near = 0 is
    gap_test's gap g(far), and 0 < near gives the gap of the nonzero lengths, which a fixed population drop between
    N = 0 and N > 0 leaves out."""
    logs = pair_logs(prep, b, near, far)
    if prep.k1 is None or logs is None:
        return None
    return (logs[0] - logs[1]) / (prep.k1 * (far - near)) - d


def pair_logs(prep: Prep, b: str, near: int, far: int) -> tuple[Dual, Dual] | None:
    """The logs of the excited population of layout b after near and after far pulses, None where either arm is gated
    out or has a schedule verdict other than asap."""
    cell = prep.cells[b]
    first, second = cell.get(near), cell.get(far)
    if first is None or second is None or not (prep.asap[b].get(near, True) and prep.asap[b].get(far, True)):
        return None
    return first, second


def qubit_gap(
    counts: Counts, prep: Prep, near: int, far: int, d: float, layouts: tuple[str, ...] | None = None
) -> Dual | None:
    """pair_gap pooled over the qubit's layouts by the inverse variance of each layout's decay rate (shot variance
    alone), as gap_test pools its rates."""
    items = []
    for b in prep.cells:
        if layouts and b not in layouts:
            continue
        gap, logs = pair_gap(prep, b, near, far, d), pair_logs(prep, b, near, far)
        if gap is not None and logs is not None:
            rate = (logs[0] - logs[1]) / ((far - near) * d)
            items.append((1 / variance(rate, counts, shared_only), gap))
    total = sum(w for w, _ in items)
    return combo([(w / total, g) for w, g in items]) if items else None


def cohort_gap(
    counts: Counts, preps: dict[str, Prep], qubits: list[str], near: int, far: int, d: float
) -> tuple[Dual | None, list[str]]:
    """The inverse-variance mean over the qubits that have a gap, weighted by each gap's shot variance as the retained
    analysis weights its qubits, and the qubits it covers; the Dual carries the full covariance."""
    members, items = [], []
    for q in qubits:
        gap = qubit_gap(counts, preps[q], near, far, d) if q in preps and preps[q].usable else None
        if gap is not None:
            members.append(q)
            items.append((1 / variance(gap, counts, shared_only), gap))
    total = sum(w for w, _ in items)
    return (combo([(w / total, g) for w, g in items]) if items else None), members


def contrast_reading(
    counts: Counts,
    preps: dict[str, Prep],
    qubits: list[str],
    coefficients: dict[int, float],
    layouts: tuple[str, ...] | None = None,
) -> dict[str, Any] | None:
    """The contrast of coefficients c over the qubits' layouts: L = sum c_i g(N_i) = -(1 / k1) sum c_i ln(p_i - r) / N_i
    per (qubit, layout) cell, where the baseline arm and the readout contrast s - r cancel because sum c_i / N_i = 0
    and sum c_i = 0.

    Covariance. The counts of a cell are independent binomial proportions: the arms p_i at the contrast's lengths, the
    bare readout one-fraction r (par-ro0, shared by the qubit's layouts, by every arm and by k1), the one-fraction s
    (par-ro1) and the delay circuits' p_j behind k1. With Var(p) = max(p (1 - p), 1 / (4 n)) / n the delta method gives
    dL/dp_i = -c_i / (N_i k1 (p_i - r)), dL/dr = (1 / k1) sum c_i / (N_i (p_i - r)) + (dL/dk1)(dk1/dr), dL/dk1 = -L / k1
    and dk1/dp_j, dk1/dr, dk1/ds from the weighted least-squares slope of ln((p_j - r) / (s - r)) against minus the
    delay (rate_dual); Var(L) = sum_k (dL/dk)^2 Var(k), and Cov(L, L') sums the products over the counts two contrasts
    share (the arms at 500 and 1000 pulses, r, k1). Cells pool by inverse variance within a qubit and qubits by inverse
    variance of the qubit's value, with the weights held fixed; the Duals carry these sums. None without a cell."""
    members, values = [], []
    for q in qubits:
        prep = preps.get(q)
        if prep is None or not prep.usable or prep.k1 is None:
            continue
        cells = []
        for b, cell in prep.cells.items():
            if layouts and b not in layouts:
                continue
            terms = [(c / n, cell.get(n)) for n, c in coefficients.items()]
            if any(log is None for _, log in terms) or not all(prep.asap[b].get(n, True) for n in coefficients):
                continue
            cells.append(-combo([(w, log) for w, log in terms if log is not None]) / prep.k1)
        if cells:
            weights = [1 / variance(c, counts) for c in cells]
            values.append(combo([(w / sum(weights), c) for w, c in zip(weights, cells, strict=True)]))
            members.append(q)
    if not values:
        return None
    weights = [1 / variance(v, counts) for v in values]
    total = combo([(w / sum(weights), v) for w, v in zip(weights, values, strict=True)])
    se = math.sqrt(variance(total, counts))
    return {
        "qubits": members,
        "weights": {q: w / sum(weights) for q, w in zip(members, weights, strict=True)},
        "value_seconds": total.value,
        "se_seconds": se,
        "z": total.value / se,
        "_dual": total,
    }


@functools.cache
def reference_report(run: str) -> tuple[Counts, dict[str, Any], dict[str, Any]]:
    """The retained run's counts, its prediction and the analysis of them: the reference of the line."""
    run_dir = ROOT / run
    counts = counts_of_run(run_dir)
    prediction = json.loads((run_dir / "prediction.json").read_text(encoding="utf-8"))
    return counts, prediction, evaluate(counts, prediction)


def reference_of(run: str) -> tuple[Counts, dict[str, Prep], float]:
    """The retained run's counts and Preps and its prx length."""
    counts, prediction, report = reference_report(run)
    preps = prepare_all(counts, prediction, report["h1_schedule"]["arms"], report["t1_delay"])
    return counts, preps, prediction["prx_seconds"]


def required[T](value: T | None, what: str) -> T:
    if value is None:
        raise ValueError(f"no reading of {what}")
    return value


def gap_value(f: Dual, counts: Counts) -> dict[str, float]:
    return {"gap_seconds": f.value, "se_seconds": math.sqrt(variance(f, counts))}


def line_of(profile: Profile) -> dict[str, Any]:
    """The retained line g(N) = a + b / N through the two anchor lengths, for each subject, with the standard error that
    the retained run's own counts give (full covariance of its two anchor gaps) and the line's offset and per-train
    term, the gap it predicts at every tested length and the per-pulse gap its nonzero lengths give."""
    path = ROOT / (profile.line_source or "")
    run = ROOT / (profile.line_run or "")
    counts, preps, d = reference_of(profile.line_run or "")
    trains = json.loads(path.read_bytes())["h2_gap"]["trains"]
    a, b = profile.line_anchors
    tested = [n for n in profile.pulses if n > 0 and n not in (a, b)]
    subjects: dict[str, Any] = {}
    for name, qubits, minimum in profile.line_subjects:
        named = ordered(qubits or set(trains[str(a)]["gaps"]) & set(trains[str(b)]["gaps"]))
        for n in (a, b):
            for qubit in named:
                held = trains[str(n)]["gaps"][qubit]
                mine = required(qubit_gap(counts, preps[qubit], 0, n, d), f"{qubit} at {n} pulses")
                if not same(
                    [mine.value, math.sqrt(variance(mine, counts, shared_only))],
                    [held["gap_seconds"], held["se_seconds"]],
                ):
                    raise ValueError(
                        f"{qubit} at {n} pulses: the retained run's counts do not reproduce {profile.line_source}"
                    )
        ga, gb = (required(cohort_gap(counts, preps, named, 0, n, d)[0], f"{name} at {n} pulses") for n in (a, b))
        duals = {a: ga, b: gb}
        slope = required(cohort_gap(counts, preps, named, a, b, d)[0], f"{name} between the anchors")
        per_train = (ga.value - gb.value) / (1 / a - 1 / b)
        predicted = {}
        for n in tested:
            alpha = (1 / n - 1 / b) / (1 / a - 1 / b)
            predicted[str(n)] = gap_value(combo([(alpha, ga), (1 - alpha, gb)]), counts)
        subjects[name] = {
            "qubits": named,
            "min_qubits": minimum,
            "retained": {str(n): gap_value(duals[n], counts) for n in (a, b)},
            "offset_seconds": gb.value - per_train / b,
            "per_train_seconds": per_train,
            "predicted": predicted,
            "nonzero_gap": gap_value(slope, counts),
        }
    return {
        "source": profile.line_source,
        "source_sha256": sha256(path.read_bytes()),
        "run": profile.line_run,
        "run_measurements_sha256": sha256((run / "raw/measurements.json").read_bytes()),
        "anchors": [a, b],
        "tested": tested,
        "z_reject": Z_RESOLVE,
        "arm_se": LINE_ARM_SE,
        "contrasts": {str(n): {str(k): c for k, c in contrast_of(n, (a, b)).items()} for n in tested},
        "subjects": subjects,
    }


def compare(mine: Dual, counts: Counts, theirs: Dual, other: Counts, z_reject: float) -> dict[str, Any]:
    """New value against a reference of an independent run, in standard errors of their combined variance."""
    se = math.sqrt(variance(mine, counts) + variance(theirs, other))
    z = (mine.value - theirs.value) / se
    return {
        "observed_seconds": mine.value,
        "reference_seconds": theirs.value,
        "se_seconds": se,
        "z": z,
        "outside": abs(z) > z_reject,
    }


def line_decision(
    counts: Counts,
    prediction: dict[str, Any],
    arms: dict[str, dict[str, list[dict[str, Any]]]],
    t1: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """The decision of the third-length case, h3_line, from the run's own counts.

    Primary reading, within the job. For each tested length n the deviation of the gap from the line through the same
    job's gaps at the anchors, L(n) = g(n) - alpha g(a) - (1 - alpha) g(b) (contrast_of), pooled over the subject's
    qubits (contrast_reading). L is the contrast of g against 1 / N, so it vanishes when ln(population) is linear in N
    (g = a + b / N) and is blind to the baseline arm, to the population drop between N = 0 and N > 0 and to the readout
    contrast. Its error is the delta method over the arms at its lengths, the qubit's bare readout one-fraction r and
    the delay circuits behind k1. The per-cell form is -(1 / k1) sum c_i ln(p_i - r) / N_i.

    Secondary readings, deciding nothing but anchors-moved: the subject's gaps at the anchors against the retained
    run's (anchors), at the tested lengths against the retained line (retained_line), and the per-pulse gap between the
    first and last tested lengths against the retained run's between its anchors (nonzero_gap).

    Subject verdict: unidentifiable when a tested length has fewer than the subject's min_qubits qubits (a qubit
    drops out on its own delay fit, readout pair, arm population or arm schedule verdict, and no other qubit's reading
    enters); off-line when a contrast lies more than z_reject standard errors from zero; anchors-moved when an anchor
    gap lies more than z_reject combined standard errors from the retained value; on-line otherwise. The case verdict
    is off-line when any subject is off-line, otherwise the cohort's."""
    line = prediction["line"]
    d = prediction["prx_seconds"]
    z_reject = line["z_reject"]
    anchors = line["anchors"]
    preps = prepare_all(counts, prediction, arms, t1)
    ref_counts, ref_preps, ref_d = reference_of(line["run"])
    subjects: dict[str, Any] = {}
    for name, spec in line["subjects"].items():
        rows: dict[str, Any] = {}
        for n in line["tested"]:
            coefficients = contrast_of(n, anchors)
            reading = contrast_reading(counts, preps, spec["qubits"], coefficients)
            row: dict[str, Any] = {"qubits": [], "enough": False}
            if reading is not None:
                reading.pop("_dual")
                row = {**reading, "enough": len(reading["qubits"]) >= spec["min_qubits"]}
                row["outside"] = abs(reading["z"]) > z_reject
                row["by_layout"] = {
                    b: {k: v for k, v in alt.items() if k != "_dual"}
                    for b in prediction["idle"]
                    if (alt := contrast_reading(counts, preps, spec["qubits"], coefficients, (b,))) is not None
                }
            rows[str(n)] = row
        secondary: dict[str, Any] = {}
        for n in (*anchors, *line["tested"]):
            mine, members = cohort_gap(counts, preps, spec["qubits"], 0, n, d)
            if mine is None:
                continue
            if n in anchors:
                theirs, _ = cohort_gap(ref_counts, ref_preps, members, 0, n, ref_d)
            else:
                alpha = (1 / n - 1 / anchors[1]) / (1 / anchors[0] - 1 / anchors[1])
                ga, _ = cohort_gap(ref_counts, ref_preps, members, 0, anchors[0], ref_d)
                gb, _ = cohort_gap(ref_counts, ref_preps, members, 0, anchors[1], ref_d)
                theirs = combo([(alpha, ga), (1 - alpha, gb)]) if ga is not None and gb is not None else None
            if theirs is not None:
                secondary[str(n)] = {
                    "kind": "anchor" if n in anchors else "line",
                    **compare(mine, counts, theirs, ref_counts, z_reject),
                    "qubits": members,
                }
        first, last = min(line["tested"]), max(line["tested"])
        mine, members = cohort_gap(counts, preps, spec["qubits"], first, last, d)
        theirs, _ = cohort_gap(ref_counts, ref_preps, members, anchors[0], anchors[1], ref_d)
        nonzero = (
            compare(mine, counts, theirs, ref_counts, z_reject) if mine is not None and theirs is not None else None
        )
        measured_rows = [r for r in rows.values()]
        if not measured_rows or any(not r["enough"] for r in measured_rows):
            verdict = "unidentifiable"
        elif any(r["outside"] for r in measured_rows):
            verdict = "off-line"
        elif any(r["outside"] for r in secondary.values() if r["kind"] == "anchor"):
            verdict = "anchors-moved"
        else:
            verdict = "on-line"
        subjects[name] = {"verdict": verdict, "contrasts": rows, "secondary": secondary, "nonzero_gap": nonzero}
    verdicts = {name: s["verdict"] for name, s in subjects.items()}
    if "off-line" in verdicts.values():
        verdict = "off-line"
    else:
        verdict = verdicts["cohort"]
    return {"verdict": verdict, "z_reject": z_reject, "subjects": subjects}


def counts_of_run(run_dir: Path) -> Counts:
    """The (ones, shots) per name@qubit of a run's retained circuits and measurements."""
    records = iqm_records.load_run(run_dir)
    case, submission = records.json_of("cases.json"), records.json_of("submission.json")
    row = next(r for r in case["jobs"] if r["job"] == submission["job"])
    circuits = [json.loads((run_dir / entry["file"]).read_text(encoding="utf-8")) for entry in row["circuits"]]
    return tally(circuits, records.json_of("raw/measurements.json"))


def analyze(run_dir: Path) -> dict[str, Any]:
    import iqm_jobs

    records = iqm_records.load_run(run_dir)

    facts = iqm_jobs.run_facts(run_dir)
    submission = records.json_of("submission.json")
    record = records.json_of("raw/job.json")
    case = records.json_of("cases.json")
    prediction_bytes = (run_dir / "prediction.json").read_bytes()
    if sha256(prediction_bytes) != case.get("prediction_sha256"):
        raise ValueError(f"{run_dir}/prediction.json is not the prediction cases.json binds")
    prediction = json.loads(prediction_bytes)
    if facts["statuses"] != {"completed": 1}:
        raise ValueError(f"{run_dir}: the job is {sorted(facts['statuses'])}; the analysis reads completed jobs")
    # Mock outcomes are random bits and never enter the analysis.
    profile = next((p for p in PROFILES.values() if p.case == case.get("case")), GARNET)
    if submission["qc"] != profile.qc or case.get("case") != profile.case:
        raise ValueError(
            f"{run_dir}: a {case.get('case')} run on {submission['qc']}, not a {profile.case} run on {profile.qc}"
        )
    if record["compilation"]["calibration_set_id"] != prediction["calibration_set"]:
        raise ValueError(f"{run_dir}: compiled against another calibration set than the prediction's")
    counts = counts_of_run(run_dir)
    return {
        "schema": "iqm-idle-schedule-probe-analysis-v1",
        "run": run_dir.name,
        "calibration_set": record["compilation"]["calibration_set_id"],
        "estimate_seconds": record["compilation"]["execution_runtime_estimate_seconds"],
        "runtime_seconds": record["metrics"]["runtime_seconds"],
        "billed_seconds": record["metrics"]["billed_seconds"],
        "charge": facts["charge"],
        **evaluate(counts, prediction),
    }


def synthetic(
    circuits: list[dict[str, Any]],
    calibration_dir: Path,
    method: str,
    eps: dict[str, float],
    seed: int,
    profile: Profile = GARNET,
) -> dict[str, tuple[int, int]]:
    """Counts of a model device: the calibration's gate noise and relaxation over one schedule, the over-rotations
    eps and SYNTHETIC_READOUT, sampled at the profile's shots."""
    rng = np.random.default_rng(seed)
    counts = {}
    for key, value in readings(circuits, calibration_dir, method, eps, profile.prx_seconds).items():
        e01, e10 = SYNTHETIC_READOUT.get(key.split("@")[1], SYNTHETIC_DEFAULT)
        counts[key] = (int(rng.binomial(profile.shots, (1 - read(value, e01, e10)) / 2)), profile.shots)
    return counts


def expected_ones(
    circuits: list[dict[str, Any]], calibration_dir: Path, method: str, eps: dict[str, float], prx_seconds: float
) -> dict[str, float]:
    """P(read 1) per name@qubit on the model device of synthetic(): its gate noise, relaxation and SYNTHETIC_READOUT."""
    out = {}
    for key, value in readings(circuits, calibration_dir, method, eps, prx_seconds).items():
        e01, e10 = SYNTHETIC_READOUT.get(key.split("@")[1], SYNTHETIC_DEFAULT)
        out[key] = (1 - read(value, e01, e10)) / 2
    return out


def study_replicate(item: tuple[dict[str, float], int, int, dict[str, Any], int]) -> dict[str, Any]:
    """One binomial replicate of the model device, evaluated; seed is the replicate's spawned generator entropy."""
    ones, shots, entropy, prediction, index = item
    rng = np.random.default_rng(np.random.SeedSequence(entropy, spawn_key=(index,)))
    keys = sorted(ones)
    drawn = rng.binomial(shots, [ones[k] for k in keys])
    return evaluate({k: (int(n), shots) for k, n in zip(keys, drawn, strict=True)}, prediction)


def study(case_dir: Path) -> dict[str, Any]:
    """Calibration study of the successor's H2 estimator on the case's own calibration and circuits. For a device
    whose pulses last the prediction's d plus each gap of STUDY_TRUE_GAPS: the noise-free reading (every count at
    its expected value, rounded, at the case's shots) and STUDY_REPLICATES binomial replicates at the case's shots,
    drawn from CALIBRATION_STUDY_SEED. It records the mean gap's bias, the coverage of the mean +- one standard error,
    the common-gap test's rejection rate at GAP_P_REJECT (every planted device has one common gap, so each rejection is
    false), the stationarity test's false-alarm rate, and the spread of the per-qubit gap and T1 z-scores."""
    calibration_dir = case_dir / "calibration"
    calibration = iqm_sim.Calibration.from_directory(calibration_dir)
    files, prediction = build_from(calibration_dir, EMERALD_T1)
    circuits = [json.loads(text) for rel, text in files.items() if rel.startswith("circuits/")]
    shots = EMERALD_T1.shots
    rows = []
    for number, gap in enumerate(STUDY_TRUE_GAPS):
        ones = expected_ones(circuits, calibration_dir, "asap", {}, EMERALD_T1.prx_seconds + gap)
        # Expected counts at the case's shots: the estimator's bias at the scale its gates and errors apply to.
        exact = evaluate({k: (round(p * shots), shots) for k, p in ones.items()}, prediction)
        entropy = CALIBRATION_STUDY_SEED * 1000 + number
        reports = ordered_map(
            study_replicate, [(ones, shots, entropy, prediction, i) for i in range(STUDY_REPLICATES)], min_items=2
        )
        longest = str(IDLE_PULSES[-1])
        means, covered, rejected, alarms, gap_z, t1_z, unidentifiable = [], 0, 0, 0, [], [], 0
        for report in reports:
            h2 = report["h2_gap"]
            if h2["verdict"] == "unidentifiable":
                unidentifiable += 1
                continue
            train = h2["trains"][longest]
            means.append(train["mean_seconds"])
            covered += abs(train["mean_seconds"] - gap) <= train["mean_se_seconds"]
            rejected += h2["verdict"] == "per-qubit"
            alarms += h2.get("stationarity", {}).get("verdict") == "falsified"
            gap_z += [(g["gap_seconds"] - gap) / g["se_seconds"] for g in train["gaps"].values()]
            for qubit, fitted in report["t1_delay"].items():
                if fitted.get("t1_seconds") is not None:
                    t1 = calibration.values[f"characterization.model.{qubit}.t1_time"]
                    t1_z.append((fitted["t1_seconds"] - t1) / fitted["t1_se_seconds"])
        used = len(means)
        rows.append(
            {
                "true_gap_ns": gap * 1e9,
                "noise_free_mean_ns": exact["h2_gap"]["trains"].get(longest, {}).get("mean_seconds", math.nan) * 1e9,
                "noise_free_excluded": exact["h2_gap"].get("excluded", []),
                "noise_free_verdict": exact["h2_gap"]["verdict"],
                "replicates": STUDY_REPLICATES,
                "unidentifiable": unidentifiable,
                "mean_of_means_ns": float(np.mean(means)) * 1e9 if used else None,
                "spread_of_means_ns": float(np.std(means, ddof=1)) * 1e9 if used > 1 else None,
                "coverage_one_se": covered / used if used else None,
                "common_gap_rejection_rate": rejected / used if used else None,
                "stationarity_false_alarm_rate": alarms / used if used else None,
                "gap_z_sd": float(np.std(gap_z, ddof=1)) if len(gap_z) > 1 else None,
                "t1_z_mean": float(np.mean(t1_z)) if t1_z else None,
                "t1_z_sd": float(np.std(t1_z, ddof=1)) if len(t1_z) > 1 else None,
            }
        )
    return {
        "schema": "iqm-idle-schedule-t1-study-v1",
        "case": EMERALD_T1.case,
        "calibration_set": calibration.set_id,
        # The draw is cited by the constant's comment and the seed ledger; a record under results/ that named the
        # draw file would claim the whole draw (ci/seed_provenance.py).
        "seed": {
            "value": CALIBRATION_STUDY_SEED,
            "constant": "scripts/iqm_idle_schedule_probe.py CALIBRATION_STUDY_SEED",
        },
        "shots": shots,
        "devices": rows,
    }


def planted_counts(
    prediction: dict[str, Any],
    factor: int = 1,
    shift: dict[int, float] | None = None,
    only: set[str] | None = None,
    drop: float = 1.0,
) -> Counts:
    """Expected counts of a model device that is the retained run at every circuit but the idle trains of the tested
    lengths, and on which each qubit's trains lie on that qubit's own line: ln(p - r) linear in N through its two anchor
    arms in each layout, so every contrast is zero, with the gap of length n raised by shift[n] seconds (the population
    after n pulses falls by exp(-k1 n shift[n])) for the qubits in only (every qubit by default), and the population of
    every nonzero length multiplied by drop, a fixed loss between N = 0 and N > 0. Shots are the retained run's times
    factor, and the counts are fractional, so no random draw and no pulse-length rounding enters."""
    line = prediction["line"]
    ref_counts, ref_preps, _ = reference_of(line["run"])
    a, b = line["anchors"]
    out = {name: (ones * factor, shots * factor) for name, (ones, shots) in ref_counts.items()}
    for layout, rows in prediction["idle"].items():
        for qubit in rows:
            prep = ref_preps.get(qubit)
            if prep is None or prep.k1 is None or layout not in prep.cells:
                continue
            cell = prep.cells[layout]
            r = ref_counts[f"par-ro0@{qubit}"][0] / ref_counts[f"par-ro0@{qubit}"][1]
            for n in (*line["tested"], a, b):
                la, lb = cell[a], cell[b]
                if la is None or lb is None:
                    continue
                log_population = la.value + (lb.value - la.value) * (n - a) / (b - a)
                if only is None or qubit in only:
                    log_population -= prep.k1.value * n * (shift or {}).get(n, 0.0)
                log_population += math.log(drop)
                shots = ref_counts[f"idle-{layout}-{a}@{qubit}"][1] * factor
                out[f"idle-{layout}-{n}@{qubit}"] = ((r + math.exp(log_population)) * shots, shots)
    return out


def arm_pass_probability(counts: Counts, prep_name: str, r_name: str) -> float:
    """P(an arm's readout-corrected population exceeds LINE_ARM_SE standard errors) at the counts' expected values, with
    the normal approximation to the arm and to the bare readout one-fraction."""
    ones, shots = counts[prep_name]
    r_ones, r_shots = counts[r_name]
    p, r = ones / shots, r_ones / r_shots
    se = math.sqrt(max(p * (1 - p), 0.25 / shots) / shots + max(r * (1 - r), 0.25 / r_shots) / r_shots)
    return float(norm.cdf((p - r) / se - LINE_ARM_SE))


def unidentifiable_probability(prediction: dict[str, Any], counts: Counts) -> dict[str, Any]:
    """The probability that a repeat of the retained run leaves the cohort below its minimum, and under the
    retained run's rule (every cohort qubit needed) for comparison.

    Model. A cohort qubit passes the delay-fit gate (usable_t1) with the probability that a noncentral chi-square
    law (dof of its fit, noncentrality max(chi2 - dof, 0) of the retained fit) stays below the gate's critical value; a
    cell passes an arm with arm_pass_probability at the planted expected counts; qubits and arms are independent. The
    minimum is read per tested length, and the two lengths share the qubit's delay fit and its 500 and 1000 pulse arms.
    The retained fits' excess chi-square is the model's one input, taken from a single run."""
    from scipy.stats import chi2 as chi2_law

    line = prediction["line"]
    cohort = line["subjects"]["cohort"]
    minimum = cohort["min_qubits"]
    _, _, report = reference_report(line["run"])
    a, b = line["anchors"]
    first, last = min(line["tested"]), max(line["tested"])
    states: dict[str, dict[tuple[bool, bool], float]] = {}
    gate: dict[str, float] = {}
    for qubit in cohort["qubits"]:
        fit_row = report["t1_delay"][qubit]
        dof = fit_row["dof"]
        critical = float(chi2_law.isf(T1_FIT_P_MIN, dof))
        gate[qubit] = float(ncx2.cdf(critical, dof, max(fit_row["chi2"] - dof, 0.0)))
        layouts = [layout for layout, rows in prediction["idle"].items() if qubit in rows]
        cells = [
            {
                n: arm_pass_probability(counts, f"idle-{layout}-{n}@{qubit}", f"par-ro0@{qubit}")
                for n in (first, a, b, last)
            }
            for layout in layouts
        ]
        joint = {(False, False): 0.0, (True, False): 0.0, (False, True): 0.0, (True, True): 0.0}
        for outcome in itertools.product((False, True), repeat=4 * len(cells)):
            weight, ok_first, ok_last = 1.0, False, False
            for k, cell in enumerate(cells):
                arms_ok = dict(zip((first, a, b, last), outcome[4 * k : 4 * k + 4], strict=True))
                for n, ok in arms_ok.items():
                    weight *= cell[n] if ok else 1 - cell[n]
                ok_first |= arms_ok[first] and arms_ok[a] and arms_ok[b]
                ok_last |= arms_ok[last] and arms_ok[a] and arms_ok[b]
            joint[(ok_first, ok_last)] += weight
        states[qubit] = joint
    # Distribution of the number of qubits that pass at each tested length, by dynamic programming over qubits.
    table: dict[tuple[int, int], float] = {(0, 0): 1.0}
    for qubit in cohort["qubits"]:
        grown: dict[tuple[int, int], float] = {}
        outcomes = {(False, False): 1 - gate[qubit]}
        for (ok_first, ok_last), p in states[qubit].items():
            outcomes[(ok_first, ok_last)] = outcomes.get((ok_first, ok_last), 0.0) + gate[qubit] * p
        for (n_first, n_last), weight in table.items():
            for (ok_first, ok_last), p in outcomes.items():
                key = (n_first + ok_first, n_last + ok_last)
                grown[key] = grown.get(key, 0.0) + weight * p
        table = grown
    short = sum(w for (n_first, n_last), w in table.items() if n_first < minimum or n_last < minimum)
    every = float(np.prod([gate[q] for q in cohort["qubits"]]))
    return {
        "model": "noncentral chi-square delay-fit gate, normal arm populations, independent qubits and arms",
        "cohort_qubits": len(cohort["qubits"]),
        "minimum_qubits": minimum,
        "delay_fit_pass": {q: round(gate[q], 4) for q in cohort["qubits"]},
        "weakest_arm_pass": round(
            min(
                arm_pass_probability(counts, f"idle-{layout}-{n}@{q}", f"par-ro0@{q}")
                for q in cohort["qubits"]
                for layout, rows in prediction["idle"].items()
                if q in rows
                for n in (first, a, b, last)
            ),
            6,
        ),
        "unidentifiable": short,
        "unidentifiable_if_every_qubit_were_needed": 1 - every,
    }


def family_false_alarm(rho: float, z_reject: float) -> float:
    """P(|Z1| > z or |Z2| > z) for two standard normals of correlation rho, by quadrature."""
    spread = math.sqrt(1 - rho * rho)

    def inside(x: float) -> float:
        return float(norm.pdf(x) * (norm.cdf((z_reject - rho * x) / spread) - norm.cdf((-z_reject - rho * x) / spread)))

    return 1 - float(quad(inside, -z_reject, z_reject, epsabs=1e-12, epsrel=1e-12)[0])


def power(case_dir: Path) -> dict[str, Any]:
    """What the case resolves, at expected counts and no random draw: the model device of planted_counts (the retained
    run's readout, delay and anchor arms, every qubit's tested lengths on its own line) at the case's shots and at
    twice them. For each subject and tested length it records the error of the within-job deviation L and the deviation
    that sits z_reject errors out, for every qubit of the subject and for the smallest cohort the decision accepts (the
    qubits of least weight), plus the probability of an unidentifiable verdict and the false-alarm rate of the two
    deviations taken together."""
    profile = EMERALD_THIRD
    prediction = json.loads((case_dir / "prediction.json").read_text(encoding="utf-8"))
    line = prediction["line"]
    rows: dict[str, Any] = {}
    family: float | None = None
    usable_at_case_shots: set[str] = set()
    for factor in (1, 2):
        counts = planted_counts(prediction, factor)
        report = evaluate(counts, prediction)
        preps = prepare_all(counts, prediction, report["h1_schedule"]["arms"], report["t1_delay"])
        passing = {q for q, prep in preps.items() if prep.usable}
        if factor == 1:
            usable_at_case_shots = passing
        for q, prep in preps.items():
            # The doubled shots keep the case's cohort so the two errors compare the same qubits; the delay-fit gate
            # failures that the doubled counts add (the fit's excess chi-square grows with the shots) are recorded.
            prep.usable = q in usable_at_case_shots
        for name, subject in line["subjects"].items():
            for n in line["tested"]:
                coefficients = contrast_of(n, line["anchors"])
                full = contrast_reading(counts, preps, subject["qubits"], coefficients)
                if full is None:
                    raise ValueError(f"{name}-{n}: the model device has no reading")
                keep = sorted(full["weights"], key=lambda q: full["weights"][q])[: subject["min_qubits"]]
                smallest = contrast_reading(counts, preps, keep, coefficients)
                predicted = subject["predicted"][str(n)]["gap_seconds"]
                held = rows.setdefault(f"{name}-{n}", {"predicted_ns": predicted * 1e9})
                held[f"x{factor}"] = {
                    "shots": profile.shots * factor,
                    "qubits": len(full["qubits"]),
                    "qubits_passing_the_delay_fit_gate": len(passing & set(subject["qubits"])),
                    "se_ns": full["se_seconds"] * 1e9,
                    "resolvable_deviation_ns": line["z_reject"] * full["se_seconds"] * 1e9,
                    "resolvable_fraction": line["z_reject"] * full["se_seconds"] / predicted,
                    "smallest_cohort_qubits": len(smallest["qubits"]) if smallest else 0,
                    "smallest_cohort_resolvable_deviation_ns": (
                        line["z_reject"] * smallest["se_seconds"] * 1e9 if smallest else None
                    ),
                    "layout_se_ns": {
                        b: alt["se_seconds"] * 1e9
                        for b in prediction["idle"]
                        if (alt := contrast_reading(counts, preps, subject["qubits"], coefficients, (b,))) is not None
                    },
                }
        if factor == 1:
            duals = [
                contrast_reading(counts, preps, line["subjects"]["cohort"]["qubits"], contrast_of(n, line["anchors"]))
                for n in line["tested"]
            ]
            first, second = duals[0], duals[-1]
            if first is None or second is None:
                raise ValueError("the model device has no cohort reading")
            rho = covariance(first["_dual"], second["_dual"], counts) / (first["se_seconds"] * second["se_seconds"])
            family = family_false_alarm(rho, line["z_reject"])
            probability = unidentifiable_probability(prediction, counts)
    return {
        "schema": "iqm-idle-schedule-third-length-power-v2",
        "case": profile.case,
        "statistic": (
            "within-job deviation of the gap at a tested length from the line through the job's gaps at the anchors"
        ),
        "rows": rows,
        "correlation_of_the_two_cohort_deviations": rho,
        "false_alarm_of_the_two_deviations_together": family,
        "unidentifiable": probability,
    }


def decision_self_test(prediction: dict[str, Any]) -> None:
    """The third-length decision on model devices (expected counts, no random draw): known-good devices read on-line,
    known-bad devices read off-line or anchors-moved with the deviation recovered, a qubit that fails its gate drops
    out until the cohort is below its minimum, a gate failure of QB44 changes nothing, and the covariance matches a
    finite-difference Jacobian of the estimator."""
    line = prediction["line"]
    cohort = line["subjects"]["cohort"]

    def read(**kwargs: Any) -> dict[str, Any]:
        return evaluate(planted_counts(prediction, **kwargs), prediction)["h3_line"]

    def contrast(report: dict[str, Any], subject: str, n: int) -> dict[str, Any]:
        row: dict[str, Any] = report["subjects"][subject]["contrasts"][str(n)]
        return row

    good = read()
    if json.loads(dump(good)) != good:
        raise RuntimeError("the decision does not survive its own serialization")
    if good["verdict"] != "on-line" or any(abs(contrast(good, "cohort", n)["z"]) > 1e-6 for n in line["tested"]):
        raise RuntimeError(f"a device on its own lines reads {good['verdict']}")
    for shift, want in (
        ({250: 3.0e-9}, "on-line"),
        ({250: 5.0e-9}, "off-line"),
        ({2000: -2.5e-9}, "off-line"),
        ({250: 5.0e-9, 2000: 5.0e-9}, "off-line"),
        ({n: 8.0e-9 for n in (250, 500, 1000, 2000)}, "anchors-moved"),
    ):
        got = read(shift=shift)
        if got["verdict"] != want:
            raise RuntimeError(f"a device shifted by {shift} reads {got['verdict']}, not {want}")
        if len(shift) == 1:
            ((n, delta),) = shift.items()
            if not 0.97 < contrast(got, "cohort", n)["value_seconds"] / delta < 1.03:
                raise RuntimeError(
                    f"a {delta * 1e9} ns shift at {n} reads {contrast(got, 'cohort', n)['value_seconds']}"
                )
    # A drift of QB24 alone moves its anchors and no one else's: its subject reads anchors-moved, the cohort stays.
    drift = read(shift={n: 20.0e-9 for n in (250, 500, 1000, 2000)}, only={"QB24"})
    if drift["verdict"] != "on-line" or drift["subjects"]["QB24"]["verdict"] != "anchors-moved":
        raise RuntimeError(f"a QB24 drift reads {drift['verdict']}, QB24 {drift['subjects']['QB24']['verdict']}")
    # A fixed population loss between N = 0 and N > 0 has the form a + b / N: the deviations and the gap between nonzero
    # lengths stay at the retained value while the anchors move.
    lost = read(drop=0.9)
    if lost["verdict"] != "anchors-moved" or abs(lost["subjects"]["cohort"]["nonzero_gap"]["z"]) > 1.0:
        raise RuntimeError(f"a fixed population loss reads {lost['verdict']}")
    if any(abs(contrast(lost, "cohort", n)["z"]) > 1e-6 for n in line["tested"]):
        raise RuntimeError("a fixed population loss leaves a deviation")
    # Gates: a corrupted delay point fails usable_t1 and the qubit leaves the cohort; below the minimum the verdict is
    # unidentifiable; a qubit outside the cohort changes no reading.
    counts = planted_counts(prediction)
    for broken, want in (
        (cohort["qubits"][:1], "on-line"),
        (cohort["qubits"][: len(cohort["qubits"]) - cohort["min_qubits"] + 1], "unidentifiable"),
    ):
        damaged = dict(counts)
        for qubit in broken:
            ones, shots = damaged[f"t1-16us@{qubit}"]
            damaged[f"t1-16us@{qubit}"] = (ones * 2.0, shots)
        got = evaluate(damaged, prediction)["h3_line"]
        members = len(got["subjects"]["cohort"]["contrasts"]["250"]["qubits"])
        if got["verdict"] != want or members != len(cohort["qubits"]) - len(broken):
            raise RuntimeError(f"{len(broken)} qubits without a delay fit leave {members} and read {got['verdict']}")
    other = dict(counts)
    for key in counts:
        if key.endswith("@QB44"):
            other[key] = (counts[key][1] / 2, counts[key][1])
    if evaluate(other, prediction)["h3_line"] != good:
        raise RuntimeError("QB44's counts change the third-length decision")
    # The covariance: the delta method against central differences of the estimator over every count it uses.
    report = evaluate(counts, prediction)
    arms, t1 = report["h1_schedule"]["arms"], report["t1_delay"]
    preps = prepare_all(counts, prediction, arms, t1)
    d = prediction["prx_seconds"]

    def finite_difference(function: Any, dual: Dual) -> tuple[float, float, float]:
        """The delta method's error of dual, the error from central differences of function over the same counts and
        the largest difference of one derivative from the delta method's, in units of the delta method's error."""
        total, worst = 0.0, 0.0
        for key, derivative in dual.grad.items():
            ones, shots = counts[key]
            step = 1e-3 * shots
            values = [function({**counts, key: (ones + sign * step, shots)}) for sign in (1, -1)]
            numeric = (values[0] - values[1]) / (2 * step / shots)
            total += numeric**2 * shot_variance(counts, key)
            worst = max(worst, abs(numeric - derivative) * math.sqrt(shot_variance(counts, key)))
        error = math.sqrt(variance(dual, counts))
        return error, math.sqrt(total), worst / error

    def contrast_value(moved: Counts) -> float:
        trial = prepare_all(moved, prediction, arms, t1)
        return required(contrast_reading(moved, trial, cohort["qubits"], coefficients), "the cohort")["value_seconds"]

    coefficients = contrast_of(250, line["anchors"])
    reading = required(contrast_reading(counts, preps, cohort["qubits"], coefficients), "the cohort")
    error, numeric, worst = finite_difference(contrast_value, reading["_dual"])
    if abs(numeric / error - 1) > 1e-3 or worst > 1e-3:
        raise RuntimeError(f"the deviation's error {error} against {numeric} by finite differences, worst {worst}")
    # The delay fit's rate against t1_fit's, qubit by qubit, with the fit's weights held in the delta method.
    for qubit in cohort["qubits"]:

        def rate_of(moved: Counts, qubit: str = qubit) -> float:
            pair = readout_pair(moved, qubit)
            fit_row = t1_fit(moved, qubit, {"e01": pair[0], "e10": pair[1]}, prediction["t1_delays"])
            return float(fit_row["rate_per_second"])

        error, numeric, _ = finite_difference(rate_of, required(preps[qubit].k1, qubit))
        if abs(numeric / error - 1.0) > FIXED_WEIGHT_TOLERANCE:
            raise RuntimeError(f"{qubit}: the rate's error {error} against {numeric} by finite differences")
    # The anchors' pooled gaps hold their pooling weights fixed, with the tolerance stated at FIXED_WEIGHT_TOLERANCE.
    for n in line["anchors"]:
        anchor = required(cohort_gap(counts, preps, cohort["qubits"], 0, n, d)[0], f"the cohort at {n}")

        def anchor_value(moved: Counts, n: int = n) -> float:
            trial = prepare_all(moved, prediction, arms, t1)
            return required(cohort_gap(moved, trial, cohort["qubits"], 0, n, d)[0], "the cohort").value

        error, numeric, _ = finite_difference(anchor_value, anchor)
        if abs(numeric / error - 1.0) > FIXED_WEIGHT_TOLERANCE:
            raise RuntimeError(f"the anchor gap at {n} pulses has error {error}, {numeric} by finite differences")
    # The cell identity behind the closed form: the contrast of the gaps to the baseline equals the closed form.
    prep = preps["QB24"]
    layout = next(iter(prep.cells))
    d = prediction["prx_seconds"]
    from_gaps = combo([(c, required(pair_gap(prep, layout, 0, n, d), f"QB24 at {n}")) for n, c in coefficients.items()])
    closed = -combo(
        [(c / n, required(prep.cells[layout][n], f"QB24 at {n}")) for n, c in coefficients.items()]
    ) / required(prep.k1, "QB24 rate")
    if (
        abs(from_gaps.value - closed.value) > 1e-18
        or max(abs(from_gaps.grad[k] - closed.grad.get(k, 0.0)) for k in from_gaps.grad) > 1e-12
    ):
        raise RuntimeError("the closed form of the deviation differs from the contrast of the gaps")
    # The retained analysis: every per-qubit gap and its error without the readout terms, and the covariance the two
    # anchor gaps share through the delay fit (0.157489 ns^2 for the cohort, as recomputed from the stored fits).
    ref_counts, ref_preps, ref_d = reference_of(line["run"])
    stored = json.loads((ROOT / line["source"]).read_text(encoding="utf-8"))["h2_gap"]["trains"]
    for n, row in stored.items():
        for qubit, held in row["gaps"].items():
            mine = qubit_gap(ref_counts, ref_preps[qubit], 0, int(n), ref_d)
            if mine is None or not same(
                [mine.value, math.sqrt(variance(mine, ref_counts, shared_only))],
                [held["gap_seconds"], held["se_seconds"]],
            ):
                raise RuntimeError(f"the retained gap of {qubit} at {n} pulses is not reproduced")
    first, second = (
        required(cohort_gap(ref_counts, ref_preps, cohort["qubits"], 0, n, ref_d)[0], f"the cohort at {n}")
        for n in line["anchors"]
    )
    shared = covariance(first, second, ref_counts, lambda k: k.startswith("t1-"))
    if abs(shared * 1e18 - 0.157489) > 1e-4:
        raise RuntimeError(f"the anchors share {shared * 1e18} ns^2 through the delay fit")


def third_length_self_test() -> None:
    """The third-length case: the successor's circuits plus the added train lengths, the line read from the retained
    run, the committed case against its own build, and the decision (decision_self_test)."""
    profile = EMERALD_THIRD
    committed = ROOT / "results/iqm/cases" / profile.case
    calibration_dir = committed / "calibration"
    files, prediction = build_from(calibration_dir, profile)
    retained = ROOT / "results/iqm/cases" / EMERALD_T1.case / "circuits"
    case = json.loads(files["cases.json"])
    job = case["jobs"][0]
    circuits = [json.loads(text) for rel, text in files.items() if rel.startswith("circuits/")]
    if case["case"] != profile.case or len(circuits) != 20 or job["shots"] != 4000:
        raise RuntimeError(f"the third-length case is {case['case']}, {len(circuits)} circuits at {job['shots']} shots")
    kept_circuits = sorted(retained.glob("*.json"))
    if len(kept_circuits) != 16 or any(
        files[f"circuits/{p.name}"] != p.read_text(encoding="utf-8") for p in kept_circuits
    ):
        raise RuntimeError("the third-length case changes a circuit of the successor")
    names = {c["name"] for c in circuits} - {p.stem for p in kept_circuits}
    if names != {f"idle-{b}-{n}" for b in profile.train for n in (250, 2000)}:
        raise RuntimeError(f"the third-length case adds {sorted(names)}")
    if JOB_SECONDS + job["expected_seconds"] > profile.max_credits["emerald"] / 0.75 - PLAN_HEADROOM:
        raise RuntimeError(f"the third-length case's {job['expected_seconds']} s leave no headroom under its ceiling")
    if job["options"]["calibration_set_id"] != {"emerald": calibration_set_of(calibration_dir)}:
        raise RuntimeError("the third-length job does not pin the calibration set it was built from")
    # The committed case against this build, floats to 1e-12, as the successor's.
    for rel, text in files.items():
        built, kept = json.loads(text), json.loads((committed / rel).read_text(encoding="utf-8"))
        if rel == "cases.json":
            built.pop("prediction_sha256"), kept.pop("prediction_sha256")
        if not same(built, kept):
            raise RuntimeError(f"the third-length build of {rel} differs from the committed case")
    cohort = prediction["line"]["subjects"]["cohort"]
    if len(cohort["qubits"]) != 11 or "QB44" in cohort["qubits"]:
        raise RuntimeError(f"the cohort is {cohort['qubits']}")
    if abs(cohort["offset_seconds"] - 21.4e-9) > 0.05e-9 or abs(cohort["per_train_seconds"] - 5.84e-6) > 0.005e-6:
        raise RuntimeError(f"the cohort line reads {cohort['offset_seconds']} + {cohort['per_train_seconds']} / N")
    decision_self_test(prediction)


def self_test() -> str:
    calibration_dir = iqm_sim.EVIDENCE / QC / "calibration"
    calibration = iqm_sim.Calibration.from_directory(calibration_dir)
    files, prediction = build_from(calibration_dir)
    case = json.loads(files["cases.json"])
    if case["prediction_sha256"] != sha256(files["prediction.json"].encode()):
        raise RuntimeError("cases.json does not bind the prediction it was built with")
    if set().union(*(prediction["idle"][b] for b in IDLE_TRAIN_QUBITS)) != set(calibration.qubits):
        raise RuntimeError("a qubit is pulsed in no idle layout")
    for b, rows in prediction["idle"].items():
        for qubit, row in rows.items():
            if frozenset((qubit, b)) in calibration.cz:
                raise RuntimeError(f"{qubit} shares a coupler with the train qubit {b}")
            weakest = min(contrast["separation_se"] for contrast in row["contrasts"])
            if weakest < 2 * Z_RESOLVE:
                raise RuntimeError(f"{qubit} beside {b}: the schedules separate by only {weakest:.1f} standard errors")
    circuits = [json.loads(text) for rel, text in files.items() if rel.startswith("circuits/")]
    if len(circuits) > 100 or any(len(c["instructions"]) > 10000 for c in circuits):
        raise RuntimeError("the job exceeds Garnet's 100 circuits or 10000 instructions per circuit")
    injected = {"QB6": -0.012, "QB11": 0.027, "QB3": 0.01}
    late = evaluate(synthetic(circuits, calibration_dir, "asap", injected, SYNTHETIC_SEEDS[0]), prediction)
    if late["h1_schedule"]["verdict"] != "asap":
        raise RuntimeError(f"an ASAP device reads {late['h1_schedule']['verdict']}")
    for qubit, eps in injected.items():
        for got in [
            late["parallel_trains"][qubit],
            *([late["h2_isolated_trains"][qubit]] if qubit in TRAIN_QUBITS else []),
        ]:
            if not got["linear"] or abs(got["eps"] - eps) > 4 * got["eps_se"] + 0.002:
                raise RuntimeError(f"{qubit}: injected {eps} through its own readout, recovered {got}")
    if late["h2_isolated_trains"]["QB11"].get("attribution", {}).get("verdict") != "consistent":
        raise RuntimeError(f"an injected 2.7 % QB11 over-rotation reads {late['h2_isolated_trains']['QB11']}")
    for b, rows in late["h1_schedule"]["arms"].items():
        for qubit, arms in rows.items():
            t1 = calibration.values[f"characterization.model.{qubit}.t1_time"]
            apparent = arms[-1]["apparent_t1_seconds"]
            if apparent is None or abs(apparent / t1 - 1) > 0.5:
                raise RuntimeError(f"{qubit} beside {b}: apparent T1 {apparent} against the calibrated {t1}")
    flat = evaluate(synthetic(circuits, calibration_dir, "alap", {}, SYNTHETIC_SEEDS[1]), prediction)
    if flat["h1_schedule"]["verdict"] != "alap":
        raise RuntimeError(f"an ALAP device reads {flat['h1_schedule']['verdict']}")
    if flat["h2_isolated_trains"]["QB11"].get("attribution", {}).get("verdict") != "excluded":
        raise RuntimeError(f"a QB11 without over-rotation reads {flat['h2_isolated_trains']['QB11']}")
    pulsed = sum(len(rows) for rows in prediction["idle"].values())
    committed = ROOT / "results/iqm/cases" / CASE
    own, _ = build_from(committed / "calibration")
    for rel, text in own.items():
        built, kept = json.loads(text), json.loads((committed / rel).read_text(encoding="utf-8"))
        if rel == "cases.json":
            # The digest binds the prediction's bytes, which differ in the last float digit between numeric paths.
            built.pop("prediction_sha256"), kept.pop("prediction_sha256")
        if not same(built, kept):
            raise RuntimeError(f"the Garnet build of {rel} differs from the committed case")
    emerald_self_test()
    emerald_t1_self_test()
    third_length_self_test()
    return (
        f"idle schedule probe: {len(circuits)} circuits, {pulsed} pulsed-qubit layouts; an ASAP and an ALAP model "
        "device read their own schedule, and injected over-rotations come back through unlike readouts; the Garnet "
        "build matches its committed case and the Emerald build matches its written case; the Emerald successor reads "
        "a zero gap and a planted 14 ns gap through its delay-measured T1"
    )


def same(a: Any, b: Any) -> bool:
    """Equality of parsed JSON with floats compared to 1e-12 relative, the spread of two numeric paths."""
    if isinstance(a, float) and isinstance(b, float):
        return math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-15)
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b, strict=True))
    return bool(a == b)


def emerald_t1_self_test() -> None:
    """The successor: the Emerald circuits unchanged plus four delay circuits on all twelve qubits, inside its ceiling;
    a model device whose pulses last the prediction's 24 ns reads a common gap near zero and each qubit's calibrated
    T1, and one whose pulses last 14 ns longer reads that gap."""
    committed = ROOT / "results/iqm/cases" / EMERALD_T1.case / "calibration"
    calibration_dir = committed if committed.is_dir() else iqm_sim.EVIDENCE / EMERALD_T1.qc / "calibration"
    calibration = iqm_sim.Calibration.from_directory(calibration_dir)
    files, prediction = build_from(calibration_dir, EMERALD_T1)
    base, _ = build_from(calibration_dir, EMERALD)
    case = json.loads(files["cases.json"])
    job = case["jobs"][0]
    circuits = [json.loads(text) for rel, text in files.items() if rel.startswith("circuits/")]
    if case["case"] != EMERALD_T1.case or len(circuits) != 16 or job["max_credits"] != EMERALD_T1.max_credits:
        raise RuntimeError(f"the successor is {case['case']} with {len(circuits)} circuits at {job['max_credits']}")
    if any(base[rel] != files[rel] for rel in base if rel.startswith("circuits/")):
        raise RuntimeError("the successor changes a circuit of the Emerald case")
    if calibration_dir == committed:
        # The committed case against this build, floats to 1e-12: its prediction bytes come from another numeric
        # path than every host's, as the Garnet case's do.
        for rel, text in files.items():
            built, kept = json.loads(text), json.loads((committed.parent / rel).read_text(encoding="utf-8"))
            if rel == "cases.json":
                built.pop("prediction_sha256"), kept.pop("prediction_sha256")
            if not same(built, kept):
                raise RuntimeError(f"the successor build of {rel} differs from the committed case")
    every = ordered(EMERALD_T1.qubits or ())
    for seconds in T1_DELAYS:
        ops = json.loads(files[f"circuits/{delay_name(seconds)}.json"])["instructions"]
        if [op["name"] for op in ops] != ["prx"] * 12 + ["delay", "measure"] or ops[12]["locus"] != every:
            raise RuntimeError(f"{delay_name(seconds)} is not prx(pi) on the twelve, one delay and one measure")
    if JOB_SECONDS + job["expected_seconds"] > EMERALD_T1.max_credits["emerald"] / 0.75 - PLAN_HEADROOM:
        raise RuntimeError(f"the successor's {job['expected_seconds']} s leave no headroom under its ceiling")

    # Expected counts at the case's shots (no random draw): the sampled behavior is the calibration study's
    # (study(), results/iqm/proposals/idle-schedule-t1-emerald/calibration-study.json).
    def expected(method: str, gap: float) -> dict[str, Any]:
        ones = expected_ones(circuits, calibration_dir, method, {}, EMERALD_T1.prx_seconds + gap)
        return evaluate({k: (round(p * EMERALD_T1.shots), EMERALD_T1.shots) for k, p in ones.items()}, prediction)

    zero = expected("asap", 0.0)
    if zero["h1_schedule"]["verdict"] != "asap" or zero["h2_gap"]["verdict"] != "common":
        read = (zero["h1_schedule"]["verdict"], zero["h2_gap"]["verdict"])
        raise RuntimeError(f"a gap-free ASAP device reads schedule {read[0]}, gap {read[1]}")
    for qubit, fitted in zero["t1_delay"].items():
        t1 = calibration.values[f"characterization.model.{qubit}.t1_time"]
        if fitted["t1_seconds"] is None or abs(fitted["t1_seconds"] / t1 - 1) > 0.01:
            raise RuntimeError(f"{qubit}: the delay fit reads {fitted.get('t1_seconds')} against the model's {t1}")
    for planted in (0.0, 14e-9):
        got = zero if planted == 0.0 else expected("asap", planted)
        train = got["h2_gap"]["trains"][str(IDLE_PULSES[-1])]
        # The calibration study reads the estimator's bias at expected counts as 0.02 to 0.04 ns.
        if abs(train["mean_seconds"] - planted) > 0.1e-9:
            raise RuntimeError(f"a {planted * 1e9:.0f} ns gap reads {train['mean_seconds'] * 1e9:.3f} ns")
        if got["h2_gap"]["stationarity"]["verdict"] != "stationary":
            raise RuntimeError(f"a stationary {planted * 1e9:.0f} ns gap reads {got['h2_gap']['stationarity']}")
    flat = expected("alap", 0.0)
    if flat["h2_gap"]["verdict"] != "unidentifiable":
        raise RuntimeError(f"an ALAP device's gap reads {flat['h2_gap']['verdict']}")
    # The preregistered test covers every pulsed qubit: one qubit without a usable delay fit, or with a nonlinear
    # readout fit, leaves H2 unidentifiable and names the qubit.
    registered = {q for rows in prediction["idle"].values() for q in rows}
    arms, t1 = zero["h1_schedule"]["arms"], zero["t1_delay"]
    lost = sorted(registered)[0]
    for broken in ({**t1, lost: {"t1_seconds": None, "points": 2}}, t1):
        valid = {q for q in registered if usable_t1(broken[q]) and (broken is t1 or q != lost)}
        if broken is t1:
            valid.discard(lost)
        got = gap_test(arms, broken, prediction["prx_seconds"], "asap", registered, valid)
        if got["verdict"] != "unidentifiable" or got["excluded"] != [lost]:
            raise RuntimeError(f"a case without {lost} reads {got['verdict']}, excluded {got['excluded']}")


def emerald_self_test() -> None:
    """The Emerald build against its written case: cohort, layouts, circuits, shots, reset, ceiling, schedule."""
    calibration_dir = iqm_sim.EVIDENCE / EMERALD.qc / "calibration"
    calibration = iqm_sim.Calibration.from_directory(calibration_dir)
    files, prediction = build_from(calibration_dir, EMERALD)
    case = json.loads(files["cases.json"])
    job = case["jobs"][0]
    if case["prediction_sha256"] != sha256(files["prediction.json"].encode()):
        raise RuntimeError("the Emerald cases.json does not bind its prediction")
    if case["case"] != EMERALD.case or case["qcs"] != ["emerald:mock", "emerald"]:
        raise RuntimeError(f"the Emerald case names {case['case']} on {case['qcs']}")
    if job["shots"] != 4000 or len(job["circuits"]) != 12:
        raise RuntimeError(f"the Emerald job is {len(job['circuits'])} circuits at {job['shots']} shots")
    if job["options"]["heralding_mode"] != "none" or job["options"]["active_reset_cycles"] != 1:
        raise RuntimeError(f"the Emerald job resets as {job['options']}")
    if job["options"]["calibration_set_id"] != {"emerald": calibration.set_id}:
        raise RuntimeError("the Emerald job does not pin the calibration set of its prediction")
    if job["max_credits"] != {"emerald": 4.5, "emerald:mock": 0.0} or job["expected_seconds"] != 2.088:
        raise RuntimeError(f"the Emerald ceiling reads {job['max_credits']} for {job['expected_seconds']} s")
    circuits = [json.loads(text) for rel, text in files.items() if rel.startswith("circuits/")]
    if {q for c in circuits for q in measured(c)} != set(EMERALD.qubits or ()) or len(EMERALD.qubits or ()) != 12:
        raise RuntimeError("the Emerald circuits do not read exactly the case's twelve qubits")
    if any(measured(c) != ordered(EMERALD.qubits or ()) for c in circuits):
        raise RuntimeError("an Emerald circuit does not read the twelve qubits in one joint measure")
    if {b: len(rows) for b, rows in prediction["idle"].items()} != {"QB20": 11, "QB26": 9}:
        raise RuntimeError(f"the Emerald layouts pulse { ({b: len(r) for b, r in prediction['idle'].items()}) }")
    if set().union(*(prediction["idle"][b] for b in EMERALD.train)) != set(EMERALD.qubits or ()):
        raise RuntimeError("an Emerald qubit is pulsed in no idle layout")
    if prediction["prx_seconds"] != 24e-9 or prediction["coherent_attribution"]:
        raise RuntimeError("the Emerald prediction carries Garnet's prx length or over-rotation attribution")
    for b, rows in prediction["idle"].items():
        for qubit, row in rows.items():
            weakest = min(contrast["separation_se"] for contrast in row["contrasts"])
            if weakest < 2 * Z_RESOLVE:
                raise RuntimeError(f"{qubit} beside {b}: the schedules separate by only {weakest:.1f} standard errors")
    for method, seed in (("asap", SYNTHETIC_SEEDS[0]), ("alap", SYNTHETIC_SEEDS[1])):
        got = evaluate(synthetic(circuits, calibration_dir, method, {}, seed, EMERALD), prediction)
        if got["h1_schedule"]["verdict"] != method or got["h2_isolated_trains"]:
            raise RuntimeError(f"an {method} Emerald device reads {got['h1_schedule']['verdict']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")
    bd = sub.add_parser("build")
    bd.add_argument("directory", type=Path)
    bd.add_argument(
        "--live", action="store_true", help="read the quantum computer's current calibration (network, read-only)"
    )
    ck = sub.add_parser("check")
    ck.add_argument("directory", type=Path)
    bd.add_argument(
        "--calibration-from",
        type=Path,
        help="a folder holding metrics.json and dynamic-quantum-architecture.json of one set, read beforehand",
    )
    for each in (bd, ck):
        each.add_argument("--qc", choices=sorted(PROFILES), default="garnet", help="the case profile to build")
    sd = sub.add_parser("study", help="calibration study of the successor's H2 estimator (local, no provider)")
    sd.add_argument("case_dir", type=Path)
    sd.add_argument("--out", type=Path, required=True)
    pw = sub.add_parser("power", help="what the third-length case resolves, at expected counts (local, no provider)")
    pw.add_argument("case_dir", type=Path)
    pw.add_argument("--out", type=Path, required=True)
    an = sub.add_parser("analyze")
    an.add_argument("run_dir", type=Path)
    an.add_argument("--out", type=Path, required=True)
    an.add_argument("--replay", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
    elif args.command == "build":
        if args.live and args.calibration_from:
            parser.error("--live and --calibration-from name two calibration sources")
        write(args.directory, args.live, PROFILES[args.qc], args.calibration_from)
    elif args.command == "check":
        check(args.directory, PROFILES[args.qc])
    elif args.command == "study":
        args.out.write_text(dump(study(args.case_dir)), encoding="utf-8")
    elif args.command == "power":
        args.out.write_text(dump(power(args.case_dir)), encoding="utf-8")
    elif args.command == "analyze":
        text = dump(analyze(args.run_dir))
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
