"""End-to-end JSON contracts preserve estimands, unavailable data and input bytes."""

import copy
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
from measurement_observability import ROOT, analyze_document, main, read_document

FIXTURE = ROOT / "tests/fixtures/measurement-observability.json"


def document() -> dict:
    return json.loads(FIXTURE.read_text())


def test_all_operations_match_independent_fixture_endpoints() -> None:
    result = analyze_document(document())
    rows = {row["id"]: row["result"] for row in result["items"]}
    np.testing.assert_allclose(rows["shared-scores"]["means"], [-0.3, 0.8])
    np.testing.assert_allclose(rows["shared-scores"]["covariance_of_means"], [[0.061, -0.026], [-0.026, 0.016]])
    state = rows["acceptance-counterexample"]
    np.testing.assert_allclose(list(state["conditional_contrasts"].values()), [-0.2, -0.2])
    np.testing.assert_allclose(list(state["unconditional_contrasts"].values()), [0, 0], atol=1e-16)
    np.testing.assert_allclose(state["contrast_covariance"], [[0.056, 0.024], [0.024, 0.056]])
    np.testing.assert_allclose(rows["shared-prediction"]["covariance"], [[1.5, 1.0], [1.0, 3.0]])
    np.testing.assert_allclose(rows["nested-herald"]["recurrence_residuals"], [0, 0], atol=1e-16)
    if rows["tomography-completion"]["family_dimensions"] != {
        "real_J_commutant": 4,
        "real_J_anticommutant": 6,
        "imaginary_skew": 6,
    }:
        raise AssertionError("incorrect Hermitian direct-sum dimensions")


def test_parallel_dispatch_preserves_item_order_and_values(forced_pool) -> None:
    result = analyze_document(document())
    if [row["id"] for row in result["items"]] != [row["id"] for row in document()["items"]]:
        raise AssertionError("parallel dispatch changes input order")
    if not forced_pool.maps or 2 not in forced_pool.pools:
        raise AssertionError("the order-preserving pool does not run")
    np.testing.assert_allclose(result["items"][0]["result"]["means"], [-0.3, 0.8])


def test_missing_attempts_remain_unavailable() -> None:
    value = document()
    for state in value["items"][1]["input"]["records"]:
        state["denominator"].update(status="unavailable", value=None)
    result = analyze_document(value)["items"][1]["result"]
    if result["unconditional_contrasts"] != {"real": None, "imaginary": None}:
        raise AssertionError("missing trials acquire an invented denominator")
    if result["contrast_covariance"] is not None:
        raise AssertionError("missing trials acquire an invented covariance")
    np.testing.assert_allclose(list(result["conditional_contrasts"].values()), [-0.2, -0.2])


@pytest.mark.parametrize(
    "text", ['{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}', '{"a":-Infinity}', '{"a":1e999}', '{"a":-1e999}']
)
def test_strict_json_rejects_ambiguous_or_nonfinite_input(text: str) -> None:
    with pytest.raises(ValueError):
        read_document(text.encode())


@pytest.mark.parametrize("mutation", ["schema", "duplicate", "extra", "kind", "sampling", "source"])
def test_document_contract_rejects_omissions_and_typos(mutation: str) -> None:
    value = document()
    if mutation == "schema":
        value["schema"] = "unknown"
    elif mutation == "duplicate":
        value["items"].append(copy.deepcopy(value["items"][0]))
    elif mutation == "extra":
        value["items"][0]["input"]["score"] = [1, 0]
    elif mutation == "kind":
        value["items"][0]["kind"] = "physical_discovery"
    elif mutation == "sampling":
        del value["items"][0]["input"]["sampling"]
    else:
        value["items"][0]["source"] = ""
    with pytest.raises(ValueError):
        analyze_document(value)


def test_cli_records_input_and_producer_digests(tmp_path: Path) -> None:
    output = tmp_path / "nested" / "result.json"
    if main([str(FIXTURE), "--output", str(output)]) != 0:
        raise AssertionError("valid CLI input fails")
    result = json.loads(output.read_text())
    if result["provenance"]["input_sha256"] != hashlib.sha256(FIXTURE.read_bytes()).hexdigest():
        raise AssertionError("input digest does not bind analyzed bytes")
    for name, digest in result["provenance"]["producer_sha256"].items():
        if digest != hashlib.sha256((ROOT / name).read_bytes()).hexdigest():
            raise AssertionError(f"producer digest differs for {name}")


@pytest.mark.parametrize("half_dimension", [128, True, 0, 1.5])
def test_tomography_checks_dimension_and_budget_before_allocation(half_dimension, monkeypatch) -> None:
    import measurement_observability as interface

    def forbidden(_dimension):
        raise AssertionError("invalid or over-budget tomography reaches the allocator")

    monkeypatch.setattr(interface, "tomography_completion", forbidden)
    value = document()
    value["items"] = [value["items"][-1]]
    value["items"][0]["input"]["half_dimension"] = half_dimension
    with pytest.raises(ValueError):
        analyze_document(value)


def test_tomography_budget_is_explicit_in_the_bound_output() -> None:
    value = document()
    value["items"] = [value["items"][-1]]
    value["items"][0]["input"]["coefficient_entry_budget"] = 512
    result = analyze_document(value)["items"][0]["result"]
    if result["coefficient_entries"] != 512 or result["coefficient_entry_budget"] != 512:
        raise AssertionError("tomography budget does not bind the result")


def test_cli_stdout_and_failure_preserve_existing_files(tmp_path: Path, capsys) -> None:
    if main([str(FIXTURE)]) != 0:
        raise AssertionError("stdout CLI fails")
    if json.loads(capsys.readouterr().out)["schema"] != "measurement-observability-result-v1":
        raise AssertionError("wrong output schema")
    invalid = tmp_path / "input.json"
    invalid.write_text('{"schema":"bad","items":[]}')
    original = invalid.read_bytes()
    if main([str(invalid), "--output", str(invalid)]) != 2 or invalid.read_bytes() != original:
        raise AssertionError("CLI overwrites its input")
    output = tmp_path / "output.json"
    output.write_text("retained output")
    if main([str(invalid), "--output", str(output)]) != 2 or output.read_text() != "retained output":
        raise AssertionError("failed analysis replaces existing output")


def test_cli_refuses_to_overwrite_a_valid_input_document(tmp_path: Path) -> None:
    copy = tmp_path / "input.json"
    copy.write_bytes(FIXTURE.read_bytes())
    if main([str(copy), "--output", str(copy)]) != 2 or copy.read_bytes() != FIXTURE.read_bytes():
        raise AssertionError("a valid analysis overwrites its own input")
    alias = tmp_path / "alias.json"
    alias.symlink_to(copy)
    if main([str(copy), "--output", str(alias)]) != 2 or copy.read_bytes() != FIXTURE.read_bytes():
        raise AssertionError("a symbolic link to the input bypasses the overwrite guard")


def test_multinomial_scores_require_the_declared_sampling_value() -> None:
    value = document()
    value["items"][0]["input"]["sampling"] = "other"
    with pytest.raises(ValueError, match="independent_fixed_trials"):
        analyze_document(value)


@pytest.mark.parametrize("field", ["id", "source", "kind"])
def test_item_text_must_be_a_single_line(field: str) -> None:
    value = document()
    original = value["items"][0][field]
    for separator in ("\n", "\u2028", "\u2029", "\x85"):
        value["items"][0][field] = original + separator + "second line"
        with pytest.raises(ValueError):
            analyze_document(value)
