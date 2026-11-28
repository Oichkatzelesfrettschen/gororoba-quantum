"""preflight_check passes the retained run of each provider and fails exactly the gate a mutant breaks."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import preflight_check
import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = Path(preflight_check.__file__)
RUNS = {
    "ibm": "results/live/2026-10-13T083417.634585Z",
    "quandela": "results/quandela/runs/2026-10-17T213646Z-qpu_belenos-box_kite_photonic_single-job-04",
    "iqm": "results/iqm/runs/2026-11-23T162638Z-garnet-grover-plane-mirrored-101-grover",
    "qi": "results/quantum_inspire/runs/2026-10-17T052547Z-zero_divisor_tuna_17-batch-00",
}
DRAW = "docs/evidence/anu_qrng/draw-2026-10-18T083548Z.json"
UNLISTED_SEED = 987654321


def check(condition: object, message: str = "check failed") -> None:
    if not condition:
        raise AssertionError(message)


def load(path: Path) -> Any:
    return json.loads(path.read_text())


def store(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=1, sort_keys=True) + "\n")


def edit(directory: Path, name: str, change: Callable[[Any], None]) -> None:
    value = load(directory / name)
    change(value)
    store(directory / name, value)


def copy_run(provider: str, tmp_path: Path) -> Path:
    target = tmp_path / Path(RUNS[provider]).name
    shutil.copytree(ROOT / RUNS[provider], target)
    return target


def failed(provider: str, directory: Path) -> list[str]:
    return [verdict.gate for verdict in preflight_check.evaluate(provider, directory) if not verdict.ok]


def strip_baseline(value: Any) -> None:
    if isinstance(value, dict):
        for key in [key for key in value if any(token in key.lower() for token in preflight_check.BASELINE_KEYS)]:
            del value[key]
        for item in value.values():
            strip_baseline(item)
    elif isinstance(value, list):
        for item in value:
            strip_baseline(item)


def seed_in(name: str) -> Callable[[Path], None]:
    def mutate(directory: Path) -> None:
        edit(directory, name, lambda value: value.update({"seed": UNLISTED_SEED}))

    return mutate


def ibm_record(change: Callable[[dict[str, Any]], None]) -> Callable[[Path], None]:
    return lambda directory: edit(directory, "record.json", change)


def submission(change: Callable[[dict[str, Any]], None]) -> Callable[[Path], None]:
    return lambda directory: edit(directory, "submission.json", change)


def cases(change: Callable[[dict[str, Any]], None]) -> Callable[[Path], None]:
    return lambda directory: edit(directory, "cases.json", change)


def drop_approval(value: dict[str, Any]) -> None:
    del value["approval"]


def drop_readouts(value: dict[str, Any]) -> None:
    value["circuits"] = [row for row in value["circuits"] if not row["file"].startswith("readout")]


def bump_prediction(directory: Path) -> None:
    with (directory / "prediction.json").open("a") as handle:
        handle.write(" ")


def swap_calibration(directory: Path) -> None:
    edit(directory, "results.json", lambda value: value["compilation"].update({"calibration_set_id": "other"}))


# (provider, gate that must fail, mutation)
MUTANTS: list[tuple[str, str, Callable[[Path], None]]] = [
    (
        "ibm",
        "gate 1 baseline",
        ibm_record(lambda v: v["compiled_ideal_validation"].update(all_candidates_passed=False)),
    ),
    ("ibm", "gate 2 fresh live read", ibm_record(lambda v: v.update(revalidation=[]))),
    ("ibm", "gate 3 seed provenance", ibm_record(lambda v: v.update(seed_simulator=UNLISTED_SEED))),
    (
        "ibm",
        "gate 4 budget and ceiling",
        ibm_record(lambda v: v["budget_plan"].update(max_total_execution_seconds=9999)),
    ),
    (
        "ibm",
        "gate 5 health control",
        ibm_record(lambda v: v["backends"]["ibm_fez"]["excluded_qubits"].update({"136": "readout error 0.3"})),
    ),
    ("ibm", "gate 6 approval and recovery", ibm_record(lambda v: v.pop("approval_consumed"))),
    ("quandela", "gate 1 baseline", cases(strip_baseline)),
    ("quandela", "gate 2 fresh live read", submission(lambda v: v.pop("availability_at_plan"))),
    ("quandela", "gate 3 seed provenance", seed_in("cases.json")),
    ("quandela", "gate 4 budget and ceiling", submission(lambda v: v.update(credit_ceiling=5.0))),
    ("quandela", "gate 5 health control", cases(lambda v: v.pop("preregistered"))),
    ("quandela", "gate 6 approval and recovery", submission(drop_approval)),
    ("iqm", "gate 1 baseline", bump_prediction),
    ("iqm", "gate 2 fresh live read", submission(lambda v: v.pop("credit_before"))),
    ("iqm", "gate 3 seed provenance", seed_in("cases.json")),
    ("iqm", "gate 4 budget and ceiling", submission(lambda v: v.update(expected_seconds=100.0))),
    ("iqm", "gate 5 health control", swap_calibration),
    ("iqm", "gate 6 approval and recovery", submission(drop_approval)),
    ("qi", "gate 1 baseline", cases(strip_baseline)),
    ("qi", "gate 2 fresh live read", submission(lambda v: v.update(backend_status_at_submit="maintenance"))),
    ("qi", "gate 3 seed provenance", seed_in("cases.json")),
    ("qi", "gate 4 budget and ceiling", submission(lambda v: v.update(queue_limit_at_submit=0))),
    ("qi", "gate 5 health control", cases(drop_readouts)),
    ("qi", "gate 6 approval and recovery", submission(drop_approval)),
]


@pytest.mark.parametrize("provider", preflight_check.PROVIDERS)
def test_retained_run_passes_all_six_gates(provider: str) -> None:
    verdicts = preflight_check.evaluate(provider, ROOT / RUNS[provider])
    check([verdict.gate.split(" ", 2)[2] for verdict in verdicts] == list(preflight_check.GATES))
    check(all(verdict.ok for verdict in verdicts), str([v for v in verdicts if not v.ok]))


@pytest.mark.parametrize(("provider", "gate", "mutate"), MUTANTS)
def test_each_mutant_fails_exactly_its_gate(
    provider: str, gate: str, mutate: Callable[[Path], None], tmp_path: Path
) -> None:
    directory = copy_run(provider, tmp_path)
    mutate(directory)
    check(failed(provider, directory) == [gate], str(preflight_check.evaluate(provider, directory)))


def test_every_gate_has_a_mutant_for_every_provider() -> None:
    covered = {(provider, gate) for provider, gate, _ in MUTANTS}
    check(
        covered
        == {(p, f"gate {n} {g}") for p in preflight_check.PROVIDERS for n, g in enumerate(preflight_check.GATES, 1)}
    )


def test_qrng_reference_accounts_for_a_new_seed(tmp_path: Path) -> None:
    value = load(ROOT / DRAW)["values"][3]
    directory = copy_run("quandela", tmp_path)
    edit(directory, "cases.json", lambda v: v.update(seed=value, seed_source=f"qrng:{DRAW}#3"))
    check(failed("quandela", directory) == [])
    edit(directory, "cases.json", lambda v: v.update(seed=value + 1))
    check(failed("quandela", directory) == ["gate 3 seed provenance"])
    edit(directory, "cases.json", lambda v: v.update(seed=value, seed_source=f"qrng:{DRAW}#999999"))
    check(failed("quandela", directory) == ["gate 3 seed provenance"])


def test_case_contract_joins_the_verdicts(tmp_path: Path) -> None:
    directory = copy_run("qi", tmp_path)
    (directory / "case_meta.json").write_text("{}")
    check(failed("qi", directory) == ["case contract"])


def run_cli(provider: str, directory: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--provider", provider, str(directory)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_command_line_exit_codes(tmp_path: Path) -> None:
    passing = run_cli("qi", ROOT / RUNS["qi"])
    check(passing.returncode == 0 and passing.stdout.count("PASS") == 6, passing.stdout)
    directory = copy_run("qi", tmp_path)
    edit(directory, "submission.json", drop_approval)
    refused = run_cli("qi", directory)
    check(refused.returncode == 1 and "FAIL gate 6 approval and recovery" in refused.stdout, refused.stdout)
    check(run_cli("qi", tmp_path / "absent").returncode == 2)
    check(run_cli("ibm", ROOT / RUNS["qi"]).returncode == 2)
