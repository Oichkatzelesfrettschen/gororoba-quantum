"""The measurement-sequence family: circuit structure, job kinds, member order, ideal laws, endpoints and CLI."""

from __future__ import annotations

import math
from typing import Any

import numpy as np
import pytest

import diagnostic_experiments as de
import live_run
from local_compute import is_dynamic
from qpe_diagnostics import ideal_branch_probabilities


def check(condition: bool) -> None:
    """Raise on a false condition; python -O strips assert, so a check raises explicitly."""
    if not condition:
        raise AssertionError("check failed")


QUBITS = [57, 65, 104]
DELAYS = {57: 1664, 65: 1696, 104: 1632}


def _member(groups: list[Any], name: str) -> Any:
    for group in groups:
        for member in group.members:
            if member.name == name:
                return member
    raise KeyError(name)


@pytest.fixture(scope="module")
def groups() -> list[Any]:
    return de.measurement_sequence_groups(QUBITS, DELAYS)


@pytest.mark.parametrize("steps", de.MSQ_STEPS)
@pytest.mark.parametrize("sign", (1, -1))
def test_measure_arm_structure(steps: int, sign: int) -> None:
    circuit = de.msq_circuit("measure", steps, sign, 5, "check", 100)
    operations = circuit.count_ops()
    check(operations["rx"] == steps)
    check(operations["measure"] == steps + 1)
    check("delay" not in operations)
    check([(register.name, register.size) for register in circuit.cregs] == [("final", 1), ("mcm", steps)])
    angles = {round(float(inst.operation.params[0]), 12) for inst in circuit.data if inst.operation.name == "rx"}
    check(angles == {round(sign * de.MSQ_THETA / steps, 12)})
    check(is_dynamic(circuit) is (steps >= 2))


@pytest.mark.parametrize("steps", de.MSQ_STEPS)
def test_delay_arm_structure(steps: int) -> None:
    circuit = de.msq_circuit("delay", steps, -1, 5, "check", 1664)
    operations = circuit.count_ops()
    check(operations["rx"] == steps)
    check(operations["delay"] == steps)
    check(operations["measure"] == 1)
    check(circuit.data[-1].operation.name == "measure")
    check([(register.name, register.size) for register in circuit.cregs] == [("final", 1)])
    check({inst.operation.duration for inst in circuit.data if inst.operation.name == "delay"} == {1664})
    check({inst.operation.unit for inst in circuit.data if inst.operation.name == "delay"} == {"dt"})
    check(not is_dynamic(circuit))


def test_group_split_by_job_kind(groups: list[Any]) -> None:
    check(
        [group.name for group in groups]
        == [name for qubit in QUBITS for name in (f"msq_static_q{qubit}", f"msq_dynamic_q{qubit}")]
    )
    for group in groups:
        dynamic = group.name.startswith("msq_dynamic_")
        check({is_dynamic(member.circuit) for member in group.members} == {dynamic})
        check(len(group.members) == (16 if dynamic else 24))


def test_member_order_signs_and_names(groups: list[Any]) -> None:
    static = groups[0]
    names = [member.name for member in static.members]
    check(names[:4] == [f"msq_measure_n1_{tag}_q57" for tag in ("pa", "ma", "mb", "pb")])
    check(names[4:8] == [f"msq_delay_n1_{tag}_q57" for tag in ("pa", "ma", "mb", "pb")])
    check(names[-4:] == [f"msq_delay_n16_{tag}_q57" for tag in ("pa", "ma", "mb", "pb")])
    dynamic_names = [member.name for member in groups[1].members]
    check(dynamic_names[:4] == [f"msq_measure_n2_{tag}_q57" for tag in ("pa", "ma", "mb", "pb")])
    check(dynamic_names[-1] == "msq_measure_n16_pb_q57")
    for group in groups:
        for start in range(0, len(group.members), 4):
            quad = group.members[start : start + 4]
            signs = []
            for member in quad:
                rx = next(inst.operation for inst in member.circuit.data if inst.operation.name == "rx")
                signs.append(1 if float(rx.params[0]) > 0 else -1)
            check(signs == [1, -1, -1, 1])


@pytest.mark.parametrize("steps", de.MSQ_STEPS)
def test_ideal_laws(groups: list[Any], steps: int) -> None:
    measure = _member(groups, f"msq_measure_n{steps}_pa_q57")
    closed = (1 + math.cos(de.MSQ_THETA / steps) ** steps) / 2
    check(len(measure.ideal) == 2 ** (steps + 1) == len(measure.weights))
    check(math.isclose(float(measure.ideal.sum()), 1.0, abs_tol=1e-12))
    check(math.isclose(float(measure.ideal @ measure.weights), closed, abs_tol=1e-12))
    if steps <= 8:
        branch = np.asarray(ideal_branch_probabilities(measure.circuit))
        check(np.allclose(branch, measure.ideal, rtol=0, atol=1e-12))
    delay = _member(groups, f"msq_delay_n{steps}_mb_q65")
    check(np.allclose(delay.ideal, [math.cos(de.MSQ_THETA / 2) ** 2, math.sin(de.MSQ_THETA / 2) ** 2], atol=1e-15))
    check(np.allclose(np.asarray(ideal_branch_probabilities(delay.circuit)), delay.ideal, rtol=0, atol=1e-12))


def test_ideal_table_and_contrast() -> None:
    check([round(de.msq_pinched_p0(steps), 4) for steps in de.MSQ_STEPS] == [0.0302, 0.5151, 0.6722, 0.8040, 0.8914])
    check(round(de.msq_delay_p0(), 4) == 0.0302)
    check(round(de.msq_pinched_p0(16) - de.msq_delay_p0(), 4) == 0.8612)


def test_summary_pools_signed_members_and_reports_deficit(groups: list[Any]) -> None:
    static = groups[0]
    distributions = {member.name: member.ideal for member in static.members}
    summary = static.summarize(distributions)
    check(math.isclose(summary["q57_msq_p0_measure_n1"], de.msq_pinched_p0(1), abs_tol=1e-12))
    check(math.isclose(summary["q57_msq_p0_delay_n16"], de.msq_delay_p0(), abs_tol=1e-12))
    check(math.isclose(summary["q57_msq_deficit_n1"], 0.0, abs_tol=1e-12))
    dynamic = groups[1]
    ideal = {member.name: member.ideal for member in dynamic.members}
    check(math.isclose(dynamic.summarize(ideal)["q57_msq_deficit_n16"], 0.0, abs_tol=1e-12))
    # A pinching that fails to project leaves more rotation: the measured P0 falls and the deficit is positive.
    coherent = {member.name: np.asarray([0.0302, 0.9698]) for member in static.members if "_measure_n1_" in member.name}
    check(static.summarize(coherent)["q57_msq_deficit_n1"] == pytest.approx(de.msq_pinched_p0(1) - 0.0302))


def test_contracts() -> None:
    contracts = de.measurement_sequence_contracts(QUBITS, 0.05, 0.8)
    names = [contract.name for contract in contracts]
    check(len(contracts) == 11 * len(QUBITS) == len(set(names)))
    check(math.isclose(math.fsum(contract.alpha for contract in contracts), 0.05))
    for qubit in QUBITS:
        for arm in de.MSQ_ARMS:
            for steps in de.MSQ_STEPS:
                check(f"msq_p0_{arm}_n{steps}_q{qubit}" in names)
        check(f"msq_zeno_contrast_n16_q{qubit}" in names)
    by_name = {contract.name: contract for contract in contracts}
    pooled = by_name["msq_p0_measure_n4_q65"]
    check([term.member for term in pooled.terms] == [f"msq_measure_n4_{tag}_q65" for tag in ("pa", "ma", "mb", "pb")])
    check(pooled.precision_half_width == de.MSQ_PRECISION["p0"])
    contrast = by_name["msq_zeno_contrast_n16_q65"]
    check([term.sign for term in contrast.terms] == [1] * 4 + [-1] * 4)
    check(contrast.precision_half_width == de.MSQ_PRECISION["contrast"])
    # The score values at weight 1/4 per member make the endpoint the pooled mean: ideal measure minus delay.
    groups = de.measurement_sequence_groups([65], {65: 1696})
    ideals = {member.name: member for group in groups for member in group.members}
    estimate = math.fsum(
        term.sign * float(np.dot(ideals[term.member].ideal, np.asarray(term.values))) for term in contrast.terms
    )
    check(estimate == pytest.approx(de.msq_pinched_p0(16) - de.msq_delay_p0(), abs=1e-12))


def test_family_contracts_and_record_groups_round_trip() -> None:
    configuration = {
        "name": de.MSQ_FAMILY,
        "qubits": QUBITS,
        "measurement_delay_dt": {str(qubit): dt for qubit, dt in DELAYS.items()},
    }
    contracts = de.family_contracts(de.MSQ_FAMILY, 0.08, 0.05, 0.8, configuration)
    check(len(contracts) == 33)
    rebuilt = de.record_groups({"family_configuration": configuration})
    check([group.name for group in rebuilt][:2] == ["msq_static_q57", "msq_dynamic_q57"])
    with pytest.raises(ValueError, match="named qubits"):
        de.family_contracts(de.MSQ_FAMILY, 0.08, 0.05, 0.8, None)


@pytest.mark.parametrize(
    "qubits, delays",
    [([], {}), ([1, 1], {1: 10}), ([-1], {-1: 10}), ([1, 2], {1: 10}), ([1], {1: 0}), ([1], {1: 1.5})],
)
def test_group_inputs_are_validated(qubits: list[int], delays: Any) -> None:
    with pytest.raises(ValueError):
        de.measurement_sequence_groups(qubits, delays)


def _cli(*arguments: str) -> list[str]:
    return [
        "--family",
        "measurement-sequence",
        "--max-execution-seconds",
        "60",
        "--max-total-execution-seconds",
        "120",
        *arguments,
    ]


def test_cli_rejects_replicas_above_one(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as raised:
        live_run.main(_cli("--layout", "57,65", "--max-replicas", "2"))
    check(raised.value.code == 2)
    check("--max-replicas must be 1" in capsys.readouterr().err)


def test_cli_requires_layout(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as raised:
        live_run.main(_cli())
    check(raised.value.code == 2)
    check("requires --layout" in capsys.readouterr().err)


def test_cli_refuses_layout_on_other_families(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as raised:
        live_run.main(
            [
                "--family",
                "folded-qpe",
                "--layout",
                "1,2",
                "--max-execution-seconds",
                "60",
                "--max-total-execution-seconds",
                "120",
            ]
        )
    check(raised.value.code == 2)
    check("--layout applies to" in capsys.readouterr().err)
