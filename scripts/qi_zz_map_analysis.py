"""Analyze a completed, hash-bound Tuna-17 conditional-Ramsey map.

This module never submits hardware or creates a result for an incomplete
acquisition. The 4x4 joint assignment matrix is inverted before conditioning
on the neighbor's prepared state. Analytic derivatives propagate the shared
calibration through conditioning, quadratures, phase unwrapping, OLS and the
Hamiltonian reconstruction. Rates require all six planned delays and quality
guards. Every rate is conditional on the first-interval frequency bound;
commensurate delays cannot identify aliases outside that bound.

Usage: python scripts/qi_zz_map_analysis.py --self-test
       python scripts/qi_zz_map_analysis.py --plan PLAN --runs-root DIR --out NEWFILE
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import chi2

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from parallel import ordered_map  # noqa: E402

TAU = 2 * math.pi
Z95 = 1.959963984540054
RATE_ORDER = ("a_given_b0", "a_given_b1", "b_given_a0", "b_given_a1")
PLAN_SCHEMAS = ("qi-zz-map-plan-v1", "qi-zz-map-plan-v2")
GUARDS = {
    "assignment_condition_number_max": 100.0,
    "retained_fraction_lower_3sigma_min": 0.10,
    "radial_amplitude_min": 0.05,
    "radial_snr_min": 5.0,
    "branch_sigma": 3.0,
    "nonphysical_sigma": 3.0,
    "model_quality_p_min": 0.01,
    "holm_family_alpha": 0.05,
    "required_delay_count": 6,
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def validate_raw(shots: Any, expected: int, width: int) -> Counter[str]:
    require(isinstance(shots, list) and len(shots) == expected and expected > 1, "raw shot count mismatch")
    require(
        all(isinstance(shot, str) and len(shot) == width and not set(shot) - {"0", "1"} for shot in shots),
        "malformed raw bitstring",
    )
    return Counter(shots)


def read_batch(task: dict[str, Any]) -> dict[str, Any]:
    directory = Path(task["runs_root"]) / task["batch"]["directory"]
    hashes = {}

    def read(name: str) -> bytes:
        path = directory / name
        payload = path.read_bytes()
        hashes[str(Path(task["batch"]["directory"]) / name)] = digest(payload)
        return payload

    case_bytes = read("cases.json")
    require(digest(case_bytes) == task["batch"]["cases_sha256"], "batch cases.json differs from approved plan")
    cases = json.loads(case_bytes)
    for key in ("backend", "backend_type_id", "shots", "nqubits"):
        require(cases.get(key) == task[key], f"cases.json {key} differs from plan")
    # A v1 manifest predates the plan_schema field; a v2 manifest names its plan's schema.
    require(cases.get("plan_schema", PLAN_SCHEMAS[0]) == task["plan_schema"], "cases.json plan schema differs")
    submission = json.loads(read("submission.json"))
    results = json.loads(read("results.json"))
    submission_schema = submission.get("schema")
    require(submission_schema in {"qi-submission-v1", "qi-submission-v2"}, "missing submission provenance")
    # The cases binding is identical for v1 and v2 receipts. A historical v1
    # receipt that predates the binding carries no cases_sha256 and fails
    # loudly here instead of passing with weaker provenance.
    require(submission.get("cases_sha256") == digest(case_bytes), "submission cases.json digest mismatch")
    if submission_schema == "qi-submission-v2":
        require(submission.get("state") == "enqueued", "submission batch was not enqueued")
    require(submission.get("backend") == task["backend"], "submission backend mismatch")
    require(submission.get("backend_type_id") == task["backend_type_id"], "submission backend type mismatch")
    require(submission.get("shots") == task["shots"], "submission shot count mismatch")
    expected = {row["file"]: row for row in task["rows"]}
    require(len(expected) == len(task["rows"]), "duplicate planned circuit")
    case_rows = {row["file"]: row for row in cases["circuits"]}
    submitted = {row["file"]: row["job"] for row in submission["jobs"]}
    submitted_hashes = {row["file"]: row.get("sha256") for row in submission["jobs"]}
    completed = {row["file"]: row for row in results["jobs"]}
    require(set(expected) == set(case_rows) == set(submitted) == set(completed), "run file set differs from plan")
    require(
        len(submitted) == len(submission["jobs"]) and len(completed) == len(results["jobs"]), "duplicate job record"
    )
    observations = []
    job_ids = []
    for name, row in expected.items():
        require(
            case_rows[name] == {key: value for key, value in row.items() if key != "batch_directory"},
            "planned role/delay/quadrature metadata differs from retained cases.json",
        )
        require(digest(read(name)) == row["sha256"] == case_rows[name]["sha256"], "circuit hash mismatch")
        # The per-job circuit digest binding is identical for v1 and v2 receipts.
        require(submitted_hashes[name] == row["sha256"], "submission job circuit digest mismatch")
        retained = completed[name]
        job = retained["job"]
        require(job["status"] == "completed", f"job for {name} is incomplete")
        require(
            job["id"] == submitted[name] and job["batch_job_id"] == submission["batch_job"], "job identity mismatch"
        )
        require(job["number_of_shots"] == task["shots"], "job denominator mismatch")
        require(job.get("raw_data_enabled") is True, "job did not retain raw output")
        counts = validate_raw(json.loads(read(f"raw/{name}.json")), task["shots"], task["nqubits"])
        quantum_results = [result for result in retained["results"] if result.get("job_id") == job["id"]]
        require(
            len(quantum_results) == 1 and quantum_results[0].get("results") == dict(counts),
            "raw shots disagree with the retained service histogram",
        )
        job_ids.append(job["id"])
        for pair in row["pairs"]:
            a, b = pair["edge"]
            require(a < b, "edge endpoints must be canonical a<b")
            histogram = [0, 0, 0, 0]
            for bitstring, count in counts.items():
                index = 2 * int(bitstring[-1 - a]) + int(bitstring[-1 - b])
                histogram[index] += count
            observations.append(
                {
                    **row,
                    "pair": pair,
                    "counts": histogram,
                    "shots": task["shots"],
                    "probabilities": [k / task["shots"] for k in histogram],
                }
            )
    return {"observations": observations, "input_sha256": hashes, "job_ids": job_ids}


def read_complete_plan(plan_path: Path, runs_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, str]]:
    payload = plan_path.read_bytes()
    plan = json.loads(payload)
    # v2 changes only the interbatch pause budget, which the analysis does not read.
    require(plan.get("schema") in PLAN_SCHEMAS, "unrecognized map plan")
    require(plan["measurement"]["bit_order"] == "qubit_0_rightmost", "unrecognized bit order")
    require(
        "2*bit_a+bit_b" in plan["measurement"]["assignment_convention"].replace(" ", ""),
        "plan must declare canonical pair index 2*bit_a+bit_b",
    )
    require(
        len(plan["delay_cycles"]) == GUARDS["required_delay_count"] and plan["delay_cycles"][0] == 0,
        "plan must retain all six delays including zero",
    )
    require(len(plan["edges"]) == 24, "this proposal requires the full 24-edge family")
    policy_keys = {
        "assignment_condition_number_max": "assignment_condition_number_max",
        "retained_fraction_lower_bound_min": "retained_fraction_lower_3sigma_min",
        "radial_amplitude_min": "radial_amplitude_min",
        "radial_signal_to_noise_min": "radial_snr_min",
        "unwrap_innovation_sigma": "branch_sigma",
        "linearity_and_reciprocity_flag_p": "model_quality_p_min",
    }
    for plan_key, implementation_key in policy_keys.items():
        require(
            plan["analysis_policy"][plan_key] == GUARDS[implementation_key],
            f"analysis policy changed at {plan_key}; review the estimator",
        )
    require(plan["analysis_policy"]["retained_fraction_lower_sigma"] == 3.0, "retention guard changed")
    require(
        plan["measurement"]["probe_preparation"] == "Y90"
        and plan["measurement"]["x_readout"] == "mY90"
        and plan["measurement"]["y_readout"] == "X90",
        "quadrature sign convention changed",
    )
    require(
        plan["model"]["design_rows"] == [[1, 0, 1], [1, 0, -1], [0, 1, 1], [0, 1, -1]], "Hamiltonian convention changed"
    )
    for row in plan["circuits"]:
        if row["kind"] == "conditional_ramsey":
            require(
                math.isclose(
                    row["delay_seconds"],
                    row["delay_cycles"] * plan["wait_cycle_ns"] * 1e-9,
                    rel_tol=1e-12,
                    abs_tol=1e-18,
                ),
                "physical delay mismatch",
            )
            require(
                row["delay_cycles"] in plan["delay_cycles"] and row["quadrature"] in ("x", "y"),
                "unplanned Ramsey setting",
            )
            for pair in row["pairs"]:
                probe_index = 0 if row["direction"] == "a_probe" else 1
                require(
                    pair["probe"] == pair["edge"][probe_index]
                    and pair["neighbor"] == pair["edge"][1 - probe_index]
                    and pair["neighbor_state"] == row["neighbor_state"],
                    "conditional role mismatch",
                )
    tasks = [
        {
            "runs_root": str(runs_root),
            "batch": batch,
            "rows": [row for row in plan["circuits"] if row["batch_directory"] == batch["directory"]],
            "backend": plan["backend"],
            "backend_type_id": plan["backend_type_id"],
            "shots": plan["shots"],
            "nqubits": plan["nqubits"],
            "plan_schema": plan["schema"],
        }
        for batch in plan["batches"]
    ]
    results = ordered_map(read_batch, tasks, min_items=1)
    observations, job_ids = [], []
    hashes = {"plan.json": digest(payload)}
    for result in results:
        observations.extend(result["observations"])
        job_ids.extend(result["job_ids"])
        hashes.update(result["input_sha256"])
    require(len(job_ids) == len(set(job_ids)) == len(plan["circuits"]), "duplicate or missing acquisition job")
    return plan, observations, hashes


def mean_covariance(probabilities: np.ndarray, shots: int) -> np.ndarray:
    return (np.diag(probabilities) - np.outer(probabilities, probabilities)) / (shots - 1)


def scalar(
    value: float, gradient: np.ndarray, covariance: np.ndarray, calibration_dimensions: int = 16
) -> dict[str, Any]:
    variance = max(float(gradient @ covariance @ gradient), 0.0)
    se = math.sqrt(variance)
    cg = gradient[:calibration_dimensions]
    calvar = max(float(cg @ covariance[:calibration_dimensions, :calibration_dimensions] @ cg), 0.0)
    z = value / se if se > 0 else None
    return {
        "estimate": float(value),
        "standard_error": se,
        "ci95_normal": [float(value - Z95 * se), float(value + Z95 * se)],
        "variance_readout_calibration": calvar,
        "z_against_zero": z,
        "two_sided_p": math.erfc(abs(z) / math.sqrt(2)) if z is not None else (1.0 if abs(value) < 1e-12 else None),
    }


def joint_observable(
    r: np.ndarray, assignment_inverse: np.ndarray, probe_index: int, neighbor_state: int, conditioned: bool
) -> tuple[float, float, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    law = assignment_inverse @ r
    bits = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
    retained_weights = (bits[:, 1 - probe_index] == neighbor_state).astype(float)
    weights = retained_weights if conditioned else np.ones(4)
    signs = (1 - 2 * bits[:, probe_index]) * weights
    denominator = float(weights @ law)
    require(denominator > 0, "nonpositive conditioning denominator")
    q = float(signs @ law) / denominator
    gx = (signs - q * weights) / denominator
    gr = gx @ assignment_inverse
    gm = -np.outer(gr, law)
    retention = float(retained_weights @ law)
    retention_gr = retained_weights @ assignment_inverse
    retention_gm = -np.outer(retention_gr, law)
    return q, retention, gr, gm, retention_gr, retention_gm, law


def embed_gradient(
    row_index: int, derivative_r: np.ndarray, derivative_m: np.ndarray, width: int, apply_correction: bool
) -> np.ndarray:
    gradient = np.zeros(width)
    gradient[4 * row_index : 4 * row_index + 4] = derivative_r
    if apply_correction:
        for column in range(4):
            gradient[4 * column : 4 * column + 4] += derivative_m[:, column]
    return gradient


def ols_weights(times: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    centred = times - times.mean()
    slope = centred / float(centred @ centred)
    return slope, np.ones(len(times)) / len(times) - times.mean() * slope


def fit_phase(
    times: np.ndarray, phases: np.ndarray, gradients: np.ndarray, covariance: np.ndarray, inherited_flags: list[str]
) -> dict[str, Any]:
    """Geometric branch selection; OLS derivative is conditional on accepted branches."""
    placed = [float(phases[0])]
    branches, flags = [], list(inherited_flags)
    for i in range(1, len(times)):
        if i == 1:
            prediction, prediction_gradient = placed[0], gradients[0]
        else:
            slope_weights, intercept_weights = ols_weights(times[:i])
            predictor = intercept_weights + times[i] * slope_weights
            prediction = float(predictor @ np.array(placed))
            prediction_gradient = predictor @ gradients[:i]
        turns = round((prediction - phases[i]) / TAU)
        unwrapped = float(phases[i] + TAU * turns)
        innovation = unwrapped - prediction
        innovation_gradient = gradients[i] - prediction_gradient
        se = math.sqrt(max(float(innovation_gradient @ covariance @ innovation_gradient), 0.0))
        margin = math.pi - abs(innovation)
        accepted = margin > GUARDS["branch_sigma"] * se + 1e-12
        if not accepted:
            flags.append("unwrap_branch_ambiguous")
        branches.append(
            {
                "delay_seconds": float(times[i]),
                "whole_turns": turns,
                "innovation_radians": innovation,
                "standard_error": se,
                "branch_margin_radians": margin,
                "accepted": accepted,
            }
        )
        placed.append(unwrapped)
    unwrapped_phases = np.array(placed)
    sw, iw = ols_weights(times)
    slope, intercept = float(sw @ unwrapped_phases), float(iw @ unwrapped_phases)
    slope_gradient, intercept_gradient = sw @ gradients, iw @ gradients
    residual = unwrapped_phases - intercept - slope * times
    projection = np.eye(len(times)) - np.outer(np.ones(len(times)), iw) - np.outer(times, sw)
    residual_gradients = projection @ gradients
    residual_covariance = residual_gradients @ covariance @ residual_gradients.T
    dof = int(np.linalg.matrix_rank(residual_covariance, tol=1e-12))
    statistic = float(residual @ np.linalg.pinv(residual_covariance, rcond=1e-12) @ residual)
    p = float(chi2.sf(statistic, dof)) if dof else (1.0 if np.max(np.abs(residual)) < 1e-10 else 0.0)
    if p < GUARDS["model_quality_p_min"]:
        flags.append("phase_model_lack_of_fit")
    bound = 0.5 / float(times[1] - times[0])
    if abs(slope / TAU) >= bound:
        flags.append("fitted_rate_outside_first_interval_range")
    return {
        "publishable": not flags,
        "quality_flags": sorted(set(flags)),
        "rate_rad_per_second": scalar(slope, slope_gradient, covariance),
        "rate_hz": scalar(slope / TAU, slope_gradient / TAU, covariance),
        "intercept_radians": scalar(intercept, intercept_gradient, covariance),
        "unwrapped_phases": placed,
        "branches": branches,
        "residual_radians": residual.tolist(),
        "linearity": {"chi_square": statistic, "degrees_of_freedom": dof, "p": p},
        "frequency_scope": {"assumed_absolute_rate_below_hz": bound, "out_of_range_aliases_identifiable": False},
        "_gradient": slope_gradient,
    }


def analyze_edge_mode(
    rows: list[dict[str, Any]], matrix: np.ndarray, covariance: np.ndarray, apply_correction: bool, conditioned: bool
) -> dict[str, Any]:
    width = len(covariance)
    condition_number = float(np.linalg.cond(matrix))
    if apply_correction and (
        not math.isfinite(condition_number) or condition_number > GUARDS["assignment_condition_number_max"]
    ):
        return {
            "publishable": False,
            "quality_flags": ["assignment_matrix_ill_conditioned"],
            "inference": None,
            "rates": {},
        }
    inverse = np.linalg.inv(matrix) if apply_correction else np.eye(4)
    rate_records, rate_gradients, rate_values, mode_flags = {}, [], [], []
    for direction, state, rate_name in (
        ("a_probe", 0, RATE_ORDER[0]),
        ("a_probe", 1, RATE_ORDER[1]),
        ("b_probe", 0, RATE_ORDER[2]),
        ("b_probe", 1, RATE_ORDER[3]),
    ):
        probe = 0 if direction == "a_probe" else 1
        selected = [
            (i, row)
            for i, row in enumerate(rows)
            if row["kind"] == "conditional_ramsey" and row["direction"] == direction and row["neighbor_state"] == state
        ]
        delays = sorted({row["delay_seconds"] for _, row in selected})
        require(len(delays) == GUARDS["required_delay_count"] and delays[0] == 0, "missing delay in conditional rate")
        points, phases, phase_gradients, flags = [], [], [], []
        for delay in delays:
            quadratures, q_gradients = [], []
            details, point_flags = {}, []
            for basis in ("x", "y"):
                matching = [
                    (i, row) for i, row in selected if row["delay_seconds"] == delay and row["quadrature"] == basis
                ]
                require(len(matching) == 1, "missing or duplicate Ramsey quadrature")
                index, row = matching[0]
                r = np.array(row["probabilities"])
                try:
                    q, retention, gr, gm, rg, rm, law = joint_observable(r, inverse, probe, state, conditioned)
                except ValueError:
                    return {
                        "publishable": False,
                        "quality_flags": ["nonpositive_conditioning_denominator"],
                        "inference": None,
                        "rates": {},
                    }
                gradient = embed_gradient(index, gr, gm, width, apply_correction)
                retention_gradient = embed_gradient(index, rg, rm, width, apply_correction)
                q_record, retention_record = (
                    scalar(q, gradient, covariance),
                    scalar(retention, retention_gradient, covariance),
                )
                if retention - 3 * retention_record["standard_error"] <= GUARDS["retained_fraction_lower_3sigma_min"]:
                    point_flags.append("insufficient_retained_fraction")
                nonphysical, significant_nonphysical = False, False
                for outcome in range(4):
                    law_gr = inverse[outcome]
                    law_gm = -np.outer(law_gr, law)
                    law_gradient = embed_gradient(index, law_gr, law_gm, width, apply_correction)
                    sigma = math.sqrt(max(float(law_gradient @ covariance @ law_gradient), 0.0))
                    nonphysical |= law[outcome] < -1e-10 or law[outcome] > 1 + 1e-10
                    significant_nonphysical |= law[outcome] < -3 * sigma - 1e-10 or law[outcome] > 1 + 3 * sigma + 1e-10
                if significant_nonphysical:
                    point_flags.append("significantly_nonphysical_corrected_law")
                details[basis] = {
                    "joint_probabilities": law.tolist(),
                    "linear_inversion_nonphysical": bool(nonphysical),
                    "clipped": False,
                    "expectation": q_record,
                    "retained_fraction": retention_record,
                    "discarded_fraction": float(1 - retention),
                }
                quadratures.append(q)
                q_gradients.append(gradient)
            x, y = quadratures
            gx, gy = q_gradients
            radius = math.hypot(x, y)
            if radius < 1e-15:
                radial_gradient, phase_gradient, phase = np.zeros(width), np.zeros(width), 0.0
                point_flags.append("weak_radial_signal")
            else:
                radial_gradient = (x * gx + y * gy) / radius
                phase_gradient = (-y * gx + x * gy) / radius**2
                phase = math.atan2(y, x)
            radial = scalar(radius, radial_gradient, covariance)
            radial_snr = radius / radial["standard_error"] if radial["standard_error"] > 0 else None
            if radius < GUARDS["radial_amplitude_min"] or (
                radial_snr is not None and radial_snr < GUARDS["radial_snr_min"]
            ):
                point_flags.append("weak_radial_signal")
            if radius > 1 + 3 * radial["standard_error"] + 1e-10:
                point_flags.append("significantly_nonphysical_radius")
            points.append(
                {
                    "delay_seconds": delay,
                    "quadratures": details,
                    "radius": radial,
                    "radial_snr": radial_snr,
                    "phase_radians": phase,
                    "quality_flags": sorted(set(point_flags)),
                }
            )
            phases.append(phase)
            phase_gradients.append(phase_gradient)
            flags.extend(point_flags)
        gradient_matrix = np.array(phase_gradients)
        fit = fit_phase(np.array(delays), np.array(phases), gradient_matrix, covariance, flags)
        rate_gradients.append(fit.pop("_gradient"))
        rate_values.append(fit["rate_rad_per_second"]["estimate"])
        rate_records[rate_name] = {
            **fit,
            "points": points,
            "phase_covariance": (gradient_matrix @ covariance @ gradient_matrix.T).tolist(),
        }
        mode_flags.extend(fit["quality_flags"])
    rates, gradients = np.array(rate_values), np.array(rate_gradients)
    rate_covariance = gradients @ covariance @ gradients.T
    weights = {
        "omega_a_hz": np.array([0.5, 0.5, 0, 0]) / TAU,
        "omega_b_hz": np.array([0, 0, 0.5, 0.5]) / TAU,
        "omega_a_minus_omega_b_hz": np.array([0.5, 0.5, -0.5, -0.5]) / TAU,
        "j_a_hz": np.array([0.5, -0.5, 0, 0]) / TAU,
        "j_b_hz": np.array([0, 0, 0.5, -0.5]) / TAU,
        "j_hz": np.array([0.25, -0.25, 0.25, -0.25]) / TAU,
        "conditional_shift_a_1_minus_0_hz": np.array([-1, 1, 0, 0]) / TAU,
        "conditional_shift_b_1_minus_0_hz": np.array([0, 0, -1, 1]) / TAU,
        "conditional_shift_average_1_minus_0_hz": np.array([-0.5, 0.5, -0.5, 0.5]) / TAU,
        "j_a_minus_j_b_hz": np.array([0.5, -0.5, -0.5, 0.5]) / TAU,
        "directional_rate_splitting_residual_rad_per_second": np.array([1, -1, -1, 1]),
    }
    reconstruction = {
        name: scalar(float(weight @ rates), weight @ gradients, covariance) for name, weight in weights.items()
    }
    reciprocal_p = reconstruction["j_a_minus_j_b_hz"]["two_sided_p"]
    if reciprocal_p is None or reciprocal_p < GUARDS["model_quality_p_min"]:
        mode_flags.append("bidirectional_j_disagreement")
    publishable = not mode_flags
    return {
        "publishable": publishable,
        "quality_flags": sorted(set(mode_flags)),
        "rates": rate_records,
        "rate_order": list(RATE_ORDER),
        "rate_covariance_rad2_per_second2": rate_covariance.tolist(),
        "diagnostic_model_fit": reconstruction,
        "inference": reconstruction if publishable else None,
    }


def analyze_edge(task: dict[str, Any]) -> dict[str, Any]:
    rows = task["observations"]
    calibration = sorted(
        (row for row in rows if row["kind"] == "readout"), key=lambda row: tuple(row["pair"]["prepared"])
    )
    require(
        [row["pair"]["prepared"] for row in calibration] == [[0, 0], [0, 1], [1, 0], [1, 1]],
        "missing or duplicate assignment column",
    )
    ramsey = [row for row in rows if row["kind"] == "conditional_ramsey"]
    require(len(ramsey) == 48, "edge requires 48 Ramsey quadratures")
    rows = calibration + ramsey
    width = 4 * len(rows)
    covariance = np.zeros((width, width))
    for i, row in enumerate(rows):
        probability = np.array(row["probabilities"])
        require(
            bool(np.all(probability >= 0)) and math.isclose(float(probability.sum()), 1.0, abs_tol=1e-10),
            "invalid observed histogram",
        )
        covariance[4 * i : 4 * i + 4, 4 * i : 4 * i + 4] = mean_covariance(probability, row["shots"])
    matrix = np.column_stack([row["probabilities"] for row in calibration])
    modes = {}
    for scale, apply_correction in (("raw", False), ("readout_corrected", True)):
        for name, conditioned in (("conditioned", True), ("unconditional", False)):
            modes[f"{scale}_{name}"] = analyze_edge_mode(rows, matrix, covariance, apply_correction, conditioned)
    condition_number = float(np.linalg.cond(matrix))
    return {
        "edge": task["edge"],
        "assignment_index": "2*bit_a+bit_b",
        "assignment_matrix": matrix.tolist(),
        "assignment_condition_number": condition_number if math.isfinite(condition_number) else None,
        "assignment_condition_number_finite": math.isfinite(condition_number),
        "modes": modes,
    }


def holm(edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tests = []
    for i, edge in enumerate(edges):
        primary = edge["modes"]["readout_corrected_conditioned"]
        p = primary["inference"]["j_hz"]["two_sided_p"] if primary["inference"] else None
        tests.append((1.0 if p is None else p, i, primary["publishable"]))
    maximum = 0.0
    output: list[dict[str, Any]] = [{} for _ in edges]
    for rank, (p, index, eligible) in enumerate(sorted(tests)):
        maximum = max(maximum, min(1.0, p * (len(edges) - rank)))
        output[index] = {
            "edge": edges[index]["edge"],
            "eligible": eligible,
            "p_for_family": p,
            "holm_adjusted_p": maximum,
            "resolved_nonzero_j": eligible and maximum < GUARDS["holm_family_alpha"],
        }
    return output


def analyze(plan_path: Path, runs_root: Path) -> dict[str, Any]:
    analyzer_source = Path(__file__).resolve()
    analyzer_identity = {
        "path": str(analyzer_source.relative_to(ROOT)),
        "sha256": digest(analyzer_source.read_bytes()),
    }
    plan, observations, hashes = read_complete_plan(plan_path, runs_root)
    tasks = [
        {"edge": edge, "observations": [row for row in observations if row["pair"]["edge"] == edge]}
        for edge in plan["edges"]
    ]
    edges = ordered_map(analyze_edge, tasks, min_items=1)
    return {
        "schema": "qi-zz-map-analysis-v1",
        "claim_kind": "retained hardware analysis under proposed protocol",
        "provider": "quantum_inspire",
        "backend": plan["backend"],
        "analyzer_source": analyzer_identity,
        "plan_sha256": digest(plan_path.read_bytes()),
        "input_sha256": hashes,
        "guards": GUARDS,
        "edges": edges,
        "holm_corrected_j_family": holm(edges),
        "method": {
            "pair_index": "2*bit_a+bit_b, a<b, qubit zero rightmost",
            "assignment": "full 4x4, observed rows and prepared columns; linear inverse before conditioning",
            "conditioning": (
                "neighbor final state equals its prepared state; report raw and corrected alongside unconditional"
            ),
            "covariance": "multinomial pair histograms and shared assignment columns; analytic delta method",
            "phase": "atan2(Y,X); geometric branch selection; OLS with free zero-idle intercept",
            "hamiltonian": "H/hbar=(omega_A*Z_A+omega_B*Z_B+J*Z_A*Z_B)/2",
            "rate_order": list(RATE_ORDER),
            "j_convention": "j_hz=J/(2*pi); (nu1-nu0)/(2*pi)=-2*j_hz",
            "cross_edge_covariance": (
                "omitted; no pooled independence assumption; Holm is valid under arbitrary dependence"
            ),
            "absolute_frequency_scope": (
                "all rates conditional on first-interval |nu/(2*pi)|<1 MHz; out-of-range aliases cannot all be detected"
            ),
            "interval_scope": (
                "pointwise normal 95%; branch-conditional; excludes drift and calibration-model misspecification"
            ),
            "invalid_edges": (
                "diagnostic values retained with flags; inference is null; never report unresolved as zero"
            ),
            "interpretation": (
                "effective pair idle Hamiltonian, not coupler flux settings or a unique coupler mechanism"
            ),
        },
    }


def synthetic_edge(kind: str = "nominal") -> dict[str, Any]:
    """Analytic probability fixtures, never acquired or quantum-simulated data."""
    assignment_a = np.array([[0.96, 0.12], [0.04, 0.88]])
    assignment_b = np.array([[0.98, 0.08], [0.02, 0.92]])
    matrix = np.kron(assignment_a, assignment_b)
    if kind == "singular":
        matrix = np.full((4, 4), 0.25)
    elif kind == "correlated":
        # A non-product stochastic channel mixes the joint 00 and 11 outcomes.
        correlation = np.eye(4)
        correlation[:, 0] = [0.94, 0, 0, 0.06]
        correlation[:, 3] = [0.03, 0, 0, 0.97]
        matrix = correlation @ matrix
    rows = []
    for column, prepared in enumerate(([0, 0], [0, 1], [1, 0], [1, 1])):
        rows.append(
            {
                "kind": "readout",
                "pair": {"edge": [0, 1], "prepared": prepared},
                "shots": 1000000,
                "probabilities": matrix[:, column].tolist(),
            }
        )
    rates = [38000.0, 22000.0, -4000.0, -20000.0]
    if kind == "reciprocal":
        rates[2] += 10000
    elif kind == "alias":
        rates[0] = 1000000
    elif kind == "constant":
        rates = [0.0] * 4
    radius = 0.005 if kind == "weak" else 0.8
    times = (0, 0.5e-6, 2e-6, 8e-6, 20e-6, 40e-6)
    for direction, probe in (("a_probe", 0), ("b_probe", 1)):
        for neighbor_state in (0, 1):
            rate = rates[2 * probe + neighbor_state]
            for delay in times:
                phase = 0.17 + TAU * rate * delay
                for basis in ("x", "y"):
                    expectation = radius * (math.cos(phase) if basis == "x" else math.sin(phase))
                    true = np.zeros(4)
                    for a in (0, 1):
                        for b in (0, 1):
                            bits = (a, b)
                            true[2 * a + b] = (
                                0.95 * (1 + (1 - 2 * bits[probe]) * expectation) / 2
                                if bits[1 - probe] == neighbor_state
                                else 0.025
                            )
                    rows.append(
                        {
                            "kind": "conditional_ramsey",
                            "direction": direction,
                            "neighbor_state": neighbor_state,
                            "quadrature": basis,
                            "delay_seconds": delay,
                            "pair": {
                                "edge": [0, 1],
                                "probe": probe,
                                "neighbor": 1 - probe,
                                "neighbor_state": neighbor_state,
                            },
                            "shots": 1000000,
                            "probabilities": (matrix @ true).tolist(),
                        }
                    )
    return {"edge": [0, 1], "observations": rows}


def test_case(kind: str) -> dict[str, Any]:
    return {"kind": kind, "result": analyze_edge(synthetic_edge(kind))}


def derivative_self_test() -> None:
    rows = synthetic_edge("correlated")["observations"]
    matrix = np.column_stack([row["probabilities"] for row in rows[:4]])
    r = np.array(rows[11]["probabilities"])
    _, _, gradient_r, gradient_m, _, _, _ = joint_observable(r, np.linalg.inv(matrix), 0, 0, True)
    step = 1e-6
    for index in range(4):
        perturbation = np.zeros(4)
        perturbation[index] = step
        high = joint_observable(r + perturbation, np.linalg.inv(matrix), 0, 0, True)[0]
        low = joint_observable(r - perturbation, np.linalg.inv(matrix), 0, 0, True)[0]
        require(
            abs((high - low) / (2 * step) - gradient_r[index]) < 1e-7, "conditioning histogram derivative is incorrect"
        )
    for row, column in ((0, 0), (1, 3), (2, 1), (3, 2)):
        perturbation = np.zeros((4, 4))
        perturbation[row, column] = step
        high = joint_observable(r, np.linalg.inv(matrix + perturbation), 0, 0, True)[0]
        low = joint_observable(r, np.linalg.inv(matrix - perturbation), 0, 0, True)[0]
        require(
            abs((high - low) / (2 * step) - gradient_m[row, column]) < 1e-7,
            "assignment inverse derivative is incorrect",
        )


def provenance_self_test() -> None:
    """A valid miniature collector record passes; corrupted or absent evidence fails."""
    with tempfile.TemporaryDirectory(prefix="qi-zz-analysis-fixture-") as scratch:
        root = Path(scratch)
        batch = root / "batch-000"
        (batch / "raw").mkdir(parents=True)
        source = "version 3.0\nqubit[2] q\nbit[2] b\nb = measure q\n"
        row = {
            "file": "fixture.cq",
            "kind": "readout",
            "pairs": [{"edge": [0, 1], "prepared": [0, 0]}],
            "sha256": digest(source.encode()),
        }
        case_bytes = json.dumps(
            {"circuits": [row], "backend": "tuna_17", "backend_type_id": 7, "shots": 2, "nqubits": 2}
        ).encode()
        (batch / "fixture.cq").write_text(source)
        (batch / "cases.json").write_bytes(case_bytes)
        submission = {
            "schema": "qi-submission-v1",
            "backend": "tuna_17",
            "backend_type_id": 7,
            "shots": 2,
            "batch_job": "synthetic-batch",
            "cases_sha256": digest(case_bytes),
            "jobs": [{"file": "fixture.cq", "job": "synthetic-job", "sha256": row["sha256"]}],
        }
        submission_path = batch / "submission.json"
        submission_path.write_text(json.dumps(submission))
        (batch / "results.json").write_text(
            json.dumps(
                {
                    "jobs": [
                        {
                            "file": "fixture.cq",
                            "job": {
                                "status": "completed",
                                "id": "synthetic-job",
                                "batch_job_id": "synthetic-batch",
                                "number_of_shots": 2,
                                "raw_data_enabled": True,
                            },
                            "results": [{"job_id": "synthetic-job", "results": {"00": 1, "01": 1}}],
                        }
                    ]
                }
            )
        )
        raw_path = batch / "raw/fixture.cq.json"
        raw_path.write_text(json.dumps(["00", "01"]))
        task = {
            "runs_root": str(root),
            "batch": {"directory": "batch-000", "cases_sha256": digest(case_bytes)},
            "rows": [row],
            "backend": "tuna_17",
            "backend_type_id": 7,
            "shots": 2,
            "nqubits": 2,
            "plan_schema": "qi-zz-map-plan-v1",
        }
        require(read_batch(task)["observations"][0]["counts"] == [1, 0, 1, 0], "canonical pair bit order failed")
        try:
            read_batch({**task, "plan_schema": "qi-zz-map-plan-v2"})
        except ValueError as error:
            require(str(error) == "cases.json plan schema differs", "plan-schema fixture failed for another reason")
        else:
            raise AssertionError("a v1 manifest was read under a v2 plan")
        v2_submission = {
            **submission,
            "schema": "qi-submission-v2",
            "state": "enqueued",
            "cases_sha256": digest(case_bytes),
            "jobs": [{"file": "fixture.cq", "job": "synthetic-job", "sha256": row["sha256"]}],
        }
        for valid in ({**submission, "cases_sha256": digest(case_bytes)}, v2_submission):
            receipt = dict(valid)
            submission_path.write_text(json.dumps(receipt))
            require(read_batch(task)["observations"][0]["counts"] == [1, 0, 1, 0], "bound receipt was rejected")
            receipt["cases_sha256"] = "0" * 64
            submission_path.write_text(json.dumps(receipt))
            try:
                read_batch(task)
            except ValueError:
                pass
            else:
                raise AssertionError("a changed cases.json digest was accepted")
        for changes, message in (
            ({"state": "created"}, "submission batch was not enqueued"),
            (
                {"jobs": [{"file": "fixture.cq", "job": "synthetic-job"}]},
                "submission job circuit digest mismatch",
            ),
            (
                {"jobs": [{"file": "fixture.cq", "job": "synthetic-job", "sha256": "0" * 64}]},
                "submission job circuit digest mismatch",
            ),
        ):
            submission_path.write_text(json.dumps({**v2_submission, **changes}))
            try:
                read_batch(task)
            except ValueError as error:
                require(str(error) == message, "v2 negative fixture failed for an unrelated reason")
            else:
                raise AssertionError("a v2 receipt accepted missing enqueue/circuit provenance")
        submission_path.write_text(
            json.dumps({key: value for key, value in v2_submission.items() if key != "cases_sha256"})
        )
        try:
            read_batch(task)
        except ValueError:
            pass
        else:
            raise AssertionError("a v2 receipt accepted an absent cases.json digest")
        # v1 receipts face the same bindings: a v1 receipt without them fails loudly.
        for receipt, message in (
            (
                {key: value for key, value in submission.items() if key != "cases_sha256"},
                "submission cases.json digest mismatch",
            ),
            (
                {**submission, "jobs": [{"file": "fixture.cq", "job": "synthetic-job"}]},
                "submission job circuit digest mismatch",
            ),
        ):
            submission_path.write_text(json.dumps(receipt))
            try:
                read_batch(task)
            except ValueError as error:
                require(str(error) == message, "v1 negative fixture failed for an unrelated reason")
            else:
                raise AssertionError("a v1 receipt accepted missing digest provenance")
        submission_path.write_text(json.dumps(submission))
        changed_task = {**task, "rows": [{**row, "pairs": [{"edge": [0, 1], "prepared": [1, 0]}]}]}
        try:
            read_batch(changed_task)
        except ValueError:
            pass
        else:
            raise AssertionError("changed plan semantics reinterpreted an unchanged retained circuit")
        for invalid in (["00", "0x"], ["00", "00"]):
            raw_path.write_text(json.dumps(invalid))
            try:
                read_batch(task)
            except ValueError:
                pass
            else:
                raise AssertionError("corrupted raw provenance was accepted")
        raw_path.unlink()
        try:
            read_batch(task)
        except FileNotFoundError:
            pass
        else:
            raise AssertionError("missing raw acquisition was accepted")


def self_test() -> None:
    fixtures = ordered_map(
        test_case, ["nominal", "correlated", "reciprocal", "alias", "weak", "constant", "singular"], min_items=1
    )
    results = {row["kind"]: row["result"]["modes"]["readout_corrected_conditioned"] for row in fixtures}
    nominal = results["nominal"]
    require(nominal["publishable"], f"nominal analytical fixture rejected: {nominal['quality_flags']}")
    require(results["correlated"]["publishable"], "jointly correlated assignment was rejected")
    require(
        abs(results["correlated"]["inference"]["j_hz"]["estimate"] - 8000) < 1e-7,
        "jointly correlated assignment was not corrected",
    )
    require(
        "assignment_matrix_ill_conditioned" in results["singular"]["quality_flags"],
        "singular assignment was not flagged",
    )
    json.dumps(fixtures, allow_nan=False)
    for name, truth in (
        ("omega_a_hz", 30000),
        ("omega_b_hz", -12000),
        ("j_hz", 8000),
        ("omega_a_minus_omega_b_hz", 42000),
        ("conditional_shift_average_1_minus_0_hz", -16000),
    ):
        require(
            abs(nominal["inference"][name]["estimate"] - truth) < 1e-7, f"wrong Hamiltonian sign or scale for {name}"
        )
    require("bidirectional_j_disagreement" in results["reciprocal"]["quality_flags"], "reciprocal-J failure was missed")
    require("unwrap_branch_ambiguous" in results["alias"]["quality_flags"], "ambiguous branch was admitted")
    require(
        "weak_radial_signal" in results["weak"]["quality_flags"] and results["weak"]["inference"] is None,
        "weak signal was reported as a valid null",
    )
    for rate in results["constant"]["rates"].values():
        require(
            rate["rate_hz"]["variance_readout_calibration"] < 1e-15,
            "a common calibration failed to cancel from a constant phase's slope",
        )
    # The common 0.5 us divisor makes a 2 MHz shift observationally identical.
    for delay in (0, 0.5e-6, 2e-6, 8e-6, 20e-6, 40e-6):
        require(
            abs(
                complex(math.cos(TAU * 30000 * delay), math.sin(TAU * 30000 * delay))
                - complex(math.cos(TAU * 2030000 * delay), math.sin(TAU * 2030000 * delay))
            )
            < 1e-12,
            "alias-scope fixture changed",
        )
    derivative_self_test()
    provenance_self_test()
    print(
        "qi ZZ map analysis self-test: asymmetric assignment, Hamiltonian scale/sign, calibration covariance, "
        "reciprocity, alias/weak-signal guards and raw provenance pass"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--runs-root", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.self_test:
        self_test()
    if any((args.plan, args.runs_root, args.out)):
        if not all((args.plan, args.runs_root, args.out)):
            parser.error("--plan, --runs-root and --out are required together")
        if args.out.exists():
            parser.error("--out must be a new analysis file")
        result = analyze(args.plan, args.runs_root)
        text = json.dumps(result, indent=1, sort_keys=True, allow_nan=False) + "\n"
        with args.out.open("x", encoding="utf-8") as stream:
            stream.write(text)
        print(f"conditional-Ramsey analysis written to {args.out}")
    elif not args.self_test:
        parser.error("choose --self-test or provide the complete acquisition arguments")
    return 0


if __name__ == "__main__":
    sys.exit(main())
