"""The exploratory phase refit of the null rotation scan histograms: its replay comparison and its retained record."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest
import qi_pathion_null_rotation_scan_phase_refit as refit

ROOT = Path(__file__).resolve().parents[2]


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _fake_record() -> dict[str, Any]:
    model = {
        "n_free": 2,
        "dof": 928,
        "histogram_chi2": 51767.25,
        "contrast_chi2": 1126.5,
        "contrast_chi2_by_kind": {"all10": 281.0, "bridge": 158.5},
        "values": {"ca": 0.01943, "cp": 0.03233},
        "free": ["ca", "cp"],
        "at_bound": [],
    }
    return {"schema": refit.SCHEMA, "observations": 30, "models": {"five_noise_terms": model}}


def _store(directory: Path, record: dict[str, Any]) -> None:
    (directory / refit.RECORD).write_text(refit.render(record), encoding="utf-8")


def test_a_record_agrees_with_itself_and_with_a_float_inside_the_tolerance() -> None:
    record = _fake_record()
    nudged = copy.deepcopy(record)
    nudged["models"]["five_noise_terms"]["values"]["cp"] += 0.5 * refit.TOLERANCE
    _expect(refit.differences(record, copy.deepcopy(record)) == [], "a record differs from its copy")
    _expect(refit.differences(record, nudged) == [], "a float inside the tolerance is reported")


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("models", "five_noise_terms", "histogram_chi2"), 51767.25 * 1.01),
        (("models", "five_noise_terms", "values", "cp"), 0.04),
        (("models", "five_noise_terms", "dof"), 929),
        (("models", "five_noise_terms", "dof"), 928.0),
        (("models", "five_noise_terms", "free"), ["ca"]),
        (("schema",), "other"),
    ],
)
def test_a_difference_beyond_the_tolerance_is_reported(path: tuple[str, ...], value: Any) -> None:
    mutated = _fake_record()
    node = mutated
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = value
    found = refit.differences(_fake_record(), mutated)
    _expect(len(found) == 1 and path[-1] in found[0], f"{path} mutated to {value!r} reads {found}")


def test_a_missing_model_is_reported() -> None:
    mutated = _fake_record()
    del mutated["models"]["five_noise_terms"]
    _expect(len(refit.differences(_fake_record(), mutated)) == 1, "a dropped model passes")


def test_check_accepts_the_replay_and_rejects_a_mutated_record(tmp_path: Path) -> None:
    record = _fake_record()
    _store(tmp_path, record)
    refit.check(tmp_path, fresh=copy.deepcopy(record))
    mutated = copy.deepcopy(record)
    mutated["models"]["five_noise_terms"]["histogram_chi2"] = 42849.0
    _store(tmp_path, mutated)
    with pytest.raises(ValueError, match="differs from the replay"):
        refit.check(tmp_path, fresh=copy.deepcopy(record))


def test_main_check_exits_nonzero_on_a_mutated_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    record = _fake_record()
    _store(tmp_path, record)
    monkeypatch.setattr(refit, "build", lambda: copy.deepcopy(record))
    monkeypatch.setattr("sys.argv", ["phase_refit", "--check", str(tmp_path)])
    _expect(refit.main() == 0, "a matching record fails --check")
    mutated = copy.deepcopy(record)
    mutated["models"]["five_noise_terms"]["values"]["cp"] = 0.0
    _store(tmp_path, mutated)
    _expect(refit.main() == 1, "a mutated record passes --check")
    _expect("differs from the replay" in capsys.readouterr().err, "the rejection names no difference")


def test_main_write_stores_the_built_record(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    record = _fake_record()
    monkeypatch.setattr(refit, "build", lambda: copy.deepcopy(record))
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


@pytest.mark.audit
def test_self_test_passes() -> None:
    _expect(refit.self_test().startswith("qi_pathion_null_rotation_scan_phase_refit self-test: OK"), "self-test fails")


def _retained() -> dict[str, Any]:
    record: dict[str, Any] = json.loads(
        (ROOT / "results" / "quantum_inspire" / refit.RECORD).read_text(encoding="utf-8")
    )
    return record


@pytest.mark.audit
def test_the_retained_record_holds_the_figures_the_written_case_quotes() -> None:
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
    for name, model in record["models"].items():
        _expect(model["dof"] == 30 * 31 - model["n_free"], f"{name} counts its degrees of freedom wrongly")
        _expect(model["n_free"] == len(model["free"]), f"{name} lists a different number of free parameters")
