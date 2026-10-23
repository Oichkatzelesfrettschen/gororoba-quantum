# Cayley-Dickson star-lattice census

`census.json` is the exact census behind the
[star-lattice tower note](../../notes/topics/cd-star-lattice-tower.md).
`scripts/cd_star_lattice.py` derives every entry from
`gororoba_quantum/cd_core.py` (`cd_sign` for the boundary points and unit
products, `sedenion_zero_divisor_corpus` and `left_mult_determinant_exact`
for the sedenion zero divisors) and binds the dimension-2 lattice to the
Tuna-17 couplers of [catalogue.json](../quantum_inspire/catalogue.json). The
`identification` block certifies the boundary groups in plain Python: an
explicit lift to SL(2, q) for the groups of dimensions 4 and 8, and the PGL(2, 7)
action on doubling pairs for dimension 16.
Values are integers, booleans and index lists; the record carries no floats,
paths, timestamps or worker counts, so pooled and serial
(`GOROROBA_WORKERS=1`) runs write the same bytes.

## Replay

```sh
"$PYTHON" -B -W error scripts/cd_star_lattice.py --check docs/evidence/cd-star-lattice/census.json
```

Gate core-665 runs it: `--check` recomputes the census and requires byte
equality with the canonical JSON (sorted keys, indent 2).
`tests/scripts/test_cd_star_lattice.py`, in the behavioral suite, holds the
contracts and their planted defects: swapped Tuna-17 coordinates fail the
catalogue binding, one reoriented cross-polytope edge drops the quaternion
symmetry from order 24 to 1, a missing boundary point fails the
one-per-edge check, one flipped skew pair of W_8 fails the conference test
and the Paley equivalence, a corrupted projective-line map fails the SL(2, 3)
lift, and the order-3 stabilizer has a commutant larger than the full
group's.

## Record layout

| Key | Contents |
|---|---|
| `tuna17` | catalogue coupler count, edge-set equality, boundary qubits, mirror point set distinct |
| `cayley_dickson[]` | dimensions 2, 4, 8, 16: `graph`, `boundary_points`, one-per-edge flag, `boundary_symmetry`, `check_types`, `left_unit_closure` |
| `cayley_dickson[3].sedenion_zero_divisors` | two-blade and corpus counts, unit and boundary zero divisors, the assessor-pair orbit and its 14 extra pairs |
| `tetrahedral_3d` | the same fields for the tetrahedral boundary, plus `octahedron_selections` over all 4096 one-per-edge boundaries |
| `identification.arc_matrix_skew_conference` | whether W_n, right multiplication by e_1 + ... + e_{n-1}, is a skew conference matrix, n = 2 to 128 |
| `identification["4"]`, `["8"]` | commutant dimension and basis squares; e_0 stabilizer equal to the table's permutation automorphisms; XOR-linear element count; `paley`: equivalences of W_n to the Paley matrix of q = 3, 7, its automorphism count, projective-line maps in PSL(2, q), line-action kernel, and the SL(2, q) lift |
| `identification["16"]` | the same commutant and stabilizer fields, the right multiplication by e_8 in the commutant; `doubling_pairs`: PGL(2, 7) image of order 336 with kernel {+-1}, derived subgroup equal to the PSL(2, 7) preimage and lifted to SL(2, 7), its two index orbits, and the orbit sizes of the 120 index pairs |

## External replay

[external/nauty_replay.py](external/nauty_replay.py) runs under an interpreter
that imports SageMath and writes
[external/nauty_replay.txt](external/nauty_replay.txt) (SageMath 10.10, GAP
4.16dev). It records the full automorphism group of each lattice graph S_n
(n = 2, 4, 8, 16) through nauty, the signed-permutation centralizer of W_n for
n = 4 to 128 as a labeled-digraph automorphism group, the GAP SmallGroup id of
each order in the library, and the Sylow 2-subgroup, center, involution count
and central quotient of the dimension-16 group. No gate runs it, because the
gate images carry no SageMath; the census backtracker needs 417 s for n = 32
on 32 workers, which keeps n >= 32 out of the gated record.

`boundary_symmetry` describes the group of signed permutation matrices that
maps the boundary set onto itself: order, determinant counts, element-order
profile, stabilizer of e_0 and whether -1 belongs to it. `check_types` lists
the classes of odd sites a CSS code reading full neighborhoods must give one
Pauli type; in dimensions 2 and 3 it also lists every two-type assignment
with its logical-qubit count and least logical weight (searched to weight 3).
