# Cayley-Dickson star-lattice census

`census.json` is the exact census behind the
[star-lattice tower note](../../notes/topics/cd-star-lattice-tower.md).
`scripts/cd_star_lattice.py` derives every entry from
`gororoba_quantum/cd_core.py` (`cd_sign` for the boundary points and unit
products, `sedenion_zero_divisor_corpus` and `left_mult_determinant_exact`
for the sedenion zero divisors) and binds the dimension-2 lattice to the
Tuna-17 couplers of [catalogue.json](../quantum_inspire/catalogue.json).
Values are integers, booleans and index lists; the record carries no floats,
paths, timestamps or worker counts, so pooled and serial
(`GOROROBA_WORKERS=1`) runs write the same bytes.

## Replay

```sh
"$PYTHON" -B -W error scripts/cd_star_lattice.py --check docs/evidence/cd-star-lattice/census.json
```

Gate core-663 runs it: `--check` recomputes the census and requires byte
equality with the canonical JSON (sorted keys, indent 2).
`tests/scripts/test_cd_star_lattice.py`, in the behavioral suite, holds the
contracts and their planted defects: swapped Tuna-17 coordinates fail the
catalogue binding, one reoriented cross-polytope edge drops the quaternion
symmetry from order 24 to 1, and a missing boundary point fails the
one-per-edge check.

## Record layout

| Key | Contents |
|---|---|
| `tuna17` | catalogue coupler count, edge-set equality, boundary qubits, mirror point set distinct |
| `cayley_dickson[]` | dimensions 2, 4, 8, 16: `graph`, `boundary_points`, one-per-edge flag, `boundary_symmetry`, `check_types`, `left_unit_closure` |
| `cayley_dickson[3].sedenion_zero_divisors` | two-blade and corpus counts, unit and boundary zero divisors, the assessor-pair orbit and its 14 extra pairs |
| `tetrahedral_3d` | the same fields for the tetrahedral boundary, plus `octahedron_selections` over all 4096 one-per-edge boundaries |

`boundary_symmetry` describes the group of signed permutation matrices that
maps the boundary set onto itself: order, determinant counts, element-order
profile, stabilizer of e_0 and whether -1 belongs to it. `check_types` lists
the classes of odd sites a CSS code reading full neighborhoods must give one
Pauli type; in dimensions 2 and 3 it also lists every two-type assignment
with its logical-qubit count and least logical weight (searched to weight 3).
