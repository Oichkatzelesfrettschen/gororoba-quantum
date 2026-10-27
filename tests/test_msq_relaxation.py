"""The measurement-sequence-relaxation constructor: row layout, readers, equilibrium row, sentinel blocks and laws."""

from __future__ import annotations

from typing import Any

import numpy as np
import pytest

import diagnostic_experiments as de
import live_run
import local_compute
import qpe_diagnostics

TIERS = (5, 16, 24, 32)
T1_IDLES = [0, 5000, 12500, 25000, 50000]
EQUILIBRIUM_DT = 100000


def check(condition: bool, message: str = "check failed") -> None:
    """Raise on a false condition; python -O strips assert, so a check raises explicitly."""
    if not condition:
        raise AssertionError(message)


def groups(qubits: list[int]) -> list[Any]:
    per = {q: 545 for q in qubits}
    fixed = {q: 500 for q in qubits}
    return de.msqr_groups(qubits, per, fixed, fixed, T1_IDLES, EQUILIBRIUM_DT)


@pytest.mark.parametrize("width", TIERS)
def test_row_count_and_alignment_at_every_width_tier(width: int) -> None:
    stems = de.msqr_row_stems(width)
    check(len(stems) == de.msqr_row_count(width), f"{len(stems)} rows, {de.msqr_row_count(width)} counted")
    check(len(set(stems)) == len(stems), "two rows share a stem")
    qubits = [3 * k + 1 for k in range(width)]
    built = groups(qubits)
    check({len(group.members) for group in built} == {len(stems)}, "a group's member count differs from the layout")
    for row, stem in enumerate(stems):
        names = {group.members[row].name.rsplit("_q", 1)[0] for group in built}
        check(names == {stem}, f"row {row} fuses {names}, not {stem}")


def test_family_adds_the_successor_rows_to_the_envelope_rows() -> None:
    extra = de.MSQR_READERS + 1 + 2 * len(de.MSQR_SENTINEL_ROWS)
    check(de.MSQR_READERS == 12 and extra == 21, f"{de.MSQR_READERS} readers, {extra} added rows")
    envelope = len(de.msqe_groups([0], {0: 545}, {0: 500}, {0: 500}, T1_IDLES)[0].members)
    check(de.msqr_row_count(5) == envelope + extra, f"{de.msqr_row_count(5)} rows vs {envelope} + {extra}")


def test_job_order_follows_the_design() -> None:
    stems = list(de.msqr_row_stems(32))
    head = [de.msq_member("delay", n, s, 0).rpartition("_q")[0] for n in de.MSQ_STEPS for s in de.MSQ_SIGNED]
    check(stems[:20] == head, "the head opens with the delay arm at every N")
    check(stems[20:24] == [de.msq_member("unitary", 16, s, 0).rpartition("_q")[0] for s in de.MSQ_SIGNED], "unitary")
    check(stems[24:30] == ["msq_ro0", *(f"msq_t1_d{k}" for k in range(5))], "ro0 and the t1 members")
    k = 30
    reader = 0
    for steps in de.MSQR_READER_STEPS:
        for signed in de.MSQ_SIGNED:
            check(stems[k] == de.msq_member("measure", steps, signed, 0).rpartition("_q")[0], f"row {k}")
            check(stems[k + 1] == f"msqr_reader{reader}", f"reader {reader} does not directly follow its predecessor")
            k, reader = k + 2, reader + 1
        if steps == 4:
            expected = [de.msqr_sentinel_member(1, i, 0).rpartition("_q")[0] for i in range(4)]
            check(stems[k : k + 4] == expected, f"the middle block sits after the N = 4 reader block, not at {k}")
            k += 4
    check(stems[k] == "msqr_eq", "the equilibrium row follows the last reader")
    check(
        stems[k + 1 : k + 5] == [de.msq_member("measure", 16, s, 0).rpartition("_q")[0] for s in de.MSQ_SIGNED], "N=16"
    )
    check(
        stems[k + 5 : k + 9] == [de.msq_member("settle", 16, s, 0).rpartition("_q")[0] for s in de.MSQ_SIGNED], "settle"
    )
    check(stems[k + 9 : k + 11] == ["msqe_rc1", "msqe_rc0"], "the reset controls follow the settle arm")
    check(stems[k + 11].startswith("msqe_pat"), "the patterns follow the reset controls")
    check(stems[-1].startswith("msqe_pat"), "the tail block lies among the patterns, not after the last row")


@pytest.mark.parametrize("width", TIERS)
def test_each_sentinel_segment_lies_in_its_own_third(width: int) -> None:
    stems = de.msqr_row_stems(width)
    count = len(stems)
    index = {stem: k for k, stem in enumerate(stems)}
    segments = de.msqr_sentinel_pairs()
    check(len(segments) == 3 and all(len(pairs) == 2 for pairs in segments), "three segments of two pairs")
    for segment, pairs in enumerate(segments):
        for first, second in pairs:
            check(index[second] == index[first] + 1, f"{first} and {second} are not consecutive rows")
            for stem in (first, second):
                third = 3 * index[stem] // count
                check(third == segment, f"segment {segment} row {index[stem]} of {count} lies in third {third}")


def test_sentinel_rows_are_delay_arm_copies_with_their_own_names() -> None:
    members = {m.name: m for m in groups([7])[0].members}
    delay = members[de.msq_member("delay", 4, de.MSQ_SIGNED[0], 7)]
    for segment in (de.MSQR_SENTINEL_MIDDLE, de.MSQR_SENTINEL_TAIL):
        for index, (steps, signed) in enumerate(de.MSQR_SENTINEL_ROWS):
            copy = members[de.msqr_sentinel_member(segment, index, 7)]
            original = members[de.msq_member("delay", steps, signed, 7)]
            check(np.array_equal(copy.ideal, original.ideal) and np.array_equal(copy.weights, original.weights), "law")
            check(
                [op.operation.name for op in copy.circuit.data] == [op.operation.name for op in original.circuit.data],
                f"{copy.name} differs from {original.name} in its instructions",
            )
            check(copy.name != original.name, "a sentinel copy needs its own name")
    check(delay.name in members, "the delay arm keeps its four signed members per N")


def test_new_members_are_dynamic_and_end_in_reset() -> None:
    for member in groups([7])[0].members:
        check(local_compute.is_dynamic(member.circuit), f"{member.name} must run in the dynamic job")
        check(member.circuit.data[-1].operation.name == "reset", f"{member.name} must end in a reset")


def test_new_members_match_their_exact_oracle() -> None:
    for member in groups([7, 11])[0].members:
        if member.circuit.num_clbits > 3:
            continue
        law = qpe_diagnostics.ideal_compiled_probabilities(member.circuit)
        check(bool(np.allclose(law, member.ideal, rtol=0, atol=1e-10)), f"{member.name}: exact oracle {law}")


def test_reader_and_equilibrium_circuits() -> None:
    by_name = {m.name: m for m in groups([7])[0].members}
    reader = by_name[de.msqr_reader_member(5, 7)].circuit
    names = [op.operation.name for op in reader.data]
    check(names == ["delay", "measure", "reset"], f"reader instructions {names}")
    equilibrium = by_name[de.msqr_equilibrium_member(7)].circuit
    delays = [op.operation.params[0] for op in equilibrium.data if op.operation.name == "delay"]
    check(delays == [EQUILIBRIUM_DT, 500], f"equilibrium idles {delays}")
    check(
        [op.operation.name for op in equilibrium.data if op.operation.name != "delay"] == ["measure", "reset"],
        "the equilibrium row starts from the initialized state with no pulse",
    )
    for bad in (0, -1, 1.5):
        with pytest.raises(ValueError):
            de.msqr_equilibrium_circuit(7, bad, 500)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        de.msqr_reader_circuit(de.MSQR_READERS, 7, 500)


def test_record_groups_and_contracts_rebuild_the_family() -> None:
    qubits = [3, 9]
    configuration = {
        "name": de.MSQR_FAMILY,
        "qubits": qubits,
        "measurement_delay_dt": {str(q): 545 for q in qubits},
        "settle_delay_dt": {str(q): 500 for q in qubits},
        "prereadout_delay_dt": {str(q): 500 for q in qubits},
        "t1_delays_dt": T1_IDLES,
        "equilibrium_delay_dt": EQUILIBRIUM_DT,
    }
    rebuilt = de.record_groups({"family_configuration": configuration})
    check([g.name for g in rebuilt] == ["msqr_q3", "msqr_q9"], "group names")
    check(
        [m.name for m in rebuilt[0].members] == [m.name for m in groups(qubits)[0].members],
        "record_groups rebuilds the constructor's members",
    )
    check(de.MSQR_FAMILY in de.FAMILY_NAMES, "the family is selectable")
    contracts = de.family_contracts(de.MSQR_FAMILY, 0.08, 0.05, 0.8, configuration)
    envelope = de.family_contracts(de.MSQE_FAMILY, 0.08, 0.05, 0.8, configuration)
    check(contracts == envelope and len(contracts) > 0, "the successor reads the main family's endpoints")
    check(live_run.is_envelope_family(de.MSQR_FAMILY) and live_run.is_envelope_family(de.MSQE_FAMILY), "envelope")
    with pytest.raises(ValueError):
        de.msqr_groups(qubits, {3: 545, 9: 545}, {3: 500, 9: 500}, {3: 500, 9: 500}, T1_IDLES, 0)


def test_the_retained_envelope_family_is_unchanged() -> None:
    members = de.msqe_groups([3], {3: 545}, {3: 500}, {3: 500}, T1_IDLES)[0].members
    check(not any(m.name.startswith("msqr_") for m in members), "the envelope gained a successor member")
    check(len(members) == de.msqr_row_count(5) - 21, "the envelope's row count moved")


def test_every_successor_member_has_a_summary_entry() -> None:
    group = groups([7])[0]
    summary = group.summarize({member.name: np.asarray(member.ideal, dtype=float) for member in group.members})
    for member in group.members:
        if member.name.startswith("msqr_"):
            tag = member.name.split("_")[1]
            check(any(key.startswith("q7_msqr_") and key.endswith(tag) for key in summary), f"{member.name}: no entry")
