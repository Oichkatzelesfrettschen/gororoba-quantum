"""A_5 complex kernel case on Garnet: builder, manifest, circuits, audit and the preregistered estimators."""

from __future__ import annotations

import cmath
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
import pathion_coset_block as pcb

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


def phase_zero(phase: float) -> dict[str, dict[str, dict[str, float]]]:
    """Exact selector-zero frequencies of every kind when the complex circuit carries the phase e^(i phase) in place of
    i (the real and sentinel kinds carry 1, the plain kind the mutated sign table at t = i)."""
    zero: dict[str, dict[str, dict[str, float]]] = {}
    for operand in case.OPERANDS:
        block = case.block_of(operand)
        kinds: dict[str, dict[str, float]] = {}
        for kind in operand.kinds:
            t = {"cplx": cmath.exp(1j * phase), "plain": 1j}.get(kind, 1)
            kinds[kind] = {
                o: float(pcx.block_law(block, t, o == "plus", plain=kind == "plain")[: 1 << block.d].sum())
                for o in ("plus", "minus")
            }
        zero[operand.name] = kinds
    return zero


@pytest.mark.parametrize("degrees", [30, 45, 135])
def test_a_wrong_phase_does_not_read_complex_strata(degrees: int) -> None:
    result = decision.analyze(counts_from(phase_zero(math.radians(degrees)), 14000))
    require("complex strata" not in result["verdict"])


def test_the_exact_quarter_turn_reads_complex_strata() -> None:
    result = decision.analyze(counts_from(phase_zero(math.pi / 2), 14000))
    require(result["verdict"].startswith("complex strata"))


def test_a_faint_s016_visibility_does_not_read_complex_strata() -> None:
    laws = phase_zero(math.pi / 2)
    laws["s016"]["cplx"] = {"plus": 0.54, "minus": 0.46}
    laws["s016"]["real"] = {"plus": 0.5, "minus": 0.5}
    if "plain" in laws["s016"]:
        laws["s016"]["plain"] = {"plus": 0.46, "minus": 0.54}
    result = decision.analyze(counts_from(laws, 14000))
    require("complex strata" not in result["verdict"])


def test_a_dead_mutation_control_does_not_pass() -> None:
    laws = phase_zero(math.pi / 2)
    for operand in case.OPERANDS:
        if "plain" in operand.kinds:
            laws[operand.name]["plain"] = {"plus": 1.0, "minus": 1.0}
    result = decision.analyze(counts_from(laws, 14000))
    require("complex strata" not in result["verdict"])
    for mutation in result["mutations"].values():
        require(mutation is None or mutation["z_below_zero"] < decision.Z_RESOLVE)


def plain_gap(block: Any) -> float:
    """Largest outcome-law distance between the plain kind and the complex kind with the orientations swapped."""
    return max(
        float(np.max(np.abs(pcx.block_law(block, 1j, plus, plain=True) - pcx.block_law(block, 1j, not plus))))
        for plus in (True, False)
    )


def test_plain_differs_from_orientation_swapped_complex_at_the_chosen_coset() -> None:
    carriers = [op for op in case.OPERANDS if "plain" in op.kinds]
    require([op.name for op in carriers] == ["s412"])
    for operand in carriers:
        block = case.block_of(operand)
        require(plain_gap(block) >= 0.1)
        require(case.ideal_difference(block, "plain") < 0 < case.ideal_difference(block, "cplx"))


def test_a_pair_with_one_sign_cannot_carry_a_mutation() -> None:
    operand = case.operand_named("s016")
    require("plain" not in operand.kinds)
    basis = pcx.normalized_basis((1, 3, 1), operand.basis)
    for coset in pcb.cosets(basis):
        block = pcb.Block("s016", (1, 3, 1), basis, coset)
        flips = pcx.selector_marginal(block, 1j, plain=True) < -1e-9
        require(not (flips and plain_gap(block) >= case.PLAIN_GAP_MIN))


def test_modeled_survives_an_unused_qubit_without_readout_fields(tmp_path: Path) -> None:
    folder = tmp_path / "calibration"
    folder.mkdir()
    for name in ("metrics.json", "dynamic-quantum-architecture.json"):
        (folder / name).write_bytes((CASE_DIR / "calibration" / name).read_bytes())
    metrics = json.loads((folder / "metrics.json").read_text(encoding="utf-8"))
    pred = prediction()
    unused = next(q for q in iqm_sim.Calibration.from_directory(folder).qubits if q not in pred["patch"])
    metrics["observations"] = [o for o in metrics["observations"] if f".{unused}." not in o["dut_field"]]
    (folder / "metrics.json").write_text(json.dumps(metrics), encoding="utf-8")
    calibration = iqm_sim.Calibration.from_directory(folder)
    modeled = case.modeled(calibration)
    require(modeled.set_id == calibration.set_id)


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
    require(len(job["circuits"]) * job["shots"] <= case.MAX_EXECUTIONS and job["shots"] == pred["shots"] == case.SHOTS)
    require(job["max_credits"] == {"garnet:mock": 0.0, "garnet": case.CEILING_CREDITS})
    require(case.CEILING_CREDITS <= case.OWNER_BOUND_CREDITS)
    require(job["options"]["heralding_mode"] == "zeros" and job["options"]["active_reset_cycles"] == 1)
    require(manifest["prediction_sha256"] == case.sha256((CASE_DIR / "prediction.json").read_bytes()))
    for entry in job["circuits"]:
        require(case.sha256((CASE_DIR / entry["file"]).read_bytes()) == entry["sha256"])
    margins = pred["cost"]["overrun_margins"]
    require(all(margins[k]["covered"] for k in ("1x", "1.5x", "2.2x")))
    require(margins["2.2x"]["margin_seconds"] >= case.OVERRUN_MARGIN_MIN_SECONDS)
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
    patch = set(pred["patch"])
    require(pred["patch"] == pred["star"]["ranking"][0]["patch"] and pred["star"]["chosen_rank"] == 1)
    for name, operand in pred["operands"].items():
        require(set(operand["physical_qubits"]) <= patch)
        for entry in json.loads((CASE_DIR / "cases.json").read_text(encoding="utf-8"))["jobs"][0]["circuits"]:
            if entry["file"].startswith(f"circuits/{name}-"):
                loci = {q for op in circuit(Path(entry["file"]).stem)["instructions"] for q in op["locus"]}
                require(loci <= patch)
    require(set(pred["operands"]["s808"]["physical_qubits"]) <= set(pred["operands"]["s412"]["physical_qubits"]))


@pytest.mark.parametrize("operand", case.OPERANDS, ids=lambda op: op.name)
def test_emitted_circuits_have_the_ideal_block_law(operand: case.Operand) -> None:
    calibration = iqm_sim.Calibration.from_directory(CASE_DIR / "calibration")
    block = case.block_of(operand)
    for kind in operand.kinds:
        for orientation in ("plus", "minus"):
            native = circuit(f"{operand.name}-{kind}-{orientation}-00")
            law = native_law(native, calibration)
            ideal = pcx.block_law(
                block, 1 if kind in ("real", "sent") else 1j, orientation == "plus", plain=kind == "plain"
            )
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


def test_the_sentinel_is_the_real_circuit_again() -> None:
    for orientation in ("plus", "minus"):
        a = circuit(f"s808-real-{orientation}-00")["instructions"]
        b = circuit(f"s808-sent-{orientation}-00")["instructions"]
        require(a == b)
    kinds = prediction()["operands"]["s808"]["kinds"]
    require(kinds["sent"]["predicted_zero"] == kinds["real"]["predicted_zero"])


def test_the_null_pair_sits_at_the_outer_end_the_sentinel_at_the_center_and_s124_between() -> None:
    names = prediction()["order"]
    centre = (len(names) - 1) / 2

    def distance(prefix: str) -> list[float]:
        return [abs(i - centre) for i, n in enumerate(names) if n.startswith(prefix)]

    require(min(distance("s808-real")) > 30 and min(distance("s808-cplx")) > 26)
    require(max(distance("s808-sent")) < 5)
    require(min(distance("s124-cplx")) >= 16)


def test_mutation_changes_the_ideal_observable() -> None:
    ideal = {
        (op.name, kind): case.ideal_difference(case.block_of(op), kind) for op in case.OPERANDS for kind in op.kinds
    }
    require(abs(ideal["s412", "plain"] + 0.75) < 1e-9 and abs(ideal["s412", "cplx"] - 0.75) < 1e-9)
    require(abs(ideal["s808", "sent"] - ideal["s808", "real"]) < 1e-9)
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
    require(result["verdict"] == "complex strata within tolerance" and result["null_resolved"])
    require(all(result["controls"].values()) and abs(result["drift_z"]) < 1e-9)
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
    laws["s412"]["cplx"] = laws["s412"]["plain"]
    result = decision.analyze(counts_from(laws, kept))
    require("complex strata" not in result["verdict"] and result["sides"]["s412"] != "complex-side")


def test_swapped_kinds_read_real_strata() -> None:
    kept = prediction()["planning"]["kept_shots_per_orientation"]
    laws = predicted_zero()
    for kinds in laws.values():
        kinds["cplx"], kinds["real"] = kinds["real"], kinds["cplx"]
    require(decision.analyze(counts_from(laws, kept))["verdict"] == "real strata within tolerance")


def test_failed_mutation_control_blocks_the_complex_verdict() -> None:
    kept = prediction()["planning"]["kept_shots_per_orientation"]
    laws = predicted_zero()
    laws["s412"]["plain"] = laws["s412"]["cplx"]
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


def test_recorded_power_is_the_joint_rule_over_the_predicted_counts() -> None:
    pred = prediction()
    kept = pred["planning"]["kept_shots_per_orientation"]
    z = pred["decision"]["z_predicted"]
    require(len(z) == len(decision.DISCRIMINATING) + len(decision.MUTATION_OPERANDS) + 2)
    counts = counts_from(predicted_zero(), kept)
    require(abs(pred["decision"]["power_complex_truth"] - round(decision.simulated_power(counts), 3)) < 1e-9)
    # Near threshold the joint rule is far from the product of independent normals: at 500 kept shots the shared null
    # and visibilities leave a power strictly between 0 and 1, and the quadrature repeats bit for bit.
    thin = counts_from(predicted_zero(), 500)
    power = decision.simulated_power(thin)
    require(0.0 < power < 1.0 and power == decision.simulated_power(thin))


def test_the_rule_constants_are_the_preregistered_numbers() -> None:
    rule = prediction()["decision"]["rule"]
    require(rule["n_tolerance"] == 2.0 and rule["v_s016_min"] == 0.5 and rule["r_null_max"] == 0.08)
    require(rule["drift_z_max"] == 5.0 and rule["z_resolve"] == 5.0)
    require(rule["source_sha256"] == case.sha256(Path(decision.__file__).read_bytes()))


def test_coherent_audit_covers_every_family_and_no_row_reads_real_strata() -> None:
    pred = prediction()
    audit = pred["coherent_audit"]
    labels = {label for label, _, _, _ in case.audit_errors(tuple(pred["patch"]))}
    require(set(audit["errors"]) == labels)
    require(any(label.startswith("prx") and "@" in label for label in labels))
    require({"cphase-0.05", "zres-0.05", "combined-1x", "combined+1x", "zz+0.05", "alap"} <= labels)
    require(all(row["verdict"] != "real strata within tolerance" for row in audit["errors"].values()))
    require(audit["errors"]["none"]["verdict"] == "complex strata within tolerance")
    bounds = audit["complex_strata_within"]
    require(set(bounds) == {"prx", "qubit_prx", "zz", "cphase", "zres", "combined", "combined_opposite"})
    for label, family, magnitude, _ in case.audit_errors(tuple(pred["patch"])):
        if family in bounds and magnitude <= bounds[family]:
            require(audit["errors"][label]["verdict"] == "complex strata within tolerance")


def test_every_audited_error_changes_the_circuit_it_acts_on() -> None:
    calibration = iqm_sim.Calibration.from_directory(CASE_DIR / "calibration")
    patch = tuple(prediction()["patch"])
    operand = case.operand_named("s124")
    block = case.block_of(operand)
    compiled = case.structural_compile(block, False, (2, 3, 1, 0), case.TRANSPILER_SEEDS[0])
    bound = case.bind(compiled, "i", True)
    base = case.exact_law(bound, calibration, patch)
    for error in (
        {"prx_scale": 0.03},
        {"prx_scale": {patch[2]: 0.05}},
        {"zz": 0.05},
        {"cphase": 0.1},
        {"zres": 0.1},
    ):
        require(float(np.max(np.abs(case.exact_law(bound, calibration, patch, errors=error) - base))) > 1e-4)


def test_the_star_rule_ranks_every_usable_star_with_total_tie_breaks() -> None:
    calibration = iqm_sim.Calibration.from_directory(case.RETAINED_CALIBRATION)
    linearity, _ = case.parallel_train_linearity()
    ranking = case.rank_stars(calibration, linearity)
    patches = [tuple(row["patch"]) for row in ranking]
    require(len(set(patches)) == len(patches) == 32)
    require(ranking == case.rank_stars(calibration, linearity))
    require(patches[0] == ("QB14", "QB4", "QB9", "QB8"))
    require(ranking[0]["nonlinear_train_qubits"] == 0 and ranking[0]["cz_product"] > 0.992)
    by_product = sorted(ranking, key=lambda row: -row["cz_product"])
    prior = [tuple(row["patch"]) for row in by_product].index(case.PRIOR_STAR) + 1
    require(prior == 22)


def test_the_star_rule_demotes_a_star_with_a_non_linear_train() -> None:
    calibration = iqm_sim.Calibration.from_directory(case.RETAINED_CALIBRATION)
    linearity, _ = case.parallel_train_linearity()
    best = case.rank_stars(calibration, linearity)[0]["patch"]
    spoiled = case.rank_stars(calibration, {**linearity, best[2]: False})
    require(next(row for row in spoiled if row["patch"] == best)["nonlinear_train_qubits"] == 1)
    counts = [row["nonlinear_train_qubits"] for row in spoiled]
    require(counts == sorted(counts))


def test_the_sentinel_drift_check_fires_on_a_symmetric_dip_that_the_halves_miss() -> None:
    kept = prediction()["planning"]["kept_shots_per_orientation"]
    laws = predicted_zero()
    for orientation in ("plus", "minus"):
        z = laws["s808"]["sent"][orientation]
        laws["s808"]["sent"][orientation] = 0.5 + 0.7 * (z - 0.5)
    result = decision.analyze(counts_from(laws, kept))
    require(abs(result["drift_z"]) >= decision.DRIFT_Z_MAX)
    require(result["verdict"] == "complex side, a control fails" and not result["controls"]["drift"])
