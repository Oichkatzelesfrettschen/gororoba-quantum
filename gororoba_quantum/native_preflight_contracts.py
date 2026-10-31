"""Offline contracts for immutable native mock timing qualification."""

from __future__ import annotations

import ast
import copy
import json
import tempfile
from functools import cache
from importlib.metadata import version
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

import numpy as np
from qiskit import QuantumCircuit
from qiskit_ibm_runtime.fake_provider import FakeFez

import live_run as runtime
import native_preflight
import run_archive
from experiments import Group, Member
from runtime_contracts import _fake_snapshot, _synthetic_fusion_choice


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


class MockResult(list[Any]):
    """Metadata-only fixture; reading randomized measurements fails the test."""

    metadata: dict[str, Any] = {"options": {"execution": {"scheduler_timing": True}}}


class MockPubResult:
    def __init__(self, timing: dict[str, Any]):
        self.metadata = {"compilation": {"scheduler_timing": timing}}

    @property
    def data(self) -> Any:
        raise RuntimeError("native preflight read randomized mock measurements")


class MockJob:
    def __init__(self, probe: Probe, index: int, names: list[str]):
        self.probe = probe
        self.index = index
        self.names = names

    def job_id(self) -> str:
        return f"mock-job-{self.index}"

    @property
    def usage_estimation(self) -> dict[str, Any]:
        return {"quantum_seconds": self.probe.estimate}

    def result(self) -> MockResult:
        report = json.loads(next(self.probe.directory.glob("native-dry-run/*/report.json")).read_text())
        accepted_ids = [entry.get("job_id") for entry in report["jobs"]]
        _require(self.job_id() in accepted_ids, "job identifier was not saved before result wait")
        _require(len(self.probe.calls) == self.probe.expected_calls, "result wait precedes later native calls")
        self.probe.waits.append(self.index)
        if self.probe.result_error:
            raise TimeoutError("fixture result remains unavailable")
        return MockResult([MockPubResult(copy.deepcopy(self.probe.timing)) for _ in self.names])

    def metrics(self) -> dict[str, Any]:
        return {"fixture": True, "instance": "crn:fixture:masked-instance"}


class Probe:
    def __init__(self, directory: Path):
        self.directory = directory
        self.calls: list[dict[str, Any]] = []
        self.waits: list[int] = []
        self.estimate: Any = 3.25
        self.timing: dict[str, Any] = {"circuit_duration": 640, "timing": "instruction,start,duration\nmeasure,0,640\n"}
        self.reject_at: int | None = None
        self.result_error = False
        self.expected_calls = 2
        self.mutate_options = False

    def configure(
        self,
        backend: Any,
        kind: str,
        twirl: bool,
        dd: str | None,
        tags: list[str],
        shots: int,
        ceiling: int | None,
    ) -> Any:
        native = tags[0] == "gororoba-native-dry-run"
        options = {
            "kind": kind,
            "execution": {"rep_delay": 0.00025, "scheduler_timing": True},
            "environment": {"job_tags": tags},
            "default_shots": shots + int(native and self.mutate_options),
            "max_execution_time": ceiling,
            "twirl": twirl,
            "dd": dd,
        }

        def invoke(circuits: list[QuantumCircuit], *, shots: int, dry_run: bool) -> MockJob:
            _require(dry_run is True, "primitive call lost dry_run=True")
            _require(shots == 128, "native shots differ from retained workload")
            index = len(self.calls)
            self.calls.append({"kind": kind, "names": [circuit.name for circuit in circuits], "options": options})
            if self.reject_at == index:
                raise PermissionError("fixture mock backend access denied")
            return MockJob(self, index, [circuit.name for circuit in circuits])

        return SimpleNamespace(options=SimpleNamespace(model_dump=lambda mode: copy.deepcopy(options)), run=invoke)


@cache
def _backend() -> Any:
    return FakeFez()


def _fixture(directory: Path) -> tuple[Any, list[Any], dict[str, Any], Any]:
    snapshot = _fake_snapshot(_backend())
    choices = []
    for index, dynamic in enumerate((True, False)):
        circuit = QuantumCircuit(1, 1)
        if dynamic:
            circuit.reset(0)
        circuit.measure(0, 0)
        name = "fixture_dynamic" if dynamic else "fixture_static"
        group = Group(name, (Member(name + "_member", circuit, np.array([1.0, 0.0])),), lambda values: {})
        choices.append(_synthetic_fusion_choice(group, snapshot, index * 2, dynamic))
    service = SimpleNamespace(active_instance=lambda: "fixture-instance")
    record = {
        "state": "planned",
        "budget_plan": {"admitted": True, "combined_ceiling_seconds": 120.0, "max_total_execution_seconds": 120.0},
        "started": "fixture-native-timing",
        "experiment_digest": runtime.experiment_digest(),
        "instance_sha256_12": runtime._instance_hash(service),
        "backends": {snapshot.name: snapshot.summary()},
        "versions": {"qiskit-ibm-runtime": version("qiskit-ibm-runtime")},
        "shots": 128,
        "policy": {"twirl": False, "dd": None, "max_execution_seconds": 60, "max_pending": None},
        "execution_pubs": [pub.manifest() for pub in runtime.execution_pubs(choices)],
    }
    record["execution_contract"] = runtime.qpu_planning.execution_contract(choices, record)
    runtime.write_archive(directory, choices)
    (directory / "record.json").write_text(json.dumps(record))
    (directory / "approval-consumed.json").write_text("preserved fixture marker\n")
    return service, choices, record, snapshot


def _case(mutation: str | None = None, estimate: Any = 3.25) -> dict[str, Any]:
    with (
        tempfile.TemporaryDirectory(prefix="native-preflight-contract-") as temporary,
        patch.object(runtime, "experiment_digest", lambda: "fixture-source-digest"),
    ):
        directory = Path(temporary)
        service, choices, record, snapshot = _fixture(directory)
        if mutation != "approval_marker":
            (directory / "approval-consumed.json").unlink()
        probe = Probe(directory)
        probe.estimate = estimate
        if mutation == "record":
            record["shots"] = 256
        elif mutation == "unadmitted":
            record["state"] = "design_infeasible"
            (directory / "record.json").write_text(json.dumps(record))
        elif mutation == "aggregate_ceiling":
            record["budget_plan"]["max_total_execution_seconds"] = 6.0
            (directory / "record.json").write_text(json.dumps(record))
        elif mutation == "missing_ceiling":
            record["budget_plan"].pop("combined_ceiling_seconds")
            (directory / "record.json").write_text(json.dumps(record))
        elif mutation == "qpy":
            (directory / "isa.qpy").write_bytes(run_archive.read_archive(directory) + b"changed")
        elif mutation == "source":
            record["experiment_digest"] = "changed"
            (directory / "record.json").write_text(json.dumps(record))
        elif mutation == "contract":
            record["execution_contract"]["backends"][0]["repetition_delay_seconds"] = 0.1
            (directory / "record.json").write_text(json.dumps(record))
        elif mutation == "calibration":
            snapshot = copy.copy(snapshot)
            snapshot.calibration = "changed"
        elif mutation == "options":
            probe.mutate_options = True
        elif mutation in ("denied", "partial"):
            probe.reject_at = 0 if mutation == "denied" else 1
            probe.expected_calls = probe.reject_at + 1
        elif mutation == "duration":
            probe.timing["circuit_duration"] = 1.5
        elif mutation == "timing_csv":
            probe.timing.pop("timing")
        elif mutation == "result":
            probe.result_error = True
        elif mutation == "job_ceiling":
            probe.estimate = 61.0
        before = native_preflight._preserved_files(directory)
        with (
            patch.object(runtime, "configure_sampler", probe.configure),
            patch.object(runtime, "take_snapshot", lambda service, name, excluded=(): snapshot),
        ):
            report = native_preflight.qualify(runtime, service, choices, record, directory)
        _require(before == native_preflight._preserved_files(directory), "preflight changed retained files")
        _require(not (directory / "raw").exists(), "preflight wrote hardware raw data")
        saved = (directory / report["report_path"]).read_text()
        _require("crn:fixture" not in saved, "preflight leaked instance identifier")
        _require(json.loads(saved) == report, "returned report differs from retained report")
        if mutation in (None, "approval_marker") and estimate == 3.25:
            _require(report["qualified"] and report["status"] == "complete", f"valid fixture rejected: {report}")
            _require(report["estimated_quantum_seconds"] == 6.5, "server estimates did not sum")
            _require(report["timing_qualified"] and report["within_execution_ceilings"], "qualification scopes lost")
            _require(len(probe.calls) == 2 and len(probe.waits) == 2, "static/dynamic grouping changed")
        else:
            _require(not report["qualified"], f"mutation was admitted: {mutation}, {estimate}")
            if mutation in ("record", "unadmitted", "qpy", "source", "contract", "calibration", "options"):
                _require(not probe.calls, f"native call preceded mutation rejection: {mutation}")
            if mutation == "denied":
                _require(report["status"] == "unavailable", "permission error status lost")
                _require(len(probe.calls) == 1, "permission failure retried with another path")
            if mutation == "partial":
                _require(report["jobs"][0]["state"] == "complete", "accepted partial job was not collected")
                _require(report["jobs"][1]["state"] == "unavailable", "failed partial attempt lost")
            if mutation in ("duration", "timing_csv", "result", "estimate"):
                _require(len(probe.calls) == 2, f"result fixture failed before both calls: {mutation}")
            if mutation in ("job_ceiling", "aggregate_ceiling", "missing_ceiling"):
                _require(report["timing_qualified"], "valid timing evidence lost on ceiling failure")
                _require(not report["within_execution_ceilings"], "server estimate admitted outside budget")
        return {"case": mutation or "valid", "status": report["status"], "primitive_calls": len(probe.calls)}


def verify() -> list[dict[str, Any]]:
    """Check literal call safety and failures without constructing a live service."""
    tree = ast.parse(Path(native_preflight.__file__).read_text())
    primitive_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "run"
    ]
    _require(len(primitive_calls) == 1, "native adapter must have one primitive call site")
    _require(
        any(
            keyword.arg == "dry_run" and isinstance(keyword.value, ast.Constant) and keyword.value.value is True
            for keyword in primitive_calls[0].keywords
        ),
        "primitive call must bind literal dry_run=True",
    )
    results = [_case(), _case("approval_marker")]
    for mutation in (
        "record",
        "unadmitted",
        "qpy",
        "source",
        "contract",
        "calibration",
        "options",
        "denied",
        "partial",
        "duration",
        "timing_csv",
        "result",
        "job_ceiling",
        "aggregate_ceiling",
        "missing_ceiling",
    ):
        results.append(_case(mutation))
    for estimate in (None, True, -1, 0, "3", float("nan"), float("inf")):
        results.append(_case("estimate", estimate))
    return results


def main() -> None:
    results = verify()
    print(json.dumps({"passed": True, "cases": results}, indent=2))


if __name__ == "__main__":
    main()
