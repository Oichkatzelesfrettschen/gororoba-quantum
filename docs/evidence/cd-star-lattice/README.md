# Cayley-Dickson star-lattice census

`census.json` is the exact census behind the
[star-lattice tower note](../../notes/topics/cd-star-lattice-tower.md).
`scripts/cd_star_lattice.py` derives every entry from
`gororoba_quantum/cd_core.py` (`cd_sign` for the boundary points and unit
products, `sedenion_zero_divisor_corpus` and `left_mult_determinant_exact`
for the sedenion zero divisors) and binds the dimension-2 lattice to the
Tuna-17 couplers of [catalogue.json](../quantum_inspire/catalogue.json). The
`identification` block identifies the boundary groups by exact finite
computation in plain Python: an explicit lift to SL(2, q) for the groups of
dimensions 4 and 8, and the PGL(2, 7) action on doubling pairs for dimension
16, each checked against the complete group the backtracker enumerates.
Values are integers, booleans and index lists; the record carries no floats,
paths, timestamps or worker counts, so pooled and serial
(`GOROROBA_WORKERS=1`) runs write the same bytes.

## Replay

```sh
"$PYTHON" -B -W error scripts/cd_star_lattice.py --check docs/evidence/cd-star-lattice/census.json
```

Gate `core-record-check-06` (`tests/test_cli_record_checks.py`) runs it: `--check` recomputes the census and requires byte
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
| `identification.doubling_blocks_match_cd_sign` | whether left and right multiplication by the imaginary sum at n equal the block recurrence assembled from dimension n/2, n = 4 to 128: the link from cd_sign to the written conference induction of the tower note |
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

[external/hadamard_replay.py](external/hadamard_replay.py) writes
[external/hadamard_replay.txt](external/hadamard_replay.txt). It places
I + W_16 and the sedenion sign table among the five equivalence classes of
Hadamard matrices of order 16 in
[external/mckay_had16.txt](external/mckay_had16.txt), Brendan McKay's list
retained unmodified from https://users.cecs.anu.edu.au/~bdm/data/hadamard/had16.txt
(sha256 `67fb6f1a36f6893fca541a85754329812b9b8b454b3438ec9b6fd00005c2f170`) under McKay's
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) grant for the collection's data files,
and counts the Hadamard automorphism pairs of I + W_n for n = 4 to 64. Classes
carry the file's line numbers; the [source note](../../notes/papers/mckay-hadamard-matrices.md)
records the page's equivalence relation and that it maps no line to Hall's or
Sloane's labels.

`boundary_symmetry` describes the group of signed permutation matrices that
maps the boundary set onto itself: order, determinant counts, element-order
profile, stabilizer of e_0 and whether -1 belongs to it. `check_types` lists
the classes of odd sites a CSS code reading full neighborhoods must give one
Pauli type; in dimensions 2 and 3 it also lists every two-type assignment
with its logical-qubit count and least logical weight (searched to weight 3).
