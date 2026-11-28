"""run_records returns one provider-neutral envelope per retained run and fails closed on a defective one."""

from __future__ import annotations

import json
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

import run_records

ROOT = Path(__file__).resolve().parents[2]
RUNS = {
    "ibm": "results/live/2026-10-13T083417.634585Z",
    "quandela": "results/quandela/runs/2026-10-17T213646Z-qpu_belenos-box_kite_photonic_single-job-04",
    "iqm": "results/iqm/runs/2026-11-23T162638Z-garnet-grover-plane-mirrored-101-grover",
    "qi": "results/quantum_inspire/runs/2026-10-17T052547Z-zero_divisor_tuna_17-batch-00",
}
BACKENDS = {"ibm": "ibm_fez", "quandela": "qpu:belenos", "iqm": "garnet", "qi": "tuna_17"}


def check(condition: object, message: str = "check failed") -> None:
    if not condition:
        raise AssertionError(message)


def load(path: Path) -> Any:
    return json.loads(path.read_text())


def store(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=1, sort_keys=True) + "\n")


def copy_run(provider: str, tmp_path: Path) -> Path:
    target = tmp_path / Path(RUNS[provider]).name
    shutil.copytree(ROOT / RUNS[provider], target)
    return target


@pytest.mark.parametrize("provider", run_records.PROVIDERS)
def test_retained_run_admits_with_one_envelope_schema(provider: str) -> None:
    envelope = run_records.read_envelope(provider, ROOT / RUNS[provider])
    check(envelope.validate() == [])
    check(envelope.provider == provider)
    check(envelope.backend == BACKENDS[provider])
    check(envelope.run_dir == RUNS[provider])
    check(envelope.status in ("completed", "done"))
    check(envelope.approval_present)
    check(envelope.job_ids)
    check(envelope.raw_sha256)
    check(envelope.executed_shots)
    check(envelope.health_verdict in run_records.VERDICTS)


def test_envelope_fields_are_identical_across_providers() -> None:
    keys = {
        provider: set(json.loads(run_records.read_envelope(provider, ROOT / RUNS[provider]).to_json()))
        for provider in run_records.PROVIDERS
    }
    check(len({tuple(sorted(value)) for value in keys.values()}) == 1)


@pytest.mark.parametrize("provider", run_records.PROVIDERS)
def test_json_form_is_byte_stable(provider: str) -> None:
    first = run_records.read_envelope(provider, ROOT / RUNS[provider]).to_json()
    second = run_records.read_envelope(provider, ROOT / RUNS[provider]).to_json()
    check(first == second)
    check(first.endswith("}\n"))
    check(json.dumps(json.loads(first), indent=2, sort_keys=True) + "\n" == first)


def test_billed_cost_units_follow_the_provider() -> None:
    ibm = run_records.read_envelope("ibm", ROOT / RUNS["ibm"]).billed_cost
    iqm = run_records.read_envelope("iqm", ROOT / RUNS["iqm"]).billed_cost
    check((ibm.unit, ibm.value) == ("seconds", 11.0))
    check((iqm.unit, iqm.value) == ("credits", 4.5))


def ibm_raw_digest(directory: Path) -> None:
    job = next((directory / "raw").iterdir())
    index = load(job / "index.json")
    first = sorted(index["files"])[0]
    index["files"][first] = "0" * 64
    store(job / "index.json", index)


def quandela_raw_digest(directory: Path) -> None:
    results = load(directory / "results.json")
    results["result_sha256"] = "0" * 64
    store(directory / "results.json", results)


def iqm_raw_digest(directory: Path) -> None:
    results = load(directory / "results.json")
    results["raw_sha256"]["measurements.json"] = "0" * 64
    store(directory / "results.json", results)


def qi_raw_digest(directory: Path) -> None:
    (directory / "raw" / "latin-1.cq.json").write_text("[]\n")


RAW_MUTANTS: dict[str, Callable[[Path], None]] = {
    "ibm": ibm_raw_digest,
    "quandela": quandela_raw_digest,
    "iqm": iqm_raw_digest,
    "qi": qi_raw_digest,
}


@pytest.mark.parametrize("provider", run_records.PROVIDERS)
def test_mutated_raw_digest_is_rejected(provider: str, tmp_path: Path) -> None:
    directory = copy_run(provider, tmp_path)
    RAW_MUTANTS[provider](directory)
    problems = run_records.read_envelope(provider, directory).validate()
    check(problems)
    check(any(problem.startswith("reader:") for problem in problems))


@pytest.mark.parametrize("provider", run_records.PROVIDERS)
def test_missing_approval_is_rejected(provider: str, tmp_path: Path) -> None:
    directory = copy_run(provider, tmp_path)
    if provider == "ibm":
        record = load(directory / "record.json")
        del record["approval_consumed"]
        store(directory / "record.json", record)
    else:
        submission = load(directory / "submission.json")
        del submission["approval"]
        store(directory / "submission.json", submission)
    envelope = run_records.read_envelope(provider, directory)
    check(not envelope.approval_present)
    check("no approval is recorded" in envelope.validate())


def mutate_ibm_live(directory: Path) -> None:
    record = load(directory / "record.json")
    record["approved_record"]["mismatches"] = ["ibm_fez calibration changed"]
    store(directory / "record.json", record)


def mutate_ibm_compiled(directory: Path) -> None:
    record = load(directory / "record.json")
    record["compiled_ideal_validation"]["all_candidates_passed"] = False
    store(directory / "record.json", record)


def mutate_quandela_live(directory: Path) -> None:
    results = load(directory / "results.json")
    results["couplers_checked"] = "live-differ"
    store(directory / "results.json", results)


def mutate_quandela_compiled(directory: Path) -> None:
    results = load(directory / "results.json")
    results["compiled_couplers_checked"] = "differ"
    store(directory / "results.json", results)


def mutate_quandela_routing(directory: Path) -> None:
    store(directory / "analysis.json", {"routing_collapsed_jobs": ["job-04"]})


HEALTH_MUTANTS: list[tuple[str, str, Callable[[Path], None]]] = [
    ("ibm", "live-differ", mutate_ibm_live),
    ("ibm", "compiled-differ", mutate_ibm_compiled),
    ("quandela", "live-differ", mutate_quandela_live),
    ("quandela", "compiled-differ", mutate_quandela_compiled),
    ("quandela", "routing_collapsed", mutate_quandela_routing),
]


@pytest.mark.parametrize(("provider", "verdict", "mutate"), HEALTH_MUTANTS)
def test_void_health_verdicts_are_rejected(
    provider: str, verdict: str, mutate: Callable[[Path], None], tmp_path: Path
) -> None:
    directory = copy_run(provider, tmp_path)
    mutate(directory)
    envelope = run_records.read_envelope(provider, directory)
    check(envelope.health_verdict == verdict)
    check(envelope.void_reasons)
    check(f"health verdict {verdict} voids the run" in envelope.validate())


def test_unknown_provider_raises() -> None:
    with pytest.raises(ValueError, match="not one of"):
        run_records.read_envelope("aws", ROOT)


def test_unreadable_directory_fails_closed(tmp_path: Path) -> None:
    for provider in run_records.PROVIDERS:
        problems = run_records.read_envelope(provider, tmp_path).validate()
        check(problems)
        check("no approval is recorded" in problems)
