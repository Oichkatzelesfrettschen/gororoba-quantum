"""A_5 complex kernel case on Garnet: builder, manifest, circuits and the preregistered estimators."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import iqm_complex_kernel_case as case
import iqm_sim
import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

import a5_complex_kernel_decision as decision
import pathion_complex_block as pcx

ROOT = Path(__file__).resolve().parents[2]
CASE_DIR = ROOT / "results/iqm/cases/a5-complex-kernel-garnet"
DRAW = ROOT / "docs/evidence/anu_qrng/draw-2026-11-27T222523Z.json"
LABEL = {"real": "1", "cplx": "i", "plain": "i"}


def require(condition: bool) -> None:
    if not condition:
        raise AssertionError


def prediction() -> dict[str, Any]:
    return dict(json.loads((CASE_DIR / "prediction.json").read_text(encoding="utf-8")))


def counts_from(
    laws: dict[str, dict[str, dict[str, float]]], kept: int
) -> dict[str, dict[str, tuple[int, int, int, int]]]:
    out: dict[str, dict[str, tuple[int, int, int, int]]] = {}
    for name, kinds in laws.items():
        out[name] = {kind: (round(z["plus"] * kept), kept, round(z["minus"] * kept), kept) for kind, z in kinds.items()}
    return out


def predicted_zero() -> dict[str, dict[str, dict[str, float]]]:
    pred = prediction()
    return {
        name: {kind: row["predicted_zero"] for kind, row in op["kinds"].items()}
        for name, op in pred["operands"].items()
    }


@pytest.mark.audit
def test_builder_regenerates_the_retained_case() -> None:
    case.check(CASE_DIR)


def native_law(circuit: dict[str, Any], calibration: iqm_sim.Calibration) -> np.ndarray:
    """Noiseless outcome law over the measured bits (bit c = qubit c of the measure locus) of a native circuit,
    simulated on the qubits it touches."""
    qc, bits = iqm_sim.to_qiskit(circuit, calibration)
    body = qc.remove_final_measurements(inplace=False)
    touched = sorted({body.find_bit(q).index for item in body.data for q in item.qubits})
    local = {q: n for n, q in enumerate(touched)}
    small = QuantumCircuit(len(touched))
    for item in body.data:
        small.append(item.operation, [local[body.find_bit(q).index] for q in item.qubits])
    return np.asarray(Statevector(small).probabilities([local[calibration.qubits.index(q)] for _, q in bits]))


def test_seeds_are_the_draw_values_at_indices_10_to_17() -> None:
    values = json.loads(DRAW.read_text(encoding="utf-8"))["values"]
    require(list(case.TRANSPILER_SEEDS) == values[10:18])


def test_manifest_limits_and_prediction_binding() -> None:
    manifest = json.loads((CASE_DIR / "cases.json").read_text(encoding="utf-8"))
    (job,) = manifest["jobs"]
    require(len(job["circuits"]) == 80 <= case.MAX_CIRCUITS)
    require(len(job["circuits"]) * job["shots"] <= case.MAX_EXECUTIONS)
    require(job["max_credits"] == {"garnet:mock": 0.0, "garnet": job["max_credits"]["garnet"]})
    require(0 < job["max_credits"]["garnet"] <= case.CEILING_CREDITS)
    require(job["options"]["heralding_mode"] == "zeros" and job["options"]["active_reset_cycles"] == 1)
    require(manifest["prediction_sha256"] == case.sha256((CASE_DIR / "prediction.json").read_bytes()))
    for entry in job["circuits"]:
        require(case.sha256((CASE_DIR / entry["file"]).read_bytes()) == entry["sha256"])


def test_every_contrast_runs_plus_minus_minus_plus_and_the_kinds_mirror() -> None:
    names = prediction()["order"]
    require(len(set(names)) == len(names) == 80)
    quads = [names[i : i + 4] for i in range(0, len(names), 4)]
    for quad in quads:
        require([n.split("-")[2] for n in quad] == ["plus", "minus", "minus", "plus"])
        require(len({tuple(n.split("-")[:2]) for n in quad}) == 1)
    kinds = [tuple(q[0].split("-")[:2]) for q in quads]
    require(kinds == kinds[::-1] and len(set(kinds[: len(kinds) // 2])) == len(kinds) // 2)
    require(len(kinds) // 2 == 10)


@pytest.mark.parametrize("operand", case.OPERANDS, ids=lambda op: op.name)
def test_emitted_circuits_have_the_ideal_block_law(operand: case.Operand) -> None:
    calibration = iqm_sim.Calibration.from_directory(CASE_DIR / "calibration")
    block = case.block_of(operand)
    for kind in operand.kinds:
        for orientation in ("plus", "minus"):
            circuit = json.loads(
                (CASE_DIR / f"circuits/{operand.name}-{kind}-{orientation}-00.json").read_text("utf-8")
            )
            law = native_law(circuit, calibration)
            t = 1 if kind == "real" else 1j
            ideal = pcx.block_law(block, t, orientation == "plus", plain=kind == "plain")
            require(bool(np.allclose(law, ideal, atol=1e-8)))
            require(
                circuit["instructions"][-1]["name"] == "measure"
                and len(circuit["instructions"][-1]["locus"]) == block.d + 1
            )


def test_real_and_complex_circuits_of_an_operand_differ_in_angles_alone() -> None:
    for operand in case.OPERANDS:
        a = json.loads((CASE_DIR / f"circuits/{operand.name}-real-plus-00.json").read_text("utf-8"))["instructions"]
        b = json.loads((CASE_DIR / f"circuits/{operand.name}-cplx-plus-00.json").read_text("utf-8"))["instructions"]
        require([(x["name"], x["locus"]) for x in a] == [(x["name"], x["locus"]) for x in b])


def test_mutation_changes_the_ideal_observable() -> None:
    ideal = {
        (op.name, kind): case.ideal_difference(case.block_of(op), kind) for op in case.OPERANDS for kind in op.kinds
    }
    require(abs(ideal["s016", "plain"] + 1) < 1e-9 and abs(ideal["s016", "cplx"] - 1) < 1e-9)
    require(abs(ideal["s412", "plain"] + 0.75) < 1e-9 and abs(ideal["s412", "cplx"] - 0.75) < 1e-9)
    require(abs(ideal["s016", "real"]) < 1e-9 and abs(ideal["s808", "cplx"] - ideal["s808", "real"]) < 1e-9)


def test_the_double_difference_is_zero_at_the_null_operand_and_signed_elsewhere() -> None:
    ideal = {
        (op.name, kind): case.ideal_difference(case.block_of(op), kind) for op in case.OPERANDS for kind in op.kinds
    }
    signs = {name: np.sign(ideal[name, "cplx"] - ideal[name, "real"]) for name in ("s016", "s412", "s124")}
    require(signs == {"s016": 1, "s412": 1, "s124": -1})
    require(abs(ideal["s808", "cplx"] - ideal["s808", "real"]) < 1e-9)


def test_device_that_follows_the_noise_model_reads_complex_strata() -> None:
    kept = prediction()["planning"]["kept_shots_per_orientation"]
    result = decision.analyze(counts_from(predicted_zero(), kept))
    require(result["verdict"] == "complex strata" and result["null_ok"])
    for name, n_c in (("s016", 16.0), ("s412", 12.0), ("s124", 4.0)):
        estimate = result["estimates"][name]["n_c"]
        require(estimate is not None and abs(estimate - n_c) < 0.2)


def test_real_map_law_for_the_complex_circuit_is_not_read_as_complex() -> None:
    kept = prediction()["planning"]["kept_shots_per_orientation"]
    laws = predicted_zero()
    for kinds in laws.values():
        kinds["cplx"] = kinds["real"]
    result = decision.analyze(counts_from(laws, kept))
    require(result["verdict"] == "no reading")
    for name in ("s016", "s412", "s124"):
        estimate = result["estimates"][name]["n_c"]
        require(estimate is None or abs(estimate - decision.MIDPOINT) < 1e-9)


def test_plain_law_for_the_complex_circuit_is_not_read_as_complex() -> None:
    kept = prediction()["planning"]["kept_shots_per_orientation"]
    laws = predicted_zero()
    for name in ("s016", "s412"):
        laws[name]["cplx"] = laws[name]["plain"]
    result = decision.analyze(counts_from(laws, kept))
    require(result["verdict"] == "no reading")
    require(result["sides"]["s016"] == "unresolved" and result["sides"]["s412"] == "unresolved")


def test_swapped_kinds_read_real_strata() -> None:
    kept = prediction()["planning"]["kept_shots_per_orientation"]
    laws = predicted_zero()
    for kinds in laws.values():
        kinds["cplx"], kinds["real"] = kinds["real"], kinds["cplx"]
    require(decision.analyze(counts_from(laws, kept))["verdict"] == "real strata")


def test_failed_mutation_control_blocks_the_complex_verdict() -> None:
    kept = prediction()["planning"]["kept_shots_per_orientation"]
    laws = predicted_zero()
    laws["s016"]["plain"] = laws["s016"]["cplx"]
    require(decision.analyze(counts_from(laws, kept))["verdict"] == "complex side, a control fails")


def test_recorded_power_follows_the_predicted_z() -> None:
    pred = prediction()
    z = [pred["operands"][n]["predicted"]["z_nullity_from_midpoint"] for n in decision.DISCRIMINATING]
    require(abs(pred["decision"]["power_complex_truth"] - round(decision.power(z), 6)) < 1e-9)
    require(decision.power([5.0]) == pytest.approx(0.5))
