"""Contracts of the merged-diagonal members of the orientation-bit kernel map (pathion_kernel_map_orientation_merged).

The merged six-qubit diagonal equals the retained member's operator on both arms for every role and operand, routes
both arms to one CZ count, routes the exchange member to the control's gate counts, and
leaves the algebra mutation test of docs/notes/algebra_circuit_rules.md#hardware-probes in force.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import DiagonalGate
from qiskit.quantum_info import Operator, Statevector

import pathion_kernel_map as pkm
import pathion_kernel_map_orientation as pko
import pathion_kernel_map_orientation_merged as pkm_merged
import qrng_seeds
from experiments import all_experiment_groups, standalone_campaign_groups
from heron_multiprogramming import HERON_BASIS, DisjointTile, HeronLattice

ROOT = Path(__file__).resolve().parents[2]
DRAW_INDEX = 0
ARMS = (0.0, np.pi)


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _unitary(circuit: QuantumCircuit, phase: float) -> Operator:
    return Operator(circuit.remove_final_measurements(inplace=False).assign_parameters({pkm.ORIENTATION: phase}))


@pytest.mark.parametrize("phase", ARMS)
@pytest.mark.parametrize("operand", pko.OPERANDS)
@pytest.mark.parametrize("role", pko.ROLES)
def test_merged_member_equals_the_retained_operator(role: str, operand: tuple[int, int, int], phase: float) -> None:
    merged = pkm_merged.merged_template(role, operand)
    retained = pko.role_template(role, operand)
    _expect(
        _unitary(merged, phase).equiv(_unitary(retained, phase)), f"{role} {operand} phase {phase}: operators differ"
    )
    _expect(
        bool(
            np.allclose(
                pko.outcome_law(merged.assign_parameters({pkm.ORIENTATION: phase})),
                pko.outcome_law(retained.assign_parameters({pkm.ORIENTATION: phase})),
                atol=1e-12,
            )
        ),
        f"{role} {operand} phase {phase}: outcome laws differ",
    )


def _cz_count(circuit: QuantumCircuit, phase: float) -> int:
    bound = circuit.assign_parameters({pkm.ORIENTATION: phase})
    return int(transpile(bound, basis_gates=list(HERON_BASIS), optimization_level=1).count_ops().get("cz", 0))


@pytest.mark.parametrize("operand", pko.OPERANDS)
def test_both_arms_carry_one_cz_count_below_the_retained_count(operand: tuple[int, int, int]) -> None:
    for role in pko.ROLES:
        merged = pkm_merged.merged_template(role, operand)
        retained = pko.role_template(role, operand)
        counts = {_cz_count(merged, phase) for phase in ARMS}
        _expect(len(counts) == 1, f"{role} {operand}: the arms route to CZ counts {counts}")
        _expect(
            counts.pop() < min(_cz_count(retained, phase) for phase in ARMS) - 25,
            f"{role} {operand}: the merged member saves fewer than 25 logical CZ",
        )


def test_group_matches_the_retained_member_order_names_and_laws() -> None:
    merged = pkm_merged.pathion_kernel_map_orientation_merged_group()
    retained = pko.pathion_kernel_map_orientation_group()
    _expect(merged.name == "pathion_kernel_map_orientation_merged", f"group name {merged.name}")
    _expect([m.name for m in merged.members] == [m.name for m in retained.members], "member names or order differ")
    for a, b in zip(merged.members, retained.members, strict=True):
        _expect(bool(np.allclose(a.ideal, b.ideal, atol=1e-12)), f"{a.name}: ideal law differs")
    ideal = {member.name: member.ideal for member in merged.members}
    summary = merged.summarize(ideal)
    for role in pko.ROLES:
        for operand in pko.OPERANDS:
            key = f"{pko.unit_name(role, operand)}_nullity_estimate"
            _expect(abs(summary[key] - pkm.nullity(operand)) < 1e-9, f"{key} reads {summary[key]}")


def test_group_is_registered_once_beside_the_retained_group() -> None:
    names = [group.name for group in standalone_campaign_groups()]
    _expect(names.count("pathion_kernel_map_orientation_merged") == 1, "merged group not registered exactly once")
    _expect(names.count("pathion_kernel_map_orientation") == 1, "retained group lost its registration")
    all_names = [group.name for group in all_experiment_groups()]
    _expect(len(all_names) == len(set(all_names)), "a group name repeats")


def _contrast(operand: tuple[int, int, int], signs: list[float]) -> np.ndarray:
    """Per-output contrast of the moved member built around the given six-qubit diagonal."""
    i, j, t = operand
    data = pkm.DATA
    laws = []
    for phase in (np.pi, 0.0):
        qc = QuantumCircuit(data + 1)
        qc.h(range(data))
        qc.p(phase, pko.MOVED_BIT)
        qc.h(data)
        if t < 0:
            qc.z(data)
        qc.append(DiagonalGate(signs), range(data + 1))
        for b in range(data):
            if i >> b & 1:
                qc.x(b)
        for b in range(data):
            if (i ^ j) >> b & 1:
                qc.cx(data, b)
        qc.h(data)
        laws.append(np.asarray(Statevector(qc).probabilities()))
    return pkm.output_contrast(laws[0], laws[1])


@pytest.mark.parametrize("operand", pko.OPERANDS)
def test_mutated_select_changes_the_merged_ideal_observable(operand: tuple[int, int, int]) -> None:
    """Mutation test of the algebra rules: the honest merged diagonal keeps the half-sum at N, and removing the
    cocycle (the oracle alone on both selector values) or negating one joint sign moves it, as for the retained
    member."""
    n = pkm.nullity(operand)
    signs = pkm_merged.merged_signs(operand, pko.MOVED_BIT)
    honest = _contrast(operand, signs)
    _expect(abs(honest.sum() / 2 - n) < 1e-9, f"{operand}: honest half-sum differs from N")
    oracle = pko.orientation_signs(operand, False, pko.MOVED_BIT)
    free = _contrast(operand, oracle + oracle)
    _expect(abs(free.sum() / 2 - n) > 1.5, f"{operand}: the cocycle-free diagonal left the half-sum near N")
    mutated = list(signs)
    mutated[pkm.DIM + 3] = -mutated[pkm.DIM + 3]
    flipped = _contrast(operand, mutated)
    _expect(abs(flipped.sum() / 2 - n) > 0.5, f"{operand}: one negated joint sign left the half-sum at N")


@pytest.fixture(scope="module")
def snapshot_tile() -> tuple[HeronLattice, DisjointTile]:
    lattice = HeronLattice.from_snapshot(ROOT / "docs/evidence/heron_platform/targets.json", "ibm_fez")
    return lattice, lattice.find_disjoint_tiles(6, min_buffer_distance=2, max_tiles=1)[0]


@pytest.mark.parametrize("operand", pko.OPERANDS)
def test_merged_exchange_compiles_to_the_controls_gate_counts(
    snapshot_tile: tuple[HeronLattice, DisjointTile], operand: tuple[int, int, int]
) -> None:
    """On the snapshot tile at optimization level 3 the merged exchange member routes to the control's cz, sx, x and
    measure counts. The gate order is not pinned: over ten transpiler seeds the non-rz sequence of the two members
    agrees in five or six of ten (the retained members agree in ten of ten), so a dry run checks the sequence on its own
    compile (docs/design/pathion-kernel-map-orientation-merged.md)."""
    lattice, tile = snapshot_tile
    seed = qrng_seeds.resolve(f"qrng:docs/evidence/anu_qrng/draw-2026-11-24T022126Z.json#{DRAW_INDEX}")[0]
    counts = {}
    for role in ("ctrl", "xtwin"):
        template = pkm_merged.merged_template(role, operand).assign_parameters({pkm.ORIENTATION: 0.0})
        routed = transpile(
            template,
            coupling_map=lattice.tile_coupling_map(tile),
            basis_gates=list(HERON_BASIS),
            optimization_level=3,
            seed_transpiler=seed,
        )
        counts[role] = dict(routed.count_ops())
    _expect(counts["ctrl"]["cz"] > 60, "the routed control holds too few cz to be the case circuit")
    for name in ("cz", "sx", "x", "measure"):
        _expect(counts["ctrl"][name] == counts["xtwin"][name], f"{operand}: {name} counts differ: {counts}")
    _expect(abs(counts["ctrl"]["rz"] - counts["xtwin"]["rz"]) <= 1, f"{operand}: rz counts differ by more than one")
