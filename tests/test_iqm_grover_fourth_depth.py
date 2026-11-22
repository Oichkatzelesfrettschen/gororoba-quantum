"""The fourth Grover depth case: the retention families, the mirrored arrangement and the preregistered verdict.

Tests that rebuild the arrangement or read the committed case carry audit; the others compute their input here."""

import json
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
import grover_depth_families as families
import iqm_records

CASE_DIR = Path(__file__).resolve().parent.parent / "results" / "iqm" / "cases" / case.CASE
MODEL = [0.85, 0.77, 0.70, 0.58]
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
        read = families.verdict(counts(lam, kept), kept, MODEL, cont)
        if read["family"] != want:
            raise AssertionError(f"planted {truth}: {read['family']}, delta {read['delta_chi2']}")
    bent = [0.85, 0.77, 0.55, 0.58]
    read = families.verdict(counts(bent, kept), kept, MODEL, cont)
    if read["bend"]["reading"] != "the retention law bends beyond the model at mirrored positions":
        raise AssertionError(read["bend"])
    if read["family"] != "neither family fits":
        raise AssertionError(read["family"])


@pytest.mark.parametrize("marked", [[1, 2, 3], [-1, 0, 0, 0], [11, 0, 0, 0]])
def test_the_verdict_refuses_malformed_counts(marked: list[int]) -> None:
    with pytest.raises(ValueError, match="marked count"):
        families.verdict(marked, [10, 10, 10, 10][: len(marked)], MODEL, {})


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
    no4 = families.verdict([*marked[:3], 0], [*kept[:3], 0], MODEL, cont)
    if no4["usable_depths"] != [1, 2, 3] or "bend" not in no4 or no4["family"] not in {"coherent", "unresolved"}:
        raise AssertionError(no4)
    if (
        "z_against_model" not in no4["bend"]
        or "beside" not in no4
        or "rho4_against_retained_geometric_z" in no4["beside"]
    ):
        raise AssertionError(no4)
    no3 = families.verdict([marked[0], marked[1], 0, marked[3]], [kept[0], kept[1], 0, kept[3]], MODEL, cont)
    if no3["bend"]["reading"] != "not evaluated: a depth of 1, 2 or 3 is unusable" or no3["family"] == "not evaluated":
        raise AssertionError(no3)
    two = families.verdict([marked[0], 0, 0, marked[3]], [kept[0], 0, 0, kept[3]], MODEL, cont)
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
    read = families.read_copies(copies, total, case.PLANNED_KEPT_PER_COPY, MODEL, cont, gate_from(prediction))
    if read["dropped_pairs"] != {"1": [[2, 35]]} or read["heterogeneity"]["per_depth"]["1"]["copies"] != 2:
        raise AssertionError(read)
    if not read["heterogeneity"]["passed"] or read["usable_depths"] != [1, 2, 3, 4]:
        raise AssertionError(read)
    with pytest.raises(ValueError, match="no mirror image"):
        families.read_copies(
            {**copies, 1: [(2, 100, 200)]}, total, case.PLANNED_KEPT_PER_COPY, MODEL, cont, gate_from(prediction)
        )


@pytest.mark.audit
def test_one_raised_copy_reads_not_evaluated_where_the_pooled_rule_read_geometric() -> None:
    prediction = json.loads((CASE_DIR / "prediction.json").read_text(encoding="utf-8"))
    cont = {"geometric_next": prediction["decisions"]["retained"]["geometric_rho_4"], "coherent_next": 0.9}
    total = len(prediction["arms"])
    plus = case.layout_copies(MODEL, tweak=lambda k, p, m, n: (m + round(0.04 * n), n) if (k, p) == (1, 2) else (m, n))
    read = families.read_copies(plus, total, case.PLANNED_KEPT_PER_COPY, MODEL, cont, gate_from(prediction))
    heterogeneity = read["heterogeneity"]
    if heterogeneity["passed"] or heterogeneity["chi2"] <= heterogeneity["threshold"]:
        raise AssertionError(heterogeneity)
    if not (read["bend"]["reading"].startswith("not evaluated") and read["family"].startswith("not evaluated")):
        raise AssertionError(read)
    pooled = [sum(c[1] for c in plus[k]) for k in families.DEPTHS]
    kept = [sum(c[2] for c in plus[k]) for k in families.DEPTHS]
    if families.verdict(pooled, kept, MODEL, cont)["family"] == "unresolved":
        raise AssertionError("the pooled counts no longer carry the one-copy artifact the gate catches")


def planted_fit(family: str, rate: float) -> str:
    kept = [67200, 67200, 67200, 302400]
    cont = {"geometric_next": 0.9, "coherent_next": 0.9}
    if family == "geometric":
        values = families.geometric_values({"A": 0.5, "r": rate}, families.DEPTHS)
    else:
        values = families.coherent_values({"eps": 0.3, "r": rate}, families.DEPTHS)
    lam = [r * m for r, m in zip(values, MODEL, strict=True)]
    return str(families.verdict(counts(lam, kept), kept, MODEL, cont)["family"])


@pytest.mark.parametrize(
    ("family", "rate"), [("geometric", 1.19), ("coherent", 1.09), ("geometric", 0.8), ("coherent", 0.6)]
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
    planned = sum(len(x) - 1 for x in positions.values())
    if gate["planned_dof"] != planned or sorted(gate["threshold_by_dof"], key=int) != [
        str(d) for d in range(1, planned + 1)
    ]:
        raise AssertionError(gate["planned_dof"])
    for dof, value in gate["threshold_by_dof"].items():
        if abs(value - float(stats.chi2.isf(gate["alpha"], int(dof)))) > 1e-6:
            raise AssertionError(f"dof {dof}: {value}")
    power = gate["power"]
    if not 0.0 < power["probability_at_half_the_retained_slope"] < power["probability_at_the_retained_slope"] < 1.0:
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


@pytest.mark.audit
def test_a_dropped_copy_and_a_linear_slope_read_not_evaluated_or_the_centered_verdict(tmp_path: Path) -> None:
    prediction = json.loads((CASE_DIR / "prediction.json").read_text(encoding="utf-8"))
    position = {n: a["position"] for n, a in prediction["arms"].items()}
    center = (len(position) - 1) / 2

    def slope(per_position: float, depths: str) -> Any:
        def plant(name: str, distribution: dict[str, float]) -> dict[str, float]:
            drifting = name.startswith("m101-k") and name[6] in depths
            return drifted(distribution, per_position * (position[name] - center)) if drifting else distribution

        return plant

    def short(name: str) -> int:
        return 2000 if name == "m101-k1-c0" else 17120

    steep = case.analyze(run_of(tmp_path, "steep", plant=slope(-0.005, "123"), kept_of=short))["decisions"]
    if steep["dropped_pairs"] != {"1": [[2, 35]]} or not steep["bend"]["reading"].startswith("not evaluated"):
        raise AssertionError(steep)
    gentle = case.analyze(run_of(tmp_path, "gentle", plant=slope(-0.00003, "1234"), kept_of=short))["decisions"]
    if gentle["dropped_pairs"] != {"1": [[2, 35]]} or not gentle["heterogeneity"]["passed"]:
        raise AssertionError(gentle)
    if (
        gentle["bend"]["reading"] != "no bend beyond the model resolved at mirrored positions"
        or abs(gentle["bend"]["z_against_model"]) > 1.0
    ):
        raise AssertionError(gentle["bend"])


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
