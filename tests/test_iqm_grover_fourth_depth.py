"""The fourth Grover depth case: the retention families, the mirrored arrangement and the preregistered verdict.

Tests that rebuild the arrangement or read the committed case carry audit; the others compute their input here."""

import json
from pathlib import Path

import iqm_grover_fourth_depth as case
import numpy as np
import pytest
from iqm_jobs import JOB_SECONDS, cancel_threshold_seconds, ceiling_credits
from iqm_platform import sha256

import grover_depth_families as families

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


def test_a_failed_copy_is_dropped_from_its_depth_only() -> None:
    copies = [(100, 1000), (110, 1000), (5, 100)]
    if families.pool_copies(copies, planned=1000.0) != (210, 2000):
        raise AssertionError(families.pool_copies(copies, planned=1000.0))


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
