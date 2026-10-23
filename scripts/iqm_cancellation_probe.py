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
  carry theta and on the control: <Z> = -sin((4k + 1)(pi/2) eps) for a relative over-rotation eps,
  fitted directly rather than linearized.

On the compile, scripts/iqm_probe_audit.py's first-order response puts every coherent error except the
theta qubit's over-rotation at zero in both parts; that over-rotation scales the odd part by 1 + O(eps)
and shifts the even part by dEven/deps * eps. So the case predicts the kernel even part from the
readout calibration and the measured eps (H4), and the odd part's sign is first-order free of coherent
error. Heralding (all zeros) and one active-reset cycle follow docs/notes/iqm/README.md.

Preregistered decisions (Z_RESOLVE standard errors):
- H1 zero-divisor sign: at phi = 0.1 and 0.3 the kernel odd part resolves when odd/se <= -Z_RESOLVE and
  falsifies the cancellation law when odd/se >= +Z_RESOLVE.
- H2 bright control: the bright odd part at phi = 0.1 departs by Z_RESOLVE standard errors from the
  prediction's own bright odd part (idle relaxation is not unital), rescaled to the measured readout.
- H3 sine law: the contrast odd(0.3) - (sin(0.6)/sin(0.2)) odd(0.1) lies Z_RESOLVE standard errors
  from zero.
- H4 even-part decomposition: the kernel even part at phi = 0.1 departs from
  (e10 - e01) + r R + r G eps by Z_RESOLVE standard errors: readout offset and scale r = 1 - e01 - e10
  from the control's readout calibration, R the prediction's incoherent even part net of its modeled
  readout (idle relaxation, which is not unital), G the noise model's derivative of the even part in the
  theta qubit's relative over-rotation (prediction.json response noisy_even), eps from its trains.
- H5 amplification: each train qubit's <Z> follows -sin((4k + 1)(pi/2) eps) through its own readout
  (the server plays each pulse); a profiled chi-square above the one-sided Z_RESOLVE tail of three
  degrees of freedom marks pulse merging or a non-stationary error, and H4 is then not evaluated.

Usage: "$PYTHON" scripts/iqm_cancellation_probe.py (build DIR [--live] | check DIR | analyze RUN_DIR...
       --out FILE [--replay] | --self-test)
build --live reads Garnet's current default calibration set (IQM_TOKENS_FILE, read-only) into DIR/calibration;
check rebuilds offline from that copy.
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
from iqm_jobs import CASE_SCHEMA, ceiling_credits, dump, write_atomic  # noqa: E402
from iqm_platform import sha256  # noqa: E402
from iqm_probe_audit import Register  # noqa: E402
from iqm_signed_probe import (  # noqa: E402
    relaxed,  # noqa: E402
    target_of,
    to_iqm,
)

import kernel_cancellation as kc  # noqa: E402
from parallel import ordered_map  # noqa: E402

CASE = "kernel-cancellation-probe"
QC = "garnet"
QCS = ["garnet:mock", "garnet"]
SEEDS = range(24)
SHOTS = 4000
# Garnet's price per second; the build records each QC's ceiling in cases.json, which submit enforces
# through the same iqm_jobs.ceiling_credits.
PRICE = {"garnet": 0.5, "garnet:mock": 0.0}
# The two heralded Garnet probe jobs (40000 and 200000 requested shots, runtimes 1.59 s and 6.52 s)
# differ by 31 us per requested shot; the shorter circuits here run faster, so this bounds the schedule.
SHOT_SECONDS = 0.000031
OPTIONS: dict[str, Any] = {"heralding_mode": "zeros", "active_reset_cycles": 1}
CALIBRATION_FILES = ("metrics.json", "dynamic-quantum-architecture.json")
# Step of the noisy-model central difference in a relative over-rotation.
NOISY_STEP = 0.01
# Train lengths 4k + 1 = 1, 5, 9, 13 keep the accumulated rotation under 0.7 rad up to a 3 % over-rotation,
# the size the signed probe's even offsets put on QB11.
AMPLIFY_K = (0, 1, 2, 3)
# The fit searches |eps| <= EPS_RANGE, where the 13-pulse train turns through at most 13 (pi/2) 0.06 =
# 1.23 rad < pi/2, so -sin(N pi/2 eps) is monotonic in eps for every train and no alias enters; a minimum
# at the edge of the range marks the train as outside the model.
EPS_RANGE = 0.06
# Distinct prx angles below this differ only by float rounding of one compile.
ANGLE_TOLERANCE = 1e-9
STEP = 1e-4
Z_RESOLVE = 3.0


def chi2_survival_3(x: float) -> float:
    """Upper tail of the chi-square law with three degrees of freedom."""
    return math.erfc(math.sqrt(x / 2)) + math.sqrt(2 * x / math.pi) * math.exp(-x / 2)


def chi2_cutoff_3(tail: float) -> float:
    low, high = 0.0, 100.0
    for _ in range(200):
        middle = (low + high) / 2
        low, high = (middle, high) if chi2_survival_3(middle) > tail else (low, middle)
    return (low + high) / 2


# H5 marks a train inconsistent with -sin(N pi/2 eps) above the chi-square quantile whose upper tail
# equals the one-sided Z_RESOLVE normal tail; four train lengths and one fitted eps leave three degrees
# of freedom.
H5_CHI2_CUTOFF = chi2_cutoff_3(0.5 * math.erfc(Z_RESOLVE / math.sqrt(2)))
# (e01, e10) of the model device: the control and every other qubit differ, as Garnet's do.
SYNTHETIC_READOUT = {"control": (0.01, 0.03), "other": (0.05, 0.12)}
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


def compile_seed(item: tuple[int, str]) -> tuple[int, int, Any]:
    """One transpiler seed's compile onto the calibration's couplers: (seed, cz, compile)."""
    seed, calibration_dir = item
    _, coupling = target_of(iqm_sim.Calibration.from_directory(Path(calibration_dir)))
    compiled = transpile(
        kc.cancellation_probe(),
        basis_gates=["r", "cz"],
        coupling_map=coupling,
        optimization_level=3,
        seed_transpiler=seed,
    )
    return seed, compiled.count_ops().get("cz", 0), compiled


def compile_probe(calibration_dir: Path) -> tuple[int, Any, list[dict[str, Any]]]:
    """The seed with the fewest CZ (lowest seed on a tie); kernel and bright bind the same compile."""
    best = None
    seeds = []
    # ordered_map returns the seeds in order, so the lowest seed wins a tie as in a serial loop.
    for seed, cz, compiled in ordered_map(compile_seed, [(seed, str(calibration_dir)) for seed in SEEDS]):
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
    # Only an angle that moves with theta tilts the selector; a phase that moves is a frame change.
    moved = {
        x["locus"][0]
        for x, y in zip(a, b, strict=True)
        if x["name"] == "prx" and abs(x["args"]["angle"] - y["args"]["angle"]) > ANGLE_TOLERANCE
    }
    return sorted(moved, key=lambda q: int(q[2:]))


def response(arms: dict[float, dict[str, Any]], qubit: str, calibration_dir: Path) -> dict[str, float]:
    """Odd and even response at phi = 0.1 to a relative over-rotation of qubit's prx pulses, noiseless and
    through the calibration noise model before readout (central differences at STEP and NOISY_STEP)."""
    register = Register(arms[0.1]["instructions"])
    error = ("over", register.index[qubit])
    ideal = {
        phi: (register.z(c["instructions"], {error: STEP}) - register.z(c["instructions"], {error: -STEP})) / (2 * STEP)
        for phi, c in arms.items()
    }
    items = [(c, str(calibration_dir), {qubit: sign * NOISY_STEP}) for c in arms.values() for sign in (1, -1)]
    values = ordered_map(exact_z, items)
    noisy = {phi: (values[2 * n] - values[2 * n + 1]) / (2 * NOISY_STEP) for n, phi in enumerate(arms)}
    return {
        "odd": (ideal[0.1] - ideal[-0.1]) / 2,
        "even": (ideal[0.1] + ideal[-0.1]) / 2,
        "noisy_odd": (noisy[0.1] - noisy[-0.1]) / 2,
        "noisy_even": (noisy[0.1] + noisy[-0.1]) / 2,
    }


def exact_z(item: tuple[dict[str, Any], str, dict[str, float]]) -> float:
    """Exact <Z> of the measured qubit before readout, under the calibration's gate noise and ALAP idle
    relaxation, with prx angles on the named qubits scaled by 1 + eps after scheduling.

    Density-matrix probabilities replace sampling, so equal circuits give equal values and the
    prediction carries no sampling error.
    """
    circuit, calibration_dir, over = item
    calibration = iqm_sim.Calibration.from_directory(Path(calibration_dir))
    target, _ = target_of(calibration)
    qiskit_circuit, _ = iqm_sim.to_qiskit(circuit, calibration)
    scheduled = relaxed(
        calibration, transpile(qiskit_circuit, target=target, optimization_level=0, scheduling_method="alap")
    )
    out = QuantumCircuit(*scheduled.qregs, *scheduled.cregs)
    measured = None
    for instruction in scheduled.data:
        op, qubits = instruction.operation, [scheduled.find_bit(q).index for q in instruction.qubits]
        if op.name == "measure":
            measured = qubits[0]
            continue
        if op.name == "r" and calibration.qubits[qubits[0]] in over:
            angle, phase = (float(x) for x in op.params)
            op = RGate(angle * (1 + over[calibration.qubits[qubits[0]]]), phase)
        out.append(op, [out.qubits[q] for q in qubits])
    if measured is None:
        raise ValueError(f"{circuit['name']} measures no qubit")
    out.save_probabilities([measured])
    simulator = AerSimulator(method="density_matrix", noise_model=calibration.noise_model(heralded=True))
    p = simulator.run(out).result().data()["probabilities"]
    return float(p[0] - p[1])


def read(z: float, e01: float, e10: float) -> float:
    """<Z> as read through readout errors (P(1|0), P(0|1))."""
    return (1 - e01 - e10) * z + (e10 - e01)


def measured_qubit(circuit: dict[str, Any]) -> str:
    return next(op["locus"][0] for op in circuit["instructions"] if op["name"] == "measure")


def build_from(calibration_dir: Path) -> tuple[dict[str, str], dict[str, Any]]:
    calibration = iqm_sim.Calibration.from_directory(calibration_dir)
    seed, compiled, seeds = compile_probe(calibration_dir)
    tilted = theta_qubits(compiled, calibration)
    circuits: list[tuple[str, dict[str, Any]]] = []
    for name, bright, phi in PROBE_ARMS:
        circuits.append((name, bind(compiled, phi, calibration, name, bright)))
    control = next(op["locus"][0] for op in circuits[0][1]["instructions"] if op["name"] == "measure")
    if any(next(op["locus"][0] for op in c["instructions"] if op["name"] == "measure") != control for _, c in circuits):
        raise ValueError("the kernel and bright compiles measure different qubits")
    # Every measured qubit gets its own readout calibration: the trains read the theta qubits, whose
    # readout errors differ from the control's.
    for qubit in [control, *tilted]:
        circuits.append((f"ro0-{qubit}", {"name": f"ro0-{qubit}", "instructions": [measure(qubit)]}))
        circuits.append(
            (f"ro1-{qubit}", {"name": f"ro1-{qubit}", "instructions": [prx(qubit, math.pi), measure(qubit)]})
        )
    for qubit in [*tilted, control]:
        for k in AMPLIFY_K:
            name = f"amp-{qubit}-{k}"
            circuits.append((name, {"name": name, "instructions": train(qubit, k)}))
    files: dict[str, str] = {}
    for name, circuit in circuits:
        files[f"circuits/{name}.json"] = dump(circuit)
    kernel_arms = {phi: bind(compiled, phi, calibration, "r") for phi in (0.1, -0.1)}
    expected = round(len(circuits) * SHOTS * SHOT_SECONDS, 3)
    ceiling = {qc: ceiling_credits(expected, price) for qc, price in PRICE.items()}
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
        "z": dict(
            zip(
                [name for name, _ in circuits],
                [
                    read(z, *calibration.readout(measured_qubit(circuit), heralded=True))
                    for z, (_, circuit) in zip(
                        ordered_map(exact_z, [(circuit, str(calibration_dir), {}) for _, circuit in circuits]),
                        circuits,
                        strict=True,
                    )
                ],
                strict=True,
            )
        ),
        "response": {q: response(kernel_arms, q, calibration_dir) for q in tilted},
        "model": (
            "iqm_sim depolarizing PRX and CZ with herald-conditioned readout, ALAP idle T1/T2, exact density matrix"
        ),
    }
    files["prediction.json"] = dump(prediction)
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
            # The approval digest of cases.json covers the prediction the analysis decides against.
            "prediction_sha256": sha256(files["prediction.json"].encode()),
        }
    )
    return files, prediction


def fetch_calibration(calibration_dir: Path) -> None:
    """Garnet's current default calibration set: its architecture and metrics, read by the set's id."""
    from iqm_platform import Client, calibration_paths, default_calibration_path, read_tokens, tokens_path

    client = Client(read_tokens(tokens_path())["access_token"])
    status, body = client.get(default_calibration_path(QC))
    if status != 200:
        raise ValueError(f"GET the default calibration set answered {status}")
    identity = json.loads(body)["observation_set_id"]
    fetched = {}
    for name, path in calibration_paths(QC, identity).items():
        status, data = client.get(path)
        if status != 200:
            raise ValueError(f"GET {path} answered {status}")
        fetched[name] = data
    architecture = json.loads(fetched["dynamic-quantum-architecture.json"])
    metrics = json.loads(fetched["metrics.json"])
    if architecture["calibration_set_id"] != identity or metrics.get("describes_id") != identity:
        raise ValueError(f"the fetched architecture and metrics do not both describe set {identity}")
    # Both files land only after both reads succeed and agree, each through one rename;
    # iqm_sim.Calibration.load refuses a directory whose two files describe different sets.
    for name, data in fetched.items():
        write_atomic(calibration_dir / name, data)


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
    # A rebuild drops the circuits an earlier build wrote and this one does not, so check() holds.
    for stale in (directory / "circuits").glob("*.json") if (directory / "circuits").exists() else []:
        if stale.relative_to(directory).as_posix() not in files:
            stale.unlink()
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


def z_one(counts: dict[str, tuple[int, int]], name: str) -> tuple[float, float, int]:
    """<Z> of one circuit, its standard error and its kept shots."""
    ones, n = counts[name]
    if n == 0:
        return 0.0, math.inf, 0
    z = 1 - 2 * ones / n
    return z, math.sqrt(max(1 - z * z, 1.0 / n) / n), n


def z_of(counts: dict[str, tuple[int, int]], *names: str) -> tuple[float, float, int]:
    """Equal-weight mean <Z> of the named circuits, its standard error and their kept shots.

    The copies of an arm sit at time-symmetric positions (+, -, -, +), and a linear drift cancels only if
    each copy carries the same weight; heralding keeps different shot counts per circuit, so a pooled count
    would weight them unequally. A circuit whose shots heralding removed contributes nothing.
    """
    rows = [z_one(counts, name) for name in names]
    kept = [row for row in rows if row[2] > 0]
    if not kept:
        return 0.0, math.inf, 0
    z = sum(row[0] for row in kept) / len(kept)
    se = math.sqrt(sum(row[1] ** 2 for row in kept)) / len(kept)
    return z, se, sum(row[2] for row in kept)


def decide(value: float, se: float) -> str:
    return "resolved" if value / se <= -Z_RESOLVE else "falsified" if value / se >= Z_RESOLVE else "unresolved"


def fit_train(
    lengths: list[int],
    rows: list[tuple[float, float, int]],
    ro0: tuple[float, float, int],
    ro1: tuple[float, float, int],
) -> tuple[float, float, float, float, float]:
    """Joint fit of a qubit's trains and its two readout-calibration circuits: (eps, se, chi2, e01, e10).

    A train of N pulses reads (1 - e01 - e10)(-sin(N pi/2 eps)) + (e10 - e01); the bare measure reads
    1 - 2 e01, and the calibration pi pulse, which carries the same over-rotation, reads
    (1 - e01 - e10)(-cos(pi eps)) + (e10 - e01). For each eps the readout errors enter linearly, so a weighted
    least squares profiles them out and the readout calibration's finite shots reach eps and chi2. Six
    readings and three parameters leave three degrees of freedom. A grid over |eps| <= EPS_RANGE brackets
    the minimum of the profiled chi-square, a golden-section search refines it, and se = sqrt(2 / chi2'').
    A minimum on the range's edge or a non-positive curvature means the trains lie outside the model; the
    fit then returns an infinite chi-square, which H5 rejects.
    """

    def solve(eps: float) -> tuple[float, Any]:
        design, target, weight = [], [], []
        for n, (z, se, _) in zip(lengths, rows, strict=True):
            s = math.sin(n * math.pi / 2 * eps)
            design.append((s - 1, s + 1))
            target.append(z + s)
            weight.append(1 / se**2)
        c = math.cos(math.pi * eps)
        design += [(-2.0, 0.0), (c - 1, c + 1)]
        target += [ro0[0] - 1, ro1[0] + c]
        weight += [1 / ro0[1] ** 2, 1 / ro1[1] ** 2]
        a = np.array(design)
        y = np.array(target)
        w = np.array(weight)
        errors = np.linalg.solve(a.T @ (w[:, None] * a), a.T @ (w * y))
        return float(np.sum(w * (y - a @ errors) ** 2)), errors

    def chi2(eps: float) -> float:
        return solve(eps)[0]

    grid = [EPS_RANGE * (i / 1500 - 1) for i in range(3001)]
    best = min(range(len(grid)), key=lambda i: chi2(grid[i]))
    if best in (0, len(grid) - 1):
        errors = solve(grid[best])[1]
        return grid[best], math.inf, math.inf, float(errors[0]), float(errors[1])
    low, high = grid[max(best - 1, 0)], grid[min(best + 1, len(grid) - 1)]
    ratio = (math.sqrt(5) - 1) / 2
    for _ in range(100):
        a_, b_ = high - ratio * (high - low), low + ratio * (high - low)
        low, high = (low, b_) if chi2(a_) < chi2(b_) else (a_, high)
    eps = (low + high) / 2
    step = 1e-4
    curvature = (chi2(eps + step) - 2 * chi2(eps) + chi2(eps - step)) / step**2
    errors = solve(eps)[1]
    if not curvature > 0:
        return eps, math.inf, math.inf, float(errors[0]), float(errors[1])
    return eps, math.sqrt(2 / curvature), chi2(eps), float(errors[0]), float(errors[1])


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
    control = prediction["control"]
    model_offset = (model[f"ro0-{control}"] + model[f"ro1-{control}"]) / 2
    model_scale = (model[f"ro0-{control}"] - model[f"ro1-{control}"]) / 2
    amplify: dict[str, Any] = {}
    for qubit in [*prediction["theta_qubits"], control]:
        rows = [z_of(counts, f"amp-{qubit}-{k}") for k in AMPLIFY_K]
        eps, eps_se, residual, fit_e01, fit_e10 = fit_train(
            [4 * k + 1 for k in AMPLIFY_K], rows, z_of(counts, f"ro0-{qubit}"), z_of(counts, f"ro1-{qubit}")
        )
        amplify[qubit] = {
            "z": [z for z, _, _ in rows],
            "eps": eps,
            "eps_se": eps_se,
            "chi2": residual,
            "dof": len(AMPLIFY_K) - 1,
            "linear": residual <= H5_CHI2_CUTOFF,
            "e01": fit_e01,
            "e10": fit_e10,
        }
    # Each qubit's readout errors come from its joint fit, which models the calibration pi pulse's own
    # over-rotation; the offset error is that of the two calibration circuits.
    readout = {}
    for qubit in [control, *prediction["theta_qubits"]]:
        ro0, ro1 = z_of(counts, f"ro0-{qubit}"), z_of(counts, f"ro1-{qubit}")
        readout[qubit] = {
            "e01": amplify[qubit]["e01"],
            "e10": amplify[qubit]["e10"],
            "offset_se": math.hypot(ro0[1], ro1[1]) / 2,
        }
    e01, e10 = readout[control]["e01"], readout[control]["e10"]
    r = 1 - e01 - e10
    offset_se = readout[control]["offset_se"]
    h1 = {phi: decide(c["odd"], c["se"]) for phi, c in (("0.1", k1), ("0.3", k3))}
    # Idle relaxation is not unital and gives the bright vector an odd part of its own; H2 tests the
    # departure from the modeled one, rescaled from the modeled to the measured readout.
    bright_model = (model["b+0.1a"] + model["b+0.1b"] - model["b-0.1a"] - model["b-0.1b"]) / 4
    bright_expected = r * bright_model / model_scale
    bright_se = b1["se"]
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
    visibility = k1["odd"] / (-math.sin(0.2) * r)
    visibility_se = k1["se"] / (math.sin(0.2) * r)
    # A failed train, the control's included, marks a run whose pulse execution or stationarity H4 rests on.
    h4: dict[str, Any] = {"evaluated": all(entry["linear"] for entry in amplify.values())}
    if h4["evaluated"]:
        # The noisy-model derivative of the read even part, rescaled from the modeled to the measured readout.
        response_even = {q: prediction["response"][q]["noisy_even"] for q in prediction["theta_qubits"]}
        shift = sum(response_even[q] * amplify[q]["eps"] for q in prediction["theta_qubits"])
        shift_se = math.sqrt(sum((response_even[q] * amplify[q]["eps_se"]) ** 2 for q in prediction["theta_qubits"]))
        model_even = (model["k+0.1a"] + model["k+0.1b"] + model["k-0.1a"] + model["k-0.1b"]) / 4
        relaxation_even = (model_even - model_offset) / model_scale
        predicted = (e10 - e01) + r * relaxation_even + r * shift
        se = math.sqrt(k1["se"] ** 2 + offset_se**2 + (r * shift_se) ** 2)
        h4.update(
            {
                "predicted_even": predicted,
                "relaxation_even": r * relaxation_even,
                "coherent_even": r * shift,
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
            ("H5", not all(entry["linear"] for entry in amplify.values())),
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
        "readout": {q: {"e01": v["e01"], "e10": v["e10"]} for q, v in readout.items()},
        "visibility": visibility,
        "visibility_se": visibility_se,
        "crossing": z_of(counts, "k0a", "k0b")[:2],
        "falsified_hypotheses": falsified,
    }


def analyze(run_dirs: list[Path]) -> dict[str, Any]:
    import iqm_jobs

    # The case is one job, and its drift cancellation is formed inside it; a second acquisition would pool
    # two runs' baselines into one contrast, so the analysis reads exactly one run.
    if len(run_dirs) != 1:
        raise ValueError(f"the case is one job; the analysis reads one run, not {len(run_dirs)}")
    counts: dict[str, tuple[int, int]] = {}
    runs = []
    prediction = json.loads((sorted(run_dirs)[0] / "prediction.json").read_text(encoding="utf-8"))
    digests = {sha256((run_dir / "cases.json").read_bytes()) for run_dir in run_dirs}
    if len(digests) != 1:
        raise ValueError(f"the runs copy {len(digests)} different cases.json; one analysis reads one case")
    bound = json.loads((sorted(run_dirs)[0] / "cases.json").read_text(encoding="utf-8")).get("prediction_sha256")
    for run_dir in run_dirs:
        if sha256((run_dir / "prediction.json").read_bytes()) != bound:
            raise ValueError(f"{run_dir}/prediction.json is not the prediction cases.json binds")
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
        if facts["statuses"] != {"completed": 1}:
            raise ValueError(f"{run_dir}: the job is {sorted(facts['statuses'])}; the analysis reads completed jobs")
        # Mock outcomes never enter the analysis, and every run must compile against the predicted set.
        if submission["qc"] != QC:
            raise ValueError(f"{run_dir}: ran on {submission['qc']}; the analysis reads {QC} runs only")
        compiled_set = record["compilation"]["calibration_set_id"]
        if compiled_set != prediction["calibration_set"]:
            raise ValueError(
                f"{run_dir}: compiled against {compiled_set}, not the predicted {prediction['calibration_set']}"
            )
        rows = [r for r in case["jobs"] if r["job"] == submission["job"]]
        if case.get("case") != CASE or len(rows) != 1:
            raise ValueError(f"{run_dir}: holds no {CASE} job named {submission['job']}")
        row = rows[0]
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
    return {
        "schema": "iqm-cancellation-probe-analysis-v1",
        "runs": runs,
        **evaluate(counts, prediction),
        "credits_charged": round(sum(r["charge"] for r in runs), 6),
    }


def synthetic(files: dict[str, str], eps: dict[str, float], control: str, calibration_dir: Path) -> dict[str, float]:
    """True <Z> of every circuit of a model device: the calibration noise model with relative
    over-rotations eps (exact density matrix), before readout."""
    circuits = {Path(rel).stem: json.loads(text) for rel, text in files.items() if rel.startswith("circuits/")}
    values = ordered_map(exact_z, [(circuit, str(calibration_dir), eps) for circuit in circuits.values()])
    return dict(zip(circuits, values, strict=True))


def sample(
    z: dict[str, float], files: dict[str, str], control: str, reverse: bool, seed: int
) -> dict[str, tuple[int, int]]:
    """Kept-shot counts drawn from true readings z through SYNTHETIC_READOUT (the control's errors and
    another qubit's); reverse swaps the +phi and -phi kernel readings, the device whose zero-divisor
    sign is opposite."""
    z = dict(z)
    if reverse:
        for name in [n for n in z if n.startswith("k+")]:
            twin = "k-" + name[2:]
            z[name], z[twin] = z[twin], z[name]
    measured = {
        Path(rel).stem: measured_qubit(json.loads(text)) for rel, text in files.items() if rel.startswith("circuits/")
    }
    rng = np.random.default_rng(seed)
    counts = {}
    for name, value in z.items():
        e01, e10 = SYNTHETIC_READOUT["control" if measured[name] == control else "other"]
        counts[name] = (int(rng.binomial(SHOTS, (1 - read(value, e01, e10)) / 2)), SHOTS)
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
    case = json.loads(files["cases.json"])
    if case["prediction_sha256"] != sha256(files["prediction.json"].encode()):
        raise RuntimeError("cases.json does not bind the prediction it was built with")
    control = prediction["control"]
    eps = {q: 0.027 for q in prediction["theta_qubits"]}
    eps[control] = -0.003
    # The model device: the prediction's own noise model, the injected over-rotations, a readout per qubit.
    # Its readout differs from the prediction's, so the analysis must use the measured calibration.
    z = synthetic(files, eps, control, calibration_dir)
    honest = evaluate(sample(z, files, control, False, 1), prediction)
    if honest["h1_zero_divisor_sign"] != {"0.1": "resolved", "0.3": "resolved"} or honest["falsified_hypotheses"]:
        raise RuntimeError(
            f"an honest device reads {honest['h1_zero_divisor_sign']}, falsifies {honest['falsified_hypotheses']}"
        )
    for q, e in eps.items():
        got = honest["h5_amplification"][q]
        if abs(got["eps"] - e) > 4 * got["eps_se"] + 0.002 or not got["linear"]:
            raise RuntimeError(f"{q}: injected over-rotation {e}, recovered {got['eps']} +- {got['eps_se']}")
    if not honest["h4_coherent_even"]["evaluated"] or honest["h4_coherent_even"]["falsified"]:
        raise RuntimeError(f"the coherent even offset is mispredicted: {honest['h4_coherent_even']}")
    # An even shift the over-rotation does not carry (leakage read as 1, say) must falsify H4.
    shifted = sample(z, files, control, False, 3)
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
    # Merged pulses read every train like the longest one: H5 fails, enters the verdict and suspends H4.
    merged = dict(shifted)
    for q in prediction["theta_qubits"]:
        for k in AMPLIFY_K:
            merged[f"amp-{q}-{k}"] = shifted[f"amp-{q}-{AMPLIFY_K[-1]}"]
    merged_verdict = evaluate(merged, prediction)
    if merged_verdict["h4_coherent_even"]["evaluated"] or "H5" not in merged_verdict["falsified_hypotheses"]:
        raise RuntimeError("trains that ignore their pulse count left H5 standing or H4 evaluated")
    # A failed train on the control alone also suspends H4.
    control_merged = dict(shifted)
    for k in AMPLIFY_K:
        control_merged[f"amp-{control}-{k}"] = shifted[f"amp-{control}-{AMPLIFY_K[-1]}"]
    if evaluate(control_merged, prediction)["h4_coherent_even"]["evaluated"]:
        raise RuntimeError("a failed control train left H4 evaluated")
    reversed_ = evaluate(sample(z, files, control, True, 2), prediction)
    if "falsified" not in reversed_["h1_zero_divisor_sign"].values():
        raise RuntimeError(f"a reversed sign reads {reversed_['h1_zero_divisor_sign']}")
    return (
        f"cancellation probe: {prediction['cz']} CZ, control {control}, theta qubits "
        f"{prediction['theta_qubits']}; the exact model device resolves H1 and recovers the injected over-rotation, "
        "a reversed sign falsifies H1, merged trains falsify H5"
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
    an.add_argument("run_dirs", type=Path, nargs="+")
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
