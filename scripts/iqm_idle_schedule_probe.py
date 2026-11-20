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

Usage: "$PYTHON" scripts/iqm_idle_schedule_probe.py (build DIR [--live] [--qc QC] | check DIR [--qc QC] |
       analyze RUN_DIR --out FILE [--replay] | --self-test)
"""

from __future__ import annotations

import argparse
import dataclasses
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

ROOT = Path(__file__).resolve().parent.parent
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
PROFILES = {p.qc: p for p in (GARNET, EMERALD)}
# Draw docs/evidence/anu_qrng/draw-2026-10-25T001615Z.json, indices 0 and 1 (allocations.json).
SYNTHETIC_SEEDS = (36215, 40623)
# The model device's readout per qubit, (P(1|0), P(0|1)), unlike every qubit's calibrated readout.
SYNTHETIC_READOUT = {"QB6": (0.04, 0.10), "QB11": (0.07, 0.05)}
SYNTHETIC_DEFAULT = (0.02, 0.06)


def prx(qubit: str, angle: float) -> dict[str, Any]:
    return {"name": "prx", "locus": [qubit], "args": {"angle": angle, "phase": 0.0}}


def measure(qubits: list[str]) -> dict[str, Any]:
    return {"name": "measure", "locus": qubits, "args": {"key": "c"}}


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
        for n in IDLE_PULSES:
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
    ops = [op for op in circuit["instructions"] if op["name"] == "prx" and op["locus"][0] in keep]
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
            for n in IDLE_PULSES[1:]:
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
        n * profile.prx_seconds for _ in profile.train for n in IDLE_PULSES
    )
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


def write(directory: Path, live: bool = False, profile: Profile = GARNET) -> None:
    """Build the case; --live reads Garnet's current calibration, otherwise the retained snapshot's copy."""
    calibration_dir = directory / "calibration"
    calibration_dir.mkdir(parents=True, exist_ok=True)
    if live:
        if profile is not GARNET:
            raise ValueError(
                "--live fetches Garnet's calibration; another quantum computer builds from its retained copy"
            )
        fetch_calibration(calibration_dir)
    else:
        source = iqm_sim.EVIDENCE / profile.qc / "calibration"
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
    return {
        "h1_schedule": {"verdict": schedule, "arms": arms},
        "h2_isolated_trains": isolated,
        "parallel_trains": parallel,
    }


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
    row = next(r for r in case["jobs"] if r["job"] == submission["job"])
    circuits = [json.loads((run_dir / entry["file"]).read_text(encoding="utf-8")) for entry in row["circuits"]]
    counts = tally(circuits, records.json_of("raw/measurements.json"))
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
    return (
        f"idle schedule probe: {len(circuits)} circuits, {pulsed} pulsed-qubit layouts; an ASAP and an ALAP model "
        "device read their own schedule, and injected over-rotations come back through unlike readouts; the Garnet "
        "build matches its committed case and the Emerald build matches its written case"
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
    bd.add_argument("--live", action="store_true", help="read Garnet's current calibration (network, read-only)")
    ck = sub.add_parser("check")
    ck.add_argument("directory", type=Path)
    for each in (bd, ck):
        each.add_argument("--qc", choices=sorted(PROFILES), default=GARNET.qc, help="the quantum computer to build for")
    an = sub.add_parser("analyze")
    an.add_argument("run_dir", type=Path)
    an.add_argument("--out", type=Path, required=True)
    an.add_argument("--replay", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
    elif args.command == "build":
        write(args.directory, args.live, PROFILES[args.qc])
    elif args.command == "check":
        check(args.directory, PROFILES[args.qc])
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
