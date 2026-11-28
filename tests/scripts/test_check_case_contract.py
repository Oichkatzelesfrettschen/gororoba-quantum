"""check_case_contract admits one good case per provider and rejects a mutant for every required field."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import check_case_contract
import pytest

SCRIPT = Path(check_case_contract.__file__)
SEED = "qrng:docs/evidence/anu_qrng/draw-2026-10-18T083548Z.json#3"


def check(condition: object, message: str = "check failed") -> None:
    if not condition:
        raise AssertionError(message)


def common(provider: str, backend: str, cost: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "case-contract-v1",
        "provider": provider,
        "case_id": "fixture-case",
        "hypothesis": "the observable moves by the predicted amount",
        "observable_primary_source": "raw/result.json",
        "falsifier": "a contrast inside two standard errors of zero",
        "why_cheaper_substrate_fails": "the question concerns the device itself",
        "backend": backend,
        "shots": 4096,
        "expected_seconds": 12.0,
        "expected_cost": cost,
        "qrng_seed_refs": [SEED],
        "preregistered_readings": ["primary: signed contrast"],
        "void_rules": ["a dead qubit in the layout voids the run"],
        "stopping_rule": "one job, no resubmission",
        "approval_quote": "Owner: submit this exact digest",
    }


def good(provider: str) -> dict[str, Any]:
    if provider == "ibm":
        meta = common("ibm", "ibm_fez", {"unit": "seconds", "value": 12.0})
        meta["ibm"] = {
            "account": "default",
            "family": "heron-r2",
            "rep_delay_s": 0.00025,
            "max_execution_seconds": 30,
            "max_total_execution_seconds": 30,
            "reserve_seconds": 60,
            "exclude_qubits": [113, 131],
            "pin_layout": True,
            "readout_pair_in_job": True,
            "check_cmd": "sh scripts/approved_run.sh --check CMD -- FLAGS",
        }
    elif provider == "quandela":
        meta = common("quandela", "qpu:belenos", {"unit": "credits", "value": 1.02})
        meta["quandela"] = {
            "platform": "qpu:belenos",
            "max_credits": 1.1,
            "per_job_credits": 1.0,
            "mitigations": [],
            "source_modes": [0, 1],
            "routing_health_floor": 0.9,
            "architecture_policy": "retained architecture must equal the live one",
        }
    elif provider == "quantum_inspire":
        meta = common("quantum_inspire", "tuna_17", {"unit": "credits", "value": 0})
        meta["quantum_inspire"] = {
            "backend_type_id": 7,
            "qx_twin_run": "results/quantum_inspire/runs/twin",
            "queue_policy": "wave-v1",
            "readout_pair_per_batch": True,
            "sanity_script": "scripts/qi_sanity.py",
        }
    else:
        meta = common("iqm", "garnet", {"unit": "credits", "value": 4.65})
        meta["iqm"] = {
            "qc": "garnet",
            "max_credits": 9.5,
            "price_per_second": 0.5,
            "calibration_set_id": "2951733a-f569-452e-92bc-44397d6a192e",
            "prediction_sha256": "b" * 64,
        }
    return meta


PROVIDERS = sorted(check_case_contract.PROVIDER_BLOCKS)
COMMON_MUTANTS = [(provider, name) for provider in PROVIDERS for name in check_case_contract.COMMON]
BLOCK_MUTANTS = [(provider, name) for provider in PROVIDERS for name in check_case_contract.PROVIDER_BLOCKS[provider]]


@pytest.mark.parametrize("provider", PROVIDERS)
def test_good_fixture_is_admitted(provider: str) -> None:
    check(check_case_contract.validate(good(provider), require_approval=True) == [])


@pytest.mark.parametrize(("provider", "name"), COMMON_MUTANTS)
def test_each_missing_common_field_is_rejected(provider: str, name: str) -> None:
    meta = good(provider)
    del meta[name]
    problems = check_case_contract.validate(meta)
    check(any(problem.startswith(f"{name}: required field is missing") for problem in problems), str(problems))


@pytest.mark.parametrize(("provider", "name"), BLOCK_MUTANTS)
def test_each_missing_provider_field_is_rejected(provider: str, name: str) -> None:
    meta = good(provider)
    del meta[provider][name]
    problems = check_case_contract.validate(meta)
    check(
        any(problem.startswith(f"{provider}.{name}: required field is missing") for problem in problems), str(problems)
    )


def test_named_provider_mutants() -> None:
    ibm = good("ibm")
    del ibm["ibm"]["max_total_execution_seconds"]
    check("ibm.max_total_execution_seconds: required field is missing" in check_case_contract.validate(ibm))
    belenos = good("quandela")
    del belenos["quandela"]["mitigations"]
    check("quandela.mitigations: required field is missing" in check_case_contract.validate(belenos))
    tuna = good("quantum_inspire")
    del tuna["quantum_inspire"]["qx_twin_run"]
    check("quantum_inspire.qx_twin_run: required field is missing" in check_case_contract.validate(tuna))


@pytest.mark.parametrize(
    ("provider", "path", "value", "needle"),
    [
        ("ibm", ("ibm", "readout_pair_in_job"), False, "ibm.readout_pair_in_job: must be true"),
        ("ibm", ("ibm", "max_execution_seconds"), 31, "exceeds max_total_execution_seconds"),
        ("ibm", ("expected_seconds",), 31.0, "exceeds ibm.max_total_execution_seconds"),
        ("ibm", ("expected_cost",), {"unit": "credits", "value": 1}, "a ibm case counts seconds"),
        ("quandela", ("expected_cost",), {"unit": "credits", "value": 2.0}, "exceeds quandela.max_credits"),
        ("quandela", ("quandela", "mitigations"), None, "quandela.mitigations: must be a list"),
        ("quandela", ("quandela", "platform"), "qpu:ascella", "quandela.platform: differs from backend"),
        (
            "quantum_inspire",
            ("quantum_inspire", "backend_type_id"),
            3,
            "quantum_inspire.backend_type_id: must be one of",
        ),
        (
            "quantum_inspire",
            ("quantum_inspire", "queue_policy"),
            "wave",
            "quantum_inspire.queue_policy: must be one of",
        ),
        ("iqm", ("expected_seconds",), 40.0, "priced above iqm.max_credits"),
        ("iqm", ("iqm", "prediction_sha256"), "xyz", "iqm.prediction_sha256: must be a lowercase 64-digit sha256"),
        ("iqm", ("qrng_seed_refs",), ["seed-17"], "qrng_seed_refs: holds malformed references"),
        ("iqm", ("shots",), 0, "shots: must be a positive integer"),
    ],
)
def test_value_and_relation_mutants_are_rejected(provider: str, path: tuple[str, ...], value: Any, needle: str) -> None:
    meta = good(provider)
    target = meta
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    problems = check_case_contract.validate(meta)
    check(any(needle in problem for problem in problems), str(problems))


def test_unknown_provider_field_and_schema_are_rejected() -> None:
    meta = good("ibm")
    meta["ibm"]["extra"] = 1
    meta["schema"] = "other"
    problems = check_case_contract.validate(meta)
    check("ibm.extra: field is not part of the contract" in problems)
    check("schema: must be case-contract-v1" in problems)
    check(check_case_contract.validate({**copy.deepcopy(good("ibm")), "provider": "aws"})[0].startswith("provider:"))
    check(check_case_contract.validate([]) == ["case_meta.json: the top level must be an object"])


def test_approval_quote_may_be_null_until_required() -> None:
    meta = good("iqm")
    meta["approval_quote"] = None
    check(check_case_contract.validate(meta) == [])
    check(
        check_case_contract.validate(meta, require_approval=True) == ["approval_quote: a quoted approval is required"]
    )


def run_cli(directory: Path, *flags: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--check", str(directory), *flags],
        capture_output=True,
        text=True,
        check=False,
    )


def test_command_line_exit_codes(tmp_path: Path) -> None:
    case = tmp_path / "case"
    case.mkdir()
    check(run_cli(case).returncode == 2)
    meta = good("quandela")
    (case / "case_meta.json").write_text(json.dumps(meta))
    check(run_cli(case, "--require-approval").returncode == 0)
    del meta["quandela"]["mitigations"]
    (case / "case_meta.json").write_text(json.dumps(meta))
    result = run_cli(case)
    check(result.returncode == 1)
    check("quandela.mitigations: required field is missing" in result.stdout)
    (case / "case_meta.json").write_text("{")
    check(run_cli(case).returncode == 2)
