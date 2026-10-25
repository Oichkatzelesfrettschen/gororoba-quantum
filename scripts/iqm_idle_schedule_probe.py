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

Usage: "$PYTHON" scripts/iqm_idle_schedule_probe.py (build DIR [--live] | check DIR | analyze RUN_DIR --out FILE
       [--replay] | --self-test)
"""

from __future__ import annotations

import argparse
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


def pulsed_qubits(train_qubit: str, calibration: iqm_sim.Calibration) -> list[str]:
    """Every qubit that shares no coupler with the train qubit and is not it."""
    return ordered(
        q for q in calibration.qubits if q != train_qubit and frozenset((q, train_qubit)) not in calibration.cz
    )


def circuits_of(calibration: iqm_sim.Calibration) -> list[dict[str, Any]]:
    every = ordered(calibration.qubits)
    circuits: list[dict[str, Any]] = []
    for b in IDLE_TRAIN_QUBITS:
        pulsed = pulsed_qubits(b, calibration)
        for n in IDLE_PULSES:
            instructions = [*(prx(q, math.pi) for q in pulsed), *(prx(b, math.pi) for _ in range(n))]
            circuits.append({"name": f"idle-{b}-{n}", "instructions": [*instructions, measure(every)]})
    circuits.append({"name": "par-ro0", "instructions": [measure(every)]})
    circuits.append({"name": "par-ro1", "instructions": [*(prx(q, math.pi) for q in every), measure(every)]})
    for k in AMPLIFY_K:
        pulses = [prx(q, math.pi / 2) for _ in range(train_pulses(k)) for q in every]
        circuits.append({"name": f"par-amp-{k}", "instructions": [*pulses, measure(every)]})
    for qubit in TRAIN_QUBITS:
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


def exact(item: tuple[dict[str, Any], str, str, dict[str, float]]) -> float:
    """Exact <Z> of a circuit's first measured qubit before readout: the calibration's gate noise, idle T1/T2 over
    the given schedule and prx angles scaled by 1 + eps on the named qubits.

    A joint measure is one instruction on the device, so a barrier over its locus aligns its readouts here.
    """
    circuit, calibration_dir, method, over = item
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
    target, _ = target_of(calibration)
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
    circuits: list[dict[str, Any]], calibration_dir: Path, method: str, over: dict[str, float]
) -> dict[str, float]:
    """True <Z> of every measured qubit of every circuit, keyed name@qubit."""
    keys = [(c, q) for c in circuits for q in measured(c)]
    values = ordered_map(exact, [(marginal(c, q), str(calibration_dir), method, over) for c, q in keys])
    return {f"{c['name']}@{q}": value for (c, q), value in zip(keys, values, strict=True)}


def build_from(calibration_dir: Path) -> tuple[dict[str, str], dict[str, Any]]:
    calibration = iqm_sim.Calibration.from_directory(calibration_dir)
    circuits = circuits_of(calibration)
    files = {f"circuits/{c['name']}.json": dump(c) for c in circuits}
    no_error: dict[str, float] = {}
    true = {method: readings(circuits, calibration_dir, method, no_error) for method in ("asap", "alap")}
    z = {
        method: {key: read(value, *calibration.readout(key.split("@")[1])) for key, value in values.items()}
        for method, values in true.items()
    }
    idle: dict[str, Any] = {}
    for b in IDLE_TRAIN_QUBITS:
        rows = {}
        for qubit in pulsed_qubits(b, calibration):
            contrasts = []
            for n in IDLE_PULSES[1:]:
                name, base = f"idle-{b}-{n}@{qubit}", f"idle-{b}-0@{qubit}"
                asap = z["asap"][name] - z["asap"][base]
                alap = z["alap"][name] - z["alap"][base]
                se = math.hypot(*(math.sqrt(max(1 - z["alap"][m] ** 2, 1 / SHOTS) / SHOTS) for m in (name, base)))
                contrasts.append({"pulses": n, "asap": asap, "alap": alap, "separation_se": abs(asap - alap) / se})
            rows[qubit] = {
                "t1_seconds": calibration.values[f"characterization.model.{qubit}.t1_time"],
                "contrasts": contrasts,
            }
        idle[b] = rows
    shot = len(circuits) * ACTIVE_SHOT_SECONDS + sum(n * DURATIONS["r"] for _ in IDLE_TRAIN_QUBITS for n in IDLE_PULSES)
    expected = round(SHOTS * shot, 3)
    budget = MAX_CREDITS[QC] / PRICE[QC]
    if JOB_SECONDS + expected > budget - PLAN_HEADROOM:
        raise ValueError(f"{expected} s of shots plus {JOB_SECONDS} s leave less than {PLAN_HEADROOM} s of {budget} s")
    job = {
        "job": "probe",
        "circuits": [{"file": rel, "sha256": sha256(text.encode())} for rel, text in files.items()],
        "shots": SHOTS,
        # The job compiles against the calibration set the prediction was made from, or fails if it is gone.
        "options": {**OPTIONS, "calibration_set_id": {QC: calibration.set_id}},
        "expected_seconds": expected,
        "max_credits": MAX_CREDITS,
    }
    prediction = {
        "calibration_set": calibration.set_id,
        "prx_seconds": DURATIONS["r"],
        "idle": idle,
        "z": z,
        "coherent_attribution": {q: COHERENT[q] for q in TRAIN_QUBITS if q in COHERENT},
        "model": (
            "iqm_sim depolarizing PRX with unheralded readout, idle T1/T2 over ASAP and over ALAP schedules with the "
            "joint measure aligned, exact density matrix per measured qubit"
        ),
    }
    files["prediction.json"] = dump(prediction)
    files["cases.json"] = dump(
        {
            "schema": CASE_SCHEMA,
            "case": CASE,
            "question": (
                "Does Garnet schedule a circuit job's gates as soon or as late as possible, read by whether pulsed "
                "qubits relax while an uncoupled qubit runs an identity train, and what over-rotation does every "
                "qubit's prx carry when fitted with its own readout, driven alone and all at once?"
            ),
            "qcs": QCS,
            "jobs": [job],
            # The approval digest of cases.json covers the prediction the analysis decides against.
            "prediction_sha256": sha256(files["prediction.json"].encode()),
        }
    )
    return files, prediction


def write(directory: Path, live: bool = False) -> None:
    """Build the case; --live reads Garnet's current calibration, otherwise the retained snapshot's copy."""
    calibration_dir = directory / "calibration"
    calibration_dir.mkdir(parents=True, exist_ok=True)
    if live:
        fetch_calibration(calibration_dir)
    else:
        source = iqm_sim.EVIDENCE / QC / "calibration"
        for name in CALIBRATION_FILES:
            shutil.copyfile(source / name, calibration_dir / name)
    files, prediction = build_from(calibration_dir)
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


def check(directory: Path) -> None:
    files, _ = build_from(directory / "calibration")
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
    items += [(counts, "amp-" + q, "ro", q) for q in TRAIN_QUBITS]
    fits = ordered_map(fit, items)
    parallel = dict(zip(qubits, fits[: len(qubits)], strict=True))
    isolated_fits = dict(zip(TRAIN_QUBITS, fits[len(qubits) :], strict=True))
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
    for qubit in TRAIN_QUBITS:
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

    facts = iqm_jobs.run_facts(run_dir)
    submission = json.loads((run_dir / "submission.json").read_text(encoding="utf-8"))
    record = json.loads((run_dir / "raw/job.json").read_bytes())
    case = json.loads((run_dir / "cases.json").read_text(encoding="utf-8"))
    prediction_bytes = (run_dir / "prediction.json").read_bytes()
    if sha256(prediction_bytes) != case.get("prediction_sha256"):
        raise ValueError(f"{run_dir}/prediction.json is not the prediction cases.json binds")
    prediction = json.loads(prediction_bytes)
    if facts["statuses"] != {"completed": 1}:
        raise ValueError(f"{run_dir}: the job is {sorted(facts['statuses'])}; the analysis reads completed jobs")
    # Mock outcomes are random bits and never enter the analysis.
    if submission["qc"] != QC or case.get("case") != CASE:
        raise ValueError(f"{run_dir}: a {case.get('case')} run on {submission['qc']}, not a {CASE} run on {QC}")
    if record["compilation"]["calibration_set_id"] != prediction["calibration_set"]:
        raise ValueError(f"{run_dir}: compiled against another calibration set than the prediction's")
    row = next(r for r in case["jobs"] if r["job"] == submission["job"])
    circuits = [json.loads((run_dir / entry["file"]).read_text(encoding="utf-8")) for entry in row["circuits"]]
    counts = tally(circuits, json.loads((run_dir / "raw/measurements.json").read_bytes()))
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
    circuits: list[dict[str, Any]], calibration_dir: Path, method: str, eps: dict[str, float], seed: int
) -> dict[str, tuple[int, int]]:
    """Counts of a model device: the calibration's gate noise and relaxation over one schedule, the over-rotations
    eps and SYNTHETIC_READOUT, sampled at SHOTS."""
    rng = np.random.default_rng(seed)
    counts = {}
    for key, value in readings(circuits, calibration_dir, method, eps).items():
        e01, e10 = SYNTHETIC_READOUT.get(key.split("@")[1], SYNTHETIC_DEFAULT)
        counts[key] = (int(rng.binomial(SHOTS, (1 - read(value, e01, e10)) / 2)), SHOTS)
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
    return (
        f"idle schedule probe: {len(circuits)} circuits, {pulsed} pulsed-qubit layouts; an ASAP and an ALAP model "
        "device read their own schedule, and injected over-rotations come back through unlike readouts"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")
    bd = sub.add_parser("build")
    bd.add_argument("directory", type=Path)
    bd.add_argument("--live", action="store_true", help="read Garnet's current calibration (network, read-only)")
    sub.add_parser("check").add_argument("directory", type=Path)
    an = sub.add_parser("analyze")
    an.add_argument("run_dir", type=Path)
    an.add_argument("--out", type=Path, required=True)
    an.add_argument("--replay", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
    elif args.command == "build":
        write(args.directory, args.live)
    elif args.command == "check":
        check(args.directory)
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
