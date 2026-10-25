"""IQM Garnet facts the circuit-job predictions rest on: the idle schedule and each trained qubit's own readout.

Schedule. The iqm_sim-based predictions (iqm_cancellation_probe.py, iqm_signed_probe.py, iqm_signed_resolve.py)
apply idle T1/T2 relaxation over an ALAP schedule, while the iqm-pulse TimeBox default is ASAP
(docs/notes/iqm/docs/iqm-pulse/using_builder.md) and a circuit job body names no strategy. The job API returns
measurements, counts, runtime estimates and sweep results, not the compiled schedule
(docs/notes/iqm/README.md, endpoint table), so the strategy is measured. An idle arm drives a probe qubit A with
one pi pulse, a qubit B that shares no coupler with A with n pi pulses (an identity for even n), and reads A and B
in one joint measure. ASAP places A's pulse at the start, so A waits n pulse lengths in |1> and relaxes by
exp(-n t_prx / T1); ALAP places it just before the measure, so A's reading does not depend on n. The contrast
z(n) - z(0) of A separates the two schedules by roughly (1 - exp(-n t_prx / T1)) times the readout contrast.

Train readout. iqm_signed_resolve.py measured prx trains on its TRAIN_QUBITS with a readout pair on its control
qubit only, so a train's over-rotation was not separable from that qubit's readout offset and scale. Here every
train qubit gets its own ro0 and ro1, and iqm_cancellation_probe.fit_train fits each train jointly with them.

Preregistered decisions (Z_RESOLVE standard errors):

- H1, per probe qubit and nonzero train length: the observed contrast lies Z_RESOLVE above the midpoint of the
  ASAP and ALAP predictions, toward ASAP (asap), Z_RESOLVE below it (alap), or between (unresolved). The schedule
  verdict is the common reading of every arm, mixed when arms resolve to both, and unresolved otherwise.
- H2, per train qubit: the joint fit is linear when its chi-square survival is at least TRAIN_P_MIN; it reports eps
  and its standard error. Where iqm_signed_resolve.COHERENT attributes an over-rotation to the qubit, that value is
  consistent when it lies within Z_RESOLVE standard errors of eps and excluded otherwise.

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
from iqm_cancellation_probe import (  # noqa: E402
    AMPLIFY_K,
    chi2_survival_3,
    fetch_calibration,
    fit_train,
    measure,
    prx,
    read,
    tally,
    train,
    z_of,
)
from iqm_jobs import CASE_SCHEMA, ceiling_credits, dump  # noqa: E402
from iqm_platform import sha256  # noqa: E402
from iqm_signed_probe import DURATIONS, relaxed, target_of  # noqa: E402
from iqm_signed_resolve import COHERENT, TRAIN_QUBITS  # noqa: E402

from parallel import ordered_map  # noqa: E402

CASE = "idle-schedule-train-readout"
QC = "garnet"
QCS = ["garnet:mock", "garnet"]
PRICE = {"garnet": 0.5, "garnet:mock": 0.0}
OPTIONS: dict[str, Any] = {"heralding_mode": "zeros", "active_reset_cycles": 1}
CALIBRATION_FILES = ("metrics.json", "dynamic-quantum-architecture.json")
SHOTS = 10000
# The heralded active-reset Garnet jobs of the signed probe differ by 31 us per requested shot; an idle arm adds
# its train's n prx durations to every shot.
SHOT_SECONDS = 0.000031
# QB1 carried the timing and reset pilots; QB7 is the signed probes' control. Their calibrated T1 differ.
IDLE_QUBITS = ("QB1", "QB7")
IDLE_PULSES = (0, 500, 1000)
Z_RESOLVE = 3.0
TRAIN_P_MIN = 0.001
# A kept-shot fraction below the heralded jobs' 55.9 % on seven qubits; it sizes the design's separation only.
DESIGN_RETENTION = 0.5
# Draw docs/evidence/anu_qrng/draw-2026-10-25T001615Z.json, indices 0 and 1 (allocations.json).
SYNTHETIC_SEEDS = (36215, 40623)
# The model device's readout per qubit, (P(1|0), P(0|1)), unlike every qubit's calibrated readout.
SYNTHETIC_READOUT = {"QB6": (0.04, 0.10), "QB11": (0.07, 0.05)}
SYNTHETIC_DEFAULT = (0.02, 0.06)


def idle_partner(qubit: str, calibration: iqm_sim.Calibration) -> str:
    """The lowest-numbered qubit with calibrated prx and relaxation that shares no coupler with qubit and carries
    no other role in the case."""
    taken = {*IDLE_QUBITS, *TRAIN_QUBITS}
    for candidate in sorted(calibration.qubits, key=lambda q: int(q[2:])):
        if candidate in taken or frozenset((qubit, candidate)) in calibration.cz:
            continue
        fields = [iqm_sim.PRX_FIELD.format(q=candidate), f"characterization.model.{candidate}.t1_time"]
        if all(field in calibration.values for field in fields):
            return candidate
    raise ValueError(f"no idle partner for {qubit}")


def idle_arm(qubit: str, partner: str, pulses: int) -> dict[str, Any]:
    name = f"idle-{qubit}-{pulses}"
    instructions = [prx(qubit, math.pi), *[prx(partner, math.pi) for _ in range(pulses)]]
    instructions.append({"name": "measure", "locus": [qubit, partner], "args": {"key": "c"}})
    return {"name": name, "instructions": instructions}


def exact(item: tuple[dict[str, Any], str, str, dict[str, float]]) -> float:
    """Exact <Z> of a circuit's first measured qubit before readout: the calibration's gate noise, idle T1/T2 over
    the given schedule and prx angles scaled by 1 + eps on the named qubits.

    A joint measure is one instruction on the device, so a barrier over its locus aligns its readouts here.
    """
    circuit, calibration_dir, method, over = item
    calibration = iqm_sim.Calibration.from_directory(Path(calibration_dir))
    index = {q: n for n, q in enumerate(calibration.qubits)}
    model = QuantumCircuit(len(calibration.qubits), 1)
    measured = None
    for op in circuit["instructions"]:
        locus = [index[q] for q in op["locus"]]
        if op["name"] == "prx":
            scale = 1 + over.get(op["locus"][0], 0.0)
            model.append(RGate(op["args"]["angle"] * scale, op["args"]["phase"]), locus)
        elif op["name"] == "measure":
            model.barrier(*locus)
            measured = locus[0]
            model.measure(locus[0], 0)
        else:
            raise ValueError(f"{circuit['name']}: {op['name']} has no model here")
    if measured is None:
        raise ValueError(f"{circuit['name']} measures no qubit")
    target, _ = target_of(calibration)
    scheduled = relaxed(calibration, transpile(model, target=target, optimization_level=0, scheduling_method=method))
    out = QuantumCircuit(*scheduled.qregs, *scheduled.cregs)
    for instruction in scheduled.data:
        if instruction.operation.name == "measure":
            continue
        out.append(instruction.operation, instruction.qubits)
    out.save_probabilities([measured])
    simulator = AerSimulator(method="density_matrix", noise_model=calibration.noise_model(heralded=True))
    p = simulator.run(out).result().data()["probabilities"]
    return float(p[0] - p[1])


def first_measured(circuit: dict[str, Any]) -> str:
    return next(op["locus"][0] for op in circuit["instructions"] if op["name"] == "measure")


def circuits_of(calibration: iqm_sim.Calibration) -> tuple[list[dict[str, Any]], dict[str, str]]:
    partners = {qubit: idle_partner(qubit, calibration) for qubit in IDLE_QUBITS}
    circuits = [idle_arm(qubit, partners[qubit], n) for qubit in IDLE_QUBITS for n in IDLE_PULSES]
    for qubit in TRAIN_QUBITS:
        circuits.append({"name": f"ro0-{qubit}", "instructions": [measure(qubit)]})
        circuits.append({"name": f"ro1-{qubit}", "instructions": [prx(qubit, math.pi), measure(qubit)]})
        for k in AMPLIFY_K:
            circuits.append({"name": f"amp-{qubit}-{k}", "instructions": train(qubit, k)})
    return circuits, partners


def build_from(calibration_dir: Path) -> tuple[dict[str, str], dict[str, Any]]:
    calibration = iqm_sim.Calibration.from_directory(calibration_dir)
    circuits, partners = circuits_of(calibration)
    files = {f"circuits/{c['name']}.json": dump(c) for c in circuits}
    no_error: dict[str, float] = {}
    items = [(c, str(calibration_dir), method, no_error) for method in ("asap", "alap") for c in circuits]
    values = ordered_map(exact, items)
    true = {"asap": values[: len(circuits)], "alap": values[len(circuits) :]}
    z = {
        method: {
            c["name"]: read(value, *calibration.readout(first_measured(c), heralded=True))
            for c, value in zip(circuits, true[method], strict=True)
        }
        for method in true
    }
    idle: dict[str, Any] = {}
    for qubit in IDLE_QUBITS:
        rows = []
        for n in IDLE_PULSES[1:]:
            name, base = f"idle-{qubit}-{n}", f"idle-{qubit}-0"
            asap = z["asap"][name] - z["asap"][base]
            alap = z["alap"][name] - z["alap"][base]
            kept = SHOTS * DESIGN_RETENTION
            se = math.hypot(*(math.sqrt(max(1 - z["alap"][m] ** 2, 1 / kept) / kept) for m in (name, base)))
            rows.append({"pulses": n, "asap": asap, "alap": alap, "separation_se": abs(asap - alap) / se})
        idle[qubit] = {
            "partner": partners[qubit],
            "t1_seconds": calibration.values[f"characterization.model.{qubit}.t1_time"],
            "contrasts": rows,
        }
    seconds = SHOTS * sum(n * DURATIONS["r"] for qubit in IDLE_QUBITS for n in IDLE_PULSES)
    expected = round(len(circuits) * SHOTS * SHOT_SECONDS + seconds, 3)
    job = {
        "job": "probe",
        "circuits": [{"file": rel, "sha256": sha256(text.encode())} for rel, text in files.items()],
        "shots": SHOTS,
        # The job compiles against the calibration set the prediction was made from, or fails if it is gone.
        "options": {**OPTIONS, "calibration_set_id": {QC: calibration.set_id}},
        "expected_seconds": expected,
        "max_credits": {qc: ceiling_credits(expected, price) for qc, price in PRICE.items()},
    }
    prediction = {
        "calibration_set": calibration.set_id,
        "prx_seconds": DURATIONS["r"],
        "idle": idle,
        "z": z,
        "coherent_attribution": {q: COHERENT[q] for q in TRAIN_QUBITS if q in COHERENT},
        "model": (
            "iqm_sim depolarizing PRX with herald-conditioned readout, idle T1/T2 over ASAP and over ALAP schedules "
            "with the joint measure aligned, exact density matrix"
        ),
    }
    files["prediction.json"] = dump(prediction)
    files["cases.json"] = dump(
        {
            "schema": CASE_SCHEMA,
            "case": CASE,
            "question": (
                "Does Garnet schedule a circuit job's gates as soon or as late as possible, read by whether a "
                "pulsed qubit relaxes while an uncoupled qubit runs an identity train, and what over-rotation does "
                "each signed-probe train qubit carry when fitted with its own readout?"
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
    for rel, text in files.items():
        path = directory / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(json.dumps({q: [r["separation_se"] for r in v["contrasts"]] for q, v in prediction["idle"].items()}))


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


def evaluate(counts: dict[str, tuple[int, int]], prediction: dict[str, Any]) -> dict[str, Any]:
    """The preregistered decisions H1 and H2 from per-circuit (ones, shots)."""
    arms: dict[str, list[dict[str, Any]]] = {}
    for qubit, idle in prediction["idle"].items():
        arms[qubit] = []
        for contrast in idle["contrasts"]:
            z, se_z, _ = z_of(counts, f"idle-{qubit}-{contrast['pulses']}")
            z0, se0, _ = z_of(counts, f"idle-{qubit}-0")
            observed, se = z - z0, math.hypot(se_z, se0)
            toward = math.copysign(1.0, contrast["asap"] - contrast["alap"])
            score = toward * (observed - (contrast["asap"] + contrast["alap"]) / 2) / se
            verdict = "asap" if score >= Z_RESOLVE else "alap" if score <= -Z_RESOLVE else "unresolved"
            arms[qubit].append({**contrast, "observed": observed, "se": se, "score": score, "verdict": verdict})
    readings = {arm["verdict"] for rows in arms.values() for arm in rows}
    resolved = readings - {"unresolved"}
    schedule = "mixed" if len(resolved) > 1 else readings.pop() if len(readings) == 1 else "unresolved"
    trains: dict[str, Any] = {}
    for qubit in TRAIN_QUBITS:
        eps, se, chi2, e01, e10 = fit_train(
            [4 * k + 1 for k in AMPLIFY_K],
            [z_of(counts, f"amp-{qubit}-{k}") for k in AMPLIFY_K],
            z_of(counts, f"ro0-{qubit}"),
            z_of(counts, f"ro1-{qubit}"),
        )
        linear = math.isfinite(chi2) and chi2_survival_3(chi2) >= TRAIN_P_MIN
        row: dict[str, Any] = {"eps": eps, "eps_se": se, "chi2": chi2, "e01": e01, "e10": e10, "linear": linear}
        attributed = prediction["coherent_attribution"].get(qubit)
        if attributed is not None and linear:
            distance = abs(eps - attributed) / se
            row["attribution"] = {
                "value": attributed,
                "z": distance,
                "verdict": "consistent" if distance < Z_RESOLVE else "excluded",
            }
        trains[qubit] = row
    return {"h1_schedule": {"verdict": schedule, "arms": arms}, "h2_train_readout": trains}


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
    names = [Path(entry["file"]).stem for entry in row["circuits"]]
    counts = tally(names, json.loads((run_dir / "raw/measurements.json").read_bytes()))
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
    """Kept-shot counts of a model device: the calibration's gate noise and relaxation over one schedule, the
    over-rotations eps and SYNTHETIC_READOUT, sampled at SHOTS."""
    values = ordered_map(exact, [(c, str(calibration_dir), method, eps) for c in circuits])
    rng = np.random.default_rng(seed)
    counts = {}
    for circuit, value in zip(circuits, values, strict=True):
        e01, e10 = SYNTHETIC_READOUT.get(first_measured(circuit), SYNTHETIC_DEFAULT)
        counts[circuit["name"]] = (int(rng.binomial(SHOTS, (1 - read(value, e01, e10)) / 2)), SHOTS)
    return counts


def self_test() -> str:
    calibration_dir = iqm_sim.EVIDENCE / QC / "calibration"
    files, prediction = build_from(calibration_dir)
    case = json.loads(files["cases.json"])
    if case["prediction_sha256"] != sha256(files["prediction.json"].encode()):
        raise RuntimeError("cases.json does not bind the prediction it was built with")
    for qubit, row in prediction["idle"].items():
        if frozenset((qubit, row["partner"])) in iqm_sim.Calibration.from_directory(calibration_dir).cz:
            raise RuntimeError(f"{qubit} shares a coupler with its idle partner {row['partner']}")
        weakest = min(contrast["separation_se"] for contrast in row["contrasts"])
        if weakest < 2 * Z_RESOLVE:
            raise RuntimeError(f"{qubit}: the schedules separate by only {weakest:.1f} standard errors")
    circuits = [json.loads(text) for rel, text in files.items() if rel.startswith("circuits/")]
    injected = {"QB6": -0.012, "QB11": 0.027}
    late = evaluate(synthetic(circuits, calibration_dir, "asap", injected, SYNTHETIC_SEEDS[0]), prediction)
    if late["h1_schedule"]["verdict"] != "asap":
        raise RuntimeError(f"an ASAP device reads {late['h1_schedule']}")
    for qubit, eps in injected.items():
        got = late["h2_train_readout"][qubit]
        if not got["linear"] or abs(got["eps"] - eps) > 4 * got["eps_se"] + 0.002:
            raise RuntimeError(f"{qubit}: injected {eps} through its own readout, recovered {got}")
    if late["h2_train_readout"]["QB11"].get("attribution", {}).get("verdict") != "consistent":
        raise RuntimeError(f"an injected 2.7 % QB11 over-rotation reads {late['h2_train_readout']['QB11']}")
    flat = evaluate(synthetic(circuits, calibration_dir, "alap", {}, SYNTHETIC_SEEDS[1]), prediction)
    if flat["h1_schedule"]["verdict"] != "alap":
        raise RuntimeError(f"an ALAP device reads {flat['h1_schedule']}")
    if flat["h2_train_readout"]["QB11"].get("attribution", {}).get("verdict") != "excluded":
        raise RuntimeError(f"a QB11 without over-rotation reads {flat['h2_train_readout']['QB11']}")
    return (
        f"idle schedule probe: {len(circuits)} circuits; an ASAP and an ALAP model device read their own schedule, "
        "and injected over-rotations come back through readouts unlike the calibration's"
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
