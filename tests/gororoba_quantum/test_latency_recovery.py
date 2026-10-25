"""The latency-recovery family: 34 dynamic members, the exact ideal laws, the Pauli-frame flip, the syndrome-window
barriers, the preregistered contracts on ideal and mutated summaries, the dispatch sites and the FakeFez routing.
"""

from __future__ import annotations

import contextlib
import io
from pathlib import Path
from typing import Any
from unittest.mock import patch

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.circuit import Delay

import diagnostic_experiments
import latency_recovery as lr
import live_run
import local_compute
import qpe_diagnostics
import qpu_cases
import qpu_planning
import qpu_planning_contracts as contracts_fixture
from experiment_optimizer import ObservableContract
from experiments import Group

LATENCY, WINDOW = 224, 528


@pytest.fixture(scope="module")
def group() -> Group:
    return lr.latency_recovery_group(LATENCY, WINDOW)


@pytest.fixture(scope="module")
def ideal(group: Group) -> dict[str, np.ndarray]:
    return {member.name: member.ideal for member in group.members}


def statistic(contract: ObservableContract, distributions: dict[str, np.ndarray]) -> float:
    return sum(term.sign * float(distributions[term.member] @ np.asarray(term.values)) for term in contract.terms)


def passes(contract: ObservableContract, distributions: dict[str, np.ndarray]) -> bool:
    """The point estimate clears a directional contract's null value, the condition its lower bound must also clear."""
    if contract.minimum_effect is None:
        raise AssertionError(f"{contract.name} is a precision contract")
    return statistic(contract, distributions) > contract.null_value


def contracts_by_name() -> dict[str, ObservableContract]:
    return {contract.name: contract for contract in lr.latency_recovery_contracts(0.05, 0.8)}


def test_members_are_34_dynamic_and_unique(group: Group) -> None:
    names = [member.name for member in group.members]
    if len(names) != 34 or len(set(names)) != 34:
        raise AssertionError(f"{len(names)} members, {len(set(names))} distinct")
    counts = {
        "encoded error": sum("_err_" in n and "unencoded" not in n for n in names),
        "error-free": sum("_ok_" in n for n in names),
        "unencoded": sum("unencoded" in n for n in names),
    }
    if counts != {"encoded error": 25, "error-free": 6, "unencoded": 3}:
        raise AssertionError(counts)
    if not all(local_compute.is_dynamic(member.circuit) for member in group.members):
        raise AssertionError("a member is static")
    for member in group.members:
        weights = np.asarray(member.weights)
        if weights.shape != (16,) or weights.min() < 0 or weights.max() > 1:
            raise AssertionError(f"{member.name}: weights leave [0, 1]")


def test_ideal_laws_match_an_independent_enumeration(group: Group) -> None:
    for member in group.members:
        enumerated = np.asarray(qpe_diagnostics.ideal_branch_probabilities(member.circuit))
        if not np.allclose(member.ideal, enumerated, atol=1e-12):
            raise AssertionError(f"{member.name}: density law differs from the branch enumeration")


def test_ideal_fidelities(group: Group, ideal: dict[str, np.ndarray]) -> None:
    summary = group.summarize(ideal)
    for arm in lr.ENCODED_ARMS:
        if not np.isclose(summary[f"{arm}_err_F"], 1.0):
            raise AssertionError(f"{arm} with the error reads F {summary[f'{arm}_err_F']}")
        if not np.isclose(summary[f"{arm}_err_C"], 1.0) or not np.isclose(summary[f"{arm}_err_phi"], 0.0):
            raise AssertionError(f"{arm}: C and phi leave 1 and 0")
    for arm in ("ff_0", "frame_0"):
        if not np.isclose(summary[f"{arm}_ok_F"], 1.0):
            raise AssertionError(f"{arm} without the error reads F {summary[f'{arm}_ok_F']}")
    for arm in lr.FRAME_ARMS:
        values = [summary[f"{arm}_err_uncorrected_{basis}_expectation"] for basis in ("XX", "YY", "ZZ")]
        if not np.allclose(values, [1.0, 1.0, -1.0]) or not np.isclose(summary[f"{arm}_err_uncorrected_F"], 0.0):
            raise AssertionError(f"{arm}: the no-correction null reads {values}")
    if not np.isclose(summary["ff_0_unencoded_err_F"], 0.25):
        raise AssertionError(f"the unencoded arm reads F {summary['ff_0_unencoded_err_F']}")
    for key in ("decay_not_phase_C_loss", "decay_not_phase_phi_shift", "window_slope_difference"):
        if not np.isclose(summary[key], 0.0):
            raise AssertionError(f"{key} is {summary[key]} on the ideal summary")


def test_frame_flip_on_synthetic_distributions() -> None:
    def point(syndrome: int, r_bit: int, d0_bit: int) -> np.ndarray:
        law = np.zeros(16)
        law[syndrome + 4 * (r_bit + 2 * d0_bit)] = 1.0
        return law

    # With r = 0 and d0 = 0 every parity is +1 unless the frame flips d0.
    flipped = {basis: lr.expectation(point(1, 0, 0), basis, framed=True) for basis in lr.BASES}
    plain = {basis: lr.expectation(point(1, 0, 0), basis, framed=False) for basis in lr.BASES}
    if set(plain.values()) != {1.0}:
        raise AssertionError(plain)
    for basis, (_r_letter, d0_letter) in lr.BASES.items():
        expected = -1.0 if d0_letter in ("Y", "Z") else 1.0
        if flipped[basis] != expected:
            raise AssertionError(f"{basis}: framed {flipped[basis]}, expected {expected}")
    for syndrome in (0, 2, 3):
        if any(lr.expectation(point(syndrome, 0, 0), basis, framed=True) != 1.0 for basis in lr.BASES):
            raise AssertionError(f"syndrome {syndrome} flipped a basis")


def test_syndrome_window_holds_only_ancilla_measurements(group: Group) -> None:
    for member in group.members:
        if lr.syndrome_window_violations(member.circuit):
            raise AssertionError(f"{member.name}: {lr.syndrome_window_violations(member.circuit)}")
        circuit = member.circuit
        data = list(circuit.data)
        barriers = [i for i, item in enumerate(data) if item.operation.name == "barrier"]
        measures = [i for i, item in enumerate(data) if item.operation.name == "measure"][:2]
        if len(barriers) != 2 or not barriers[0] < measures[0] < measures[1] < barriers[1]:
            raise AssertionError(f"{member.name}: barriers {barriers} do not bracket measures {measures}")
        if [circuit.find_bit(data[i].qubits[0]).index for i in measures] != list(lr.ANCILLAS):
            raise AssertionError(f"{member.name}: the bracketed measurements are not the ancillas")
        if any(len(data[i].qubits) != circuit.num_qubits for i in barriers):
            raise AssertionError(f"{member.name}: a barrier misses a qubit")
        flow = [item for item in data if item.operation.name == "if_else"]
        arm = member.name.split("_err_")[0].split("_ok_")[0].removeprefix("lr_")
        if len(flow) != int(arm in (*lr.FF_ARMS, lr.UNENCODED_ARM)):
            raise AssertionError(f"{member.name}: {len(flow)} conditionals")
        for item in flow:
            body = item.operation.blocks[0].data
            target, value = item.operation.condition
            if (
                [b.operation.name for b in body] != ["x"]
                or [circuit.find_bit(q).index for q in item.qubits] != [lr.DATA[0]]
                or target.name != "s"
                or value != 1
            ):
                raise AssertionError(f"{member.name}: the conditional is not X(d0) on s == 1")
        delays = [(i, item) for i, item in enumerate(data) if isinstance(item.operation, Delay)]
        expected_dt = lr.arm_window_dt(arm, LATENCY, WINDOW)
        if bool(delays) != bool(expected_dt):
            raise AssertionError(f"{member.name}: delays {len(delays)} for a {expected_dt} dt window")
        for index, item in delays:
            if index < barriers[1] or item.operation.duration != expected_dt:
                raise AssertionError(f"{member.name}: a delay precedes the closing barrier or has another length")
            if circuit.find_bit(item.qubits[0]).index not in (lr.REFERENCE, *lr.DATA):
                raise AssertionError(f"{member.name}: a delay idles an ancilla")
        if [circuit.find_bit(item.qubits[0]).index for _, item in delays] != [lr.REFERENCE, *lr.DATA] * bool(delays):
            raise AssertionError(f"{member.name}: the window covers other qubits than r, d0, d1 and d2")


def test_a_gate_inside_the_window_is_flagged() -> None:
    base = lr.latency_recovery_circuit("ff_0", True, "ZZ", LATENCY, WINDOW)
    mutated = QuantumCircuit(*base.qregs, *base.cregs)
    closing = [i for i, item in enumerate(base.data) if item.operation.name == "barrier"][1]
    for index, item in enumerate(base.data):
        if index == closing:
            mutated.x(lr.DATA[0])
        mutated.append(item)
    if lr.syndrome_window_violations(mutated) != [f"x on [{lr.DATA[0]}]"]:
        raise AssertionError(lr.syndrome_window_violations(mutated))
    unbracketed = QuantumCircuit(*base.qregs, *base.cregs)
    for item in base.data:
        if item.operation.name != "barrier":
            unbracketed.append(item)
    with pytest.raises(ValueError, match="not bracketed"):
        lr.syndrome_window_violations(unbracketed)


def test_contracts_split_alpha_and_pass_on_ideal_summaries(ideal: dict[str, np.ndarray]) -> None:
    contracts = contracts_by_name()
    if set(contracts) != {
        "lr_recovery",
        "lr_code_property",
        "lr_latency_cost",
        "lr_latency_is_idle",
        "lr_window_cost_ff",
        "lr_window_cost_frame",
        "lr_window_slope",
    }:
        raise AssertionError(sorted(contracts))
    if not np.isclose(sum(c.alpha for c in contracts.values()), 0.05):
        raise AssertionError("alpha is not split equally over the seven inferential tests")
    values = {name: statistic(contract, ideal) for name, contract in contracts.items()}
    expected = {
        "lr_recovery": 1.0,
        "lr_code_property": 0.75,
        "lr_latency_cost": 0.0,
        "lr_latency_is_idle": 0.0,
        "lr_window_cost_ff": 0.0,
        "lr_window_cost_frame": 0.0,
        "lr_window_slope": 0.0,
    }
    for name, value in expected.items():
        if not np.isclose(values[name], value):
            raise AssertionError(f"{name}: statistic {values[name]}, expected {value}")
    # The ideal circuit carries no latency cost, idle excess or window slope difference: the precision endpoints
    # read 0, which a model that applies the conditional instantly also predicts.
    if not (passes(contracts["lr_recovery"], ideal) and passes(contracts["lr_code_property"], ideal)):
        raise AssertionError("a directional contract fails on the ideal summary")
    for name in (
        "lr_latency_cost",
        "lr_latency_is_idle",
        "lr_window_cost_ff",
        "lr_window_cost_frame",
        "lr_window_slope",
    ):
        if contracts[name].precision_half_width is None or contracts[name].minimum_effect is not None:
            raise AssertionError(f"{name} is not a precision endpoint")


def test_contracts_fail_on_mutated_summaries(ideal: dict[str, np.ndarray]) -> None:
    contracts = contracts_by_name()
    uniform = np.full(16, 1 / 16)

    def degrade(arms: tuple[str, ...], weight: float) -> dict[str, np.ndarray]:
        return {
            name: (1 - weight) * law + weight * uniform
            if any(name.startswith(f"lr_{arm}_err_") for arm in arms)
            else law
            for name, law in ideal.items()
        }

    # A feed-forward arm with a 0.2 mixture loses F = 0.15: both difference endpoints read it.
    costly = degrade(("ff_0",), 0.2)
    for name in ("lr_latency_cost", "lr_latency_is_idle"):
        if not np.isclose(statistic(contracts[name], costly), 0.15):
            raise AssertionError(f"{name}: {statistic(contracts[name], costly)}")
    # Removing the code (the encoded law in place of ff_0_unencoded) breaks code_property.
    uncoded = dict(ideal)
    for basis in lr.FIDELITY_BASES:
        uncoded[lr.member_name("ff_0_unencoded", True, basis)] = ideal[lr.member_name("ff_0", True, basis)]
    if passes(contracts["lr_code_property"], uncoded):
        raise AssertionError("code_property held with the code removed")
    # An arm that equals its own no-correction null breaks recovery.
    unflipped = dict(ideal)
    for basis in lr.FIDELITY_BASES:
        unflipped[lr.member_name("ff_0", True, basis)] = ideal[lr.member_name("frame_0", True, basis)]
    if passes(contracts["lr_recovery"], unflipped):
        raise AssertionError("recovery held for an arm that equals its own null")
    # A slope on the feed-forward side only moves window_slope, and the summary reports the same value.
    sloped = degrade(("ff_w",), 0.2)
    if not np.isclose(statistic(contracts["lr_window_cost_ff"], sloped), 0.15):
        raise AssertionError(statistic(contracts["lr_window_cost_ff"], sloped))
    if not np.isclose(statistic(contracts["lr_window_cost_frame"], sloped), 0.0):
        raise AssertionError(statistic(contracts["lr_window_cost_frame"], sloped))
    if not np.isclose(statistic(contracts["lr_window_slope"], sloped), 0.15):
        raise AssertionError(statistic(contracts["lr_window_slope"], sloped))
    summary = lr.latency_recovery_group(LATENCY, WINDOW).summarize(sloped)
    if not np.isclose(summary["window_slope_difference"], 0.15):
        raise AssertionError(summary["window_slope_difference"])
    if not np.isclose(lr.latency_recovery_group(LATENCY, WINDOW).summarize(costly)["latency_cost"], 0.15):
        raise AssertionError("the summary lost latency_cost")


def test_dispatch_sites() -> None:
    if "latency-recovery" not in diagnostic_experiments.FAMILY_NAMES or "latency-recovery" not in qpu_cases.FAMILIES:
        raise AssertionError("the family is not registered")
    if diagnostic_experiments.family_contracts("latency-recovery", 0.08, 0.05, 0.8) != lr.latency_recovery_contracts(
        0.05, 0.8
    ):
        raise AssertionError("family_contracts differs from the family's contracts")
    if qpu_planning.contract_configuration("latency-recovery", {"name": "latency-recovery"}) != {}:
        raise AssertionError("the contracts read no configuration")
    rebuilt = diagnostic_experiments.record_groups(
        {"family_configuration": {"name": "latency-recovery", "latency_dt": LATENCY, "window_dt": WINDOW}}
    )
    reference = lr.latency_recovery_group(LATENCY, WINDOW)
    if [m.name for m in rebuilt[0].members] != [m.name for m in reference.members]:
        raise AssertionError("record_groups rebuilds other members")
    delays = {
        m.name: {i.operation.duration for i in m.circuit.data if isinstance(i.operation, Delay)}
        for m in rebuilt[0].members
    }
    if delays["lr_frame_lw_err_XX"] != {LATENCY + WINDOW}:
        raise AssertionError(delays["lr_frame_lw_err_XX"])
    for bad in ((0, WINDOW), (LATENCY, -1), (1.5, WINDOW), (True, WINDOW)):
        with pytest.raises(ValueError):
            lr.latency_recovery_group(*bad)


def test_cli_validation() -> None:
    ceilings = ["--max-execution-seconds", "10", "--max-total-execution-seconds", "10"]
    for argv, message in (
        (["--family", "n21-feedback", "--latency-dt", "224", *ceilings], "--latency-dt applies to the latency-rec"),
        (["--family", "state-prep-control", "--window-dt", "528", *ceilings], "--window-dt applies to the latency-rec"),
        (["--family", "latency-recovery", "--latency-dt", "0", *ceilings], "--latency-dt must be a positive integer"),
        (["--family", "latency-recovery", "--max-replicas", "2", *ceilings], "--max-replicas must be 1"),
    ):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr), contextlib.suppress(SystemExit):
            live_run.main(argv)
        if message not in stderr.getvalue():
            raise AssertionError(f"{argv}: {stderr.getvalue()!r} lacks {message!r}")


def test_settings_bind_given_delays_only() -> None:
    plain = contracts_fixture._args("latency-recovery")
    if "latency_dt" in qpu_planning.settings(plain) or "window_dt" in qpu_planning.settings(plain):
        raise AssertionError("an omitted delay entered the policy")
    given = contracts_fixture._args("latency-recovery", latency_dt=224, window_dt=528)
    bound = qpu_planning.settings(given)
    if (bound["latency_dt"], bound["window_dt"]) != (224, 528):
        raise AssertionError(bound)


def test_case_text_and_replay_arguments() -> None:
    record = qpu_cases._fixture()
    record["policy"]["design"].update(family="latency-recovery", latency_dt=LATENCY, window_dt=WINDOW)
    record["family_configuration"] = {
        "name": "latency-recovery",
        "latency_dt": LATENCY,
        "window_dt": WINDOW,
        "requested_latency_dt": 215,
        "requested_window_dt": 526,
        "granularity_dt": 16,
        "dt_seconds": 4e-9,
    }
    record["groups"] = [{"backend": "ibm_kingston"}]
    arguments = " ".join(qpu_cases._reproduction_arguments(record, Path("results/live/fixture/record.json")))
    if "--family latency-recovery" not in arguments or f"--latency-dt {LATENCY} --window-dt {WINDOW}" not in arguments:
        raise AssertionError(arguments)
    text = " ".join(qpu_cases._scientific_case("latency-recovery", record))
    for fragment in ("latency-recovery family", "ff_0_unencoded", "round up to the timing granularity of 16 dt"):
        if fragment not in text:
            raise AssertionError(f"the case text lacks {fragment!r}")
    record["policy"]["design"]["latency_dt"] = 0
    with pytest.raises(ValueError, match="positive integer dt"):
        qpu_cases._reproduction_arguments(record, Path("results/live/fixture/record.json"))
    other = qpu_cases._fixture()
    other["policy"]["design"]["window_dt"] = WINDOW
    with pytest.raises(ValueError, match="only for latency-recovery"):
        qpu_cases._reproduction_arguments(other, Path("results/live/fixture/record.json"))


def test_compiled_members_keep_the_syndrome_window_clean() -> None:
    """Two members, the longest window and a conditional one, compile on FakeFez with clean bracketed windows."""
    forbid = contracts_fixture._forbid_service
    with patch.object(live_run, "QiskitRuntimeService", forbid), patch.object(live_run, "configure_sampler", forbid):
        _service, snapshot = contracts_fixture._fixture()
        for arm, basis in (("frame_lw", "XY"), ("ff_w", "ZZ")):
            circuit = lr.latency_recovery_circuit(arm, True, basis, LATENCY, WINDOW)
            isa = live_run._compile(circuit, snapshot, live_run.SEED_TRANSPILER)
            if lr.syndrome_window_violations(isa):
                raise AssertionError(f"{circuit.name}: {lr.syndrome_window_violations(isa)}")


@pytest.mark.audit
def test_fakefez_routing_plans_the_family() -> None:
    forbid = contracts_fixture._forbid_service
    with patch.object(live_run, "QiskitRuntimeService", forbid), patch.object(live_run, "configure_sampler", forbid):
        _service, snapshot = contracts_fixture._fixture()
        args = contracts_fixture._args("latency-recovery", latency_dt=200, window_dt=500)
        candidates: list[Any] = qpu_planning.family_candidates(live_run, [snapshot], args, {})
    if len(candidates) != 1:
        raise AssertionError(f"{len(candidates)} candidates")
    (choice,), configuration = candidates[0]
    granularity = configuration["granularity_dt"]
    if (
        configuration["name"] != "latency-recovery"
        or configuration["requested_latency_dt"] != 200
        or configuration["latency_dt"] % granularity
        or configuration["latency_dt"] < 200
        or configuration["window_dt"] < 500
    ):
        raise AssertionError(configuration)
    if len(choice.isas) != 34 or any(lr.syndrome_window_violations(isa) for isa in choice.isas):
        raise AssertionError("a routed member holds an operation inside the syndrome window")


@pytest.mark.audit
def test_fakefez_plan_admits_the_family_at_16384_shots() -> None:
    """Ideal predictions admit all seven contracts at 16384 shots; 8192 refuses the five difference endpoints."""
    forbid = contracts_fixture._forbid_service
    usage = {"usage_limit_reached": False, "usage_remaining_seconds": 600.0}
    with patch.object(live_run, "QiskitRuntimeService", forbid), patch.object(live_run, "configure_sampler", forbid):
        _service, snapshot = contracts_fixture._fixture()
        args = contracts_fixture._args(
            "latency-recovery",
            optimize=True,
            shot_tiers=[8192, 16384],
            max_execution_seconds=300,
            max_total_execution_seconds=600.0,
            model_shots=32768,
        )
        with patch.object(live_run, "simulate", contracts_fixture._ideal_predictions):
            _selected, metadata = qpu_planning.prepare(live_run, [snapshot], args, usage, {})
    optimization = metadata["optimization"]
    if optimization["selected"] != "candidate-000-shots-16384":
        raise AssertionError(optimization["selected"])
    refused = {
        observable["name"]
        for candidate in optimization["candidates"]
        if candidate["name"].endswith("8192")
        for observable in candidate["observables"]
        if not observable["feasible"]
    }
    if refused != {
        "lr_latency_cost",
        "lr_latency_is_idle",
        "lr_window_cost_ff",
        "lr_window_cost_frame",
        "lr_window_slope",
    }:
        raise AssertionError(refused)
