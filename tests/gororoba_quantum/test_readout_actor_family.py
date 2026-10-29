"""Full-PUB actor planning, approval and collection without a dense state space."""

from __future__ import annotations

import copy
import io
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from qiskit import qpy
from qiskit.circuit import Delay, Measure, Parameter, Reset
from qiskit.circuit.library import XGate
from qiskit.primitives.containers import BitArray, DataBin, PrimitiveResult, SamplerPubResult
from qiskit.transpiler import InstructionProperties, Target
from qiskit_ibm_runtime.options_models import SamplerOptions

import adjudicate
import live_run
import qpu_cases
import readout_actor_family as family


def submit_reviewed(*arguments: Any, **keywords: Any) -> None:
    if "reviewed_dir" not in keywords:
        keywords["reviewed_dir"] = arguments[-2]
        keywords["reviewed_sha256"] = arguments[-1]
    family.submit(*arguments, **keywords)


def case() -> dict[str, Any]:
    return {
        "schema": "readout-actor-case-v1",
        "backend": "fixture-backend",
        "width": 156,
        "reporters": [0, 1],
        "actors": [2],
        "pairs": [[0, 1]],
        "groups": [[0, 1, 155]],
        "allocations": [
            {
                "name": f"actor-{arm}-{bits}",
                "arm": arm,
                "input": bits,
                "stage": "references",
                "shots": 4,
                "rep_delay_seconds": 0.00003,
            }
            for arm in ("idle", "active")
            for bits in range(4)
        ],
        "purpose": "Qualification of full-register retention and descriptive actor contrasts",
        "reference_rule": "Retain all four preparations under both actor arms",
        "carryover_rule": "Report within-PUB positions; withhold physical predecessor claims",
        "selection_rule": "Retain every fixed pair and group without outcome selection",
        "inference": "descriptive",
        "max_execution_seconds": 5,
        "max_total_execution_seconds": 5,
        "reserve_seconds": 1,
        "max_pending": 100,
        "initialization_seconds": 0.000003,
        "job_overhead_seconds": 2,
    }


class Job:
    def __init__(self, circuits: list[Any], shots: int) -> None:
        self.circuits = circuits
        self.shots = shots

    def job_id(self) -> str:
        return "fixture-job"

    def backend(self) -> Any:
        return SimpleNamespace(name="fixture-backend")

    def status(self) -> str:
        return "DONE"

    def metrics(self) -> dict[str, Any]:
        return {"usage": {"status": "complete"}}

    def usage(self, partial: bool = False) -> float:
        return 0.5

    def result(self) -> Any:
        rows = []
        for circuit in self.circuits:
            values = [0] * circuit.num_qubits
            for item in circuit.data:
                if item.operation.name == "x":
                    values[circuit.find_bit(item.qubits[0]).index] ^= 1
            strings = ["".join(str(value) for value in reversed(values))] * self.shots
            rows.append(
                SamplerPubResult(DataBin(c=BitArray.from_samples(strings, num_bits=circuit.num_clbits)), metadata={})
            )
        return PrimitiveResult(rows, metadata={})


@pytest.fixture
def environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Any:
    target = Target(num_qubits=156, dt=4e-9)
    target.add_instruction(XGate(), {(index,): InstructionProperties(duration=32e-9) for index in range(156)})
    target.add_instruction(Measure(), {(index,): InstructionProperties(duration=2.18e-6) for index in range(156)})
    target.add_instruction(Delay(Parameter("duration"), unit="dt"), {(index,): None for index in range(156)})
    configuration = SimpleNamespace(
        dynamic_reprate_enabled=True,
        default_rep_delay=0.00025,
        rep_delay_range=[0.00002, 0.001],
        processor_type={"family": "heron"},
        max_shots=1_000_000,
    )
    backend = SimpleNamespace(name="fixture-backend", target=target, configuration=lambda: configuration)
    properties = SimpleNamespace(fingerprint=1)
    snapshot = live_run.Snapshot(
        backend,
        properties,
        backend.name,
        True,
        "active",
        0,
        "2026-10-28T00:00:00Z",
        "2026-10-28T00:00:00Z",
        live_run.BackendCapabilities(156, True, ("cz", "x", "measure", "delay"), ()),
    )
    env = SimpleNamespace(backend=backend, snapshot=snapshot, sent=[], instance="fixture-instance", remaining=68.0)
    env.backends = lambda: [backend]
    env.active_instance = lambda: env.instance
    env.usage = lambda: {"usage_remaining_seconds": env.remaining, "usage_limit_reached": False}
    env.job = lambda job_id: env.sent[0]
    monkeypatch.setattr(live_run, "take_snapshot", lambda *args: snapshot)
    monkeypatch.setattr(live_run, "calibration_values", lambda circuits, target, props: {"fixture": props.fingerprint})
    monkeypatch.setattr(live_run, "_distribution", lambda *args: pytest.fail("dense probability allocation reached"))
    monkeypatch.setattr(live_run, "all_experiment_groups", lambda: pytest.fail("dense ideal construction reached"))
    monkeypatch.setattr(family, "_approval_registry", lambda: tmp_path / "approval-registry", raising=False)

    def sampler(
        _backend: Any, _kind: str, _twirl: bool, _dd: Any, tags: Any, shots: int, ceiling: int, *, rep_delay: float
    ) -> Any:
        def run(circuits: list[Any]) -> Job:
            job = Job(circuits, shots)
            env.sent.append(job)
            return job

        options = SamplerOptions(default_shots=shots, max_execution_time=ceiling)
        options.execution.rep_delay = rep_delay
        options.execution.scheduler_timing = True
        options.environment.job_tags = tags
        return SimpleNamespace(run=run, options=options)

    monkeypatch.setattr(live_run, "configure_sampler", sampler)
    return env


def save_plan(directory: Path, environment: Any) -> tuple[dict[str, Any], bytes]:
    record, archive, _ = family.plan(live_run, environment, case())
    directory.mkdir()
    (directory / "isa.qpy").write_bytes(archive)
    live_run.write_json(directory, record)
    live_run._write_once_atomically(directory / "actor-case.json", family.encode(case()).decode())
    return record, archive


@pytest.mark.parametrize("partial", [False, True])
def test_actor_plan_rejects_incomplete_target_reset_durations(environment: Any, partial: bool) -> None:
    durations = {(index,): InstructionProperties(duration=2e-6) for index in range(155)} if partial else {}
    durations[(155,)] = None
    environment.backend.target.add_instruction(Reset(), durations)
    with pytest.raises(ValueError, match="reset duration"):
        family.plan(live_run, environment, case())


@pytest.mark.parametrize("field", ["pairs", "groups"])
def test_actor_qubits_are_excluded_from_reporter_projections(field: str) -> None:
    specification = case()
    specification[field] = [[0, 2]]
    with pytest.raises(ValueError, match="actor"):
        family.validate_case(specification)


def test_adjudicator_reports_missing_anchored_collection(tmp_path: Path) -> None:
    (tmp_path / "record.json").write_bytes(family.encode({"family_configuration": {"name": family.FAMILY}}))
    with pytest.raises(adjudicate.AdjudicationError, match="collection"):
        adjudicate.adjudicate(None, tmp_path, actor_collection_sha256="0" * 64)


def test_actor_dry_run_has_unapproved_written_case(environment: Any, tmp_path: Path) -> None:
    run = tmp_path / "run"
    record, archive = save_plan(run, environment)
    destination = qpu_cases.write_case(run, record)
    if destination is None:
        raise AssertionError("the full-PUB plan must have a reviewable unapproved case")
    text = destination.read_text()
    if (
        "UNAPPROVED" not in text
        or family.digest(archive) not in text
        or "descriptive" not in text
        or "--actor-reviewed-record" not in text
        or "--actor-reviewed-sha256" not in text
    ):
        raise AssertionError("the case must bind the archive and describe the unapproved inference boundary")
    command = text.split("```sh\n", 1)[1].split("\n```", 1)[0]
    arguments = shlex.split(command)
    reviewed_path = arguments[arguments.index("--actor-reviewed-record") + 1]
    if (Path(qpu_cases.__file__).parent / reviewed_path).resolve() != run.resolve():
        raise AssertionError("the generated command must reach the actual reviewed run outside the checkout")
    check = arguments[arguments.index("--check") + 1]
    executed = subprocess.run(
        ["sh", "-c", check],
        cwd=Path(qpu_cases.__file__).parent,
        env=os.environ | {"PYTHON": sys.executable, "RUN": str(run)},
        capture_output=True,
        text=True,
        check=False,
    )
    if executed.returncode:
        raise AssertionError(f"the generated offline check must reach the reviewed case: {executed.stderr}")
    (run / "isa.qpy").write_bytes(archive + b"changed")
    with pytest.raises(ValueError, match="QPY"):
        qpu_cases.write_case(run, record)


@pytest.mark.parametrize("mutation", ["physical", "register", "backend", "shots"])
def test_archive_rejects_forged_pub_mapping(environment: Any, mutation: str) -> None:
    record, archive, _ = family.plan(live_run, environment, case())
    first = record["execution_pubs"][0]
    if mutation == "physical":
        first["components"][0]["physical_qubits"] = [0]
    elif mutation == "register":
        first["components"][0]["registers_by_replica"] = [["wrong"]]
    elif mutation == "backend":
        first["backend"] = "other"
    else:
        record["pub_shots"][first["name"]] += 1
    with pytest.raises(ValueError, match="actor.*(manifest|allocation)"):
        family.verify_archive(record, archive)


@pytest.mark.parametrize("field", ["status", "hardware_verdict"])
def test_collector_rejects_forged_inference_verdict(environment: Any, tmp_path: Path, field: str) -> None:
    approved = tmp_path / "approved"
    record, archive = save_plan(approved, environment)
    run = tmp_path / "run"
    run.mkdir()
    (run / "isa.qpy").write_bytes(archive)
    submit_reviewed(
        live_run, environment, record, archive, run, approved, family.digest((approved / "record.json").read_bytes())
    )
    record["inference"][field] = "confirmed"
    live_run.write_json(run, record)
    with pytest.raises(ValueError, match="inference"):
        family.collect(live_run, environment, run, family.digest((run / "record.json").read_bytes()))


def test_full_width_approved_submit_collect_and_adjudicate(
    environment: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(adjudicate, "bit_values", lambda *_args: pytest.fail("full-string integer narrowing reached"))
    approved = tmp_path / "approved"
    record, archive = save_plan(approved, environment)
    run = tmp_path / "run"
    run.mkdir()
    (run / "isa.qpy").write_bytes(archive)
    anchor = family.digest((approved / "record.json").read_bytes())
    fresh, fresh_archive, _ = family.plan(live_run, environment, case())
    if live_run.approved_record_mismatches(approved, fresh, family.digest(fresh_archive), anchor):
        raise AssertionError("independent fresh actor plans must preserve the approved QPY identity")
    record, archive = fresh, fresh_archive
    submit_reviewed(live_run, environment, record, archive, run, approved, anchor)
    for options in record["execution_contract"]["runtime_options"]:
        if (
            options["twirling"]["enable_gates"] is not False
            or options["twirling"]["enable_measure"] is not False
            or options["dynamical_decoupling"]["enable"] is not False
            or options["execution"]["init_qubits"] is not True
        ):
            raise AssertionError("the actor policy must bind initialization and disable every twirl/DD")
    if len(environment.sent) != 1 or record["state"] != "submitted":
        raise AssertionError("one complete actor batch must submit")
    live_run.collect(environment, run, actor_record_sha256=family.digest((run / "record.json").read_bytes()))
    collections = list(run.glob("actor-collection-*.json"))
    if len(collections) != 1:
        raise AssertionError("collection must retain one anchored descriptive record")
    result = adjudicate.adjudicate(None, run, actor_collection_sha256=family.digest(collections[0].read_bytes()))
    if result.get("reviewed_record_sha256") != anchor:
        raise AssertionError("adjudication must retain the independently reviewed record digest")
    if result.get("all_allocations_retained") is not True or "complete_case_valid" in result:
        raise AssertionError("retention completeness must not claim timing or alignment validity")
    if len(result["jobs"]["fixture-job"]["pubs"]) != 8 or result["inference"]["hardware_verdict"] is not None:
        raise AssertionError("full-width adjudication must remain descriptive")
    for pub in result["jobs"]["fixture-job"]["pubs"]:
        if pub["projection"]["pair_counts"][0]["error_cells_00_01_10_11"] != [4, 0, 0, 0]:
            raise AssertionError("prepared-bit errors must survive 156-bit collection and projection")
    archive_path = run / "isa.qpy"
    displaced = run / "held-isa.qpy"
    archive_path.rename(displaced)
    try:
        with pytest.raises(adjudicate.AdjudicationError):
            adjudicate.adjudicate(None, run, actor_collection_sha256=family.digest(collections[0].read_bytes()))
        with pytest.raises(live_run.LiveRunError):
            live_run.collect(environment, run, actor_record_sha256=family.digest((run / "record.json").read_bytes()))
    finally:
        displaced.rename(archive_path)
    metadata = run / "raw" / "fixture-job" / "result_metadata.json"
    original_metadata = metadata.read_bytes()
    metadata.write_bytes(original_metadata + b" ")
    try:
        with pytest.raises(adjudicate.AdjudicationError, match="indexed"):
            adjudicate.adjudicate(None, run, actor_collection_sha256=family.digest(collections[0].read_bytes()))
    finally:
        metadata.write_bytes(original_metadata)
    original_record_bytes = (run / "record.json").read_bytes()
    with pytest.raises(live_run.LiveRunError, match="consumed"):
        fresh, fresh_archive, _ = family.plan(live_run, environment, case())
        submit_reviewed(live_run, environment, fresh, fresh_archive, run, approved, anchor)
    if len(environment.sent) != 1:
        raise AssertionError("consumed approval must prohibit another submission")
    if (run / "record.json").read_bytes() != original_record_bytes:
        raise AssertionError("duplicate submission refusal must preserve the retained ledger bytes")


@pytest.mark.audit
def test_full_width_collection_includes_input_and_parsing_memory(
    environment: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(adjudicate, "bit_values", lambda *_args: pytest.fail("full-string integer narrowing reached"))

    def memory() -> dict[str, int]:
        rows = (Path("/proc/self/status").read_text()).splitlines()
        return {row.split(":", 1)[0]: int(row.split()[1]) for row in rows if row.startswith(("VmRSS:", "VmHWM:"))}

    initial = memory()
    specification = case()
    specification["allocations"] = [dict(specification["allocations"][0], shots=40000)]
    record, archive, _ = family.plan(live_run, environment, specification)
    reviewed = tmp_path / "reviewed"
    reviewed.mkdir()
    (reviewed / "isa.qpy").write_bytes(archive)
    live_run.write_json(reviewed, record)
    run = tmp_path / "run"
    run.mkdir()
    (run / "isa.qpy").write_bytes(archive)
    submit_reviewed(
        live_run, environment, record, archive, run, reviewed, family.digest((reviewed / "record.json").read_bytes())
    )
    collected = family.collect(live_run, environment, run, family.digest((run / "record.json").read_bytes()))
    replay = family.adjudicate(live_run, run, family.digest(Path(collected["path"]).read_bytes()))
    if replay["jobs"]["fixture-job"]["pubs"][0]["projection"]["num_shots"] != 40000:
        raise AssertionError("the full collector must retain and replay every 156-bit shot")
    final = memory()
    print(f"full-PUB synthetic 40000 shots: initial {initial} KiB; final {final} KiB")


@pytest.mark.parametrize("mutation", ["anchor", "quota", "instance", "source", "calibration", "preparation", "mapping"])
def test_submission_refuses_changed_bindings(environment: Any, tmp_path: Path, mutation: str) -> None:
    approved = tmp_path / "approved"
    record, archive = save_plan(approved, environment)
    run = tmp_path / "run"
    run.mkdir()
    anchor = family.digest((approved / "record.json").read_bytes())
    if mutation == "anchor":
        anchor = "0" * 64
    elif mutation == "quota":
        environment.remaining = 1
    elif mutation == "instance":
        environment.instance = "other-instance"
    elif mutation == "source":
        record["family_configuration"]["source_sha256"]["scripts/readout_sparse_receipt.py"] = "0" * 64
    elif mutation == "calibration":
        environment.snapshot.properties.fingerprint = 2
    else:
        circuits = qpy.load(io.BytesIO(archive))
        if mutation == "preparation":
            circuits[0].x(2)
        else:
            circuits[0].measure(1, 0)
        buffer = io.BytesIO()
        qpy.dump(circuits, buffer)
        archive = buffer.getvalue()
        record["qpy_sha256"] = family.digest(archive)
    with pytest.raises((ValueError, live_run.LiveRunError)):
        submit_reviewed(live_run, environment, record, archive, run, approved, anchor)
    if environment.sent or (approved / "approval-consumed.json").exists():
        raise AssertionError("failed admission must leave approval unconsumed")


def test_collector_requires_external_anchor_and_matching_instance(environment: Any, tmp_path: Path) -> None:
    approved = tmp_path / "approved"
    record, archive = save_plan(approved, environment)
    run = tmp_path / "run"
    run.mkdir()
    (run / "isa.qpy").write_bytes(archive)
    submit_reviewed(
        live_run, environment, record, archive, run, approved, family.digest((approved / "record.json").read_bytes())
    )
    with pytest.raises(live_run.LiveRunError, match="anchor"):
        live_run.collect(environment, run)
    environment.instance = "other-instance"
    with pytest.raises(live_run.LiveRunError, match="instance"):
        live_run.collect(environment, run, actor_record_sha256=family.digest((run / "record.json").read_bytes()))


@pytest.mark.parametrize("mutation", ["archive", "order"])
def test_collector_rejects_submission_ledger_that_differs_from_approved_case(
    environment: Any, tmp_path: Path, mutation: str
) -> None:
    approved = tmp_path / "approved"
    record, archive = save_plan(approved, environment)
    run = tmp_path / "run"
    run.mkdir()
    (run / "isa.qpy").write_bytes(archive)
    submit_reviewed(
        live_run, environment, record, archive, run, approved, family.digest((approved / "record.json").read_bytes())
    )
    submission = record["submission"]
    planned = submission["planned_jobs"][0]
    submitted = submission["jobs"][0]
    if mutation == "archive":
        submission["qpy_archive_sha256"] = "0" * 64
        for row in (planned, submitted):
            row["qpy_archive_sha256"] = "0" * 64
    else:
        for row in (planned, submitted):
            row["pubs"] = list(reversed(row["pubs"]))
            row["members"] = list(reversed(row["members"]))
    tags = live_run._recovery_tags(
        submission["started"],
        planned["backend"],
        planned["kind"],
        planned["batch_index"],
        planned["batch_count"],
        planned["pubs"],
        submission["qpy_archive_sha256"],
    )
    for row in (planned, submitted):
        row["recovery_tags"] = tags
    live_run.write_json(run, record)
    with pytest.raises(ValueError, match="actor submission"):
        family.collect(live_run, environment, run, family.digest((run / "record.json").read_bytes()))


@pytest.mark.parametrize(
    "field,value",
    [("job_overhead_seconds", 0), ("initialization_seconds", 0), ("inference", "confirmatory"), ("reference_rule", "")],
)
def test_incomplete_or_optimistic_case_refuses_planning(environment: Any, field: str, value: Any) -> None:
    request = copy.deepcopy(case())
    request[field] = value
    with pytest.raises(ValueError):
        family.plan(live_run, environment, request)


def test_live_cli_routes_actor_plan_before_dense_groups(
    environment: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    request = tmp_path / "case.json"
    request.write_bytes(family.encode(case()))
    monkeypatch.setattr(live_run.ibm_account, "open_service", lambda constructor: environment)
    output = tmp_path / "runs"
    status = live_run.main(
        [
            "--family",
            family.FAMILY,
            "--actor-case",
            str(request),
            "--out",
            str(output),
            "--max-execution-seconds",
            "5",
            "--max-total-execution-seconds",
            "5",
        ]
    )
    if status != 0 or len(list(output.glob("*/record.json"))) != 1 or environment.sent:
        raise AssertionError("the public CLI must create a bounded submit-free actor plan")
    with pytest.raises(SystemExit):
        live_run.main(
            [
                "--family",
                family.FAMILY,
                "--actor-case",
                str(request),
                "--out",
                str(output),
                "--max-execution-seconds",
                "5",
                "--max-total-execution-seconds",
                "5",
                "--exclude-qubits",
                "fixture-backend:0",
            ]
        )


def test_actor_submission_requires_independently_reviewed_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    request = tmp_path / "case.json"
    request.write_bytes(family.encode(case()))
    monkeypatch.setattr(live_run.ibm_account, "open_service", lambda *_args: pytest.fail("provider access reached"))
    with pytest.raises(SystemExit):
        live_run.main(
            [
                "--family",
                family.FAMILY,
                "--actor-case",
                str(request),
                "--out",
                str(tmp_path),
                "--max-execution-seconds",
                "5",
                "--max-total-execution-seconds",
                "5",
                "--submit",
                "--approved-record",
                str(tmp_path),
                "--approved-record-sha256",
                "0" * 64,
            ]
        )


def test_actor_reviewed_record_rejects_changed_fresh_case(
    environment: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    approved = tmp_path / "reviewed"
    save_plan(approved, environment)
    request = tmp_path / "changed.json"
    altered = case()
    altered["selection_rule"] = "A different candidate-selection rule"
    request.write_bytes(family.encode(altered))
    monkeypatch.setattr(live_run.ibm_account, "open_service", lambda *_args: environment)
    status = live_run.main(
        [
            "--family",
            family.FAMILY,
            "--actor-case",
            str(request),
            "--out",
            str(tmp_path / "runs"),
            "--max-execution-seconds",
            "5",
            "--max-total-execution-seconds",
            "5",
            "--actor-reviewed-record",
            str(approved),
            "--actor-reviewed-sha256",
            family.digest((approved / "record.json").read_bytes()),
        ]
    )
    if status == 0 or environment.sent:
        raise AssertionError("fresh planning must refuse a case that differs from independent review")


def test_reviewed_actor_approval_is_consumed_across_wrapper_runs(environment: Any, tmp_path: Path) -> None:
    reviewed = tmp_path / "reviewed"
    save_plan(reviewed, environment)
    reviewed_hash = family.digest((reviewed / "record.json").read_bytes())
    for index in range(2):
        binding = tmp_path / f"binding-{index}"
        record, archive = save_plan(binding, environment)
        run = tmp_path / f"run-{index}"
        run.mkdir()
        (run / "isa.qpy").write_bytes(archive)
        arguments = (
            live_run,
            environment,
            record,
            archive,
            run,
            binding,
            family.digest((binding / "record.json").read_bytes()),
        )
        if index == 0:
            submit_reviewed(*arguments, reviewed_dir=reviewed, reviewed_sha256=reviewed_hash)
        else:
            with pytest.raises(live_run.LiveRunError, match="consumed"):
                submit_reviewed(*arguments, reviewed_dir=reviewed, reviewed_sha256=reviewed_hash)
    if len(environment.sent) != 1:
        raise AssertionError("a reviewed authorization must permit only one submission attempt")


def test_reviewed_record_copy_cannot_reuse_consumed_authorization(environment: Any, tmp_path: Path) -> None:
    reviewed = tmp_path / "reviewed"
    save_plan(reviewed, environment)
    duplicate = tmp_path / "duplicate"
    shutil.copytree(reviewed, duplicate)
    reviewed_hash = family.digest((reviewed / "record.json").read_bytes())
    for index, owner in enumerate((reviewed, duplicate)):
        binding = tmp_path / f"binding-copy-{index}"
        record, archive = save_plan(binding, environment)
        run = tmp_path / f"copy-run-{index}"
        run.mkdir()
        (run / "isa.qpy").write_bytes(archive)
        arguments = (
            live_run,
            environment,
            record,
            archive,
            run,
            binding,
            family.digest((binding / "record.json").read_bytes()),
        )
        if index == 0:
            submit_reviewed(*arguments, reviewed_dir=owner, reviewed_sha256=reviewed_hash)
        else:
            with pytest.raises(live_run.LiveRunError, match="consumed"):
                submit_reviewed(*arguments, reviewed_dir=owner, reviewed_sha256=reviewed_hash)
    if len(environment.sent) != 1:
        raise AssertionError("copying the reviewed bytes must not duplicate their authorization")


def test_approval_registry_parent_is_synced_before_marker(
    environment: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    reviewed = tmp_path / "reviewed"
    record, archive = save_plan(reviewed, environment)
    run = tmp_path / "run"
    run.mkdir()
    synced: list[str] = []
    real_fsync = os.fsync

    def traced_fsync(descriptor: int) -> None:
        synced.append(os.readlink(f"/proc/self/fd/{descriptor}"))
        real_fsync(descriptor)

    monkeypatch.setattr(os, "fsync", traced_fsync)
    reviewed_hash = family.digest((reviewed / "record.json").read_bytes())
    submit_reviewed(live_run, environment, record, archive, run, reviewed, reviewed_hash)
    parent = str(tmp_path.resolve())
    marker = str(tmp_path / "approval-registry" / f"{reviewed_hash}.json")
    if parent not in synced or marker not in synced or synced.index(parent) > synced.index(marker):
        raise AssertionError("the registry parent must be synced before the approval marker")


def test_direct_submit_rejects_missing_reviewed_record(environment: Any, tmp_path: Path) -> None:
    approved = tmp_path / "approved"
    record, archive = save_plan(approved, environment)
    run = tmp_path / "run"
    run.mkdir()
    with pytest.raises(live_run.LiveRunError, match="reviewed actor record"):
        family.submit(
            live_run,
            environment,
            record,
            archive,
            run,
            approved,
            family.digest((approved / "record.json").read_bytes()),
        )
    if environment.sent:
        raise AssertionError("direct submission must fail before provider access")


def test_case_checker_compares_fresh_plan_to_reviewed_record(environment: Any, tmp_path: Path) -> None:
    reviewed = tmp_path / "reviewed"
    save_plan(reviewed, environment)
    fresh = tmp_path / "fresh"
    save_plan(fresh, environment)
    arguments = [
        "--validate-actor",
        str(fresh),
        "--reviewed-record",
        str(reviewed),
        "--reviewed-sha256",
        family.digest((reviewed / "record.json").read_bytes()),
    ]
    if qpu_cases.main(arguments) != 0:
        raise AssertionError("the same frozen case must pass independent-record comparison")
    arguments[-1] = "0" * 64
    if qpu_cases.main(arguments) == 0:
        raise AssertionError("a changed reviewed-record anchor must fail the case check")


@pytest.mark.parametrize("first_status", ["ERROR", "CANCELLED", "RUNNING", "unavailable", "missing"])
def test_partial_collection_retains_later_completed_job(
    environment: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, first_status: str
) -> None:
    specification = case()
    specification["allocations"] = specification["allocations"][:3]
    specification["allocations"][0]["shots"] = 5
    specification["max_total_execution_seconds"] = 10
    monkeypatch.setattr(Job, "job_id", lambda job: f"fixture-{job.shots}")
    record, archive, _ = family.plan(live_run, environment, specification)
    approved = tmp_path / "approved"
    approved.mkdir()
    (approved / "isa.qpy").write_bytes(archive)
    live_run.write_json(approved, record)
    run = tmp_path / "run"
    run.mkdir()
    (run / "isa.qpy").write_bytes(archive)
    submit_reviewed(
        live_run, environment, record, archive, run, approved, family.digest((approved / "record.json").read_bytes())
    )
    jobs = {job.job_id(): job for job in environment.sent}
    jobs["fixture-5"].status = lambda: first_status

    def retrieve(job_id: str) -> Any:
        if job_id == "fixture-5" and first_status == "unavailable":
            raise RuntimeError("retrieval unavailable")
        return jobs[job_id]

    environment.job = retrieve
    if first_status == "missing":
        record["submission"]["jobs"] = [
            entry for entry in record["submission"]["jobs"] if entry["job_id"] != "fixture-5"
        ]
        record["submission"]["planned_jobs"][0]["state"] = "planned"
        record["submission"]["complete"] = False
        live_run.write_json(run, record)
    output = family.collect(live_run, environment, run, family.digest((run / "record.json").read_bytes()))
    if output["all_allocations_retained"] or output["acquisition_status"] != "incomplete":
        raise AssertionError("partial acquisitions must withhold complete-case validity")
    if len(output["jobs"]["fixture-4"]["pubs"]) != 2 or len(output["allocations_without_results"]) != 1:
        raise AssertionError("later completed jobs must retain all available raw projections")
    replay = family.adjudicate(live_run, run, family.digest(Path(output["path"]).read_bytes()))
    if replay["all_allocations_retained"] or len(replay["jobs"]["fixture-4"]["pubs"]) != 2:
        raise AssertionError("adjudication must preserve partial acquisition status")


def test_actor_anchor_prevents_generic_dispatch_after_family_mutation(environment: Any, tmp_path: Path) -> None:
    run = tmp_path / "run"
    record, _archive = save_plan(run, environment)
    anchor = family.digest((run / "record.json").read_bytes())
    record["family_configuration"]["name"] = "altered-family"
    live_run.write_json(run, record)
    with pytest.raises(live_run.LiveRunError, match="anchor"):
        live_run.collect(environment, run, actor_record_sha256=anchor)
    with pytest.raises(adjudicate.AdjudicationError, match="SHA-256"):
        adjudicate.adjudicate(None, run, actor_collection_sha256="invalid")


@pytest.mark.parametrize("status", ["DONE", "ERROR"])
def test_sparse_actor_retention_uses_external_anchor_without_current_source_revalidation(
    environment: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, status: str
) -> None:
    import json
    from decimal import Decimal

    import reconcile_qpu_inventory as audit

    timestamps = {"running": "2026-10-29T00:00:00Z", "finished": "2026-10-29T00:00:01Z"}
    monkeypatch.setattr(
        Job,
        "metrics",
        lambda self: {"usage": {"status": "complete", "qpu_charge_time_seconds": 0.01}, "timestamps": timestamps},
    )
    monkeypatch.setattr(Job, "status", lambda self: status)
    monkeypatch.setattr(Job, "usage", lambda self, partial=False: 0.01)
    approved = tmp_path / "approved"
    record, archive = save_plan(approved, environment)
    run = tmp_path / "results/live/actor"
    run.mkdir(parents=True)
    (run / "isa.qpy").write_bytes(archive)
    submit_reviewed(
        live_run, environment, record, archive, run, approved, family.digest((approved / "record.json").read_bytes())
    )
    record_sha = family.digest((run / "record.json").read_bytes())
    collected = family.collect(live_run, environment, run, record_sha)
    anchor = tmp_path / "docs/evidence/readout-actor-acquisition-review/retention-anchors" / f"{record_sha}.json"
    anchor.parent.mkdir(parents=True)
    anchor.write_text(
        json.dumps(
            {
                "schema": "readout-actor-retention-anchor-v1",
                "run": "results/live/actor",
                "record_sha256": record_sha,
                "collection_sha256": family.digest(Path(collected["path"]).read_bytes()),
                "reviewed_record_sha256": record["reviewed_record_sha256"],
            }
        )
    )
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    monkeypatch.setattr(family, "verify_archive", lambda *_: pytest.fail("historical audit rechecks current source"))
    job = {
        "job_id": "fixture-job",
        "backend": "fixture-backend",
        "status": status,
        "pub_count": 8,
        "shots_per_pub": 4,
        "timestamps": timestamps,
    }
    if status == "DONE":
        result = audit.archived_row((job, run / "raw/fixture-job/index.json", Decimal("0.01")))
        if result["provenance"] != "registered_actor_collection" or result["submitted_pub_shots"] != 32:
            raise AssertionError("actor retention must bind the genuine full-register collection")
        metadata = run / "raw/fixture-job/result_metadata.json"
        original_metadata = metadata.read_bytes()
        metadata.write_text('{"changed": true}')
        with pytest.raises(ValueError, match="indexed raw artifact"):
            audit.actor_job_evidence(job, run, Decimal("0.01"))
        metadata.write_bytes(original_metadata)
        receipt = next((run / "raw/fixture-job").glob("receipt-*.json"))
        receipt.write_text("{}")
        with pytest.raises(ValueError):
            audit.archived_row((job, run / "raw/fixture-job/index.json", Decimal("0.01")))
    else:
        result = audit.failed_row(job, run, Decimal("0.01"))
        if result["provenance"] != "failed_actor_collection" or result["raw_data_files"] != 0:
            raise AssertionError("failed actor retention must preserve status without synthesizing shots")
