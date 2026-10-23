"""IQM Garnet case of the signed sedenion kernel probe: odd dilation overlap against an even offset.

gororoba_quantum/signed_kernel_probe.py certifies the kernel u = (e4 - e15)/sqrt2 of L_(e1+e10) and
the perturbation B(t) = (L_e1 + L_e10 + t L_e2)/(2 + |t|): the dilation overlap Re<v|B(t)|u> =
t/(2 + |t|) is odd in t and first order, read as <Z> of control qubit 6 of matched_signed_probe(),
one parametrized circuit for every t whose bound compiles differ only in rotation angles. The arms
+t and -t give the odd part (Z(t) - Z(-t))/2, which cancels every offset even in t such as readout
asymmetry, and the even part (Z(t) + Z(-t))/2. The registered falsifier is an odd part of zero or of
the wrong sign at either |t|. Amplitude damping is not unital, so under relaxation the odd part is
not a fixed visibility times t/(2 + |t|); prediction.json records the modeled odd part per |t| as a
prediction, not as a visibility law.

The case compiles the matched probe once per transpiler seed onto Garnet's calibrated CZ couplers
(basis r and cz), predicts each seed's odd part at t = 0.25 from the case's own copy of the
calibration (scripts/iqm_sim.py noise plus idle T1 and T2 relaxation over the ALAP schedule) and
keeps the seed with the largest predicted visibility. Its job holds arms t = +-0.25 and t = +-0.05,
the +-0.05 arms replicated to reach their shots, under active reset with all-zeros heralding:
docs/design/iqm-garnet-timing-pilot.md measured one active-reset cycle leaving QB1 6 % excited, and
heralding discards every shot whose pre-circuit measurement is not all zeros.

Usage: "$PYTHON" scripts/iqm_signed_probe.py (build DIR | check DIR | analyze RUN_DIR... --out FILE [--replay]
       | --self-test)
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
import sys
from pathlib import Path
from typing import Any

from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Delay, Measure, Parameter
from qiskit.circuit.library import CZGate, RGate
from qiskit.transpiler import CouplingMap, InstructionProperties, Target
from qiskit_aer import AerSimulator
from qiskit_aer.noise import RelaxationNoisePass

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import iqm_sim  # noqa: E402
from iqm_jobs import CASE_SCHEMA, dump  # noqa: E402
from iqm_platform import sha256  # noqa: E402

import signed_kernel_probe as skp  # noqa: E402
from parallel import ordered_map  # noqa: E402

CASE = "signed-kernel-probe"
QC = "garnet"
SEEDS = range(8)
SELECT_T = 0.25
STRONG_T = 0.25
WEAK_T = 0.05
STRONG_SHOTS = 20000
WEAK_SHOTS = 20000
WEAK_COPIES = 5
PREDICTION_SHOTS = 400000
SELECTION_SHOTS = 100000
PREDICTION_SEED = 20261022
# Measured on Garnet QB1 by the reset and billing pilot: 37.5 us of execution per active-reset shot.
ACTIVE_SHOT_SECONDS = 0.0000375
OPTIONS: dict[str, Any] = {"heralding_mode": "zeros", "active_reset_cycles": 1}
QCS = ["garnet:mock", "garnet"]
CALIBRATION_FILES = ("metrics.json", "dynamic-quantum-architecture.json")
DURATIONS = {"r": 16e-9, "cz": 40e-9, "measure": 480e-9}


def law(t: float) -> float:
    return t / (2 + abs(t))


def target_of(calibration: iqm_sim.Calibration) -> tuple[Target, CouplingMap]:
    index = {q: n for n, q in enumerate(calibration.qubits)}
    edges = [(index[a], index[b]) for pair in calibration.cz for a, b in [sorted(pair, key=calibration.qubits.index)]]
    coupling = CouplingMap([e for a, b in edges for e in ((a, b), (b, a))])
    target = Target(num_qubits=len(calibration.qubits), dt=1e-9)
    n = len(calibration.qubits)
    target.add_instruction(
        RGate(Parameter("angle"), Parameter("phase")),
        {(q,): InstructionProperties(duration=DURATIONS["r"]) for q in range(n)},
    )
    target.add_instruction(CZGate(), {e: InstructionProperties(duration=DURATIONS["cz"]) for e in coupling.get_edges()})
    target.add_instruction(Measure(), {(q,): InstructionProperties(duration=DURATIONS["measure"]) for q in range(n)})
    target.add_instruction(Delay(Parameter("t")), {(q,): None for q in range(n)})
    return target, coupling


# A qubit no gate touches stays in |0>, which idle T1/T2 relaxation leaves unchanged, so its relaxation
# times cannot reach the reading; one without a calibrated value takes this inert placeholder.
UNTOUCHED_SECONDS = 1.0


def relaxation(calibration: iqm_sim.Calibration, touched: set[str] | None = None) -> RelaxationNoisePass:
    """Idle T1/T2 from the calibration, required for every touched qubit (all qubits when touched is
    None); T2 is capped at 2 T1, the physical bound."""
    required = set(calibration.qubits) if touched is None else touched
    missing = [
        f"characterization.model.{q}.{kind}"
        for q in sorted(required, key=calibration.qubits.index)
        for kind in ("t1_time", "t2_time")
        if f"characterization.model.{q}.{kind}" not in calibration.values
    ]
    if missing:
        raise ValueError(f"the calibration lacks valid relaxation times of touched qubits: {missing}")
    t1 = [calibration.values.get(f"characterization.model.{q}.t1_time", UNTOUCHED_SECONDS) for q in calibration.qubits]
    t2 = [
        min(calibration.values.get(f"characterization.model.{q}.t2_time", UNTOUCHED_SECONDS), 2 * t1[n])
        for n, q in enumerate(calibration.qubits)
    ]
    return RelaxationNoisePass(t1s=t1, t2s=t2, dt=1e-9, op_types=[Delay])


def relaxed(calibration: iqm_sim.Calibration, scheduled: QuantumCircuit) -> QuantumCircuit:
    """A scheduled circuit with idle relaxation on its delays, requiring calibrated times for the qubits
    its gates touch."""
    touched = {
        calibration.qubits[scheduled.find_bit(q).index]
        for instruction in scheduled.data
        if instruction.operation.name != "delay"
        for q in instruction.qubits
    }
    return relaxation(calibration, touched)(scheduled)


def predict(
    compiled: QuantumCircuit, t: float, calibration: iqm_sim.Calibration, target: Target, shots: int = PREDICTION_SHOTS
) -> float:
    """<Z> of the control under the calibration noise and idle relaxation, sampled at a fixed seed."""
    bound = compiled.assign_parameters(skp.matched_values(t))
    scheduled = transpile(bound, target=target, optimization_level=0, scheduling_method="alap")
    noisy = relaxed(calibration, scheduled)
    simulator = AerSimulator(noise_model=calibration.noise_model(), seed_simulator=PREDICTION_SEED)
    counts = simulator.run(noisy, shots=shots).result().get_counts()
    return sum((1 if key[-1] == "0" else -1) * n for key, n in counts.items()) / shots


def to_iqm(bound: QuantumCircuit, name: str, qubits: list[str]) -> dict[str, Any]:
    instructions = []
    for item in bound.data:
        op, locus = item.operation, [qubits[bound.find_bit(q).index] for q in item.qubits]
        if op.name == "r":
            angle, phase = (float(p) for p in op.params)
            instructions.append({"name": "prx", "locus": locus, "args": {"angle": angle, "phase": phase}})
        elif op.name == "cz":
            instructions.append({"name": "cz", "locus": locus, "args": {}})
        elif op.name == "measure":
            instructions.append({"name": "measure", "locus": locus, "args": {"key": "c"}})
        elif op.name != "barrier":
            raise ValueError(f"{name}: {op.name} is not a Garnet native operation")
    return {"name": name, "instructions": instructions}


def seed_trial(item: tuple[int, str]) -> tuple[float, int, int, QuantumCircuit]:
    """One transpiler seed's compile and its predicted visibility at SELECT_T: (visibility, seed, cz, compile)."""
    seed, calibration_dir = item
    calibration = iqm_sim.Calibration.from_directory(Path(calibration_dir))
    target, coupling = target_of(calibration)
    compiled = transpile(
        skp.matched_signed_probe(),
        basis_gates=["r", "cz"],
        coupling_map=coupling,
        optimization_level=3,
        seed_transpiler=seed,
    )
    plus = predict(compiled, SELECT_T, calibration, target, SELECTION_SHOTS)
    odd = (plus - predict(compiled, -SELECT_T, calibration, target, SELECTION_SHOTS)) / 2
    return odd / law(SELECT_T), seed, compiled.count_ops().get("cz", 0), compiled


def arm_prediction(item: tuple[float, str, QuantumCircuit]) -> float:
    t, calibration_dir, compiled = item
    calibration = iqm_sim.Calibration.from_directory(Path(calibration_dir))
    target, _ = target_of(calibration)
    return predict(compiled, t, calibration, target)


def build_from(calibration_dir: Path) -> tuple[dict[str, str], dict[str, Any]]:
    calibration = iqm_sim.Calibration.from_directory(calibration_dir)
    best: tuple[float, int, QuantumCircuit] | None = None
    seeds = []
    # Seeds compile and predict independently; ordered_map returns them in seed order, so the first
    # seed of the largest visibility wins as in a serial loop.
    for visibility, seed, cz, compiled in ordered_map(seed_trial, [(seed, str(calibration_dir)) for seed in SEEDS]):
        seeds.append({"seed": seed, "cz": cz, "visibility": round(visibility, 4)})
        if best is None or visibility > best[0]:
            best = (visibility, seed, compiled)
    if best is None:
        raise ValueError("no transpiler seed compiled")
    _, seed, compiled = best
    ts = (STRONG_T, -STRONG_T, WEAK_T, -WEAK_T)
    predicted = ordered_map(arm_prediction, [(t, str(calibration_dir), compiled) for t in ts])
    arms = [{"t": t, "law": law(t), "predicted_z": z} for t, z in zip(ts, predicted, strict=True)]
    files: dict[str, str] = {}
    names = []
    for t, copies in ((STRONG_T, 1), (-STRONG_T, 1), (WEAK_T, WEAK_COPIES), (-WEAK_T, WEAK_COPIES)):
        bound = compiled.assign_parameters(skp.matched_values(t))
        for copy in range(copies):
            name = f"t{t:+.2f}-{copy:02d}"
            rel = f"circuits/{name}.json"
            files[rel] = dump(to_iqm(bound, name, calibration.qubits))
            names.append((rel, t))
    weak = [rel for rel, t in names if abs(t) == WEAK_T]
    strong = [rel for rel, t in names if abs(t) == STRONG_T]
    jobs = []
    for job, rels, shots in (("strong", strong, STRONG_SHOTS), ("weak", weak, WEAK_SHOTS)):
        jobs.append(
            {
                "job": job,
                "circuits": [{"file": rel, "sha256": sha256(files[rel].encode())} for rel in rels],
                "shots": shots,
                # The job compiles against the calibration set the prediction was made from, or fails if it is gone.
                "options": {**OPTIONS, "calibration_set_id": calibration.set_id},
                "expected_seconds": round(len(rels) * shots * ACTIVE_SHOT_SECONDS, 3),
            }
        )
    by_t = {arm["t"]: arm["predicted_z"] for arm in arms}
    prediction = {
        "calibration_set": calibration.set_id,
        "transpiler_seeds": seeds,
        "chosen_seed": seed,
        "cz": compiled.count_ops().get("cz", 0),
        "physical_qubits": sorted(
            {q for rel, _ in names[:1] for op in json.loads(files[rel])["instructions"] for q in op["locus"]}
        ),
        "arms": arms,
        "odd": {
            f"{t}": {"predicted": (by_t[t] - by_t[-t]) / 2, "law": law(t), "even_offset": (by_t[t] + by_t[-t]) / 2}
            for t in (STRONG_T, WEAK_T)
        },
        "model": (
            "iqm_sim depolarizing PRX and CZ, readout errors, ALAP idle T1/T2; no coherent error, leakage or crosstalk"
        ),
    }
    files["cases.json"] = dump(
        {
            "schema": CASE_SCHEMA,
            "case": CASE,
            "question": (
                "Is the dilation overlap of the perturbed sedenion kernel odd in t on Garnet: does (Z(t) - Z(-t))/2 "
                "carry the sign of t, as Re<v|B(t)|u> = t/(2 + |t|) requires?"
            ),
            "ideal": {f"{t:+.2f}": law(t) for t in (STRONG_T, -STRONG_T, WEAK_T, -WEAK_T)},
            "qcs": QCS,
            "jobs": jobs,
        }
    )
    files["prediction.json"] = dump(prediction)
    return files, prediction


def write(directory: Path) -> None:
    calibration_dir = directory / "calibration"
    calibration_dir.mkdir(parents=True, exist_ok=True)
    source = iqm_sim.EVIDENCE / QC / "calibration"
    for name in CALIBRATION_FILES:
        shutil.copyfile(source / name, calibration_dir / name)
    files, prediction = build_from(calibration_dir)
    for rel, text in files.items():
        path = directory / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(json.dumps({k: prediction[k] for k in ("chosen_seed", "cz", "odd")}, indent=1))


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


# Preregistered decision (docs/design/iqm-garnet-signed-kernel-probe.md): at each |t| the odd part
# resolves the sign of t when it lies Z_RESOLVE standard errors from zero with the sign of t, and
# falsifies the signed law when it lies Z_RESOLVE standard errors from zero with the opposite sign.
Z_RESOLVE = 3.0


def analyze(run_dirs: list[Path]) -> dict[str, Any]:
    """Odd and even parts, decisions, predictions and billing of the retained Garnet probe runs."""
    import iqm_jobs

    arms: dict[float, list[int]] = {}
    runs = []
    # The prediction both runs carry must be the retained case's, which core-638 rebuilds from its
    # calibration copy; cases.json predates a recorded prediction digest, so the case directory binds it.
    case_name = json.loads((sorted(run_dirs)[0] / "cases.json").read_text(encoding="utf-8"))["case"]
    retained = (ROOT / "results/iqm/cases" / case_name / "prediction.json").read_bytes()
    for run_dir in run_dirs:
        if (run_dir / "prediction.json").read_bytes() != retained:
            raise ValueError(f"{run_dir}/prediction.json differs from results/iqm/cases/{case_name}/prediction.json")
    prediction = json.loads(retained)
    # The preregistered analysis reads one Garnet run of each job of one case, compiled against the
    # calibration set the prediction was made from; mock outcomes never enter it.
    digests = {sha256((run_dir / "cases.json").read_bytes()) for run_dir in run_dirs}
    if len(digests) != 1:
        raise ValueError(f"the runs copy {len(digests)} different cases.json; one analysis reads one case")
    names = sorted(json.loads((run_dir / "submission.json").read_text(encoding="utf-8"))["job"] for run_dir in run_dirs)
    if names != ["strong", "weak"]:
        raise ValueError(f"the analysis reads exactly one strong and one weak run, not {names}")
    for run_dir in run_dirs:
        submission = json.loads((run_dir / "submission.json").read_text(encoding="utf-8"))
        compiled = json.loads((run_dir / "raw/job.json").read_bytes())["compilation"]["calibration_set_id"]
        if submission["qc"] != QC or compiled != prediction["calibration_set"]:
            raise ValueError(
                f"{run_dir}: ran on {submission['qc']} against {compiled}, not {QC} against the prediction's set"
            )
    if len({run_dir.resolve() for run_dir in run_dirs}) != len(run_dirs):
        raise ValueError("a run directory is named twice; each acquisition counts once")
    jobs = [json.loads((run_dir / "submission.json").read_text(encoding="utf-8"))["job_id"] for run_dir in run_dirs]
    if len(set(jobs)) != len(jobs):
        raise ValueError("two run directories hold one job; each acquisition counts once")
    for run_dir in sorted(run_dirs):
        facts = iqm_jobs.run_facts(run_dir)
        submission = json.loads((run_dir / "submission.json").read_text(encoding="utf-8"))
        record = json.loads((run_dir / "raw/job.json").read_bytes())
        case = json.loads((run_dir / "cases.json").read_text(encoding="utf-8"))
        row = [r for r in case["jobs"] if r["job"] == submission["job"]][0]
        measured = json.loads((run_dir / "raw/measurements.json").read_bytes())
        kept = 0
        for entry, circuit in zip(row["circuits"], measured, strict=True):
            t = float(entry["file"].split("/t")[1].rsplit("-", 1)[0])
            bits = [shot[0] for shot in circuit["c"]]
            tally = arms.setdefault(t, [0, 0])
            tally[0] += sum(bits)
            tally[1] += len(bits)
            kept += len(bits)
        runs.append(
            {
                "run": run_dir.name,
                "job": submission["job"],
                "qc": submission["qc"],
                "calibration_set": record["compilation"]["calibration_set_id"],
                "estimate_seconds": record["compilation"]["execution_runtime_estimate_seconds"],
                "runtime_seconds": record["metrics"]["runtime_seconds"],
                "billed_seconds": record["metrics"]["billed_seconds"],
                "charge": facts["charge"],
                "heralding_retention": kept / (row["shots"] * len(row["circuits"])),
            }
        )
    z = {t: (1 - 2 * ones / n, 1 / math.sqrt(n), n) for t, (ones, n) in arms.items()}
    parts = {}
    for size in sorted({abs(t) for t in z}):
        (plus, se_plus, n_plus), (minus, se_minus, n_minus) = z[size], z[-size]
        odd, even, se = (plus - minus) / 2, (plus + minus) / 2, math.hypot(se_plus, se_minus) / 2
        decision = "sign resolved" if odd / se >= Z_RESOLVE else "falsified" if odd / se <= -Z_RESOLVE else "unresolved"
        predicted = prediction["odd"][f"{size}"]["predicted"]
        parts[f"{size}"] = {
            "z_plus": plus,
            "z_minus": minus,
            "kept_plus": n_plus,
            "kept_minus": n_minus,
            "odd": odd,
            "even": even,
            "se": se,
            "odd_over_se": odd / se,
            "decision": decision,
            "law": law(size),
            "odd_over_law": odd / law(size),
            "odd_over_law_se": se / law(size),
            "predicted_odd": predicted,
            "prediction_z": (odd - predicted) / se,
        }
    ratios = [(v["odd_over_law"], v["odd_over_law_se"]) for v in parts.values()]
    weight = sum(1 / s**2 for _, s in ratios)
    pooled = sum(r / s**2 for r, s in ratios) / weight
    chi2 = sum(((r - pooled) / s) ** 2 for r, s in ratios)
    return {
        "schema": "iqm-signed-probe-analysis-v1",
        "runs": runs,
        "parts": parts,
        "falsified": any(v["decision"] == "falsified" for v in parts.values()),
        "linear_visibility": {"pooled": pooled, "se": 1 / math.sqrt(weight), "chi2": chi2, "dof": len(ratios) - 1},
        "credits_charged": round(sum(r["charge"] for r in runs), 6),
    }


def self_test() -> str:
    calibration = iqm_sim.Calibration(QC)
    target, coupling = target_of(calibration)
    compiled = transpile(
        skp.matched_signed_probe(),
        basis_gates=["r", "cz"],
        coupling_map=coupling,
        optimization_level=1,
        seed_transpiler=0,
    )
    ideal = AerSimulator(seed_simulator=1)
    for t in (0.25, -0.25):
        bound = compiled.assign_parameters(skp.matched_values(t))
        counts = ideal.run(bound, shots=200000).result().get_counts()
        z = sum((1 if key[-1] == "0" else -1) * n for key, n in counts.items()) / 200000
        if abs(z - law(t)) > 5 * math.sqrt(1 / 200000) * 2:
            raise RuntimeError(f"the noiseless compile reads {z} at t = {t}, not {law(t)}")
        circuit = to_iqm(bound, "probe", calibration.qubits)
        for op in circuit["instructions"]:
            if op["name"] == "cz" and frozenset(op["locus"]) not in calibration.cz:
                raise RuntimeError(f"cz on {op['locus']} is off the coupler graph")
    flipped = QuantumCircuit(1)
    flipped.ry(0.3, 0)
    try:
        to_iqm(flipped, "bad", calibration.qubits)
    except ValueError:
        pass
    else:
        raise RuntimeError("a non-native operation was translated")
    return (
        f"iqm signed probe: noiseless Garnet compile reads t/(2+|t|) at t = +-0.25; {compiled.count_ops().get('cz')} CZ"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("build").add_argument("directory", type=Path)
    sub.add_parser("check").add_argument("directory", type=Path)
    an = sub.add_parser("analyze")
    an.add_argument("run_dirs", type=Path, nargs="+")
    an.add_argument("--out", type=Path, required=True)
    an.add_argument("--replay", action="store_true", help="compare --out with the recomputation")
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
    elif args.command == "build":
        write(args.directory)
    elif args.command == "check":
        check(args.directory)
    elif args.command == "analyze":
        text = dump(analyze(args.run_dirs))
        if args.replay:
            if args.out.read_text(encoding="utf-8") != text:
                raise ValueError(f"{args.out} differs from the recomputation")
            print(f"{args.out}: replays byte for byte")
        else:
            args.out.write_text(text, encoding="utf-8")
    else:
        parser.error("choose build, check or --self-test")
    return 0


if __name__ == "__main__":
    sys.exit(main())
