"""The plane model of the line-native Grover retention: the noisy-path engine, the plane family, the departure rule
and the mirror-pair estimator. The tests read the committed fourth-depth case as a known-good oracle (its
prediction.json holds the exact model of iqm_grover_line.predicted) and compute every planted input here."""

import json
import math
from pathlib import Path
from typing import Any

import iqm_grover_line as grover
import iqm_grover_plane_case as case
import iqm_sim
import numpy as np
import pytest

import grover_plane as plane
import grover_plane_calibration as calibration
import grover_plane_decision as decision
import grover_plane_sim as sim

ROOT = Path(__file__).resolve().parent.parent
OLD = ROOT / "results" / "iqm" / "cases" / "grover-fourth-depth-mirrored"
NEW = ROOT / "results" / "iqm" / "cases" / case.CASE
NEW_101 = ROOT / "results" / "iqm" / "cases" / case.CASE_101
PATH = ["QB20", "QB16", "QB17"]


def require(condition: bool, message: str = "") -> None:
    if not condition:
        raise AssertionError(message)


def circuits() -> dict[int, dict]:
    return {k: json.loads((OLD / "circuits" / f"m101-k{k}-c0.json").read_text(encoding="utf-8")) for k in (1, 2, 3, 4)}


@pytest.fixture(scope="module")
def cal() -> iqm_sim.Calibration:
    return iqm_sim.Calibration.from_directory(OLD / "calibration")


@pytest.fixture(scope="module")
def response(cal: iqm_sim.Calibration) -> sim.Response:
    return sim.Response(circuits(), cal, PATH, "101")


@pytest.fixture(scope="module")
def fitter(response: sim.Response) -> decision.Fitter:
    return decision.Fitter(response, 31, 41)


def key_of(i: int) -> str:
    return "".join(str((i >> q) & 1) for q in range(3))


def test_the_engine_reproduces_the_committed_exact_model(cal: iqm_sim.Calibration) -> None:
    arms = json.loads((OLD / "prediction.json").read_text(encoding="utf-8"))["arms"]
    for name in ("m101-k1-c0", "m101-k3-c0", "m101-k4-c0", "ro-011"):
        circuit = json.loads((OLD / "circuits" / f"{name}.json").read_text(encoding="utf-8"))
        dist = case.final_distribution(circuit, cal)
        for i in range(8):
            require(abs(dist[i] - arms[name]["predicted"][key_of(i)]) < 1e-8)


def test_the_noiseless_cut_channels_equal_the_logical_iteration(cal: iqm_sim.Calibration) -> None:
    frame = sim.logical_frame(circuits()[4], cal, PATH, "101", 4, noisy=False)
    logical = [grover.logical_unitary(grover.grover_ops("101", j)) for j in range(5)]
    g = sim.conjugation(logical[1] @ logical[0].conj().T)
    require(all(np.abs(lam - g).max() < 1e-12 for lam in frame["lambda"]))


def test_the_noisy_channels_of_iterations_two_to_four_agree(cal: iqm_sim.Calibration) -> None:
    frame = sim.logical_frame(circuits()[4], cal, PATH, "101", 4, noisy=True)
    require(np.abs(frame["lambda"][1] - frame["lambda"][2]).max() < 1e-10)
    require(np.abs(frame["lambda"][2] - frame["lambda"][3]).max() < 1e-10)


def test_the_affine_plane_closure_holds_for_the_model_to_the_stated_bound(cal: iqm_sim.Calibration) -> None:
    for k, bound in ((1, 1e-5), (2, 2e-4), (3, 2e-3), (4, 6e-3)):
        arm = plane.arm_of(circuits()[k], cal, PATH, "101", k)
        error = plane.retention(arm, plane.probability(arm, 1.0, 1.0, 0.0)) - plane.retention(
            arm, arm.model_probability
        )
        require(abs(error) < bound)


def test_the_response_matches_the_model_and_the_depth_one_dependence_on_each_parameter(response: sim.Response) -> None:
    arms = json.loads((OLD / "prediction.json").read_text(encoding="utf-8"))["arms"]
    model = response.probabilities(1.0, 1.0, 0.0)
    require(np.allclose(model, [arms[f"m101-k{k}-c0"]["predicted_marked"] for k in (1, 2, 3, 4)], atol=2e-9))
    require(response.probabilities(0.9, 1.0, 0.0)[0] == pytest.approx(1 / 8 + 0.9 * (model[0] - 1 / 8)))
    require(response.probabilities(1.0, 0.9, 0.0)[0] < model[0])
    require(response.probabilities(1.0, 1.0, 0.02)[2] != pytest.approx(model[2], abs=1e-3))


def test_a_cz_phase_error_rotates_the_plane_of_mark_101_and_leaves_mark_011_unrotated(cal: iqm_sim.Calibration) -> None:
    def eps_of(mark: str, x: float) -> float:
        d = (
            ROOT
            / "results"
            / "iqm"
            / "runs"
            / "2026-11-21T220358Z-garnet-grover-depth-sedenion-walsh-grover"
            / "circuits"
        )
        circuit = json.loads((d / f"m{mark}-k3.json").read_text(encoding="utf-8"))
        frame = sim.logical_frame(circuit, cal, PATH, mark, 3, noisy=False, cz_phase=x)
        m, _ = sim.plane_map(frame["lambda"][1], plane.marked_index(mark))
        b = m[np.ix_([1, 3], [1, 3])]
        return math.atan2((b[1, 0] - b[0, 1]) / 2, (b[0, 0] + b[1, 1]) / 2) - 4 * sim.THETA

    require(eps_of("101", 0.01) - eps_of("101", -0.01) == pytest.approx(-1.29 * 0.02, rel=0.02))
    require(abs(eps_of("011", 0.01) - eps_of("011", -0.01)) < 1e-6)


def test_the_mirror_pair_mean_cancels_a_linear_drift_at_unequal_kept_shots() -> None:
    drift = 0.01
    pair = ((round(0.3 * 16800 - drift * 16800), 16800), (round(0.3 * 8400 + drift * 8400), 8400))
    mean, _ = decision.pair_mean(pair)
    pooled = (pair[0][0] + pair[1][0]) / (pair[0][1] + pair[1][1])
    require(mean == pytest.approx(0.3, abs=1e-4))
    require(abs(pooled - 0.3) > 1e-3)


def planted(response: sim.Response, p: np.ndarray, kept: int = 13440) -> dict[int, list[Any]]:
    pairs: dict[int, list[Any]] = {}
    for i, k in enumerate(decision.DEPTHS):
        pairs[k] = [((round(p[i] * kept), kept), (round(p[i] * kept), kept)) for _ in range(case.COPIES[k] // 2)]
    return pairs


def test_a_planted_rotation_reads_coherent_and_a_planted_geometric_law_does_not(
    fitter: decision.Fitter, response: sim.Response
) -> None:
    ro = np.zeros((4, 4))
    zero = np.zeros(4)
    rotated = decision.read_pairs(
        fitter, planted(response, response.probabilities(0.97, 0.98, 0.03)), zero, ro, 13440, 6.64
    )
    require(rotated["departure"] == "coherent")
    require(rotated["rotation"]["eps"] == pytest.approx(0.03, abs=0.004))
    geometric = decision.read_pairs(
        fitter, planted(response, response.probabilities(0.97, 0.98, 0.0)), zero, ro, 13440, 6.64
    )
    require(geometric["departure"] != "coherent")
    require(geometric["geometric"]["s"] == pytest.approx(0.98, abs=0.01))


def test_a_depth_independent_offset_is_not_a_per_iteration_loss_and_an_unresolved_term_is_not_geometric(
    fitter: decision.Fitter, response: sim.Response
) -> None:
    ro = np.zeros((4, 4))
    zero = np.zeros(4)
    spam = decision.read_pairs(fitter, planted(response, response.probabilities(0.97, 1.0, 0.0)), zero, ro, 13440, 6.64)
    require(spam["per_iteration_loss"] == "not resolved")
    require(spam["offset_a"] == pytest.approx(0.97, abs=0.01))
    # a few copies at one eighth of the kept shots leave the rotation unresolved and the geometric reading unavailable
    thin = {
        k: [((round(p * 300), 300), (round(p * 300), 300))] * 2
        for k, p in zip(decision.DEPTHS, response.probabilities(0.97, 0.98, 0.003), strict=True)
    }
    reading = decision.read_pairs(fitter, thin, zero, ro, 300, 6.64)
    require(reading["departure"] == "unresolved")


def sole_pair_probe(response: sim.Response, shift: float = -0.08) -> dict[int, list[Any]]:
    """Geometric truth a = 0.97, s = 0.98, eps = 0; four depth-3 pairs fall below the shot floor and the surviving
    pair carries one circuit displaced by shift."""
    p = response.probabilities(0.97, 0.98, 0.0)
    pairs = planted(response, p)
    thin = round(p[2] * 3000), 3000
    for i in range(4):
        pairs[3][i] = (thin, thin)
    pairs[3][4] = ((round((p[2] + shift) * 13440), 13440), (round(p[2] * 13440), 13440))
    return pairs


def test_a_depth_with_one_surviving_pair_reads_not_evaluated(fitter: decision.Fitter, response: sim.Response) -> None:
    out = decision.read_pairs(fitter, sole_pair_probe(response), np.zeros(4), np.zeros((4, 4)), 13440, 6.64)
    require(out["dropped_pairs"] == {"3": [0, 1, 2, 3]}, out["dropped_pairs"])
    require(out["departure"] == decision.NO_PAIRS, out["departure"])
    require("rotation" not in out and "influence" not in out)
    intact = decision.read_pairs(
        fitter, planted(response, response.probabilities(0.97, 0.98, 0.0)), np.zeros(4), np.zeros((4, 4)), 13440, 6.64
    )
    require(intact["departure"] in decision.VALID_READINGS, intact["departure"])


def test_a_displaced_copy_pair_reads_not_evaluated(fitter: decision.Fitter, response: sim.Response) -> None:
    ro = np.zeros((4, 4))
    p = response.probabilities(0.97, 0.98, 0.0)
    pairs = planted(response, p)
    pairs[3][0] = ((round((p[2] + 0.03) * 13440), 13440), (round((p[2] + 0.03) * 13440), 13440))
    out = decision.read_pairs(fitter, pairs, np.zeros(4), ro, 13440, 6.64)
    require(out["departure"].startswith("not evaluated"))


def test_the_leave_one_pair_out_check_names_a_reading_that_one_pair_carries(
    fitter: decision.Fitter, response: sim.Response
) -> None:
    ro = np.zeros((4, 4))
    p = response.probabilities(0.97, 0.98, 0.0)
    pairs = planted(response, p)
    pairs[1] = [((round((p[0] + 0.04) * 3000), 3000), (round((p[0] + 0.04) * 3000), 3000)), pairs[1][0]]
    out = decision.read_pairs(fitter, pairs, np.zeros(4), ro, 13440, 6.64)
    require("influence" in out or out["departure"].startswith("not evaluated"))


def test_the_boundary_search_walks_the_perimeter_of_the_null_box() -> None:
    corners = {calibration.perimeter(float(t)) for t in range(4)}
    require(corners == {(a, s) for a in calibration.NULL_A for s in calibration.NULL_S}, str(corners))
    for t in (0.3, 1.5, 2.9, 3.7):
        a, s = calibration.perimeter(t)
        require(a in calibration.NULL_A or s in calibration.NULL_S, str((t, a, s)))


def test_the_heterogeneity_gate_follows_the_dispersion_the_covariance_assumes() -> None:
    # two pairs per depth whose means differ by 1.4 binomial standard deviations of a pair mean
    kept = 13440
    sd = math.sqrt(0.2 * 0.8 / (2 * kept))
    pairs = {
        k: [((round(kept * (0.2 + 1.4 * sd)), kept),) * 2, ((round(kept * 0.2), kept),) * 2] for k in decision.DEPTHS
    }
    binomial, _ = decision.heterogeneity(pairs, 1.0)
    consistent, dof = decision.heterogeneity(pairs, decision.PHI)
    require(consistent == pytest.approx(binomial / decision.PHI, rel=1e-6), str((binomial, consistent)))
    require(dof == 4)


def test_the_readout_gate_rates_fall_with_the_dispersion_of_the_copies() -> None:
    plan = {"planned_covariance": 1e-5 * np.eye(4), "tolerance": 0.05, "sides_dof": 56, "sides_threshold": 82.29}
    rates = calibration.readout_gate_rates(plan)
    by_phi = rates["sides_pass_rate_by_dispersion"]
    require(by_phi["1"] == pytest.approx(0.99, abs=0.005) and by_phi["1.54"] < 0.5 < by_phi["0.86"], by_phi)
    require(rates["shift_pass_rate"] == 1.0 and rates["copy_floor"] == "not modeled")


def test_the_reading_rates_count_each_category_of_the_departure() -> None:
    cell = {
        "T": np.array([10.0, 1.0, 1.0]),
        "eps": np.array([0.03, 0.001, 0.02]),
        "se": np.array([0.003, 0.002, 0.003]),
    }
    rates = calibration.readings(cell, 6.64)
    expected = {"coherent": 1 / 3, "geometric": 1 / 3, "unresolved": 1 / 3}
    require(all(rates[k] == pytest.approx(v) for k, v in expected.items()))


@pytest.mark.audit
def test_the_null_box_calibration_holds_the_false_alarm_rate_at_a_small_grid(fitter: decision.Fitter) -> None:
    kept = [4 * 13440.0, 4 * 13440.0, 10 * 13440.0, 4 * 13440.0]
    out = calibration.calibrate(
        fitter, kept, np.zeros((4, 4)), log2n=7, cell_log2n=2, search_log2n=5, nodes=4, refinements=1
    )
    require(out["delta_resolve"] >= 6.634)
    require(out["false_coherent_max"] <= 0.03)
    require(out["cells_by_kind"]["corner"] == 4 and out["cells_by_kind"]["boundary"] >= 4, out["cells_by_kind"])
    require("non_rotation_false_alarm_max" in out)


@pytest.mark.audit
@pytest.mark.parametrize("design", [case.DESIGN, case.DESIGN_101], ids=lambda d: d.case)
def test_each_committed_case_arrangement_is_the_local_optimum_and_mirrored(design: case.Design) -> None:
    require(case.best_first_half(design) == design.first_half)
    arms = case.depth_arms(design)
    require(len(arms) == 2 * len(design.first_half))
    require(case.feasible(design.first_half, design))
    require({a["marked"] for a in arms if a["marked"]} == set(design.marks))


@pytest.mark.audit
def test_the_101_case_is_the_primary_arms_of_the_full_case_without_mark_011() -> None:
    full = json.loads((NEW / "cases.json").read_text(encoding="utf-8"))
    only = json.loads((NEW_101 / "cases.json").read_text(encoding="utf-8"))
    prediction = json.loads((NEW_101 / "prediction.json").read_text(encoding="utf-8"))
    require(len(full["jobs"][0]["circuits"]) == 52 and len(only["jobs"][0]["circuits"]) == 38)
    require(only["case"] == case.CASE_101 and prediction["marks"] == ["101"] and "copies_011" not in prediction)
    require("mark_011" not in prediction["decisions"] and prediction["decisions"]["contrast"] is None)
    require(only["question"] == case.question(None) and "011" not in only["question"])
    require(only["prediction_sha256"] == case.sha256((NEW_101 / "prediction.json").read_bytes()))
    full_prediction = json.loads((NEW / "prediction.json").read_text(encoding="utf-8"))["decisions"]
    for key in ("calibration", "power", "gated_power", "rule", "gate", "model_probabilities"):
        require(full_prediction[key] == prediction["decisions"][key], key)
    names = lambda c: {e["file"] for e in c["jobs"][0]["circuits"] if "m101" in e["file"]}  # noqa: E731
    cost = prediction["decisions"]["cost"]
    require(cost["circuits"] == 38 and cost["executions"] == 38 * case.SHOTS and len(names(only)) == 22)


@pytest.mark.audit
def test_the_committed_case_binds_its_prediction_and_its_response_digest() -> None:
    cases = json.loads((NEW / "cases.json").read_text(encoding="utf-8"))
    text = (NEW / "prediction.json").read_bytes()
    require(cases["prediction_sha256"] == case.sha256(text))
    prediction = json.loads(text)
    d = prediction["decisions"]
    require(d["rule"]["delta_resolve"] >= 6.634)
    require(d["calibration"]["false_coherent_max_plus_3se"] <= 0.02)
    require(d["calibration"]["cells_by_kind"]["corner"] == 4 and d["calibration"]["blocks"] == 8)
    require(d["power"]["worst_resolved_truth"]["coherent"] >= 0.85)
    require(d["contrast"]["ratio_interval"][0] <= d["contrast"]["ratio_prx"] <= d["contrast"]["ratio_interval"][1])
    require(set(d["readout_gates"]) == {"101", "011"} and d["gate"]["min_pairs_per_depth"] == 2)
    cal = iqm_sim.Calibration.from_directory(NEW / "calibration")
    circuits_by_depth = {
        k: json.loads(next((NEW / "circuits").glob(f"m101-k{k}-c0.json")).read_text(encoding="utf-8"))
        for k in (1, 2, 3, 4)
    }
    import grover_plane_analysis as analysis

    response = sim.Response(circuits_by_depth, cal, PATH, "101")
    require(analysis.response_digest(response, d["response"]) == d["response"]["sha256"])
    job = cases["jobs"][0]
    require(job["max_credits"]["garnet"] == d["cost"]["max_credits_garnet"])
    require(job["max_credits"]["garnet"] >= d["cost"]["max_credits_grover_band"])
    require(d["cost"]["cancel_threshold_seconds"] == d["cost"]["billed_seconds_of_ceiling"] - 1)
    require(d["contrast"]["power"] and d["mark_011"]["response"]["sha256"])


def test_an_inadequate_departure_reads_non_geometric_not_a_rotation(
    fitter: decision.Fitter, response: sim.Response
) -> None:
    truth = response.probabilities(0.97, 0.98, 0.0)
    bumped = truth + np.array([0.0, -0.05, 0.0, 0.0])
    cov = np.diag(decision.PHI * bumped * (1 - bumped) / (4 * 13440.0))
    out = decision.decide(fitter, bumped, cov, 6.64)
    require(out["departure"] == decision.NON_ROTATION, out["departure"])
    require(not out["rotation_adequate"])
    rotated = decision.decide(fitter, response.probabilities(0.97, 0.98, 0.03), cov, 6.64)
    require(rotated["departure"] == "coherent" and rotated["rotation_adequate"], rotated["departure"])


def test_a_fit_on_a_bound_of_the_calibrated_box_reads_out_of_domain(
    fitter: decision.Fitter, response: sim.Response
) -> None:
    truth = response.probabilities(0.70, 0.98, 0.0)
    cov = np.diag(decision.PHI * truth * (1 - truth) / (4 * 13440.0))
    out = decision.decide(fitter, truth, cov, 6.64)
    require(out["departure"] == decision.OUT_OF_DOMAIN, out["departure"])
    require(decision.A_BOX == calibration.NULL_A and decision.S_BOX == calibration.NULL_S)


def prx_ratio() -> float:
    """The fitted PRX ratio of the committed case: the value the decision, the question and these tests share."""
    return float(
        json.loads((NEW / "prediction.json").read_text(encoding="utf-8"))["decisions"]["contrast"]["ratio_prx"]
    )


def test_the_approval_question_states_the_fitted_prx_ratio() -> None:
    cases = json.loads((NEW / "cases.json").read_text(encoding="utf-8"))
    ratio = prx_ratio()
    require(case.question(ratio).count(f"{ratio} times mark 101") == 1, case.question(ratio))
    require(cases["question"] == case.question(ratio))
    require(ratio == pytest.approx(1.194651206, abs=1e-9))


def test_the_mark_contrast_separates_a_cz_phase_from_a_prx_amplitude() -> None:
    ratio = prx_ratio()
    cz = decision.contrast(0.037, 0.004, 0.001, 0.005, ratio)
    prx = decision.contrast(0.037, 0.004, ratio * 0.037, 0.005, ratio)
    flat = decision.contrast(0.037, 0.004, 0.02, 0.02, ratio)
    # a PRX amplitude is rejected only when it is rejected at every ratio of the interval
    wide = decision.contrast(0.037, 0.004, 0.001, 0.005, ratio, ratio_interval=(0.0, 3.0))
    narrow = decision.contrast(0.037, 0.004, 0.001, 0.005, ratio, ratio_interval=(ratio, ratio * 1.01))
    require(wide["reading"] == "unresolved" and wide["z_prx_nearest"] < 3.0, str(wide))
    require(narrow["reading"].startswith("CZ-phase-like") and narrow["ratio_interval"][0] == ratio, str(narrow))
    require(cz["reading"].startswith("CZ-phase-like"), cz["reading"])
    require(prx["reading"].startswith("PRX-like"), prx["reading"])
    require(flat["reading"] == "unresolved", flat["reading"])


@pytest.fixture(scope="module")
def good(fitter: decision.Fitter, response: sim.Response) -> dict[str, Any]:
    return coherent_fit(fitter, response)


def coherent_fit(fitter: decision.Fitter, response: sim.Response) -> dict[str, Any]:
    out = decision.read_pairs(
        fitter, planted(response, response.probabilities(0.97, 0.98, 0.03)), np.zeros(4), np.zeros((4, 4)), 13440, 6.64
    )
    require(out["departure"] == "coherent", out["departure"])
    return out


def contrast_with(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    return decision.mark_contrast({"101": a, "011": b}, prx_ratio())


def test_the_mark_contrast_reads_only_when_both_marks_pass_every_gate(good: dict[str, Any]) -> None:
    read = contrast_with(good, good)
    require(not read["reading"].startswith("not evaluated"), read["reading"])
    require(math.isfinite(read["z_cz"]) and math.isfinite(read["z_prx"]))


@pytest.mark.parametrize("gate", ["pair_floor", "readout", "heterogeneity", "influence", "domain", "rotation"])
def test_a_failed_gate_of_either_mark_removes_its_rotation_fit_from_the_contrast(
    fitter: decision.Fitter, response: sim.Response, good: dict[str, Any], gate: str
) -> None:
    zero, ro = np.zeros(4), np.zeros((4, 4))
    p = response.probabilities(0.97, 0.98, 0.0)
    if gate == "pair_floor":
        failed = decision.read_pairs(fitter, sole_pair_probe(response), zero, ro, 13440, 6.64)
    elif gate == "heterogeneity":
        pairs = planted(response, p)
        pairs[3][0] = ((round((p[2] + 0.03) * 13440), 13440), (round((p[2] + 0.03) * 13440), 13440))
        failed = decision.read_pairs(fitter, pairs, zero, ro, 13440, 6.64)
        require(failed["departure"].startswith("not evaluated: the mirror pairs"), failed["departure"])
    elif gate == "readout":
        failed = decision.fail_gate(dict(good), "not evaluated: a readout preparation kept fewer than half its shots")
    elif gate == "influence":
        failed = decision.fail_gate(dict(good), decision.INFLUENCE_FAIL)
    elif gate == "domain":
        truth = response.probabilities(0.70, 0.98, 0.0)
        failed = decision.decide(fitter, truth, np.diag(decision.PHI * truth * (1 - truth) / (4 * 13440.0)), 6.64)
        require(failed["departure"] == decision.OUT_OF_DOMAIN and "rotation" in failed, failed["departure"])
    else:
        bumped = p + np.array([0.0, -0.05, 0.0, 0.0])
        failed = decision.decide(fitter, bumped, np.diag(decision.PHI * bumped * (1 - bumped) / (4 * 13440.0)), 6.64)
        require(failed["departure"] == decision.NON_ROTATION and "rotation" in failed, failed["departure"])
    for first, second, mark in ((failed, good, "101"), (good, failed, "011")):
        read = contrast_with(first, second)
        require(read["reading"].startswith("not evaluated"), read["reading"])
        require(f"mark {mark}" in read["reading"], read["reading"])
        require(math.isnan(read["z_cz"]) and math.isnan(read["z_prx"]))


def plant_of(case_dir: Path, **mechanism: Any) -> Any:
    import iqm_grover_plane_case as builder

    cal_dir = iqm_sim.Calibration.from_directory(case_dir / "calibration")
    responses = {}
    for mark in ("101", "011"):
        found = {
            k: json.loads(next((case_dir / "circuits").glob(f"m{mark}-k{k}-c0.json")).read_text(encoding="utf-8"))
            for k in (1, 2, 3, 4)
            if next((case_dir / "circuits").glob(f"m{mark}-k{k}-c0.json"), None)
        }
        if found:
            responses[mark] = sim.Response(found, cal_dir, PATH, mark, **mechanism)
    _ = builder

    def plant(name: str, distribution: dict[str, float]) -> dict[str, float]:
        parts = name.split("-")
        if not name.startswith("m"):
            return distribution
        mark, k = parts[0][1:], int(parts[1][1:])
        marked = "".join(mark)
        p = float(responses[mark].probabilities(1.0, 1.0, 0.0)[k - 1])
        rest = 1 - distribution[marked]
        return {key: (p if key == marked else v * (1 - p) / rest) for key, v in distribution.items()}

    return plant


@pytest.mark.audit
def test_analyze_reads_a_synthetic_collected_record_end_to_end(tmp_path: Path) -> None:
    import iqm_garnet_followup as followup

    import grover_plane_analysis as analysis

    model = followup.synthetic_run(NEW, tmp_path / "model", "grover")
    record = analysis.analyze(model, NEW)
    require(record["schema"] == analysis.SCHEMA and record["case"] == case.CASE)
    require(
        record["decisions"]["101"]["departure"] in ("geometric", "unresolved"), record["decisions"]["101"]["departure"]
    )
    require(record["readout"]["101"]["passed"] and record["readout"]["011"]["passed"])
    cz = followup.synthetic_run(NEW, tmp_path / "cz", "grover", plant_of(NEW, cz_phase=-0.03))
    read = analysis.analyze(cz, NEW)
    require(read["decisions"]["101"]["departure"] == "coherent", read["decisions"]["101"]["departure"])
    require(read["contrast"]["reading"].startswith("CZ-phase-like"), read["contrast"]["reading"])
    prx = followup.synthetic_run(NEW, tmp_path / "prx", "grover", plant_of(NEW, prx_scale=-0.016))
    read = analysis.analyze(prx, NEW)
    require(read["decisions"]["101"]["departure"] == "coherent", read["decisions"]["101"]["departure"])
    require(read["contrast"]["reading"].startswith("PRX-like"), read["contrast"]["reading"])
    mock = followup.synthetic_run(NEW, tmp_path / "mock", "grover", qc="garnet:mock")
    with pytest.raises(analysis.AnalysisError):
        analysis.analyze(mock, NEW)


@pytest.mark.audit
def test_analyze_reads_the_mark_101_case_without_a_contrast(tmp_path: Path) -> None:
    import iqm_garnet_followup as followup

    import grover_plane_analysis as analysis

    model = followup.synthetic_run(NEW_101, tmp_path / "model", "grover")
    record = analysis.analyze(model, NEW_101)
    require(record["case"] == case.CASE_101 and set(record["decisions"]) == {"101"}, str(record["case"]))
    require(
        record["decisions"]["101"]["departure"] in ("geometric", "unresolved"), record["decisions"]["101"]["departure"]
    )
    require(record["contrast"]["reading"].startswith("not evaluated"), record["contrast"]["reading"])
    cz = followup.synthetic_run(NEW_101, tmp_path / "cz", "grover", plant_of(NEW_101, cz_phase=-0.03))
    require(analysis.analyze(cz, NEW_101)["decisions"]["101"]["departure"] == "coherent")
