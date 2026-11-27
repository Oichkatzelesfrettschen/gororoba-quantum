"""Complex coset blocks of the pathion kernel map of A_5 on bounded fixtures."""

from __future__ import annotations

import itertools

import a5_complex_kernel_map_statevector as record
import numpy as np
import pytest

import parallel
import pathion_complex_block as pcx
import pathion_coset_block as pcb

# (pair, subspace basis, N of the real map, N of the complex map)
OPERANDS = (
    ((1, 3), (2,), 0, 16),
    ((1, 26), (27, 4, 9), 4, 12),
    ((1, 10), (11, 4), 8, 8),
    ((1, 18), (19, 4, 8), 12, 4),
)


def require(condition: bool) -> None:
    if not condition:
        raise AssertionError


def block(pair: tuple[int, int], basis: tuple[int, ...], coset: int) -> pcb.Block:
    return pcb.Block("t", (*pair, 1), pcx.normalized_basis((*pair, 1), basis), coset)


@pytest.mark.parametrize(("pair", "basis", "n_real", "n_complex"), OPERANDS)
def test_every_coset_reads_the_nullity_in_every_phase(
    pair: tuple[int, int], basis: tuple[int, ...], n_real: int, n_complex: int
) -> None:
    nb = pcx.normalized_basis((*pair, 1), basis)
    for coset in pcb.cosets(nb):
        b = pcb.Block("t", (*pair, 1), nb, coset)
        require(abs(16 * pcx.selector_marginal(b, 1) - n_real) < 1e-9)
        require(abs(16 * pcx.selector_marginal(b, 1j) - n_complex) < 1e-9)
        require(abs(16 * pcx.selector_marginal(b, -1j) - n_complex) < 1e-9)
    require(record.exact_nullity(*pair, 1) == n_real)
    require(record.exact_nullity(*pair, 1j) == n_complex)


@pytest.mark.parametrize(("pair", "basis", "n_real", "n_complex"), OPERANDS)
def test_gate_form_folded_law_and_six_qubit_map_agree(
    pair: tuple[int, int], basis: tuple[int, ...], n_real: int, n_complex: int
) -> None:
    nb = pcx.normalized_basis((*pair, 1), basis)
    worst = 0.0
    for coset in pcb.cosets(nb):
        b = pcb.Block("t", (*pair, 1), nb, coset)
        size = 1 << b.d
        labels = pcb.output_labels(b)
        for label in ("1", "i", "-i"):
            for plus in (False, True):
                folded = pcx.block_law(b, pcx.PHASES[label], plus)
                gates = pcb.block_law(pcx.block_circuit(b, label, plus, measure=False))
                six = record.law(record.kernel_map(*pair, pcx.PHASES[label], plus))
                restricted = [six[labels[y] + 32 * s] * 32 / size for y in range(size) for s in (0, 1)]
                worst = max(
                    worst,
                    float(np.abs(gates - folded).max()),
                    max(
                        abs(folded[y + size * s] - six[labels[y] + 32 * s] * 32 / size)
                        for y in range(size)
                        for s in (0, 1)
                    ),
                )
                require(len(restricted) == 2 * size)
    require(worst < 1e-12)


def test_real_and_complex_circuits_share_one_gate_skeleton() -> None:
    b = block((1, 26), (27, 4, 9), 1)
    skeletons = set()
    for label in ("1", "i", "-i"):
        for plus in (False, True):
            circuit = pcx.block_circuit(b, label, plus, measure=False)
            skeletons.add(
                tuple((i.operation.name, tuple(circuit.find_bit(q).index for q in i.qubits)) for i in circuit.data)
            )
    require(len(skeletons) == 1)
    template = pcx.block_template(b, measure=False)
    require({p.name for p in template.parameters} == {"orientation", "phase"})


def test_template_refuses_a_basis_with_bit_h_beyond_vector_zero() -> None:
    with pytest.raises(ValueError):
        pcx.block_template(pcb.Block("t", (1, 26, 1), (27, 4, 9 | 16), 0))


@pytest.mark.parametrize(("pair", "basis", "tile_sum"), [((1, 3), (2,), -14), ((1, 26), (27, 4, 9), -2)])
def test_plain_phases_read_the_tile_sum_of_the_six_qubit_mutation(
    pair: tuple[int, int], basis: tuple[int, ...], tile_sum: int
) -> None:
    nb = pcx.normalized_basis((*pair, 1), basis)
    readings = [pcx.selector_marginal(pcb.Block("t", (*pair, 1), nb, c), 1j, plain=True) for c in pcb.cosets(nb)]
    require(abs(16 * float(np.mean(readings)) - tile_sum) < 1e-9)
    require(record.reading(*pair, 1j, plain=True)["half_sum"] == tile_sum)
    require(min(readings) < 0 < 16 * pcx.selector_marginal(pcb.Block("t", (*pair, 1), nb, pcb.cosets(nb)[0]), 1j))


def test_qubit_count_follows_the_denominator_of_n_over_16() -> None:
    dims = {(n_real, n_complex): len(basis) for _, basis, n_real, n_complex in OPERANDS}
    require(dims == {(0, 16): 1, (4, 12): 3, (8, 8): 2, (12, 4): 3})


STRATUM_DIMENSION = {0: 1, 16: 1, 8: 2, 4: 3, 12: 3}


def uniform_subspace_exists(pair: tuple[int, int]) -> bool:
    """Whether some subspace of dimension d(N) holding m reads N / 16 on every coset in the three phases."""
    n_real, n_complex = record.exact_nullity(*pair, 1), record.exact_nullity(*pair, 1j)
    d = STRATUM_DIMENSION[n_complex]
    m = pair[0] ^ pair[1]
    seen: set[frozenset[int]] = set()
    for rest in itertools.combinations(range(1, 32), d - 1):
        members = frozenset(pcb.span((m, *rest)))
        if len(members) != 1 << d or members in seen:
            continue
        seen.add(members)
        nb = pcx.normalized_basis((*pair, 1), (m, *rest))
        if all(
            abs(16 * pcx.selector_marginal(pcb.Block("t", (*pair, 1), nb, c), t) - n) < 1e-9
            for c in pcb.cosets(nb)
            for t, n in ((1, n_real), (1j, n_complex), (-1j, n_complex))
        ):
            return True
    return False


@pytest.mark.audit
def test_every_pair_of_imaginary_units_reads_n_on_every_coset_of_a_subspace_of_dimension_d_of_n() -> None:
    pairs = list(itertools.combinations(range(1, 32), 2))
    results = parallel.ordered_map(uniform_subspace_exists, pairs, min_items=1)
    require(len(pairs) == 465 and all(results))
