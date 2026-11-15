"""The exploratory phase refit of the null rotation scan histograms: its replay comparison and its retained record."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest
import qi_pathion_null_rotation_scan_phase_refit as refit

ROOT = Path(__file__).resolve().parents[2]
MODEL = "five_noise_terms"


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _fake_record() -> dict[str, Any]:
    model = {
        "n_free": 2,
        "dof": 928,
        "histogram_chi2": 51767.25,
        "min_expected_probability": 1.5e-4,
        "contrast_chi2": 1126.5,
        "contrast_chi2_by_kind": {"all10": 281.0, "bridge": 158.5},
        "values": {"ca": 0.01943, "cp": 0.03233},
        "free": ["ca", "cp"],
        "start": {"ca": 0.005, "cp": 0.005},
        "x_scale": {"ca": 0.03, "cp": 0.03},
        "diff_step": 1e-3,
        "at_bound": [],
        "search": {"starts": 4, "best_histogram_chi2": 51767.25, "best_minus_headline": 0.0},
    }
    return {
        "schema": refit.SCHEMA,
        "observations": 30,
        "data_sha256": refit.data_digest([]),
        "models": {MODEL: model},
    }


def _store(directory: Path, record: dict[str, Any]) -> None:
    (directory / refit.RECORD).write_text(refit.render(record), encoding="utf-8")


def _node(record: dict[str, Any], path: tuple[str, ...]) -> Any:
    node: Any = record
    for key in path:
        node = node[key]
    return node


def test_a_record_agrees_with_itself_and_with_a_float_inside_the_tolerance() -> None:
    record = _fake_record()
    nudged = copy.deepcopy(record)
    nudged["models"][MODEL]["values"]["cp"] += 0.5 * refit.TOLERANCE
    _expect(refit.differences(record, copy.deepcopy(record)) == [], "a record differs from its copy")
    _expect(refit.differences(record, nudged) == [], "a float inside the tolerance is reported")


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("models", MODEL, "histogram_chi2"), 51767.25 * 1.01),
        (("models", MODEL, "values", "cp"), 0.04),
        (("models", MODEL, "start", "cp"), 0.02),
        (("models", MODEL, "x_scale", "ca"), 0.3),
        (("models", MODEL, "diff_step"), 1e-2),
        (("models", MODEL, "min_expected_probability"), 1e-9),
        (("models", MODEL, "dof"), 929),
        (("models", MODEL, "dof"), 928.0),
        (("models", MODEL, "free"), ["ca"]),
        (("schema",), "other"),
    ],
)
def test_a_difference_beyond_the_tolerance_is_reported(path: tuple[str, ...], value: Any) -> None:
    mutated = _fake_record()
    _node(mutated, path[:-1])[path[-1]] = value
    found = refit.differences(_fake_record(), mutated)
    _expect(len(found) == 1 and path[-1] in found[0], f"{path} mutated to {value!r} reads {found}")


def test_a_missing_model_is_reported() -> None:
    mutated = _fake_record()
    del mutated["models"][MODEL]
    _expect(len(refit.differences(_fake_record(), mutated)) == 1, "a dropped model passes")


def test_check_accepts_the_replay_and_rejects_a_mutated_record(tmp_path: Path) -> None:
    record = _fake_record()
    fresh = refit.without_search(record)
    _store(tmp_path, record)
    refit.check(tmp_path, fresh=copy.deepcopy(fresh))
    mutated = copy.deepcopy(record)
    mutated["models"][MODEL]["histogram_chi2"] = 42849.0
    _store(tmp_path, mutated)
    with pytest.raises(ValueError, match="differs from the replay"):
        refit.check(tmp_path, fresh=copy.deepcopy(fresh))


def test_check_rejects_a_stored_search_that_found_a_lower_minimum(tmp_path: Path) -> None:
    record = _fake_record()
    record["models"][MODEL]["search"]["best_histogram_chi2"] = 42849.0
    _store(tmp_path, record)
    with pytest.raises(ValueError, match="lower minimum"):
        refit.check(tmp_path, fresh=refit.without_search(record))


def test_check_rejects_a_record_without_its_search(tmp_path: Path) -> None:
    record = _fake_record()
    _store(tmp_path, refit.without_search(record))
    with pytest.raises(ValueError, match="no search section"):
        refit.check(tmp_path, fresh=refit.without_search(record))


def test_profile_accepts_the_replayed_search_and_rejects_a_lower_or_changed_one(tmp_path: Path) -> None:
    record = _fake_record()
    _store(tmp_path, record)
    stored = {MODEL: copy.deepcopy(record["models"][MODEL]["search"])}
    refit.profile(tmp_path, fresh=copy.deepcopy(stored))
    lower = copy.deepcopy(stored)
    lower[MODEL]["best_histogram_chi2"] = 42849.0
    with pytest.raises(ValueError, match="differs from its replay"):
        refit.profile(tmp_path, fresh=lower)
    lower_stored = copy.deepcopy(record)
    lower_stored["models"][MODEL]["search"] = lower[MODEL]
    _store(tmp_path, lower_stored)
    with pytest.raises(ValueError, match="lower minimum"):
        refit.profile(tmp_path, fresh=lower)
    changed = copy.deepcopy(stored)
    changed[MODEL]["starts"] = 5
    _store(tmp_path, record)
    with pytest.raises(ValueError, match="differs from its replay"):
        refit.profile(tmp_path, fresh=changed)


def test_verify_search_allows_a_difference_inside_the_tolerance_only() -> None:
    inside = {"m": {"histogram_chi2": 100.0, "search": {"best_histogram_chi2": 100.0 - 0.5 * refit.TOLERANCE * 100}}}
    outside = {"m": {"histogram_chi2": 100.0, "search": {"best_histogram_chi2": 100.0 - 2 * refit.TOLERANCE * 100}}}
    refit.verify_search(inside)
    with pytest.raises(ValueError, match="lower minimum"):
        refit.verify_search(outside)


def test_main_check_and_profile_exit_nonzero_on_a_mutated_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    record = _fake_record()
    _store(tmp_path, record)
    monkeypatch.setattr(
        refit, "build", lambda search=True: copy.deepcopy(record if search else refit.without_search(record))
    )
    monkeypatch.setattr(refit, "observations", lambda: ([], []))
    monkeypatch.setattr(
        refit, "search_all", lambda found, models: {MODEL: copy.deepcopy(record["models"][MODEL]["search"])}
    )
    for flag in ("--check", "--profile"):
        monkeypatch.setattr("sys.argv", ["phase_refit", flag, str(tmp_path)])
        _expect(refit.main() == 0, f"a matching record fails {flag}")
    mutated = copy.deepcopy(record)
    mutated["models"][MODEL]["values"]["cp"] = 0.0
    mutated["models"][MODEL]["search"]["starts"] = 9
    _store(tmp_path, mutated)
    for flag in ("--check", "--profile"):
        monkeypatch.setattr("sys.argv", ["phase_refit", flag, str(tmp_path)])
        _expect(refit.main() == 1, f"a mutated record passes {flag}")
    _expect("differs from" in capsys.readouterr().err, "the rejection names no difference")


def test_main_write_stores_the_built_record(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    record = _fake_record()
    monkeypatch.setattr(refit, "build", lambda search=True: copy.deepcopy(record))
    monkeypatch.setattr("sys.argv", ["phase_refit", "--write", str(tmp_path / "out")])
    _expect(refit.main() == 0, "--write fails")
    stored = json.loads((tmp_path / "out" / refit.RECORD).read_text(encoding="utf-8"))
    _expect(stored == record, "the stored record differs from the built one")


def test_the_declared_models_carry_consistent_fit_specifications() -> None:
    names = [spec.name for spec in refit.SPECS]
    _expect(len(set(names)) == len(names), "two fit specifications share a name")
    _expect(refit.MODEL_NAMES == (refit.EXACT, refit.RETENTION, *names), "MODEL_NAMES departs from SPECS")
    for spec in refit.SPECS:
        sizes = {len(spec.free), len(spec.start), len(spec.lower), len(spec.upper), len(spec.x_scale)}
        _expect(len(sizes) == 1, f"{spec.name} has parameter vectors of different lengths")
        for start, lower, upper in zip(spec.start, spec.lower, spec.upper, strict=True):
            _expect(lower <= start <= upper, f"{spec.name} starts outside its bounds")


def test_the_raw_directory_of_a_run_must_hold_exactly_the_manifest_files(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    for name in ("a.cq.json", "b.cq.json"):
        (raw / name).write_text("{}", encoding="utf-8")
    refit.verify_raw_files(tmp_path, ["a.cq", "b.cq"])
    with pytest.raises(ValueError, match="manifest lists"):
        refit.verify_raw_files(tmp_path, ["a.cq"])
    with pytest.raises(ValueError, match="manifest lists"):
        refit.verify_raw_files(tmp_path, ["a.cq", "b.cq", "c.cq"])
    (raw / "stray.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="manifest lists"):
        refit.verify_raw_files(tmp_path, ["a.cq", "b.cq"])


@pytest.mark.audit
def test_self_test_passes() -> None:
    _expect(refit.self_test().startswith("qi_pathion_null_rotation_scan_phase_refit self-test: OK"), "self-test fails")


def _retained() -> dict[str, Any]:
    path = ROOT / "results" / "quantum_inspire" / refit.RECORD
    record: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return record


@pytest.mark.audit
def test_the_retained_record_holds_the_headline_figures() -> None:
    models = _retained()["models"]
    retention, five = models[refit.RETENTION], models["five_noise_terms"]
    phase, flip = models["cz_noise_flip_q12_z_after_pulse"], models["five_noise_terms_selector_flip"]
    _expect(round(retention["histogram_chi2"], 1) == 182795.4 and retention["dof"] == 920, "retention fit moved")
    _expect(round(five["histogram_chi2"]) == 51767 and five["dof"] == 925, "five-term fit moved")
    _expect(round(phase["histogram_chi2"]) == 42849 and phase["dof"] == 926, "q12 phase fit moved")
    _expect(round(phase["values"]["z12"], 3) == -0.151, "the q12 phase moved")
    _expect(round(five["values"]["cp"], 3) == 0.032 and round(flip["values"]["cp"], 3) == 0.031, "cp moved")
    _expect(models[refit.EXACT]["histogram_chi2"] > 2.6e6, "the zero-parameter exact model moved")


@pytest.mark.audit
def test_the_retained_record_is_complete_and_degrees_of_freedom_follow_the_free_parameters() -> None:
    record = _retained()
    _expect(record["schema"] == refit.SCHEMA, "the retained record has another schema")
    _expect(tuple(record["models"]) == tuple(sorted(refit.MODEL_NAMES)), "the retained models differ from the declared")
    _expect(record["expected_probability_floor"] == refit.CLIP, "the floor differs from the script's")
    for name, model in record["models"].items():
        _expect(model["dof"] == 30 * 31 - model["n_free"], f"{name} counts its degrees of freedom wrongly")
        _expect(model["n_free"] == len(model["free"]), f"{name} lists a different number of free parameters")
        _expect(set(model["start"]) == set(model["free"]) == set(model["x_scale"]), f"{name} stores a partial config")
        _expect(model["min_expected_probability"] > refit.CLIP, f"{name} reaches the probability floor")


@pytest.mark.audit
def test_the_retained_search_found_no_lower_minimum_and_ran_every_start() -> None:
    models = _retained()["models"]
    refit.verify_search(models)
    for name, model in models.items():
        search = model["search"]
        _expect(search["starts"] >= (0 if name == refit.EXACT else 4), f"{name} ran {search['starts']} starts")
        _expect(
            abs(search["best_minus_headline"] - (search["best_histogram_chi2"] - model["histogram_chi2"])) < 1e-6,
            f"{name} stores an inconsistent search gap",
        )
