"""Validate the scatter-floor estimator on Aer outcomes under a Heron noise model.

The planner compiles the measurement-sequence-diagnostic members for the main family's eight qubits and thirty
further qubits (the calibration-only rule applied to the FakeFez Target, the repository's Heron r2 fixture). Each
scenario simulates every entry with the repository's noise simulator at 8192 shots, hands the distributions and the
Target values in force to measurement_sequence_scatter.collected and checks the floor against its construction:

- planning: the Target's noise as reported. The floor stays within sampling error of the model-mismatch allowance
  and the statistical scatter, `sqrt(statistical_rms ** 2 + MISMATCH ** 2)`.
- injected: an RZ after every sx of the named qubits (a tilt of the next pulse's axis), solved per member to move
  the ideal P0 by +INJECTED or -INJECTED, alternating by qubit index. The floor recovers INJECTED within TOLERANCE
  and every residual carries the injected sign.
- main_only: the tilt error of +INJECTED_MAIN on the main qubits only (a tilt moves the ideal P0 down by at most about
  0.021, so the larger magnitude takes the positive side). The all-qubit root-mean-square falls below the
  main-qubit value and the floor equals the larger, the main-qubit value.
- t2_ordered: the tilt error of +INJECTED on qubits above the median T2 and -INJECTED below it. The residual-vs-T2
  rank correlation is positive and its two-sided p value is below 0.001.

The seeds are values 0 to 3 of one ANU QRNG draw, one per scenario in scenario order.

Usage: "$PYTHON" scripts/measurement_sequence_scatter_validation.py [--out FILE]
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import io
import json
import math
import sys
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any

import numpy as np
from qiskit_ibm_runtime.fake_provider import FakeFez
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import live_run  # noqa: E402
import measurement_sequence_scatter as scatter  # noqa: E402
import qpu_planning  # noqa: E402
import qpu_planning_contracts as contracts  # noqa: E402
from diagnostic_experiments import MSQD_FAMILY, MSQD_MAIN_QUBITS  # noqa: E402

SHOTS = 8192
INJECTED = 0.02
INJECTED_MAIN = 0.03
# Aer charges no relaxation during a measure instruction and the model takes the planning excitation and the
# calibrated T1, so the planning residual carries a small bias that the allowance covers.
MISMATCH = 0.003
# Relative tolerance of the recovered floor: the injected residuals are exact up to the readout scale and the
# statistical noise (about 0.001), so the root-mean-square has almost no sampling spread.
TOLERANCE = 0.10
# Values 0 to 3 of docs/evidence/anu_qrng/draw-2026-10-26T013550Z.json, one per scenario in order: planning,
# injected, main_only, t2_ordered.
VALIDATION_SEEDS = (51265, 23818, 46022, 56168)
SCENARIOS = ("planning", "injected", "main_only", "t2_ordered")


def snapshot() -> Any:
    backend = contracts._ProbeBackend("measurement_sequence_scatter_validation", FakeFez())
    service = contracts._ProbeService([backend])
    with redirect_stdout(io.StringIO()):
        return live_run.take_snapshot(service, backend.name)


def plan(snap: Any) -> tuple[list[Any], dict[str, Any], list[int], dict[str, Any]]:
    calibration = scatter.calibration_from_snapshot(snap)
    # The fixture excludes some of the main family's qubits; the layout keeps the others and tops up to 38 qubits.
    main = tuple(q for q in MSQD_MAIN_QUBITS if q not in calibration["excluded"])
    count = scatter.EXTRA_COUNT + len(MSQD_MAIN_QUBITS) - len(main)
    qubits = [*main, *scatter.select_extra_qubits(calibration, main, count)]
    args = contracts._args(
        MSQD_FAMILY,
        layout=qubits,
        optimize=True,
        shot_tiers=[SHOTS],
        optimizer_candidates=1,
        max_execution_seconds=200,
        max_total_execution_seconds=400.0,
        reserve_seconds=0.0,
    )
    trace: dict[str, Any] = {}
    candidates = qpu_planning.family_candidates(live_run, [snap], args, trace)
    if len(candidates) != 1:
        raise RuntimeError(f"the planner refused the validation layout: {trace.get('family_rejections')}")
    choices, configuration = candidates[0]
    return choices, configuration, qubits, calibration


def executed_stub(entries: list[Any], props: Any, qubits: list[int]) -> dict[str, Any]:
    calibration = live_run.placed_qubit_calibration(props, qubits)
    gates = live_run.placed_gate_calibration(props, qubits)
    return {
        entry.name: {"shots": SHOTS, "placed_qubit_calibration": calibration, "placed_gate_calibration": gates}
        for entry in entries
    }


SX = np.array([[1 + 1j, 1 - 1j], [1 - 1j, 1 + 1j]]) / 2


def rz_matrix(angle: float) -> np.ndarray:
    return np.diag([np.exp(-0.5j * angle), np.exp(0.5j * angle)])


def compiled_p0(replica: Any, error: float) -> float:
    """Ideal P0 of a compiled single-qubit member with an RZ(error) after each sx: the relative-tilt class of the
    analysis. The compiled circuit holds only rz, sx, x and non-unitary delay, barrier and measure operations."""
    unitary = np.eye(2, dtype=complex)
    for inst in replica.data:
        name = inst.operation.name
        if name == "rz":
            unitary = rz_matrix(float(inst.operation.params[0])) @ unitary
        elif name == "sx":
            unitary = rz_matrix(error) @ SX @ unitary
        elif name == "x":
            unitary = np.array([[0, 1], [1, 0]], dtype=complex) @ unitary
        elif name not in ("delay", "barrier", "measure", "id"):
            raise RuntimeError(f"unexpected compiled operation {name}")
    return float(abs(unitary[0, 0]) ** 2)


def tilt_for(replica: Any, residual: float) -> float:
    """The smallest RZ error after each sx that moves the member's ideal P0 by `residual`."""
    base = compiled_p0(replica, 0.0)

    def gap(error: float) -> float:
        return compiled_p0(replica, error) - base - residual

    grid = np.linspace(-0.03, 0.03, 601)
    values = [gap(float(e)) for e in grid]
    crossings = [k for k in range(len(grid) - 1) if values[k] == 0.0 or values[k] * values[k + 1] < 0]
    if not crossings:
        raise RuntimeError(f"no tilt in +-0.03 rad moves the member's P0 by {residual}")
    k = min(crossings, key=lambda i: abs(grid[i] + grid[i + 1]))
    return float(brentq(gap, grid[k], grid[k + 1], xtol=1e-15))


def tilted(entries: list[Any], residuals: dict[int, float]) -> list[Any]:
    """Entries whose unitary-member replicas carry an RZ after every sx on a qubit with a named residual.

    The RZ is a native gate that the noise model leaves exact. A tilt of given sign moves the +THETA and -THETA
    members' P0 in opposite directions, so each member takes its own error, solved so that every member's ideal P0
    moves by the qubit's residual and the pooled P0 moves by the same amount.
    """
    out = []
    for entry in entries:
        qubit = int(entry.name.rsplit("_q", 1)[1])
        if not entry.name.startswith("msq_unitary_") or residuals.get(qubit, 0.0) == 0.0:
            out.append(entry)
            continue
        replicas = []
        for replica in entry.replicas:
            error = tilt_for(replica, residuals[qubit])
            rebuilt = replica.copy_empty_like()
            for inst in replica.data:
                rebuilt.append(inst.operation, inst.qubits, inst.clbits)
                if inst.operation.name == "sx":
                    rebuilt.rz(error, inst.qubits[0])
            replicas.append(rebuilt)
        out.append(dataclasses.replace(entry, replicas=replicas))
    return out


def scenario_residuals(qubits: list[int], t2: dict[int, float]) -> dict[str, dict[int, float]]:
    median = sorted(t2[q] for q in qubits)[len(qubits) // 2]
    return {
        "planning": {},
        "injected": {q: INJECTED if q % 2 == 0 else -INJECTED for q in qubits},
        "main_only": {q: INJECTED_MAIN for q in MSQD_MAIN_QUBITS if q in qubits},
        "t2_ordered": {q: INJECTED if t2[q] >= median else -INJECTED for q in qubits},
    }


def violations(scenario: str, result: dict[str, Any], injected: dict[int, float], baseline: float) -> list[str]:
    if "withheld" in result:
        return [f"{scenario}: withheld: {result['withheld']}"]
    rows = {int(q): r for q, r in result["qubits"].items()}
    summary = result["floor"]
    if summary.get("floor") is None:
        return [f"{scenario}: no floor: {summary.get('withheld')}"]
    n = summary["informative"]
    failures = []
    floor = summary["floor"]
    if scenario == "planning":
        allowance = math.sqrt(summary["statistical_rms"] ** 2 + MISMATCH**2)
        limit = (1 + 3 / math.sqrt(2 * n)) * allowance
        if floor > limit:
            failures.append(f"planning: floor {floor:.4f} exceeds {limit:.4f}")
        return failures
    expected_all = math.sqrt(
        math.fsum(injected.get(q, 0.0) ** 2 for q in rows if rows[q]["informative"]) / n + baseline**2
    )
    if scenario in ("injected", "t2_ordered"):
        if abs(floor - expected_all) > TOLERANCE * expected_all:
            failures.append(f"{scenario}: floor {floor:.4f}, expected {expected_all:.4f}")
        wrong = [q for q, r in rows.items() if r["informative"] and r["residual"] * injected[q] <= 0]
        if wrong:
            failures.append(f"{scenario}: residual sign wrong on {wrong}")
    if scenario == "main_only":
        if not (summary["rms_main"] > summary["rms_all"] and floor == summary["rms_main"]):
            failures.append(
                f"main_only: floor {floor:.4f}, main {summary['rms_main']:.4f}, all {summary['rms_all']:.4f}"
            )
        if abs(summary["rms_main"] - INJECTED_MAIN) > TOLERANCE * INJECTED_MAIN:
            failures.append(f"main_only: the main root-mean-square {summary['rms_main']:.4f} misses {INJECTED_MAIN}")
    if scenario == "t2_ordered":
        pattern = result["t2_pattern"]["residual_vs_t2"]
        if not (pattern["rho"] > 0 and pattern["p_two_sided"] < 1e-3):
            failures.append(f"t2_ordered: the T2 pattern {pattern}")
    return failures


def summary_of(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "floor": result["floor"],
        "t2_pattern": result["t2_pattern"],
        "residual": {q: r.get("residual") for q, r in result["qubits"].items()},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, help="write the scenario summaries as JSON")
    args = parser.parse_args(argv)
    snap = snapshot()
    choices, configuration, qubits, calibration = plan(snap)
    entries = [entry for choice in choices for entry in choice.entries]
    props, target = snap.properties, snap.backend.target
    record = {"family_configuration": configuration}
    executed = executed_stub(entries, props, qubits)
    t2 = {q: float(calibration["qubits"][q]["t2_s"]) for q in qubits}
    residuals = scenario_residuals(qubits, t2)
    results: dict[str, dict[str, Any]] = {}
    for seed, scenario in zip(VALIDATION_SEEDS, SCENARIOS, strict=True):
        simulator = live_run.noise_simulator(snap.name, target, props)
        distributions = live_run.simulate_entries(simulator, tilted(entries, residuals[scenario]), SHOTS, seed)
        results[scenario] = scatter.collected(record, distributions, executed)
    planning = results["planning"]
    baseline = planning["floor"]["floor"] if "withheld" not in planning else 0.0
    failures = [f for s in SCENARIOS for f in violations(s, results[s], residuals[s], baseline or 0.0)]
    text = json.dumps(
        {
            "schema": "measurement-sequence-scatter-validation-v1",
            "backend_fixture": "FakeFez",
            "shots": SHOTS,
            "qubits": qubits,
            "injected": {"alternating": INJECTED, "main_only": INJECTED_MAIN, "mismatch_allowance": MISMATCH},
            "tolerance": TOLERANCE,
            "seeds": dict(zip(SCENARIOS, VALIDATION_SEEDS, strict=True)),
            "scatter_sha256": hashlib.sha256(
                (ROOT / "gororoba_quantum/measurement_sequence_scatter.py").read_bytes()
            ).hexdigest(),
            "analysis_sha256": hashlib.sha256(
                (ROOT / "gororoba_quantum/measurement_sequence_analysis.py").read_bytes()
            ).hexdigest(),
            "failures": failures,
            "scenarios": {s: summary_of(r) for s, r in results.items() if "withheld" not in r},
        },
        indent=2,
        sort_keys=True,
    )
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    if failures:
        raise SystemExit("validation failed: " + "; ".join(failures))
    return 0


if __name__ == "__main__":
    sys.exit(main())
