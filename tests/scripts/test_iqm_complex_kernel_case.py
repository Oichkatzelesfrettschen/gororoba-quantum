"""A_5 complex kernel case on Garnet: builder, manifest, circuits, audit and the preregistered estimators."""

from __future__ import annotations

import json
import math
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


def require(condition: bool) -> None:
    if not condition:
        raise AssertionError


def prediction() -> dict[str, Any]:
    return dict(json.loads((CASE_DIR / "prediction.json").read_text(encoding="utf-8")))


def counts_from(laws: dict[str, dict[str, dict[str, float]]], kept: int) -> dict[str, dict[str, Any]]:
    return case.counts_from_zero(laws, kept)


def predicted_zero() -> dict[str, dict[str, dict[str, float]]]:
    pred = prediction()
    return {
        name: {kind: dict(row["predicted_zero"]) for kind, row in op["kinds"].items()}
        for name, op in pred["operands"].items()
    }


def circuit(name: str) -> dict[str, Any]:
    return dict(json.loads((CASE_DIR / f"circuits/{name}.json").read_text(encoding="utf-8")))


def native_law(native: dict[str, Any], calibration: iqm_sim.Calibration) -> np.ndarray:
    """Noiseless outcome law over the measured bits (bit c = qubit c of the measure locus) of a native circuit,
    simulated on the qubits it touches."""
    qc, bits = iqm_sim.to_qiskit(native, calibration)
    body = qc.remove_final_measurements(inplace=False)
    touched = sorted({body.find_bit(q).index for item in body.data for q in item.qubits})
    local = {q: n for n, q in enumerate(touched)}
    small = QuantumCircuit(len(touched))
    for item in body.data:
        small.append(item.operation, [local[body.find_bit(q).index] for q in item.qubits])
    return np.asarray(Statevector(small).probabilities([local[calibration.qubits.index(q)] for _, q in bits]))


@pytest.mark.audit
def test_builder_regenerates_the_retained_case() -> None:
    case.check(CASE_DIR)


def test_seeds_are_the_draw_values_at_indices_10_to_17() -> None:
    values = json.loads(DRAW.read_text(encoding="utf-8"))["values"]
    require(list(case.TRANSPILER_SEEDS) == values[10:18])


def test_manifest_limits_ceiling_and_prediction_binding() -> None:
    manifest = json.loads((CASE_DIR / "cases.json").read_text(encoding="utf-8"))
    pred = prediction()
    (job,) = manifest["jobs"]
    require(len(job["circuits"]) == 80 <= case.MAX_CIRCUITS)
    require(len(job["circuits"]) * job["shots"] <= case.MAX_EXECUTIONS and job["shots"] == pred["shots"])
    require(job["max_credits"] == {"garnet:mock": 0.0, "garnet": case.CEILING_CREDITS})
    require(case.CEILING_CREDITS <= case.OWNER_BOUND_CREDITS)
    require(job["options"]["heralding_mode"] == "zeros" and job["options"]["active_reset_cycles"] == 1)
    require(manifest["prediction_sha256"] == case.sha256((CASE_DIR / "prediction.json").read_bytes()))
    for entry in job["circuits"]:
        require(case.sha256((CASE_DIR / entry["file"]).read_bytes()) == entry["sha256"])
    margins = pred["cost"]["overrun_margins"]
    require(all(margins[k]["covered"] for k in ("1x", "1.5x", "2.2x")))
    require(pred["cost"]["job_ceiling"]["cancel_threshold_seconds"] == 20.0)


def test_every_contrast_runs_plus_minus_minus_plus_and_the_kinds_mirror() -> None:
    names = prediction()["order"]
    require(len(set(names)) == len(names) == 80)
    quads = [names[i : i + 4] for i in range(0, len(names), 4)]
    for quad in quads:
        require([n.split("-")[2] for n in quad] == ["plus", "minus", "minus", "plus"])
        require(len({tuple(n.split("-")[:2]) for n in quad}) == 1)
    kinds = [tuple(q[0].split("-")[:2]) for q in quads]
    require(kinds == kinds[::-1] and len(set(kinds[: len(kinds) // 2])) == len(kinds) // 2 == 10)


def test_all_operands_run_on_one_patch_including_the_null_operand() -> None:
    pred = prediction()
    require(pred["patch"] == list(case.PATCH))
    for name, operand in pred["operands"].items():
        require(set(operand["physical_qubits"]) <= set(case.PATCH))
        for entry in json.loads((CASE_DIR / "cases.json").read_text(encoding="utf-8"))["jobs"][0]["circuits"]:
            if entry["file"].startswith(f"circuits/{name}-"):
                loci = {q for op in circuit(Path(entry["file"]).stem)["instructions"] for q in op["locus"]}
                require(loci <= set(case.PATCH))
    require(set(pred["operands"]["s808"]["physical_qubits"]) <= set(pred["operands"]["s412"]["physical_qubits"]))


@pytest.mark.parametrize("operand", case.OPERANDS, ids=lambda op: op.name)
def test_emitted_circuits_have_the_ideal_block_law(operand: case.Operand) -> None:
    calibration = iqm_sim.Calibration.from_directory(CASE_DIR / "calibration")
    block = case.block_of(operand)
    for kind in operand.kinds:
        for orientation in ("plus", "minus"):
            native = circuit(f"{operand.name}-{kind}-{orientation}-00")
            law = native_law(native, calibration)
            ideal = pcx.block_law(block, 1 if kind == "real" else 1j, orientation == "plus", plain=kind == "plain")
            require(bool(np.allclose(law, ideal, atol=1e-8)))
            require(len(native["instructions"][-1]["locus"]) == block.d + 1)


def test_real_and_complex_circuits_differ_in_prx_phase_alone() -> None:
    for operand in case.OPERANDS:
        for orientation in ("plus", "minus"):
            a = circuit(f"{operand.name}-real-{orientation}-00")["instructions"]
            b = circuit(f"{operand.name}-cplx-{orientation}-00")["instructions"]
            require([(x["name"], x["locus"]) for x in a] == [(x["name"], x["locus"]) for x in b])
            prx = [(x, y) for x, y in zip(a, b, strict=True) if x["name"] == "prx"]
            require(all(x["args"]["angle"] == y["args"]["angle"] for x, y in prx))
            require(any(x["args"]["phase"] != y["args"]["phase"] for x, y in prx))
        plus = circuit(f"{operand.name}-real-plus-00")["instructions"]
        minus = circuit(f"{operand.name}-real-minus-00")["instructions"]
        require(all(x["args"].get("angle") == y["args"].get("angle") for x, y in zip(plus, minus, strict=True)))


def test_plain_kind_compiles_to_the_cz_count_of_the_real_kind() -> None:
    for name in ("s016", "s412"):
        cz = {kind: row["cz"] for kind, row in prediction()["operands"][name]["kinds"].items()}
        require(cz["plain"] == cz["real"] == cz["cplx"])


def test_mutation_changes_the_ideal_observable() -> None:
    ideal = {
        (op.name, kind): case.ideal_difference(case.block_of(op), kind) for op in case.OPERANDS for kind in op.kinds
    }
    require(abs(ideal["s016", "plain"] + 1) < 1e-9 and abs(ideal["s016", "cplx"] - 1) < 1e-9)
    require(abs(ideal["s412", "plain"] + 0.75) < 1e-9 and abs(ideal["s412", "cplx"] - 0.75) < 1e-9)
    require(abs(ideal["s016", "real"]) < 1e-9 and abs(ideal["s808", "cplx"] - ideal["s808", "real"]) < 1e-9)
    signs = {name: np.sign(ideal[name, "cplx"] - ideal[name, "real"]) for name in ("s016", "s412", "s124")}
    require(signs == {"s016": 1, "s412": 1, "s124": -1})


def test_frame_elimination_keeps_the_outcome_law() -> None:
    block = case.block_of(case.OPERANDS[1])
    compiled = case.structural_compile(block, False, (2, 3, 1, 0), case.TRANSPILER_SEEDS[0])
    for label in ("1", "i"):
        for plus in (True, False):
            bound = compiled.assign_parameters(
                {pcx.ORIENTATION: float(np.pi) if plus else 0.0, pcx.PHASE: pcx.ANGLES[label]}
            )
            kept = case.eliminate_frames(bound).remove_final_measurements(inplace=False)
            full = bound.remove_final_measurements(inplace=False)
            require(bool(np.allclose(Statevector(full).probabilities(), Statevector(kept).probabilities(), atol=1e-9)))


def test_device_that_follows_the_noise_model_reads_complex_strata() -> None:
    kept = prediction()["planning"]["kept_shots_per_orientation"]
    result = decision.analyze(counts_from(predicted_zero(), kept))
    require(result["verdict"] == "complex strata" and result["null_resolved"])
    for name, n_c in (("s016", 16.0), ("s412", 12.0), ("s124", 4.0)):
        require(abs(result["subtracted"][name]["n_c"] - n_c) < 0.3)


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


def test_null_subtraction_moves_every_reading_by_the_null_offset() -> None:
    estimates: dict[str, float | None] = {"ratio": 0.5, "se_ratio": 0.01}
    null: dict[str, float | None] = {"ratio": 0.1, "se_ratio": 0.02}
    n_c, se = decision.subtracted(estimates, null)
    if n_c is None or se is None:
        raise AssertionError
    require(abs(n_c - (8 + 8 * 0.4)) < 1e-12 and abs(se - 8 * math.hypot(0.01, 0.02)) < 1e-12)
    require(decision.subtracted(estimates, {"ratio": None, "se_ratio": None}) == (None, None))


def test_unresolved_null_visibility_blocks_the_complex_verdict() -> None:
    kept = prediction()["planning"]["kept_shots_per_orientation"]
    laws = predicted_zero()
    laws["s808"]["cplx"] = {"plus": 0.5, "minus": 0.5}
    laws["s808"]["real"] = {"plus": 0.5, "minus": 0.5}
    result = decision.analyze(counts_from(laws, kept))
    require(not result["null_resolved"] and result["verdict"] == "no reading")


def test_recorded_power_covers_every_condition_of_the_verdict() -> None:
    pred = prediction()
    z = pred["decision"]["z_predicted"]
    require(len(z) == len(decision.DISCRIMINATING) + len(decision.MUTATION_OPERANDS) + 1)
    require(abs(pred["decision"]["power_complex_truth"] - round(decision.power(z), 6)) < 1e-9)
    require(decision.power([5.0]) == pytest.approx(0.5))


def test_coherent_audit_covers_the_errors_and_no_error_reads_real_strata() -> None:
    audit = prediction()["coherent_audit"]
    expected = {"none", "alap"}
    expected |= {f"prx{e:+.2f}" for e in case.PRX_ERRORS} | {f"zz{e:+.2f}" for e in case.ZZ_ERRORS}
    require(set(audit["errors"]) == expected)
    require(all(row["verdict"] != "real strata" for row in audit["errors"].values()))
    require(audit["errors"]["none"]["verdict"] == "complex strata")
    within = audit["prx_amplitude_complex_strata_within"]
    require(
        all(audit["errors"][f"prx{e:+.2f}"]["verdict"] == "complex strata" for e in case.PRX_ERRORS if abs(e) <= within)
    )
    require(all(audit["errors"][f"zz{e:+.2f}"]["verdict"] == "complex strata" for e in case.ZZ_ERRORS))
