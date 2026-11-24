"""Contracts of the orientation-bit variants of the kernel map (pathion_kernel_map_orientation).

The defaults reproduce the retained circuits gate for gate; moving the orientation to another set bit of m keeps every
ideal output contrast at +-1, the nullity N and the selector marginals while it moves the Walsh support from character
16 to character 2^b; the bit-4 exchange equals the retained quarter-turn twin's ideal law on all 64 outcomes.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from qiskit import QuantumCircuit, transpile

import pathion_kernel_map as pkm
import pathion_kernel_map_orientation as pko
import qrng_seeds
from experiments import standalone_campaign_groups
from heron_multiprogramming import HERON_BASIS, DisjointTile, HeronLattice

ROOT = Path(__file__).resolve().parents[2]
# The transpiler seed of the case compile (index 0 of the draw that docs/evidence/pathion-kernel-map/orientation-bit/
# compile_case.py owns); the compile of this test reproduces that run's first routing.
DRAW_INDEX = 0
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


def _quarters(sign: np.ndarray) -> dict[int, int]:
    """Nonzero Walsh coefficients of an ideal sign vector in units of 1/4, keyed by character."""
    n = len(sign)
    walsh = np.array([[(-1) ** bin(a & y).count("1") for y in range(n)] for a in range(n)])
    coefficients = 4.0 * (walsh @ sign) / n
    return {int(a): int(round(coefficients[a])) for a in np.nonzero(np.abs(coefficients) > 1e-9)[0]}


def _role_quarters(operand: tuple[int, int, int], role: str) -> dict[int, int]:
    template = pko.role_template(role, operand)
    laws = [pko.outcome_law(template.assign_parameters({pkm.ORIENTATION: p})) for p in (np.pi, 0.0)]
    return _quarters(np.sign(pkm.output_contrast(laws[0], laws[1])))


# Exact Walsh supports of the ideal contrast, computed from the statevector laws (coefficients times 4). The
# signature character (the one that carries bit 4 of the control and bit 1 of the moved member) moves from 16 to 2.
SUPPORTS: dict[tuple[int, int, int], dict[str, dict[int, int]]] = {
    (1, 26, 1): {
        "ctrl": {0: 1, 4: 1, 10: -1, 14: -1, 16: -3, 20: 1, 26: -1, 30: -1},
        "move": {0: 1, 2: -3, 4: 1, 6: 1, 8: -1, 10: -1, 12: -1, 14: -1},
        "xtwin": {0: 1, 4: 1, 10: -1, 14: -1, 16: 3, 20: -1, 26: 1, 30: 1},
        "swap": {0: 1, 4: 1, 10: -1, 14: -1, 16: -3, 20: 1, 26: -1, 30: -1},
    },
    (1, 18, 1): {
        "ctrl": {0: 3, 4: -1, 8: -1, 12: -1, 16: -1, 20: -1, 24: -1, 28: -1},
        "move": {0: 3, 2: -1, 4: -1, 6: -1, 8: -1, 10: -1, 12: -1, 14: -1},
        "xtwin": {0: 3, 4: -1, 8: -1, 12: -1, 16: 1, 20: 1, 24: 1, 28: 1},
        "swap": {0: 3, 4: -1, 8: -1, 12: -1, 16: -1, 20: -1, 24: -1, 28: -1},
    },
}


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
def test_walsh_supports_are_exact(operand: tuple[int, int, int]) -> None:
    """Eight characters per member: the signature character moves from 16 to 2, the control and the moved member share
    three of the other seven, the exchange keeps the support and flips the sign of the characters that carry bit 4, and
    the (0, signature) weight pair is identical between control and moved member."""
    for role in pko.ROLES:
        _expect(_role_quarters(operand, role) == SUPPORTS[operand][role], f"{operand} {role}: support differs")
    ctrl, move, xtwin, swap = (SUPPORTS[operand][role] for role in pko.ROLES)
    _expect(len(ctrl) == len(move) == len(xtwin) == len(swap) == 8, "a support does not hold eight characters")
    _expect(swap == ctrl, f"{operand}: the wire exchange changed the ideal law")
    shared = (set(ctrl) & set(move)) - {0}
    _expect(len(shared) == 3 and 16 not in shared and 2 not in shared, f"{operand}: shared characters {shared}")
    _expect(abs(ctrl[16]) == abs(move[2]) and ctrl[0] == move[0], f"{operand}: the (0, signature) weights differ")
    _expect(set(xtwin) == set(ctrl), f"{operand}: the exchange changed the support")
    for a in ctrl:
        _expect(xtwin[a] == (-ctrl[a] if a & 16 else ctrl[a]), f"{operand}: character {a} under the exchange")


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


def test_group_holds_sixteen_circuits_in_balanced_arm_order() -> None:
    group = pko.pathion_kernel_map_orientation_group()
    names = [member.name for member in group.members]
    _expect(len(names) == 16 and len(set(names)) == 16, f"unexpected members {names}")
    _expect(len(names) <= 24, "more than 24 PUBs")
    first_arm = [n.rsplit("_", 1)[1] for n in names[::2]]
    _expect(first_arm == ["plus", "minus"] * 4, f"arm order {first_arm}")
    for unit in range(8):
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


@pytest.mark.parametrize("operand", pko.OPERANDS)
def test_swap_member_exchanges_data_wires_one_and_four_and_keeps_the_law(operand: tuple[int, int, int]) -> None:
    """The swap circuit is the control with every gate on the other of wires 1 and 4 and each wire measured into its own
    classical bit, so a shared layout puts bit 4 on the qubit that carries bit 1 in the other members."""
    ctrl = pko.role_template("ctrl", operand)
    swap = pko.role_template("swap", operand)
    perm = {1: 4, 4: 1}

    def gates(circuit: QuantumCircuit) -> list[tuple[str, tuple[int, ...], tuple[int, ...]]]:
        return [
            (
                ins.operation.name,
                tuple(circuit.find_bit(q).index for q in ins.qubits),
                tuple(circuit.find_bit(b).index for b in ins.clbits),
            )
            for ins in circuit.data
        ]

    want = [(n, tuple(perm.get(q, q) for q in qs), cs) for n, qs, cs in gates(ctrl) if n != "measure"]
    got = [g for g in gates(swap) if g[0] != "measure"]
    _expect(want == got, f"{operand}: the swap circuit is not the control with wires 1 and 4 exchanged")
    measures = {cs[0]: qs[0] for n, qs, cs in gates(swap) if n == "measure"}
    _expect(measures == {0: 0, 1: 4, 2: 2, 3: 3, 4: 1, 5: 5}, f"{operand}: measure map {measures}")
    for phase in (0.0, np.pi):
        bound = {pkm.ORIENTATION: phase}
        _expect(
            np.allclose(
                pko.outcome_law(swap.assign_parameters(bound)),
                pko.outcome_law(ctrl.assign_parameters(bound)),
                atol=1e-12,
            ),
            f"{operand}: phase {phase}: the wire exchange changed the outcome law",
        )
    raw = pkm.ideal_law(swap.assign_parameters({pkm.ORIENTATION: 0.0}))
    _expect(
        not np.allclose(raw, pkm.ideal_law(ctrl.assign_parameters({pkm.ORIENTATION: 0.0})), atol=1e-6),
        f"{operand}: the raw wire law equals the control's, so the exchange did nothing",
    )


def test_group_is_a_registered_standalone_campaign() -> None:
    _expect(
        any(group.name == "pathion_kernel_map_orientation" for group in standalone_campaign_groups()),
        "the orientation group is not registered",
    )


@pytest.fixture(scope="module")
def snapshot_tile() -> tuple[HeronLattice, DisjointTile]:
    lattice = HeronLattice.from_snapshot(ROOT / "docs/evidence/heron_platform/targets.json", "ibm_fez")
    return lattice, lattice.find_disjoint_tiles(6, min_buffer_distance=2, max_tiles=1)[0]


def _routed_rows(circuit: QuantumCircuit) -> list[tuple[str, tuple[int, ...], tuple[int, ...], float]]:
    return [
        (
            ins.operation.name,
            tuple(circuit.find_bit(q).index for q in ins.qubits),
            tuple(circuit.find_bit(b).index for b in ins.clbits),
            float(ins.operation.params[0]) if ins.operation.name == "rz" else 0.0,
        )
        for ins in circuit.data
    ]


@pytest.mark.parametrize("operand", pko.OPERANDS)
def test_exchange_compiles_to_one_frame_on_the_bit_four_wire(
    snapshot_tile: tuple[HeronLattice, DisjointTile], operand: tuple[int, int, int]
) -> None:
    """On the snapshot target the exchange member routes to the control's cz, sx and x sequence and measure mapping;
    only rz angles of the wire measured into data bit 4 differ, all in the stretch before that wire's last sx or x, a
    stretch of cz and rz gates that commute with the frame (compiled evidence at optimization level 3)."""
    lattice, tile = snapshot_tile
    seed = qrng_seeds.resolve(f"qrng:docs/evidence/anu_qrng/draw-2026-11-24T022126Z.json#{DRAW_INDEX}")[0]
    rows = {}
    for role in ("ctrl", "xtwin"):
        template = pko.role_template(role, operand).assign_parameters({pkm.ORIENTATION: 0.0})
        routed = transpile(
            template,
            coupling_map=lattice.tile_coupling_map(tile),
            basis_gates=list(HERON_BASIS),
            optimization_level=3,
            seed_transpiler=seed,
        )
        rows[role] = _routed_rows(routed)
    ctrl, xtwin = rows["ctrl"], rows["xtwin"]
    _expect([r for r in ctrl if r[0] != "rz"] == [r for r in xtwin if r[0] != "rz"], "a non-rz gate differs")
    _expect(sum(r[0] == "cz" for r in ctrl) > 100, "the routed control holds too few cz to be the case circuit")
    wire = next(r[1][0] for r in ctrl if r[0] == "measure" and r[2] == (4,))

    def stretches(rows_: list[tuple[str, tuple[int, ...], tuple[int, ...], float]]) -> dict[int, float]:
        segment = 0
        total: dict[int, float] = {}
        for name, qubits, _, angle in rows_:
            if wire in qubits and name in ("sx", "x"):
                segment += 1
            elif name == "rz" and qubits == (wire,):
                total[segment] = total.get(segment, 0.0) + angle
        total[-1] = float(segment)
        return total

    a, b = stretches(ctrl), stretches(xtwin)
    _expect(a[-1] == b[-1], "the wire carries different numbers of sx and x gates")
    differing = [
        s
        for s in set(a) | set(b)
        if s >= 0 and abs((a.get(s, 0.0) - b.get(s, 0.0) + np.pi) % (2 * np.pi) - np.pi) > 1e-6
    ]
    _expect(differing == [int(a[-1]) - 1], f"rz angles differ in stretches {differing}, not the last one")
    others = {role: [(row[1], row[3]) for row in rows[role] if row[0] == "rz" and row[1] != (wire,)] for role in rows}
    _expect(bool(others["ctrl"]), "the check saw no rz on another wire")
    _expect(others["ctrl"] == others["xtwin"], "an rz on another wire differs")
