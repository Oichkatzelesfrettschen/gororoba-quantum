"""Observable and provenance failures that must stop conjecture synthesis."""

from __future__ import annotations

import copy
import importlib
import importlib.util
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from sympy import Matrix, Rational, eye, zeros


def implementation() -> Any:
    if importlib.util.find_spec("algebra_device_conjectures") is None:
        raise AssertionError("the offline conjecture implementation is missing")
    return importlib.import_module("algebra_device_conjectures")


def test_filter_preserves_failure_mass_and_refuses_zero_success_conditioning() -> None:
    module = implementation()
    state = eye(2) / 2
    result = module.filter_state(Matrix.diag(1, Rational(1, 2)), state)
    if result["success"] != Rational(5, 8) or result["conditional"] != Matrix.diag(Rational(4, 5), Rational(1, 5)):
        raise AssertionError(result)
    if result["unconditional"] != state or result["failure"] != Rational(3, 8):
        raise AssertionError("failure accounting changed the ensemble")
    dark = module.filter_state(Matrix.diag(0, 1), Matrix.diag(1, 0))
    if dark["success"] != 0 or dark["conditional"] is not None:
        raise AssertionError("zero-probability conditioning was admitted")


@pytest.mark.parametrize("state", [Matrix.diag(2, -1), Matrix([[1, 1], [0, 0]]), eye(2)])
def test_filter_rejects_non_density_inputs(state: Any) -> None:
    with pytest.raises(ValueError, match="density"):
        implementation().filter_state(eye(2), state)


def test_filter_rejects_gain_without_a_dilation_scale() -> None:
    with pytest.raises(ValueError, match="contraction"):
        implementation().filter_state(2 * eye(2), eye(2) / 2)


def test_exact_families_distinguish_order_sector_and_dimension_mutations() -> None:
    facts = implementation().exact_families()
    if facts["order"]["anticommuting_control_x"] != "-1" or facts["order"]["incoherent_control_x"] != "0":
        raise AssertionError(facts["order"])
    if facts["sectors"]["multiplicities"] != {"0": 4, "2": 8, "4": 4}:
        raise AssertionError(facts["sectors"])
    if facts["sectors"]["kernel_product"] != ["0"] * 16 or facts["sectors"]["bright_norm_squared"] != "8":
        raise AssertionError(facts["sectors"])
    if facts["conditioning"]["remote_unconditional"] != [["1/2", "0"], ["0", "1/2"]]:
        raise AssertionError(facts["conditioning"])
    if not facts["dimension"]["outside_support_changes_product"]:
        raise AssertionError(facts["dimension"])
    if facts["pt"]["exceptional_rank"] != 1 or not facts["pt"]["exceptional_square_zero"]:
        raise AssertionError(facts["pt"])


def test_zeno_is_exact_at_rational_rotation_and_preserves_branch_mass() -> None:
    result = implementation().measurement_sequence(Rational(3, 5), Rational(4, 5), 3)
    if result["all_zero_survival"] != Rational(3, 5) ** 6 or result["total_probability"] != 1:
        raise AssertionError(result)
    with pytest.raises(ValueError):
        implementation().measurement_sequence(Rational(1), Rational(1), 3)


def test_projected_shots_preserve_order_and_register_semantics() -> None:
    module = implementation()
    shots = ["001", "100", "101"]
    if module.project_shots(shots, 3, [0, 2]) != [(1, 0), (0, 1), (1, 1)]:
        raise AssertionError("shot order or little-endian mapping changed")
    for bad in (["01"], ["00x"]):
        with pytest.raises(ValueError):
            module.project_shots(bad, 3, [0])
    with pytest.raises(ValueError):
        module.project_shots(shots, 3, [3])


@pytest.mark.audit
def test_manifest_covers_every_proposal_and_rejects_corruption(tmp_path: Path) -> None:
    module = implementation()
    manifest = module.load_manifest(module.DEFAULT_MANIFEST)
    if len(manifest["proposals"]) != 22:
        raise AssertionError("the two drafts lost a proposal")
    module.validate_manifest(manifest)
    duplicate = copy.deepcopy(manifest)
    duplicate["proposals"].append(duplicate["proposals"][0])
    with pytest.raises(ValueError, match="duplicate"):
        module.validate_manifest(duplicate)
    damaged = copy.deepcopy(manifest)
    damaged["sources"][0]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="digest"):
        module.validate_manifest(damaged)
    escape = copy.deepcopy(manifest)
    escape["sources"][0]["path"] = "../outside"
    with pytest.raises(ValueError, match="relative"):
        module.validate_manifest(escape)


def test_holm_keeps_unresolved_and_handles_empty_family() -> None:
    module = implementation()
    if module.holm([0.01, 0.04, 0.8]) != [True, False, False] or module.holm([]) != []:
        raise AssertionError("Holm step-down decision differs")
    for invalid in ([float("nan")], [-0.1], [1.1]):
        with pytest.raises(ValueError):
            module.holm(invalid)


def test_exact_normality_rejects_a_mutated_sign_table() -> None:
    module = implementation()
    matrix = zeros(2)
    matrix[0, 1] = 1
    with pytest.raises(ValueError, match="skew"):
        module.require_skew(matrix)


def test_global_phase_associator_and_code_error_set_have_distinct_controls() -> None:
    facts = implementation().exact_families()
    if not facts["phase"]["unconditional_invariant"] or facts["phase"]["controlled_relative_x"] != "cos(phi)":
        raise AssertionError(facts["phase"])
    if facts["associator"]["encoded_overlap"] != "-1" or facts["associator"]["associative_control_overlap"] != "1":
        raise AssertionError(facts["associator"])
    if not facts["code"]["corrects_single_x"] or facts["code"]["corrects_single_z"]:
        raise AssertionError(facts["code"])
    if not facts["code"]["recovery_complete"] or not facts["code"]["logical_phase_ensembles_collide"]:
        raise AssertionError(facts["code"])


def test_bell_selection_changes_conditional_kernel_rate_and_preserves_unconditional_rate() -> None:
    facts = implementation().exact_families()["conditioning"]
    if facts["remote_z_selector_success"] != ["0", "1"]:
        raise AssertionError(facts)
    if facts["remote_x_selector_success"] != ["1/2", "1/2"] or facts["remote_selector_unconditional"] != "1/2":
        raise AssertionError(facts)


def test_measurement_schedule_refuses_short_cycles_and_requires_explicit_units() -> None:
    module = implementation()
    if module.timing_admission(50, 1340, 4)["admitted"]:
        raise AssertionError("50 ns cycle admitted a 1340 ns measurement")
    if not module.timing_admission(1400, 1340, 4)["admitted"]:
        raise AssertionError("aligned lower-bound timing check failed")
    with pytest.raises(ValueError):
        module.timing_admission(float("nan"), 1340, 4)


def test_joint_shots_and_singular_readout_are_preserved_by_existing_analysis() -> None:
    from qi_zero_divisor_secondary import corrected, moments

    result = moments([[0, 0], [0, 0], [1, 1], [1, 1]])
    if result["covariance_of_mean"][0][1] != result["covariance_of_mean"][0][0]:
        raise AssertionError("shared-shot covariance was discarded")
    with pytest.raises(ValueError, match="singular"):
        corrected(0.5, 0.5, 0.5)


@pytest.mark.audit
def test_manifest_rejects_cross_job_pairing_and_missing_selected_acquisition() -> None:
    module = implementation()
    manifest = module.load_manifest(module.DEFAULT_MANIFEST)
    manifest["comparisons"][0]["sampling_unit"] = "paired-job-shot-index"
    with pytest.raises(ValueError, match="pairing"):
        module.validate_manifest(manifest)
    manifest = module.load_manifest(module.DEFAULT_MANIFEST)
    manifest["acquisitions"] = [row for row in manifest["acquisitions"] if not row["included"]]
    with pytest.raises(ValueError):
        module.validate_manifest(manifest)


@pytest.mark.parametrize("mutation", ["excluded", "raw", "jobs", "statuses", "charge", "charge_unit"])
def test_frozen_census_rejects_omissions_and_fabricated_provider_facts(mutation: str) -> None:
    module = implementation()
    manifest = module.load_manifest(module.DEFAULT_MANIFEST)
    if mutation == "excluded":
        row = next(row for row in manifest["acquisitions"] if not row["included"])
        manifest["acquisitions"].remove(row)
        manifest["acquisition_count"] -= 1
    elif mutation == "raw":
        row = next(row for row in manifest["sources"] if "/raw/" in row["path"])
        manifest["sources"].remove(row)
    else:
        row = next(row for row in manifest["acquisitions"] if row["included"])
        if mutation == "charge_unit":
            row["charge_unit"] = "invented-unit"
        else:
            row["facts"][mutation] = {"invented": 99999} if mutation == "statuses" else 99999
    with pytest.raises(ValueError):
        module.validate_manifest(manifest)


@pytest.mark.parametrize("mutation", ["comparison_claim", "companion_pin"])
def test_comparison_attribution_and_companion_pin_follow_their_bound_sources(mutation: str) -> None:
    module = implementation()
    manifest = module.load_manifest(module.DEFAULT_MANIFEST)
    if mutation == "comparison_claim":
        manifest["comparisons"][0]["claim"] = "iqm-garnet-kernel-cancellation"
    else:
        manifest["companion_pin"] = "0" * 40
    with pytest.raises(ValueError):
        module.validate_manifest(manifest)


@pytest.mark.parametrize("mutation", ["reason", "base_commit", "digest", "extra", "path", "bytes"])
def test_predecessor_record_requires_digest_commit_and_reason(mutation: str) -> None:
    module = implementation()
    manifest = module.load_manifest(module.DEFAULT_MANIFEST)
    if "supersedes" not in manifest:
        raise AssertionError("the refreshed manifest names no predecessor")
    predecessor = manifest["supersedes"]
    if mutation == "reason":
        predecessor["reason"] = " "
    elif mutation == "base_commit":
        predecessor["base_commit"] = predecessor["base_commit"][:12]
    elif mutation == "digest":
        predecessor["manifest_sha256"] = predecessor["manifest_sha256"].upper()
    elif mutation == "extra":
        predecessor["note"] = "unbound"
    elif mutation == "path":
        predecessor["path"] = 7
    else:
        # A rewritten predecessor bundle no longer matches the digest its successor recorded.
        predecessor["manifest_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="predecessor" if mutation != "bytes" else "source digest differs"):
        module.validate_manifest(manifest)


def test_freeze_runs_only_on_a_checkout_identical_to_head(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = implementation()

    def git(*arguments: str) -> None:
        subprocess.run(["git", *arguments], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-q")
    for name in ("kept", "edited", "moved", "with space"):
        (tmp_path / name).write_text(f"{name}\n")
    git("add", ".")
    git("-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q", "-m", "base")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    manifest = {"base_commit": "0" * 40, "selected_claim_ids": []}
    if module._uncommitted():
        raise AssertionError("a clean checkout reported changes")
    with pytest.raises(ValueError, match="reason"):
        module.freeze_manifest(manifest, tmp_path / "census.json", " ", "kept")
    (tmp_path / "edited").write_text("changed\n")
    (tmp_path / "with space").write_text("changed\n")
    (tmp_path / "untracked").write_text("new\n")
    git("mv", "moved", "renamed")
    found = sorted(module._uncommitted())
    if found != ["edited", "renamed", "untracked", "with space"]:
        raise AssertionError(f"uncommitted state reported as {found}")
    with pytest.raises(ValueError, match="identical to HEAD"):
        module.freeze_manifest(manifest, tmp_path / "census.json", "a reason", "kept")


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        (["--freeze", "--predecessor", "x.json"], "requires --reason and --predecessor"),
        (["--freeze", "--reason", "r"], "requires --reason and --predecessor"),
        (["--freeze", "--reason", "r", "--predecessor", "x.json"], "writes a new bundle"),
    ],
)
def test_freeze_needs_a_reason_a_predecessor_and_a_new_bundle(
    arguments: list[str], message: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # The default --manifest names the current bundle, which a freeze never overwrites.
    module = implementation()
    monkeypatch.setattr(sys, "argv", ["algebra_device_conjectures.py", *arguments])
    with pytest.raises(SystemExit) as stopped:
        module.main()
    if stopped.value.code != 2 or message not in capsys.readouterr().err:
        raise AssertionError(f"--freeze {arguments} was accepted")
