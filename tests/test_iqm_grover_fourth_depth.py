"""The fourth Grover depth case: the retention families, the mirrored arrangement and the preregistered verdict.

Tests that rebuild the arrangement or read the committed case carry audit; the others compute their input here."""

import json
import math
import shutil
from pathlib import Path
from typing import Any

import iqm_garnet_followup as followup
import iqm_grover_fourth_depth as case
import numpy as np
import pytest
from iqm_jobs import JOB_SECONDS, cancel_threshold_seconds, ceiling_credits, dump
from iqm_platform import sha256

import grover_depth_analysis as analysis
import grover_depth_calibration as calibration
import grover_depth_families as families
import iqm_records

CASE_DIR = Path(__file__).resolve().parent.parent / "results" / "iqm" / "cases" / case.CASE
MODEL = [0.85, 0.77, 0.70, 0.58]
# The mechanics tests fix the threshold; the audit tests read the committed case's calibrated one.
DELTA = 9.0
# The two fits of the retained ratios, decisions.retained of the committed prediction.
GEOMETRIC = {"A": 1.025983, "r": 0.963383}
COHERENT = {"eps": 0.304302, "r": 1.013413}


def counts(lam: list[float], kept: list[int]) -> list[int]:
    return [round(families.probability_of(x, k) * n) for x, k, n in zip(lam, families.DEPTHS, kept, strict=True)]


def test_zero_phase_error_is_the_ideal_rotation() -> None:
    zero = np.zeros(1)
    for k in families.DEPTHS:
        if abs(float(families.oracle_phase_probability(k, zero)[0]) - families.ideal_marked(k)) > 1e-12:
            raise AssertionError(f"depth {k}")
    ideal = [families.ideal_marked(k) for k in families.DEPTHS]
    if [round(x, 3) for x in ideal] != [0.781, 0.945, 0.330, 0.012]:
        raise AssertionError(f"ideal marked probabilities {ideal}")


def test_each_family_recovers_its_own_parameters() -> None:
    ks = families.DEPTHS
    se = [0.01] * 4
    geo = families.fit_geometric(families.geometric_values(GEOMETRIC, ks), se, ks)
    coh = families.fit_coherent(families.coherent_values(COHERENT, ks), se, ks)
    if max(abs(geo["A"] - GEOMETRIC["A"]), abs(geo["r"] - GEOMETRIC["r"])) > 1e-3 or geo["chi2"] > 1e-6:
        raise AssertionError(f"geometric fit {geo}")
    if max(abs(coh["eps"] - COHERENT["eps"]), abs(coh["r"] - COHERENT["r"])) > 1e-3 or coh["chi2"] > 1e-4:
        raise AssertionError(f"coherent fit {coh}")


def test_the_verdict_reads_each_planted_family_and_the_model() -> None:
    kept = [67200, 67200, 67200, 302400]
    cont = {
        "geometric_next": families.geometric_values(GEOMETRIC, [4])[0],
        "coherent_next": families.coherent_values(COHERENT, [4])[0],
    }
    for truth, values, want in (
        ("geometric", families.geometric_values(GEOMETRIC, families.DEPTHS), "geometric"),
        ("coherent", families.coherent_values(COHERENT, families.DEPTHS), "coherent"),
        ("model", [1.0] * 4, "unresolved"),
    ):
        lam = [r * m for r, m in zip(values, MODEL, strict=True)]
        read = families.verdict(counts(lam, kept), kept, MODEL, cont, DELTA)
        if read["family"] != want:
            raise AssertionError(f"planted {truth}: {read['family']}, delta {read['delta_chi2']}")
    bent = [0.85, 0.77, 0.55, 0.58]
    read = families.verdict(counts(bent, kept), kept, MODEL, cont, DELTA)
    if read["bend"]["reading"] != "the retention law bends beyond the model at mirrored positions":
        raise AssertionError(read["bend"])
    if read["family"] != "neither family fits":
        raise AssertionError(read["family"])


@pytest.mark.parametrize("marked", [[1, 2, 3], [-1, 0, 0, 0], [11, 0, 0, 0]])
def test_the_verdict_refuses_malformed_counts(marked: list[int]) -> None:
    with pytest.raises(ValueError, match="marked count"):
        families.verdict(marked, [10, 10, 10, 10][: len(marked)], MODEL, {}, DELTA)


@pytest.mark.audit
def test_every_depth_sits_at_mirrored_positions() -> None:
    order = case.arrangement()
    total = len(order)
    if order != order[::-1] or total != sum(case.COPIES.values()) + case.READOUTS:
        raise AssertionError("the arrangement is not a palindrome of the job's circuits")
    for k, n in case.COPIES.items():
        at = [p for p, depth in enumerate(order) if depth == k]
        if len(at) != n or sum(at) != n * (total - 1) / 2:
            raise AssertionError(f"depth {k}: positions {at}")
    readout = [p for p, depth in enumerate(order) if depth == 0]
    if readout != list(range(readout[0], readout[0] + case.READOUTS)) or readout[0] * 2 + case.READOUTS != total:
        raise AssertionError(f"readout block {readout}")


@pytest.mark.audit
def test_the_committed_case_binds_a_resolved_prediction_and_a_bounded_cost() -> None:
    cases = json.loads((CASE_DIR / "cases.json").read_text(encoding="utf-8"))
    prediction_text = (CASE_DIR / "prediction.json").read_text(encoding="utf-8")
    if cases["prediction_sha256"] != sha256(prediction_text.encode()):
        raise AssertionError("cases.json does not bind prediction.json")
    prediction = json.loads(prediction_text)
    z = prediction["decisions"]["continuation"]["z"]
    if abs(z) < families.Z_RESOLVE:
        raise AssertionError(f"depth 4 continuations separate by {z} standard errors")
    (job,) = cases["jobs"]
    if len(job["circuits"]) != len(prediction["arms"]) or job["shots"] > 20000 or len(job["circuits"]) > 100:
        raise AssertionError("the job exceeds Garnet's limits or leaves an arm unpredicted")
    ceiling = ceiling_credits(job["expected_seconds"], case.PRICE["garnet"], JOB_SECONDS)
    approved = job["max_credits"]["garnet"]
    if not ceiling < approved or job["max_credits"]["garnet:mock"] != 0:
        raise AssertionError(f"ceiling {ceiling} credits, approved {approved}")
    if cancel_threshold_seconds(approved, case.PRICE["garnet"]) < JOB_SECONDS + job["expected_seconds"]:
        raise AssertionError("the cancel threshold lies below the expected runtime")
    names = [Path(c["file"]).stem for c in job["circuits"]]
    if names != sorted(prediction["arms"], key=lambda n: prediction["arms"][n]["position"]):
        raise AssertionError("the job's circuit order differs from the prediction's positions")


def test_one_unusable_depth_leaves_the_other_decision_standing() -> None:
    kept = [67200, 67200, 67200, 302400]
    values = families.coherent_values(COHERENT, families.DEPTHS)
    lam = [r * m for r, m in zip(values, MODEL, strict=True)]
    marked = counts(lam, kept)
    cont = {"geometric_next": 0.9, "coherent_next": 0.9}
    no4 = families.verdict([*marked[:3], 0], [*kept[:3], 0], MODEL, cont, DELTA)
    if no4["usable_depths"] != [1, 2, 3] or "bend" not in no4 or no4["family"] not in {"coherent", "unresolved"}:
        raise AssertionError(no4)
    if (
        "z_against_model" not in no4["bend"]
        or "beside" not in no4
        or "rho4_against_retained_geometric_z" in no4["beside"]
    ):
        raise AssertionError(no4)
    no3 = families.verdict([marked[0], marked[1], 0, marked[3]], [kept[0], kept[1], 0, kept[3]], MODEL, cont, DELTA)
    if no3["bend"]["reading"] != "not evaluated: a depth of 1, 2 or 3 is unusable" or no3["family"] == "not evaluated":
        raise AssertionError(no3)
    two = families.verdict([marked[0], 0, 0, marked[3]], [kept[0], 0, 0, kept[3]], MODEL, cont, DELTA)
    if not two["family"].startswith("not evaluated"):
        raise AssertionError(two)


def gate_from(prediction: dict[str, Any]) -> dict[str, Any]:
    return {k: prediction["decisions"]["heterogeneity"][k] for k in ("copy_floor", "threshold_by_dof")}


@pytest.mark.audit
def test_a_failed_copy_leaves_its_depth_with_its_mirror_image() -> None:
    prediction = json.loads((CASE_DIR / "prediction.json").read_text(encoding="utf-8"))
    cont = {"geometric_next": 0.9, "coherent_next": 0.9}
    total = len(prediction["arms"])
    copies = case.layout_copies(MODEL, tweak=lambda k, p, m, n: (m // 20, n // 20) if (k, p) == (1, 2) else (m, n))
    read = families.read_copies(copies, total, case.PLANNED_KEPT_PER_COPY, MODEL, cont, gate_from(prediction), DELTA)
    if read["dropped_pairs"] != {"1": [[2, 35]]} or read["heterogeneity"]["per_depth"]["1"]["pairs"] != 1:
        raise AssertionError(read)
    if not read["heterogeneity"]["passed"] or read["usable_depths"] != [1, 2, 3, 4]:
        raise AssertionError(read)
    with pytest.raises(ValueError, match="no mirror image"):
        families.read_copies(
            {**copies, 1: [(2, 100, 200)]},
            total,
            case.PLANNED_KEPT_PER_COPY,
            MODEL,
            cont,
            gate_from(prediction),
            DELTA,
        )


@pytest.mark.audit
def test_one_raised_copy_reads_not_evaluated_where_the_pooled_rule_read_geometric() -> None:
    prediction = json.loads((CASE_DIR / "prediction.json").read_text(encoding="utf-8"))
    cont = {"geometric_next": prediction["decisions"]["retained"]["geometric_rho_4"], "coherent_next": 0.9}
    total = len(prediction["arms"])
    plus = case.layout_copies(MODEL, tweak=lambda k, p, m, n: (m + round(0.04 * n), n) if (k, p) == (1, 2) else (m, n))
    read = families.read_copies(plus, total, case.PLANNED_KEPT_PER_COPY, MODEL, cont, gate_from(prediction), DELTA)
    heterogeneity = read["heterogeneity"]
    if heterogeneity["passed"] or heterogeneity["chi2"] <= heterogeneity["threshold"]:
        raise AssertionError(heterogeneity)
    if not (read["bend"]["reading"].startswith("not evaluated") and read["family"].startswith("not evaluated")):
        raise AssertionError(read)
    pooled = [sum(c[1] for c in plus[k]) for k in families.DEPTHS]
    kept = [sum(c[2] for c in plus[k]) for k in families.DEPTHS]
    if families.verdict(pooled, kept, MODEL, cont, DELTA)["family"] == "unresolved":
        raise AssertionError("the pooled counts no longer carry the one-copy artifact the gate catches")


def planted_fit(family: str, rate: float) -> str:
    kept = [67200, 67200, 67200, 302400]
    cont = {"geometric_next": 0.9, "coherent_next": 0.9}
    if family == "geometric":
        values = families.geometric_values({"A": 0.5, "r": rate}, families.DEPTHS)
    else:
        values = families.coherent_values({"eps": 0.3, "r": rate}, families.DEPTHS)
    lam = [r * m for r, m in zip(values, MODEL, strict=True)]
    return str(families.verdict(counts(lam, kept), kept, MODEL, cont, DELTA)["family"])


@pytest.mark.parametrize(
    ("family", "rate"),
    [
        ("geometric", 1.19),
        ("coherent", 1.09),
        ("geometric", 0.8),
        ("coherent", 0.6),
        # The coherent fit of exact geometric data of amplitude 0.5 ends on its rate bound of 0.5 at and below these
        # rates, and a losing bound-limited fit does not void the exact fit of the other family.
        ("geometric", 0.7),
        ("geometric", 0.6),
        ("geometric", 0.5),
        ("geometric", 0.4),
    ],
)
def test_data_inside_the_rate_bounds_read_their_family(family: str, rate: float) -> None:
    if planted_fit(family, rate) != family:
        raise AssertionError(f"{family} at {rate} reads {planted_fit(family, rate)}")


@pytest.mark.parametrize(("family", "rate"), [("coherent", 0.52)])
def test_data_just_inside_a_lower_rate_bound_stay_in_domain(family: str, rate: float) -> None:
    if planted_fit(family, rate).startswith("out of domain"):
        raise AssertionError(f"{family} at {rate} reads {planted_fit(family, rate)}")


@pytest.mark.parametrize(
    ("family", "rate"), [("geometric", 1.25), ("geometric", 0.28), ("coherent", 1.11), ("coherent", 0.48)]
)
def test_data_outside_a_rate_bound_read_out_of_domain_not_neither_family(family: str, rate: float) -> None:
    reading = planted_fit(family, rate)
    if not (reading.startswith("out of domain") and family in reading):
        raise AssertionError(f"{family} at {rate} reads {reading}")


@pytest.mark.audit
def test_the_committed_gate_holds_the_chi_square_quantile_of_every_degree_of_freedom() -> None:
    prediction = json.loads((CASE_DIR / "prediction.json").read_text(encoding="utf-8"))
    gate = prediction["decisions"]["heterogeneity"]
    from scipy import stats

    positions = case.depth_positions(prediction["arms"])
    planned = sum(len(x) // 2 - 1 for x in positions.values())
    if gate["planned_dof"] != planned or sorted(gate["threshold_by_dof"], key=int) != [
        str(d) for d in range(1, planned + 1)
    ]:
        raise AssertionError(gate["planned_dof"])
    for dof, value in gate["threshold_by_dof"].items():
        if abs(value - float(stats.chi2.isf(gate["alpha"], int(dof)))) > 1e-6:
            raise AssertionError(f"dof {dof}: {value}")
    power = gate["power"]
    # Linear drift moves no mirror pair, so the gate fires at its false-alarm level there.
    for key in (
        "probability_under_linear_drift_in_retention_at_the_retained_slope",
        "probability_under_linear_drift_in_marked_frequency_at_the_retained_slope",
    ):
        if abs(power[key] - gate["alpha"]) > 1e-6:
            raise AssertionError(f"{key}: {power[key]}")
    if not 0.5 < power["probability_for_one_copy_of_depth_1_raised_by_0.04"] <= 1.0:
        raise AssertionError(power)
    if (
        not power["one_copy_of_depth_1_shift_at_half_power"]
        < 0.04
        < power["one_copy_of_depth_1_shift_at_nine_tenths_power"] * 2
    ):
        raise AssertionError(power)


@pytest.mark.audit
def test_the_fixed_arrangement_is_the_exhaustive_search_optimum() -> None:
    if case.best_first_half() != case.FIRST_HALF:
        raise AssertionError(case.best_first_half())
    case.verify_first_half(case.FIRST_HALF)


def drifted(distribution: dict[str, float], delta: float) -> dict[str, float]:
    """The distribution with the mark's probability moved by delta and the other outcomes scaled to keep the sum."""
    p = distribution[case.MARKED] + delta
    scale = (1 - p) / (1 - distribution[case.MARKED])
    return {k: (p if k == case.MARKED else v * scale) for k, v in distribution.items()}


def run_of(tmp_path: Path, name: str, **plants: Any) -> Path:
    return followup.synthetic_run(CASE_DIR, tmp_path / name, "grover", **plants)


@pytest.mark.audit
def test_the_model_device_reads_no_bend_and_an_unresolved_family(tmp_path: Path) -> None:
    record = case.analyze(run_of(tmp_path, "model"))
    decisions = record["decisions"]
    if decisions["bend"]["reading"] != "no bend beyond the model resolved at mirrored positions":
        raise AssertionError(decisions["bend"])
    if decisions["family"] != "unresolved" or not decisions["heterogeneity"]["passed"] or decisions["dropped_pairs"]:
        raise AssertionError(decisions)
    names = [row["name"] for row in record["circuits"]]
    if names != sorted(
        names, key=lambda n: json.loads((CASE_DIR / "prediction.json").read_text())["arms"][n]["position"]
    ):
        raise AssertionError("the record lists circuits out of position")
    depth_digests = {row["depth"]: row["circuit_sha256"] for row in record["circuits"] if "depth" in row}
    if len(depth_digests) != 4 or len(set(depth_digests.values())) != 4:
        raise AssertionError(depth_digests)


@pytest.mark.audit
def test_a_copy_raised_by_four_points_reads_not_evaluated_on_raw_counts(tmp_path: Path) -> None:
    def plant(name: str, distribution: dict[str, float]) -> dict[str, float]:
        return drifted(distribution, 0.04) if name == "m101-k1-c0" else distribution

    decisions = case.analyze(run_of(tmp_path, "raised", plant=plant))["decisions"]
    if not (
        decisions["bend"]["reading"].startswith("not evaluated") and decisions["family"].startswith("not evaluated")
    ):
        raise AssertionError(decisions)
    if decisions["heterogeneity"]["passed"]:
        raise AssertionError(decisions["heterogeneity"])


def slope_plant(position: dict[str, int], center: float, per_position: float, depths: str, power: int) -> Any:
    """A drift of the marked frequency of the depths named: per_position times the offset from center ** power."""

    def plant(name: str, distribution: dict[str, float]) -> dict[str, float]:
        drifting = name.startswith("m101-k") and name[6] in depths
        return drifted(distribution, per_position * (position[name] - center) ** power) if drifting else distribution

    return plant


@pytest.mark.audit
def test_a_dropped_copy_and_a_linear_slope_read_the_centered_verdict(tmp_path: Path) -> None:
    """A failed copy leaves with its image, so the surviving positions stay centered and a linear slope cancels in
    every pair. A depth that keeps several pairs reads the centered verdict; a depth left with one pair cannot lose it
    without becoming unusable, so the influence check reads its decisions as not evaluated, never as a bend."""
    prediction = json.loads((CASE_DIR / "prediction.json").read_text(encoding="utf-8"))
    position = {n: a["position"] for n, a in prediction["arms"].items()}
    center = (len(position) - 1) / 2
    centered = "no bend beyond the model resolved at mirrored positions"
    changed = "not evaluated: the reading depends on one mirror pair"
    for victim, depth, bend in (("m101-k4-c0", "4", centered), ("m101-k1-c0", "1", changed)):
        pair = [position[victim], len(position) - 1 - position[victim]]

        def short(name: str, victim: str = victim) -> int:
            return 2000 if name == victim else 17120

        for per_position, depths in ((-0.005, "123"), (-0.00003, "1234")):
            plant = slope_plant(position, center, per_position, depths, 1)
            read = case.analyze(run_of(tmp_path, f"slope{depths}{depth}", plant=plant, kept_of=short))["decisions"]
            if read["dropped_pairs"] != {depth: [pair]} or not read["heterogeneity"]["passed"]:
                raise AssertionError(read)
            if read["bend"]["reading"] != bend:
                raise AssertionError(read["bend"])
            if depth == "4" and abs(read["bend"]["z_against_model"]) > 1.0:
                raise AssertionError(read["bend"])


@pytest.mark.audit
def test_a_symmetric_quadratic_drift_reads_not_evaluated(tmp_path: Path) -> None:
    prediction = json.loads((CASE_DIR / "prediction.json").read_text(encoding="utf-8"))
    position = {n: a["position"] for n, a in prediction["arms"].items()}
    center = (len(position) - 1) / 2
    plant = slope_plant(position, center, -0.0003, "123", 2)
    read = case.analyze(run_of(tmp_path, "quadratic", plant=plant))["decisions"]
    if read["heterogeneity"]["passed"] or not read["bend"]["reading"].startswith("not evaluated"):
        raise AssertionError(read)


@pytest.mark.audit
def test_a_mock_run_a_foreign_prediction_and_another_calibration_are_refused(tmp_path: Path) -> None:
    for label, plants, fragment in (
        ("mock", {"qc": "garnet:mock"}, "not a"),
        ("unbound", {"prediction_edit": "unbound"}, "prediction.json"),
        ("rebound", {"prediction_edit": "rebound"}, "another prediction digest"),
        ("calibration", {"calibration": "another-calibration-set"}, "calibration set"),
    ):
        with pytest.raises((analysis.AnalysisError, iqm_records.RecordError), match=fragment):
            case.analyze(run_of(tmp_path, label, **plants))


def tampered_case(tmp_path: Path, edit: Any) -> Path:
    """A copy of the case whose prediction (and the circuit files it names) edit changed, rebound so that the copy
    is self-consistent: the run built on it passes the shared record checks and meets the analyzer's own."""
    target = tmp_path / "case"
    shutil.copytree(CASE_DIR, target, ignore=shutil.ignore_patterns("calibration"))
    prediction = json.loads((target / "prediction.json").read_text(encoding="utf-8"))
    cases = json.loads((target / "cases.json").read_text(encoding="utf-8"))
    edit(prediction, target)
    (target / "prediction.json").write_text(dump(prediction), encoding="utf-8")
    cases["prediction_sha256"] = sha256((target / "prediction.json").read_bytes())
    for row in cases["jobs"][0]["circuits"]:
        row["sha256"] = sha256((target / row["file"]).read_bytes())
    (target / "cases.json").write_text(dump(cases), encoding="utf-8")
    return target


def swap_position(prediction: dict[str, Any], target: Path) -> None:
    prediction["arms"]["m101-k1-c0"]["position"] = 0


def mislabel_depth(prediction: dict[str, Any], target: Path) -> None:
    prediction["arms"]["m101-k1-c0"]["iterations"] = 2


def swap_circuit(prediction: dict[str, Any], target: Path) -> None:
    other = json.loads((target / "circuits" / "m101-k2-c0.json").read_text(encoding="utf-8"))
    other["name"] = "m101-k1-c0"
    (target / "circuits" / "m101-k1-c0.json").write_text(dump(other), encoding="utf-8")


@pytest.mark.audit
@pytest.mark.parametrize(
    ("edit", "fragment"),
    [
        (swap_position, "not the prediction's"),
        (mislabel_depth, "line-native Grover"),
        (swap_circuit, "line-native Grover"),
    ],
)
def test_the_analyzer_binds_depth_and_position_to_each_circuit(tmp_path: Path, edit: Any, fragment: str) -> None:
    folder = tampered_case(tmp_path, edit)
    run = followup.synthetic_run(folder, tmp_path / "run", "grover")
    with pytest.raises(analysis.AnalysisError, match=fragment):
        analysis.analyze(run, folder)


@pytest.mark.audit
def test_a_live_build_regenerates_the_case_from_the_calibration_it_reads(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = CASE_DIR / "calibration"

    def stand_in(calibration_dir: Path) -> None:
        for name in case.CALIBRATION_FILES:
            (calibration_dir / name).write_bytes((source / name).read_bytes())

    monkeypatch.setattr(case, "fetch_live", stand_in)
    case.write(tmp_path, None, live=True)
    case.check(tmp_path)
    for name in ("cases.json", "prediction.json"):
        if (tmp_path / name).read_bytes() != (CASE_DIR / name).read_bytes():
            raise AssertionError(f"{name} differs from the committed build on the same calibration")
    with pytest.raises(ValueError, match="exactly one"):
        case.write(tmp_path, source, live=True)
    with pytest.raises(ValueError, match="exactly one"):
        case.write(tmp_path, None, live=False)


def fit_of(chi2: float, at_bound: bool) -> dict[str, Any]:
    return {"chi2": chi2, "at_bound": at_bound}


def test_a_rate_bound_blocks_a_reading_only_when_the_bound_limited_fit_is_what_it_rests_on() -> None:
    select = families.select_family
    # A losing bound-limited fit beside an adequate interior winner: the winner stands, the bound is reported.
    for geo, coh, want, bounded in (
        (fit_of(0.0, False), fit_of(1822.0, True), "geometric", ["coherent"]),
        (fit_of(1822.0, True), fit_of(0.0, False), "coherent", ["geometric"]),
    ):
        if select(geo, coh, 2, DELTA) != (want, bounded):
            raise AssertionError(select(geo, coh, 2, DELTA))
    # The bound-limited fit is the winner, or the claim that neither family fits rests on it: out of domain.
    for geo, coh, name in (
        (fit_of(1822.0, False), fit_of(0.0, True), "coherent"),
        (fit_of(0.0, True), fit_of(1822.0, False), "geometric"),
        (fit_of(50.0, False), fit_of(60.0, True), "coherent"),
        (fit_of(2.0, False), fit_of(3.0, True), "coherent"),
    ):
        reading, bounded = select(geo, coh, 2, DELTA)
        if not reading.startswith("out of domain") or name not in reading or name not in bounded:
            raise AssertionError((reading, bounded))
    reading, _ = select(fit_of(50.0, True), fit_of(60.0, True), 2, DELTA)
    if reading != "out of domain: the geometric and coherent fits end on their rate bounds":
        raise AssertionError(reading)


def test_a_coherent_winner_stands_beside_a_geometric_fit_on_its_rate_bound() -> None:
    kept = [67200, 67200, 67200, 302400]
    cont = {"geometric_next": 0.9, "coherent_next": 0.9}
    values = families.coherent_values({"eps": 1.5, "r": 0.9}, families.DEPTHS)
    lam = [r * m for r, m in zip(values, MODEL, strict=True)]
    read = families.verdict(counts(lam, kept), kept, MODEL, cont, DELTA)
    if read["family"] != "coherent" or read["beside"]["fits_on_a_rate_bound"] != ["geometric"]:
        raise AssertionError(read)
    if not read["geometric"]["at_bound"] or read["coherent"]["at_bound"]:
        raise AssertionError(read)


def test_the_readout_shift_moves_each_depth_by_its_weight_and_ties_the_depths() -> None:
    weights = [[0.5, 0.5, 0.0], [0.2, 0.8, 0.0], [0.0, 0.5, 0.5], [1 / 3, 1 / 3, 1 / 3]]
    shift = families.readout_shift(weights, [0.9, 0.1, 0.0], [0.88, 0.1, 0.0], [1000.0] * 3)
    if not np.allclose(shift.shift, [-0.01, -0.004, 0.0, -0.02 / 3]):
        raise AssertionError(shift.shift)
    variance = 0.88 * 0.12 / 1000 + 0.1 * 0.9 / 1000
    if not np.isclose(shift.cov[0, 3], 0.5 * (1 / 3) * variance) or not np.allclose(shift.cov, shift.cov.T):
        raise AssertionError(shift.cov)
    if np.min(np.linalg.eigvalsh(shift.cov)) < -1e-18:
        raise AssertionError("the readout covariance is not positive semidefinite")
    # The correction subtracts the shift from the observed frequencies: counts that read 0.01 below the model at a
    # depth whose preparation row fell by 0.02 read at the model once corrected.
    kept = [67200, 67200, 67200, 302400]
    cont = {"geometric_next": 0.9, "coherent_next": 0.9}
    model_p = [families.probability_of(m, k) for m, k in zip(MODEL, families.DEPTHS, strict=True)]
    marked = [round((p + s) * n) for p, s, n in zip(model_p, shift.shift, kept, strict=True)]
    read = families.verdict(marked, kept, MODEL, cont, DELTA, shift)
    if abs(read["lambda"]["1"] - MODEL[0]) > 1e-4 or read["bend"]["reading"].startswith("the retention law bends"):
        raise AssertionError(read)


def test_the_quadrature_points_are_deterministic_and_centered() -> None:
    first = calibration.sobol_normals(4, 6)
    if first.shape != (64, 4) or not np.array_equal(first, calibration.sobol_normals(4, 6)):
        raise AssertionError(first.shape)
    if np.max(np.abs(first.mean(axis=0))) > 0.05 or np.max(np.abs(first.std(axis=0) - 1)) > 0.1:
        raise AssertionError((first.mean(axis=0), first.std(axis=0)))


def case_inputs(prediction: dict[str, Any]) -> tuple[list[float], families.ReadoutShift, dict[str, list[float]]]:
    plan = prediction["decisions"]["readout"]
    readout = families.readout_shift(
        plan["q"], plan["r_model"], plan["r_model"], [case.PLANNED_KEPT_PER_COPY] * case.READOUTS
    )
    truths = {n: v["ratios"] for n, v in prediction["decisions"]["calibration"]["truths"].items()}
    return families.model_retention(prediction["arms"]), readout, truths


@pytest.mark.audit
def test_the_committed_threshold_holds_every_misclassification_at_the_stated_rate() -> None:
    prediction = json.loads((CASE_DIR / "prediction.json").read_text(encoding="utf-8"))
    cal = prediction["decisions"]["calibration"]
    threshold = cal["delta_resolve"]
    if threshold != prediction["decisions"]["continuation"]["delta_resolve"] or threshold not in cal["grid"]:
        raise AssertionError(threshold)
    j = cal["grid"].index(threshold)
    below = []
    for name, truth in cal["truths"].items():
        for rates in (truth["wrong_family_by_grid"], truth["first_half_wrong_family_by_grid"]):
            if not rates[j] <= cal["stated_rate"]:
                raise AssertionError(f"{name}: {rates[j]} at {threshold}")
            below.append(j == 0 or rates[j - 1] <= cal["stated_rate"])
    if all(below):
        raise AssertionError("the threshold is not the smallest that holds the stated rate")
    wrong = (
        cal["truths"]["geometric"]["at_delta_resolve"]["coherent"],
        cal["truths"]["coherent"]["at_delta_resolve"]["geometric"],
    )
    if max(wrong) > cal["stated_rate"]:
        raise AssertionError(wrong)
    power = cal["influence_power"]
    for name, entry in power.items():
        if isinstance(entry, dict) and "family_power_pooled" in entry:
            if entry["family_power_with_every_leave_one_out"] > entry["family_power_pooled"] + 1e-12:
                raise AssertionError((name, entry))


@pytest.mark.audit
def test_the_calibration_replays_its_first_half_points() -> None:
    prediction = json.loads((CASE_DIR / "prediction.json").read_text(encoding="utf-8"))
    cal = prediction["decisions"]["calibration"]
    model, readout, truths = case_inputs(prediction)
    retained = {"geometric_next": 0.0, "coherent_next": 0.0}
    log2n = int(math.log2(cal["points"])) - 1
    replay = calibration.calibrate(model, retained, truths, readout, case.planned_kept(), log2n)
    for name, truth in cal["truths"].items():
        # prediction.json holds its inputs to six digits, so a replay may move a point or two across a boundary.
        got, want = replay["truths"][name]["wrong_family_by_grid"], truth["first_half_wrong_family_by_grid"]
        if not np.allclose(got, want, atol=3 / cal["points"] * 2):
            raise AssertionError((name, got, want))


def readout_plant(prediction: dict[str, Any], row_drop: float) -> Any:
    """A job whose marked row of the assignment matrix lies row_drop below the model's at the marked preparation: the
    readout preparation of the mark reads row_drop lower, and each depth reads row_drop times its weight on that
    preparation lower, the way the readout reaches every circuit."""
    plan = prediction["decisions"]["readout"]

    def plant(name: str, distribution: dict[str, float]) -> dict[str, float]:
        if name == "ro-" + case.MARKED:
            return drifted(distribution, -row_drop)
        if name.startswith("m101-k"):
            return drifted(distribution, -row_drop * plan["q"][int(name[6]) - 1][plan["marked_index"]])
        return distribution

    return plant


@pytest.mark.audit
def test_a_readout_row_mismatch_reads_no_bend_once_the_job_readout_corrects_it(tmp_path: Path) -> None:
    prediction = json.loads((CASE_DIR / "prediction.json").read_text(encoding="utf-8"))
    row_drop = 0.1
    record = case.analyze(run_of(tmp_path, "readout", plant=readout_plant(prediction, row_drop)))
    read = record["decisions"]
    if read["bend"]["reading"] != "no bend beyond the model resolved at mirrored positions":
        raise AssertionError(read["bend"])
    if read["family"] != "unresolved" or not read["heterogeneity"]["passed"]:
        raise AssertionError(read)
    shift = record["readout"]["frequency_shift"]
    plan = prediction["decisions"]["readout"]
    weights = [plan["q"][k][plan["marked_index"]] for k in range(4)]
    if not np.allclose(shift, [-row_drop * w for w in weights], atol=2e-4):
        raise AssertionError((shift, weights))
    # The same counts read without the readout correction are a resolved bend: the plant is not vacuous.
    rows = [r for r in record["circuits"] if "depth" in r]
    marked = [sum(r["marked"] for r in rows if r["depth"] == k) for k in families.DEPTHS]
    kept = [sum(r["kept_shots"] for r in rows if r["depth"] == k) for k in families.DEPTHS]
    model = families.model_retention(prediction["arms"])
    retained = {"geometric_next": 0.9, "coherent_next": 0.9}
    delta = prediction["decisions"]["calibration"]["delta_resolve"]
    raw = families.verdict(marked, kept, model, retained, delta)
    if not raw["bend"]["reading"].startswith("the retention law bends"):
        raise AssertionError(raw["bend"])


@pytest.mark.audit
def test_one_depth_3_copy_lowered_by_three_points_passes_the_gate_and_reads_not_evaluated(tmp_path: Path) -> None:
    prediction = json.loads((CASE_DIR / "prediction.json").read_text(encoding="utf-8"))
    (victim,) = [n for n, a in prediction["arms"].items() if a["position"] == 4]
    if not victim.startswith("m101-k3-c"):
        raise AssertionError(victim)

    def plant(name: str, distribution: dict[str, float]) -> dict[str, float]:
        return drifted(distribution, -0.03) if name == victim else distribution

    read = case.analyze(run_of(tmp_path, "lowered", plant=plant))["decisions"]
    heterogeneity = read["heterogeneity"]
    if not heterogeneity["passed"] or heterogeneity["chi2"] > 0.9 * heterogeneity["threshold"]:
        raise AssertionError(heterogeneity)
    changed = "not evaluated: the reading depends on one mirror pair"
    if read["bend"]["reading"] != changed or read["family"] != changed:
        raise AssertionError(read)
    influence = read["influence"]
    if influence["bend_stands"] or influence["family_stands"]:
        raise AssertionError(influence)
    if not influence["bend_before"].startswith("the retention law bends beyond") or influence["family_before"] != (
        "coherent"
    ):
        raise AssertionError(influence)
    moved = [row for row in influence["refits"] if row["bend"] != "beyond" or row["family"] != "coherent"]
    if [row["depth"] for row in moved] != [3] or moved[0]["positions"] != [4, 33]:
        raise AssertionError(moved)
