"""Credential-free contracts for matched diagnostic planning and invocation budgets.

FakeFez supplies calibration and routing fixtures. Every service constructor is
replaced by a failing sentinel, so the checks cannot discover saved credentials
or submit quantum work. Run the module directly; GOROROBA_WORKERS overrides the detected CPU count.
"""

from __future__ import annotations

import argparse
import contextlib
import copy
import dataclasses
import hashlib
import io
import json
import math
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

from qiskit.circuit import Delay, Measure
from qiskit.transpiler import InstructionProperties, Target
from qiskit_ibm_runtime.fake_provider import FakeFez

import diagnostic_experiments
import live_run
import local_compute
import native_preflight
import qpu_cases
import qpu_planning
from runtime_contracts import _fixture_args, _ProbeBackend, _ProbeSampler, _ProbeService


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _args(family: str, **overrides: Any) -> argparse.Namespace:
    args = _fixture_args(
        family=family,
        optimize=False,
        optimizer_candidates=1,
        replica_tiers=[1],
        max_replicas=1,
        isolated_reference=False,
        model_shots=512,
        max_total_execution_seconds=120.0,
        reserve_seconds=10.0,
    )
    vars(args).update(qpu_planning.settings(args))
    vars(args).update(overrides)
    return args


def _fixture() -> tuple[_ProbeService, live_run.Snapshot]:
    backend = _ProbeBackend("planning_fixture", FakeFez())
    service = _ProbeService([backend])
    snapshot = live_run.take_snapshot(cast(Any, service), backend.name)
    return service, snapshot


def _verify_family_layouts(snapshot: live_run.Snapshot) -> tuple[list[live_run.Choice], dict[str, Any]]:
    args = _args("folded-qpe")
    trace: dict[str, Any] = {}
    candidates = qpu_planning.family_candidates(live_run, [snapshot], args, trace)
    _require(bool(candidates), f"FakeFez rejects every folded family: {trace}")
    choices, configuration = candidates[0]
    _require(len(choices) == 2, "folded family must retain its static and dynamic groups")
    by_kind = {
        "dynamic" if live_run._is_dynamic(choice.group.members[0].circuit) else "static": choice for choice in choices
    }
    _require(set(by_kind) == {"static", "dynamic"}, "folded family lost one execution kind")
    static, dynamic = by_kind["static"], by_kind["dynamic"]
    shared = configuration["shared_initial_layout"]
    _require(static.layout[:5] == dynamic.layout == shared, "folded groups changed the shared physical mapping")
    _require(static.layout[5] == configuration["extra_control"], "coherent extra control lost its physical mapping")
    _require(configuration["extra_control"] not in shared, "coherent control aliases the shared work register")
    for choice in choices:
        _require(len(choice.replicas) == 1, "fixed-layout ladder was silently re-embedded into extra replicas")
        _require(
            all(source == target for source, target in choice.replicas[0].mapping.items()),
            "fixed-layout ladder changed its calibrated physical qubits during packing",
        )
        for member, isa in zip(choice.group.members, choice.isas, strict=True):
            initial_layout = isa.layout.initial_index_layout(filter_ancillas=True)
            _require(initial_layout[:5] == shared, f"{member.name}: source controls use a different work register")
            _require(
                not live_run.compiled_violations(isa, snapshot), f"{member.name}: compiled ISA violates the Target"
            )
    target = snapshot.backend.target
    granularity = max(1, int(target.granularity))
    delay_members = [member for member in dynamic.group.members if member.name.startswith("qpe_delay_")]
    _require(len(delay_members) == 4, "folded family omitted a delay eigenstate control")
    for member in delay_members:
        label = member.name[-1]
        archived_isa = dynamic.isas[int(label)]
        first_writer = next(qubits[0] for name, qubits in live_run._ops(archived_isa) if name == "measure")
        _require(
            configuration["replaced_measurement_qubits"][label] == first_writer,
            f"{member.name}: calibration records the initial control instead of its routed measurement writer",
        )
        duration_seconds = target["measure"][(first_writer,)].duration
        expected_delay = granularity * math.ceil(duration_seconds / target.dt / granularity)
        _require(
            configuration["measurement_delay_dt"][label] == expected_delay,
            f"{member.name}: recorded delay uses another physical qubit's calibration",
        )
        delays = [
            instruction.operation.duration
            for instruction in member.circuit.data
            if instruction.operation.name == "delay"
        ]
        _require(delays == [expected_delay], f"{member.name}: circuit delay differs from its calibrated record")
        _require(member.circuit.num_clbits == 1, f"{member.name}: delay arm presents an unmeasured label bit")
    pubs = live_run.execution_pubs(choices)
    _require(len(pubs) == 16, "four controls for four eigenstates did not produce sixteen isolated PUBs")
    for pub in pubs:
        observed_kind = "dynamic" if live_run._is_dynamic(pub.circuit) else "static"
        _require(pub.kind == observed_kind, f"{pub.name}: declared job kind differs from its circuit")
    batches = {kind: live_run.submission_batches(choices, kind, args.shots) for kind in ("dynamic", "static")}
    _require([len(batch) for batch in batches["dynamic"]] == [12], "dynamic ladder controls changed their job boundary")
    _require([len(batch) for batch in batches["static"]] == [4], "coherent controls changed their static job boundary")

    n21_trace: dict[str, Any] = {}
    n21_candidates = qpu_planning.family_candidates(live_run, [snapshot], _args("n21-feedback"), n21_trace)
    _require(bool(n21_candidates), f"FakeFez rejects every N=21 family: {n21_trace}")
    n21_choices, _configuration = n21_candidates[0]
    _require(len(n21_choices) == 1, "N=21 feedback comparison split its matched group")
    n21_choice = n21_choices[0]
    _require(len(n21_choice.isas) == 2, "N=21 feedback comparison lost an arm")
    for isa in n21_choice.isas:
        _require(
            isa.layout.initial_index_layout(filter_ancillas=True) == n21_choice.layout,
            "N=21 feedback controls use different initial physical layouts",
        )
    _require(
        {pub.kind for pub in live_run.execution_pubs(n21_choices)} == {"dynamic"},
        "N=21 feedback controls crossed execution kinds",
    )
    orbit_trace: dict[str, Any] = {}
    orbit_candidates = qpu_planning.family_candidates(live_run, [snapshot], _args("n21-orbit-feedback"), orbit_trace)
    _require(bool(orbit_candidates), f"FakeFez rejects every N=21 orbit family: {orbit_trace}")
    (orbit_choice,) = orbit_candidates[0][0]
    _require(len(orbit_choice.isas) == 2, "N=21 orbit comparison lost an arm")
    orbit_cz = max(isa.count_ops().get("cz", 0) for isa in orbit_choice.isas)
    full_cz = max(isa.count_ops().get("cz", 0) for isa in n21_choice.isas)
    _require(orbit_cz * 10 < full_cz, f"orbit multipliers use {orbit_cz} CZ against {full_cz} for the full register")
    _require(
        {pub.kind for pub in live_run.execution_pubs(orbit_candidates[0][0])} == {"dynamic"},
        "N=21 orbit controls crossed execution kinds",
    )
    rca_trace: dict[str, Any] = {}
    rca_candidates = qpu_planning.family_candidates(live_run, [snapshot], _args("n21-orbit-rca"), rca_trace)
    _require(bool(rca_candidates), f"FakeFez rejects every N=21 window family: {rca_trace}")
    (rca_choice,), rca_configuration = rca_candidates[0]
    _require(
        rca_configuration["window_delay_dt"] > 0 and rca_configuration["echo_half_dt"] > 0,
        f"window durations missing from the family configuration: {rca_configuration}",
    )
    _require(len(rca_choice.isas) == 8, "N=21 window family lost an arm")
    arms = dict(zip((member.name for member in rca_choice.group.members), rca_choice.isas, strict=True))

    def ops(name: str) -> dict[str, int]:
        return dict(arms[name].count_ops())

    # The interventions preserve the ideal law, so only these structural
    # checks show they survived transpilation, in both arms of every pair.
    for arm in ("feedback", "no_feedback"):
        nominal = ops(f"n21_orbit_nominal_{arm}")
        extra = ops(f"n21_orbit_extra_readout_{arm}")
        _require(extra["measure"] == nominal["measure"] + 1, f"extra readout was removed from the {arm} arm")
        _require(ops(f"n21_orbit_window_delay_{arm}").get("delay", 0) >= 1, f"window delay left the {arm} arm")
        echo_isa = arms[f"n21_orbit_window_echo_{arm}"]
        wires: dict[int, list[str]] = {}
        for instruction in echo_isa.data:
            for qubit in instruction.qubits:
                wires.setdefault(echo_isa.find_bit(qubit).index, []).append(instruction.operation.name)
        echoed = [
            wire
            for wire, names in wires.items()
            if ["barrier", "delay", "x", "delay", "x", "barrier"]
            in [names[index : index + 6] for index in range(len(names))]
        ]
        _require(len(echoed) == 2, f"the {arm} echo lost its delay-X-delay-X sequence on the work wires: {echoed}")
    return choices, configuration


class _TargetOverride:
    """Backend view that serves a replacement Target and delegates every other attribute."""

    def __init__(self, backend: Any, target: Target) -> None:
        self._backend = backend
        self.target = target

    def __getattr__(self, name: str) -> Any:
        return getattr(self._backend, name)


def _verify_window_control_durations(snapshot: live_run.Snapshot) -> None:
    """The N=21 window arms take the routed control's measure and reset, not the slowest qubit's.

    The fixture lengthens measure and reset on an excluded qubit, which no
    placement can route the control onto, so the backend-wide maximum exceeds
    the routed control's durations.
    """
    slow = 113
    _require(slow in snapshot.excluded_qubits, "the slow fixture qubit must stay excluded from placement")
    uniform = qpu_planning.window_durations(live_run, snapshot)
    target = copy.deepcopy(snapshot.backend.target)
    for name in ("measure", "reset"):
        properties = target[name][(slow,)]
        target.update_instruction_properties(
            name, (slow,), InstructionProperties(duration=3 * properties.duration, error=properties.error)
        )
    heterogeneous = dataclasses.replace(
        snapshot, backend=_TargetOverride(snapshot.backend, target), admission_target=None
    )
    bound = qpu_planning.window_durations(live_run, heterogeneous)
    _require(
        bound[0] > uniform[0] and bound[1] > uniform[1],
        f"the slow qubit must raise the backend-wide window bound: {bound} against {uniform}",
    )
    _require(
        qpu_planning.window_durations(live_run, heterogeneous, [slow])[:2] == bound[:2],
        "the slow qubit's own durations must set the bound",
    )
    trace: dict[str, Any] = {}
    candidates = qpu_planning.family_candidates(live_run, [heterogeneous], _args("n21-orbit-rca"), trace)
    _require(bool(candidates), f"the heterogeneous Target rejects every N=21 window family: {trace}")
    (choice,), configuration = candidates[0]
    sites = qpu_planning.control_sites(live_run, choice.isas)
    controls = qpu_planning.window_controls(sites)
    _require(bool(controls) and slow not in controls, f"the control routed onto {controls}")
    expected = qpu_planning.window_durations(live_run, heterogeneous, controls)
    _require(expected == uniform, f"the control's durations {expected} differ from the uniform {uniform}")
    _require(
        (configuration["window_delay_dt"], configuration["echo_half_dt"]) == uniform[:2],
        f"window configuration {configuration} kept the backend-wide bound {bound}",
    )
    arms = dict(zip((member.name for member in choice.group.members), choice.isas, strict=True))
    for arm in ("feedback", "no_feedback"):
        delays = [
            int(instruction.operation.duration)
            for instruction in arms[f"n21_orbit_window_delay_{arm}"].data
            if instruction.operation.name == "delay"
        ]
        _require(uniform[0] in delays, f"the {arm} window delay {delays} differs from the control readout {uniform[0]}")
    # Routing moves the control between the rounds, so the terminal readout
    # sits on another qubit; slowing that qubit leaves the windows unchanged.
    terminal = sorted({arm[-1][1] for arm in sites} - {arm[0][1] for arm in sites})
    _require(bool(terminal), f"the routed fixture keeps its terminal readout on the window site: {sites}")
    readout = copy.deepcopy(snapshot.backend.target)
    for name in ("measure", "reset"):
        for qubit in terminal:
            properties = readout[name][(qubit,)]
            readout.update_instruction_properties(
                name, (qubit,), InstructionProperties(duration=3 * properties.duration, error=properties.error)
            )
    slow_terminal = dataclasses.replace(
        snapshot, backend=_TargetOverride(snapshot.backend, readout), admission_target=None
    )
    relocated = copy.copy(choice)
    relocated.snap = slow_terminal
    terminal_bound = qpu_planning.window_durations(live_run, slow_terminal)
    _require(terminal_bound[:2] != uniform[:2], "the slow terminal readout must raise the backend-wide bound")
    resized, window = qpu_planning._control_windows(live_run, relocated, terminal_bound)
    _require(
        (window["window_delay_dt"], window["echo_half_dt"]) == uniform[:2],
        f"the terminal readout on {terminal} set the windows {window} instead of {uniform[:2]}",
    )
    _require(qpu_planning.control_sites(live_run, resized.isas) == sites, "the resized arms moved their measure sites")


def _verify_heterogeneous_measurement_duration() -> None:
    target = Target(num_qubits=2, dt=1e-9, granularity=16)
    target.add_instruction(
        Measure(),
        {(0,): InstructionProperties(duration=95e-9), (1,): InstructionProperties(duration=317e-9)},
    )
    snapshot = SimpleNamespace(backend=SimpleNamespace(target=target))
    _require(qpu_planning.measurement_delay(live_run, snapshot, 0) == 96, "initial-site duration rounding changed")
    _require(
        qpu_planning.measurement_delay(live_run, snapshot, 1) == 320,
        "routed measurement writer lost its distinct duration or device granularity",
    )


def _verify_mixed_noise_batch(choices: list[live_run.Choice]) -> None:
    dynamic = next(choice for choice in choices if choice.group.name.endswith("dynamic"))
    entries = {entry.name: entry for entry in dynamic.entries}
    archived, delayed = entries["qpe_archived_s2"], entries["qpe_delay_s2"]
    snapshot = dynamic.snap
    simulator = live_run.noise_simulator(snapshot.name, snapshot.backend.target, snapshot.properties)
    _require(
        simulator.options.method == "density_matrix", "noise simulation silently restored automatic kernel selection"
    )
    shots = 2048
    isolated = live_run.simulate_entries(simulator, [delayed], shots, 20261011)[delayed.name][0]
    mixed = live_run.simulate_entries(simulator, [archived, delayed], shots, 20261012)[delayed.name][0]
    reversed_batch = live_run.simulate_entries(simulator, [delayed, archived], shots, 20261013)[delayed.name][0]
    # A union bound gives all three Bernoulli estimates error at most radius/2
    # with failure probability 1e-6, covering both differences by the triangle
    # inequality without assuming independent streams across simulator calls.
    radius = math.sqrt(2 * math.log(6 / 1e-6) / shots)
    for label, distribution in (("mixed", mixed), ("reversed", reversed_batch)):
        _require(
            abs(float(distribution[1] - isolated[1])) <= radius,
            f"{label} noisy batch changes the delay arm beyond shot noise: {distribution} vs {isolated}",
        )


def _verify_budget_reservation(choices: list[live_run.Choice]) -> None:
    args = _args("folded-qpe")
    usage = {"usage_limit_reached": False, "usage_remaining_seconds": 130.0}
    admitted = qpu_planning.budget_plan(live_run, choices, args, usage)
    _require(admitted["admitted"], f"exact ceiling-plus-reserve boundary was rejected: {admitted}")
    _require(len(admitted["jobs"]) == 2, "reservation omitted an unsent static or dynamic job")
    _require(admitted["combined_ceiling_seconds"] == 120.0, "reservation counts fewer than both job ceilings")
    _require(admitted["reserve_seconds"] == 10.0, "reservation lost the requested reserve")
    cap_shortfall = qpu_planning.budget_plan(
        live_run, choices, _args("folded-qpe", max_total_execution_seconds=119.0), usage
    )
    _require(not cap_shortfall["admitted"], "reservation accepted a ceiling above the combined invocation cap")
    reserve_shortfall = qpu_planning.budget_plan(live_run, choices, args, {**usage, "usage_remaining_seconds": 129.0})
    _require(not reserve_shortfall["admitted"], "reservation spent the protected reserve by one second")
    limit_reached = qpu_planning.budget_plan(live_run, choices, args, {**usage, "usage_limit_reached": True})
    _require(not limit_reached["admitted"], "reservation ignored the service usage-limit flag")


def _verify_optimizer(
    snapshot: live_run.Snapshot, choices: list[live_run.Choice], configuration: dict[str, Any]
) -> dict[str, Any]:
    args = _args("folded-qpe", optimize=True, shot_tiers=[512, 2048, 8192])
    usage = {"usage_limit_reached": False, "usage_remaining_seconds": 130.0}
    with patch.object(qpu_planning, "family_candidates", return_value=[(choices, configuration)]):
        selected, metadata = qpu_planning.prepare(live_run, [snapshot], args, usage, {})
    _require(selected == choices, "optimizer lost the selected physical circuit family")
    _require(args.shots == 8192, f"optimizer selected {args.shots} shots despite the declared precision")
    optimization = metadata["optimization"]
    selected_rows = [row for row in optimization["candidates"] if row["name"] == optimization["selected"]]
    _require(len(selected_rows) == 1 and selected_rows[0]["feasible"], "optimizer selected an infeasible candidate")
    rejected_shots = {int(row["proxy_metadata"]["shots"]) for row in optimization["candidates"] if not row["feasible"]}
    _require(rejected_shots == {512, 2048}, "optimizer failed to reject underpowered precision tiers")
    _require(
        selected_rows[0]["total_execution_ceiling_seconds"] == 120.0,
        "optimizer omitted the coherent or dynamic job ceiling",
    )
    _require(len(metadata["observable_contracts"]) == 12, "optimizer lost a preregistered folded contrast")
    return metadata


def _verify_approval_mutations(choices: list[live_run.Choice], metadata: dict[str, Any]) -> None:
    record = {
        "state": "planned",
        "shots": 8192,
        "policy": {"design": metadata["optimizer_settings"], "local_compute": local_compute.settings()},
        "groups": [],
        **metadata,
    }
    record["execution_contract"] = qpu_planning.execution_contract(choices, record)
    with tempfile.TemporaryDirectory(prefix="gororoba-planning-approval-") as directory:
        approved = Path(directory)
        live_run.write_archive(approved, choices)
        live_run.write_json(approved, record)
        qpy_digest = hashlib.sha256((approved / "isa.qpy").read_bytes()).hexdigest()
        _require(
            not live_run.approved_record_mismatches(approved, record, qpy_digest),
            "unchanged diagnostic configuration failed approval comparison",
        )
        changed_delay = copy.deepcopy(record)
        changed_delay["family_configuration"]["measurement_delay_dt"]["0"] += 1
        _require(
            "family_configuration differs" in live_run.approved_record_mismatches(approved, changed_delay, qpy_digest),
            "approval accepted a changed calibrated measurement delay",
        )
        changed_endpoint = copy.deepcopy(record)
        changed_endpoint["observable_contracts"][0]["precision_half_width"] *= 2
        _require(
            "observable_contracts differs"
            in live_run.approved_record_mismatches(approved, changed_endpoint, qpy_digest),
            "approval accepted a relaxed scientific precision contract",
        )
        changed_tiers = copy.deepcopy(record)
        changed_tiers["policy"]["design"]["shot_tiers"] = [8192, 16384]
        _require(
            "policy differs" in live_run.approved_record_mismatches(approved, changed_tiers, qpy_digest),
            "approval accepted a changed optimizer search policy",
        )
        for field, value in (
            ("objective", "precision_at_budget"),
            ("cost_scenarios", [{"name": "stress", "job_overhead_seconds": 4.6, "classical_latency_us": 60.0}]),
        ):
            changed_policy = copy.deepcopy(record)
            changed_policy["policy"]["design"][field] = value
            _require(
                "policy differs" in live_run.approved_record_mismatches(approved, changed_policy, qpy_digest),
                f"approval accepted changed {field}",
            )
        changed_compute = copy.deepcopy(record)
        changed_compute["policy"]["local_compute"]["threads"] += 1
        _require(
            "policy differs" in live_run.approved_record_mismatches(approved, changed_compute, qpy_digest),
            "approval accepted changed local simulation policy",
        )
        changed_repetition = copy.deepcopy(record)
        changed_repetition["execution_contract"]["backends"][0]["repetition_delay_seconds"] += 1e-6
        _require(
            "execution_contract differs"
            in live_run.approved_record_mismatches(approved, changed_repetition, qpy_digest),
            "approval accepted a changed backend repetition delay",
        )
        changed_costs = copy.deepcopy(record)
        selected = next(
            candidate
            for candidate in changed_costs["optimization"]["candidates"]
            if candidate["name"] == changed_costs["optimization"]["selected"]
        )
        selected["jobs"][0]["pubs"][0]["scheduled_seconds"] += 1e-6
        changed_costs["execution_contract"] = qpu_planning.execution_contract(choices, changed_costs)
        _require(
            "execution_contract differs" in live_run.approved_record_mismatches(approved, changed_costs, qpy_digest),
            "approval accepted changed selected circuit duration inputs",
        )


def _verify_cli_approval_boundary() -> None:
    stderr = io.StringIO()
    with redirect_stderr(stderr):
        try:
            live_run.main(
                [
                    "--submit",
                    "--out",
                    "/tmp/planning-contract-output-unused",
                    "--approved-record",
                    "/tmp/planning-contract-approved-unused",
                    "--approved-record-sha256",
                    "0" * 64,
                    "--max-execution-seconds",
                    "60",
                ]
            )
        except SystemExit as error:
            _require(error.code == 2, f"missing combined ceiling produced CLI status {error.code}")
        else:
            raise RuntimeError("submission CLI accepted a missing combined invocation ceiling")
    _require("--max-total-execution-seconds" in stderr.getvalue(), "CLI rejection did not identify the combined cap")


def _verify_precision_defaults() -> None:
    """An omitted --precision resolves to the family default; a given one reaches the coherence contracts."""
    from coherence_window import COHERENCE_PRECISION

    class _Parsed(Exception):
        pass

    resolved: list[float] = []

    def capture(args: Any) -> Any:
        resolved.append(args.precision)
        raise _Parsed

    ceilings = ["--max-execution-seconds", "9", "--max-total-execution-seconds", "18"]
    coherence = ["--family", "coherence-window", "--patch-qubits", "142,136,143,144,123,145"]
    cases = (
        (coherence, COHERENCE_PRECISION),
        ([*coherence, "--precision", "0.2"], 0.2),
        (["--family", "coherence-window"], COHERENCE_PRECISION),
        (["--family", "folded-qpe"], 0.08),
    )
    with patch.object(live_run.local_compute, "settings", side_effect=capture):
        for arguments, expected in cases:
            try:
                live_run.main([*ceilings, *arguments])
            except _Parsed:
                pass
            _require(bool(resolved) and resolved[-1] == expected, f"{arguments}: --precision resolved to {resolved}")
            resolved.clear()
    contracts = diagnostic_experiments.family_contracts("coherence-window", 0.2, 0.05, 0.8)
    _require(all(c.precision_half_width == 0.2 for c in contracts), "coherence contracts ignore --precision")


def _verify_compute_boundary() -> None:
    with tempfile.TemporaryDirectory(prefix="gororoba-compute-boundary-") as directory:
        with (
            patch.object(local_compute.AerSimulator, "available_devices", return_value=("CPU",)),
            redirect_stderr(io.StringIO()),
            redirect_stdout(io.StringIO()),
        ):
            status = live_run.main(["--local-compute", "gpu", "--out", directory])
        _require(status == 1, "gpu policy without an Aer GPU passed service construction boundary")
        with (
            patch.object(local_compute.aer_identity, "identity", side_effect=ValueError("native binary replaced")),
            redirect_stderr(io.StringIO()),
            redirect_stdout(io.StringIO()),
        ):
            status = live_run.main(["--local-compute", "cpu", "--out", directory])
        _require(status == 1, "failed binary provenance escaped the diagnostic-record boundary")
        records = [json.loads(path.read_text()) for path in Path(directory).glob("*/record.json")]
        _require(len(records) == 2, "compute failures lost their diagnostic records")
        _require(all(record["state"] == "local_compute_unavailable" for record in records), "wrong failure state")
        _require(all("submission" not in record for record in records), "capability failure reached submission")
        _require(
            any(record["reason"] == "native binary replaced" for record in records), "binary failure lost its cause"
        )
    parsed = live_run._cost_scenario("stress:4.6:60")
    _require(parsed == {"name": "stress", "job_overhead_seconds": 4.6, "classical_latency_us": 60.0}, "scenario parse")
    for malformed in ("missing", "stress:nan:1", "stress:1:-2", ":1:2", "nominal:1:2", "_stress:1:2", "-stress:1:2"):
        try:
            live_run._cost_scenario(malformed)
        except argparse.ArgumentTypeError:
            pass
        else:
            raise RuntimeError(f"malformed cost scenario passes: {malformed}")


def _verify_usage_accounting() -> None:
    record = {
        "submission": {"complete": True, "jobs": [{"job_id": "dynamic"}, {"job_id": "static"}]},
        "optimization": {
            "selected": "selected_fixture",
            "candidates": [{"name": "selected_fixture", "estimated_charge_seconds": 8.0}],
        },
    }
    jobs = {
        job_id: {"usage": {"usage_status": "final", "job_status": "DONE", "qpu_charge_time_seconds": charge}}
        for job_id, charge in (("dynamic", "3"), ("static", "4"))
    }
    completed = live_run.invocation_usage(record, jobs)
    _require(completed["total_charge_seconds"] == "7", "successful invocation lost final billed charge")
    _require(completed["charge_prediction_residual_seconds"] == -1.0, "successful cost residual changed")
    for status in ("ERROR", "CANCELLED"):
        failed = copy.deepcopy(jobs)
        failed["static"]["usage"]["job_status"] = status
        usage = live_run.invocation_usage(record, failed)
        _require(usage["charge_complete"], f"{status}: terminal final billing was withheld")
        _require(usage["total_charge_seconds"] == "7", f"{status}: terminal job charge disappeared")
        _require(not usage["workload_complete"], f"{status}: failed workload was declared complete")
        _require(
            usage["charge_prediction_residual_seconds"] is None,
            f"{status}: incomplete execution was compared with a full-workload charge prediction",
        )
        _require(bool(usage["charge_prediction_residual_withheld"]), f"{status}: withheld residual lacks a reason")
    pending = copy.deepcopy(jobs)
    pending["static"]["usage"] = {"usage_status": "pending", "job_status": "RUNNING"}
    usage = live_run.invocation_usage(record, pending)
    _require(usage["known_final_charge_seconds"] == "3", "partial accounting lost known final charge")
    _require(usage["total_charge_seconds"] is None, "partial charge was presented as the invocation total")
    _require(usage["charge_prediction_residual_seconds"] is None, "partial accounting produced a cost residual")


def _verify_infeasible_archive(
    service: _ProbeService, choices: list[live_run.Choice], configuration: dict[str, Any]
) -> None:
    with (
        tempfile.TemporaryDirectory(prefix="gororoba-planning-infeasible-") as directory,
        patch.object(qpu_planning, "family_candidates", return_value=[(choices, configuration)]),
        patch.object(live_run, "QiskitRuntimeService", return_value=service),
        redirect_stdout(io.StringIO()),
    ):
        status = live_run.main(
            [
                "--family",
                "folded-qpe",
                "--optimize",
                "--shot-tiers",
                "64",
                "--model-shots",
                "64",
                "--precision",
                "0.001",
                "--max-replicas",
                "1",
                "--no-isolated-reference",
                "--max-execution-seconds",
                "60",
                "--max-total-execution-seconds",
                "120",
                "--out",
                directory,
            ]
        )
        _require(status == 0, f"diagnostic dry run failed to retain its infeasibility evidence: {status}")
        records = list(Path(directory).glob("*/record.json"))
        _require(len(records) == 1, "infeasible dry run did not write exactly one audit record")
        record = json.loads(records[0].read_text())
        _require(record["state"] == "design_infeasible", f"infeasible design recorded state {record['state']}")
        _require(record["optimization"]["selected"] is None, "infeasible dry run selected a shot tier")
        _require(bool(record["optimization"]["candidates"]), "infeasible dry run omitted its rejected candidates")
        _require((records[0].parent / "isa.qpy").is_file(), "infeasible dry run omitted its concrete circuit archive")
        _require("submission" not in record, "infeasible dry run contains a submission ledger")


def _verify_unrouted_family_diagnostics(service: _ProbeService) -> None:
    trace_fixture = {
        "family_rejections": [
            {
                "backend": "planning_fixture",
                "reason": "joint placement exhausted; groups={lane0: 21, lane1: 32}",
            }
        ],
        "algebra_backends": {
            "planning_fixture": {
                "lane0": {"planning_fixture": [{"seed": 20261010, "layout": [1, 2], "score": 0.91}]},
                "lane1": {
                    "planning_fixture": [
                        {"seed": 20261010, "layout": [3, 4], "rejected": ["physical buffer conflict"]},
                        {"seed": 20261011, "compile_error": "fixture crn:private:instance"},
                    ]
                },
            }
        },
    }
    supplied_traces: list[dict[str, Any]] = []

    def reject_family(
        runtime: Any, snapshots: list[Any], args: Any, trace: dict[str, Any]
    ) -> list[tuple[list[Any], dict[str, Any]]]:
        del runtime, snapshots, args
        trace.update(copy.deepcopy(trace_fixture))
        supplied_traces.append(trace)
        return []

    stderr = io.StringIO()
    with (
        tempfile.TemporaryDirectory(prefix="gororoba-planning-unrouted-") as directory,
        patch.object(qpu_planning, "family_candidates", side_effect=reject_family),
        patch.object(live_run, "QiskitRuntimeService", return_value=service),
        patch.object(live_run, "evaluate", side_effect=_forbid_service) as evaluate,
        patch.object(live_run, "write_archive", side_effect=_forbid_service) as write_archive,
        patch.object(live_run, "submit", side_effect=_forbid_service) as submit,
        patch.object(qpu_cases, "write_case", side_effect=_forbid_service) as write_case,
        patch.object(native_preflight, "qualify", side_effect=_forbid_service) as qualify,
        redirect_stdout(io.StringIO()),
        redirect_stderr(stderr),
    ):
        status = live_run.main(
            [
                "--family",
                "ripple",
                "--max-replicas",
                "1",
                "--replica-tiers",
                "1",
                "--max-execution-seconds",
                "60",
                "--max-total-execution-seconds",
                "60",
                "--native-dry-run",
                "--out",
                directory,
            ]
        )
        _require(status == 1, f"unrouted family changed the failing CLI status to {status}")
        _require(not list(Path(directory).iterdir()), "unrouted family created a synthetic run or approval case")
        for operation in (evaluate, write_archive, submit, write_case, qualify):
            _require(operation.call_count == 0, f"unrouted family reached {operation._mock_name}")
    prefix = "FAIL: the experiment family has no admitted routed candidate; family='ripple'; selection_trace="
    failure = stderr.getvalue()
    _require(failure.startswith(prefix), "unrouted family lost its family and failure boundary")
    retained_trace = json.loads(failure.removeprefix(prefix))
    expected_trace = live_run._scrub_instances(live_run._jsonable(trace_fixture))
    _require(retained_trace == expected_trace, "unrouted family omitted or changed nested rejection evidence")
    _require("crn:private:instance" not in failure, "unrouted diagnostics exposed an IBM Cloud instance")
    _require(supplied_traces == [trace_fixture], "diagnostic sanitization mutated the caller's selection trace")


def _verify_control_timing() -> None:
    """A Target missing the control's measure or reset timing, or dt, raises ValueError."""
    from types import SimpleNamespace

    class Target:
        def __init__(self, dt: float | None, measure: float | None, reset: float | None) -> None:
            self.dt = dt
            self.table = {name: value for name, value in (("measure", measure), ("reset", reset)) if value is not None}
            self.operation_names = set(self.table)

        def __getitem__(self, name: str) -> dict[tuple[int], Any]:
            return {(3,): SimpleNamespace(duration=self.table[name])}

    measure, reset = qpu_planning.control_timing_dt(Target(2e-9, 1.6e-6, 0.8e-6), 3)
    if not (math.isclose(measure, 800.0) and math.isclose(reset, 400.0)):
        raise RuntimeError("control timing differs from duration / dt")
    for broken in (Target(None, 1.6e-6, 0.8e-6), Target(2e-9, None, 0.8e-6), Target(2e-9, 1.6e-6, 0.0)):
        try:
            qpu_planning.control_timing_dt(broken, 3)
        except ValueError:
            continue
        raise RuntimeError("incomplete control timing was admitted")


def _verify_coherence_readout(snapshot: live_run.Snapshot) -> None:
    """The extracted readout map equals the routed final layout; a post-prefix two-qubit gate or a split map raises."""
    from coherence_window import B0, READ_A, READ_B, SECTOR, coherence_circuits
    from patch_characterization import CONTROL, SPECTATOR, WORK_A, WORK_B

    layout = [142, 136, 143, 144, 123, 145]
    static, dynamic = coherence_circuits(836)
    isas = [live_run._compile(circuit, snapshot, live_run.SEED_TRANSPILER, layout) for circuit in (*static, *dynamic)]
    readout = qpu_planning.coherence_readout_qubits(isas)
    final = isas[0].layout.final_index_layout()
    roles = {"b0": CONTROL, "read_a": WORK_A, "read_b": WORK_B, "sector": SPECTATOR}
    _require(readout == {label: final[role] for label, role in roles.items()}, f"readout {readout} != final layout")
    _require({B0, READ_A, READ_B, SECTOR} == set(range(4)), "coherence clbits changed")
    entangled = isas[0].copy()
    entangled.cz(readout["read_a"], readout["read_b"])
    split = isas[1].copy()
    split.measure(readout["sector"], READ_A)
    for broken in ([entangled], [isas[0], split]):
        try:
            qpu_planning.coherence_readout_qubits(broken)
        except ValueError:
            continue
        raise RuntimeError("a post-prefix two-qubit gate or a split readout map was admitted")


def _verify_patch_selection(snapshot: live_run.Snapshot) -> None:
    """Calibrated patch embeddings are valid, ordered and deterministic; exclusions and the declared override hold."""
    import copy as copy_module

    from patch_characterization import PATCH_EDGES, PATCH_ROLES

    layouts, found = qpu_planning.patch_layouts(snapshot, 8)
    _require(len(layouts) == 8 and found >= 8, f"FakeFez offers {len(layouts)} of {found} patch embeddings")
    _require((layouts, found) == qpu_planning.patch_layouts(snapshot, 8), "patch embeddings are not deterministic")
    couplers = {tuple(sorted(pair)) for pair in snapshot.backend.target["cz"]}
    for layout, prefilter in layouts:
        _require(len(set(layout)) == len(PATCH_ROLES), f"{layout} reuses a qubit")
        _require(
            all(tuple(sorted((layout[a], layout[b]))) in couplers for a, b in PATCH_EDGES), f"{layout} lacks a coupler"
        )
        _require(0.0 < prefilter <= 1.0, f"{layout} prefilter {prefilter}")
    _require(
        [p for _, p in layouts] == sorted((p for _, p in layouts), reverse=True), "prefilter order is not descending"
    )
    best = layouts[0][0]
    excluded = copy_module.copy(snapshot)
    excluded.excluded_qubits = {**snapshot.excluded_qubits, best[0]: "fixture"}
    _require(
        all(best[0] not in layout for layout, _ in qpu_planning.patch_layouts(excluded, 8)[0]),
        "an excluded qubit entered a patch",
    )
    coupler = (best[PATCH_EDGES[0][0]], best[PATCH_EDGES[0][1]])
    blocked = copy_module.copy(snapshot)
    blocked.excluded_edges = {**snapshot.excluded_edges, coupler: "fixture", coupler[::-1]: "fixture"}
    _require(
        all(
            tuple(sorted(coupler)) not in {tuple(sorted((layout[a], layout[b]))) for a, b in PATCH_EDGES}
            for layout, _ in qpu_planning.patch_layouts(blocked, 8)[0]
        ),
        "an excluded coupler entered a patch",
    )
    with patch.object(qpu_planning, "PATCH_PREFILTER", 3):
        trace: dict[str, Any] = {}
        chosen = qpu_planning.patch_candidates(
            live_run, [snapshot], _args("coherence-window", patch_qubits=None, optimizer_candidates=2), trace
        )
    _require(1 <= len(chosen) <= 2, f"{len(chosen)} calibrated patches reached admission")
    _require(all(configuration["patch_selection"] == "calibration" for _, configuration in chosen), "selection label")
    scores = {tuple(row["patch_qubits"]): row["joint_score"] for row in trace["patch_search"]}
    picked = [scores[tuple(configuration["patch_qubits"])] for _, configuration in chosen]
    _require(picked == sorted(scores.values(), reverse=True)[: len(picked)], "admission skipped a better patch")
    prefilter = trace["patch_prefilter"][snapshot.name]
    _require(prefilter["compiled"] == 3 and prefilter["embeddings"] >= 3, f"prefilter trace {prefilter}")
    configuration = chosen[0][1]
    record = {
        "policy": {"design": {"family": "coherence-window", "patch_qubits": None}},
        "family_configuration": configuration,
    }
    arguments = qpu_cases._patch_arguments(record)
    _require(arguments == [], f"a calibration-chosen patch replays with {arguments}")
    record["policy"]["design"]["patch_qubits"] = list(configuration["patch_qubits"])
    try:
        qpu_cases._patch_arguments(record)
    except ValueError:
        pass
    else:
        raise RuntimeError("a declared patch was replayed for a calibration-chosen selection")
    declared = qpu_planning.patch_candidates(
        live_run, [snapshot], _args("coherence-window", patch_qubits=[142, 136, 143, 144, 123, 145]), {}
    )
    _require(
        len(declared) == 1 and declared[0][1]["patch_selection"] == "declared", "the declared patch override changed"
    )


def _measure_first(circuit: Any) -> Any:
    """Move the first measurement directly after the last earlier operation on its qubit.

    The moved measurement acts on another qubit than the operations it now
    precedes, so the distribution is unchanged and only circuit.data order,
    which is_dynamic reads, differs.
    """
    data = list(circuit.data)
    first = next(index for index, instruction in enumerate(data) if instruction.operation.name == "measure")
    qubit = data[first].qubits[0]
    last = max(index for index in range(first) if qubit in data[index].qubits)
    moved = circuit.copy_empty_like()
    for index, instruction in enumerate(data):
        if index != first:
            moved.append(instruction)
        if index == last:
            moved.append(data[first])
    return moved


def _verify_static_group_admission(service: _ProbeService, snapshot: live_run.Snapshot) -> None:
    """A static patch group holding a measure-then-gate member writes no planned record and names the member."""
    import patch_characterization

    original = patch_characterization.patch_groups
    names: list[str] = []

    def injected(*args: Any, **kwargs: Any) -> list[Any]:
        static, *rest = original(*args, **kwargs)
        member = static.members[0]
        moved = dataclasses.replace(member, circuit=_measure_first(member.circuit))
        _require(not local_compute.is_dynamic(member.circuit), f"{member.name}: the patch member is already dynamic")
        _require(local_compute.is_dynamic(moved.circuit), f"{member.name}: the reordered member stays static")
        names.append(member.name)
        return [dataclasses.replace(static, members=(moved, *static.members[1:])), *rest]

    patch_qubits = [142, 136, 143, 144, 123, 145]
    args = _args("patch-window", patch_qubits=patch_qubits)
    clean = qpu_planning.family_candidates(live_run, [snapshot], args, {})
    _require(
        len(qpu_planning.admitted_family_candidates(live_run, clean, {})) == 1, "admission rejects the static family"
    )
    with patch.object(patch_characterization, "patch_groups", injected):
        trace: dict[str, Any] = {}
        mixed = qpu_planning.family_candidates(live_run, [snapshot], args, trace)
    _require(len(mixed) == 1 and bool(names), f"the injected patch family did not compile: {trace}")
    expected = f"dynamic members {names[:1]}"
    _require(not qpu_planning.admitted_family_candidates(live_run, mixed, trace), "a mixed static group was admitted")
    _require(expected in trace["family_rejections"][-1]["reason"], f"admission omits {expected}: {trace}")
    static_choice = mixed[0][0][0]
    _require(
        expected in live_run.choice_change_reasons(static_choice, snapshot),
        "the pre-submit refresh reads another predicate than planning",
    )
    stderr = io.StringIO()
    with (
        tempfile.TemporaryDirectory(prefix="gororoba-planning-mixed-static-") as directory,
        patch.object(patch_characterization, "patch_groups", injected),
        patch.object(live_run, "QiskitRuntimeService", return_value=service),
        patch.object(live_run, "simulate", side_effect=_forbid_service) as simulate,
        patch.object(live_run, "evaluate", side_effect=_forbid_service) as evaluate,
        patch.object(live_run, "write_archive", side_effect=_forbid_service) as write_archive,
        patch.object(live_run, "submit", side_effect=_forbid_service) as submit,
        patch.object(qpu_cases, "write_case", side_effect=_forbid_service) as write_case,
        redirect_stdout(io.StringIO()),
        redirect_stderr(stderr),
    ):
        status = live_run.main(
            [
                "--family",
                "patch-window",
                "--patch-qubits",
                ",".join(map(str, patch_qubits)),
                "--max-replicas",
                "1",
                "--replica-tiers",
                "1",
                "--no-isolated-reference",
                "--max-execution-seconds",
                "9",
                "--max-total-execution-seconds",
                "27",
                "--out",
                directory,
            ]
        )
        _require(status == 1, f"a mixed static group changed the dry-run status to {status}")
        _require(not list(Path(directory).iterdir()), "a mixed static group wrote a dry-run record")
        for operation in (simulate, evaluate, write_archive, submit, write_case):
            _require(operation.call_count == 0, f"a mixed static group reached {operation._mock_name}")
    _require(expected in stderr.getvalue(), f"the dry-run refusal omits {expected}")


class _RangeBackend(_ProbeBackend):
    """FakeFez whose rep_delay_range the contract can move between configuration reads."""

    rep_delay_range: list[float] | None = None

    def configuration(self) -> Any:
        configuration = super().configuration()
        if self.rep_delay_range is not None:
            configuration.rep_delay_range = list(self.rep_delay_range)
        return configuration


def _verify_rep_delay_range() -> None:
    """--rep-delay outside rep_delay_range refuses in the CLI, the planner, the charge model and the Sampler."""
    backend = _RangeBackend("rep_delay_fixture", FakeFez())
    low, high = backend.configuration().rep_delay_range
    _require(qpu_planning.repetition_delay(backend) == 0.00025, "the default repetition delay moved")
    _require(qpu_planning.repetition_delay(backend, 0.00005) == 0.00005, "an in-range request was not honored")
    for outside in (high + 1e-6, -1e-6, float("nan")):
        try:
            qpu_planning.repetition_delay(backend, outside)
        except ValueError:
            pass
        else:
            raise RuntimeError(f"the charge model accepted a repetition delay {outside} outside [{low}, {high}]")
        _require(
            bool(qpu_planning.repetition_delay_violations(backend, outside, None)),
            f"repetition_delay_violations admitted {outside}",
        )
    service = _ProbeService([backend])
    try:
        with redirect_stdout(io.StringIO()):
            live_run.plan(
                cast(Any, service), _fixture_args(groups=["hybrid_shor_mod15"], max_replicas=1, rep_delay=high * 2)
            )
    except live_run.LiveRunError as error:
        _require("--rep-delay" in str(error), f"the planner refused for another reason: {error}")
    else:
        raise RuntimeError("the planner admitted a repetition delay outside the backend range")
    # The client-side Sampler takes a Backend instance; FakeFez carries the same range.
    sampler_backend = FakeFez()
    default = live_run.configure_sampler(sampler_backend, "dynamic", False, None, [], 64, 60)
    _require(default.options.execution.rep_delay == 0.00025, "the Sampler default left the backend default")
    requested = live_run.configure_sampler(sampler_backend, "dynamic", False, None, [], 64, 60, rep_delay=0.00005)
    _require(requested.options.execution.rep_delay == 0.00005, "the Sampler omitted the requested rep_delay")
    try:
        live_run.configure_sampler(sampler_backend, "dynamic", False, None, [], 64, 60, rep_delay=high * 2)
    except live_run.LiveRunError:
        pass
    else:
        raise RuntimeError("the Sampler accepted a repetition delay outside the backend range")
    for value in ("-0.0001", "nan", "inf"):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            try:
                live_run.main(["--rep-delay", value, "--out", "/tmp/rep-delay-contract-unused"])
            except SystemExit as error:
                _require(error.code == 2, f"--rep-delay {value} produced CLI status {error.code}")
            else:
                raise RuntimeError(f"the CLI accepted --rep-delay {value}")
        _require("--rep-delay" in stderr.getvalue(), f"the CLI rejection of {value} did not name --rep-delay")


def _ideal_predictions(choice: Any, noise: Any, shots: int) -> dict[str, list[Any]]:
    del noise, shots
    return {entry.name: [entry.ideal for _ in entry.replicas] for entry in choice.entries}


def _verify_rep_delay_charge(snapshot: live_run.Snapshot, choices: list[Any], configuration: dict[str, Any]) -> None:
    """Every PUB's charge per shot moves by exactly the requested repetition-delay change."""
    usage = {"usage_limit_reached": False, "usage_remaining_seconds": 130.0}
    ledgers: dict[float | None, list[dict[str, Any]]] = {}
    for delay in (None, 0.0001, 0.0004):
        args = _args("folded-qpe", rep_delay=delay)
        # The charge reads circuit durations and the delay, never the outcome
        # model, so each replica predicts its ideal law.
        with (
            patch.object(qpu_planning, "family_candidates", return_value=[(choices, configuration)]),
            patch.object(live_run, "simulate", _ideal_predictions),
        ):
            _selected, metadata = qpu_planning.prepare(live_run, [snapshot], args, usage, {})
        candidates = metadata["optimization"]["candidates"]
        _require(len(candidates) == 1, "the fixed-tier plan searched more than one candidate")
        ledgers[delay] = candidates[0]["jobs"]
    default = qpu_planning.repetition_delay(snapshot.backend)
    for delay in (0.0001, 0.0004):
        for job, base in zip(ledgers[delay], ledgers[None], strict=True):
            change = math.fsum(
                pub["estimated_execution_seconds"] - other["estimated_execution_seconds"]
                for pub, other in zip(job["pubs"], base["pubs"], strict=True)
            )
            shots = sum(pub["shots"] for pub in job["pubs"])
            for pub, other in zip(job["pubs"], base["pubs"], strict=True):
                _require(pub["repetition_delay_seconds"] == delay, f"{pub['name']}: the charge left --rep-delay")
                _require(other["repetition_delay_seconds"] == default, f"{pub['name']}: the default delay moved")
                per_shot = (pub["estimated_execution_seconds"] - other["estimated_execution_seconds"]) / pub["shots"]
                _require(
                    math.isclose(per_shot, delay - default, rel_tol=1e-9, abs_tol=1e-15),
                    f"{pub['name']}: charge per shot moved {per_shot} s for a {delay - default} s delay change",
                )
            _require(
                math.isclose(
                    job["estimated_charge_seconds"] - base["estimated_charge_seconds"],
                    change,
                    rel_tol=1e-9,
                    abs_tol=1e-12,
                ),
                f"{job['name']}: the job charge moved by more than its PUBs' repetition change",
            )
            _require(
                math.isclose(change, shots * (delay - default), rel_tol=1e-9, abs_tol=1e-12),
                f"{job['name']}: the charge moved {change} s, not shots x delay change",
            )


class _UnsentSampler(_ProbeSampler):
    def run(self, circuits: list[Any]) -> Any:
        raise RuntimeError(f"a refused repetition delay reached Sampler.run with {len(circuits)} circuits")


def _unsent_sampler(
    backend: Any, kind: str, twirl: bool, dd: str | None, tags: list[str], *args: Any, **kwargs: Any
) -> Any:
    del backend, twirl, dd
    return _UnsentSampler(kind, tags, int(args[0]) if args else 4096, None, None, args[1] if len(args) > 1 else None)


def _verify_rep_delay_approval() -> None:
    """The policy and execution contract bind --rep-delay; a changed delay or range stops before any job."""
    backend = _RangeBackend("rep_delay_fixture", FakeFez())
    service = _ProbeService([backend])
    args = _fixture_args(groups=["hybrid_shor_mod15"], max_replicas=1, rep_delay=0.0001)
    with redirect_stdout(io.StringIO()):
        choices, record = live_run.plan(cast(Any, service), args)
        live_run.evaluate(choices, record)
        default_choices, default_record = live_run.plan(
            cast(Any, service), _fixture_args(groups=["hybrid_shor_mod15"], max_replicas=1)
        )
    _require(record["policy"]["rep_delay_seconds"] == 0.0001, "the policy omitted the requested repetition delay")
    _require("rep_delay_seconds" not in default_record["policy"], "a default plan recorded a repetition delay")
    _require(
        default_record["execution_contract"]["backends"]
        == [{"name": backend.name, "repetition_delay_seconds": 0.00025}],
        "the default execution contract changed shape",
    )
    bound = record["execution_contract"]["backends"][0]
    _require(
        bound["repetition_delay_seconds"] == 0.0001
        and bound["default_repetition_delay_seconds"] == 0.00025
        and bound["repetition_delay_range_seconds"] == [0.0, 0.0005],
        f"the execution contract does not bind the requested delay and its range: {bound}",
    )
    del default_choices
    with tempfile.TemporaryDirectory(prefix="gororoba-rep-delay-approval-") as directory:
        approved = Path(directory) / "approved"
        approved.mkdir()
        live_run.write_archive(approved, choices)
        live_run.write_json(approved, record)
        qpy_digest = hashlib.sha256((approved / "isa.qpy").read_bytes()).hexdigest()
        record_digest = hashlib.sha256((approved / "record.json").read_bytes()).hexdigest()
        _require(not live_run.approved_record_mismatches(approved, record, qpy_digest), "an unchanged plan mismatches")
        moved = copy.deepcopy(record)
        moved["policy"]["rep_delay_seconds"] = 0.00005
        _require(
            "policy differs" in live_run.approved_record_mismatches(approved, moved, qpy_digest),
            "the approval accepted a changed repetition delay",
        )
        ranged = copy.deepcopy(record)
        ranged["execution_contract"]["backends"][0]["repetition_delay_range_seconds"] = [0.0, 0.001]
        _require(
            "execution_contract differs" in live_run.approved_record_mismatches(approved, ranged, qpy_digest),
            "the approval accepted a moved repetition-delay range",
        )
        run_dir = Path(directory) / "run"
        run_dir.mkdir()

        def attempt(submit_args: argparse.Namespace, label: str) -> dict[str, Any]:
            # submit compares the refreshed choices, so the fresh plan needs no evaluation.
            with redirect_stdout(io.StringIO()):
                fresh_choices, fresh_record = live_run.plan(cast(Any, service), submit_args)
            submit_args.approved_record = approved
            submit_args.approved_record_sha256 = record_digest
            try:
                with patch.object(live_run, "configure_sampler", _unsent_sampler), redirect_stdout(io.StringIO()):
                    live_run.submit(
                        cast(Any, service),
                        fresh_choices,
                        submit_args,
                        fresh_record,
                        lambda: live_run.write_archive(run_dir, fresh_choices),
                        lambda: None,
                    )
            except live_run.LiveRunError:
                pass
            else:
                raise RuntimeError(f"{label}: the submission completed")
            _require(fresh_record["state"] == "approval_required", f"{label}: left {fresh_record['state']}")
            _require(not (approved / live_run.APPROVAL_CONSUMED_FILE).exists(), f"{label}: consumed the approval")
            return fresh_record

        differing = attempt(
            _fixture_args(groups=["hybrid_shor_mod15"], max_replicas=1, rep_delay=0.00005), "a differing --rep-delay"
        )
        _require(
            "policy differs" in differing["renewed_approval"]["mismatches"],
            f"a differing --rep-delay stopped for {differing['renewed_approval']}",
        )
        omitted = attempt(_fixture_args(groups=["hybrid_shor_mod15"], max_replicas=1), "an omitted --rep-delay")
        _require("policy differs" in omitted["renewed_approval"]["mismatches"], "an omitted --rep-delay passed")

        # The range moves between planning and the pre-submission refresh.
        submit_args = _fixture_args(groups=["hybrid_shor_mod15"], max_replicas=1, rep_delay=0.0001)
        with redirect_stdout(io.StringIO()):
            fresh_choices, fresh_record = live_run.plan(cast(Any, service), submit_args)
        backend.rep_delay_range = [0.0, 0.001]
        submit_args.approved_record = approved
        submit_args.approved_record_sha256 = record_digest
        try:
            with patch.object(live_run, "configure_sampler", _unsent_sampler), redirect_stdout(io.StringIO()):
                live_run.submit(
                    cast(Any, service),
                    fresh_choices,
                    submit_args,
                    fresh_record,
                    lambda: live_run.write_archive(run_dir, fresh_choices),
                    lambda: None,
                )
        except live_run.LiveRunError:
            pass
        else:
            raise RuntimeError("a moved repetition-delay range reached submission")
        finally:
            backend.rep_delay_range = None
        reasons = fresh_record.get("renewed_approval", {}).get("changed_groups", {}).get("repetition_delay")
        _require(
            fresh_record["state"] == "approval_required" and reasons is not None,
            f"a range moved before the refresh left {fresh_record['state']}: {fresh_record.get('renewed_approval')}",
        )

        # The range moves after the approved-record check, before the batch.
        submit_args = _fixture_args(groups=["hybrid_shor_mod15"], max_replicas=1, rep_delay=0.0001)
        with redirect_stdout(io.StringIO()):
            fresh_choices, fresh_record = live_run.plan(cast(Any, service), submit_args)
        submit_args.approved_record = approved
        submit_args.approved_record_sha256 = record_digest
        original_drift = live_run.approved_calibration_drift

        def drift_then_move(record_: dict[str, Any], name: str, calibration: str, *values: Any) -> str | None:
            backend.rep_delay_range = [0.0, 0.00008]
            return original_drift(record_, name, calibration, *values)

        try:
            with (
                patch.object(live_run, "configure_sampler", _unsent_sampler),
                patch.object(live_run, "approved_calibration_drift", drift_then_move),
                redirect_stdout(io.StringIO()),
            ):
                live_run.submit(
                    cast(Any, service),
                    fresh_choices,
                    submit_args,
                    fresh_record,
                    lambda: live_run.write_archive(run_dir, fresh_choices),
                    lambda: None,
                )
        except live_run.LiveRunError as error:
            _require("repetition delay" in str(error), f"the batch stopped for another reason: {error}")
        else:
            raise RuntimeError("a repetition delay outside the batch-time range reached Sampler.run")
        finally:
            backend.rep_delay_range = None
        _require(
            fresh_record["state"] == "approval_required" and not fresh_record["submission"]["jobs"],
            f"a batch-time range change left {fresh_record['state']}",
        )
        _require(not (approved / live_run.APPROVAL_CONSUMED_FILE).exists(), "the refused batch consumed the approval")


def _verify_state_prep_family() -> None:
    """state-prep-control pins each arm to its qubit, fuses two static PUBs and one dynamic, admits 8192 shots."""
    backend = _ProbeBackend("state_prep_fixture", FakeFez())
    service = _ProbeService([backend])
    with redirect_stdout(io.StringIO()):
        snapshot = live_run.take_snapshot(cast(Any, service), backend.name)
    qubits = [qubit for qubit in range(40, 156, 7) if qubit not in snapshot.excluded_qubits][:14]
    _require(len(qubits) == 14, "FakeFez lacks 14 admitted fixture qubits")
    args = _args(
        "state-prep-control",
        layout=qubits,
        optimize=True,
        shot_tiers=[4096, 8192, 16384],
        optimizer_candidates=1,
        max_execution_seconds=60,
        max_total_execution_seconds=120.0,
        reserve_seconds=0.0,
    )
    trace: dict[str, Any] = {}
    candidates = qpu_planning.family_candidates(live_run, [snapshot], args, trace)
    _require(len(candidates) == 1, f"the declared layout produced {len(candidates)} candidates: {trace}")
    choices, configuration = candidates[0]
    _require(configuration["qubits"] == qubits and configuration["layout_source"] == "declared", "layout lost")
    _require(len(choices) == 28, "each qubit needs one static and one dynamic group")
    for choice in choices:
        qubit = int(choice.group.name.rsplit("_q", 1)[1])
        _require([r.qubits for r in choice.replicas] == [[qubit]], f"{choice.group.name}: moved off qubit {qubit}")
    pubs = live_run.execution_pubs(choices)
    _require(sorted(pub.kind for pub in pubs) == ["dynamic", "static", "static"], "the arms fused into other PUBs")
    for pub in pubs:
        covered = sorted(q for component in pub.components for q in component.manifest()["physical_qubits"])
        _require(covered == sorted(qubits), f"{pub.name}: measures {covered}, not every named qubit")
        arms = {component.entry.name.split("_q")[0] for component in pub.components}
        _require(len(arms) == 1, f"{pub.name}: mixes arms {arms}")
    batches = {kind: live_run.submission_batches(choices, kind, 8192) for kind in ("static", "dynamic")}
    _require([len(b) for b in batches["static"]] == [2] and [len(b) for b in batches["dynamic"]] == [1], "jobs")
    default_trace: dict[str, Any] = {}
    default_args = _args("state-prep-control", layout=None)
    _require(
        not qpu_planning.family_candidates(live_run, [snapshot], default_args, default_trace),
        "the retained n21 layout was placed on a backend other than its own",
    )
    _require(
        "ibm_kingston" in default_trace["family_rejections"][0]["reason"],
        f"the default layout refused for another reason: {default_trace}",
    )
    usage = {"usage_limit_reached": False, "usage_remaining_seconds": 300.0}
    with patch.object(live_run, "simulate", _ideal_predictions):
        selected, metadata = qpu_planning.prepare(live_run, [snapshot], args, usage, {})
    _require(
        [choice.group.name for choice in selected] == [choice.group.name for choice in choices] and args.shots == 8192,
        f"the optimizer selected {args.shots} shots",
    )
    rejected = {
        int(row["proxy_metadata"]["shots"]) for row in metadata["optimization"]["candidates"] if not row["feasible"]
    }
    _require(rejected == {4096}, f"the optimizer rejected tiers {rejected}, not 4096 alone")
    _require(len(metadata["observable_contracts"]) == 42, "the plan lost a per-qubit endpoint")
    rebuilt = diagnostic_experiments.record_groups({"family_configuration": configuration})
    _require([g.name for g in rebuilt] == [c.group.name for c in choices], "record_groups lost the per-qubit groups")
    _verify_shot_ceiling(snapshot, qubits)
    subset_args = _args(
        "state-prep-control",
        layout=qubits[:7],
        state_prep_arms=["prep0"],
        optimize=True,
        shot_tiers=[4096, 8192],
        optimizer_candidates=1,
        max_execution_seconds=60,
        max_total_execution_seconds=120.0,
        reserve_seconds=0.0,
    )
    subset = qpu_planning.family_candidates(live_run, [snapshot], subset_args, {})
    _require(len(subset) == 1, "the prep0-only selection produced no candidate")
    subset_choices, subset_configuration = subset[0]
    _require(list(subset_configuration["arms"]) == ["prep0"], f"arms recorded {subset_configuration['arms']}")
    _require([pub.kind for pub in live_run.execution_pubs(subset_choices)] == ["static"], "prep0 alone left one PUB")
    _require(qpu_planning.settings(subset_args)["state_prep_arms"] == ["prep0"], "the policy lost the arm selection")
    _require("state_prep_arms" not in qpu_planning.settings(args), "an omitted selection entered the policy")
    _verify_state_prep_history(snapshot, qubits[:7])


def _verify_state_prep_history(snapshot: Any, qubits: list[int]) -> None:
    """x_history alone fuses one dynamic PUB, measure then X on every named qubit, in one job of its own."""
    args = _args(
        "state-prep-control",
        layout=qubits,
        state_prep_arms=["x_history"],
        optimize=True,
        shot_tiers=[4096, 8192],
        optimizer_candidates=1,
        max_execution_seconds=60,
        max_total_execution_seconds=120.0,
        reserve_seconds=0.0,
    )
    candidates = qpu_planning.family_candidates(live_run, [snapshot], args, {})
    _require(len(candidates) == 1, "the x_history selection produced no candidate")
    choices, configuration = candidates[0]
    _require(configuration["arms"] == {"x_history": "init, measure, x"}, f"arms recorded {configuration['arms']}")
    _require("dynamic x_history PUB, alone in its job" in configuration["placement_contract"], "placement contract")
    pubs = live_run.execution_pubs(choices)
    _require([pub.kind for pub in pubs] == ["dynamic"], f"x_history fused into {[pub.kind for pub in pubs]}")
    pub = pubs[0]
    covered = sorted(q for component in pub.components for q in component.manifest()["physical_qubits"])
    _require(covered == sorted(qubits), f"{pub.name}: measures {covered}, not every named qubit")
    manifest = pub.manifest()
    _require(
        manifest["feed_forward_operation_count"] == 0 and manifest["sequential_stage_count"] == 0,
        "the measure-then-X PUB carries classical stages",
    )
    # The X follows the measurement on each qubit, so a shot ends in the flip of the projected state.
    for qubit in qubits:
        steps = [
            instruction.operation.name
            for instruction in pub.circuit.data
            if [pub.circuit.find_bit(bit).index for bit in instruction.qubits] == [qubit]
        ]
        _require(steps == ["measure", "x"], f"qubit {qubit}: the fused PUB runs {steps}, not measure then x")
    _require(
        [len(batch) for batch in live_run.submission_batches(choices, "dynamic", 8192)] == [1]
        and not live_run.submission_batches(choices, "static", 8192),
        "x_history left its own single-PUB job",
    )
    usage = {"usage_limit_reached": False, "usage_remaining_seconds": 300.0}
    with patch.object(live_run, "simulate", _ideal_predictions):
        _selected, metadata = qpu_planning.prepare(live_run, [snapshot], args, usage, {})
    names = sorted(contract["name"] for contract in metadata["observable_contracts"])
    _require(names == sorted(f"spc_history_excited_q{q}" for q in qubits), f"history endpoints {names}")
    _require(qpu_planning.settings(args)["state_prep_arms"] == ["x_history"], "the policy lost the history arm")
    for arms in ("x_history,prep0", "prep0,x_history", "x_history,reset", "reset"):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            try:
                live_run.main(
                    [
                        "--family",
                        "state-prep-control",
                        "--state-prep-arms",
                        arms,
                        "--max-execution-seconds",
                        "60",
                        "--max-total-execution-seconds",
                        "60",
                    ]
                )
            except SystemExit as error:
                _require(error.code == 2, f"--state-prep-arms {arms} produced CLI status {error.code}")
            else:
                raise RuntimeError(f"the CLI accepted --state-prep-arms {arms}")
        _require("--state-prep-arms" in stderr.getvalue(), f"the rejection of {arms} did not name the flag")


def _verify_shot_ceiling(snapshot: Any, qubits: list[int]) -> None:
    """Shot tiers above configuration().max_shots leave the plan, and a batch above it refuses."""
    reported = qpu_planning.shot_ceiling(snapshot.backend)
    _require(reported == 100000, f"FakeFez reports max_shots {reported}")
    ceiling = 100000
    _require(not qpu_planning.shot_ceiling_violations(snapshot.backend, ceiling), "max_shots itself was refused")
    _require(bool(qpu_planning.shot_ceiling_violations(snapshot.backend, ceiling + 1)), "max_shots + 1 was admitted")
    usage = {"usage_limit_reached": False, "usage_remaining_seconds": 300.0}

    def tier_args(tiers: list[int]) -> Any:
        return _args(
            "state-prep-control",
            layout=qubits,
            optimize=True,
            shot_tiers=tiers,
            optimizer_candidates=1,
            max_execution_seconds=60,
            max_total_execution_seconds=120.0,
            reserve_seconds=0.0,
        )

    trace: dict[str, Any] = {}
    args = tier_args([8192, ceiling + 1])
    with patch.object(live_run, "simulate", _ideal_predictions):
        _selected, metadata = qpu_planning.prepare(live_run, [snapshot], args, usage, trace)
    planned = {int(row["proxy_metadata"]["shots"]) for row in metadata["optimization"]["candidates"]}
    _require(planned == {8192} and args.shots == 8192, f"the optimizer planned tiers {planned}")
    _require(
        trace.get("shot_ceiling") == {"max_shots": ceiling, "dropped_tiers": [ceiling + 1]},
        f"the dropped tier left no trace: {trace.get('shot_ceiling')}",
    )
    try:
        with patch.object(live_run, "simulate", _ideal_predictions):
            qpu_planning.prepare(live_run, [snapshot], tier_args([ceiling + 1]), usage, {})
    except live_run.LiveRunError as error:
        _require("max_shots" in str(error), f"the planner refused for another reason: {error}")
    else:
        raise RuntimeError("a plan whose every tier exceeds max_shots was admitted")


def _verify_prep_excitation() -> None:
    """--prep-excitation is an N21 planning assumption the policy binds and both model paths apply."""
    import numpy as np
    from qiskit_aer import AerSimulator

    import dynamic_density
    import n21_exact_planning
    from packing import Replica

    for argv, label in (
        (["--family", "folded-qpe", "--prep-excitation", "0.01"], "a non-N21 family"),
        (["--family", "n21-feedback-encoded", "--prep-excitation", "1.0"], "an excitation of 1"),
        (["--family", "n21-feedback-encoded", "--prep-excitation", "nan"], "a NaN excitation"),
    ):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            try:
                live_run.main([*argv, "--max-execution-seconds", "60", "--max-total-execution-seconds", "60"])
            except SystemExit as error:
                _require(error.code == 2, f"{label} produced CLI status {error.code}")
            else:
                raise RuntimeError(f"the CLI accepted {label}")
        _require("--prep-excitation" in stderr.getvalue(), f"the CLI rejection of {label} did not name the flag")
    _require("prep_excitation" not in qpu_planning.settings(_args("n21-feedback")), "a default plan binds epsilon")
    _require(
        qpu_planning.settings(_args("n21-feedback", prep_excitation=0.01))["prep_excitation"] == 0.01,
        "the design settings omit the declared excitation",
    )
    try:
        qpu_planning.prepare(live_run, [], _args("folded-qpe", prep_excitation=0.01), {}, {})
    except live_run.LiveRunError as error:
        _require("N21" in str(error), f"the planner refused a non-N21 excitation for another reason: {error}")
    except Exception as error:  # an empty snapshot list reaches no other refusal first
        raise RuntimeError(f"the planner did not refuse a non-N21 excitation: {error!r}") from error
    # The planner's sampled path (live_run.simulate) and its exact law
    # (n21_exact_planning.exact_predictions) apply one channel.
    circuit, noise = dynamic_density._fixture()
    entry = live_run._entry("fixture", circuit, np.zeros(2**circuit.num_clbits), [Replica(0, {0: 0, 1: 1, 2: 2}, 1.0)])
    snap = object()
    choice = SimpleNamespace(snap=snap, entries=[entry])
    simulator = AerSimulator(method="density_matrix", noise_model=noise)
    shots = 200_000
    epsilon = 0.25
    excited = live_run.simulate(cast(Any, choice), simulator, shots, prep_excitation=epsilon)
    sampled = {"fixture": tuple(tuple(map(float, dist)) for dist in excited["fixture"])}
    exact, evidence = n21_exact_planning.exact_predictions(
        [choice], {id(snap): noise}, sampled, shots, 0.01, prep_excitation=epsilon
    )
    _require(evidence["passed"] and evidence["prep_excitation"] == epsilon, f"excited planning failed: {evidence}")
    expected = dynamic_density.probabilities(entry.replicas[0], noise, prep_excitation=epsilon)
    _require(np.allclose(exact["fixture"][0], expected, rtol=0, atol=1e-15), "the exact law left dynamic_density")
    try:
        n21_exact_planning.exact_predictions([choice], {id(snap): noise}, sampled, shots, 0.01)
    except n21_exact_planning.ExactModelRejected:
        pass
    else:
        raise RuntimeError("an excited sample validated against the unexcited exact law")


# Fields Aer and local_compute fill with the run's own elapsed time.
_TIMING_FIELDS = frozenset({"wall_seconds", "time_taken", "sample_measure_time"})


def _without_timing(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _without_timing(item) for key, item in value.items() if key not in _TIMING_FIELDS}
    if isinstance(value, list):
        return [_without_timing(item) for item in value]
    return value


def _first_difference(left: Any, right: Any, path: str = "") -> str | None:
    """The path of the first value where two JSON trees differ, or None."""
    if isinstance(left, dict) and isinstance(right, dict):
        for key in sorted(set(left) | set(right)):
            if key not in left or key not in right:
                return f"{path}/{key}"
            if (found := _first_difference(left[key], right[key], f"{path}/{key}")) is not None:
                return found
        return None
    if isinstance(left, list) and isinstance(right, list):
        if len(left) != len(right):
            return f"{path} (length {len(left)} != {len(right)})"
        for index, (first, second) in enumerate(zip(left, right, strict=True)):
            if (found := _first_difference(first, second, f"{path}[{index}]")) is not None:
                return found
        return None
    return None if left == right else f"{path}: {left!r} != {right!r}"


def _planning_outcomes(
    snapshot: live_run.Snapshot,
    cases: list[tuple[str, argparse.Namespace, list[tuple[list[Any], dict[str, Any]]]]],
    excited: list[bool],
) -> dict[str, Any]:
    """Every distribution, plan and evaluation record one planning pass derives from simulation, timing removed.

    Each case plans through qpu_planning.prepare on its fixed candidates and
    evaluates the selection through live_run.evaluate. A declared excitation
    then reruns the first case's first selected choice, whose
    QuantumChannelInstruction errors make Aer serialize a copied model;
    excited[0] marks that rerun.
    """
    calls: list[Any] = []
    simulate_entries = live_run.simulate_entries

    def capture(noise: Any, entries: list[Any], shots: int, seed: int) -> dict[str, list[Any]]:
        result = simulate_entries(noise, entries, shots, seed)
        laws = {name: [distribution.tolist() for distribution in laws] for name, laws in result.items()}
        calls.append([[entry.name for entry in entries], shots, seed, laws])
        return result

    outcomes: dict[str, Any] = {}
    usage = {"usage_limit_reached": False, "usage_remaining_seconds": 300.0}
    with patch.object(live_run, "simulate_entries", capture), redirect_stdout(io.StringIO()):
        for label, args, candidates in cases:
            with patch.object(qpu_planning, "family_candidates", return_value=candidates):
                selected, metadata = qpu_planning.prepare(live_run, [snapshot], args, usage, {})
            record: dict[str, Any] = {"shots": args.shots, "policy": {"local_compute": local_compute.settings(args)}}
            live_run.evaluate(selected, record)
            outcomes[label] = live_run._jsonable({"metadata": metadata, "record": record})
            if label == cases[0][0]:
                simulator = live_run.noise_simulator(snapshot.name, snapshot.backend.target, snapshot.properties)
                excited[0] = True
                live_run.simulate(selected[0], simulator, args.model_shots, prep_excitation=0.02)
                excited[0] = False
                # with_prep_excitation draws a fresh QuantumError per call, and
                # its generated id enters the QPY bytes, so the excited batch's
                # QPY digest differs between any two reruns.
                outcomes["excited_batches"] = live_run._jsonable(
                    [
                        {key: value for key, value in batch.items() if key != "ordered_qpy_sha256"}
                        for batch in local_compute.batches(simulator)
                    ]
                )
    # prepare simulates choices on a thread pool; the set of calls is the outcome.
    calls.sort(key=lambda call: json.dumps(call[:3]))
    return cast(dict[str, Any], _without_timing(json.loads(json.dumps({"calls": calls, "outcomes": outcomes}))))


def _verify_serialized_noise(snapshot: live_run.Snapshot) -> None:
    """One retained, qubit-restricted noise serialization leaves every planning outcome bit-identical.

    The stock pass patches SerializedNoiseSimulator back to AerSimulator's
    per-run NoiseModel.to_dict and AerBackend._assemble_noise_model. The
    cases cover one-qubit static and reset groups (state-prep-control), a
    multi-qubit static group and a feed-forward group with Delay members
    (folded-qpe), and an excited rerun whose copied model serializes afresh.
    Qubit 2's own errors hold no Kraus channel while the device model does,
    so its reset batch also serves as the negative control of the opset
    witnesses that _Serialization.restrict keeps.
    """
    from qiskit_aer.noise import NoiseModel

    _require(2 not in snapshot.excluded_qubits, "FakeFez excludes the negative-control qubit 2")
    state_prep = _args("state-prep-control", layout=[2])
    folded = _args("folded-qpe")
    cases = [
        (label, args, qpu_planning.family_candidates(live_run, [snapshot], args, {}))
        for label, args in (("state-prep-control", state_prep), ("folded-qpe", folded))
    ]
    for label, _planning_args, candidates in cases:
        _require(len(candidates) == 1, f"{label}: the fixture produced {len(candidates)} candidates")
    _require(
        any(
            isinstance(instruction.operation, Delay)
            for choices, _configuration in cases[1][2]
            for choice in choices
            for entry in choice.entries
            for replica in entry.replicas
            for instruction in replica.data
        ),
        "folded-qpe lost the Delay members that exercise the relaxation pass",
    )
    model = live_run.noise_simulator(snapshot.name, snapshot.backend.target, snapshot.properties).options.noise_model
    _require(
        local_compute.serialized_noise(model) == model.to_dict(serializable=True),
        "the retained serialization differs from a fresh NoiseModel.to_dict",
    )
    to_dict = NoiseModel.to_dict
    pass_manager = NoiseModel._pass_manager
    observed: dict[str, list[int]] = {}
    excited = [False]

    def counting_to_dict(self: Any, serializable: bool = False) -> Any:
        if serializable and self is model:
            observed["snapshot_serializations"].append(1)
        return to_dict(self, serializable)

    def counting_pass_manager(self: Any) -> Any:
        manager = pass_manager(self)
        if manager is not None:
            run = manager.run

            def counted(programs: list[Any], *args: Any, **kwargs: Any) -> Any:
                if not excited[0]:
                    observed["pass_runs"].append(len(programs))
                return run(programs, *args, **kwargs)

            manager.run = counted
        return manager

    outcomes = {}
    for mode in ("stock", "serialized"):
        observed.update(snapshot_serializations=[], pass_runs=[])
        with (
            patch.object(NoiseModel, "to_dict", counting_to_dict),
            patch.object(NoiseModel, "_pass_manager", counting_pass_manager),
            _stock_aer() if mode == "stock" else contextlib.nullcontext(),
        ):
            outcomes[mode] = _planning_outcomes(snapshot, cases, excited)
        serializations = len(observed["snapshot_serializations"])
        empty_runs = observed["pass_runs"].count(0)
        delay_runs = sum(1 for count in observed["pass_runs"] if count > 0)
        _require(delay_runs > 0, f"{mode}: no batch ran the relaxation pass on its Delay circuits")
        if mode == "stock":
            _require(serializations > 0 and empty_runs > 0, f"{mode}: the per-run Aer path was not exercised")
        else:
            _require(serializations == 0, f"the snapshot model was serialized {serializations} times after configure")
            _require(empty_runs == 0, f"{empty_runs} unexcited batches without Delay still ran the noise passes")
    stock_calls, serialized_calls = outcomes["stock"]["calls"], outcomes["serialized"]["calls"]
    _require(len(stock_calls) == len(serialized_calls) > 0, "the two planning passes simulated different batches")
    for stock_call, serialized_call in zip(stock_calls, serialized_calls, strict=True):
        _require(stock_call == serialized_call, f"{stock_call[:3]}: a simulated distribution changed bits")
    changed = _first_difference(outcomes["stock"], outcomes["serialized"])
    _require(changed is None, f"a plan or evaluation record field changed at {changed}")
    reset = next(
        choice for choices, _configuration in cases[0][2] for choice in choices if "reset" in choice.group.name
    )
    restrict = local_compute._Serialization.restrict

    def unwitnessed(self: Any, active: frozenset[int]) -> dict[str, Any]:
        errors = restrict(self, active)["errors"]
        return {
            "errors": [
                error
                for error in errors
                if "gate_qubits" not in error or any(set(qubits) <= active for qubits in error["gate_qubits"])
            ]
        }

    laws = {}
    for label in ("stock", "restricted", "unwitnessed"):
        with (
            _stock_aer() if label == "stock" else contextlib.nullcontext(),
            patch.object(local_compute._Serialization, "restrict", unwitnessed)
            if label == "unwitnessed"
            else contextlib.nullcontext(),
        ):
            simulator = live_run.noise_simulator(snapshot.name, snapshot.backend.target, snapshot.properties)
            laws[label] = [law.tolist() for laws in live_run.simulate(reset, simulator, 32768).values() for law in laws]
    _require(laws["restricted"] == laws["stock"], "the restricted reset batch changed bits at 32768 shots")
    _require(
        laws["unwitnessed"] != laws["stock"],
        "the reset batch without opset witnesses kept the stock counts, so the control no longer tests them",
    )


@contextlib.contextmanager
def _stock_aer() -> Any:
    """SerializedNoiseSimulator with AerSimulator's own per-run serialization and noise assembly."""
    from qiskit_aer import AerSimulator

    with (
        patch.object(local_compute.SerializedNoiseSimulator, "_execute_circuits", AerSimulator._execute_circuits),
        patch.object(
            local_compute.SerializedNoiseSimulator, "_assemble_noise_model", AerSimulator._assemble_noise_model
        ),
    ):
        yield


def _verify_serialized_noise_only() -> None:
    with (
        patch.object(live_run, "QiskitRuntimeService", _forbid_service),
        patch.object(live_run, "configure_sampler", _forbid_service),
    ):
        _service, snapshot = _fixture()
        _verify_serialized_noise(snapshot)
    print(
        "QPU planning: one retained noise serialization per snapshot model, restricted to each batch's qubits with "
        "opset witnesses, and the skipped empty noise-pass run reproduce every simulated distribution, plan and "
        "evaluation record of the per-run Aer path; dropping the witnesses changes the reset batch's counts"
    )


def _forbid_service(*args: Any, **kwargs: Any) -> Any:
    del args, kwargs
    raise RuntimeError("credential-free planning contract reached a RuntimeService constructor")


def _verify() -> None:
    with (
        patch.object(live_run, "QiskitRuntimeService", _forbid_service),
        patch.object(live_run, "configure_sampler", _forbid_service),
    ):
        service, snapshot = _fixture()
        choices, configuration = _verify_family_layouts(snapshot)
        _verify_heterogeneous_measurement_duration()
        _verify_window_control_durations(snapshot)
        _verify_budget_reservation(choices)
        _verify_mixed_noise_batch(choices)
        metadata = _verify_optimizer(snapshot, choices, configuration)
        _verify_approval_mutations(choices, metadata)
        _verify_rep_delay_charge(snapshot, choices, configuration)
        _verify_cli_approval_boundary()
        _verify_precision_defaults()
        _verify_compute_boundary()
        _verify_usage_accounting()
        _verify_infeasible_archive(service, choices, configuration)
        _verify_unrouted_family_diagnostics(service)
        _verify_coherence_readout(snapshot)
        _verify_patch_selection(snapshot)
        _verify_static_group_admission(service, snapshot)
        _verify_state_prep_family()
        _verify_prep_excitation()
    _verify_control_timing()
    with patch.object(live_run, "QiskitRuntimeService", _forbid_service):
        _verify_rep_delay_range()
        _verify_rep_delay_approval()
    print(
        "QPU planning: matching, calibrated timing, budgets, shot optimization, "
        "approval, infeasible archives, unrouted rejection diagnostics, coherence readout maps, calibrated "
        "patch selection and the requested repetition delay checked"
    )


def _verify_prep_excitation_only() -> None:
    with (
        patch.object(live_run, "QiskitRuntimeService", _forbid_service),
        patch.object(live_run, "configure_sampler", _forbid_service),
    ):
        _verify_prep_excitation()
    print(
        "QPU planning: --prep-excitation refuses outside the N21 families and [0, 1), joins the design settings "
        "only when declared, and enters the sampled model and the exact law alike"
    )


def _verify_state_prep_only() -> None:
    with (
        patch.object(live_run, "QiskitRuntimeService", _forbid_service),
        patch.object(live_run, "configure_sampler", _forbid_service),
    ):
        _verify_state_prep_family()
    print(
        "QPU planning: state-prep-control pins each arm to its named qubit, fuses two static PUBs and one "
        "dynamic PUB over every qubit, refuses the retained layout off its backend, admits 8192 shots and drops "
        "tiers above max_shots; x_history alone fuses one dynamic measure-then-X PUB in its own job and refuses any "
        "other arm beside it"
    )


def _verify_rep_delay_only() -> None:
    with (
        patch.object(live_run, "QiskitRuntimeService", _forbid_service),
        patch.object(live_run, "configure_sampler", _forbid_service),
    ):
        _service, snapshot = _fixture()
        choices, configuration = _verify_family_layouts(snapshot)
        _verify_rep_delay_charge(snapshot, choices, configuration)
    with patch.object(live_run, "QiskitRuntimeService", _forbid_service):
        _verify_rep_delay_range()
        _verify_rep_delay_approval()
    print(
        "QPU planning: --rep-delay refuses outside rep_delay_range, moves each PUB's charge per shot by the delay "
        "change, binds the policy and execution contract, and stops a changed delay or range before any job"
    )


def _verify_static_admission_only() -> None:
    with (
        patch.object(live_run, "QiskitRuntimeService", _forbid_service),
        patch.object(live_run, "configure_sampler", _forbid_service),
    ):
        service, snapshot = _fixture()
        _verify_static_group_admission(service, snapshot)
    print("QPU planning: a static group with a measure-then-gate member writes no planned record")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--static-group-admission", action="store_true", help="run only the static-group admission contract"
    )
    parser.add_argument("--rep-delay", action="store_true", help="run only the requested repetition-delay contracts")
    parser.add_argument("--state-prep", action="store_true", help="run only the state-prep-control planning contract")
    parser.add_argument(
        "--prep-excitation", action="store_true", help="run only the declared initial-excitation contracts"
    )
    parser.add_argument(
        "--serialized-noise",
        action="store_true",
        help="run only the retained noise-serialization equivalence contract",
    )
    parsed = parser.parse_args()
    if parsed.serialized_noise:
        _verify_serialized_noise_only()
    elif parsed.static_group_admission:
        _verify_static_admission_only()
    elif parsed.rep_delay:
        _verify_rep_delay_only()
    elif parsed.state_prep:
        _verify_state_prep_only()
    elif parsed.prep_excitation:
        _verify_prep_excitation_only()
    else:
        _verify()
