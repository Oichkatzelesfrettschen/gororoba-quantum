"""Contracts and verification of the Ascella associator predecessor and sentinel benchmark."""

from __future__ import annotations

import json
import math
from pathlib import Path

import ascella_associator_predecessor as case
import numpy as np
from qd_platform import template_experiment


def test_check_passes() -> None:
    if case.check() != 0:
        raise AssertionError("case.check() failed")


def test_optical_phase_wrapping_identity() -> None:
    """Wave-optics identity: U(2*pi) == U(0) on all modes."""
    circuit = case.build_template_circuit()
    u_cold = case.compute_template_unitary(
        circuit["ops"],
        {f"x{k}": 0.0 for k in range(circuit["parameters"])},
    )
    u_wrapped = case.compute_template_unitary(
        circuit["ops"],
        {f"x{k}": (0.0 if circuit["ops"][k][0] == "BS" else 2 * math.pi) for k in range(circuit["parameters"])},
    )
    diff = float(np.max(np.abs(u_cold - u_wrapped)))
    if diff >= case.TOLERANCE:
        raise AssertionError(f"optical phase wrapping difference {diff} >= {case.TOLERANCE}")


def test_ideal_associator_and_control_contrast() -> None:
    """Octonion associator yields Delta = 2.0 (indistinguishable) and 0.0 (distinguishable).

    Quaternion control yields Delta = 0.0 identically for both.
    """
    u_oct_lalb = case.route_operator("associator", "LaLb")
    u_oct_lab = case.route_operator("associator", "Lab")

    # Indistinguishable (V = 1.0)
    d_oct_lalb_indist = case.endpoint_d(case.two_click_law(u_oct_lalb, 1.0))
    d_oct_lab_indist = case.endpoint_d(case.two_click_law(u_oct_lab, 1.0))
    delta_oct_indist = d_oct_lalb_indist - d_oct_lab_indist
    if abs(delta_oct_indist - 2.0) > case.BODY_TOLERANCE:
        raise AssertionError(f"ideal indistinguishable Octonion Delta {delta_oct_indist} != 2.0")

    # Distinguishable (V = 0.0)
    d_oct_lalb_dist = case.endpoint_d(case.two_click_law(u_oct_lalb, 0.0))
    d_oct_lab_dist = case.endpoint_d(case.two_click_law(u_oct_lab, 0.0))
    delta_oct_dist = d_oct_lalb_dist - d_oct_lab_dist
    if abs(delta_oct_dist) > case.BODY_TOLERANCE:
        raise AssertionError(f"ideal distinguishable Octonion Delta {delta_oct_dist} != 0.0")

    # Quaternion control (V = 1.0)
    u_quat_lalb = case.route_operator("control", "LaLb")
    u_quat_lab = case.route_operator("control", "Lab")
    delta_quat = case.endpoint_d(case.two_click_law(u_quat_lalb, 1.0)) - case.endpoint_d(
        case.two_click_law(u_quat_lab, 1.0)
    )
    if abs(delta_quat) > case.BODY_TOLERANCE:
        raise AssertionError(f"ideal Quaternion control Delta {delta_quat} != 0.0")


def test_in_situ_closure_identity() -> None:
    """In-situ closure C = Delta_oct + 2 * mean(D_control) == 0.0 holds at every visibility."""
    u_oct_lalb = case.route_operator("associator", "LaLb")
    u_oct_lab = case.route_operator("associator", "Lab")
    u_quat_lalb = case.route_operator("control", "LaLb")
    u_quat_lab = case.route_operator("control", "Lab")

    for v in (0.0, 0.25, 0.5, 0.875, 1.0):
        d_oct_lalb = case.endpoint_d(case.two_click_law(u_oct_lalb, v))
        d_oct_lab = case.endpoint_d(case.two_click_law(u_oct_lab, v))
        delta_oct = d_oct_lalb - d_oct_lab

        d_quat_lalb = case.endpoint_d(case.two_click_law(u_quat_lalb, v))
        d_quat_lab = case.endpoint_d(case.two_click_law(u_quat_lab, v))
        mean_d_quat = (d_quat_lalb + d_quat_lab) / 2

        closure = delta_oct + 2 * mean_d_quat
        if abs(closure) > 1e-9:
            raise AssertionError(f"in-situ closure failed at V = {v}: C = {closure}")


def test_schedule_balance_and_drift_cancellation() -> None:
    """Verify counterbalanced schedule structure and linear drift cancellation."""
    spec = case.PAIRED_SCHEDULE_SPEC
    if len(spec) != 16:
        raise AssertionError(f"expected 16 pairs, got {len(spec)}")

    # Check Block 1 (Associator, Hot vs Cold): ABBA on predecessors
    block1_hot_indices = [int(str(row["pair"])) for row in spec[:4] if row["pred"] == "hot"]
    block1_cold_indices = [int(str(row["pair"])) for row in spec[:4] if row["pred"] == "cold"]
    if sum(block1_hot_indices) / len(block1_hot_indices) != sum(block1_cold_indices) / len(block1_cold_indices):
        raise AssertionError("Block 1 predecessor mean indices do not balance")

    # Check Block 2 (Associator, Wrapped vs Cold): AWWA on predecessors
    block2_wrapped = [int(str(row["pair"])) for row in spec[4:8] if row["pred"] == "wrapped"]
    block2_cold = [int(str(row["pair"])) for row in spec[4:8] if row["pred"] == "cold"]
    if sum(block2_wrapped) / len(block2_wrapped) != sum(block2_cold) / len(block2_cold):
        raise AssertionError("Block 2 predecessor mean indices do not balance")

    # Check that under the Cold baseline across Blocks 1 & 2, LaLb and Lab have matching mean pair indices
    cold_associator = [row for row in spec[:8] if row["pred"] == "cold"]
    lalb_pairs = [int(str(row["pair"])) for row in cold_associator if row["route"] == "LaLb"]
    lab_pairs = [int(str(row["pair"])) for row in cold_associator if row["route"] == "Lab"]
    mean_lalb = sum(lalb_pairs) / len(lalb_pairs)
    mean_lab = sum(lab_pairs) / len(lab_pairs)
    if abs(mean_lalb - mean_lab) > 1e-12:
        raise AssertionError(f"Cold baseline associator targets not balanced: LaLb {mean_lalb} != Lab {mean_lab}")


def test_template_experiment_binding() -> None:
    """Verify that all 32 settings bind natively into qd_platform.template_experiment."""
    docs = case.build_documents()
    manifest = json.loads(docs["cases.json"].decode())
    circuit = json.loads(docs["circuit.json"].decode())
    experiment, settings = template_experiment(manifest, circuit)
    if experiment is None or len(settings) != 32:
        raise AssertionError(f"template_experiment failed to bind 32 settings: {len(settings)}")


def test_credit_ceiling_rule() -> None:
    """Verify credit billing rule: 1 + 10^-6 * max_shots_per_setting."""
    docs = case.build_documents()
    manifest = json.loads(docs["cases.json"].decode())
    shots_per_setting = case.SHOTS_PER_ITERATION
    expected_credits = 1.0 + 1e-6 * shots_per_setting
    if abs(manifest["credit_ceiling"] - expected_credits) > 1e-12:
        raise AssertionError(f"credit ceiling {manifest['credit_ceiling']} != {expected_credits}")


def test_end_to_end_simulation_and_analysis(tmp_path: Path) -> None:
    """Verify simulation and analysis produce correct verdicts and endpoints."""
    docs = case.build_documents()
    manifest = json.loads(docs["cases.json"].decode())
    circuit = json.loads(docs["circuit.json"].decode())
    _, settings = template_experiment(manifest, circuit)

    simulated_iterations = []
    for setting in settings:
        if setting["role"] == "predecessor":
            counts = {"|1,0,1,0,0,0,0,0,0,0,0,0>": case.SAMPLES_PER_ITERATION}
        else:
            law = setting["ideal"]["two_click_law_indistinguishable"]
            counts = {}
            for pair, prob in law.items():
                state_vec = [0] * case.MODES
                state_vec[int(pair[0])] = 1
                state_vec[int(pair[1])] = 1
                counts[f"|{','.join(str(v) for v in state_vec)}>"] = int(round(prob * case.SAMPLES_PER_ITERATION))
        simulated_iterations.append({"setting": setting["name"], "counts": counts})

    (tmp_path / "cases.json").write_bytes(docs["cases.json"])
    (tmp_path / "results.json").write_text(json.dumps({"iterations": simulated_iterations}))

    report = case.analyze(tmp_path)
    verdicts = report["verdicts"]

    if verdicts["associator_signal_detected"] is not True:
        raise AssertionError(f"associator signal not detected: {report}")
    if verdicts["quaternion_null_admitted"] is not True:
        raise AssertionError(f"quaternion null not admitted: {report}")
    if verdicts["closure_admitted"] is not True:
        raise AssertionError(f"closure not admitted: {report}")
    if abs(verdicts["predecessor_shift_hot_vs_cold"]) > 1e-9:
        raise AssertionError(f"ideal predecessor shift hot != 0: {verdicts}")
    if abs(verdicts["predecessor_shift_wrapped_vs_cold"]) > 1e-9:
        raise AssertionError(f"ideal predecessor shift wrapped != 0: {verdicts}")
