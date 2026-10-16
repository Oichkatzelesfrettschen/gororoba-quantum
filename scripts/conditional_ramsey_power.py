"""Injection-recovery power of the conditional Ramsey design under a retained calibration.

The held conditional Ramsey case (gororoba_quantum/conditional_ramsey.py,
docs/notes/conditional_ramsey_hamiltonian.md) quotes delta-method standard
errors computed from noisy laws with every rate at zero, because live_run's
noise model carries no detuning and no Z Z term. This script asks whether
those errors, and the intervals a collected run reports, hold once the rates
the case is meant to find are present.

Laws. Each arm is compiled to the snapshot Target on the pair's physical
qubits with every idle cut into slices of at most SLICE_DT, and each slice is
followed by its share of the reduced Hamiltonian exp(-i H dt_k) as a
noise-free diagonal unitary. Amplitude damping on B does not commute with
Z_A Z_B, so a slice bounds the error of placing the Hamiltonian after its
relaxation; ``slice_convergence`` records the unconditioned estimator's J
bias at longer slices. snapshot_laws.outcome_law gives the exact noisy law
of every arm (gate, idle and assignment noise of live_run's model).

Statistics, over ``--trials`` multinomial resamples of the whole job at
``--shots`` per circuit, drawn in BLOCKS seeded blocks through
parallel.ordered_map:

- systematic error: the exact-law estimate against the injected value;
- the delta-method standard error of the exact law (the figure a case
  quotes) against the Monte Carlo spread;
- 95 percent coverage of the injected value with that standard error, and
  with each trial's own plug-in error from
  conditional_ramsey.summarize_distributions, which is what a collected run
  reports (computed on ``--plugin-trials`` of the resamples);
- unwrap slips and falsifier rejection, the latter with both errors.

Scenario rates are in Hz; omega is each qubit's frame detuning, J the Z Z
rate of H / hbar = (omega_A Z_A + omega_B Z_B + J Z_A Z_B) / 2 and stark a
detuning added to A on the conditional arms only, which the falsifier must
see as residual -2 stark.

The entry reads GOROROBA_AER_DEVICE (CPU by default). ``--check FILE --run
DIR`` requires FILE to be byte-identical to the result collected in the
Kaggle run DIR (its collect.json ledger), then reruns a reduced case on the
CPU: the first pair and the ``--scenarios`` named, at ``--trials``
resamples. Exact-law estimates and delta-method errors must match FILE to
1e-8 relative, and each spread-to-error ratio must agree within five
standard errors of the difference of two independent spread estimates.
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
from qiskit.circuit import Instruction  # noqa: E402
from qiskit.circuit.library import UnitaryGate  # noqa: E402

import calibration_snapshot  # noqa: E402
import conditional_ramsey as cr  # noqa: E402
import parallel  # noqa: E402
import snapshot_laws  # noqa: E402

SNAPSHOT = ROOT / "docs/evidence/calibration/ibm_kingston.json"
OUTPUT = "results/kaggle_out/conditional_ramsey_power.json"
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
# Longest idle slice in dt (0.5 us); slice_convergence records how far the
# unconditioned J bias moves at longer slices and with the idle unsliced.
SLICE_DT = 125
CONVERGENCE_SLICES = (10000, 500, 250)
CONVERGENCE_CASE = ((67, 66), "split")
BLOCKS = 16


def injected(scenario: dict[str, float]) -> dict[str, float]:
    """Expected value of each KEY in Hz under the scenario's static Hamiltonian."""
    return {
        "omega_a_bell": scenario["omega_a"],
        "omega_a_conditional": scenario["omega_a"] + scenario["stark"],
        "omega_b": scenario["omega_b"],
        "zz_j": scenario["zz"],
        "falsifier_residual": -2.0 * scenario["stark"],
    }


def sliced_idle(slice_dt: int) -> cr.Evolution:
    """The design's idle cut into slices of at most slice_dt, each followed by a labeled barrier."""

    def evolve(circuit: QuantumCircuit, sector: str, delay: int) -> None:
        if not delay:
            return
        count = math.ceil(delay / slice_dt)
        base, extra = divmod(delay, count)
        for index in range(count):
            length = base + (1 if index < extra else 0)
            circuit.delay(length, [0, 1], unit="dt")
            circuit.barrier([0, 1], label=f"H:{sector}:{length}")

    return evolve


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


_COMPILED: dict[tuple[str, tuple[int, int], int], dict[str, QuantumCircuit]] = {}


def compiled_arms(snapshot: dict[str, Any], pair: tuple[int, int], slice_dt: int) -> dict[str, QuantumCircuit]:
    """Every member of the design compiled to the snapshot Target with A on pair[0], B on pair[1]."""
    key = (snapshot["calibration"], pair, slice_dt)
    if key not in _COMPILED:
        view, _ = calibration_snapshot.noise_model(snapshot)
        arms = {}
        for name, circuit, _ in cr.circuits(sliced_idle(slice_dt)):
            compiled = transpile(
                circuit, view, initial_layout=list(pair), optimization_level=1, seed_transpiler=SEED_TRANSPILER
            )
            final = compiled.layout.final_index_layout() if compiled.layout else [0, 1]
            if [final[0], final[1]] != list(pair):
                raise SystemExit(f"{name}: routing moved the pair to {final[:2]}")
            arms[name] = compiled
        _COMPILED[key] = arms
    return _COMPILED[key]


def exact_laws(
    snapshot: dict[str, Any], pair: tuple[int, int], scenario: dict[str, float], device: str, slice_dt: int
) -> dict[str, np.ndarray]:
    """Exact noisy law of every arm, with each slice's exp(-i H dt_k) in place of its labeled barrier."""
    to_rad = 2.0 * math.pi * snapshot["dt"]
    rates = {key: value * to_rad for key, value in scenario.items()}

    def insert(operation: Instruction, qubits: list[int]) -> Instruction | None:
        if operation.name != "barrier":
            return operation
        label = operation.label or ""
        if not label.startswith("H:"):
            return None
        if qubits != list(pair):
            raise SystemExit(f"Hamiltonian marker on {qubits}, expected {list(pair)}")
        _, sector, length = label.split(":")
        return hamiltonian_unitary(rates, sector, int(length))

    return {
        name: snapshot_laws.outcome_law(snapshot, compiled, device, insert)
        for name, compiled in compiled_arms(snapshot, pair, slice_dt).items()
    }


class LawTask:
    """Picklable worker: (pair, scenario name, slice) -> exact laws and their summaries."""

    def __init__(self, snapshot: dict[str, Any], device: str) -> None:
        self.snapshot = snapshot
        self.device = device

    def __call__(self, item: tuple[tuple[int, int], str, int]) -> dict[str, Any]:
        pair, name, slice_dt = item
        laws = exact_laws(self.snapshot, pair, SCENARIOS[name], self.device, slice_dt)
        return {
            "laws": {member: [float(x) for x in law] for member, law in laws.items()},
            "summary": cr.summarize_distributions(laws),
            "unconditioned": cr.point_summary(laws, postselect=False),
        }


def sample_block(item: dict[str, Any]) -> dict[str, Any]:
    """One seeded block of whole-job resamples: point estimates, and plug-in errors on its first trials."""
    rng = np.random.default_rng(item["seed"])
    laws = {member: np.asarray(law) for member, law in item["laws"].items()}
    shots = item["shots"]
    estimates: dict[str, list[float]] = {key: [] for key in (*KEYS, *RATE_KEYS)}
    plugin: dict[str, list[float]] = {key: [] for key in KEYS}
    for trial in range(item["trials"]):
        sampled = {member: rng.multinomial(shots, law / law.sum()) / shots for member, law in laws.items()}
        if trial < item["plugin_trials"]:
            summary = cr.summarize_distributions(sampled)
            for key in KEYS:
                plugin[key].append(cr.standard_error(summary, key, shots))
        else:
            summary = cr.point_summary(sampled)
        for key in estimates:
            estimates[key].append(summary[key])
    return {"estimates": estimates, "plugin_se": plugin}


def to_hz(value: float, dt: float) -> float:
    return cr.rate_hz(value, dt)


def aggregate(
    pair: tuple[int, int], name: str, exact: dict[str, Any], blocks: list[dict[str, Any]], shots: int, dt: float
) -> dict[str, Any]:
    summary, unconditioned = exact["summary"], exact["unconditioned"]
    expected = injected(SCENARIOS[name])
    draws = {key: np.concatenate([block["estimates"][key] for block in blocks]) for key in (*KEYS, *RATE_KEYS)}
    starts = np.cumsum([0] + [len(block["estimates"][KEYS[0]]) for block in blocks[:-1]])
    plugin_index = np.concatenate(
        [start + np.arange(len(block["plugin_se"][KEYS[0]])) for start, block in zip(starts, blocks, strict=True)]
    ).astype(int)
    plugin_se = {key: np.concatenate([block["plugin_se"][key] for block in blocks]) for key in KEYS}
    trials = len(draws[KEYS[0]])
    slipped = np.zeros(trials, dtype=bool)
    for key in RATE_KEYS:
        slipped |= np.abs(draws[key] - summary[key]) > SLIP_SE * cr.standard_error(summary, key, shots)
    kept = ~slipped
    plugin_kept = kept[plugin_index]
    keys: dict[str, Any] = {}
    for key in KEYS:
        kept_draws = draws[key][kept]
        se = cr.standard_error(summary, key, shots)
        truth = expected[key] * 2.0 * math.pi * dt
        spread = float(np.std(kept_draws, ddof=1))
        plugin_draws = draws[key][plugin_index][plugin_kept]
        plugin_errors = plugin_se[key][plugin_kept]
        keys[key] = {
            "injected_hz": expected[key],
            "exact_law_hz": to_hz(summary[key], dt),
            "systematic_hz": to_hz(summary[key] - truth, dt),
            "unconditioned_systematic_hz": to_hz(unconditioned[key] - truth, dt),
            "delta_se_hz": to_hz(se, dt),
            "monte_carlo_sd_hz": to_hz(spread, dt),
            "sd_to_se": spread / se,
            "monte_carlo_bias_hz": to_hz(float(np.mean(kept_draws)) - summary[key], dt),
            "coverage_95": float(np.mean(np.abs(kept_draws - truth) <= Z95 * se)),
            "coverage_95_plugin": float(np.mean(np.abs(plugin_draws - truth) <= Z95 * plugin_errors)),
            "plugin_se_hz_median": to_hz(float(np.median(plugin_errors)), dt),
        }
    residual = draws["falsifier_residual"][kept]
    residual_se = cr.standard_error(summary, "falsifier_residual", shots)
    plugin_residual = draws["falsifier_residual"][plugin_index][plugin_kept]
    return {
        "pair": list(pair),
        "scenario": name,
        "rates_hz": SCENARIOS[name],
        "trials": trials,
        "plugin_trials": len(plugin_index),
        "slips": int(slipped.sum()),
        "falsifier_rejection_rate": float(np.mean(np.abs(residual) > Z95 * residual_se)),
        "falsifier_rejection_rate_plugin": float(
            np.mean(np.abs(plugin_residual) > Z95 * plugin_se["falsifier_residual"][plugin_kept])
        ),
        "visibility_10000dt": {
            sector: float(summary[f"{sector}_{cr.DELAYS_DT[-1]}dt_visibility"]) for sector in cr.SECTORS
        },
        "keys": keys,
    }


def environment(device: str) -> dict[str, Any]:
    return {
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "qiskit": qiskit.__version__,
        "qiskit_aer": qiskit_aer.__version__,
        "device": device,
        "workers": parallel.workers(),
    }


def run(
    pairs: tuple[tuple[int, int], ...],
    names: list[str],
    shots: int,
    trials: int,
    plugin_trials: int,
    device: str,
    convergence: bool = True,
) -> dict[str, Any]:
    if trials % BLOCKS or plugin_trials % BLOCKS or plugin_trials > trials:
        raise SystemExit(f"--trials and --plugin-trials must be multiples of {BLOCKS}, plugin at most trials")
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    dt = snapshot["dt"]
    started = time.time()
    cases = [(pair, name) for pair in pairs for name in names]
    extra = [(CONVERGENCE_CASE[0], CONVERGENCE_CASE[1], s) for s in CONVERGENCE_SLICES] if convergence else []
    items = [(pair, name, SLICE_DT) for pair, name in cases] + extra
    exact = parallel.ordered_map(LawTask(snapshot, device), items, min_items=1)
    blocks = [
        {
            "seed": [SEED_SAMPLES, pair[0], pair[1], list(SCENARIOS).index(name), block],
            "laws": exact[index]["laws"],
            "shots": shots,
            "trials": trials // BLOCKS,
            "plugin_trials": plugin_trials // BLOCKS,
        }
        for index, (pair, name) in enumerate(cases)
        for block in range(BLOCKS)
    ]
    sampled = parallel.ordered_map(sample_block, blocks, min_items=1)
    results = [
        aggregate(pair, name, exact[index], sampled[index * BLOCKS : (index + 1) * BLOCKS], shots, dt)
        for index, (pair, name) in enumerate(cases)
    ]
    expected_j = injected(SCENARIOS[CONVERGENCE_CASE[1]])["zz_j"]
    convergence_rows = [
        {
            "slice_dt": slice_dt,
            "unconditioned_zz_j_bias_hz": to_hz(row["unconditioned"]["zz_j"], dt) - expected_j,
            "postselected_zz_j_bias_hz": to_hz(row["summary"]["zz_j"], dt) - expected_j,
        }
        for (_, _, slice_dt), row in zip(extra, exact[len(cases) :], strict=True)
    ]
    return {
        "schema": "gororoba-conditional-ramsey-power-v2",
        "snapshot": str(SNAPSHOT.relative_to(ROOT)),
        "snapshot_sha256": hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest(),
        "calibration": snapshot["calibration"],
        "shots": shots,
        "trials": trials,
        "plugin_trials": plugin_trials,
        "blocks": BLOCKS,
        "slice_dt": SLICE_DT,
        "slice_convergence": {
            "pair": list(CONVERGENCE_CASE[0]),
            "scenario": CONVERGENCE_CASE[1],
            "rows": convergence_rows,
        },
        "slip_threshold_se": SLIP_SE,
        "seed_samples": SEED_SAMPLES,
        "seed_transpiler": SEED_TRANSPILER,
        "environment": environment(device),
        "seconds": round(time.time() - started, 1),
        "results": results,
    }


def bound_to_run(path: Path, run_dir: Path) -> list[str]:
    """FILE must be the byte-identical output that run_dir's collect.json ledger records."""
    ledger = json.loads((run_dir / "collect.json").read_text(encoding="utf-8"))
    recorded = ledger["files"].get(f"output/repo/{OUTPUT}")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if recorded is None:
        return [f"{run_dir}/collect.json records no {OUTPUT}"]
    return [] if digest == recorded else [f"{path} sha256 {digest} differs from the collected {recorded}"]


def check(path: Path, run_dir: Path, names: list[str], trials: int, plugin_trials: int) -> int:
    retained = json.loads(path.read_text(encoding="utf-8"))
    failures = bound_to_run(path, run_dir)
    pair = tuple(retained["results"][0]["pair"])
    replay = run((pair,), names, retained["shots"], trials, plugin_trials, "CPU", convergence=False)
    by_key = {(tuple(r["pair"]), r["scenario"]): r for r in retained["results"]}
    for result in replay["results"]:
        old = by_key[(tuple(result["pair"]), result["scenario"])]
        for key, fresh in result["keys"].items():
            kept = old["keys"][key]
            for field in ("exact_law_hz", "delta_se_hz", "unconditioned_systematic_hz"):
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
    parser.add_argument("--plugin-trials", type=int, default=400)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--run", type=Path, help="Kaggle run directory whose collected output --check binds")
    args = parser.parse_args()
    names = list(SCENARIOS) if args.scenarios == "all" else args.scenarios.split(",")
    unknown = sorted(set(names) - set(SCENARIOS))
    if unknown:
        parser.error(f"unknown scenarios {unknown}")
    if args.check:
        if args.run is None:
            parser.error("--check needs --run")
        return check(args.check, args.run, names, args.trials, args.plugin_trials)
    if args.out is None:
        parser.error("--out is required without --check")
    device = os.environ.get("GOROROBA_AER_DEVICE", "CPU")
    result = run(PAIRS, names, args.shots, args.trials, args.plugin_trials, device)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.out}: {len(result['results'])} pair-scenarios in {result['seconds']} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
