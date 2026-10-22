"""Retained numerical contracts reject altered samples, probabilities and verdicts."""

import copy
import json
import subprocess
from pathlib import Path
from typing import Any

import local_simulation_replay
import pytest
from local_simulation_replay import check_photonic, check_probabilities, check_qi, load


def retained_live_payload() -> dict[str, Any]:
    return {
        "versions": load("fullprecision-compiler-crosscheck/qi.json")["versions"],
        "rows": load("fullprecision-compiler-crosscheck/qi.json")["rows"],
        "default_compiled": {
            row["case"]: row["compiled"]
            for row in load("validated-terminal-unitary-compiler-crosscheck/qi.json")["rows"]
        },
        "simulations": [
            {field: row["simulations"][kind][field] for field in ("counts", "state")}
            for directory, _, _ in local_simulation_replay.QI_BUNDLES
            for row in load(directory + "/qi.json")["rows"]
            for kind in ("source", "compiled")
        ],
    }


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


def test_qi_replay_binds_manifest_digest(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    row = copy.deepcopy(load("fullprecision-compiler-crosscheck/qi.json")["rows"][0])
    source = local_simulation_replay.ROOT / row["case"]
    target = tmp_path / row["case"]
    target.parent.mkdir(parents=True)
    target.write_bytes(source.read_bytes())
    manifest = json.loads(source.with_name("cases.json").read_text())
    next(case for case in manifest["circuits"] if case["file"] == source.name)["sha256"] = "0" * 64
    target.with_name("cases.json").write_text(json.dumps(manifest))
    monkeypatch.setattr(local_simulation_replay, "ROOT", tmp_path)
    with pytest.raises(ValueError, match="source identity"):
        check_qi((row, True, True))


@pytest.mark.parametrize("distribution", ["opensquirrel", "libqasm", "qxelarator"])
def test_replay_rejects_altered_qi_version(distribution: str, monkeypatch: pytest.MonkeyPatch) -> None:
    original_load = local_simulation_replay.load

    def altered_load(name: str) -> dict[str, Any]:
        record = original_load(name)
        if name == "photonic-compiler-crosscheck/qi.json":
            record["versions"][distribution] = "0.0.0"
        return record

    monkeypatch.setattr(local_simulation_replay, "load", altered_load)
    monkeypatch.setattr(local_simulation_replay, "ordered_map", lambda *args, **kwargs: [])
    with pytest.raises(ValueError, match="toolchain versions"):
        local_simulation_replay.check()


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


def test_state_basis_label_rejects_negative_index_alias() -> None:
    row = copy.deepcopy(load("fullprecision-compiler-crosscheck/qi.json")["rows"][1])
    row["simulations"]["source"]["state"]["-1"] = row["simulations"]["source"]["state"].pop("11")
    with pytest.raises(ValueError, match="basis labels"):
        check_qi((row, True, True))


def test_optical_source_identity_requires_every_circuit() -> None:
    record = copy.deepcopy(load("physical-photonic-compiler-crosscheck/photonic.json"))
    circuit = next(name for name in record["source_sha256"] if name.endswith("circuit.json"))
    del record["source_sha256"][circuit]
    with pytest.raises(ValueError, match="source-hash denominator"):
        local_simulation_replay.check_optical_sources(record)


def test_retained_histogram_rejects_impossible_readout_reference() -> None:
    row = copy.deepcopy(load("physical-photonic-compiler-crosscheck/qi.json")["rows"][1])
    row["simulations"]["source"]["counts"] = {"00": 1024}
    with pytest.raises(ValueError, match="native support"):
        check_qi((row, False, False))


def test_live_replay_checks_default_writer_histograms(monkeypatch: pytest.MonkeyPatch) -> None:
    import qi_stack

    payload = retained_live_payload()
    payload["simulations"][0]["counts"] = {"11": 1024}
    monkeypatch.setattr(qi_stack, "live", lambda *args: True)
    monkeypatch.setattr(qi_stack, "run", lambda *args: json.dumps(payload))
    with pytest.raises(ValueError, match="seeded counts or states"):
        local_simulation_replay.live_qi()


def test_live_replay_checks_probed_versions(monkeypatch: pytest.MonkeyPatch) -> None:
    import qi_stack

    payload = retained_live_payload()
    payload["versions"]["libqasm"] = "0.0.0"
    monkeypatch.setattr(qi_stack, "live", lambda *args: True)
    monkeypatch.setattr(qi_stack, "run", lambda *args: json.dumps(payload))
    with pytest.raises(ValueError, match="toolchain versions"):
        local_simulation_replay.live_qi()


def test_live_replay_checks_default_writer_states(monkeypatch: pytest.MonkeyPatch) -> None:
    import qi_stack

    payload = retained_live_payload()
    payload["simulations"][0]["state"] = {"00": [0.0, 1.0]}
    monkeypatch.setattr(qi_stack, "live", lambda *args: True)
    monkeypatch.setattr(qi_stack, "run", lambda *args: json.dumps(payload))
    with pytest.raises(ValueError, match="seeded counts or states"):
        local_simulation_replay.live_qi()


def test_synthetic_photonic_counts_replay_the_recorded_seed() -> None:
    row = copy.deepcopy(load("physical-photonic-compiler-crosscheck/photonic.json")["rows"][0])
    row["simulated_counts"][0] -= 1
    row["simulated_counts"][1] += 1
    with pytest.raises(ValueError, match="seeded sampler"):
        check_photonic(row)


def test_live_replay_compares_ordinary_default_compiler(monkeypatch: pytest.MonkeyPatch) -> None:
    import qi_stack

    payload = retained_live_payload()
    first_case = next(iter(payload["default_compiled"]))
    payload["default_compiled"][first_case] += "// changed default compiler\n"
    monkeypatch.setattr(qi_stack, "live", lambda *args: True)
    monkeypatch.setattr(qi_stack, "run", lambda *args: json.dumps(payload))
    with pytest.raises(ValueError, match="default-compiler output"):
        local_simulation_replay.live_qi()


@pytest.mark.parametrize("reported", [0.0, float("nan")])
def test_complete_operator_output_rejects_lowered_or_nonfinite_residual(reported: float) -> None:
    row = copy.deepcopy(load("physical-photonic-compiler-crosscheck/photonic.json")["rows"][0])
    outputs = load("optical-operator-replay.json")["rows"]
    actual = next(output for output in outputs if (output["case"], output["index"]) == (row["case"], row["index"]))
    row["full_operator_max_error"] = reported
    with pytest.raises(ValueError, match="full-operator maximum"):
        local_simulation_replay.check_optical_operator((row, actual))
