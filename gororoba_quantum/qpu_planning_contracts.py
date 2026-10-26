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
from collections.abc import Callable
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

import numpy as np
from qiskit.circuit import Delay, Measure
from qiskit.transpiler import InstructionProperties, Target
from qiskit_ibm_runtime.fake_provider import FakeFez, FakePrague

import diagnostic_experiments
import live_run
import local_compute
import native_preflight
import qpe_diagnostics
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
    _require(
        len(rca_choice.isas) == 14 and rca_configuration.get("window_sweep") is True,
        "N=21 window family lost an arm or the window sweep",
    )
    _require(
        {pub.kind for pub in live_run.execution_pubs([rca_choice])} == {"dynamic"},
        "N=21 window family crossed execution kinds",
    )
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
        long_delays = [
            int(instruction.operation.duration)
            for instruction in arms[f"n21_orbit_window_delay_long_{arm}"].data
            if instruction.operation.name == "delay"
        ]
        _require(
            2 * rca_configuration["window_delay_dt"] in long_delays,
            f"the long window delay {long_delays} of the {arm} arm is not twice window_delay_dt",
        )
    for quadrature in ("x", "y"):
        measured = ops(f"n21_spectator_measured_{quadrature}")
        reference = arms[f"n21_spectator_reset_only_{quadrature}"]
        _require(
            measured.get("measure") == 2 and measured.get("reset") == 1,
            f"the measured {quadrature} spectator lost its control readout or reset: {measured}",
        )
        _require(
            dict(reference.count_ops()).get("measure") == 1
            and rca_configuration["window_delay_dt"]
            in [int(i.operation.duration) for i in reference.data if i.operation.name == "delay"],
            f"the reset_only {quadrature} spectator does not idle the control's measure duration",
        )
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
    sites = qpu_planning.orbit_sites(qpu_planning.control_sites(live_run, choice.isas), choice.group.members)
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
    _require(
        qpu_planning.orbit_sites(qpu_planning.control_sites(live_run, resized.isas), resized.group.members) == sites,
        "the resized arms moved their measure sites",
    )


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
    default_rep_delay: float | None = None

    def configuration(self) -> Any:
        configuration = super().configuration()
        if self.rep_delay_range is not None:
            configuration.rep_delay_range = list(self.rep_delay_range)
        if self.default_rep_delay is not None:
            configuration.default_rep_delay = self.default_rep_delay
        return configuration


def _verify_rep_delay_range() -> None:
    """--rep-delay outside rep_delay_range refuses in the CLI, the planner, the charge model and the Sampler."""
    backend = _RangeBackend("rep_delay_fixture", FakeFez())
    low, high = backend.configuration().rep_delay_range
    _require(qpu_planning.repetition_delay(backend) == 0.00025, "the default repetition delay moved")
    _require(qpu_planning.repetition_delay(backend, 0.00005) == 0.00005, "an in-range request was not honored")
    _require(qpu_planning.repetition_delay(backend, 20e-6) == 20e-6, "the Heron floor itself was refused")
    _require(
        (backend.configuration().processor_type or {}).get("family") == "Heron",
        "the range fixture lost its Heron processor family",
    )
    for below in (0.0, 19e-6):
        try:
            qpu_planning.repetition_delay(backend, below)
        except ValueError:
            pass
        else:
            raise RuntimeError(f"the charge model accepted a repetition delay {below} below the Heron floor")
        _require(
            bool(qpu_planning.repetition_delay_violations(backend, below, None)),
            f"a repetition delay {below} below the Heron floor raised no violation",
        )
    low_default = _RangeBackend("rep_delay_low_default", FakeFez())
    low_default.default_rep_delay = 10e-6
    try:
        qpu_planning.repetition_delay(low_default)
    except ValueError as error:
        _require("backend default" in str(error), f"a low backend default refused for another reason: {error}")
    else:
        raise RuntimeError("a backend default below the Heron floor was admitted without a request")
    _require(qpu_planning.repetition_delay(low_default, 20e-6) == 20e-6, "a request at the floor was refused")
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


class _SmallHeronBackend(_ProbeBackend):
    """FakePrague, 33 qubits with native CZ, carrying FakeFez's repetition-rate configuration."""

    def configuration(self) -> Any:
        configuration = super().configuration()
        heron = FakeFez().configuration()
        for name in ("dynamic_reprate_enabled", "default_rep_delay", "rep_delay_range", "max_shots"):
            setattr(configuration, name, getattr(heron, name))
        return configuration


class _DynamicHeronBackend(_SmallHeronBackend):
    """_SmallHeronBackend whose Target also carries if_else, so dynamic families route on it."""

    def __init__(self, name: str) -> None:
        from qiskit.circuit import IfElseOp

        backend = FakePrague()
        backend.target.add_instruction(IfElseOp, name="if_else")
        super().__init__(name, cast(Any, backend))


class _SimulationForbidden(RuntimeError):
    """A reused submission reached a noise simulation."""


SUBMIT_REUSE_PHASES = ("full", "moved", "device", "changed")


def _submit_reuse_case(
    name: str, argv: list[str], directory: Path, phases: tuple[str, ...] = SUBMIT_REUSE_PHASES
) -> None:
    """One approved dry run and its reuse submission, then the selected full-path and refused submissions through
    live_run.main.

    Every discovery reads a newly republished calibration stamp, so the
    preflight accepts a timestamp-only change and the refresh before the
    first batch rebuilds the plan; a shifted readout value on a placed qubit
    stands for a moved value. Each phase reads only the approved record and
    the reuse run's PUB bytes, so a subset of phases checks the same contracts
    as the whole sequence.
    """
    _require(set(phases) <= set(SUBMIT_REUSE_PHASES), f"{name}: unknown reuse phases {phases}")
    from runtime_contracts import _ShiftedReadout

    out = directory / name
    with redirect_stdout(io.StringIO()):
        status = live_run.main([*argv, "--out", str(out / "dry")])
    dry_runs = list((out / "dry").iterdir())
    _require(status == 0 and len(dry_runs) == 1, f"{name}: the dry run exited {status}")
    approved = dry_runs[0]
    record_sha = hashlib.sha256((approved / "record.json").read_bytes()).hexdigest()
    approved_record = json.loads((approved / "record.json").read_text())
    _require(approved_record["state"] == "planned", f"{name}: the dry run left {approved_record['state']}")
    measured = sorted(
        int(key.split(":")[1]) for key in approved_record["groups"][0]["calibration_fingerprint"] if key[:4] == "e10:"
    )
    _require(bool(measured), f"{name}: the approved group binds no readout value")
    qubit = measured[0]
    original_snapshot = live_run.take_snapshot

    def rolled(after: int, shift_after: int | None) -> Any:
        calls = 0

        def take(service_: Any, backend_name: str, operator_excluded: Any = ()) -> Any:
            nonlocal calls
            calls += 1
            snapshot = original_snapshot(service_, backend_name, operator_excluded)
            if calls > after:
                snapshot.calibration = f"2099-01-01T00:{calls:02d}:00+00:00"
            if shift_after is not None and calls > shift_after:
                snapshot.properties = _ShiftedReadout(snapshot.properties, qubit)
            return snapshot

        return patch.object(live_run, "take_snapshot", take)

    def forbidden(*_args: Any, **_kwargs: Any) -> Any:
        raise _SimulationForbidden("a noise simulation ran")

    def submit(
        label: str,
        extra: list[str],
        shift_after: int | None,
        *,
        reuse: bool,
        simulate: bool,
        republish: bool = True,
    ) -> tuple[int, dict[str, Any], list[bytes]]:
        sent: list[bytes] = []

        def capture(circuits: list[Any]) -> None:
            buffer = io.BytesIO()
            live_run.qpy.dump(circuits, buffer)
            sent.append(buffer.getvalue())

        def sampler(
            backend_: Any,
            kind: str,
            twirl: bool,
            dd: str | None,
            tags: list[str],
            shots: int = 4096,
            max_execution_seconds: int | None = None,
            *,
            rep_delay: float | None = None,
        ) -> Any:
            del backend_, twirl, dd, rep_delay
            return _ProbeSampler(kind, tags, shots, capture, None, max_execution_seconds)

        (approved / live_run.APPROVAL_CONSUMED_FILE).unlink(missing_ok=True)
        target = out / label
        patches = [
            rolled(0 if republish else 1 << 30, shift_after),
            patch.object(live_run, "configure_sampler", sampler),
        ]
        if not simulate:
            patches += [
                patch.object(live_run, "simulate", forbidden),
                patch.object(live_run, "noise_simulator", forbidden),
                patch.object(local_compute, "run", forbidden),
            ]
        if not reuse:
            patches.append(patch.object(live_run, "_reuse_context", lambda _args: None))
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            for active in patches:
                active.start()
            try:
                code = live_run.main(
                    [
                        *argv,
                        *extra,
                        "--out",
                        str(target),
                        "--submit",
                        "--approved-record",
                        str(approved),
                        "--approved-record-sha256",
                        record_sha,
                    ]
                )
            finally:
                for active in reversed(patches):
                    active.stop()
        written = [json.loads(path.read_text()) for path in target.glob("*/record.json")]
        _require(len(written) == 1, f"{name} {label}: wrote {len(written)} records")
        return code, written[0], sent

    # Reuse: no planning or evaluation simulation, and a timestamp-only
    # republish at the refresh rebuilds through the approved design again.
    code, reused, reused_bytes = submit("reuse", [], None, reuse=True, simulate=False)
    _require(code == 0 and reused["state"] == "submitted", f"{name}: the reuse run left {reused['state']}")
    _require(reused["approved_record"]["mismatches"] == [], f"{name}: {reused['approved_record']['mismatches']}")
    _require(bool(reused_bytes), f"{name}: the reuse run sent nothing")
    reuse_log = reused["prediction_reuse"]
    _require(
        reuse_log["predictions"]["reused"] and reuse_log["record_sha256"] == record_sha,
        f"{name}: predictions were not reused: {reuse_log}",
    )
    family = "family_configuration" in approved_record
    if family:
        _require(reuse_log["design"]["reused"], f"{name}: the design was not reused: {reuse_log}")
        refresh = reused["revalidation"][0]
        _require(
            refresh["rebuilt"] and refresh["prediction_reuse"]["design"]["reused"],
            f"{name}: the refresh rebuilt without the approved design: {refresh}",
        )
    _require(
        {group["calibration"] for group in reused["groups"]} == {"2099-01-01T00:01:00+00:00"},
        f"{name}: reused groups keep a stale calibration identity",
    )

    if "full" in phases:
        _submit_full_path(name, submit, reused, reused_bytes)
    if "moved" in phases:
        _submit_moved_values(name, submit, approved, family, qubit)
    if "device" in phases:
        _submit_device_route(name, submit, family, reused_bytes)
    if "changed" in phases:
        _submit_changed_inputs(name, submit, family)


SubmitReuse = Callable[..., tuple[int, dict[str, Any], list[bytes]]]


def _submit_full_path(name: str, submit: SubmitReuse, reused: dict[str, Any], reused_bytes: list[bytes]) -> None:
    """The full path under the same republish sends the reuse run's PUB bytes and reaches its verdict; its fresh
    simulation reproduces the reused predictions."""
    code, full, full_bytes = submit("full", [], None, reuse=False, simulate=True)
    _require(code == 0 and full["state"] == "submitted", f"{name}: the full path left {full['state']}")
    _require(full["approved_record"]["mismatches"] == [], f"{name}: {full['approved_record']['mismatches']}")
    _require("prediction_reuse" not in full or not full["prediction_reuse"], f"{name}: the full path reused")
    _require(full_bytes == reused_bytes, f"{name}: reuse and full path sent different PUB bytes")
    unbound = {"noise_model_calibration"}
    for fresh, copied in zip(full["groups"], reused["groups"], strict=True):
        _require(
            {k: v for k, v in fresh.items() if k not in unbound}
            == {k: v for k, v in copied.items() if k not in unbound},
            f"{name} {fresh['group']}: the fresh simulation differs from the reused predictions",
        )
    for key in live_run.DESIGN_RECORD_FIELDS:
        if key != "local_simulation_batches":
            _require(full.get(key) == reused.get(key), f"{name}: the full path's {key} differs from the reused one")
    for key in ("shots", "pub_shots", "execution_pubs", "execution_contract", "budget_plan"):
        _require(full.get(key) == reused.get(key), f"{name}: the full path's {key} differs from the reused one")


def _submit_moved_values(name: str, submit: SubmitReuse, approved: Path, family: bool, qubit: int) -> None:
    """A moved value refuses at the preflight, at the refresh and at the batch, and consumes no approval."""
    for shift_after, where in ((0, "preflight"), (1, "refresh"), (2, "batch")):
        code, moved, sent = submit(f"moved-{where}", [], shift_after, reuse=True, simulate=where != "preflight")
        _require(
            code == 1 and moved["state"] == "approval_required" and not sent,
            f"{name}: a value moved at the {where} left {moved['state']} with {len(sent)} jobs",
        )
        _require(not (approved / live_run.APPROVAL_CONSUMED_FILE).exists(), f"{name}: the {where} refusal consumed it")
        if where == "refresh" and family:
            blockers = moved["revalidation"][0]["prediction_reuse"]["design"]["blockers"]
            _require(any(f"e10:{qubit}" in b for b in blockers), f"{name}: the refresh reused moved values {blockers}")


def _submit_device_route(name: str, submit: SubmitReuse, family: bool, reused_bytes: list[bytes]) -> None:
    """An approved batch whose device depended on the host's GPU re-plans through the full path and sends the
    reuse run's PUB bytes, which the full-path phase equates with the full path's."""
    with patch.object(local_compute, "host_independent_route", lambda _batch: "routed by GPU availability"):
        code, routed, routed_bytes = submit("device", [], None, reuse=True, simulate=True)
    _require(code == 0 and routed["state"] == "submitted", f"{name}: the device fallback left {routed['state']}")
    _require(
        not routed["prediction_reuse"]["predictions"]["reused"]
        and (not family or not routed["prediction_reuse"]["design"]["reused"]),
        f"{name}: a host-dependent device route reused the approved predictions",
    )
    _require(routed_bytes == reused_bytes, f"{name}: the device fallback sent other PUB bytes than the reuse run")


def _submit_changed_inputs(name: str, submit: SubmitReuse, family: bool) -> None:
    """A changed seed or source digest falls back to the full path, which refuses exactly as before."""
    changes: tuple[tuple[str, list[str], str, Any], ...] = (
        ("seed", ["--seeds", "2"], "policy differs", None),
        ("digest", [], "experiment_digest differs", patch.object(live_run, "experiment_digest", lambda: "0" * 64)),
    )
    for label, extra, mismatch, patched in changes:
        if patched is not None:
            patched.start()
        try:
            # Without a republish the refresh keeps the plan, so the
            # comparison alone decides.
            code, changed, sent = submit(label, extra, None, reuse=True, simulate=True, republish=False)
        finally:
            if patched is not None:
                patched.stop()
        _require(
            code == 1 and changed["state"] == "approval_required" and not sent,
            f"{name}: a changed {label} left {changed['state']}",
        )
        _require(
            mismatch in changed["approved_record"]["mismatches"],
            f"{name}: a changed {label} refused for {changed['approved_record']['mismatches']}",
        )
        _require(
            not changed["prediction_reuse"]["predictions"]["reused"]
            and (not family or not changed["prediction_reuse"]["design"]["reused"]),
            f"{name}: a changed {label} reused the approved predictions",
        )


# Independent phase sets of the heralded reuse contract; ci/gates.json runs each as its own case of core-570, and
# each case repeats the approved dry run and its reuse submission.
SUBMIT_REUSE_HERALD_CASES: dict[str, tuple[str, ...]] = {
    "reuse_and_full_path": ("full",),
    "moved_value_refusals": ("moved",),
    "device_route_fallback": ("device",),
    "changed_input_refusals": ("changed",),
}


def _verify_submit_reuse_herald(cases: list[str] | None = None) -> None:
    """A heralded n21-orbit-rca submission reuses its approved design and predictions without simulating.

    approved_family_design rebuilds the family contracts with the herald
    configuration (qpu_planning.contract_configuration); four-outcome terms
    would differ from the approved 64-outcome ones and send the submission
    through the noise simulation, which the reuse case forbids.
    """
    from runtime_contracts import _FiniteQuotaService

    backend = _DynamicHeronBackend("reuse_dynamic_fixture")
    service = _FiniteQuotaService([backend])
    family = [
        "--family",
        "n21-orbit-rca",
        "--init-herald",
        "--rep-delay",
        "0.00005",
        "--optimize",
        "--shots",
        "16384",
        "--shot-tiers",
        "16384",
        "--replica-tiers",
        "1",
        "--optimizer-candidates",
        "1",
        "--model-shots",
        "32768",
        "--local-compute",
        "auto",
        "--local-compute-method",
        "density_matrix_dynamic_statevector",
        "--simulation-threads",
        "1",
        "--backends",
        backend.name,
        "--max-execution-seconds",
        "60",
        "--max-total-execution-seconds",
        "120",
    ]
    with (
        patch.object(live_run, "QiskitRuntimeService", lambda: service),
        tempfile.TemporaryDirectory(prefix="gororoba-submit-reuse-herald-") as directory,
    ):
        if cases is None:
            _submit_reuse_case("n21-orbit-rca-herald", family, Path(directory))
        for case in cases or []:
            _submit_reuse_case(f"n21-orbit-rca-herald-{case}", family, Path(directory), SUBMIT_REUSE_HERALD_CASES[case])
            print(f"QPU planning herald reuse case {case}: pass")
    if cases is not None:
        return
    print(
        "QPU planning: a heralded n21-orbit-rca submission whose inputs match the approved record reuses its "
        "lifted contracts, design and predictions without simulating, and a moved value refuses"
    )


def _verify_submit_reuse() -> None:
    """A submission reuses the approved predictions exactly when every input they read is unchanged."""
    from runtime_contracts import _FiniteQuotaService

    narrow = [{"active_input_qubits": list(range(local_compute.GPU_MIN_ACTIVE_QUBITS - 1))}]
    wide = [{"active_input_qubits": list(range(local_compute.GPU_MIN_ACTIVE_QUBITS))}]
    routes: tuple[tuple[str, str, str, dict[str, Any] | None, list[dict[str, Any]], bool], ...] = (
        ("cpu", "density_matrix", "CPU", None, wide, True),
        ("auto", "statevector", "CPU", None, wide, True),
        ("auto", "density_matrix", "CPU", None, narrow, True),
        ("auto", "density_matrix", "CPU", None, wide, False),
        ("auto", "density_matrix", "CPU", {"rejected": "memory"}, wide, False),
        ("auto", "density_matrix", "GPU", {"active_qubits": 11}, wide, False),
        ("gpu", "density_matrix", "GPU", {"active_qubits": 11}, wide, False),
    )
    for mode, method, device, admission, metadata, stable in routes:
        batch = {
            "policy": {"mode": mode},
            "method": method,
            "device": device,
            "gpu_admission": admission,
            "experiment_metadata": metadata,
        }
        _require(
            (local_compute.host_independent_route(batch) is None) == stable,
            f"host_independent_route misreads {mode} {method} on {device} with admission {admission}",
        )

    # A 33-qubit device keeps each whole-device noise model small.
    backend = _SmallHeronBackend("reuse_fixture", cast(Any, FakePrague()))
    service = _FiniteQuotaService([backend])
    with redirect_stdout(io.StringIO()):
        snapshot = live_run.take_snapshot(cast(Any, service), backend.name)
    qubits = [qubit for qubit in range(snapshot.backend.num_qubits) if qubit not in snapshot.excluded_qubits][:1]
    common = ["--backends", backend.name, "--max-execution-seconds", "60", "--max-total-execution-seconds", "120"]
    family = [
        "--family",
        "state-prep-control",
        "--layout",
        ",".join(map(str, qubits)),
        "--state-prep-arms",
        "prep0,reset",
        "--optimize",
        "--shot-tiers",
        "4096,8192",
        "--replica-tiers",
        "1",
        "--optimizer-candidates",
        "1",
        "--model-shots",
        "512",
        "--simulation-threads",
        "1",
        *common,
    ]
    groups = ["--groups", "design_c_8_1_4", "--max-replicas", "1", "--simulation-threads", "1", *common]
    with (
        patch.object(live_run, "QiskitRuntimeService", lambda: service),
        tempfile.TemporaryDirectory(prefix="gororoba-submit-reuse-") as directory,
    ):
        _submit_reuse_case("state-prep-control", family, Path(directory))
        _submit_reuse_case("groups", groups, Path(directory))
    print(
        "QPU planning: a submission whose calibration values, seeds, policy, sources and versions match the "
        "approved record reuses its design and predictions without simulating and sends the full path's PUB bytes; "
        "a moved value refuses at the preflight, refresh and batch, a batch routed by the host's GPU re-plans "
        "and sends the same bytes, and a changed seed or source digest re-plans and refuses as before"
    )


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


def _verify_window_bracket(snapshot: live_run.Snapshot) -> None:
    """Every n21-orbit-rca arm keeps work-qubit gates out of the control's measurement-and-reset window.

    The barrier-free n21-orbit-feedback pair is the negative control: its
    compiled multipliers place work-only gates inside the window, and so do
    the unbracketed arms of a pinned overlap split, whose bracketed arms keep
    the window clear (_window_bracket_split).
    """
    traces: dict[str, Any] = {}
    rca = qpu_planning.family_candidates(live_run, [snapshot], _args("n21-orbit-rca"), traces)
    _require(bool(rca), f"FakeFez rejects every N=21 window family: {traces}")
    (choice,), _configuration = rca[0]
    _require(len(choice.isas) == 14, "N=21 window family lost an arm")
    for member, isa in zip(choice.group.members, choice.isas, strict=True):
        if "_reset_only_" in member.name:
            # The reference idles in place of the measurement, so no
            # measurement opens a window.
            continue
        inside = frozenset({"delay", "x"}) if "_window_echo_" in member.name else frozenset({"delay"})
        found = qpe_diagnostics.window_bracket_violations(isa, inside)
        _require(not found, f"{member.name}: the window holds work-qubit operations {found}")
    unbracketed = qpu_planning.family_candidates(live_run, [snapshot], _args("n21-orbit-feedback"), traces)
    _require(bool(unbracketed), f"FakeFez rejects every N=21 orbit family: {traces}")
    (control,), _configuration = unbracketed[0]
    for member, isa in zip(control.group.members, control.isas, strict=True):
        _require(
            bool(qpe_diagnostics.window_bracket_violations(isa)),
            f"{member.name}: the barrier-free window holds no work-qubit operation, so the check proves nothing",
        )
    _window_bracket_split(snapshot)


PINNED_ORBIT_LAYOUT = [142, 136, 143, 144]
OVERLAP_SPLIT_MEMBERS = [
    *(
        f"n21_orbit_{variant}_{arm}"
        for variant in ("nominal", "window_delay", "window_delay_unbracketed")
        for arm in ("feedback", "no_feedback")
    ),
    *(f"n21_spectator_{kind}_{q}" for kind in ("immediate", "idle", "reset_only") for q in ("x", "y")),
]


def _overlap_split_plan(snapshot: live_run.Snapshot) -> tuple[Any, dict[str, Any]]:
    """The first pinned overlap-split candidate on snapshot and its family configuration."""
    pin = {"backend": snapshot.name, "qubits": PINNED_ORBIT_LAYOUT}
    traces: dict[str, Any] = {}
    candidates = qpu_planning.family_candidates(
        live_run, [snapshot], _args("n21-orbit-rca", pin_layout=pin, overlap_split=True), traces
    )
    _require(bool(candidates), f"FakeFez refuses the pinned overlap split: {traces.get('family_rejections')}")
    (choice,), configuration = candidates[0]
    return choice, configuration


def _window_bracket_split(snapshot: live_run.Snapshot) -> None:
    """The overlap split's bracketed arms keep the window clear and its unbracketed arms do not.

    The immediate and idle spectators measure no control and the reset_only
    one resets it before any measurement, so no measurement opens their
    window and the bracket test leaves them out.
    """
    choice, _configuration = _overlap_split_plan(snapshot)
    for member, isa in zip(choice.group.members, choice.isas, strict=True):
        if member.name.startswith("n21_spectator_"):
            continue
        found = qpe_diagnostics.window_bracket_violations(isa)
        if "_unbracketed_" in member.name:
            _require(bool(found), f"{member.name}: the unbracketed window holds no work-qubit operation")
        else:
            _require(not found, f"{member.name}: the window holds work-qubit operations {found}")


def _verify_overlap_split(snapshot: live_run.Snapshot) -> None:
    """A pinned overlap split plans its twelve members and binds the flag only when set.

    The group holds the bracketed nominal and window_delay pairs, the
    window_delay_unbracketed pair and the immediate, idle and reset_only
    spectators in X and Y, in that order; the window_delay arms of both
    kinds idle window_delay_dt, the configuration records every orbit arm's
    CZ and sx counts, and a configuration without overlap_arm rebuilds the
    ten-member nominal configuration; the unbracketed arms
    hold a work-qubit operation in the control's window and the bracketed
    ones do not; the idle spectator idles window_delay_dt + reset_dt and the
    immediate one plays no delay, each resetting the control only after
    qubit 2's readout; the configuration records
    overlap_split and reset_dt and no window_sweep, and record_groups and
    family_contracts rebuild it; the policy carries overlap_split only when
    set; live_run refuses the flag without --pin-layout or on another family,
    and the group refuses it beside window_sweep.
    """
    _require("overlap_split" not in qpu_planning.settings(_args("n21-orbit-rca")), "an absent split entered the policy")
    pin = {"backend": snapshot.name, "qubits": PINNED_ORBIT_LAYOUT}
    _require(
        qpu_planning.settings(_args("n21-orbit-rca", pin_layout=pin, overlap_split=True)).get("overlap_split") is True,
        "the policy settings drop the overlap split",
    )
    choice, configuration = _overlap_split_plan(snapshot)
    names = [member.name for member in choice.group.members]
    _require(names == OVERLAP_SPLIT_MEMBERS, f"the overlap split plans {names}")
    _require(
        configuration.get("overlap_split") is True
        and "window_sweep" not in configuration
        and type(configuration.get("reset_dt")) is int
        and configuration["reset_dt"] > 0
        and configuration.get("pin_layout") == pin
        and configuration.get("overlap_arm") == "window_delay"
        and configuration.get("orbit_gate_counts")
        == {
            member.name: {gate: int(isa.count_ops().get(gate, 0)) for gate in ("cz", "sx")}
            for member, isa in zip(choice.group.members, choice.isas, strict=True)
            if member.name in OVERLAP_SPLIT_MEMBERS[:6]
        },
        f"the overlap-split configuration reads {configuration}",
    )
    _window_bracket_split(snapshot)
    arms = dict(zip(names, choice.isas, strict=True))
    control = PINNED_ORBIT_LAYOUT[0]

    def reset_after_readout(isa: Any) -> bool:
        names = [i.operation.name for i in isa.data if i.operation.name in ("measure", "reset")]
        return names == ["measure", "reset"]

    for arm in ("feedback", "no_feedback"):
        for variant in ("window_delay", "window_delay_unbracketed"):
            isa = arms[f"n21_orbit_{variant}_{arm}"]
            delays = [int(i.operation.duration) for i in isa.data if i.operation.name == "delay"]
            _require(
                configuration["window_delay_dt"] in delays,
                f"the {variant} {arm} arm does not idle window_delay_dt: {delays}",
            )
    for quadrature in ("x", "y"):
        idle = arms[f"n21_spectator_idle_{quadrature}"]
        immediate = arms[f"n21_spectator_immediate_{quadrature}"]
        idle_delays = [
            int(i.operation.duration)
            for i in idle.data
            if i.operation.name == "delay" and idle.find_bit(i.qubits[0]).index == control
        ]
        _require(
            configuration["window_delay_dt"] + configuration["reset_dt"] in idle_delays and reset_after_readout(idle),
            f"the idle {quadrature} spectator idles {idle_delays} on the control, not measure plus reset",
        )
        _require(
            "delay" not in immediate.count_ops() and reset_after_readout(immediate),
            f"the immediate {quadrature} spectator plays a window: {dict(immediate.count_ops())}",
        )
    rebuilt = diagnostic_experiments.record_groups({"family_configuration": configuration})
    _require(
        [member.name for member in rebuilt[0].members] == names,
        "record_groups does not rebuild the overlap split",
    )
    contracts = diagnostic_experiments.family_contracts("n21-orbit-rca", 0.08, 0.05, 0.8, configuration=configuration)
    _require(
        [contract.name for contract in contracts]
        == [
            "n21_orbit_nominal_feedback_contrast",
            "n21_orbit_window_delay_feedback_contrast",
            "n21_orbit_window_delay_unbracketed_feedback_contrast",
            *(f"{name}_one" for name in OVERLAP_SPLIT_MEMBERS[6:]),
        ]
        and all(math.isclose(contract.alpha, 0.05 / 9) for contract in contracts),
        f"the overlap-split family contracts read {[contract.name for contract in contracts]}",
    )
    legacy = {key: value for key, value in configuration.items() if key not in ("overlap_arm", "orbit_gate_counts")}
    _require(
        [m.name for m in diagnostic_experiments.record_groups({"family_configuration": legacy})[0].members]
        == [
            *(f"n21_orbit_{v}_{a}" for v in ("nominal", "unbracketed") for a in ("feedback", "no_feedback")),
            *OVERLAP_SPLIT_MEMBERS[6:],
        ],
        "a configuration without overlap_arm does not build the ten-member nominal configuration",
    )
    fixture = qpu_cases._fixture()
    location = Path("results/live/fixture/record.json")
    _require(
        "--overlap-split" not in qpu_cases._reproduction_arguments(fixture, location)
        and not any("--overlap-split" in line for line in qpu_cases._scientific_case("n21-orbit-rca", fixture)),
        "a record without the split replays or describes it",
    )
    fixture["policy"]["design"]["overlap_split"] = True
    fixture["family_configuration"] = {
        **fixture.get("family_configuration", {}),
        "overlap_split": True,
        "overlap_arm": "window_delay",
        "orbit_gate_counts": configuration["orbit_gate_counts"],
    }
    case = " ".join(qpu_cases._scientific_case("n21-orbit-rca", fixture))
    counts = configuration["orbit_gate_counts"]["n21_orbit_window_delay_unbracketed_feedback"]
    bracketed_cz = configuration["orbit_gate_counts"]["n21_orbit_window_delay_feedback"]["cz"]
    _require(
        "--overlap-split" in qpu_cases._reproduction_arguments(fixture, location)
        and "--overlap-split replaces" in case
        and qpu_cases._gate_count_bias(configuration["orbit_gate_counts"]) in case
        and "not that it caused the 2026-10-13T083417 loss" in case
        and f"hold {counts['cz']} CZ and {counts['sx']} sx unbracketed" in case,
        f"a split record's written command or case text omits the split, its CZ bias or its scope: {case}",
    )
    # The bias sentence follows the recorded CZ difference in each direction.
    for unbracketed_cz, phrase in (
        (bracketed_cz - 2, "plays 2 CZ fewer than its bracketed twin"),
        (bracketed_cz, "biases window_overlap_loss in neither direction"),
        (bracketed_cz + 3, "plays 3 CZ more than its bracketed twin"),
    ):
        varied = {
            "n21_orbit_window_delay_feedback": {"cz": bracketed_cz, "sx": 0},
            "n21_orbit_window_delay_unbracketed_feedback": {"cz": unbracketed_cz, "sx": 0},
        }
        fixture["family_configuration"]["orbit_gate_counts"] = varied
        varied_case = " ".join(qpu_cases._scientific_case("n21-orbit-rca", fixture))
        _require(phrase in varied_case, f"the case text misstates a CZ difference of {bracketed_cz - unbracketed_cz}")
    if bracketed_cz - counts["cz"] > 0:
        _require("biases window_overlap_loss against a pass" in case, "the recorded CZ deficit reads unbiased")
    try:
        diagnostic_experiments.n21_orbit_rca_group(415, 502, window_sweep=True, overlap_split=True, reset_dt=520)
    except ValueError:
        pass
    else:
        raise RuntimeError("the group accepted overlap_split beside window_sweep")
    ceilings = ["--max-execution-seconds", "10", "--max-total-execution-seconds", "10"]
    for argv, message in (
        (["--family", "n21-orbit-rca", "--overlap-split", *ceilings], "--overlap-split requires --pin-layout"),
        (
            ["--family", "n21-orbit-feedback", "--overlap-split", *ceilings],
            "--overlap-split applies to the n21-orbit-rca family only",
        ),
    ):
        stderr = io.StringIO()
        with redirect_stderr(stderr), contextlib.suppress(SystemExit):
            live_run.main(argv)
        _require(message in stderr.getvalue(), f"live_run {argv} reads {stderr.getvalue()!r}, not {message!r}")


GROUND_CONTROL_SPLIT_MEMBERS = [
    f"n21_spectator_{kind}_{q}" for kind in ("immediate", "idle", "idle_ground") for q in ("x", "y")
]


def _verify_ground_control_split(snapshot: live_run.Snapshot) -> None:
    """A pinned ground-control split plans its six spectators and binds the flag only when set.

    The group holds the immediate, idle and idle_ground spectators in X and
    Y and no orbit arm; idle and idle_ground idle window_delay_dt + reset_dt
    on the pinned control, idle_ground plays no gate on the control before
    that idle, so the control stays in |0>, and every arm resets the control
    only after qubit 2's readout; the configuration records
    ground_control_split and reset_dt and neither window_sweep nor
    overlap_split, and record_groups and family_contracts rebuild it; the
    policy carries ground_control_split only when set; a record's written
    command and case replay it only when set; live_run refuses the flag
    without --pin-layout, on another family or beside --overlap-split, and
    the group refuses it beside window_sweep or overlap_split.
    """
    _require(
        "ground_control_split" not in qpu_planning.settings(_args("n21-orbit-rca")),
        "an absent ground-control split entered the policy",
    )
    pin = {"backend": snapshot.name, "qubits": PINNED_ORBIT_LAYOUT}
    arguments = _args("n21-orbit-rca", pin_layout=pin, ground_control_split=True)
    _require(
        qpu_planning.settings(arguments).get("ground_control_split") is True,
        "the policy settings drop the ground-control split",
    )
    traces: dict[str, Any] = {}
    candidates = qpu_planning.family_candidates(live_run, [snapshot], arguments, traces)
    _require(bool(candidates), f"FakeFez refuses the pinned ground split: {traces.get('family_rejections')}")
    (choice,), configuration = candidates[0]
    names = [member.name for member in choice.group.members]
    _require(names == GROUND_CONTROL_SPLIT_MEMBERS, f"the ground-control split plans {names}")
    _require(
        configuration.get("ground_control_split") is True
        and "window_sweep" not in configuration
        and "overlap_split" not in configuration
        and type(configuration.get("reset_dt")) is int
        and configuration["reset_dt"] > 0
        and configuration.get("pin_layout") == pin,
        f"the ground-control-split configuration reads {configuration}",
    )
    arms = dict(zip(names, choice.isas, strict=True))
    control = PINNED_ORBIT_LAYOUT[0]
    window = configuration["window_delay_dt"] + configuration["reset_dt"]

    def control_ops(isa: Any) -> list[tuple[str, int | None]]:
        return [
            (i.operation.name, int(i.operation.duration) if i.operation.name == "delay" else None)
            for i in isa.data
            if i.operation.name != "barrier" and any(isa.find_bit(q).index == control for q in i.qubits)
        ]

    for quadrature in ("x", "y"):
        immediate = control_ops(arms[f"n21_spectator_immediate_{quadrature}"])
        idle = control_ops(arms[f"n21_spectator_idle_{quadrature}"])
        ground = control_ops(arms[f"n21_spectator_idle_ground_{quadrature}"])
        _require(
            ("delay", window) in idle and idle[-1] == ("reset", None),
            f"the idle {quadrature} spectator plays {idle} on the control, not measure plus reset then a reset",
        )
        _require(
            ground == [("delay", window), ("reset", None)],
            f"the idle_ground {quadrature} spectator plays {ground} on the control, not an idle in |0> and a reset",
        )
        _require(
            idle[: idle.index(("delay", window))] != [],
            f"the idle {quadrature} spectator prepares no |+> on the control: {idle}",
        )
        _require(
            not any(name == "delay" for name, _ in immediate) and immediate[-1] == ("reset", None),
            f"the immediate {quadrature} spectator plays a window on the control: {immediate}",
        )
    rebuilt = diagnostic_experiments.record_groups({"family_configuration": configuration})
    _require(
        [member.name for member in rebuilt[0].members] == names,
        "record_groups does not rebuild the ground-control split",
    )
    contracts = diagnostic_experiments.family_contracts("n21-orbit-rca", 0.08, 0.05, 0.8, configuration=configuration)
    _require(
        [contract.name for contract in contracts] == [f"{name}_one" for name in GROUND_CONTROL_SPLIT_MEMBERS]
        and all(math.isclose(contract.alpha, 0.05 / 6) for contract in contracts),
        f"the ground-control-split family contracts read {[contract.name for contract in contracts]}",
    )
    fixture = qpu_cases._fixture()
    location = Path("results/live/fixture/record.json")
    _require(
        "--ground-control-split" not in qpu_cases._reproduction_arguments(fixture, location)
        and not any("--ground-control-split" in line for line in qpu_cases._scientific_case("n21-orbit-rca", fixture)),
        "a record without the ground-control split replays or describes it",
    )
    fixture["policy"]["design"]["ground_control_split"] = True
    fixture["family_configuration"] = {**fixture.get("family_configuration", {}), "ground_control_split": True}
    case = " ".join(qpu_cases._scientific_case("n21-orbit-rca", fixture))
    _require(
        "--ground-control-split" in qpu_cases._reproduction_arguments(fixture, location)
        and "--ground-control-split plans only qubit-2 spectators" in case,
        f"a ground-control-split record's written command or case text omits the split: {case}",
    )
    for sweep, split in ((True, False), (False, True)):
        try:
            diagnostic_experiments.n21_orbit_rca_group(
                415, 502, window_sweep=sweep, overlap_split=split, reset_dt=520, ground_control_split=True
            )
        except ValueError:
            continue
        raise RuntimeError(
            f"the group accepted ground_control_split beside window_sweep {sweep}, overlap_split {split}"
        )
    ceilings = ["--max-execution-seconds", "10", "--max-total-execution-seconds", "10"]
    pinned = ["--pin-layout", f"{snapshot.name}:{','.join(str(q) for q in PINNED_ORBIT_LAYOUT)}"]
    for argv, message in (
        (
            ["--family", "n21-orbit-rca", "--ground-control-split", *ceilings],
            "--ground-control-split requires --pin-layout",
        ),
        (
            ["--family", "n21-orbit-feedback", "--ground-control-split", *ceilings],
            "--ground-control-split applies to the n21-orbit-rca family only",
        ),
        (
            ["--family", "n21-orbit-rca", "--ground-control-split", "--overlap-split", *pinned, *ceilings],
            "--ground-control-split and --overlap-split are separate",
        ),
        (
            ["--family", "n21-orbit-rca", "--ground-control-split", *pinned, *ceilings],
            "--ground-control-split requires --init-herald",
        ),
    ):
        stderr = io.StringIO()
        with redirect_stderr(stderr), contextlib.suppress(SystemExit):
            live_run.main(argv)
        _require(message in stderr.getvalue(), f"live_run {argv} reads {stderr.getvalue()!r}, not {message!r}")


RAMSEY_WINDOWS = [1, 2, 3, 4, 5, 6]


def _verify_ground_ramsey_sweep(snapshot: live_run.Snapshot) -> None:
    """A pinned ground Ramsey sweep plans immediate and idle_ground at each multiple, and binds the multiples.

    The group holds immediate and idle_ground at each idle multiple m in X
    and Y, no idle arm and no orbit arm; idle_ground at m plays exactly a
    delay of m * (window_delay_dt + reset_dt) and a reset on the pinned
    control, and qubit 2 (the pinned spectator) plays only its preparation
    and basis change around a bare idle, so no decoupling pulse turns the
    Ramsey into an echo; no ISA holds a classically conditioned block; the
    configuration and policy carry the sorted multiples, record_groups and
    family_contracts rebuild them, the written command replays them, and
    live_run refuses the multiples without --ground-control-split and a
    single or repeated multiple.
    """
    _require(
        "ramsey_windows" not in qpu_planning.settings(_args("n21-orbit-rca")),
        "an absent ground Ramsey sweep entered the policy",
    )
    pin = {"backend": snapshot.name, "qubits": PINNED_ORBIT_LAYOUT}
    arguments = _args(
        "n21-orbit-rca", pin_layout=pin, ground_control_split=True, init_herald=True, ramsey_windows=RAMSEY_WINDOWS
    )
    _require(
        qpu_planning.settings(arguments).get("ramsey_windows") == RAMSEY_WINDOWS,
        "the policy settings drop the ground Ramsey multiples",
    )
    scripts = Path(qpu_planning.__file__).resolve().parents[1] / "scripts"
    bound = qpu_planning.settings(arguments).get("ramsey_analyzer_closure")
    expected_files = {
        f"scripts/{name}": hashlib.sha256((scripts / name).read_bytes()).hexdigest()
        for name in ("n21_orbit_rca.py", "n21_spectator_ramsey.py")
    }
    _require(
        isinstance(bound, dict) and bound.get("files") == expected_files,
        f"the policy binds the analyzer closure {bound}, not {sorted(expected_files)} at their bytes",
    )
    with tempfile.TemporaryDirectory() as scratch:
        approved_dir = Path(scratch) / "approved"
        approved_dir.mkdir()
        approved: dict[str, Any] = {
            "state": "planned",
            "policy": {"design": qpu_planning.settings(arguments)},
            "groups": [],
        }
        (approved_dir / "record.json").write_text(json.dumps(approved))
        (approved_dir / "isa.qpy").write_bytes(b"ramsey")
        qpy_digest = hashlib.sha256(b"ramsey").hexdigest()
        _require(
            not live_run.approved_record_mismatches(approved_dir, json.loads(json.dumps(approved)), qpy_digest),
            "an unchanged ground Ramsey plan differs from its own approved record",
        )
        # A copy of scripts/ whose n21_orbit_rca.py alone gains one byte.
        copied = Path(scratch) / "scripts"
        copied.mkdir()
        for name in expected_files:
            source = scripts / Path(name).name
            (copied / source.name).write_bytes(source.read_bytes())
        (copied / "n21_orbit_rca.py").write_bytes((scripts / "n21_orbit_rca.py").read_bytes() + b"\n")
        with (
            patch.object(qpu_planning, "SCRIPTS_DIR", copied),
            patch.object(qpu_planning, "RAMSEY_ANALYZER", copied / "n21_spectator_ramsey.py"),
        ):
            moved = qpu_planning.settings(arguments)
        changed = {**approved, "policy": {"design": moved}}
        _require(
            moved["ramsey_analyzer_closure"]["files"]["scripts/n21_spectator_ramsey.py"]
            == expected_files["scripts/n21_spectator_ramsey.py"]
            and "policy differs" in live_run.approved_record_mismatches(approved_dir, changed, qpy_digest),
            "a change to n21_orbit_rca.py alone leaves the approved record's policy equal",
        )
    traces: dict[str, Any] = {}
    candidates = qpu_planning.family_candidates(live_run, [snapshot], arguments, traces)
    _require(bool(candidates), f"FakeFez refuses the pinned ground Ramsey sweep: {traces.get('family_rejections')}")
    (choice,), configuration = candidates[0]
    names = [member.name for member in choice.group.members]
    expected = [f"n21_spectator_immediate_{q}" for q in ("x", "y")] + [
        f"n21_spectator_idle_ground_w{m}_{q}" for m in RAMSEY_WINDOWS for q in ("x", "y")
    ]
    _require(names == expected, f"the ground Ramsey sweep plans {names}")
    _require(
        configuration.get("ground_control_split") is True
        and configuration.get("ramsey_windows") == RAMSEY_WINDOWS
        and configuration.get("init_herald") is True
        and configuration.get("pin_layout") == pin,
        f"the ground Ramsey configuration reads {configuration}",
    )
    control, spectator = PINNED_ORBIT_LAYOUT[0], PINNED_ORBIT_LAYOUT[2]
    window = configuration["window_delay_dt"] + configuration["reset_dt"]

    def wire_ops(isa: Any, wire: int) -> list[tuple[str, int | None]]:
        return [
            (i.operation.name, int(i.operation.duration) if i.operation.name == "delay" else None)
            for i in isa.data
            if i.operation.name != "barrier" and any(isa.find_bit(q).index == wire for q in i.qubits)
        ]

    for name, isa in zip(names, choice.isas, strict=True):
        _require(
            not any(i.operation.name in ("if_else", "while_loop", "for_loop", "switch_case") for i in isa.data),
            f"{name} holds a control-flow block",
        )
        multiple = 0 if "_immediate_" in name else int(name.rsplit("_w", 1)[1].split("_")[0])
        ops = wire_ops(isa, control)
        if multiple:
            _require(
                ops[-2:] == [("delay", multiple * window), ("reset", None)]
                and not any(op in ("sx", "x", "rz") for op, _ in ops[: len(ops) - 2] if op != "measure"),
                f"{name} plays {ops} on the control, not a herald, an idle in |0> and a reset",
            )
        # The barriers alone hold the spectator across the control's idle,
        # so any delay instruction on it is an inserted idle the exposure
        # does not name, and any further pulse is a decoupling pulse.
        program = [op for op, _ in wire_ops(isa, spectator) if op != "rz"]
        _require(
            program == ["measure", "sx", "sx", "measure"],
            f"{name} plays {program} on the spectator, not a herald, a preparation, a basis change and a readout",
        )
    rebuilt = diagnostic_experiments.record_groups({"family_configuration": configuration})
    _require([member.name for member in rebuilt[0].members] == names, "record_groups does not rebuild the ground sweep")
    contracts = diagnostic_experiments.family_contracts("n21-orbit-rca", 0.08, 0.05, 0.8, configuration=configuration)
    _require(
        [contract.name for contract in contracts] == [f"{name}_one" for name in expected],
        f"the ground Ramsey family contracts read {[contract.name for contract in contracts]}",
    )
    fixture = qpu_cases._fixture()
    location = Path("results/live/fixture/record.json")
    fixture["policy"]["design"]["ground_control_split"] = True
    fixture["policy"]["design"]["ramsey_windows"] = RAMSEY_WINDOWS
    fixture["family_configuration"] = {
        **fixture.get("family_configuration", {}),
        "ground_control_split": True,
        "ramsey_windows": RAMSEY_WINDOWS,
    }
    replay = qpu_cases._reproduction_arguments(fixture, location)
    case = " ".join(qpu_cases._scientific_case("n21-orbit-rca", fixture))
    _require(
        "--ramsey-windows" in replay
        and replay[replay.index("--ramsey-windows") + 1] == "1,2,3,4,5,6"
        and "--ramsey-windows is the ground Ramsey sweep" in case,
        f"a ground Ramsey record's written command or case text omits the multiples: {replay}",
    )
    try:
        diagnostic_experiments.n21_orbit_rca_group(415, 502, reset_dt=520, ramsey_windows=(1, 2))
    except ValueError:
        pass
    else:
        raise RuntimeError("the group accepted ramsey_windows without ground_control_split")
    ceilings = ["--max-execution-seconds", "10", "--max-total-execution-seconds", "10"]
    pinned = ["--pin-layout", f"{snapshot.name}:{','.join(str(q) for q in PINNED_ORBIT_LAYOUT)}"]
    for argv, message in (
        (
            ["--family", "n21-orbit-rca", "--ramsey-windows", "1,2", "--init-herald", *pinned, *ceilings],
            "--ramsey-windows requires --ground-control-split",
        ),
        (
            ["--family", "n21-orbit-rca", "--ground-control-split", "--ramsey-windows", "2", *pinned, *ceilings],
            "at least two distinct positive integer multiples",
        ),
        (
            ["--family", "n21-orbit-rca", "--ground-control-split", "--ramsey-windows", "2,2", *pinned, *ceilings],
            "at least two distinct positive integer multiples",
        ),
    ):
        stderr = io.StringIO()
        with redirect_stderr(stderr), contextlib.suppress(SystemExit):
            live_run.main(argv)
        _require(message in stderr.getvalue(), f"live_run {argv} reads {stderr.getvalue()!r}, not {message!r}")


WINDOW_DOSES = [0, 3500, 7000]


def _verify_window_dose_sweep(snapshot: live_run.Snapshot) -> None:
    """A window-dose plan keeps each dose as a top-level delay on all four wires and binds the doses.

    The group holds a window_dose feedback pair at every dose and a
    window_dose_echo pair at every nonzero dose. After the transpiler, every
    qubit of a window_dose arm holds one delay of exactly the dose, and in
    a window_dose_echo arm the control and the work bit for 4 hold the dose
    and the other work bits delay a quarter, play X, delay a half, play X and
    delay a quarter; no if_else body holds a delay. The policy and the
    configuration carry the sorted doses and no window_sweep, record_groups,
    family_contracts and the written command rebuild them, a dose that
    breaks the Target's delay timing refuses the snapshot, and live_run
    refuses the flag on another family or beside another sweep.
    """
    _require("window_doses" not in qpu_planning.settings(_args("n21-orbit-rca")), "absent doses entered the policy")
    pin = {"backend": snapshot.name, "qubits": PINNED_ORBIT_LAYOUT}
    arguments = _args("n21-orbit-rca", init_herald=True, window_doses_dt=WINDOW_DOSES, pin_layout=pin)
    settings = qpu_planning.settings(arguments)
    _require(settings.get("window_doses") == WINDOW_DOSES, f"the policy binds {settings.get('window_doses')}")
    with tempfile.TemporaryDirectory() as scratch:
        approved_dir = Path(scratch)
        approved: dict[str, Any] = {"state": "planned", "policy": {"design": settings}, "groups": []}
        (approved_dir / "record.json").write_text(json.dumps(approved))
        (approved_dir / "isa.qpy").write_bytes(b"dose")
        digest = hashlib.sha256(b"dose").hexdigest()
        _require(
            not live_run.approved_record_mismatches(approved_dir, json.loads(json.dumps(approved)), digest),
            "an unchanged window-dose plan differs from its own approved record",
        )
        moved = qpu_planning.settings(_args("n21-orbit-rca", init_herald=True, window_doses_dt=[0, 3500, 7004]))
        _require(
            "policy differs"
            in live_run.approved_record_mismatches(approved_dir, {**approved, "policy": {"design": moved}}, digest),
            "a changed dose list leaves the approved record's policy equal",
        )
    traces: dict[str, Any] = {}
    candidates = qpu_planning.family_candidates(live_run, [snapshot], arguments, traces)
    _require(bool(candidates), f"FakeFez refuses the window-dose sweep: {traces.get('family_rejections')}")
    (choice,), configuration = candidates[0]
    expected = [
        qpe_diagnostics.n21_dose_name(variant, dose, feedback)
        for dose in WINDOW_DOSES
        for variant in ("window_dose", "window_dose_echo")
        if dose or variant == "window_dose"
        for feedback in (True, False)
    ]
    names = [member.name for member in choice.group.members]
    _require(names == expected, f"the window-dose sweep plans {names}")
    _require(
        configuration.get("window_doses") == WINDOW_DOSES
        and "window_sweep" not in configuration
        and configuration.get("init_herald") is True,
        f"the window-dose configuration reads {configuration}",
    )
    for name, isa in zip(names, choice.isas, strict=True):
        key = qpe_diagnostics.n21_dose_key(name)
        _require(key is not None, f"{name} is not a window-dose member")
        variant, dose, _feedback = cast(tuple[str, int, bool], key)
        for instruction in isa.data:
            if instruction.operation.name == "if_else":
                for body in instruction.operation.blocks:
                    _require(
                        not any(inner.operation.name == "delay" for inner in body.data),
                        f"{name} holds a delay inside an if_else body",
                    )
        names_in_order = [inner.operation.name for inner in isa.data]
        # The barriers bracket the control's mid-circuit measure and reset;
        # a nonzero dose opens with a full-width barrier after the reset, so
        # its delays and echo pulses start once the reset ends. Instruction
        # order on one wire is the program order, and across wires is not.
        reset = names_in_order.index("reset")
        opened = reset - names_in_order[reset::-1].index("barrier")
        closed = reset + 1
        while closed < len(names_in_order) and names_in_order[closed] in ("delay", "x", "barrier"):
            closed += 1
        tail = isa.data[reset + 1 : closed]
        first_dose = next((k for k, inner in enumerate(tail) if inner.operation.name in ("delay", "x")), None)
        if dose:
            _require(
                first_dose is not None
                and any(
                    inner.operation.name == "barrier" and len(inner.qubits) == len(PINNED_ORBIT_LAYOUT)
                    for inner in tail[:first_dose]
                ),
                f"{name} starts its dose without a full-width barrier after the reset",
            )
        window = [inner for inner in isa.data[opened + 1 : closed] if inner.operation.name in ("delay", "x")]
        programs = {
            wire: [
                (inner.operation.name, int(inner.operation.duration) if inner.operation.name == "delay" else None)
                for inner in window
                if any(isa.find_bit(q).index == wire for q in inner.qubits)
            ]
            for wire in PINNED_ORBIT_LAYOUT
        }
        plain = [("delay", dose)] if dose else []
        quarter = dose // 4
        echoed = [("delay", quarter), ("x", None), ("delay", 2 * quarter), ("x", None), ("delay", quarter)]
        # The echo moves the superposition's work bits for 1 and 16 through
        # X pulses; the control and the bit for 4, which stays in |0>, idle.
        echo_arm = variant == "window_dose_echo"
        want = {PINNED_ORBIT_LAYOUT[role]: echoed if echo_arm and role in (1, 3) else plain for role in range(4)}
        _require(programs == want, f"{name} plays {programs}, not {want}")
    rebuilt = diagnostic_experiments.record_groups({"family_configuration": configuration})
    _require([member.name for member in rebuilt[0].members] == names, "record_groups does not rebuild the doses")
    contracts = diagnostic_experiments.family_contracts("n21-orbit-rca", 0.08, 0.05, 0.8, configuration=configuration)
    _require(
        [contract.name for contract in contracts]
        == [
            f"n21_orbit_{variant}_d{dose}_feedback_contrast"
            for dose in WINDOW_DOSES
            for variant in ("window_dose", "window_dose_echo")
            if dose or variant == "window_dose"
        ]
        and all(contract.precision_half_width == 0.08 and len(contract.terms) == 2 for contract in contracts),
        f"the window-dose family contracts read {[contract.name for contract in contracts]}",
    )
    fixture = qpu_cases._fixture()
    location = Path("results/live/fixture/record.json")
    fixture["policy"]["design"]["family"] = "n21-orbit-rca"
    fixture["policy"]["design"]["window_doses"] = WINDOW_DOSES
    fixture["family_configuration"] = {
        **fixture.get("family_configuration", {}),
        "name": "n21-orbit-rca",
        "window_doses": WINDOW_DOSES,
    }
    replay = qpu_cases._reproduction_arguments(fixture, location)
    case = " ".join(qpu_cases._scientific_case("n21-orbit-rca", fixture))
    _require(
        "--window-doses-dt" in replay
        and replay[replay.index("--window-doses-dt") + 1] == "0,3500,7000"
        and "--window-doses-dt is the window-dose sweep" in case,
        f"a window-dose record's written command or case text omits the doses: {replay}",
    )
    for doses, reason in (([0, 3500, 7001], "the echo needs"), ([0, 3500, 1], "is not a multiple of granularity")):
        try:
            qpu_planning.family_candidates(live_run, [snapshot], _args("n21-orbit-rca", window_doses_dt=doses), {})
        except (live_run.LiveRunError, ValueError) as error:
            _require(reason in str(error), f"doses {doses} are refused as {error}")
        else:
            raise RuntimeError(f"the planner accepted doses {doses}")
    _require(
        qpe_diagnostics.n21_dose_violations([0, 4096], 16, 2) == []
        and len(qpe_diagnostics.n21_dose_violations([0, 4097], 16, 2)) == 1
        and len(qpe_diagnostics.n21_dose_violations([0, 4112], 16, 2)) == 1,
        "the timing check ignores the Target's granularity",
    )
    for kwargs in (
        {"window_sweep": True},
        {"overlap_split": True, "reset_dt": 520},
        {"ground_control_split": True, "reset_dt": 520},
        {"ramsey_windows": (1, 2)},
        {"segmented": SEGMENTED_SWEEP},
    ):
        try:
            diagnostic_experiments.n21_orbit_rca_group(415, 502, window_doses=tuple(WINDOW_DOSES), **kwargs)
        except ValueError as error:
            _require("window_doses excludes" in str(error), f"the group refused {kwargs} as {error}")
        else:
            raise RuntimeError(f"the group accepted window_doses beside {kwargs}")
    ceilings = ["--max-execution-seconds", "10", "--max-total-execution-seconds", "10"]
    pinned = ["--pin-layout", f"{snapshot.name}:{','.join(str(q) for q in PINNED_ORBIT_LAYOUT)}"]
    for argv, message in (
        (["--family", "n21-feedback", "--window-doses-dt", "0,3500,7000", *ceilings], "n21-orbit-rca family only"),
        (["--family", "n21-orbit-rca", "--window-doses-dt", "0,3500", *ceilings], "window_doses needs 0"),
        (["--family", "n21-orbit-rca", "--window-doses-dt", "3500,7000,14000", *ceilings], "window_doses needs 0"),
        (["--family", "n21-orbit-rca", "--window-doses-dt", "0,1,3500", *ceilings], "window_doses needs 0"),
        (["--family", "n21-orbit-rca", "--window-doses-dt", "0,3500,3500", *ceilings], "window_doses needs 0"),
        (
            ["--family", "n21-orbit-rca", "--window-doses-dt", "0,3500,7000", "--overlap-split", *pinned, *ceilings],
            "separate n21-orbit-rca configurations",
        ),
        (
            [
                "--family",
                "n21-orbit-rca",
                "--window-doses-dt",
                "0,3500,7000",
                "--ground-control-split",
                "--init-herald",
                *pinned,
                *ceilings,
            ],
            "separate n21-orbit-rca configurations",
        ),
    ):
        stderr = io.StringIO()
        with redirect_stderr(stderr), contextlib.suppress(SystemExit):
            live_run.main(argv)
        _require(message in stderr.getvalue(), f"live_run {argv} reads {stderr.getvalue()!r}, not {message!r}")


def _verify_window_dose_sweep_only() -> None:
    with (
        patch.object(live_run, "QiskitRuntimeService", _forbid_service),
        patch.object(live_run, "configure_sampler", _forbid_service),
    ):
        _service, snapshot = _fixture()
        _verify_window_dose_sweep(snapshot)
    print(
        "QPU planning: an n21-orbit-rca window-dose sweep plans a window_dose pair at every dose and a "
        "window_dose_echo pair at every nonzero dose, keeps each dose as a top-level delay on all four wires, "
        "binds the sorted doses in the configuration, policy, contracts and written command, and refuses doses "
        "that break the Target's delay timing, another family and every other sweep"
    )


SEGMENTED_SWEEP: dict[str, Any] = {
    "delays_dt": [0, 693, 819],
    "segments": 4,
    "backaction_delays_dt": [693],
    "backaction_pre_idle_dt": 1250,
}


def _verify_segmented_sweep(snapshot: live_run.Snapshot) -> None:
    """A pinned segmented ground sweep plans xy and z arms per delay plus backaction arms and binds its analyzer.

    Each arm plays, on the pinned spectator only, K segments of herald,
    preparation, an idle of exactly the configured dt (none at 0), basis
    change and readout, with a reset opening every segment after the first;
    the control plays its segment-1 herald alone; no ISA holds a
    classically conditioned block. The policy binds the configuration and
    the closure of scripts/n21_q143_segmented_sweep.py over scripts/ and
    gororoba_quantum/ while a plan without
    the sweep keeps its settings; record_groups, family_contracts and the
    written command rebuild it, and live_run refuses malformed flags.
    """
    plain = qpu_planning.settings(_args("n21-orbit-rca"))
    _require(
        "segmented_sweep" not in plain and "segmented_analyzer_closure" not in plain,
        "an absent segmented sweep entered the policy",
    )
    pin = {"backend": snapshot.name, "qubits": PINNED_ORBIT_LAYOUT}
    arguments = _args(
        "n21-orbit-rca", pin_layout=pin, ground_control_split=True, init_herald=True, segmented_sweep=SEGMENTED_SWEEP
    )
    settings = qpu_planning.settings(arguments)
    scripts = Path(qpu_planning.__file__).resolve().parents[1] / "scripts"
    expected_files = {
        f"scripts/{name}": hashlib.sha256((scripts / name).read_bytes()).hexdigest()
        for name in (
            "n21_orbit_rca.py",
            "n21_q143_beat_model.py",
            "n21_q143_segmented_sweep.py",
            "n21_spectator_ramsey.py",
        )
    }
    modules = Path(qpu_planning.__file__).resolve().parent
    # The analyzer decodes members through qpe_diagnostics after collection.
    expected_files["gororoba_quantum/qpe_diagnostics.py"] = hashlib.sha256(
        (modules / "qpe_diagnostics.py").read_bytes()
    ).hexdigest()
    bound = settings.get("segmented_analyzer_closure", {}).get("files", {})
    _require(
        settings.get("segmented_sweep") == SEGMENTED_SWEEP
        and {name: bound.get(name) for name in expected_files} == expected_files
        and all(name.startswith(("scripts/", "gororoba_quantum/")) for name in bound)
        and "ramsey_analyzer_closure" not in settings,
        f"the policy binds {settings.get('segmented_sweep')} with closure {settings.get('segmented_analyzer_closure')}",
    )
    traces: dict[str, Any] = {}
    candidates = qpu_planning.family_candidates(live_run, [snapshot], arguments, traces)
    _require(bool(candidates), f"FakeFez refuses the pinned segmented sweep: {traces.get('family_rejections')}")
    (choice,), configuration = candidates[0]
    names = [member.name for member in choice.group.members]
    expected = [
        f"n21_spectator_segmented_{kind}_d{delay}" for delay in SEGMENTED_SWEEP["delays_dt"] for kind in ("xy", "z")
    ] + ["n21_spectator_segmented_xy_d693_pre1250"]
    _require(names == expected, f"the segmented sweep plans {names}")
    _require(
        configuration.get("segmented_sweep") == SEGMENTED_SWEEP
        and configuration.get("ground_control_split") is True
        and configuration.get("init_herald") is True
        and configuration.get("pin_layout") == pin,
        f"the segmented configuration reads {configuration}",
    )
    control, spectator = PINNED_ORBIT_LAYOUT[0], PINNED_ORBIT_LAYOUT[2]

    def wire_ops(isa: Any, wire: int) -> list[tuple[str, int | None]]:
        return [
            (i.operation.name, int(i.operation.duration) if i.operation.name == "delay" else None)
            for i in isa.data
            if i.operation.name not in ("barrier", "rz") and any(isa.find_bit(q).index == wire for q in i.qubits)
        ]

    segments = int(SEGMENTED_SWEEP["segments"])
    for name, isa in zip(names, choice.isas, strict=True):
        _require(
            not any(i.operation.name in ("if_else", "while_loop", "for_loop", "switch_case") for i in isa.data),
            f"{name} holds a control-flow block",
        )
        kind, delay, pre = qpe_diagnostics.n21_segmented_key(name) or ("", 0, 0)
        expected_ops: list[tuple[str, int | None]] = []
        for index, basis in enumerate(qpe_diagnostics.n21_segment_bases(kind, segments)):
            expected_ops += [("reset", None)] if index else []
            expected_ops += [("measure", None)]
            expected_ops += [("delay", pre)] if pre else []
            expected_ops += [("x", None)] if basis == "z" else [("sx", None)]
            expected_ops += [("delay", delay)] if delay else []
            expected_ops += [] if basis == "z" else [("sx", None)]
            expected_ops += [("measure", None)]
        found = wire_ops(isa, spectator)
        _require(found == expected_ops, f"{name} plays {found} on the spectator, not {expected_ops}")
        _require(wire_ops(isa, control) == [("measure", None)], f"{name} plays {wire_ops(isa, control)} on the control")
    rebuilt = diagnostic_experiments.record_groups({"family_configuration": configuration})
    _require([member.name for member in rebuilt[0].members] == names, "record_groups does not rebuild the sweep")
    contracts = diagnostic_experiments.family_contracts("n21-orbit-rca", 0.08, 0.05, 0.8, configuration=configuration)
    _require(
        [contract.name for contract in contracts] == [f"{name}_one" for name in expected],
        f"the segmented family contracts read {[contract.name for contract in contracts]}",
    )
    fixture = qpu_cases._fixture()
    location = Path("results/live/fixture/record.json")
    fixture["policy"]["design"]["ground_control_split"] = True
    fixture["policy"]["design"]["segmented_sweep"] = SEGMENTED_SWEEP
    fixture["family_configuration"] = {
        **fixture.get("family_configuration", {}),
        "ground_control_split": True,
        "segmented_sweep": SEGMENTED_SWEEP,
    }
    replay = qpu_cases._reproduction_arguments(fixture, location)
    case = " ".join(qpu_cases._scientific_case("n21-orbit-rca", fixture))
    _require(
        replay[replay.index("--segmented-delays-dt") + 1] == "0,693,819"
        and replay[replay.index("--segments") + 1] == "4"
        and replay[replay.index("--backaction-delays-dt") + 1] == "693"
        and replay[replay.index("--backaction-pre-idle-dt") + 1] == "1250"
        and "--segmented-delays-dt is the segmented ground sweep" in case,
        f"a segmented record's written command or case text omits the sweep: {replay}",
    )
    for config, message in (
        (SEGMENTED_SWEEP | {"segments": 3}, "segments must be even"),
        (SEGMENTED_SWEEP | {"segments": 8}, "segments must be even"),
        (SEGMENTED_SWEEP | {"delays_dt": [0, 1]}, "delays_dt needs"),
        (SEGMENTED_SWEEP | {"backaction_delays_dt": [5]}, "must be distinct members"),
    ):
        try:
            diagnostic_experiments.n21_segmented_config(config)
        except ValueError as error:
            _require(message in str(error), f"{config} raised {error}, not {message!r}")
        else:
            raise RuntimeError(f"the segmented configuration accepted {config}")
    ceilings = ["--max-execution-seconds", "10", "--max-total-execution-seconds", "10"]
    pinned = ["--pin-layout", f"{snapshot.name}:{','.join(str(q) for q in PINNED_ORBIT_LAYOUT)}"]
    sweep = ["--segmented-delays-dt", "0,693", "--segments", "4"]
    for argv, message in (
        (["--family", "n21-orbit-rca", *sweep, "--init-herald", *pinned, *ceilings], "requires --ground-control-split"),
        (
            [
                "--family",
                "n21-orbit-rca",
                "--ground-control-split",
                "--init-herald",
                "--segments",
                "4",
                *pinned,
                *ceilings,
            ],
            "apply only with --segmented-delays-dt",
        ),
        (
            [
                "--family",
                "n21-orbit-rca",
                "--ground-control-split",
                "--init-herald",
                "--segmented-delays-dt",
                "0,693",
                *pinned,
                *ceilings,
            ],
            "requires --segments",
        ),
        (
            [
                "--family",
                "n21-orbit-rca",
                "--ground-control-split",
                "--init-herald",
                *sweep,
                "--ramsey-windows",
                "1,2",
                *pinned,
                *ceilings,
            ],
            "separate ground sweeps",
        ),
        (
            [
                "--family",
                "n21-orbit-rca",
                "--ground-control-split",
                "--init-herald",
                *sweep,
                "--backaction-delays-dt",
                "0",
                *pinned,
                *ceilings,
            ],
            "go together",
        ),
    ):
        stderr = io.StringIO()
        with redirect_stderr(stderr), contextlib.suppress(SystemExit):
            live_run.main(argv)
        _require(message in stderr.getvalue(), f"live_run {argv} reads {stderr.getvalue()!r}, not {message!r}")


def _verify_segmented_sweep_only() -> None:
    with (
        patch.object(live_run, "QiskitRuntimeService", _forbid_service),
        patch.object(live_run, "configure_sampler", _forbid_service),
    ):
        _service, snapshot = _fixture()
        _verify_segmented_sweep(snapshot)
    print(
        "QPU planning: a pinned segmented ground sweep plans an xy and a z arm per delay and its backaction arms, "
        "plays each segment's herald, preparation, exact idle, basis change and readout on the spectator alone "
        "with no control flow, binds its configuration and analyzer closure, and rebuilds, contracts, replays and "
        "refuses malformed flags"
    )


def _verify_ground_ramsey_sweep_only() -> None:
    with (
        patch.object(live_run, "QiskitRuntimeService", _forbid_service),
        patch.object(live_run, "configure_sampler", _forbid_service),
    ):
        _service, snapshot = _fixture()
        _verify_ground_ramsey_sweep(snapshot)
    print(
        "QPU planning: a pinned n21-orbit-rca ground Ramsey sweep plans immediate and idle_ground at each idle "
        "multiple, idles the control in |0> for m windows with a bare spectator idle and no control flow, binds "
        "the sorted multiples in the configuration, policy and written command, and live_run refuses them "
        "without --ground-control-split or with fewer than two distinct multiples"
    )


def _verify_ground_control_split_only() -> None:
    with (
        patch.object(live_run, "QiskitRuntimeService", _forbid_service),
        patch.object(live_run, "configure_sampler", _forbid_service),
    ):
        _service, snapshot = _fixture()
        _verify_ground_control_split(snapshot)
    print(
        "QPU planning: a pinned n21-orbit-rca ground-control split plans the immediate, idle and idle_ground "
        "spectators alone, idle_ground idles the control in |0> for measure plus reset, the configuration, "
        "policy, written command and case bind the split only when set, and live_run refuses it without "
        "--pin-layout or --init-herald, on another family or beside --overlap-split"
    )


def _verify_overlap_split_only() -> None:
    with (
        patch.object(live_run, "QiskitRuntimeService", _forbid_service),
        patch.object(live_run, "configure_sampler", _forbid_service),
    ):
        _service, snapshot = _fixture()
        _verify_overlap_split(snapshot)
    print(
        "QPU planning: a pinned n21-orbit-rca overlap split plans the bracketed nominal and window_delay pairs, "
        "the unbracketed window_delay pair and the immediate, idle and reset_only spectators, the unbracketed "
        "arms alone hold a window operation and their CZ and sx counts enter the configuration, the "
        "configuration and policy bind the split only when set, and live_run refuses it without --pin-layout"
    )


def _verify_pin_layout(snapshot: live_run.Snapshot) -> None:
    """A pinned n21-orbit-rca plan keeps every role on its named qubit and binds the pin in its policy.

    The pinned candidate's replica places logical qubit i on the i-th named
    qubit with the window on the pinned control; a pin naming another
    backend or a qubit the calibration excludes refuses the snapshot, and an
    unpinned plan's settings carry no pin key.
    """
    _require("pin_layout" not in qpu_planning.settings(_args("n21-orbit-rca")), "an unpinned plan carries a pin")
    pin = {"backend": snapshot.name, "qubits": PINNED_ORBIT_LAYOUT}
    args = _args("n21-orbit-rca", pin_layout=pin)
    _require(qpu_planning.settings(args).get("pin_layout") == pin, "the policy settings drop the pin")
    traces: dict[str, Any] = {}
    candidates = qpu_planning.family_candidates(live_run, [snapshot], args, traces)
    _require(bool(candidates), f"FakeFez refuses the pinned layout: {traces.get('family_rejections')}")
    for (choice,), configuration in candidates:
        _require(configuration.get("pin_layout") == pin, f"the configuration records {configuration.get('pin_layout')}")
        _require(len(choice.replicas) == 1, "a pinned plan placed more than one replica")
        placed = [choice.replicas[0].mapping.get(qubit) for qubit in choice.layout]
        _require(placed == PINNED_ORBIT_LAYOUT, f"the pinned replica places the roles on {placed}")
        controls = qpu_planning.window_controls(
            qpu_planning.orbit_sites(
                qpu_planning.control_sites(live_run, [entry.packed for entry in choice.entries]), choice.group.members
            )
        )
        _require(controls == [PINNED_ORBIT_LAYOUT[0]], f"the packed window plays on {controls}")
    for refused, reason in (
        ({"backend": "another_backend", "qubits": PINNED_ORBIT_LAYOUT}, "names another_backend"),
        (pin, "calibration excludes [143]"),
    ):
        fixture = copy.copy(snapshot)
        if refused is pin:
            fixture.excluded_qubits = {**snapshot.excluded_qubits, 143: "operator exclusion"}
        rejected: dict[str, Any] = {}
        try:
            qpu_planning.family_candidates(live_run, [fixture], _args("n21-orbit-rca", pin_layout=refused), rejected)
        except live_run.LiveRunError:
            pass
        else:
            raise RuntimeError(f"a pin that {reason} still planned")
        found = [row["reason"] for row in rejected.get("family_rejections", [])]
        _require(any(reason in text for text in found), f"the refusal reads {found}, not {reason!r}")
    stderr = io.StringIO()
    with redirect_stderr(stderr), contextlib.suppress(SystemExit):
        live_run.main(
            [
                "--family",
                "n21-orbit-feedback",
                "--pin-layout",
                f"{snapshot.name}:142,136,143,144",
                "--max-execution-seconds",
                "10",
                "--max-total-execution-seconds",
                "10",
            ]
        )
    _require(
        "--pin-layout applies to the n21-orbit-rca family and the campaigns" in stderr.getvalue(),
        "another family took the pin",
    )


def _verify_pin_layout_only() -> None:
    with (
        patch.object(live_run, "QiskitRuntimeService", _forbid_service),
        patch.object(live_run, "configure_sampler", _forbid_service),
    ):
        _service, snapshot = _fixture()
        _verify_pin_layout(snapshot)
    print(
        "QPU planning: a pinned n21-orbit-rca plan places each logical qubit and the window on its named qubit "
        "with one identity replica and binds the pin in policy and configuration; another backend or an "
        "excluded pinned qubit refuses, and another family rejects the flag"
    )


def _herald_renamed(isa: Any) -> Any:
    """isa with every classical register renamed, so no register plays the herald role."""
    from qiskit import ClassicalRegister, QuantumCircuit

    renamed = QuantumCircuit(*isa.qregs, *(ClassicalRegister(r.size, r.name + "_plain") for r in isa.cregs))
    renamed.compose(isa, inplace=True)
    return renamed


def _verify_init_herald(snapshot: live_run.Snapshot) -> None:
    """The heralded n21-orbit-rca family is its unheralded twin after one herald readout per qubit.

    Every compiled arm measures each active qubit into the herald register
    before a barrier over all of them, keeps the window bracket, the control
    sites and the window durations of its unheralded twin compiled on the
    same seed and layout, and has the lifted labeled law as its ideal. The
    policy, the family configuration, the contracts and record_groups carry
    the flag only when it is on, and the planner admits the heralded plan.
    Negative controls: the herald written into a register of another name
    opens the window at the first herald readout, which either leaves no
    reset to close it or holds work-qubit operations, and the unfiltered
    operation list holds the herald readouts.
    """
    from qpe_diagnostics import N21_PHASE_OUTCOMES, n21_labeled_law, phase_marginal

    heralded_args = _args("n21-orbit-rca", init_herald=True)
    plain_args = _args("n21-orbit-rca")
    _require(qpu_planning.settings(heralded_args).get("init_herald") is True, "the policy lost the herald")
    _require("init_herald" not in qpu_planning.settings(plain_args), "an absent herald entered the policy")
    # approved_record_mismatches compares the record policy whole, so a
    # submission whose herald differs from its approved record refuses.
    heralded_policy = live_run.record_policy(heralded_args)
    _require(
        heralded_policy["design"].get("init_herald") is True and heralded_policy != live_run.record_policy(plain_args),
        "the record policy does not bind the herald",
    )
    import qpu_cases

    fixture = qpu_cases._fixture()
    location = Path("results/live/fixture/record.json")
    _require(
        "--init-herald" not in qpu_cases._reproduction_arguments(fixture, location),
        "an unheralded record replays with the herald",
    )
    fixture["policy"]["design"]["init_herald"] = True
    _require(
        "--init-herald" in qpu_cases._reproduction_arguments(fixture, location),
        "a heralded record's written commands omit --init-herald",
    )
    trace: dict[str, Any] = {}
    candidates = qpu_planning.family_candidates(live_run, [snapshot], heralded_args, trace)
    _require(bool(candidates), f"FakeFez rejects every heralded N=21 window family: {trace}")
    (choice,), configuration = candidates[0]
    _require(configuration.get("init_herald") is True, f"the family configuration lost the herald: {configuration}")
    plain = qpu_planning.family_candidates(live_run, [snapshot], plain_args, {})
    _require(bool(plain) and "init_herald" not in plain[0][1], "an absent herald entered the family configuration")
    twins = [
        live_run._compile(member.circuit, choice.snap, choice.seed, choice.layout)
        for member in qpu_planning.n21_orbit_rca_group(
            int(configuration["window_delay_dt"]), int(configuration["echo_half_dt"]), window_sweep=True
        ).members
    ]
    _require(
        qpu_planning.control_sites(live_run, choice.isas) == qpu_planning.control_sites(live_run, twins),
        "the herald changes the control's measure and reset sites",
    )
    controls = qpu_planning.window_controls(
        qpu_planning.orbit_sites(qpu_planning.control_sites(live_run, choice.isas), choice.group.members)
    )
    _require(
        qpu_planning.window_durations(live_run, choice.snap, controls)[:2]
        == (configuration["window_delay_dt"], configuration["echo_half_dt"]),
        "the heralded windows differ from the control's own measure and reset durations",
    )
    for member, isa, twin in zip(choice.group.members, choice.isas, twins, strict=True):
        active = sorted({isa.find_bit(q).index for i in isa.data if i.operation.name != "barrier" for q in i.qubits})
        width = len(active)
        prefix = isa.data[: width + 1]
        herald_sites = [
            isa.find_bit(i.qubits[0]).index for i in prefix[:width] if qpe_diagnostics.herald_measurement(isa, i)
        ]
        _require(sorted(herald_sites) == active, f"{member.name}: the herald reads {herald_sites}, not {active}")
        _require(
            prefix[width].operation.name == "barrier"
            and sorted(isa.find_bit(q).index for q in prefix[width].qubits) == active,
            f"{member.name}: no barrier over every active qubit follows the herald",
        )
        unfiltered = [name for name, _qubits in live_run._ops(isa) if name == "measure"]
        _require(
            len(unfiltered) == len([name for name, _qubits in live_run._ops(twin) if name == "measure"]) + width,
            f"{member.name}: the operation list does not hold one herald readout per active qubit",
        )
        ideal = qpe_diagnostics.ideal_compiled_probabilities(isa)
        _require(np.allclose(ideal, member.ideal, rtol=0, atol=1e-10), f"{member.name}: the heralded ideal moved")
        unheralded = (
            qpe_diagnostics.n21_spectator_law(*member.name.removeprefix("n21_spectator_").rsplit("_", 1))
            if member.name.startswith("n21_spectator_")
            else n21_labeled_law("_no_feedback" not in member.name)
        )
        _require(
            np.allclose(phase_marginal(ideal), [float(v) for v in unheralded]),
            f"{member.name}: the phase marginal differs from the unheralded law",
        )
        if "_reset_only_" in member.name:
            continue
        inside = frozenset({"delay", "x"}) if "_window_echo_" in member.name else frozenset({"delay"})
        found = qpe_diagnostics.window_bracket_violations(isa, inside)
        _require(
            not found and found == qpe_diagnostics.window_bracket_violations(twin, inside),
            f"{member.name}: the heralded window bracket reads {found}",
        )
        try:
            opened_at_herald = qpe_diagnostics.window_bracket_violations(_herald_renamed(isa), inside)
        except ValueError as error:
            # The first readout sits on a wire that is never reset.
            opened_at_herald = [str(error)]
        _require(
            bool(opened_at_herald),
            f"{member.name}: a window opened at the herald readout passes, so the herald exclusion proves nothing",
        )
    # prepare and live_run.approved_family_design build the contracts through
    # qpu_planning.contract_configuration, so a dropped configuration here
    # leaves four-outcome terms and fails the lift below.
    contracts = diagnostic_experiments.family_contracts(
        "n21-orbit-rca", 0.08, 0.05, 0.8, **qpu_planning.contract_configuration("n21-orbit-rca", configuration)
    )
    plain_contracts = diagnostic_experiments.family_contracts(
        "n21-orbit-rca", 0.08, 0.05, 0.8, configuration={"window_sweep": True}
    )
    for lifted, unlifted in zip(contracts, plain_contracts, strict=True):
        for term, plain_term in zip(lifted.terms, unlifted.terms, strict=True):
            member = next(m for m in choice.group.members if m.name == term.member)
            _require(
                len(term.values) == member.ideal.size
                and math.isclose(
                    float(np.dot(term.values, member.ideal)),
                    float(np.dot(plain_term.values, member.ideal[:N21_PHASE_OUTCOMES])),
                    abs_tol=1e-12,
                ),
                f"{lifted.name}: the lifted contract scores the heralded law differently",
            )
    (rebuilt,) = diagnostic_experiments.record_groups({"family_configuration": configuration})
    _require(
        [m.name for m in rebuilt.members] == [m.name for m in choice.group.members]
        and all(qpe_diagnostics.has_herald(m.circuit) for m in rebuilt.members),
        "record_groups lost the heralded members",
    )
    ideal_summary = choice.group.summarize({m.name: m.ideal for m in choice.group.members})
    plain_group = qpu_planning.n21_orbit_rca_group(1, 1, window_sweep=True)
    plain_summary = plain_group.summarize({m.name: m.ideal for m in plain_group.members})
    _require(
        all(ideal_summary[key] == value for key, value in plain_summary.items())
        and all(value == 0.0 for key, value in ideal_summary.items() if "_herald_q" in key)
        and sum("_herald_q" in key for key in ideal_summary) == 14 * 4,
        f"the heralded summary moved the contrasts or the herald fractions: {ideal_summary}",
    )
    usage = {"usage_limit_reached": False, "usage_remaining_seconds": 300.0}
    prepare_args = _args("n21-orbit-rca", init_herald=True, max_execution_seconds=60)
    with patch.object(live_run, "simulate", _ideal_predictions):
        selected, metadata = qpu_planning.prepare(live_run, [snapshot], prepare_args, usage, {})
    _require(
        [c.group.name for c in selected] == ["n21_orbit_rca"]
        and all(qpe_diagnostics.has_herald(isa) for isa in selected[0].isas),
        "the planner did not admit the heralded family",
    )
    _require(
        all(
            len(term["values"]) == 1 << 6 for contract in metadata["observable_contracts"] for term in contract["terms"]
        ),
        "the planned contracts do not score every heralded outcome",
    )
    # Collection joins a replica's registers in circuit order; the joined
    # outcome must read phase + 4 * herald, the index the lifted laws use.
    from qiskit.primitives.containers import BitArray, DataBin, SamplerPubResult

    entry = selected[0].entries[0]
    (prefix,) = entry.prefixes
    registers = live_run.packing.registers(entry.packed, prefix)
    _require(
        [qpe_diagnostics.register_role(name) for name in registers] == ["phase", "herald"],
        f"the packed replica's registers read {registers}",
    )
    patterns = {"phase": "01", "herald": "0010"}
    pub = SamplerPubResult(
        DataBin(
            **{
                name: BitArray.from_samples(
                    [patterns[qpe_diagnostics.register_role(name)]] * 8,
                    num_bits=len(patterns[qpe_diagnostics.register_role(name)]),
                )
                for name in registers
            }
        )
    )
    joined = live_run._distribution(live_run._pub_counts(pub, registers, entry.name), entry.replicas[0].num_clbits)
    _require(
        joined.size == 1 << 6 and joined[1 + 4 * 0b0010] == 1.0,
        f"phase 01 with herald 0010 joins to outcome {int(np.argmax(joined))}, not {1 + 4 * 0b0010}",
    )
    stderr = io.StringIO()
    with redirect_stderr(stderr), contextlib.suppress(SystemExit):
        live_run.main(
            [
                "--family",
                "n21-orbit-feedback",
                "--init-herald",
                "--max-execution-seconds",
                "10",
                "--max-total-execution-seconds",
                "10",
            ]
        )
    _require(
        "--init-herald applies to the n21-orbit-rca family only" in stderr.getvalue(), "another family took the herald"
    )


def _verify_init_herald_only() -> None:
    with (
        patch.object(live_run, "QiskitRuntimeService", _forbid_service),
        patch.object(live_run, "configure_sampler", _forbid_service),
    ):
        _service, snapshot = _fixture()
        _verify_init_herald(snapshot)
    print(
        "QPU planning: the heralded n21-orbit-rca family reads every active qubit before a full barrier, keeps its "
        "unheralded twin's window bracket, control sites and windows, marginalizes to the labeled law, binds the "
        "herald in policy, configuration, contracts and record_groups, and the planner admits it; a window opened "
        "at the herald readout fails the bracket"
    )


def _verify_window_bracket_only() -> None:
    with (
        patch.object(live_run, "QiskitRuntimeService", _forbid_service),
        patch.object(live_run, "configure_sampler", _forbid_service),
    ):
        _service, snapshot = _fixture()
        _verify_window_bracket(snapshot)
    print(
        "QPU planning: every compiled n21-orbit-rca arm keeps work-qubit gates outside the control's "
        "measurement-and-reset window, and the barrier-free n21-orbit-feedback pair does not"
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
        "--submit-reuse", action="store_true", help="run only the approved-prediction reuse submission contracts"
    )
    parser.add_argument(
        "--submit-reuse-herald",
        action="store_true",
        help="run only the heralded n21-orbit-rca approved-design reuse submission contract",
    )
    parser.add_argument(
        "--case",
        action="append",
        choices=tuple(SUBMIT_REUSE_HERALD_CASES),
        help="with --submit-reuse-herald, run one named phase set after the shared dry run and reuse; repeatable",
    )
    parser.add_argument(
        "--serialized-noise",
        action="store_true",
        help="run only the retained noise-serialization equivalence contract",
    )
    parser.add_argument("--window-bracket", action="store_true", help="run only the N=21 orbit window-bracket contract")
    parser.add_argument(
        "--init-herald", action="store_true", help="run only the n21-orbit-rca initialization-herald contract"
    )
    parser.add_argument("--pin-layout", action="store_true", help="run only the n21-orbit-rca pinned-layout contract")
    parser.add_argument(
        "--overlap-split", action="store_true", help="run only the n21-orbit-rca overlap-split contract"
    )
    parser.add_argument(
        "--ground-control-split",
        action="store_true",
        help="run only the n21-orbit-rca ground-control-split contract",
    )
    parser.add_argument(
        "--ground-ramsey-sweep",
        action="store_true",
        help="run only the n21-orbit-rca ground Ramsey sweep contract",
    )
    parsed = parser.parse_args()
    if parsed.case and not parsed.submit_reuse_herald:
        parser.error("--case selects a --submit-reuse-herald phase set")
    if parsed.ground_ramsey_sweep:
        _verify_ground_ramsey_sweep_only()
    elif parsed.ground_control_split:
        _verify_ground_control_split_only()
    elif parsed.overlap_split:
        _verify_overlap_split_only()
    elif parsed.pin_layout:
        _verify_pin_layout_only()
    elif parsed.serialized_noise:
        _verify_serialized_noise_only()
    elif parsed.window_bracket:
        _verify_window_bracket_only()
    elif parsed.init_herald:
        _verify_init_herald_only()
    elif parsed.static_group_admission:
        _verify_static_admission_only()
    elif parsed.rep_delay:
        _verify_rep_delay_only()
    elif parsed.state_prep:
        _verify_state_prep_only()
    elif parsed.prep_excitation:
        _verify_prep_excitation_only()
    elif parsed.submit_reuse:
        _verify_submit_reuse()
    elif parsed.submit_reuse_herald:
        _verify_submit_reuse_herald(parsed.case)
    else:
        _verify()
