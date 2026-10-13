"""Credential-free tests of archived correction mock-scheduling boundaries.

Real QPY archives exercise names, ordering, and retained bytes. Circuit and
schedule validators are injected so these checks isolate preparation behavior;
the separate circuit and schedule contract modules exercise their mathematics.
"""

from __future__ import annotations

import copy
import io
import json
import tempfile
from collections.abc import Callable, Iterator
from contextlib import ExitStack, contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

from qiskit import QuantumCircuit, qpy

import correction_preparation as preparation


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _archive(circuits: list[QuantumCircuit]) -> bytes:
    stream = io.BytesIO()
    qpy.dump(circuits, stream)
    return stream.getvalue()


class _MetadataPub:
    def __init__(self, name: str) -> None:
        self.metadata: dict[str, Any] = {
            "compilation": {"scheduler_timing": {"fixture_member": name, "circuit_duration": 1000}}
        }
        self.data_reads = 0

    @property
    def data(self) -> Any:
        self.data_reads += 1
        raise RuntimeError("randomized mock measurement data must remain unread")


class _Fixture:
    def __init__(self, directory: Path) -> None:
        self.directory = directory
        self.sources = {"fixture.py": "a" * 64}
        self.versions = dict.fromkeys(preparation.PACKAGES, "fixture-version")
        self.calibration = "2026-10-12T00:00:00+00:00"
        self.fingerprint = {"fixture_calibration": "stable"}
        self.instance = "0123456789ab"
        self.delay = 0.00025
        self.before_snapshot: Callable[[], None] = lambda: None
        self.before_configure: Callable[[], None] = lambda: None
        self.before_result: Callable[[], None] = lambda: None
        self.sampler_calls: list[dict[str, Any]] = []
        self.configuration_calls: list[tuple[Any, ...]] = []
        self.schedule_calls: list[dict[str, Any]] = []
        self.circuit_calls: list[tuple[str, str, int]] = []
        self.schedule_qualified = True
        self.pubs = [_MetadataPub(name) for name in preparation.MEMBERS]
        self.returned_pubs = self.pubs[:]
        self.usage: dict[str, Any] = {"quantum_seconds": 11.3}
        self.backend = SimpleNamespace(name="fixture_backend", target=object(), dt=4e-9)
        self.snapshot = SimpleNamespace(
            name=self.backend.name,
            backend=self.backend,
            properties=object(),
            calibration=self.calibration,
            ineligible_reason=lambda _budget: None,
        )
        self.runtime = SimpleNamespace(
            _instance_hash=lambda _service: self.instance,
            take_snapshot=self.take_snapshot,
            fingerprint=lambda *_args: copy.deepcopy(self.fingerprint),
            configure_sampler=self.configure_sampler,
        )
        self.service = object()
        circuits = []
        for name in preparation.MEMBERS:
            circuit = QuantumCircuit(1, 2, name=name)
            circuit.h(0)
            circuit.measure(0, 0)
            circuit.reset(0)
            circuit.measure(0, 1)
            circuits.append(circuit)
        self.circuits = circuits
        files = {"isa.qpy": _archive(circuits), "template.qpy": _archive([circuits[0]])}
        for name, data in files.items():
            (directory / name).write_bytes(data)
        self.pair_reports = {str(label): {"phase_label": label, "fixture_pair": True} for label in (1, 3)}
        self.report: dict[str, Any] = {
            "schema": "known-label-correction-preparation-v1",
            "state": "prepared_schedule_unqualified",
            "physical_execution_authorized": False,
            "native_schedule_qualified": False,
            "backend": self.backend.name,
            "backend_snapshot": {"calibration": self.calibration},
            "instance_sha256_12": self.instance,
            "sources": copy.deepcopy(self.sources),
            "versions": copy.deepcopy(self.versions),
            "files": {name: preparation._hash(data) for name, data in files.items()},
            "member_order": list(preparation.MEMBERS),
            "shots_per_pub": 8192,
            "pub_count": 4,
            "replicas_per_pub": 1,
            "calibration_fingerprint": copy.deepcopy(self.fingerprint),
            "timing": {"repetition_delay_seconds": self.delay},
            "circuit_pairs": copy.deepcopy(self.pair_reports),
        }
        self.bind_report()

    def write_report(self) -> None:
        (self.directory / "preparation.json").write_text(json.dumps(self.report, sort_keys=True) + "\n")

    def bind_report(self) -> None:
        self.write_report()
        self.preparation_sha256 = preparation._hash((self.directory / "preparation.json").read_bytes())

    def take_snapshot(self, _service: Any, backend: str) -> Any:
        _require(backend == self.backend.name, "preparer requested an unbound backend")
        self.before_snapshot()
        return self.snapshot

    def configure_sampler(self, *args: Any) -> Any:
        self.configuration_calls.append(args)
        self.before_configure()
        options = {
            "max_execution_time": 30,
            "execution": {"rep_delay": self.delay},
            "twirling": {"enable_gates": False, "enable_measure": False},
            "dynamical_decoupling": {"enable": False},
        }
        return SimpleNamespace(options=SimpleNamespace(model_dump=lambda **_kwargs: options), run=self.run)

    def run(self, circuits: list[QuantumCircuit], *, shots: int, dry_run: bool) -> Any:
        _require(dry_run is True, "preparer invoked a physical primitive")
        self.sampler_calls.append({"names": [circuit.name for circuit in circuits], "shots": shots, "dry_run": dry_run})
        return SimpleNamespace(job_id=lambda: "fixture_mock_job", result=self.result, usage_estimation=self.usage)

    def result(self) -> list[_MetadataPub]:
        retained = json.loads((self.directory / "native-qualification.json").read_text())
        _require(retained["job_id"] == "fixture_mock_job", "accepted job identity was not retained before waiting")
        _require(retained["status"] == "accepted", "result wait preceded the acceptance checkpoint")
        self.before_result()
        return self.returned_pubs

    def qualify_pair(self, feedback: Any, known: Any, **kwargs: Any) -> dict[str, Any]:
        self.schedule_calls.append({"feedback": feedback, "known": known, **kwargs})
        if not isinstance(feedback, dict) or not isinstance(known, dict):
            raise ValueError("unsupported schedule metadata")
        if "fixture_member" not in feedback or "fixture_member" not in known:
            raise ValueError("unsupported schedule schema")
        return {"schema": "folded-correction-exposed-schedule-pair-v2", "qualified": self.schedule_qualified}

    def validate_pair(
        self, _template: Any, measured: QuantumCircuit, known: QuantumCircuit, label: int
    ) -> dict[str, Any]:
        self.circuit_calls.append((measured.name, known.name, label))
        _require(measured.name == f"correction_measured_s{label}", "circuit validator received wrong measured arm")
        _require(known.name == f"correction_known_s{label}", "circuit validator received wrong known arm")
        return copy.deepcopy(self.pair_reports[str(label)])

    def qualify(self) -> dict[str, Any]:
        return preparation.native_qualification(
            self.service,
            self.directory,
            expected_preparation_sha256=self.preparation_sha256,
            runtime=self.runtime,
        )


@contextmanager
def _fixture() -> Iterator[_Fixture]:
    with tempfile.TemporaryDirectory(prefix="correction-preparation-contract-") as directory, ExitStack() as stack:
        fixture = _Fixture(Path(directory))
        stack.enter_context(
            patch.object(preparation, "source_hashes", side_effect=lambda: copy.deepcopy(fixture.sources))
        )
        stack.enter_context(patch.object(preparation, "version", side_effect=lambda name: fixture.versions[name]))
        stack.enter_context(patch.object(preparation, "repetition_delay", side_effect=lambda _backend: fixture.delay))
        stack.enter_context(
            patch.object(preparation.correction_schedule, "qualify_pair", side_effect=fixture.qualify_pair)
        )
        stack.enter_context(
            patch.object(preparation.correction_circuits, "validate_correction_pair", side_effect=fixture.validate_pair)
        )
        yield fixture


def _check_success() -> None:
    with _fixture() as fixture:
        originals = {
            name: (fixture.directory / name).read_bytes() for name in ("preparation.json", "isa.qpy", "template.qpy")
        }
        report = fixture.qualify()
        _require(report["qualified"] is True and report["physical_execution_authorized"] is False, "mock scope changed")
        _require(report["status"] == "schedule_qualified_preparation_only", "qualification became submission authority")
        _require(
            fixture.sampler_calls == [{"names": list(preparation.MEMBERS), "shots": 8192, "dry_run": True}],
            "mock primitive lost exact PUB identities, order, shots or dry-run flag",
        )
        arguments = fixture.configuration_calls[0]
        _require(arguments[1:4] == ("dynamic", False, None), "native options changed dynamic/twirling/DD policy")
        _require(arguments[-2:] == (8192, 30), "mock ceiling or shot count changed")
        _require(len(fixture.schedule_calls) == 2, "successful scheduling skipped the strict pair validator")
        _require(
            fixture.circuit_calls
            == [
                ("correction_measured_s1", "correction_known_s1", 1),
                ("correction_measured_s3", "correction_known_s3", 3),
            ],
            "qualification skipped restored-circuit revalidation",
        )
        for call, label in zip(fixture.schedule_calls, (1, 3), strict=True):
            _require(call["feedback"]["fixture_member"] == f"correction_measured_s{label}", "feedback timing misbound")
            _require(call["known"]["fixture_member"] == f"correction_known_s{label}", "known timing misbound")
            _require(call["circuit_pair_report"] == fixture.pair_reports[str(label)], "pair evidence misbound")
            _require(call["dt_seconds"] == fixture.backend.dt, "backend time unit changed")
        _require(all(pub.data_reads == 0 for pub in fixture.pubs), "mock measurement data was inspected")
        for name, expected in originals.items():
            _require((fixture.directory / name).read_bytes() == expected, f"qualification changed retained {name}")
        try:
            fixture.qualify()
        except ValueError:
            pass
        else:
            raise RuntimeError("existing qualification permitted a repeated native call")
        _require(len(fixture.sampler_calls) == 1, "duplicate qualification invoked the primitive")


def _check_digest_binding() -> None:
    for mutation in ("report_changed_before_call", "wrong_expected_digest"):
        with _fixture() as fixture:
            if mutation == "report_changed_before_call":
                fixture.report["shots_per_pub"] = 4096
                fixture.write_report()
            else:
                fixture.preparation_sha256 = "0" * 64
            try:
                fixture.qualify()
            except ValueError as error:
                _require(str(error) == "preparation digest differs from expected bytes", mutation)
            else:
                raise RuntimeError(f"{mutation}: unbound preparation accepted")
            _require(fixture.sampler_calls == [], f"{mutation}: primitive reached")
            _require(not (fixture.directory / "native-qualification.json").exists(), "unbound record was checkpointed")


def _check_pre_call_mutations() -> None:
    def altered_qpy(fixture: _Fixture) -> None:
        with (fixture.directory / "isa.qpy").open("ab") as stream:
            stream.write(b"changed")

    def altered_template(fixture: _Fixture) -> None:
        (fixture.directory / "template.qpy").write_bytes(b"changed")

    def altered_report_during_snapshot(fixture: _Fixture) -> None:
        def change_report() -> None:
            (fixture.directory / "preparation.json").write_text("changed")

        fixture.before_snapshot = change_report

    def altered_sources(fixture: _Fixture) -> None:
        fixture.sources["fixture.py"] = "b" * 64

    def altered_versions(fixture: _Fixture) -> None:
        fixture.versions["numpy"] = "changed"

    def altered_calibration(fixture: _Fixture) -> None:
        fixture.snapshot.calibration = "2026-10-12T01:00:00+00:00"

    def altered_fingerprint(fixture: _Fixture) -> None:
        fixture.fingerprint["fixture_calibration"] = "changed"

    def altered_instance(fixture: _Fixture) -> None:
        fixture.instance = "fedcba987654"

    def altered_delay(fixture: _Fixture) -> None:
        fixture.delay = 0.0001

    def altered_order(fixture: _Fixture) -> None:
        archive = _archive(list(reversed(fixture.circuits)))
        (fixture.directory / "isa.qpy").write_bytes(archive)
        fixture.report["files"]["isa.qpy"] = preparation._hash(archive)
        fixture.bind_report()

    def altered_source_at_configure(fixture: _Fixture) -> None:
        fixture.before_configure = lambda: fixture.sources.update({"fixture.py": "b" * 64})

    def incomplete_versions(fixture: _Fixture) -> None:
        del fixture.report["versions"]["numpy"]
        fixture.bind_report()

    def incomplete_archive(fixture: _Fixture) -> None:
        del fixture.report["files"]["template.qpy"]
        fixture.bind_report()

    def escaped_archive_path(fixture: _Fixture) -> None:
        fixture.report["files"]["../unexpected.qpy"] = "0" * 64
        fixture.bind_report()

    def altered_pair_report(fixture: _Fixture) -> None:
        fixture.report["circuit_pairs"]["1"]["fixture_pair"] = False
        fixture.bind_report()

    def multiple_templates(fixture: _Fixture) -> None:
        archive = _archive(fixture.circuits[:2])
        (fixture.directory / "template.qpy").write_bytes(archive)
        fixture.report["files"]["template.qpy"] = preparation._hash(archive)
        fixture.bind_report()

    def boolean_shots(fixture: _Fixture) -> None:
        fixture.report["shots_per_pub"] = True
        fixture.bind_report()

    def invalid_execution_state(fixture: _Fixture) -> None:
        fixture.report["physical_execution_authorized"] = True
        fixture.bind_report()

    for mutate, expected_reason in (
        (altered_qpy, "archive changed: isa.qpy"),
        (altered_template, "archive changed: template.qpy"),
        (altered_report_during_snapshot, "preparation record changed"),
        (altered_sources, "preparation source changed"),
        (altered_versions, "dependency changed: numpy"),
        (altered_calibration, "calibration changed"),
        (altered_fingerprint, "compiled calibration changed"),
        (altered_instance, "service instance changed"),
        (altered_delay, "repetition delay changed"),
        (altered_order, "QPY member order changed"),
        (altered_source_at_configure, "preparation source changed"),
        (incomplete_versions, "dependency manifest is incomplete"),
        (incomplete_archive, "archive manifest is incomplete"),
        (escaped_archive_path, "archive manifest is incomplete"),
        (altered_pair_report, "archived pair report changed"),
        (multiple_templates, "exactly one common template is required"),
        (boolean_shots, "invalid shot count"),
        (invalid_execution_state, "preparation has an invalid execution state"),
    ):
        with _fixture() as fixture:
            mutate(fixture)
            report = fixture.qualify()
            _require(report["qualified"] is False and report["status"] == "unqualified", mutate.__name__)
            _require(
                report.get("reason") == expected_reason, f"{mutate.__name__}: expected gate was not reached: {report}"
            )
            _require(fixture.sampler_calls == [] and report["job_id"] is None, f"{mutate.__name__}: primitive reached")


def _check_accepted_failures() -> None:
    for failure in (
        "missing_timing",
        "unsupported_timing",
        "unqualified_pair",
        "short_result",
        "result_error",
        "missing_usage",
        "boolean_usage",
        "nonfinite_usage",
        "source_drift",
    ):
        with _fixture() as fixture:
            if failure == "missing_timing":
                fixture.pubs[0].metadata = {}
            elif failure == "unsupported_timing":
                fixture.pubs[0].metadata["compilation"]["scheduler_timing"] = {"other_schema": True}
            elif failure == "unqualified_pair":
                fixture.schedule_qualified = False
            elif failure == "short_result":
                fixture.returned_pubs = fixture.pubs[:3]
            elif failure == "result_error":

                def fail_result() -> None:
                    raise RuntimeError("fixture result retrieval failed")

                fixture.before_result = fail_result
            elif failure == "missing_usage":
                fixture.usage.clear()
            elif failure == "boolean_usage":
                fixture.usage["quantum_seconds"] = True
            elif failure == "nonfinite_usage":
                fixture.usage["quantum_seconds"] = float("inf")
            else:
                fixture.before_result = lambda: fixture.sources.update({"fixture.py": "b" * 64})
            report = fixture.qualify()
            retained = json.loads((fixture.directory / "native-qualification.json").read_text())
            _require(report == retained, f"{failure}: returned and retained reports differ")
            _require(report["status"] == "unqualified" and report["qualified"] is False, f"{failure}: failed open")
            _require(report["job_id"] == "fixture_mock_job", f"{failure}: accepted job identity lost")
            _require(len(fixture.sampler_calls) == 1, f"{failure}: unexpected primitive count")
            _require(all(pub.data_reads == 0 for pub in fixture.pubs), f"{failure}: mock data was read")


def main() -> None:
    _check_success()
    _check_digest_binding()
    _check_pre_call_mutations()
    _check_accepted_failures()
    print(
        "Correction preparation: mock-only calls, exact PUBs, mutation guards and retained failure identities verified"
    )


if __name__ == "__main__":
    main()
