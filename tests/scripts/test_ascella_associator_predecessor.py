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


def test_schedule_quadratic_drift_cancellation() -> None:
    """Verify exact algebraic cancellation of constant, linear, and quadratic drift."""
    spec = case.PAIRED_SCHEDULE_SPEC
    if len(spec) != 16:
        raise AssertionError(f"expected 16 pairs, got {len(spec)}")

    # Check Block 1 (Associator, Pairs 0..7)
    b1 = spec[:8]
    b1_lalb = [int(str(row["pair"])) for row in b1 if row["route"] == "LaLb"]
    b1_lab = [int(str(row["pair"])) for row in b1 if row["route"] == "Lab"]
    if sum(b1_lalb) != sum(b1_lab):
        raise AssertionError("Block 1 linear drift on routes not cancelled")
    if sum(t**2 for t in b1_lalb) != sum(t**2 for t in b1_lab):
        raise AssertionError("Block 1 quadratic drift on routes not cancelled")

    # Check Block 2 (Control, Pairs 8..15)
    b2 = spec[8:]
    b2_lalb = [int(str(row["pair"])) for row in b2 if row["route"] == "LaLb"]
    b2_lab = [int(str(row["pair"])) for row in b2 if row["route"] == "Lab"]
    if sum(b2_lalb) != sum(b2_lab):
        raise AssertionError("Block 2 linear drift on routes not cancelled")
    if sum(t**2 for t in b2_lalb) != sum(t**2 for t in b2_lab):
        raise AssertionError("Block 2 quadratic drift on routes not cancelled")

    # Check that Cold baseline anchors occur at all odd indices
    cold_pairs = [int(str(row["pair"])) for row in spec if row["pred"] == "cold"]
    expected_anchors = [1, 3, 5, 7, 9, 11, 13, 15]
    if cold_pairs != expected_anchors:
        raise AssertionError(f"Cold anchors {cold_pairs} != {expected_anchors}")


def test_synthetic_nonlinear_drift_recovery() -> None:
    """Test that quadratic drift is annihilated from Delta and recovered from Cold anchors."""
    spec = case.PAIRED_SCHEDULE_SPEC

    # True parameters: Delta_oct = 1.647058 (LaLb = +0.823529, Lab = -0.823529)
    # Drift: f(t) = 0.05 + 0.01*t + 0.002*t^2
    def true_drift(t: float) -> float:
        return 0.05 + 0.01 * t + 0.002 * (t**2)

    d_obs: list[float] = []
    for row in spec:
        t = float(int(str(row["pair"])))
        route = str(row["route"])
        block = str(row["block"])
        sign = 1.0 if route == "LaLb" else -1.0
        signal = sign * 0.823529 if block == "associator" else -0.823529
        d_obs.append(signal + true_drift(t))

    # Evaluate raw difference between LaLb and Lab on Block 1
    b1_obs_lalb = [d_obs[int(str(r["pair"]))] for r in spec[:8] if r["route"] == "LaLb"]
    b1_obs_lab = [d_obs[int(str(r["pair"]))] for r in spec[:8] if r["route"] == "Lab"]
    measured_delta = np.mean(b1_obs_lalb) - np.mean(b1_obs_lab)

    # Must equal true Delta without any quadratic drift corruption
    if abs(measured_delta - (2 * 0.823529)) > 1e-12:
        raise AssertionError(f"quadratic drift corrupted raw Delta: {measured_delta} != {2 * 0.823529}")

    # Reconstruct drift polynomial from Cold anchors
    cold_anchors_t = np.array([int(str(r["pair"])) for r in spec if r["pred"] == "cold"], dtype=float)
    cold_y = np.array([d_obs[int(t)] for t in cold_anchors_t], dtype=float)
    anchor_residuals = np.array(
        [
            cold_y[i]
            - (
                (0.823529 if spec[int(t)]["route"] == "LaLb" else -0.823529)
                if spec[int(t)]["block"] == "associator"
                else -0.823529
            )
            for i, t in enumerate(cold_anchors_t)
        ]
    )
    poly = np.poly1d(np.polyfit(cold_anchors_t, anchor_residuals, deg=2))
    # Fitted coefficients must match [0.002, 0.01, 0.05]
    if abs(poly.coefficients[0] - 0.002) > 1e-6 or abs(poly.coefficients[1] - 0.01) > 1e-6:
        raise AssertionError(f"fitted drift polynomial incorrect: {poly.coefficients}")


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
    docs = case.build_documents(samples_per_iteration=8192, shots_factor=64)
    manifest = json.loads(docs["cases.json"].decode())
    shots_per_setting = 8192 * 64  # 524,288
    expected_credits = round(1.0 + 1e-6 * shots_per_setting, 6)
    if abs(manifest["credit_ceiling"] - expected_credits) > 1e-12:
        raise AssertionError(f"credit ceiling {manifest['credit_ceiling']} != {expected_credits}")
    if manifest["credit_ceiling"] != 1.524288:
        raise AssertionError(f"expected 1.524288 credits, got {manifest['credit_ceiling']}")


def test_end_to_end_simulation_and_analysis(tmp_path: Path) -> None:
    """Verify simulation and analysis produce correct verdicts and endpoints."""
    docs = case.build_documents(samples_per_iteration=8192, shots_factor=64)
    manifest = json.loads(docs["cases.json"].decode())
    circuit = json.loads(docs["circuit.json"].decode())
    _, settings = template_experiment(manifest, circuit)

    simulated_iterations = []
    for setting in settings:
        if setting["role"] == "predecessor":
            counts = {"|1,0,1,0,0,0,0,0,0,0,0,0>": 8192}
        else:
            law = setting["ideal"]["two_click_law_indistinguishable"]
            counts = {}
            for pair, prob in law.items():
                state_vec = [0] * case.MODES
                state_vec[int(pair[0])] = 1
                state_vec[int(pair[1])] = 1
                counts[f"|{','.join(str(v) for v in state_vec)}>"] = int(round(prob * 8192))
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
    if verdicts["quadratic_drift_annihilation"] is not True:
        raise AssertionError(f"quadratic drift annihilation flag not true: {verdicts}")
