"""IQM Garnet case of the kernel cancellation probe: the zero-divisor sign, its control and its coherent errors.

gororoba_quantum/kernel_cancellation.py reads <Z> of a control qubit as cos(2 theta) for the certified
sedenion kernel vector u = (e4 - e15)/sqrt2 of L(e1 + e10) and as 1 for the bright vector
(e4 + e15)/sqrt2, with theta = pi/4 + phi the selector angle between e1 and e10. One job holds:

- kernel arms phi = +-0.1 (listed +, -, -, + so drift along the batch cancels in the odd part),
  +-0.3 and two copies of phi = 0; the odd part (Z(phi) - Z(-phi))/2 = -V sin(2 phi) carries the
  zero-divisor sign, and the even part holds every offset even in phi;
- bright arms phi = +-0.1 (+, -, -, +) and phi = 0, whose odd part is zero for every visibility;
- readout calibration of the control qubit (a bare measure and a pi pulse then measure);
- amplification trains of 4k + 1 prx(pi/2) pulses, k in AMPLIFY_K, on the qubit whose prx angles
  carry theta and on the control: <Z> = -sin((4k + 1)(pi/2) eps) for a relative over-rotation eps.

On the compile, scripts/iqm_probe_audit.py's first-order response puts every coherent error except the
theta qubit's over-rotation at zero in both parts; that over-rotation scales the odd part by 1 + O(eps)
and shifts the even part by dEven/deps * eps. So the case predicts the kernel even part from the
readout calibration and the measured eps (H4), and the odd part's sign is first-order free of coherent
error. Heralding (all zeros) and one active-reset cycle follow docs/notes/iqm/README.md.

Preregistered decisions (Z_RESOLVE standard errors):
- H1 zero-divisor sign: at phi = 0.1 and 0.3 the kernel odd part resolves when odd/se <= -Z_RESOLVE and
  falsifies the cancellation law when odd/se >= +Z_RESOLVE.
- H2 bright control: the bright odd part at phi = 0.1 falsifies the probe (a circuit artifact) when
  |odd/se| >= Z_RESOLVE.
- H3 sine law: odd(0.3)/odd(0.1) departs from sin(0.6)/sin(0.2) by Z_RESOLVE standard errors.
- H4 even-part decomposition: the kernel even part at phi = 0.1 departs from
  (e10 - e01) + r R + r V dEven/deps eps by Z_RESOLVE standard errors: readout offset and scale
  r = 1 - e01 - e10 from the readout calibration, R the prediction's incoherent even part net of its
  modeled readout (idle relaxation, which is not unital), V the visibility from the phi = 0.1 odd
  part, eps from the theta qubit's trains.
- H5 amplification: the trains' <Z> is linear in 4k + 1 (the server plays each pulse); a slope ratio
  outside Z_RESOLVE standard errors marks pulse merging, and H4 is then not evaluated.

Usage: "$PYTHON" scripts/iqm_cancellation_probe.py (build DIR | check DIR | analyze RUN_DIR... --out FILE
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
from qiskit import transpile
from qiskit_aer import AerSimulator

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import iqm_sim  # noqa: E402
from iqm_jobs import CASE_SCHEMA, dump  # noqa: E402
from iqm_platform import sha256  # noqa: E402
from iqm_probe_audit import Register  # noqa: E402
from iqm_signed_probe import relaxation, target_of, to_iqm  # noqa: E402

import kernel_cancellation as kc  # noqa: E402

CASE = "kernel-cancellation-probe"
QC = "garnet"
QCS = ["garnet:mock", "garnet"]
SEEDS = range(24)
SHOTS = 4000
# Garnet's price per second; the build records each QC's ceiling in cases.json, which submit enforces.
PRICE = {"garnet": 0.5, "garnet:mock": 0.0}
JOB_SECONDS = 1.6
# The heralded 199-CZ probe ran 21.4 us per requested shot beyond the fixed job cost; shorter circuits
# run faster, so this bounds the schedule from above.
SHOT_SECONDS = 0.0000214
OPTIONS: dict[str, Any] = {"heralding_mode": "zeros", "active_reset_cycles": 1}
CALIBRATION_FILES = ("metrics.json", "dynamic-quantum-architecture.json")
PREDICTION_SHOTS = 200000
PREDICTION_SEED = 20261023
AMPLIFY_K = (0, 5, 10)
STEP = 1e-4
Z_RESOLVE = 3.0
# H5 marks a train non-linear above the chi-square quantile whose upper tail equals the one-sided
# Z_RESOLVE normal tail; with three train lengths the residual has two degrees of freedom, whose
# survival function is exp(-x/2).
H5_CHI2_CUTOFF = -2 * math.log(0.5 * math.erfc(Z_RESOLVE / math.sqrt(2)))
SYNTHETIC_VISIBILITY = 0.6
SYNTHETIC_READOUT = (0.01, 0.03)
# (name, bright, phi) in list order: +, -, -, + for each contrast.
PROBE_ARMS = (
    ("k+0.1a", False, 0.1),
    ("k-0.1a", False, -0.1),
    ("k-0.1b", False, -0.1),
    ("k+0.1b", False, 0.1),
    ("k+0.3a", False, 0.3),
    ("k-0.3a", False, -0.3),
    ("k-0.3b", False, -0.3),
    ("k+0.3b", False, 0.3),
    ("k0a", False, 0.0),
    ("k0b", False, 0.0),
    ("b+0.1a", True, 0.1),
    ("b-0.1a", True, -0.1),
    ("b-0.1b", True, -0.1),
    ("b+0.1b", True, 0.1),
    ("b0", True, 0.0),
)


def measure(qubit: str) -> dict[str, Any]:
    return {"name": "measure", "locus": [qubit], "args": {"key": "c"}}


def prx(qubit: str, angle: float, phase: float = 0.0) -> dict[str, Any]:
    return {"name": "prx", "locus": [qubit], "args": {"angle": angle, "phase": phase}}


def train(qubit: str, k: int) -> list[dict[str, Any]]:
    return [prx(qubit, math.pi / 2) for _ in range(4 * k + 1)] + [measure(qubit)]


def compile_probe(calibration: iqm_sim.Calibration) -> tuple[int, Any, list[dict[str, Any]]]:
    """The seed with the fewest CZ (lowest seed on a tie); kernel and bright bind the same compile."""
    _, coupling = target_of(calibration)
    best = None
    seeds = []
    for seed in SEEDS:
        compiled = transpile(
            kc.cancellation_probe(),
            basis_gates=["r", "cz"],
            coupling_map=coupling,
            optimization_level=3,
            seed_transpiler=seed,
        )
        cz = compiled.count_ops().get("cz", 0)
        seeds.append({"seed": seed, "cz": cz})
        if best is None or cz < best[1]:
            best = (seed, cz, compiled)
    if best is None:
        raise ValueError("no transpiler seed compiled")
    return best[0], best[2], seeds


def bind(
    compiled: Any, phi: float, calibration: iqm_sim.Calibration, name: str, bright: bool = False
) -> dict[str, Any]:
    return to_iqm(compiled.assign_parameters(kc.values(phi, bright)), name, calibration.qubits)


def theta_qubits(compiled: Any, calibration: iqm_sim.Calibration) -> list[str]:
    """Qubits whose prx angles change with theta: the over-rotations that tilt the selector."""
    a = bind(compiled, 0.1, calibration, "a")["instructions"]
    b = bind(compiled, -0.1, calibration, "b")["instructions"]
    if [(op["name"], op["locus"]) for op in a] != [(op["name"], op["locus"]) for op in b]:
        raise ValueError("the +phi and -phi compiles differ in structure")
    moved = {x["locus"][0] for x, y in zip(a, b, strict=True) if x["name"] == "prx" and x["args"] != y["args"]}
    return sorted(moved, key=lambda q: int(q[2:]))


def response(instructions_by_phi: dict[float, list[dict[str, Any]]], qubit: str) -> dict[str, float]:
    """First-order odd and even response at phi = 0.1 to a relative over-rotation of qubit's prx pulses."""
    register = Register(instructions_by_phi[0.1])
    error = ("over", register.index[qubit])
    grad = {
        phi: (register.z(ops, {error: STEP}) - register.z(ops, {error: -STEP})) / (2 * STEP)
        for phi, ops in instructions_by_phi.items()
    }
    return {"odd": (grad[0.1] - grad[-0.1]) / 2, "even": (grad[0.1] + grad[-0.1]) / 2}


def predict(circuit: dict[str, Any], calibration: iqm_sim.Calibration, target: Any) -> float:
    """<Z> of the measured qubit under calibration noise and ALAP idle relaxation."""
    qiskit_circuit, _ = iqm_sim.to_qiskit(circuit, calibration)
    scheduled = transpile(qiskit_circuit, target=target, optimization_level=0, scheduling_method="alap")
    noisy = relaxation(calibration)(scheduled)
    simulator = AerSimulator(noise_model=calibration.noise_model(), seed_simulator=PREDICTION_SEED)
    counts = simulator.run(noisy, shots=PREDICTION_SHOTS).result().get_counts()
    ones = sum(n for key, n in counts.items() if key[-1] == "1")
    return 1 - 2 * ones / PREDICTION_SHOTS


def build_from(calibration_dir: Path) -> tuple[dict[str, str], dict[str, Any]]:
    calibration = iqm_sim.Calibration.from_directory(calibration_dir)
    target, _ = target_of(calibration)
    seed, compiled, seeds = compile_probe(calibration)
    tilted = theta_qubits(compiled, calibration)
    circuits: list[tuple[str, dict[str, Any]]] = []
    for name, bright, phi in PROBE_ARMS:
        circuits.append((name, bind(compiled, phi, calibration, name, bright)))
    control = next(op["locus"][0] for op in circuits[0][1]["instructions"] if op["name"] == "measure")
    if any(next(op["locus"][0] for op in c["instructions"] if op["name"] == "measure") != control for _, c in circuits):
        raise ValueError("the kernel and bright compiles measure different qubits")
    circuits.append(("ro0", {"name": "ro0", "instructions": [measure(control)]}))
    circuits.append(("ro1", {"name": "ro1", "instructions": [prx(control, math.pi), measure(control)]}))
    for qubit in [*tilted, control]:
        for k in AMPLIFY_K:
            name = f"amp-{qubit}-{k}"
            circuits.append((name, {"name": name, "instructions": train(qubit, k)}))
    files: dict[str, str] = {}
    for name, circuit in circuits:
        files[f"circuits/{name}.json"] = dump(circuit)
    kernel_ops = {phi: bind(compiled, phi, calibration, "r")["instructions"] for phi in (0.1, -0.1)}
    expected = round(len(circuits) * SHOTS * SHOT_SECONDS, 3)
    ceiling = {qc: math.ceil(JOB_SECONDS + expected) * price for qc, price in PRICE.items()}
    job = {
        "job": "cancellation",
        "circuits": [
            {"file": f"circuits/{n}.json", "sha256": sha256(files[f"circuits/{n}.json"].encode())} for n, _ in circuits
        ],
        "shots": SHOTS,
        # The job compiles against the calibration set the prediction was made from, or fails if it is gone.
        "options": {**OPTIONS, "calibration_set_id": {QC: calibration.set_id}},
        "expected_seconds": expected,
        "max_credits": ceiling,
    }
    used = sorted({q for op in circuits[0][1]["instructions"] for q in op["locus"]}, key=lambda q: int(q[2:]))
    prediction = {
        "calibration_set": calibration.set_id,
        "transpiler_seeds": seeds,
        "chosen_seed": seed,
        "cz": compiled.count_ops().get("cz", 0),
        "physical_qubits": used,
        "control": control,
        "theta_qubits": tilted,
        "z": {name: predict(circuit, calibration, target) for name, circuit in circuits},
        "response": {q: response(kernel_ops, q) for q in tilted},
        "model": "iqm_sim depolarizing PRX and CZ, readout errors, ALAP idle T1/T2; coherent response first order",
    }
    files["cases.json"] = dump(
        {
            "schema": CASE_SCHEMA,
            "case": CASE,
            "question": (
                "Does Garnet read the zero-divisor sign of the certified sedenion kernel, cos(2 theta) changing "
                "sign at the balanced selector, while the bright vector reads flat, and does the selector "
                "qubit's measured over-rotation account for the kernel's even offset?"
            ),
            "ideal": {name: kc.law(phi, bright) for name, bright, phi in PROBE_ARMS},
            "qcs": QCS,
            "jobs": [job],
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
    print(json.dumps({k: prediction[k] for k in ("chosen_seed", "cz", "control", "theta_qubits")}, indent=1))


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


def tally(names: list[str], measured: list[dict[str, Any]]) -> dict[str, tuple[int, int]]:
    """(ones, shots) per circuit name, summed over the runs."""
    out: dict[str, tuple[int, int]] = {}
    for name, circuit in zip(names, measured, strict=True):
        bits = [shot[0] for shot in circuit["c"]]
        ones, n = out.get(name, (0, 0))
        out[name] = (ones + sum(bits), n + len(bits))
    return out


def z_of(counts: dict[str, tuple[int, int]], *names: str) -> tuple[float, float, int]:
    ones = sum(counts[n][0] for n in names)
    n = sum(counts[n][1] for n in names)
    z = 1 - 2 * ones / n
    return z, math.sqrt(max(1 - z * z, 1.0 / n) / n), n


def decide(value: float, se: float) -> str:
    return "resolved" if value / se <= -Z_RESOLVE else "falsified" if value / se >= Z_RESOLVE else "unresolved"


def evaluate(counts: dict[str, tuple[int, int]], prediction: dict[str, Any]) -> dict[str, Any]:
    """The preregistered decisions H1-H5 from per-circuit (ones, shots)."""
    contrast: dict[str, dict[str, Any]] = {}
    for label, plus, minus in (
        ("kernel 0.1", ("k+0.1a", "k+0.1b"), ("k-0.1a", "k-0.1b")),
        ("kernel 0.3", ("k+0.3a", "k+0.3b"), ("k-0.3a", "k-0.3b")),
        ("bright 0.1", ("b+0.1a", "b+0.1b"), ("b-0.1a", "b-0.1b")),
    ):
        (zp, sp, np_), (zm, sm, nm) = z_of(counts, *plus), z_of(counts, *minus)
        contrast[label] = {
            "z_plus": zp,
            "z_minus": zm,
            "kept": [np_, nm],
            "odd": (zp - zm) / 2,
            "even": (zp + zm) / 2,
            "se": math.hypot(sp, sm) / 2,
        }
    k1, k3, b1 = contrast["kernel 0.1"], contrast["kernel 0.3"], contrast["bright 0.1"]
    model = prediction["z"]
    model_offset = (model["ro0"] + model["ro1"]) / 2
    model_scale = (model["ro0"] - model["ro1"]) / 2
    # Each modeled <Z> is sampled at PREDICTION_SHOTS; a mean over four circuits carries this error.
    model_se = 1 / math.sqrt(4 * PREDICTION_SHOTS)
    ro0, ro1 = z_of(counts, "ro0"), z_of(counts, "ro1")
    e01, e10 = (1 - ro0[0]) / 2, (1 + ro1[0]) / 2
    r = 1 - e01 - e10
    offset_se = math.hypot(ro0[1], ro1[1]) / 2
    h1 = {phi: decide(c["odd"], c["se"]) for phi, c in (("0.1", k1), ("0.3", k3))}
    # Idle relaxation is not unital and gives the bright vector an odd part of its own; H2 tests the
    # departure from the modeled one, rescaled from the modeled to the measured readout.
    bright_model = (model["b+0.1a"] + model["b+0.1b"] - model["b-0.1a"] - model["b-0.1b"]) / 4
    bright_expected = r * bright_model / model_scale
    bright_se = math.hypot(b1["se"], r * model_se / model_scale)
    h2 = {
        "expected_odd": bright_expected,
        "z": (b1["odd"] - bright_expected) / bright_se,
        "falsified": abs(b1["odd"] - bright_expected) / bright_se >= Z_RESOLVE,
    }
    # H3 as a contrast, odd(0.3) - c odd(0.1) with c = sin(0.6)/sin(0.2), defined at every reading.
    sine = math.sin(0.6) / math.sin(0.2)
    h3_se = math.hypot(k3["se"], sine * k1["se"])
    h3 = {
        "law": sine,
        "contrast": k3["odd"] - sine * k1["odd"],
        "se": h3_se,
        "z": (k3["odd"] - sine * k1["odd"]) / h3_se,
        "falsified": abs(k3["odd"] - sine * k1["odd"]) / h3_se >= Z_RESOLVE,
    }
    amplify: dict[str, Any] = {}
    for qubit in [*prediction["theta_qubits"], prediction["control"]]:
        xs = np.array([4 * k + 1 for k in AMPLIFY_K], dtype=float)
        rows = [z_of(counts, f"amp-{qubit}-{k}") for k in AMPLIFY_K]
        # Readout maps <Z>_true to r <Z> + (e10 - e01); invert it, then -sin(N pi/2 eps) ~ -N (pi/2) eps.
        ys = np.array([(z - (e10 - e01)) / r for z, _, _ in rows])
        ws = np.array([(r / se) ** 2 for _, se, _ in rows])
        slope = float(np.sum(ws * xs * ys) / np.sum(ws * xs * xs))
        slope_se = float(1 / math.sqrt(np.sum(ws * xs * xs)))
        residual = float(np.sum(ws * (ys - slope * xs) ** 2))
        amplify[qubit] = {
            "z": [z for z, _, _ in rows],
            "eps": -slope / (math.pi / 2),
            "eps_se": slope_se / (math.pi / 2),
            "chi2": residual,
            "dof": len(AMPLIFY_K) - 1,
            "linear": residual <= H5_CHI2_CUTOFF,
        }
    visibility = k1["odd"] / (-math.sin(0.2) * r)
    visibility_se = k1["se"] / (math.sin(0.2) * r)
    h4: dict[str, Any] = {"evaluated": all(amplify[q]["linear"] for q in prediction["theta_qubits"])}
    if h4["evaluated"]:
        shift = sum(prediction["response"][q]["even"] * amplify[q]["eps"] for q in prediction["theta_qubits"])
        shift_se = math.sqrt(
            sum((prediction["response"][q]["even"] * amplify[q]["eps_se"]) ** 2 for q in prediction["theta_qubits"])
        )
        model_even = (model["k+0.1a"] + model["k+0.1b"] + model["k-0.1a"] + model["k-0.1b"]) / 4
        relaxation = (model_even - model_offset) / model_scale
        predicted = (e10 - e01) + r * relaxation + r * visibility * shift
        se = math.sqrt(
            k1["se"] ** 2
            + offset_se**2
            + (r * model_se / model_scale) ** 2
            + (r * visibility * shift_se) ** 2
            + (r * shift * visibility_se) ** 2
        )
        h4.update(
            {
                "predicted_even": predicted,
                "relaxation_even": r * relaxation,
                "coherent_even": r * visibility * shift,
                "measured_even": k1["even"],
                "se": se,
                "z": (k1["even"] - predicted) / se,
                "falsified": abs(k1["even"] - predicted) / se >= Z_RESOLVE,
            }
        )
    falsified = [
        name
        for name, hit in (
            ("H1", "falsified" in h1.values()),
            ("H2", h2["falsified"]),
            ("H3", h3["falsified"]),
            ("H4", bool(h4.get("falsified"))),
        )
        if hit
    ]
    return {
        "contrasts": contrast,
        "h1_zero_divisor_sign": h1,
        "h2_bright_control": h2,
        "h3_sine_law": h3,
        "h4_coherent_even": h4,
        "h5_amplification": amplify,
        "readout": {"e01": e01, "e10": e10, "scale": r},
        "visibility": visibility,
        "visibility_se": visibility_se,
        "crossing": z_of(counts, "k0a", "k0b")[:2],
        "falsified_hypotheses": falsified,
    }


def analyze(run_dirs: list[Path]) -> dict[str, Any]:
    import iqm_jobs

    counts: dict[str, tuple[int, int]] = {}
    runs = []
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
        names = [Path(entry["file"]).stem for entry in row["circuits"]]
        for name, (ones, n) in tally(names, json.loads((run_dir / "raw/measurements.json").read_bytes())).items():
            before = counts.get(name, (0, 0))
            counts[name] = (before[0] + ones, before[1] + n)
        runs.append(
            {
                "run": run_dir.name,
                "qc": submission["qc"],
                "calibration_set": record["compilation"]["calibration_set_id"],
                "estimate_seconds": record["compilation"]["execution_runtime_estimate_seconds"],
                "runtime_seconds": record["metrics"]["runtime_seconds"],
                "billed_seconds": record["metrics"]["billed_seconds"],
                "charge": facts["charge"],
            }
        )
    prediction = json.loads((sorted(run_dirs)[0] / "prediction.json").read_text(encoding="utf-8"))
    return {
        "schema": "iqm-cancellation-probe-analysis-v1",
        "runs": runs,
        **evaluate(counts, prediction),
        "credits_charged": round(sum(r["charge"] for r in runs), 6),
    }


def synthetic(
    files: dict[str, str], eps: dict[str, float], reverse: bool, seed: int, relaxation: float
) -> dict[str, tuple[int, int]]:
    """Binomial counts of a model device: each circuit's exact <Z> under relative over-rotations eps,
    probe arms at visibility SYNTHETIC_VISIBILITY with the kernel arms shifted by the relaxation even
    part, readout errors SYNTHETIC_READOUT; reverse swaps the +phi and -phi kernel readings, the device
    whose zero-divisor sign is opposite."""
    e01, e10 = SYNTHETIC_READOUT
    z: dict[str, float] = {}
    for rel, text in files.items():
        if rel.startswith("circuits/"):
            circuit = json.loads(text)
            register = Register(circuit["instructions"])
            errors = {("over", register.index[q]): e for q, e in eps.items() if q in register.index}
            name = Path(rel).stem
            value = register.z(circuit["instructions"], errors)
            z[name] = SYNTHETIC_VISIBILITY * value if name[0] in "kb" else value
            z[name] += relaxation if name[0] == "k" else 0.0
    if reverse:
        for name in [n for n in z if n.startswith("k+")]:
            twin = "k-" + name[2:]
            z[name], z[twin] = z[twin], z[name]
    rng = np.random.default_rng(seed)
    counts = {}
    for name, value in z.items():
        p1 = (1 - ((1 - e01 - e10) * value + (e10 - e01))) / 2
        counts[name] = (int(rng.binomial(SHOTS, p1)), SHOTS)
    return counts


def self_test() -> str:
    calibration_dir = iqm_sim.EVIDENCE / QC / "calibration"
    files, prediction = build_from(calibration_dir)
    if prediction["cz"] > 60 or not prediction["theta_qubits"]:
        raise RuntimeError(f"compile {prediction['cz']} CZ, theta qubits {prediction['theta_qubits']}")
    for rel, text in files.items():
        if rel.startswith("circuits/k") or rel.startswith("circuits/b"):
            circuit = json.loads(text)
            name = Path(rel).stem
            bright = name.startswith("b")
            phi = 0.0 if name in ("k0a", "k0b", "b0") else float(name[1:].rstrip("ab"))
            ideal = Register(circuit["instructions"]).z(circuit["instructions"], {})
            if abs(ideal - kc.law(phi, bright)) > 1e-9:
                raise RuntimeError(f"{name} reads {ideal} noiselessly, not {kc.law(phi, bright)}")
    eps = {q: 0.006 for q in prediction["theta_qubits"]}
    z = prediction["z"]
    relaxation = (sum(z[n] for n in ("k+0.1a", "k+0.1b", "k-0.1a", "k-0.1b")) / 4 - (z["ro0"] + z["ro1"]) / 2) / (
        (z["ro0"] - z["ro1"]) / 2
    )
    eps[prediction["control"]] = -0.003
    honest = evaluate(synthetic(files, eps, False, 1, relaxation), prediction)
    if honest["h1_zero_divisor_sign"] != {"0.1": "resolved", "0.3": "resolved"} or honest["falsified_hypotheses"]:
        raise RuntimeError(
            f"an honest device reads {honest['h1_zero_divisor_sign']}, falsifies {honest['falsified_hypotheses']}"
        )
    for q, e in eps.items():
        got = honest["h5_amplification"][q]
        if abs(got["eps"] - e) > 4 * got["eps_se"] or not got["linear"]:
            raise RuntimeError(f"{q}: injected over-rotation {e}, recovered {got['eps']} +- {got['eps_se']}")
    if not honest["h4_coherent_even"]["evaluated"] or honest["h4_coherent_even"]["falsified"]:
        raise RuntimeError(f"the coherent even offset is mispredicted: {honest['h4_coherent_even']}")
    # An even shift the over-rotation does not carry (leakage read as 1, say) must falsify H4.
    shifted = synthetic(files, eps, False, 3, relaxation)
    for name in [n for n in shifted if n.startswith("k")]:
        ones, n = shifted[name]
        shifted[name] = (ones + int(0.025 * n), n)
    verdict = evaluate(shifted, prediction)
    if not verdict["h4_coherent_even"].get("falsified") or "H4" not in verdict["falsified_hypotheses"]:
        raise RuntimeError("an even shift outside the coherent model left H4 standing")
    # A device with no signed response (every arm reads the same) leaves H1 unresolved and H3 defined.
    flat = {name: (SHOTS // 2, SHOTS) if name[0] in "kb" else counts for name, counts in shifted.items()}
    null = evaluate(flat, prediction)
    if null["h1_zero_divisor_sign"] != {"0.1": "unresolved", "0.3": "unresolved"} or not math.isfinite(
        null["h3_sine_law"]["z"]
    ):
        raise RuntimeError(f"a null device reads {null['h1_zero_divisor_sign']}, H3 {null['h3_sine_law']}")
    reversed_ = evaluate(synthetic(files, eps, True, 2, relaxation), prediction)
    if "falsified" not in reversed_["h1_zero_divisor_sign"].values():
        raise RuntimeError(f"a reversed sign reads {reversed_['h1_zero_divisor_sign']}")
    return (
        f"cancellation probe: {prediction['cz']} CZ, control {prediction['control']}, theta qubits "
        f"{prediction['theta_qubits']}; an honest device resolves H1 and recovers the injected over-rotation, "
        "a reversed sign falsifies H1"
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
    an.add_argument("--replay", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
    elif args.command == "build":
        write(args.directory)
    elif args.command == "check":
        check(args.directory)
    elif args.command == "analyze":
        text = json.dumps(analyze(args.run_dirs), indent=1, sort_keys=True) + "\n"
        if args.replay:
            if args.out.read_text(encoding="utf-8") != text:
                raise SystemExit(f"{args.out} differs from the replayed analysis")
            print(f"{args.out}: matches the replayed analysis")
        else:
            args.out.write_text(text, encoding="utf-8")
            print(f"wrote {args.out}")
    else:
        parser.error("choose build, check, analyze or --self-test")
    return 0


if __name__ == "__main__":
    sys.exit(main())
