"""Retained numerical contracts reject altered samples, probabilities and verdicts."""

import copy
import subprocess
from pathlib import Path

import local_simulation_replay
import pytest
from local_simulation_replay import check_photonic, check_probabilities, check_qi, load


def test_photonic_replay_rejects_changed_probability() -> None:
    row = copy.deepcopy(load("physical-photonic-compiler-crosscheck/photonic.json")["rows"][0])
    row["probabilities"]["SLOS"][0] += 0.01
    with pytest.raises(ValueError, match="probabilit"):
        check_photonic(row)


def test_qi_replay_rejects_changed_sample_denominator() -> None:
    row = copy.deepcopy(load("fullprecision-compiler-crosscheck/qi.json")["rows"][0])
    row["simulations"]["source"]["counts"]["00"] -= 1
    with pytest.raises(ValueError, match="denominator"):
        check_qi((row, True, True))


def test_qi_replay_rejects_changed_verdict() -> None:
    row = copy.deepcopy(load("validated-terminal-unitary-compiler-crosscheck/qi.json")["rows"][8])
    row["passed"] = True
    with pytest.raises(ValueError, match="verdict"):
        check_qi((row, False, True))


@pytest.mark.parametrize("values", [[float("nan"), 1.0], [float("inf")], [0.5], [-0.1, 1.1]])
def test_probability_contract_rejects_nonfinite_or_unnormalized(values: list[float]) -> None:
    with pytest.raises(ValueError, match="probabilities"):
        check_probabilities(values)


@pytest.mark.parametrize("field", ["probability", "maximum_error", "operator_error"])
def test_photonic_replay_rejects_every_nonfinite_error_surface(field: str) -> None:
    row = copy.deepcopy(load("physical-photonic-compiler-crosscheck/photonic.json")["rows"][0])
    if field == "probability":
        row["probabilities"]["SLOS"][0] = float("nan")
    elif field == "maximum_error":
        row["max_probability_errors"]["SLOS"] = float("nan")
    else:
        row["full_operator_max_error"] = float("nan")
    with pytest.raises(ValueError):
        check_photonic(row)


def test_qi_replay_requires_both_simulation_and_error_branches() -> None:
    row = copy.deepcopy(load("fullprecision-compiler-crosscheck/qi.json")["rows"][0])
    del row["simulations"]["compiled"]
    del row["native_probability_errors"]["compiled"]
    with pytest.raises(ValueError, match="source and compiled"):
        check_qi((row, True, True))


def test_inventory_excludes_fresh_untracked_replay_output(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    bundle = tmp_path / "results/local-simulation"
    bundle.mkdir(parents=True)
    (bundle / "retained.json").write_text("{}\n")
    subprocess.run(["git", "add", "results/local-simulation/retained.json"], cwd=tmp_path, check=True)
    (bundle / "fresh-replay").mkdir()
    (bundle / "fresh-replay/generated.json").write_text("{}\n")
    monkeypatch.setattr(local_simulation_replay, "ROOT", tmp_path)
    monkeypatch.setattr(local_simulation_replay, "BUNDLE", bundle)
    if set(local_simulation_replay.inventory()) != {"retained.json"}:
        raise RuntimeError("fresh untracked replay output entered the retained artifact denominator")
