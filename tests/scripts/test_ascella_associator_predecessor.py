"""Contracts and verification of the Ascella associator predecessor and sentinel benchmark."""

from __future__ import annotations

import copy
import json
import math
from pathlib import Path

import ascella_associator_predecessor as case
import numpy as np
import pytest
from qd_platform import PlatformError, template_experiment


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
    """Test that quadratic drift contaminates naive carryover but is annihilated by the Joint WLS Model."""
    spec = case.PAIRED_SCHEDULE_SPEC

    # True parameters: Delta_oct = 1.647058 (LaLb = +0.823529, Lab = -0.823529)
    # Strong drift: f(t) = 0.05 + 0.15*(t/15) + 0.08*(t/15)^2
    target_records = []
    d_obs_list = []
    for row in spec:
        p_idx = int(str(row["pair"]))
        t_norm = float(p_idx) / 15.0
        route = str(row["route"])
        block = str(row["block"])
        pred = str(row["pred"])
        sign = 1.0 if route == "LaLb" else -1.0
        signal = sign * 0.823529 if block == "associator" else -0.823529
        drift_val = 0.05 + 0.15 * t_norm + 0.08 * (t_norm**2)
        obs_val = signal + drift_val
        d_obs_list.append(obs_val)
        target_records.append(
            {
                "pair_index": p_idx,
                "block": block,
                "pred": pred,
                "route": route,
                "d_observable": obs_val,
                "focal_samples": 8192,
                "time": t_norm,
            }
        )

    # 1. Show naive estimator contamination
    # In Block 1 (Associator): Hot has Lab at pair 0 and LaLb at pair 4
    naive_delta_hot = d_obs_list[4] - d_obs_list[0]
    # Cold has LaLb at {1, 7} and Lab at {3, 5}
    naive_delta_cold = ((d_obs_list[1] + d_obs_list[7]) / 2.0) - ((d_obs_list[3] + d_obs_list[5]) / 2.0)
    naive_hot_carryover = naive_delta_hot - naive_delta_cold

    # Naive carryover is contaminated by 4*beta1 + 8*beta2 = 0.042844 != 0
    if abs(naive_hot_carryover) < 0.02:
        raise AssertionError(f"expected naive carryover to be drift-contaminated, got {naive_hot_carryover}")

    # 2. Joint WLS model eliminates quadratic drift to machine precision
    joint = case.fit_joint_model(target_records, drift_degree=2)
    gamma_hot_est = joint["coefficients"]["gamma_hot"]["estimate"]
    gamma_wrapped_est = joint["coefficients"]["gamma_wrapped"]["estimate"]
    delta_assoc_est = joint["coefficients"]["delta_assoc"]["estimate"]

    if abs(gamma_hot_est) > 1e-10:
        raise AssertionError(f"joint model failed to eliminate drift from gamma_hot: {gamma_hot_est}")
    if abs(gamma_wrapped_est) > 1e-10:
        raise AssertionError(f"joint model failed to eliminate drift from gamma_wrapped: {gamma_wrapped_est}")
    if abs(delta_assoc_est - (2 * 0.823529)) > 1e-10:
        raise AssertionError(f"joint model failed to recover true Delta_assoc: {delta_assoc_est}")


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
    # Test explicit shots_factor=64
    docs64 = case.build_documents(samples_per_iteration=8192, shots_factor=64)
    manifest64 = json.loads(docs64["cases.json"].decode())
    shots_per_setting_64 = 8192 * 64  # 524,288
    expected_credits_64 = round(1.0 + 1e-6 * shots_per_setting_64, 6)
    if abs(manifest64["credit_ceiling"] - expected_credits_64) > 1e-12:
        raise AssertionError(f"credit ceiling {manifest64['credit_ceiling']} != {expected_credits_64}")
    if manifest64["credit_ceiling"] != 1.524288:
        raise AssertionError(f"expected 1.524288 credits, got {manifest64['credit_ceiling']}")

    # Test default shots_factor=80 (satisfies Perceval physical threshold on 5.37% transmittance)
    docs80 = case.build_documents(samples_per_iteration=8192)
    manifest80 = json.loads(docs80["cases.json"].decode())
    shots_per_setting_80 = 8192 * 80  # 655,360
    expected_credits_80 = round(1.0 + 1e-6 * shots_per_setting_80, 6)
    if abs(manifest80["credit_ceiling"] - expected_credits_80) > 1e-12:
        raise AssertionError(f"credit ceiling {manifest80['credit_ceiling']} != {expected_credits_80}")
    if manifest80["credit_ceiling"] != 1.65536:
        raise AssertionError(f"expected 1.65536 credits, got {manifest80['credit_ceiling']}")


def test_end_to_end_simulation_and_analysis(tmp_path: Path) -> None:
    """Verify simulation and analysis produce correct verdicts and endpoints under Joint WLS."""
    docs = case.build_documents(samples_per_iteration=8192, shots_factor=64)
    manifest = json.loads(docs["cases.json"].decode())
    circuit = json.loads(docs["circuit.json"].decode())
    _, settings = template_experiment(manifest, circuit)

    simulated_iterations = []
    for idx, setting in enumerate(settings):
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
        simulated_iterations.append(
            {
                "setting": setting["name"],
                "counts": counts,
                "elapsed_seconds": round(idx * 3.2, 2),
                "duration": 3.2,
            }
        )

    (tmp_path / "cases.json").write_bytes(docs["cases.json"])
    (tmp_path / "results.json").write_text(json.dumps({"iterations": simulated_iterations}))

    report = case.analyze(tmp_path)
    verdicts = report["verdicts"]

    if verdicts["execution_status"] != "ADMITTED":
        raise AssertionError(f"execution status not ADMITTED: {verdicts}")
    if verdicts["associator_signal_detected"] is not True:
        raise AssertionError(f"associator signal not detected: {report}")
    if verdicts["quaternion_null_admitted"] is not True:
        raise AssertionError(f"quaternion null not admitted: {report}")
    if verdicts["closure_admitted"] is not True:
        raise AssertionError(f"closure not admitted: {report}")
    if verdicts["predecessor_carryover_hot"] != "EQUIVALENT":
        raise AssertionError(f"predecessor carryover hot != EQUIVALENT: {verdicts}")
    if verdicts["predecessor_carryover_wrapped"] != "EQUIVALENT":
        raise AssertionError(f"predecessor carryover wrapped != EQUIVALENT: {verdicts}")


def test_adversarial_exponential_relaxation_drift() -> None:
    """Adversarial test: non-polynomial exponential drift f(t) = A * exp(-t / tau)."""
    spec = case.PAIRED_SCHEDULE_SPEC
    target_records = []
    for row in spec:
        p_idx = int(str(row["pair"]))
        t_norm = float(p_idx) / 15.0
        route = str(row["route"])
        block = str(row["block"])
        pred = str(row["pred"])
        sign = 1.0 if route == "LaLb" else -1.0
        signal = sign * 0.823529 if block == "associator" else -0.823529
        # Exponential relaxation with tau = 0.5 (relative to normalized time 1.0)
        drift_val = 0.08 * math.exp(-t_norm / 0.5)
        target_records.append(
            {
                "pair_index": p_idx,
                "block": block,
                "pred": pred,
                "route": route,
                "d_observable": signal + drift_val,
                "focal_samples": 8192,
                "time": t_norm,
            }
        )
    joint = case.fit_joint_model(target_records, drift_degree=2)
    gamma_hot = joint["coefficients"]["gamma_hot"]["estimate"]
    gamma_wrapped = joint["coefficients"]["gamma_wrapped"]["estimate"]
    # Model absorbs smooth relaxation without reporting spurious large carryover
    if abs(gamma_hot) > 0.015:
        raise AssertionError(f"exponential drift induced spurious carryover: gamma_hot = {gamma_hot}")
    if abs(gamma_wrapped) > 0.015:
        raise AssertionError(f"exponential drift induced spurious carryover: gamma_wrapped = {gamma_wrapped}")


def test_adversarial_cubic_drift() -> None:
    """Adversarial test: cubic drift f(t) = beta3 * t^3 handled via drift_degree=3."""
    spec = case.PAIRED_SCHEDULE_SPEC
    target_records = []
    for row in spec:
        p_idx = int(str(row["pair"]))
        t_norm = float(p_idx) / 15.0
        route = str(row["route"])
        block = str(row["block"])
        pred = str(row["pred"])
        sign = 1.0 if route == "LaLb" else -1.0
        signal = sign * 0.823529 if block == "associator" else -0.823529
        drift_val = 0.05 * (t_norm**3)
        target_records.append(
            {
                "pair_index": p_idx,
                "block": block,
                "pred": pred,
                "route": route,
                "d_observable": signal + drift_val,
                "focal_samples": 8192,
                "time": t_norm,
            }
        )
    joint3 = case.fit_joint_model(target_records, drift_degree=3)
    gamma_hot = joint3["coefficients"]["gamma_hot"]["estimate"]
    if abs(gamma_hot) > 1e-10:
        raise AssertionError(f"degree-3 model failed to cancel cubic drift: {gamma_hot}")


def test_adversarial_abrupt_step_change_quarantine(tmp_path: Path) -> None:
    """Adversarial test: sudden laser drop / alignment shock at observation 8 triggers quarantine."""
    docs = case.build_documents()
    manifest = json.loads(docs["cases.json"].decode())
    circuit = json.loads(docs["circuit.json"].decode())
    _, settings = template_experiment(manifest, circuit)

    simulated_iterations = []
    for idx, setting in enumerate(settings):
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
            if idx == 17:
                # Sudden optical misalignment / phase shock at iteration 17
                plus_state = "|1,0,0,1,0,0,0,0,0,0,0,0>"
                counts[plus_state] = counts.get(plus_state, 0) + 1500
        simulated_iterations.append({"setting": setting["name"], "counts": counts})

    (tmp_path / "cases.json").write_bytes(docs["cases.json"])
    (tmp_path / "results.json").write_text(json.dumps({"iterations": simulated_iterations}))

    report = case.analyze(tmp_path)
    if report["status"] != "QUARANTINED_ABRUPT_STEP":
        raise AssertionError(f"abrupt step change not quarantined: {report['status']}")
    if report["joint_model"]["step_change_diagnostic"]["abrupt_step_detected"] is not True:
        raise AssertionError("abrupt_step_detected flag was False")


def test_adversarial_unequal_focal_yields() -> None:
    """Adversarial test: varying focal sample yields across iterations do not bias WLS carryover."""
    spec = case.PAIRED_SCHEDULE_SPEC
    target_records = []
    # Unequal focal counts: odd pairs have 2,000, even pairs have 10,000
    for row in spec:
        p_idx = int(str(row["pair"]))
        t_norm = float(p_idx) / 15.0
        route = str(row["route"])
        block = str(row["block"])
        pred = str(row["pred"])
        sign = 1.0 if route == "LaLb" else -1.0
        signal = sign * 0.823529 if block == "associator" else -0.823529
        focal_n = 2000 if (p_idx % 2 == 1) else 10000
        drift_val = 0.03 * t_norm + 0.02 * (t_norm**2)
        target_records.append(
            {
                "pair_index": p_idx,
                "block": block,
                "pred": pred,
                "route": route,
                "d_observable": signal + drift_val,
                "focal_samples": focal_n,
                "time": t_norm,
            }
        )
    joint = case.fit_joint_model(target_records, drift_degree=2)
    gamma_hot = joint["coefficients"]["gamma_hot"]["estimate"]
    gamma_wrapped = joint["coefficients"]["gamma_wrapped"]["estimate"]
    if abs(gamma_hot) > 1e-10 or abs(gamma_wrapped) > 1e-10:
        raise AssertionError(f"WLS joint model biased by unequal focal yields: {gamma_hot}, {gamma_wrapped}")


def test_adversarial_incomplete_and_truncated_results(tmp_path: Path) -> None:
    """Adversarial test: fail-closed rejection of missing, truncated, or reordered settings."""
    docs = case.build_documents()
    (tmp_path / "cases.json").write_bytes(docs["cases.json"])

    # 1. Truncated iterations (only 16 instead of 32)
    truncated_results = {"iterations": [{"setting": "pair00-pred_hot", "counts": {"|1,0,1,0,0,0,0,0,0,0,0,0>": 1000}}]}
    (tmp_path / "results.json").write_text(json.dumps(truncated_results))
    with pytest.raises(ValueError, match="iteration count mismatch"):
        case.analyze(tmp_path)

    # 2. Reordered / mismatched setting names
    manifest = json.loads(docs["cases.json"].decode())
    bad_settings = copy.deepcopy(manifest["settings"])
    bad_settings.reverse()
    bad_iter = [{"setting": s["name"], "counts": {"|1,0,1,0,0,0,0,0,0,0,0,0>": 1000}} for s in bad_settings]
    (tmp_path / "results.json").write_text(json.dumps({"iterations": bad_iter}))
    with pytest.raises(ValueError, match="setting sequence mismatch"):
        case.analyze(tmp_path)


def test_adversarial_insufficient_sample_count_inconclusive(tmp_path: Path) -> None:
    """Adversarial test: under-sampled run correctly reports INCONCLUSIVE rather than spurious EQUIVALENT."""
    docs = case.build_documents(samples_per_iteration=120)
    manifest = json.loads(docs["cases.json"].decode())
    circuit = json.loads(docs["circuit.json"].decode())
    _, settings = template_experiment(manifest, circuit)

    simulated_iterations = []
    for setting in settings:
        if setting["role"] == "predecessor":
            counts = {"|1,0,1,0,0,0,0,0,0,0,0,0>": 120}
        else:
            law = setting["ideal"]["two_click_law_indistinguishable"]
            counts = {}
            for pair, prob in law.items():
                state_vec = [0] * case.MODES
                state_vec[int(pair[0])] = 1
                state_vec[int(pair[1])] = 1
                counts[f"|{','.join(str(v) for v in state_vec)}>"] = max(1, int(round(prob * 120)))
        simulated_iterations.append({"setting": setting["name"], "counts": counts})

    (tmp_path / "cases.json").write_bytes(docs["cases.json"])
    (tmp_path / "results.json").write_text(json.dumps({"iterations": simulated_iterations}))

    # Set min_focal_per_iter=50 to admit analysis, but wide CI should yield INCONCLUSIVE
    report = case.analyze(tmp_path, min_focal_per_iter=50)
    verdicts = report["verdicts"]
    if verdicts["predecessor_carryover_hot"] != "INCONCLUSIVE":
        raise AssertionError(f"under-sampled run did not report INCONCLUSIVE: {verdicts['predecessor_carryover_hot']}")


def test_adversarial_malformed_fock_states(tmp_path: Path) -> None:
    """Adversarial test: fail-closed rejection of negative counts, mode mismatch, or syntax corruption."""
    docs = case.build_documents()
    (tmp_path / "cases.json").write_bytes(docs["cases.json"])
    manifest = json.loads(docs["cases.json"].decode())

    # Negative count
    bad_counts = [{"setting": s["name"], "counts": {"|1,0,1,0,0,0,0,0,0,0,0,0>": -5}} for s in manifest["settings"]]
    (tmp_path / "results.json").write_text(json.dumps({"iterations": bad_counts}))
    with pytest.raises(ValueError, match="must be non-negative integer"):
        case.analyze(tmp_path)

    # 11 modes instead of 12
    bad_modes = [{"setting": s["name"], "counts": {"|1,0,1,0,0,0,0,0,0,0,0>": 500}} for s in manifest["settings"]]
    (tmp_path / "results.json").write_text(json.dumps({"iterations": bad_modes}))
    with pytest.raises(ValueError, match="modes, expected 12"):
        case.analyze(tmp_path)


def test_adversarial_template_nan_and_shape_rejection() -> None:
    """Adversarial test: template_experiment strictly rejects NaN parameters, Inf columns, and wrong shapes."""
    docs = case.build_documents()
    manifest = json.loads(docs["cases.json"].decode())
    circuit = json.loads(docs["circuit.json"].decode())

    # 1. NaN in circuit parameters
    bad_manifest = copy.deepcopy(manifest)
    first_setting = bad_manifest["settings"][0]
    param_name = next(iter(first_setting["circuit_params"]))
    first_setting["circuit_params"][param_name] = float("nan")
    with pytest.raises(PlatformError, match="must be finite numbers"):
        template_experiment(bad_manifest, circuit)

    # 2. Inf in column
    bad_manifest2 = copy.deepcopy(manifest)
    bad_manifest2["settings"][0]["column"][0] = [float("inf"), 0.0]
    with pytest.raises(PlatformError, match="column must be finite"):
        template_experiment(bad_manifest2, circuit)

    # 3. Wrong column length (e.g. 10 instead of 12)
    bad_manifest3 = copy.deepcopy(manifest)
    bad_manifest3["settings"][0]["column"] = bad_manifest3["settings"][0]["column"][:10]
    with pytest.raises(PlatformError, match="column must be a list of length 12"):
        template_experiment(bad_manifest3, circuit)
