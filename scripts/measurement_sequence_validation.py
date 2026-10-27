"""Validate the measurement-sequence pinching analysis on Aer outcomes under a Heron noise model.

The planner compiles the family's 50 members per qubit onto the FakeFez Target (the repository's Heron r2
fixture) for eight qubits, the same entries a collected run archives. Each scenario simulates every entry with the
repository's noise simulator (live_run.noise_simulator: Target gate and coherence noise, asymmetric readout) at
8192 shots, hands the distributions and the Target values in force to measurement_sequence_analysis.collected, and
checks the device verdicts the decision rule fixes before any hardware data:

- planning: the Aer noise model as the Target reports it. Every qubit is usable, the mutation test passes on
  every qubit, no qubit departs by 3 standard errors and no device verdict fires. NoiseModel.from_backend charges
  no relaxation during a measure instruction, the window fraction 0, which the analysis covers with its window
  systematic.
- sx stress: the sx errors four times the Target's. The unitary arm's residual exceeds STRESS_RESIDUAL_MIN on every
  qubit, the propagated gate systematic widens each departure standard error, and no departure is attributed.
- tail: a bit flip of probability TAIL_EPS after each mid-circuit measurement of the measure arm only, the
  signature of a readout tail that decays within the settle gap. The settle verdict `settle_reduced_by_gap`
  fires at the device and on every qubit, and the measure arm's departure is attributed.
- transition: the same flip after each mid-circuit measurement of the measure and settle arms. The departure is
  attributed at the device and the settle verdict stays `unchanged_by_gap` on every qubit.

Shot-sampled rows use the 3 standard error rule on every per-qubit statistic. The seeds are values of one ANU QRNG
draw, one per scenario in scenario order.

Usage: "$PYTHON" scripts/measurement_sequence_validation.py [--out FILE]
"""

from __future__ import annotations

import argparse
import copy
import dataclasses
import hashlib
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any

from qiskit.transpiler import InstructionProperties
from qiskit_aer.noise import pauli_error
from qiskit_ibm_runtime.fake_provider import FakeFez

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import live_run  # noqa: E402
import measurement_sequence_analysis as analysis  # noqa: E402
import qpu_planning  # noqa: E402
import qpu_planning_contracts as contracts  # noqa: E402

SHOTS = 8192
LAYOUT_CANDIDATES = (10, 25, 40, 55, 70, 85, 100, 115, 130, 145)
QUBITS = 8
SX_STRESS = 4.0
# The unitary arm's measured-minus-modeled residual that a stress of SX_STRESS must exceed on every qubit.
STRESS_RESIDUAL_MIN = 0.01
TAIL_EPS = 0.01
# Values 0 to 3 of docs/evidence/anu_qrng/draw-2026-10-25T225550Z.json, one per scenario in order: planning,
# sx stress, tail, transition.
VALIDATION_SEEDS = (29206, 27743, 23218, 58511)
SCENARIOS = ("planning", "sx_stress", "tail", "transition")


def snapshot() -> Any:
    backend = contracts._ProbeBackend("measurement_sequence_validation", FakeFez())
    service = contracts._ProbeService([backend])
    with redirect_stdout(io.StringIO()):
        return live_run.take_snapshot(service, backend.name)


def plan(snap: Any) -> tuple[list[Any], dict[str, Any], list[int]]:
    qubits = [q for q in LAYOUT_CANDIDATES if q not in snap.excluded_qubits][:QUBITS]
    if len(qubits) != QUBITS:
        raise RuntimeError(f"the fixture admits {len(qubits)} of {QUBITS} qubits")
    args = contracts._args(
        "measurement-sequence",
        layout=qubits,
        optimize=True,
        shot_tiers=[SHOTS],
        optimizer_candidates=1,
        max_execution_seconds=200,
        max_total_execution_seconds=400.0,
        reserve_seconds=0.0,
    )
    candidates = qpu_planning.family_candidates(live_run, [snap], args, {})
    if len(candidates) != 1:
        raise RuntimeError("the planner refused the validation layout")
    choices, configuration = candidates[0]
    return choices, configuration, qubits


def executed_stub(entries: list[Any], props: Any, qubits: list[int]) -> dict[str, Any]:
    calibration = live_run.placed_qubit_calibration(props, qubits)
    gates = live_run.placed_gate_calibration(props, qubits)
    return {
        entry.name: {"shots": SHOTS, "placed_qubit_calibration": calibration, "placed_gate_calibration": gates}
        for entry in entries
    }


def stressed_target(target: Any, qubits: list[int]) -> Any:
    stressed = copy.deepcopy(target)
    for q in qubits:
        item = target["sx"][(q,)]
        stressed.update_instruction_properties(
            "sx", (q,), InstructionProperties(duration=item.duration, error=SX_STRESS * item.error)
        )
    return stressed


def inject(entries: list[Any], arms: tuple[str, ...]) -> list[Any]:
    """Entries whose replicas carry an `id` after every mid-circuit measurement of the named arms."""
    out = []
    for entry in entries:
        if entry.name.split("_")[1] not in arms:
            out.append(entry)
            continue
        replicas = []
        for replica in entry.replicas:
            rebuilt = replica.copy_empty_like()
            for inst in replica.data:
                rebuilt.append(inst.operation, inst.qubits, inst.clbits)
                if inst.operation.name == "measure" and replica.find_bit(inst.clbits[0]).index >= 1:
                    rebuilt.id(inst.qubits[0])
            replicas.append(rebuilt)
        out.append(dataclasses.replace(entry, replicas=replicas))
    return out


def flip_simulator(snap: Any, qubits: list[int]) -> Any:
    """The snapshot's noise model with a bit flip of probability TAIL_EPS on every `id`."""
    view = live_run.TargetView(snap.name, snap.backend.target)
    noise = copy.deepcopy(live_run._noise_model(snap.name, view, snap.backend.target, snap.properties))
    for q in qubits:
        noise.add_quantum_error(pauli_error([("X", TAIL_EPS), ("I", 1 - TAIL_EPS)]), ["id"], [q])
    simulator = live_run.local_compute.SerializedNoiseSimulator.from_backend(
        view, noise_model=noise, method="density_matrix"
    )
    live_run.local_compute.configure(simulator, live_run.local_compute.settings())
    return simulator


def scenario_rows(
    snap: Any, entries: list[Any], configuration: dict[str, Any], qubits: list[int]
) -> dict[str, dict[str, Any]]:
    props = snap.properties
    target = snap.backend.target
    record = {"family_configuration": configuration}
    executed = executed_stub(entries, props, qubits)
    out: dict[str, dict[str, Any]] = {}
    runs = {
        "planning": (live_run.noise_simulator(snap.name, target, props), entries),
        "sx_stress": (live_run.noise_simulator(snap.name + "_stress", stressed_target(target, qubits), props), entries),
        "tail": (flip_simulator(snap, qubits), inject(entries, ("measure",))),
        "transition": (flip_simulator(snap, qubits), inject(entries, ("measure", "settle"))),
    }
    for seed, scenario in zip(VALIDATION_SEEDS, SCENARIOS, strict=True):
        simulator, run_entries = runs[scenario]
        distributions = live_run.simulate_entries(simulator, run_entries, SHOTS, seed)
        out[scenario] = analysis.collected(record, distributions, executed, analysis.DEMONSTRATION_SCATTER_FLOOR)
    return out


def violations(scenario: str, result: dict[str, Any]) -> list[str]:
    """The scenario's assertions; an empty list means the decision rule behaved as preregistered."""
    if "withheld" in result:
        return [f"{scenario}: withheld: {result['withheld']}"]
    failures = []
    device, qubits = result["device"], result["qubits"]
    flags = analysis.device_flags(device)
    rows = list(qubits.values())
    if any(not r["usable"] for r in rows):
        failures.append(f"{scenario}: an unusable qubit")
        return failures
    if not device["mutation_test_passes"]:
        failures.append(f"{scenario}: the mutation test fails on {device['mutation_test_failed_qubits']}")
    if scenario != "sx_stress" and device["status"] != "informative":
        failures.append(f"{scenario}: the device reads {device['status']}: {device['uninformative_qubits']}")
    gap = [r["settle_n16"]["verdict"] for r in rows]
    z_dep = [r["decisions"]["departure"]["z"] for r in rows]
    if scenario == "planning":
        if any(abs(z) >= analysis.Z_DECIDE for z in z_dep):
            failures.append(f"planning: departure z {z_dep}")
        if any(v != "unchanged_by_gap" for v in gap):
            failures.append(f"planning: settle {gap}")
        if any(flags.values()):
            failures.append(f"planning: device flags {flags}")
    elif scenario == "sx_stress":
        residuals = [r["gate_systematic_n16"]["unitary_residual"] for r in rows]
        if min(residuals) <= STRESS_RESIDUAL_MIN:
            failures.append(f"sx_stress: the unitary arm did not show the stress: {residuals}")
        if flags["departs_below"] or flags["exceeds_prediction"]:
            failures.append(f"sx_stress: a departure was attributed to a gate error: {flags}")
        if device["status"] == "informative" and device["departs_below"]["status"] != "none":
            failures.append(f"sx_stress: {device['departs_below']}")
    elif scenario == "tail":
        if not flags["settle_reduced_by_gap"] or any(v != "reduced_by_gap" for v in gap):
            failures.append(f"tail: the settle verdict missed the tail: {gap} {device['settle_reduced_by_gap']}")
        if not flags["departs_below"]:
            failures.append(f"tail: the measure arm's departure is not attributed: {device['departs_below']}")
    elif scenario == "transition":
        if not flags["departs_below"]:
            failures.append(f"transition: the departure is not attributed: {device['departs_below']}")
        if any(v != "unchanged_by_gap" for v in gap) or flags["settle_reduced_by_gap"]:
            failures.append(f"transition: the settle verdict moved: {gap}")
    return failures


def summary(result: dict[str, Any]) -> dict[str, Any]:
    qubits = result["qubits"]
    return {
        "device": result["device"],
        "informative": {q: r["informative"] for q, r in qubits.items()},
        "departure_z": {q: r["decisions"]["departure"]["z"] for q, r in qubits.items()},
        "settle_z": {q: r["settle_n16"]["z"] for q, r in qubits.items()},
        "settle_verdict": {q: r["settle_n16"]["verdict"] for q, r in qubits.items()},
        "mutation_z": {q: r["decisions"]["mutation_test"]["z"] for q, r in qubits.items()},
        "unitary_residual": {q: r["gate_systematic_n16"]["unitary_residual"] for q, r in qubits.items()},
        "propagated_se": {q: r["gate_systematic_n16"]["propagated_se"] for q, r in qubits.items()},
        "t1_fit_over_target": {q: r["fitted"]["t1_s"] for q, r in qubits.items()},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, help="write the scenario summaries as JSON")
    args = parser.parse_args(argv)
    snap = snapshot()
    choices, configuration, qubits = plan(snap)
    entries = [entry for choice in choices for entry in choice.entries]
    results = scenario_rows(snap, entries, configuration, qubits)
    failures = [f for scenario, result in results.items() for f in violations(scenario, result)]
    text = json.dumps(
        {
            "schema": "measurement-sequence-aer-validation-v1",
            "backend_fixture": "FakeFez",
            "shots": SHOTS,
            "model_scatter_floor": {
                "value": analysis.DEMONSTRATION_SCATTER_FLOOR,
                "source": "illustrative value that exercises the mechanism; no measurement of a device",
            },
            "qubits": qubits,
            "seeds": dict(zip(SCENARIOS, VALIDATION_SEEDS, strict=True)),
            "analysis_sha256": hashlib.sha256(
                (ROOT / "gororoba_quantum/measurement_sequence_analysis.py").read_bytes()
            ).hexdigest(),
            "failures": failures,
            "scenarios": {scenario: summary(r) for scenario, r in results.items() if "withheld" not in r},
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
