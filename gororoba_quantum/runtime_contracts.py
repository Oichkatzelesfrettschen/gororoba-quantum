"""Credential-free contracts for live capability, routing, batching, and Runtime helpers."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister, qpy, transpile
from qiskit.circuit.controlflow import IfElseOp
from qiskit.circuit.library import RZGate
from qiskit.primitives import StatevectorSampler
from qiskit.transpiler import Target
from qiskit_ibm_runtime.fake_provider import FakeFez, FakeManilaV2

import hybrid_shor  # noqa: F401 - proves the digest ignores module load order
import live_run as live_run_module
from experiments import Group, experiment_groups
from live_run import (
    BackendCapabilities,
    Choice,
    CircuitRequirements,
    LiveRunError,
    Snapshot,
    _compile,
    _distribution,
    _is_dynamic,
    _job_record,
    _ops,
    _physical,
    _pub_counts,
    build_admission_target,
    build_submission_plan,
    capability_violations,
    check_snapshot_matches_properties,
    choice_change_reasons,
    collect,
    compiled_violations,
    configure_sampler,
    discover_snapshots,
    experiment_digest,
    group_requirements,
    reconcile_attempted_jobs,
    select,
    submission_batches,
    submission_gaps,
    target_violations,
    write_archive,
    write_json,
)
from order_finding import factor_order_finding


class _ProbeBackend:
    """Named fake backend that can fail one snapshot stage."""

    def __init__(
        self,
        name: str,
        backend: FakeFez,
        failure_stage: str | None = None,
        max_circuits: int | None = 2,
    ):
        self.name = name
        self._backend = backend
        self._failure_stage = failure_stage
        self.max_circuits = max_circuits
        self.property_refreshes = 0

    def __getattr__(self, name: str) -> Any:
        return getattr(self._backend, name)

    def refresh(self) -> None:
        if self._failure_stage == "refresh":
            raise RuntimeError("fixture refresh failure")

    def properties(self, refresh: bool = False) -> Any:
        if self._failure_stage == "properties":
            raise RuntimeError("fixture properties failure")
        if refresh:
            self.property_refreshes += 1
        return self._backend.properties(refresh=refresh)

    def status(self) -> Any:
        if self._failure_stage == "status":
            raise RuntimeError("fixture status failure")
        return self._backend.status()

    def configuration(self) -> Any:
        if self._failure_stage == "capabilities":
            raise RuntimeError("fixture capability failure")
        configuration = copy.copy(self._backend.configuration())
        supported_features = list(getattr(configuration, "supported_features", []))
        if "dynamic_circuits" not in supported_features:
            supported_features.append("dynamic_circuits")
        configuration.supported_features = supported_features
        return configuration


class _ProbeService:
    """Minimal service surface for isolated discovery contracts."""

    def __init__(self, backends: list[_ProbeBackend], recovery_jobs: list[Any] | None = None):
        self._backends = {backend.name: backend for backend in backends}
        self.recovery_jobs = recovery_jobs or []
        self.recovery_queries: list[dict[str, Any]] = []

    def backends(self) -> list[_ProbeBackend]:
        return list(self._backends.values())

    def backend(self, name: str) -> _ProbeBackend:
        return self._backends[name]

    def usage(self) -> dict[str, Any]:
        return {"usage_limit_reached": False, "usage_remaining_seconds": None}

    def active_instance(self) -> str:
        return "fixture-instance"

    def instances(self) -> list[dict[str, str]]:
        return [{"crn": "fixture-instance", "plan": "fixture", "name": "fixture"}]

    def jobs(self, **query: Any) -> list[Any]:
        self.recovery_queries.append(query)
        return self.recovery_jobs


class _ProbeJob:
    def __init__(self, job_id: str):
        self._job_id = job_id

    def job_id(self) -> str:
        return self._job_id


class _ProbeSamplerOptions:
    def __init__(self, kind: str, tags: list[str], shots: int):
        self._value = {"kind": kind, "environment": {"job_tags": tags}, "default_shots": shots}

    def model_dump(self, mode: str) -> dict[str, Any]:
        if mode != "json":
            raise RuntimeError(f"unexpected options serialization mode {mode}")
        return copy.deepcopy(self._value)


class _ProbeSampler:
    def __init__(
        self,
        kind: str,
        tags: list[str],
        shots: int,
        before_run: Any,
        after_run: Any = None,
    ):
        self.options = _ProbeSamplerOptions(kind, tags, shots)
        self._before_run = before_run
        self._after_run = after_run

    def run(self, circuits: list[QuantumCircuit]) -> _ProbeJob:
        self._before_run(circuits)
        if self._after_run is not None:
            self._after_run()
        return _ProbeJob("fixture-job-id")


def _verify_dynamic_classification() -> None:
    final_measurement = QuantumCircuit(2, 2)
    final_measurement.h(0)
    final_measurement.measure([0, 1], [0, 1])
    if _is_dynamic(final_measurement):
        raise RuntimeError("terminal measurements classify as dynamic")

    later_work = QuantumCircuit(2, 1)
    later_work.measure(0, 0)
    later_work.x(1)
    if not _is_dynamic(later_work):
        raise RuntimeError("measurement followed by work on another qubit classifies as static")


def _verify_nested_operations() -> None:
    nested = QuantumCircuit(2, 1)
    nested.measure(0, 0)
    with nested.if_test((nested.clbits[0], 1)):
        nested.cz(0, 1)
    operations = _ops(nested)
    if operations != [("measure", (0,)), ("cz", (0, 1))]:
        raise RuntimeError(f"nested physical operations decode as {operations}")

    operation_names = ("cswap", "p", "measure", "reset")
    shor_operations = _ops(factor_order_finding(15, 2, 8))
    counts = {name: sum(operation == name for operation, _ in shor_operations) for name in operation_names}
    expected = {"cswap": 5, "p": 1, "measure": 2, "reset": 1}
    if counts != expected:
        raise RuntimeError(f"N=15 dynamic operation coefficients are {counts}")
    null_operations = _ops(factor_order_finding(15, 2, 8, identity=True))
    null_counts = {name: sum(operation == name for operation, _ in null_operations) for name in operation_names}
    expected_null = {"cswap": 0, "p": 1, "measure": 2, "reset": 1}
    if null_counts != expected_null:
        raise RuntimeError(f"N=15 identity-null operation coefficients are {null_counts}")


def _verify_result_register_order() -> None:
    qubits = QuantumRegister(2, "q")
    low = ClassicalRegister(1, "low")
    high = ClassicalRegister(1, "high")
    circuit = QuantumCircuit(qubits, low, high)
    circuit.x(qubits[0])
    circuit.measure(qubits[0], low[0])
    circuit.measure(qubits[1], high[0])
    pub = StatevectorSampler(seed=1).run([circuit], shots=8).result()[0]
    counts = _pub_counts(pub, circuit)
    if counts != {"01": 8}:
        raise RuntimeError(f"multi-register counts decode as {counts}")
    distribution = _distribution(counts, circuit.num_clbits)
    if distribution[1] != 1.0:
        raise RuntimeError(f"multi-register distribution places probability at {distribution.argmax()}")


def _verify_twirling_shot_contract() -> None:
    sampler = configure_sampler(FakeManilaV2(), "static", True, None, ["local-contract"], shots=4096)
    if sampler.options.twirling.num_randomizations != 32:
        raise RuntimeError(f"twirling uses {sampler.options.twirling.num_randomizations} randomizations")
    if sampler.options.twirling.shots_per_randomization != 128:
        raise RuntimeError(f"twirling uses {sampler.options.twirling.shots_per_randomization} shots per randomization")
    try:
        configure_sampler(FakeManilaV2(), "static", True, None, ["local-contract"], shots=16)
    except LiveRunError:
        pass
    else:
        raise RuntimeError("twirling accepted a shot count that Runtime 0.50 rounds upward")


def _verify_capability_admission() -> None:
    groups = {group.name: group for group in experiment_groups()}
    hybrid = group_requirements(groups["hybrid_shor_mod15"])
    expected_hybrid = {
        "qubits": 5,
        "classical_bits": 8,
        "static_circuits": 0,
        "dynamic_circuits": 2,
        "target_operations": ["if_else", "measure", "reset"],
        "control_flow": ["if_else"],
    }
    if hybrid.summary() != expected_hybrid:
        raise RuntimeError(f"hybrid-Shor capability requirements are {hybrid.summary()}")

    heron_like = BackendCapabilities(156, None, True, ("cz", "if_else", "measure", "reset"), ("if_else",))
    if capability_violations(hybrid, heron_like):
        raise RuntimeError("Heron-like capabilities reject the hybrid-Shor group")

    static_only = BackendCapabilities(156, None, False, ("cz", "measure"), ())
    static = group_requirements(groups["design_a"])
    if capability_violations(static, static_only):
        raise RuntimeError("static design A requires dynamic-circuit capabilities")
    hybrid_rejections = capability_violations(hybrid, static_only)
    if not any("dynamic-circuit" in reason for reason in hybrid_rejections):
        raise RuntimeError(f"static backend fails to reject dynamic hybrid Shor: {hybrid_rejections}")
    if not any("if_else" in reason and "reset" in reason for reason in hybrid_rejections):
        raise RuntimeError(f"missing dynamic operations are absent from rejection evidence: {hybrid_rejections}")

    one_circuit = BackendCapabilities(156, 1, False, ("cz", "measure"), ())
    if not any("backend limit" in reason for reason in capability_violations(static, one_circuit)):
        raise RuntimeError("backend circuit limit fails to reject a witness-plus-mirror group")

    exact_limit = BackendCapabilities(156, static.static_circuits, False, ("cz", "measure"), ())
    if capability_violations(static, exact_limit):
        raise RuntimeError("backend circuit limit rejects an exact-fit static group")

    narrow = BackendCapabilities(2, None, True, ("cz", "if_else", "measure", "reset"), ("if_else",))
    if not any("needs 5 qubits" in reason for reason in capability_violations(hybrid, narrow)):
        raise RuntimeError("backend quantum width fails to reject hybrid Shor")

    mixed = CircuitRequirements(2, 2, 1, 1, ("measure", "reset"), ())
    if not any("mixes static and dynamic" in reason for reason in capability_violations(mixed, heron_like)):
        raise RuntimeError("capability admission accepts a mixed static and dynamic result group")


def _verify_discovered_capabilities() -> None:
    backend = _ProbeBackend("viable", FakeFez(), max_circuits=2)
    snapshots, skipped, inventory = discover_snapshots(_ProbeService([backend]), None, None)
    if skipped or len(snapshots) != 1:
        raise RuntimeError(f"viable capability discovery returned snapshots={snapshots} skipped={skipped}")
    if backend.property_refreshes:
        raise RuntimeError("snapshot discovery refreshes properties again after backend.refresh()")
    capabilities = snapshots[0].capabilities
    summary = capabilities.summary()
    expected_control_flow = ["for_loop", "if_else", "switch_case"]
    if summary["num_qubits"] != 156 or summary["max_circuits"] != 2:
        raise RuntimeError(f"discovered backend dimensions are {summary}")
    if summary["dynamic_circuits"] is not True:
        raise RuntimeError(f"discovered dynamic-circuit support is {summary['dynamic_circuits']}")
    if not {"if_else", "measure", "reset"}.issubset(summary["operation_names"]):
        raise RuntimeError(f"discovered operations are {summary['operation_names']}")
    if summary["control_flow"] != expected_control_flow:
        raise RuntimeError(f"discovered control-flow operations are {summary['control_flow']}")
    if inventory["viable"]["capabilities"] != summary:
        raise RuntimeError("system inventory differs from discovered capabilities")

    hybrid = next(group for group in experiment_groups() if group.name == "hybrid_shor_mod15")
    violations = capability_violations(group_requirements(hybrid), capabilities)
    if violations:
        raise RuntimeError(f"discovered backend rejects hybrid Shor: {violations}")
    trace: dict[str, Any] = {}
    choice = select(hybrid, snapshots, 1, trace)
    if choice.snap is not snapshots[0] or len(choice.entries) != 2:
        raise RuntimeError("discovered backend fails hybrid-Shor routing admission")


def _fake_snapshot(backend: Any) -> Snapshot:
    properties = backend.properties()
    if properties is None:
        raise RuntimeError("FakeManilaV2 carries no properties")
    operations = tuple(sorted(backend.target.operation_names))
    capabilities = BackendCapabilities(
        backend.num_qubits,
        backend.max_circuits,
        True,
        operations,
        tuple(name for name in operations if name in {"for_loop", "if_else", "switch_case"}),
    )
    return Snapshot(
        backend=backend,
        properties=properties,
        name=backend.name,
        operational=True,
        status_msg="active",
        pending_jobs=0,
        calibration=properties.last_update_date.isoformat(),
        fetched_at="fixture",
        capabilities=capabilities,
    )


def _verify_target_and_bad_qubit_status() -> None:
    backend = FakeManilaV2()
    circuit = QuantumCircuit(2, 2)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure([0, 1], [0, 1])
    isa = transpile(circuit, backend=backend, optimization_level=1, seed_transpiler=7)
    if target_violations(isa, backend.target):
        raise RuntimeError(f"valid FakeManila ISA violates its Target: {target_violations(isa, backend.target)}")

    invalid = QuantumCircuit(backend.num_qubits)
    invalid.cx(0, 2)
    if target_violations(invalid, backend.target) != ["target lacks cx(0, 2)"]:
        raise RuntimeError(f"unsupported coupling status is {target_violations(invalid, backend.target)}")

    if "if_else" not in backend.target.operation_names:
        backend.target.add_instruction(IfElseOp, name="if_else")
    nested = QuantumCircuit(3, 1)
    nested.measure(0, 0)
    with nested.if_test((nested.clbits[0], 1)):
        nested.cx(0, 2)
    nested_violations = target_violations(nested, backend.target)
    if "target lacks cx(0, 2)" not in nested_violations:
        raise RuntimeError(f"unsupported nested coupling status is {nested_violations}")

    fixed_angle_target = Target(num_qubits=1)
    fixed_angle_target.add_instruction(RZGate(math.pi / 2), {(0,): None})
    unsupported_angle = QuantumCircuit(1)
    unsupported_angle.rz(math.pi / 4, 0)
    angle_violations = target_violations(unsupported_angle, fixed_angle_target)
    if angle_violations != ["target lacks rz(0,)"]:
        raise RuntimeError(f"unsupported fixed-angle status is {angle_violations}")

    snapshot = _fake_snapshot(backend)
    bad_qubit = _physical(isa)[0]
    snapshot.excluded_qubits[bad_qubit] = "fixture degradation"
    if f"qubit {bad_qubit}" not in compiled_violations(isa, snapshot):
        raise RuntimeError("fresh bad-qubit status fails to reject a routed circuit")

    filtered = _fake_snapshot(FakeFez())
    excluded_edge = next(iter(filtered.backend.target["cz"]))
    filtered.excluded_edges[excluded_edge] = "fixture degradation"
    filtered.admission_target = build_admission_target(filtered)
    if excluded_edge in filtered.admission_target["cz"]:
        raise RuntimeError(f"admission Target retains excluded CZ edge {excluded_edge}")
    reversed_edge = tuple(reversed(excluded_edge))
    if reversed_edge in filtered.admission_target["cz"]:
        raise RuntimeError(f"admission Target retains reverse of excluded CZ edge {excluded_edge}")
    routed_source = QuantumCircuit(2, 2)
    routed_source.h(0)
    routed_source.cz(0, 1)
    routed_source.measure([0, 1], [0, 1])
    for seed in range(4):
        routed = _compile(routed_source, filtered, seed)
        rejected = compiled_violations(routed, filtered)
        if rejected:
            raise RuntimeError(f"admission Target seed {seed} routed through excluded hardware: {rejected}")
        routed_edges = {qargs for operation, qargs in _ops(routed) if operation == "cz"}
        if excluded_edge in routed_edges or reversed_edge in routed_edges:
            raise RuntimeError(f"admission Target seed {seed} used excluded CZ edge {excluded_edge}")


def _verify_snapshot_and_fingerprint_coherence() -> None:
    backend = FakeFez()
    check_snapshot_matches_properties(backend.target, backend.properties(), backend.name)
    snapshot = _fake_snapshot(backend)
    hybrid = next(group for group in experiment_groups() if group.name == "hybrid_shor_mod15")
    choice = select(hybrid, [snapshot], 1, {})
    fresh = _fake_snapshot(FakeFez())
    reset_qargs = next(qargs for operation, qargs in _ops(choice.entries[0][1]) if operation == "reset")
    reset_properties = fresh.backend.target["reset"][reset_qargs]
    if reset_properties is None or reset_properties.duration is None:
        raise RuntimeError(f"FakeFez reset{reset_qargs} lacks a duration fixture")
    reset_properties.duration *= 2
    reasons = choice_change_reasons(choice, fresh)
    if "calibration values changed on compiled instructions" not in reasons:
        raise RuntimeError(f"reset Target-property drift is absent from revalidation reasons: {reasons}")

    timing_changed = _fake_snapshot(FakeFez())
    timing_changed.backend.target.granularity += 1
    reasons = choice_change_reasons(choice, timing_changed)
    if "calibration values changed on compiled instructions" not in reasons:
        raise RuntimeError(f"Target timing-constraint drift is absent from revalidation reasons: {reasons}")


def _source_entries(group: Group) -> list[tuple[str, QuantumCircuit, Any]]:
    entries = []
    for member in group.members:
        entries.append((member.name, member.circuit, member.ideal))
        if member.mirror:
            entries.append((member.name + "_mirror", member.circuit, member.ideal))
    return entries


def _verify_submission_batching() -> None:
    backend = FakeManilaV2()
    snapshot = _fake_snapshot(backend)
    groups = {group.name: group for group in experiment_groups()}

    def choice(name: str) -> Choice:
        group = groups[name]
        return Choice(group, snapshot, 7, [], [], [], 1.0, _source_entries(group))

    static_choices = [choice("design_a"), choice("design_c_8_1_4")]
    limited = submission_batches(static_choices, "static", 3)
    if [len(batch) for batch in limited] != [3, 2]:
        raise RuntimeError(f"group-preserving circuit-limit batches are {[len(batch) for batch in limited]}")
    expected_names = [
        [name for name, _, _ in static_choices[1].entries],
        [name for name, _, _ in static_choices[0].entries],
    ]
    actual_names = [[name for name, _, _ in batch] for batch in limited]
    if actual_names != expected_names:
        raise RuntimeError(f"group-preserving circuit-limit member order is {actual_names}")
    expected_owners = [static_choices[1], static_choices[0]]
    if any(
        owner is not expected_owner
        for expected_owner, batch in zip(expected_owners, limited, strict=True)
        for _, _, owner in batch
    ):
        raise RuntimeError("group-preserving circuit-limit batch loses its Choice owner")
    unlimited = submission_batches(static_choices, "static", None)
    if [len(batch) for batch in unlimited] != [5]:
        raise RuntimeError(f"unlimited backend unexpectedly splits batches: {[len(batch) for batch in unlimited]}")

    hybrid_choice = choice("hybrid_shor_mod15")
    dynamic = submission_batches([hybrid_choice], "dynamic", 2)
    if [[name for name, _, _ in batch] for batch in dynamic] != [[name for name, _, _ in hybrid_choice.entries]]:
        raise RuntimeError("exact-limit dynamic batch changes member order")
    try:
        submission_batches([hybrid_choice], "dynamic", 1)
    except LiveRunError:
        pass
    else:
        raise RuntimeError("over-limit dynamic group reaches submission")

    static_circuit = QuantumCircuit(1, 1)
    static_circuit.measure(0, 0)
    ideal = np.array([1.0, 0.0])

    def synthetic(names: list[str]) -> Choice:
        return Choice(
            groups["design_a"], snapshot, 7, [], [], [], 1.0, [(name, static_circuit, ideal) for name in names]
        )

    packed = submission_batches(
        [synthetic(["a0", "a1"]), synthetic(["b0", "b1"]), synthetic(["c0"]), synthetic(["d0"])],
        "static",
        3,
    )
    packed_names = [[name for name, _, _ in batch] for batch in packed]
    if packed_names != [["a0", "a1", "c0"], ["b0", "b1", "d0"]]:
        raise RuntimeError(f"first-fit-decreasing batches are {packed_names}")

    dynamic_circuit = QuantumCircuit(1, 1)
    dynamic_circuit.reset(0)
    dynamic_circuit.measure(0, 0)
    mixed_choice = synthetic(["static"])
    mixed_choice.entries.append(("dynamic", dynamic_circuit, ideal))
    try:
        submission_batches([mixed_choice], "static", 4)
    except LiveRunError:
        pass
    else:
        raise RuntimeError("mixed static and dynamic group reaches submission")


def _fixture_args(**overrides: Any) -> argparse.Namespace:
    values = {
        "backends": None,
        "groups": None,
        "max_pending": None,
        "seeds": 1,
        "started": "2026-10-10T00:00:00.000000+00:00",
        "shots": 4096,
        "twirl": False,
        "dd": None,
        "min_remaining_seconds": 0.0,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def _verify_schema_lifecycle() -> None:
    backend = _ProbeBackend("viable", FakeFez(), max_circuits=2)
    service = _ProbeService([backend])
    args = _fixture_args(groups=["hybrid_shor_mod15"])
    choices, record = live_run_module.plan(service, args)
    if record["schema_version"] != 3 or record["state"] != "planned":
        raise RuntimeError("live planning fails to create a schema-3 planned record")
    for field_name in ("system_inventory", "backends", "circuit_requirements", "selection_trace"):
        if field_name not in record:
            raise RuntimeError(f"schema-3 planning record lacks {field_name}")

    checkpoints: list[dict[str, Any]] = []
    run_observations: list[list[str]] = []

    def checkpoint() -> None:
        checkpoints.append(copy.deepcopy(record))

    def before_run(circuits: list[QuantumCircuit]) -> None:
        if not checkpoints:
            raise RuntimeError("mocked Sampler.run precedes every record checkpoint")
        submission = checkpoints[-1].get("submission", {})
        planned_jobs = submission.get("planned_jobs", [])
        if not planned_jobs or any("recovery_tags" not in entry for entry in planned_jobs):
            raise RuntimeError("mocked Sampler.run precedes the complete recovery ledger")
        if planned_jobs[0].get("state") != "attempted":
            raise RuntimeError("mocked Sampler.run precedes its attempted-state checkpoint")
        run_observations.append([circuit.name for circuit in circuits])

    original_configure_sampler = live_run_module.configure_sampler

    def fake_configure_sampler(
        backend: Any,
        kind: str,
        twirl: bool,
        dd: str | None,
        tags: list[str],
        shots: int = 4096,
    ) -> Any:
        del backend, twirl, dd
        return _ProbeSampler(kind, tags, shots, before_run)

    with tempfile.TemporaryDirectory(prefix="gororoba-schema3-") as directory:
        run_dir = Path(directory)
        live_run_module.configure_sampler = fake_configure_sampler
        try:
            live_run_module.submit(
                service,
                choices,
                args,
                record,
                lambda: write_archive(run_dir, choices),
                checkpoint,
            )
        finally:
            live_run_module.configure_sampler = original_configure_sampler

        if not record.get("revalidation"):
            raise RuntimeError("submission record lacks a fresh revalidation entry")
        if record["state"] != "submitted" or not record["submission"]["complete"]:
            raise RuntimeError("mocked submission fails to reach the submitted lifecycle state")
        if len(run_observations) != 1:
            raise RuntimeError(f"mocked Sampler received {len(run_observations)} calls")
        missing, _, _ = submission_gaps(record["submission"])
        if missing:
            raise RuntimeError(f"complete mocked submission reports missing jobs: {missing}")

        write_json(run_dir, record)
        round_trip_record = json.loads((run_dir / "record.json").read_text())
        qpy_bytes = (run_dir / "isa.qpy").read_bytes()
        with open(run_dir / "isa.qpy", "rb") as handle:
            round_trip_circuits = {circuit.name: circuit for circuit in qpy.load(handle)}
        if round_trip_record["schema_version"] != 3:
            raise RuntimeError("schema-3 JSON round trip changes the record version")
        if hashlib.sha256(qpy_bytes).hexdigest() != round_trip_record["submission"]["qpy_archive_sha256"]:
            raise RuntimeError("schema-3 QPY archive digest changes after its checkpoint")
        for planned_job in round_trip_record["submission"]["planned_jobs"]:
            for member in planned_job["members"]:
                if member not in round_trip_circuits:
                    raise RuntimeError(f"schema-3 QPY round trip loses {member}")

        incomplete_record = copy.deepcopy(round_trip_record)
        incomplete_record["state"] = "submission_started"
        incomplete_record["submission"]["jobs"] = []
        incomplete_record["submission"]["complete"] = False
        for planned_job in incomplete_record["submission"]["planned_jobs"]:
            planned_job["state"] = "planned"
        write_json(run_dir, incomplete_record)
        collect(service, run_dir)
        collection = json.loads((run_dir / "collect.json").read_text())
        if (
            collection[0]["members_without_recorded_job_id"]
            != incomplete_record["submission"]["planned_jobs"][0]["members"]
        ):
            raise RuntimeError(f"partial collection gap evidence is {collection[0]}")
        (run_dir / "isa.qpy").write_bytes(qpy_bytes + b"tampered")
        try:
            collect(service, run_dir)
        except LiveRunError as error:
            if "archive digest" not in str(error):
                raise RuntimeError(f"tampered QPY archive reports {error}") from error
        else:
            raise RuntimeError("collection accepts a QPY archive after byte tampering")

    recovery_submission = copy.deepcopy(record["submission"])
    recovery_submission["jobs"] = []
    recovery_submission["complete"] = False
    recovery_submission["planned_jobs"][0]["state"] = "attempted"
    recovery_service = _ProbeService([backend], [_ProbeJob("recovered-job-id")])
    if not reconcile_attempted_jobs(recovery_service, recovery_submission):
        raise RuntimeError("attempted-job reconciliation reports no record change")
    if recovery_submission["jobs"][0]["job_id"] != "recovered-job-id":
        raise RuntimeError("attempted-job reconciliation records the wrong job id")
    if recovery_service.recovery_queries[0]["job_tags"] != recovery_submission["planned_jobs"][0]["recovery_tags"]:
        raise RuntimeError("attempted-job reconciliation changes the recovery tags")
    if recovery_service.recovery_queries[0]["instance"] != "fixture-instance":
        raise RuntimeError("attempted-job reconciliation queries the wrong instance")
    if submission_gaps(recovery_submission)[0]:
        raise RuntimeError("recovered submission retains an unexplained ledger gap")

    for matches in ([], [_ProbeJob("first"), _ProbeJob("second")]):
        unresolved = copy.deepcopy(record["submission"])
        unresolved["jobs"] = []
        unresolved["complete"] = False
        unresolved["planned_jobs"][0]["state"] = "attempted"
        try:
            reconcile_attempted_jobs(_ProbeService([backend], matches), unresolved)
        except LiveRunError:
            pass
        else:
            raise RuntimeError(f"recovery accepted {len(matches)} matching jobs")

    static_backend = FakeManilaV2()
    static_snapshot = _fake_snapshot(static_backend)
    static_snapshot.capabilities = BackendCapabilities(
        static_snapshot.capabilities.num_qubits,
        3,
        static_snapshot.capabilities.dynamic_circuits,
        static_snapshot.capabilities.operation_names,
        static_snapshot.capabilities.control_flow,
    )
    groups = {group.name: group for group in experiment_groups()}
    static_choices = [
        Choice(groups[name], static_snapshot, 7, [], [], [], 1.0, _source_entries(groups[name]))
        for name in ("design_a", "design_c_8_1_4")
    ]
    partial, _ = build_submission_plan(static_choices, _fixture_args(), "0" * 64)
    if len(partial["planned_jobs"]) != 2:
        raise RuntimeError("finite backend fails to produce two planned jobs")
    first_plan = partial["planned_jobs"][0]
    first_plan["budget_before"] = {}
    first_plan["state"] = "accepted"
    partial["jobs"].append(_job_record(first_plan, "recorded-first-job"))
    missing_jobs, missing_backends, missing_members = submission_gaps(partial)
    second_plan = partial["planned_jobs"][1]
    if missing_backends != [second_plan["backend"]] or missing_members != second_plan["members"]:
        raise RuntimeError(f"partial submission gaps are backends={missing_backends} members={missing_members}")
    if len(missing_jobs) != 1 or missing_jobs[0]["batch_index"] != second_plan["batch_index"]:
        raise RuntimeError(f"partial submission batch evidence is {missing_jobs}")
    partial["complete"] = True
    try:
        submission_gaps(partial)
    except LiveRunError:
        pass
    else:
        raise RuntimeError("complete ledger accepts a missing submitted-job record")


def _verify_every_batch_revalidates() -> None:
    backend = _ProbeBackend("viable", FakeFez(), max_circuits=3)
    service = _ProbeService([backend])
    snapshots, _, _ = discover_snapshots(service, None, None)
    groups = {group.name: group for group in experiment_groups()}
    choices = [select(groups[name], snapshots, 1, {}) for name in ("design_a", "design_c_8_1_4")]
    args = _fixture_args()
    record: dict[str, Any] = {"shots": args.shots}
    checkpoints: list[dict[str, Any]] = []
    run_count = 0

    def checkpoint() -> None:
        checkpoints.append(copy.deepcopy(record))

    def after_run() -> None:
        nonlocal run_count
        run_count += 1
        backend._failure_stage = "status"

    original_configure_sampler = live_run_module.configure_sampler

    def fake_configure_sampler(
        backend: Any,
        kind: str,
        twirl: bool,
        dd: str | None,
        tags: list[str],
        shots: int = 4096,
    ) -> Any:
        del backend, twirl, dd
        return _ProbeSampler(kind, tags, shots, lambda unused_circuits: None, after_run)

    live_run_module.configure_sampler = fake_configure_sampler
    try:
        try:
            live_run_module.submit(service, choices, args, record, lambda: "0" * 64, checkpoint)
        except LiveRunError as error:
            if "status" not in str(error):
                raise RuntimeError(f"second-batch refresh reports {error}") from error
        else:
            raise RuntimeError("second batch submits after its status probe fails")
    finally:
        live_run_module.configure_sampler = original_configure_sampler
    if run_count != 1 or len(record["submission"]["jobs"]) != 1:
        raise RuntimeError("later-batch failure changes the number of accepted mocked jobs")
    missing_jobs, _, missing_members = submission_gaps(record["submission"])
    if len(missing_jobs) != 1 or len(missing_members) != 2:
        raise RuntimeError(f"later-batch failure loses unsent evidence: {missing_jobs}")


def _verify_live_reselection() -> None:
    backend = FakeFez()
    degraded = _fake_snapshot(backend)
    degraded.name = "degraded"
    degraded.excluded_qubits.update({qubit: "fixture degradation" for qubit in range(backend.num_qubits)})
    viable = _fake_snapshot(backend)
    viable.name = "viable"
    group = next(group for group in experiment_groups() if group.name == "design_a")
    trace: dict[str, Any] = {}
    choice = select(group, [degraded, viable], 1, trace)
    if choice.snap.name != "viable":
        raise RuntimeError(f"selector chose {choice.snap.name} instead of the viable system")
    if not any(entry.get("rejected") for entry in trace[group.name]["degraded"]):
        raise RuntimeError("degraded routed patch leaves no rejection evidence")

    fresh = _fake_snapshot(backend)
    fresh.name = "viable"
    used_qubit = _physical(choice.entries[0][1])[0]
    fresh.excluded_qubits[used_qubit] = "new fixture degradation"
    reasons = choice_change_reasons(choice, fresh)
    if not any(f"qubit {used_qubit}" in reason for reason in reasons):
        raise RuntimeError(f"pre-submit gate misses newly degraded qubit {used_qubit}: {reasons}")


def _verify_discovery_failure_isolation() -> None:
    group = next(group for group in experiment_groups() if group.name == "design_a")
    for failure_stage in ("refresh", "properties", "status", "capabilities"):
        fake_backend = FakeFez()
        broken_name = f"broken_{failure_stage}"
        service = _ProbeService(
            [
                _ProbeBackend(broken_name, fake_backend, failure_stage),
                _ProbeBackend("viable", fake_backend),
            ]
        )
        snapshots, skipped, inventory = discover_snapshots(service, None, None)
        if [snapshot.name for snapshot in snapshots] != ["viable"]:
            raise RuntimeError(f"{failure_stage} failure suppresses viable discovery")
        reason = skipped.get(broken_name, {}).get("reason", "")
        if failure_stage not in reason:
            raise RuntimeError(f"{failure_stage} probe reports {reason!r}")
        if inventory[broken_name]["eligibility"] != "probe_failed":
            raise RuntimeError(f"{failure_stage} probe lacks probe_failed inventory state")
        if inventory["viable"]["eligibility"] != "eligible":
            raise RuntimeError(f"{failure_stage} probe changes viable inventory state")
        trace: dict[str, Any] = {}
        selected = select(group, snapshots, 1, trace)
        if selected.snap.name != "viable":
            raise RuntimeError(f"{failure_stage} failure prevents viable selection")


def _verify() -> None:
    _verify_dynamic_classification()
    _verify_nested_operations()
    _verify_result_register_order()
    _verify_twirling_shot_contract()
    _verify_capability_admission()
    _verify_discovered_capabilities()
    _verify_target_and_bad_qubit_status()
    _verify_snapshot_and_fingerprint_coherence()
    _verify_submission_batching()
    _verify_schema_lifecycle()
    _verify_every_batch_revalidates()
    _verify_live_reselection()
    _verify_discovery_failure_isolation()
    first_digest = experiment_digest()
    second_digest = experiment_digest()
    if len(first_digest) != 64 or first_digest != second_digest:
        raise RuntimeError("experiment source manifest digest is unstable")
    print(
        "runtime contracts: discovery, capability admission, coherent snapshots, "
        "Target routing, batch revalidation, schema lifecycle, recovery, result order, and digest pass"
    )


if __name__ == "__main__":
    _verify()
