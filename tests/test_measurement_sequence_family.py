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
SETTLES = {57: 500, 65: 500, 104: 500}
PREREADOUTS = {57: 480, 65: 480, 104: 480}
T1_IDLES = [0, 5000, 12500, 25000, 50000]


def _member(groups: list[Any], name: str) -> Any:
    for group in groups:
        for member in group.members:
            if member.name == name:
                return member
    raise KeyError(name)


@pytest.fixture(scope="module")
def groups() -> list[Any]:
    return de.measurement_sequence_groups(QUBITS, DELAYS, SETTLES, PREREADOUTS, T1_IDLES)


@pytest.mark.parametrize("steps", de.MSQ_MEASURE_STEPS)
@pytest.mark.parametrize("sign", (1, -1))
def test_measure_arm_structure(steps: int, sign: int) -> None:
    circuit = de.msq_circuit("measure", steps, sign, 5, "check", 100, 500, 480)
    operations = circuit.count_ops()
    check(operations["rx"] == steps)
    check(operations["measure"] == steps + 1)
    check(operations["delay"] == 1)
    check([inst.operation.name for inst in circuit.data[-2:]] == ["delay", "measure"])
    check(circuit.data[-2].operation.duration == 480)
    check([(register.name, register.size) for register in circuit.cregs] == [("final", 1), ("mcm", steps)])
    angles = {round(float(inst.operation.params[0]), 12) for inst in circuit.data if inst.operation.name == "rx"}
    check(angles == {round(sign * de.MSQ_THETA / steps, 12)})
    check(is_dynamic(circuit))


def test_one_step_measure_arm_is_refused() -> None:
    check(1 not in de.MSQ_MEASURE_STEPS)
    with pytest.raises(ValueError):
        de.msq_circuit("measure", 1, 1, 5, "check", 100)


@pytest.mark.parametrize("steps", de.MSQ_STEPS)
def test_delay_arm_structure(steps: int) -> None:
    circuit = de.msq_circuit("delay", steps, -1, 5, "check", 1664, 500, 480)
    operations = circuit.count_ops()
    check(operations["rx"] == steps)
    check(operations["delay"] == steps + 1)
    check(operations["measure"] == 1)
    check(circuit.data[-1].operation.name == "measure")
    check([(register.name, register.size) for register in circuit.cregs] == [("final", 1)])
    check({inst.operation.duration for inst in circuit.data if inst.operation.name == "delay"} == {1664, 480})
    check({inst.operation.unit for inst in circuit.data if inst.operation.name == "delay"} == {"dt"})
    check(not is_dynamic(circuit))


@pytest.mark.parametrize("sign", (1, -1))
def test_unitary_arm_structure(sign: int) -> None:
    circuit = de.msq_circuit("unitary", 16, sign, 5, "check", 1664, 500, 480)
    operations = circuit.count_ops()
    check(operations["rx"] == 16)
    check(operations["barrier"] == 15)
    check(operations["measure"] == 1)
    check(operations["delay"] == 1)
    check([(register.name, register.size) for register in circuit.cregs] == [("final", 1)])
    names = [inst.operation.name for inst in circuit.data]
    check(names == ["rx", "barrier"] * 15 + ["rx", "delay", "measure"])
    check(not is_dynamic(circuit))
    with pytest.raises(ValueError):
        de.msq_circuit("unitary", 8, sign, 5, "check", 1664)


@pytest.mark.parametrize("sign", (1, -1))
def test_settle_arm_structure(sign: int) -> None:
    circuit = de.msq_circuit("settle", 16, sign, 5, "check", 1664, 500, 480)
    operations = circuit.count_ops()
    check(operations["rx"] == 16)
    check(operations["measure"] == 17)
    check(operations["delay"] == 17)
    check([(register.name, register.size) for register in circuit.cregs] == [("final", 1), ("mcm", 16)])
    names = [inst.operation.name for inst in circuit.data]
    check(names == ["rx", "measure", "delay"] * 16 + ["delay", "measure"])
    check({inst.operation.duration for inst in circuit.data if inst.operation.name == "delay"} == {500, 480})
    check(is_dynamic(circuit))
    with pytest.raises(ValueError):
        de.msq_circuit("settle", 8, sign, 5, "check", 1664, 500)
    with pytest.raises(ValueError):
        de.msq_circuit("settle", 16, sign, 5, "check", 1664, 0)


def test_settle_ideal_is_the_measure_law(groups: list[Any]) -> None:
    settle = _member(groups, "msq_settle_n16_ma_q65")
    measure = _member(groups, "msq_measure_n16_ma_q65")
    check(np.array_equal(settle.ideal, measure.ideal))
    check(math.isclose(float(settle.ideal @ settle.weights), de.msq_pinched_p0(16), abs_tol=1e-12))
    check(round(de.msq_pinched_p0(16), 4) == 0.8914)


def test_t1_members(groups: list[Any]) -> None:
    for index, idle in enumerate(T1_IDLES):
        member = _member(groups, f"msq_t1_d{index}_q65")
        names = [inst.operation.name for inst in member.circuit.data]
        check(names == ["x", *(["delay"] if idle else []), "delay", "measure"])
        durations = [inst.operation.duration for inst in member.circuit.data if inst.operation.name == "delay"]
        check(durations == ([idle, 480] if idle else [480]))
        check(np.array_equal(member.ideal, [0.0, 1.0]) and np.array_equal(member.weights, [0.0, 1.0]))
        check(not is_dynamic(member.circuit))
    with pytest.raises(ValueError):
        de.msq_t1_circuit(5, 65, 10, 480)
    with pytest.raises(ValueError):
        de.msq_t1_delays([0, 10, 5, 20, 30])


def test_t1_summary(groups: list[Any]) -> None:
    static = groups[0]
    summary = static.summarize({member.name: member.ideal for member in static.members})
    check(summary["q57_msq_p1_t1_d3"] == 1.0)
    check(not any("readout_history" in key for key in summary))


def test_group_split_by_job_kind(groups: list[Any]) -> None:
    check(
        [group.name for group in groups]
        == [name for qubit in QUBITS for name in (f"msq_static_q{qubit}", f"msq_dynamic_q{qubit}")]
    )
    for group in groups:
        dynamic = group.name.startswith("msq_dynamic_")
        check({is_dynamic(member.circuit) for member in group.members} == {dynamic})
        check(len(group.members) == (20 if dynamic else 29))


def test_member_order_signs_and_names(groups: list[Any]) -> None:
    static = groups[0]
    names = [member.name for member in static.members]
    check(names[:4] == [f"msq_delay_n1_{tag}_q57" for tag in ("pa", "ma", "mb", "pb")])
    check(names[-13:-9] == [f"msq_delay_n16_{tag}_q57" for tag in ("pa", "ma", "mb", "pb")])
    check(names[-9:-5] == [f"msq_unitary_n16_{tag}_q57" for tag in ("pa", "ma", "mb", "pb")])
    check(names[-5:] == [f"msq_t1_d{k}_q57" for k in range(5)])
    dynamic_names = [member.name for member in groups[1].members]
    check(dynamic_names[:4] == [f"msq_measure_n2_{tag}_q57" for tag in ("pa", "ma", "mb", "pb")])
    check(dynamic_names[-8:-4] == [f"msq_measure_n16_{tag}_q57" for tag in ("pa", "ma", "mb", "pb")])
    check(dynamic_names[-4:] == [f"msq_settle_n16_{tag}_q57" for tag in ("pa", "ma", "mb", "pb")])
    for group in groups:
        signed = [member for member in group.members if "_t1_" not in member.name]
        for start in range(0, len(signed), 4):
            quad = signed[start : start + 4]
            signs = []
            for member in quad:
                rx = next(inst.operation for inst in member.circuit.data if inst.operation.name == "rx")
                signs.append(1 if float(rx.params[0]) > 0 else -1)
            check(signs == [1, -1, -1, 1])


@pytest.mark.parametrize("steps", de.MSQ_STEPS)
def test_delay_ideal(groups: list[Any], steps: int) -> None:
    delay = _member(groups, f"msq_delay_n{steps}_mb_q65")
    check(np.allclose(delay.ideal, [math.cos(de.MSQ_THETA / 2) ** 2, math.sin(de.MSQ_THETA / 2) ** 2], atol=1e-15))
    check(np.allclose(np.asarray(ideal_branch_probabilities(delay.circuit)), delay.ideal, rtol=0, atol=1e-12))


@pytest.mark.parametrize("steps", de.MSQ_MEASURE_STEPS)
def test_ideal_laws(groups: list[Any], steps: int) -> None:
    measure = _member(groups, f"msq_measure_n{steps}_pa_q57")
    closed = (1 + math.cos(de.MSQ_THETA / steps) ** steps) / 2
    check(len(measure.ideal) == 2 ** (steps + 1) == len(measure.weights))
    check(math.isclose(float(measure.ideal.sum()), 1.0, abs_tol=1e-12))
    check(math.isclose(float(measure.ideal @ measure.weights), closed, abs_tol=1e-12))
    if steps <= 8:
        branch = np.asarray(ideal_branch_probabilities(measure.circuit))
        check(np.allclose(branch, measure.ideal, rtol=0, atol=1e-12))


def test_unitary_ideal(groups: list[Any]) -> None:
    unitary = _member(groups, "msq_unitary_n16_mb_q104")
    check(np.allclose(unitary.ideal, [de.msq_delay_p0(), 1.0 - de.msq_delay_p0()], atol=1e-15))
    check(np.allclose(np.asarray(ideal_branch_probabilities(unitary.circuit)), unitary.ideal, rtol=0, atol=1e-12))


def test_ideal_table_and_contrast() -> None:
    check([round(de.msq_pinched_p0(steps), 4) for steps in de.MSQ_STEPS] == [0.0302, 0.5151, 0.6722, 0.8040, 0.8914])
    check(round(de.msq_delay_p0(), 4) == 0.0302)
    check(round(de.msq_pinched_p0(16) - de.msq_delay_p0(), 4) == 0.8612)
    check(de.MSQ_ENDPOINTS_PER_QUBIT == 17)


def test_summary_pools_signed_members_and_reports_deficit(groups: list[Any]) -> None:
    static = groups[0]
    summary = static.summarize({member.name: member.ideal for member in static.members})
    check(math.isclose(summary["q57_msq_p0_delay_n16"], de.msq_delay_p0(), abs_tol=1e-12))
    check(not any("measure" in key for key in summary))
    dynamic = groups[1]
    ideal = {member.name: member.ideal for member in dynamic.members}
    result = dynamic.summarize(ideal)
    check(math.isclose(result["q57_msq_deficit_n16"], 0.0, abs_tol=1e-12))
    check(math.isclose(result["q57_msq_settle_deficit_n16"], 0.0, abs_tol=1e-12))
    check(math.isclose(result["q57_msq_p0_measure_n2"], de.msq_pinched_p0(2), abs_tol=1e-12))
    # A pinching that fails to project leaves more rotation: the measured P0 falls and the deficit is positive.
    unpinched = {name: law for name, law in ideal.items()}
    for member in dynamic.members:
        if "_measure_n2_" in member.name:
            law = np.zeros(2**3)
            law[0b000] = 0.0302
            law[0b011] = 0.9698
            unpinched[member.name] = law
    check(dynamic.summarize(unpinched)["q57_msq_deficit_n2"] == pytest.approx(de.msq_pinched_p0(2) - 0.0302))


def test_contracts() -> None:
    contracts = de.measurement_sequence_contracts(QUBITS, 0.05, 0.8)
    names = [contract.name for contract in contracts]
    check(len(contracts) == 17 * len(QUBITS) == len(set(names)))
    check(math.isclose(math.fsum(contract.alpha for contract in contracts), 0.05))
    for qubit in QUBITS:
        for arm in de.MSQ_ARMS:
            for steps in de.MSQ_ARM_COUNTS[arm]:
                check(f"msq_p0_{arm}_n{steps}_q{qubit}" in names)
        check(f"msq_p0_unitary_n8_q{qubit}" not in names)
        for index in range(5):
            check(f"msq_p1_t1_d{index}_q{qubit}" in names)
        check(f"msq_zeno_contrast_n16_q{qubit}" in names)
    by_name = {contract.name: contract for contract in contracts}
    pooled = by_name["msq_p0_measure_n4_q65"]
    check([term.member for term in pooled.terms] == [f"msq_measure_n4_{tag}_q65" for tag in ("pa", "ma", "mb", "pb")])
    check(pooled.precision_half_width == de.MSQ_PRECISION["p0"])
    contrast = by_name["msq_zeno_contrast_n16_q65"]
    check([term.sign for term in contrast.terms] == [1] * 4 + [-1] * 4)
    check(
        [term.member for term in contrast.terms[4:]] == [f"msq_unitary_n16_{t}_q65" for t in ("pa", "ma", "mb", "pb")]
    )
    check(contrast.precision_half_width == de.MSQ_PRECISION["contrast"])
    # The score values at weight 1/4 per member make the endpoint the pooled mean: ideal measure minus unitary.
    groups = de.measurement_sequence_groups([65], {65: 1696}, {65: 500}, {65: 480}, T1_IDLES)
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
        "settle_delay_dt": {str(qubit): dt for qubit, dt in SETTLES.items()},
        "prereadout_delay_dt": {str(qubit): dt for qubit, dt in PREREADOUTS.items()},
        "t1_delays_dt": T1_IDLES,
    }
    contracts = de.family_contracts(de.MSQ_FAMILY, 0.08, 0.05, 0.8, configuration)
    check(len(contracts) == 51)
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
        de.measurement_sequence_groups(qubits, delays, {q: 500 for q in qubits}, {q: 480 for q in qubits}, T1_IDLES)


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


def test_recorded_wide_law_passes_the_rounding_bound() -> None:
    import qpu_cases

    law = de.msq_measure_law(16)
    recorded = [round(float(p), qpu_cases.IDEAL_DECIMALS) for p in law]
    check(len(recorded) == 131072)
    check(sum(1 for p, q in zip(law, recorded, strict=True) if p > 0 and q == 0) > 0)
    check(abs(math.fsum(recorded) - 1.0) > 1e-9)
    check(qpu_cases._ideal_law_valid(recorded))
    bound = 1e-9 + len(recorded) * 0.5 * 10**-qpu_cases.IDEAL_DECIMALS
    short = list(recorded)
    peak = max(range(len(short)), key=short.__getitem__)
    short[peak] -= 2 * bound
    check(not qpu_cases._ideal_law_valid(short))
    check(not qpu_cases._ideal_law_valid([*recorded[:-1], -0.1]))


def test_ideal_decimals_match_the_recorder() -> None:
    import inspect

    import qpu_cases

    source = inspect.getsource(live_run._member_fields)
    check(f'"ideal": law_encoding.encode([round(float(p), {qpu_cases.IDEAL_DECIMALS}) for p in entry.ideal])' in source)


class _PluginBackend:
    """A backend that adds IBMBackend.get_translation_stage_plugin to a wrapped backend."""

    def __init__(self, backend: Any, plugin: str) -> None:
        self._backend = backend
        self._plugin = plugin

    def get_translation_stage_plugin(self) -> str:
        return self._plugin

    def __getattr__(self, name: str) -> Any:
        return getattr(self._backend, name)


def _fixture_snapshot() -> Any:
    import io
    from contextlib import redirect_stdout

    from qiskit_ibm_runtime.fake_provider import FakeFez

    import qpu_planning_contracts as contracts

    backend = contracts._ProbeBackend("measurement_sequence_fixture", FakeFez())
    service = contracts._ProbeService([backend])
    with redirect_stdout(io.StringIO()):
        return live_run.take_snapshot(service, backend.name)


@pytest.mark.parametrize("plugin", (None, "ibm_dynamic_circuits"))
@pytest.mark.parametrize("workers", ("1", "4"))
def test_member_compilations_match_the_serial_compile(
    monkeypatch: pytest.MonkeyPatch, workers: str, plugin: str | None
) -> None:
    """The pooled compiler returns the member order, pinned qubits and operation counts of live_run._compile."""
    import parallel
    import qpu_planning

    snapshot = _fixture_snapshot()
    if plugin is not None:
        # An IBMBackend reports this translation plugin; transpile reads it from the backend in live_run._compile.
        snapshot.backend = _PluginBackend(snapshot.backend, plugin)
    qubits = [qubit for qubit in (45, 59, 73, 87) if qubit not in snapshot.excluded_qubits][:2]
    check(len(qubits) == 2)
    delays = {q: 1664 for q in qubits}
    settles = {q: 500 for q in qubits}
    prereadouts = {q: 480 for q in qubits}
    built = de.measurement_sequence_groups(qubits, delays, settles, prereadouts, T1_IDLES)
    work = [(m.circuit, int(g.name.rsplit("_q", 1)[1])) for g in built for m in g.members]
    check(len(work) == 49 * len(qubits))
    serial = [live_run._compile(c, snapshot, live_run.SEED_TRANSPILER, [q]) for c, q in work]
    monkeypatch.setenv("GOROROBA_WORKERS", workers)
    compiler = qpu_planning.MemberCompiler(snapshot.admission_target, live_run.SEED_TRANSPILER, plugin)
    pooled = parallel.ordered_map(compiler, work, min_items=2)
    check([c.name for c in pooled] == [c.name for c, _ in work])
    check([live_run._physical(c) for c in pooled] == [[q] for _, q in work])
    check([dict(c.count_ops()) for c in pooled] == [dict(c.count_ops()) for c in serial])
    check(all(a == b for a, b in zip(pooled, serial, strict=True)))


def test_case_text_states_the_settle_gap_as_a_hypothesis() -> None:
    import qpu_cases

    record = {
        "family_configuration": {"qubits": [57, 65], "steps": list(de.MSQ_STEPS)},
        "groups": [{"backend": "ibm_kingston"}],
        "policy": {},
    }
    text = " ".join(qpu_cases._scientific_case("measurement-sequence", record))
    check("experimental hypothesis, not a validated bound" in text)
    check("from zero to 2 us changes the deficit" in text)
    check("a tail slower than 2 us stays unexcluded" in text)
    check("excludes a readout tail" not in text)
    check("bounds a readout tail that decays within 2 us" in text)
    check("and a readout tail. The calibration" not in text)
    check("do not bias the read" not in text)
