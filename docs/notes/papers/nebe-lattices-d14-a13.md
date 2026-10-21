# Nebe--Sloane lattice catalogue: D14 and A13 entries

[P] marks a statement on the inspected catalogue pages. [I] marks the
mapping to the repository's lattice identification. The reading covers the
NAME/DIMENSION/DET fields of both entries; the full basis and Gram-matrix
tables were not needed.

## Citation and retrieval

- Source: Catalogue of Lattices, a joint project of Gabriele Nebe (RWTH
  Aachen University) and Neil J. A. Sloane.
- D14 entry: <https://www.math.rwth-aachen.de/~Gabriele.Nebe/LATTICES/D14.html>
- A13 entry: <https://www.math.rwth-aachen.de/~Gabriele.Nebe/LATTICES/A13.html>
- Retrieval: both pages fetched 2026-10-19; response bytes retained only as
  hashes below (external web references, not hosted).
- D14 page: 12,642 bytes,
  SHA-256 `032039560532561fb8a46c81ac6c6e72c3515cc9dfa3143d189be6e9628f7b6a`.
- A13 page: 16,931 bytes,
  SHA-256 `4eb3f2dd31f5fa742d791d6ab4fc457920853c638e9701b76d55e229c2eb75bd`.
- Last modified (per page footers): 18 July 2014 (both entries).

## Mathematical content used

[P] The D14 entry records NAME D14, DIMENSION 14, DET 4.

[P] The A13 entry records NAME A13, DIMENSION 13, DET 14, DIVISORS
1 14 (x12), MINIMAL_NORM 13, KISSING_NUMBER 28, GROUP_NAME C2 x S14.

[I] The MINIMAL_NORM and KISSING_NUMBER fields describe the dual A13*
scaled by 14: A13* has minimal norm 13/14 and kissing number 28 (the
vectors of the classes +/-1 modulo the root lattice). The root lattice A13
itself has minimal norm 2 and kissing number 182 = 14 x 13, its roots
e_i - e_j. The repository's assessor-lattice identification uses rank and
determinant alone, which both readings share.

[I] These are the standard lattice data against which the repository's
computed identifications were checked: the integer span of the 84 both-sign
assessor blades has rank 14 and Gram determinant 4 (D14); the integer span
of the 42 all-plus assessor blades has rank 13 and Gram determinant 14
(A13). The catalogue entries corroborate the (rank, determinant) pairs;
they supply no statement about sedenion assessors.

## Mapping and evidence boundary

[I] The catalogue is used solely as an independent check of lattice
invariants. The generator matrices, Smith normal forms, and the sign-policy
dependence (42 all-plus -> A13; 84 both-sign -> D14) are computed in the
repository from its own sign table, not read from the catalogue.
