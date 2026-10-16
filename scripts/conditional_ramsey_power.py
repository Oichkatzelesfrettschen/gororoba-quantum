"""Injection-recovery power of the conditional Ramsey design under a retained calibration.

The held conditional Ramsey case (gororoba_quantum/conditional_ramsey.py,
docs/notes/conditional_ramsey_hamiltonian.md) quotes delta-method standard
errors computed from noisy laws with every rate at zero, because live_run's
noise model carries no detuning and no Z Z term. This script asks whether
those errors hold once the rates the case is meant to find are present:

- For each pair and scenario it compiles every arm to the snapshot Target
  (calibration_snapshot.build_target) on the named physical qubits, inserts
  the reduced Hamiltonian exp(-i H t) of the scenario as a noise-free
  diagonal unitary right after each idle, and computes the exact noisy law of
  each circuit: Aer density matrix with the snapshot's gate, idle and
  measurement relaxation noise, then the snapshot's per-qubit assignment
  channel. The Hamiltonian is diagonal and the relaxation channels are phase
  covariant, so placing exp(-i H t) after the idle equals evolving under it
  during the idle.
- It reports the noise-free recovery of every parameter from the exact laws
  (the systematic error the noise leaves), the delta-method standard error at
  ``--shots`` (conditional_ramsey.one_shot_standard_errors on the same laws),
  and the Monte Carlo spread, 95 percent interval coverage of the injected
  value, unwrap slips and falsifier rejection rate over ``--trials``
  multinomial resamples of the whole job.

Scenario rates are in Hz; omega is each qubit's frame detuning, J the Z Z
rate of H / hbar = (omega_A Z_A + omega_B Z_B + J Z_A Z_B) / 2 and stark a
detuning added to A on the conditional arms only, which the falsifier must
see as residual -2 stark.

The entry reads GOROROBA_AER_DEVICE (CPU by default). ``--check FILE``
reruns a reduced case of FILE on the CPU: its first pair and the scenarios
``--scenarios`` names, at ``--trials`` resamples. Exact-law quantities must
match FILE to 1e-8 relative, and each spread-to-SE ratio within five standard
errors of the difference of two independent spread estimates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import numpy as np  # noqa: E402
import qiskit  # noqa: E402
import qiskit_aer  # noqa: E402
from qiskit import QuantumCircuit, transpile  # noqa: E402
from qiskit.circuit.library import UnitaryGate  # noqa: E402

import calibration_snapshot  # noqa: E402
import conditional_ramsey as cr  # noqa: E402

SNAPSHOT = ROOT / "docs/evidence/calibration/ibm_kingston.json"
# (A, B) physical qubits of the two held records; the coherence window's work
# qubits are 68 and 66 with 67 between them.
PAIRS = ((68, 67), (67, 66))
# The window's -1.130 rad over 4.392 us is a 40.9 kHz rate, or 40.9 kHz plus
# whole turns of 227.7 kHz.
WINDOW_HZ = 40.9e3
WINDOW_TURN_HZ = 1.0 / 4.392e-6
SCENARIOS: dict[str, dict[str, float]] = {
    "zero": {"omega_a": 0.0, "omega_b": 0.0, "zz": 0.0, "stark": 0.0},
    "window_on_a": {"omega_a": -WINDOW_HZ, "omega_b": 0.0, "zz": 0.0, "stark": 0.0},
    "split": {"omega_a": -WINDOW_HZ / 2, "omega_b": 15e3, "zz": 3e3, "stark": 0.0},
    "wound": {"omega_a": WINDOW_TURN_HZ - WINDOW_HZ, "omega_b": -10e3, "zz": 20e3, "stark": 0.0},
    "stark_300": {"omega_a": -WINDOW_HZ / 2, "omega_b": 15e3, "zz": 3e3, "stark": 300.0},
    "stark_600": {"omega_a": -WINDOW_HZ / 2, "omega_b": 15e3, "zz": 3e3, "stark": 600.0},
    "stark_1200": {"omega_a": -WINDOW_HZ / 2, "omega_b": 15e3, "zz": 3e3, "stark": 1200.0},
}
KEYS = ("omega_a_bell", "omega_a_conditional", "omega_b", "zz_j", "falsifier_residual")
RATE_KEYS = tuple(f"{sector}_rate_rad_per_dt" for sector in cr.SECTORS)
SEED_TRANSPILER = 11
SEED_SAMPLES = 20261016
Z95 = 1.959963984540054
# A sector rate further than this many standard errors from its exact-law
# value is a phase-unwrap slip, not sampling noise.
SLIP_SE = 8.0


def injected(scenario: dict[str, float]) -> dict[str, float]:
    """Expected value of each KEY in Hz under the scenario's static Hamiltonian."""
    return {
        "omega_a_bell": scenario["omega_a"],
        "omega_a_conditional": scenario["omega_a"] + scenario["stark"],
        "omega_b": scenario["omega_b"],
        "zz_j": scenario["zz"],
        "falsifier_residual": -2.0 * scenario["stark"],
    }


def marked_idle(circuit: QuantumCircuit, sector: str, delay: int) -> None:
    """The design's idle followed by a labeled barrier where the Hamiltonian goes."""
    cr.idle(circuit, sector, delay)
    circuit.barrier([0, 1], label=f"H:{sector}:{delay}")


def hamiltonian_unitary(rates: dict[str, float], sector: str, delay: int) -> UnitaryGate:
    """exp(-i H t) on (A, B) as a diagonal UnitaryGate; rates in rad per dt."""
    omega_a = rates["omega_a"] + (rates["stark"] if sector.startswith("a_given") else 0.0)
    phases = []
    for index in range(4):
        z_a = 1 - 2 * (index & 1)
        z_b = 1 - 2 * ((index >> 1) & 1)
        energy = (omega_a * z_a + rates["omega_b"] * z_b + rates["zz"] * z_a * z_b) / 2.0
        phases.append(np.exp(-1j * energy * delay))
    return UnitaryGate(np.diag(phases), label="hamiltonian")


_COMPILED: dict[tuple[str, tuple[int, int]], dict[str, QuantumCircuit]] = {}


def compiled_arms(snapshot: dict[str, Any], pair: tuple[int, int]) -> dict[str, QuantumCircuit]:
    """Every member of the design compiled to the snapshot Target with A on pair[0], B on pair[1]."""
    key = (snapshot["calibration"], pair)
    if key not in _COMPILED:
        _COMPILED[key] = _compile_arms(snapshot, pair)
    return _COMPILED[key]


def _compile_arms(snapshot: dict[str, Any], pair: tuple[int, int]) -> dict[str, QuantumCircuit]:
    view, _ = calibration_snapshot.noise_model(snapshot)
    out = {}
    for name, circuit, _ in cr.circuits(marked_idle):
        compiled = transpile(
            circuit, view, initial_layout=list(pair), optimization_level=1, seed_transpiler=SEED_TRANSPILER
        )
        final = compiled.layout.final_index_layout() if compiled.layout else [0, 1]
        if [final[0], final[1]] != list(pair):
            raise SystemExit(f"{name}: routing moved the pair to {final[:2]}")
        out[name] = compiled
    return out


def pair_snapshot(snapshot: dict[str, Any], pair: tuple[int, int]) -> dict[str, Any]:
    """The snapshot restricted to the pair, renumbered (pair[0], pair[1]) -> (0, 1).

    live_run's noise is local: each gate error and relaxation channel reads
    only its own qubits' entries, so the restriction carries the same channels
    on a two-qubit register that Aer simulates without the idle 154 qubits.
    """
    index = {q: k for k, q in enumerate(pair)}
    instructions = {
        op: [dict(row, qargs=[index[q] for q in row["qargs"]]) for row in rows if all(q in index for q in row["qargs"])]
        for op, rows in snapshot["instructions"].items()
    }
    return dict(snapshot, num_qubits=2, qubits=[snapshot["qubits"][q] for q in pair], instructions=instructions)


def law(
    simulator: Any,
    compiled: QuantumCircuit,
    pair: tuple[int, int],
    rates: dict[str, float],
    flips: dict[int, tuple[float, float]],
) -> np.ndarray:
    """Exact four-outcome law (index b << 1 | a) of one compiled arm with the Hamiltonian inserted.

    The arm is moved onto a two-qubit register (physical pair[k] -> k) and
    simulated against pair_snapshot's noise; live_run's model attaches no
    quantum error to measure, so the pre-measurement probabilities followed by
    the assignment channel are the outcome law.
    """
    index = {q: k for k, q in enumerate(pair)}
    body = QuantumCircuit(2)
    measured: list[int] = []
    for instruction in compiled.data:
        op = instruction.operation
        qubits = [compiled.find_bit(q).index for q in instruction.qubits]
        if op.name == "barrier" and (op.label or "").startswith("H:"):
            _, sector, delay = op.label.split(":")
            if qubits != list(pair):
                raise SystemExit(f"Hamiltonian marker on {qubits}, expected {list(pair)}")
            body.append(hamiltonian_unitary(rates, sector, int(delay)), [0, 1])
            continue
        if op.name == "barrier":
            continue
        if any(q not in index for q in qubits):
            raise SystemExit(f"{op.name} acts on {qubits} outside the pair {list(pair)}")
        if op.name == "measure":
            measured.append(qubits[0])
            continue
        body.append(op, [index[q] for q in qubits])
    if sorted(measured) != sorted(pair):
        raise SystemExit(f"measured {measured}, expected {list(pair)}")
    body.save_probabilities([0, 1], label="p")
    probs = np.asarray(simulator.run(body).result().data(0)["p"], dtype=float)

    def channel(q: int) -> np.ndarray:
        e10, e01 = flips[q]
        return np.array([[1.0 - e10, e01], [e10, 1.0 - e01]])

    out = np.kron(channel(pair[1]), channel(pair[0])) @ probs
    return np.clip(out, 0.0, None) / out.sum()


def exact_laws(
    snapshot: dict[str, Any], pair: tuple[int, int], scenario: dict[str, float], device: str
) -> dict[str, np.ndarray]:
    to_rad = 2.0 * math.pi * snapshot["dt"]
    rates = {key: value * to_rad for key, value in scenario.items()}
    reduced = pair_snapshot(snapshot, pair)
    simulator = calibration_snapshot.noise_simulator(reduced, device)
    _, noise = calibration_snapshot.noise_model(reduced)
    if noise._local_quantum_errors.get("measure"):
        raise SystemExit("the noise model attaches a quantum error to measure; law() would drop it")
    flips = {q: (snapshot["qubits"][q]["e10"], snapshot["qubits"][q]["e01"]) for q in pair}
    arms = compiled_arms(snapshot, pair)
    return {name: law(simulator, compiled, pair, rates, flips) for name, compiled in arms.items()}


def to_hz(value: float, dt: float) -> float:
    return cr.rate_hz(value, dt)


def evaluate(
    snapshot: dict[str, Any], pair: tuple[int, int], name: str, shots: int, trials: int, device: str
) -> dict[str, Any]:
    dt = snapshot["dt"]
    scenario = SCENARIOS[name]
    laws = exact_laws(snapshot, pair, scenario, device)
    exact = cr.summarize_distributions(laws)
    expected = injected(scenario)
    rng = np.random.default_rng([SEED_SAMPLES, pair[0], pair[1], list(SCENARIOS).index(name)])
    draws: dict[str, list[float]] = {key: [] for key in (*KEYS, *RATE_KEYS)}
    for _ in range(trials):
        sampled = {member: rng.multinomial(shots, p) / shots for member, p in laws.items()}
        values = cr.point_summary(sampled)
        for key in draws:
            draws[key].append(values[key])
    rate_se = {key: cr.standard_error(exact, key, shots) for key in RATE_KEYS}
    slipped = np.zeros(trials, dtype=bool)
    for key in RATE_KEYS:
        slipped |= np.abs(np.asarray(draws[key]) - exact[key]) > SLIP_SE * rate_se[key]
    keys: dict[str, Any] = {}
    for key in KEYS:
        values = np.asarray(draws[key])[~slipped]
        se = cr.standard_error(exact, key, shots)
        truth = expected[key] * 2.0 * math.pi * dt
        spread = float(np.std(values, ddof=1))
        keys[key] = {
            "injected_hz": expected[key],
            "exact_law_hz": to_hz(exact[key], dt),
            "systematic_hz": to_hz(exact[key] - truth, dt),
            "delta_se_hz": to_hz(se, dt),
            "monte_carlo_sd_hz": to_hz(spread, dt),
            "sd_to_se": spread / se,
            "monte_carlo_bias_hz": to_hz(float(np.mean(values)) - exact[key], dt),
            "coverage_95": float(np.mean(np.abs(values - truth) <= Z95 * se)),
        }
    unconditioned = cr.point_summary(laws, postselect=False)
    unconditioned_systematic = {key: to_hz(unconditioned[key] - expected[key] * 2.0 * math.pi * dt, dt) for key in KEYS}
    residual = np.asarray(draws["falsifier_residual"])
    residual_se = cr.standard_error(exact, "falsifier_residual", shots)
    return {
        "pair": list(pair),
        "scenario": name,
        "rates_hz": scenario,
        "trials": trials,
        "slips": int(slipped.sum()),
        "falsifier_rejection_rate": float(np.mean(np.abs(residual) > Z95 * residual_se)),
        "visibility_10000dt": {
            sector: float(exact[f"{sector}_{cr.DELAYS_DT[-1]}dt_visibility"]) for sector in cr.SECTORS
        },
        "keys": keys,
        "unconditioned_systematic_hz": unconditioned_systematic,
    }


def environment(device: str) -> dict[str, Any]:
    return {
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "qiskit": qiskit.__version__,
        "qiskit_aer": qiskit_aer.__version__,
        "device": device,
    }


def run(pairs: tuple[tuple[int, int], ...], names: list[str], shots: int, trials: int, device: str) -> dict[str, Any]:
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    started = time.time()
    results = [evaluate(snapshot, pair, name, shots, trials, device) for pair in pairs for name in names]
    return {
        "schema": "gororoba-conditional-ramsey-power-v1",
        "snapshot": str(SNAPSHOT.relative_to(ROOT)),
        "snapshot_sha256": hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest(),
        "calibration": snapshot["calibration"],
        "shots": shots,
        "trials": trials,
        "slip_threshold_se": SLIP_SE,
        "seed_samples": SEED_SAMPLES,
        "seed_transpiler": SEED_TRANSPILER,
        "environment": environment(device),
        "seconds": round(time.time() - started, 1),
        "results": results,
    }


def check(path: Path, names: list[str], trials: int) -> int:
    retained = json.loads(path.read_text(encoding="utf-8"))
    pair = tuple(retained["results"][0]["pair"])
    replay = run((pair,), names, retained["shots"], trials, "CPU")
    by_key = {(tuple(r["pair"]), r["scenario"]): r for r in retained["results"]}
    failures = []
    for result in replay["results"]:
        old = by_key[(tuple(result["pair"]), result["scenario"])]
        for key, fresh in result["keys"].items():
            kept = old["keys"][key]
            for field in ("exact_law_hz", "delta_se_hz"):
                if not math.isclose(fresh[field], kept[field], rel_tol=1e-8, abs_tol=1e-6):
                    failures.append(f"{result['scenario']} {key} {field}: {fresh[field]} against {kept[field]}")
            tolerance = 5.0 * math.sqrt(1.0 / (2 * (trials - 1)) + 1.0 / (2 * (retained["trials"] - 1)))
            if abs(fresh["sd_to_se"] - kept["sd_to_se"]) > tolerance:
                failures.append(f"{result['scenario']} {key} sd_to_se {fresh['sd_to_se']} against {kept['sd_to_se']}")
    for failure in failures:
        print(failure)
    print(
        f"conditional Ramsey power replay: pair {list(pair)}, {len(names)} scenarios, {trials} trials, "
        f"{len(failures)} departures"
    )
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--scenarios", default="all", help="comma-separated names from SCENARIOS, or all")
    parser.add_argument("--shots", type=int, default=1024)
    parser.add_argument("--trials", type=int, default=4000)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    names = list(SCENARIOS) if args.scenarios == "all" else args.scenarios.split(",")
    unknown = sorted(set(names) - set(SCENARIOS))
    if unknown:
        parser.error(f"unknown scenarios {unknown}")
    if args.check:
        return check(args.check, names, args.trials)
    if args.out is None:
        parser.error("--out is required without --check")
    result = run(PAIRS, names, args.shots, args.trials, os.environ.get("GOROROBA_AER_DEVICE", "CPU"))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.out}: {len(result['results'])} pair-scenarios in {result['seconds']} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
