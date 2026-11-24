"""Contracts of the orientation-bit variants of the kernel map (pathion_kernel_map_orientation).

The defaults reproduce the retained circuits gate for gate; moving the orientation to another set bit of m keeps every
ideal output contrast at +-1, the nullity N and the selector marginals while it moves the Walsh support from character
16 to character 2^b; the bit-4 exchange equals the retained quarter-turn twin's ideal law on all 64 outcomes.
"""

from __future__ import annotations

import numpy as np
import pytest
from qiskit import QuantumCircuit

import pathion_kernel_map as pkm
import pathion_kernel_map_orientation as pko
from experiments import standalone_campaign_groups

TWIN_OF = dict((primary, twin) for twin, primary in pkm.TWINS)


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _same_circuit(a: QuantumCircuit, b: QuantumCircuit) -> bool:
    """Gate-for-gate equality; DiagonalGate compares by identity, so its parameters compare by value."""
    if len(a.data) != len(b.data) or a.num_qubits != b.num_qubits or a.num_clbits != b.num_clbits:
        return False
    for x, y in zip(a.data, b.data, strict=True):
        if x.operation.name != y.operation.name or x.qubits != y.qubits or x.clbits != y.clbits:
            return False
        if [str(p) for p in x.operation.params] != [str(p) for p in y.operation.params] and not (
            x.operation.name == "diagonal"
            and np.array_equal(np.array(x.operation.params), np.array(y.operation.params))
        ):
            return False
    return True


def _contrast(
    operand: tuple[int, int, int],
    orientation_bit: int | None = None,
    cocycle_free: bool = False,
    flip_input: int | None = None,
) -> np.ndarray:
    template = pko.kernel_map_template(
        operand, orientation_bit=orientation_bit, cocycle_free=cocycle_free, flip_input=flip_input
    )
    laws = [pkm.ideal_law(template.assign_parameters({pkm.ORIENTATION: p})) for p in (np.pi, 0.0)]
    return pkm.output_contrast(laws[0], laws[1])


def _support(sign: np.ndarray) -> set[int]:
    n = len(sign)
    walsh = np.array([[(-1) ** bin(a & y).count("1") for y in range(n)] for a in range(n)])
    return {int(a) for a in np.nonzero(np.abs(walsh @ sign / n) > 1e-12)[0]}


def _set_bits(operand: tuple[int, int, int]) -> list[int]:
    m = operand[0] ^ operand[1]
    return [b for b in range(5) if m >> b & 1]


@pytest.mark.parametrize("operand", [*pkm.OPERANDS, *TWIN_OF.values(), *(twin for twin, _ in pkm.TWINS)])
def test_default_circuit_is_the_retained_circuit(operand: tuple[int, int, int]) -> None:
    _expect(
        _same_circuit(pko.kernel_map_template(operand), pkm.kernel_map_template(operand)),
        f"{operand}: the default orientation circuit differs from pathion_kernel_map",
    )


@pytest.mark.parametrize("operand", pko.OPERANDS)
def test_every_orientation_bit_keeps_contrasts_nullity_and_marginals(operand: tuple[int, int, int]) -> None:
    n = pkm.nullity(operand)
    for bit in _set_bits(operand):
        template = pko.kernel_map_template(operand, orientation_bit=bit)
        minus = pkm.ideal_law(template.assign_parameters({pkm.ORIENTATION: 0.0}))
        plus = pkm.ideal_law(template.assign_parameters({pkm.ORIENTATION: np.pi}))
        _expect(abs(pkm.selector_zero(minus) - (16 - n) / 32) < 1e-12, f"{operand} bit {bit}: minus marginal")
        _expect(abs(pkm.selector_zero(plus) - (16 + n) / 32) < 1e-12, f"{operand} bit {bit}: plus marginal")
        contrast = pkm.output_contrast(plus, minus)
        _expect(bool(np.allclose(np.abs(contrast), 1.0)), f"{operand} bit {bit}: a contrast differs from +-1")
        _expect(abs(contrast.sum() / 2 - n) < 1e-9, f"{operand} bit {bit}: half-sum differs from N")


@pytest.mark.parametrize("operand", pko.OPERANDS)
def test_walsh_support_follows_the_orientation_bit(operand: tuple[int, int, int]) -> None:
    retained = _support(np.sign(_contrast(operand)))
    _expect(16 in retained, f"{operand}: the retained support lacks character 16")
    moved = _support(np.sign(_contrast(operand, orientation_bit=pko.MOVED_BIT)))
    _expect(2**pko.MOVED_BIT in moved, f"{operand}: the moved support lacks character {2**pko.MOVED_BIT}")
    _expect(16 not in moved, f"{operand}: the moved support still holds character 16")
    _expect(moved != retained, f"{operand}: moving the orientation changed no ideal sign")


def test_orientation_bit_must_split_the_pairs() -> None:
    with pytest.raises(ValueError, match="does not split"):
        pko.orientation_signs((1, 18, 1), True, 2)


@pytest.mark.parametrize("operand", pko.OPERANDS)
def test_mutated_select_changes_the_moved_ideal_observable(operand: tuple[int, int, int]) -> None:
    n = pkm.nullity(operand)
    honest = _contrast(operand, orientation_bit=pko.MOVED_BIT)
    _expect(abs(honest.sum() / 2 - n) < 1e-9, f"{operand}: honest half-sum differs from N")
    free = _contrast(operand, orientation_bit=pko.MOVED_BIT, cocycle_free=True)
    _expect(abs(free.sum() / 2 - n) > 1.5, f"{operand}: the cocycle-free SELECT left the half-sum near N")
    flipped = _contrast(operand, orientation_bit=pko.MOVED_BIT, flip_input=3)
    _expect(abs(flipped.sum() / 2 - n) > 0.5, f"{operand}: one negated SELECT sign left the half-sum at N")


@pytest.mark.parametrize("primary", pko.OPERANDS)
def test_exchange_circuit_equals_the_retained_twin_law(primary: tuple[int, int, int]) -> None:
    twin = TWIN_OF[primary]
    for plus in (False, True):
        phase = np.pi if plus else 0.0
        exchanged = pko.kernel_map_template(primary, exchange_bit=pko.EXCHANGE_BIT).assign_parameters(
            {pkm.ORIENTATION: phase}
        )
        want = pkm.ideal_law(pkm.kernel_map_circuit(twin, plus))
        _expect(
            bool(np.allclose(pkm.ideal_law(exchanged), want, atol=1e-9)),
            f"{primary} arm plus={plus}: the exchange law differs from the twin law on some of 64 outcomes",
        )
        _expect(
            bool(np.max(np.abs(pkm.ideal_law(pkm.kernel_map_circuit(primary, plus)) - want)) > 1e-3),
            f"{primary} arm plus={plus}: the primary law already equals the twin law, the control has no power",
        )


@pytest.mark.parametrize("primary", pko.OPERANDS)
def test_exchange_at_another_position_or_qubit_does_not_equal_the_twin(primary: tuple[int, int, int]) -> None:
    twin = TWIN_OF[primary]
    want = pkm.ideal_law(pkm.kernel_map_circuit(twin, False))
    wrong_qubit = pko.kernel_map_template(primary, exchange_bit=0).assign_parameters({pkm.ORIENTATION: 0.0})
    _expect(not np.allclose(pkm.ideal_law(wrong_qubit), want, atol=1e-9), f"{primary}: an X on qubit 0 equals the twin")
    early = pkm.kernel_map_template(primary, measure=False)
    shifted = QuantumCircuit(early.num_qubits)
    shifted.h(range(5))
    shifted.x(4)
    for instruction in early.data[5:]:
        shifted.append(instruction)
    law = pkm.ideal_law(shifted.assign_parameters({pkm.ORIENTATION: 0.0}))
    _expect(not np.allclose(law, want, atol=1e-9), f"{primary}: an X before the oracle equals the twin")


def test_group_holds_twelve_circuits_in_balanced_arm_order() -> None:
    group = pko.pathion_kernel_map_orientation_group()
    names = [member.name for member in group.members]
    _expect(len(names) == 12 and len(set(names)) == 12, f"unexpected members {names}")
    _expect(len(names) <= 24, "more than 24 PUBs")
    first_arm = [n.rsplit("_", 1)[1] for n in names[::2]]
    _expect(first_arm == ["plus", "minus", "plus", "minus", "plus", "minus"], f"arm order {first_arm}")
    for unit in range(6):
        _expect(
            names[2 * unit].rsplit("_", 1)[0] == names[2 * unit + 1].rsplit("_", 1)[0],
            f"unit {unit}: arms are not adjacent",
        )
    ideal = {member.name: member.ideal for member in group.members}
    summary = group.summarize(ideal)
    for role in pko.ROLES:
        for operand in pko.OPERANDS:
            key = f"{pko.unit_name(role, operand)}_nullity_estimate"
            _expect(abs(summary[key] - pkm.nullity(operand)) < 1e-9, f"{key} reads {summary[key]}")


def test_group_is_a_registered_standalone_campaign() -> None:
    _expect(
        any(group.name == "pathion_kernel_map_orientation" for group in standalone_campaign_groups()),
        "the orientation group is not registered",
    )
