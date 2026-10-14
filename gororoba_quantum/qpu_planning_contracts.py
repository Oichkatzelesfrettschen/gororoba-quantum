"""Credential-free contracts for matched diagnostic planning and invocation budgets.

FakeFez supplies calibration and routing fixtures. Every service constructor is
replaced by a failing sentinel, so the checks cannot discover saved credentials
or submit quantum work. Run the module directly; GOROROBA_WORKERS overrides the detected CPU count.
"""

from __future__ import annotations

import argparse
import copy
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

from qiskit.circuit import Measure
from qiskit.transpiler import InstructionProperties, Target
from qiskit_ibm_runtime.fake_provider import FakeFez

import diagnostic_experiments
import live_run
import local_compute
import native_preflight
import qpu_cases
import qpu_planning
from runtime_contracts import _fixture_args, _ProbeBackend, _ProbeService


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
        _verify_budget_reservation(choices)
        _verify_mixed_noise_batch(choices)
        metadata = _verify_optimizer(snapshot, choices, configuration)
        _verify_approval_mutations(choices, metadata)
        _verify_cli_approval_boundary()
        _verify_precision_defaults()
        _verify_compute_boundary()
        _verify_usage_accounting()
        _verify_infeasible_archive(service, choices, configuration)
        _verify_unrouted_family_diagnostics(service)
        _verify_coherence_readout(snapshot)
    _verify_control_timing()
    print(
        "QPU planning: matching, calibrated timing, budgets, shot optimization, "
        "approval, infeasible archives, unrouted rejection diagnostics and coherence readout maps checked"
    )


if __name__ == "__main__":
    _verify()
