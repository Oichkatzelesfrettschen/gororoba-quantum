# Kernel certificates of left multiplication at the canonical points of the A_5 nullity strata

Two Rocq files extend the commutative-ring tower of
[cd-tower-ring](../cd-tower-ring/README.md) and the base change of
[cd-tower-ring-base-change](../cd-tower-ring-base-change/README.md):

- [CdTowerKernelCertificate.v](../../../proofs/CdTowerKernelCertificate.v)
  turns three finite checks over a source ring into a description of the
  kernel of z -> y z over every commutative ring that receives a homomorphism
  from it;
- [CdTowerCanonicalKernels.v](../../../proofs/CdTowerCanonicalKernels.v)
  applies it over Z to one integer point y of each of the twelve orbits of
  nullity 8, 12 and 16 of the 32-dimensional Cayley-Dickson algebra.

The result, for each point: the kernel of left multiplication by y contains n
explicit vectors, d times every kernel element is a combination of them, and
where the image of d is invertible the kernel is the free module on them. Here
n is the nullity (8, 12 or 16) and d is 2 at eleven points and 50 at the point
of V.

## The certificate

For an element y of level k over a ring A, a certificate is a scalar d, n
vectors v_j, n coordinate functionals f_j and a table `back` of 2^k images
with

| Check over A | Statement |
| --- | --- |
| `vectors_annihilated` | y v_j = 0 for j below n |
| `splitting_on_basis` | d e_i = back(y e_i) + sum_j f_j(e_i) v_j for the 2^k basis vectors e_i |
| `functionals_dual` | f_j(v_l) = d for j = l and 0 otherwise |

In matrix form, with L the matrix of z -> y z, V the matrix of the vectors,
C that of the functionals and P that of `back`: L V = 0, d I = P L + V C and
C V = d I_n.

## Theorems of `KernelCertificate`, for a ring homomorphism h from A to B

`tmap` applies h to every coordinate (`BaseChange`).

| Theorem | Statement over B |
| --- | --- |
| `kernel_vectors` | y v_j = 0 |
| `combination_annihilated` | y (sum_j a_j v_j) = 0 for all coefficients a_j |
| `splitting` | h(d) z = back(y z) + sum_j f_j(z) v_j for every z |
| `kernel_spanned` | y z = 0 implies h(d) z = sum_j f_j(z) v_j |
| `coefficients_recovered` | f_l(sum_j a_j v_j) = h(d) a_l |
| `kernel_free_basis` | with an inverse of h(d): y z = 0 exactly when z = sum_j (inverse f_j(z)) v_j |
| `kernel_coefficients_unique` | with an inverse of h(d): the coefficients of a combination are inverse f_l of it |

The last two say that the kernel is the free B-module on v_0, ..., v_(n-1).
The proofs check the identities on the basis vectors over A and extend them
by `tmap_basis`, `tmap_mul`, `target_map_tmap` and `RingTowerBasis.linear_ext`;
no ordering, division or characteristic hypothesis enters before the inverse
of h(d).

## The twelve points

The points are the representatives `REPS` of
`docs/evidence/a5-strata-regularity/strata_regularity.py`, given there in
split coordinates z'_1, ..., z'_15. A doubly pure y has z_k = y_k + i y_(16+k)
and z_k = i^popcount(k) z'_k, so integer split coordinates give integer
coordinates y_k = Re z_k and y_(16+k) = Im z_k.

| Point | Nonzero coordinates of y | Nullity n | d | Smith invariants of L |
| --- | --- | --- | --- | --- |
| `W8` | e_17 - e_27 | 8 | 2 | 1 (16 times), 2 (8 times) |
| `Ehat` | -e_3 - 5 e_9 - 2 e_10 + 3 e_17 + e_18 + 4 e_24 - 2 e_27 | 8 | 2 | 1 (16), 2 (8) |
| `Iso` | -e_3 - e_10 + e_17 - e_29 | 8 | 2 | 1 (16), 2 (8) |
| `Xp` | -e_3 - e_9 + e_17 + e_18 | 8 | 2 | 1 (16), 2 (8) |
| `Xm` | -e_3 + e_9 + e_17 + e_18 | 8 | 2 | 1 (16), 2 (8) |
| `B9` | -e_3 - 2 e_6 - 3 e_9 - 5 e_12 + e_17 + 2 e_20 - 3 e_27 - 5 e_30 | 12 | 2 | 1 (16), 2 (4) |
| `V` | -5 e_9 + 3 e_17 + 4 e_24 | 12 | 50 | 1 (16), 50 (4) |
| `VB` | -e_3 + e_17 | 12 | 2 | 1 (16), 2 (4) |
| `Vap` | -e_9 + e_17 | 12 | 2 | 1 (16), 2 (4) |
| `Vam` | e_9 + e_17 | 12 | 2 | 1 (16), 2 (4) |
| `Np` | -e_3 - e_9 + e_17 - e_27 | 16 | 2 | 1 (8), 2 (8) |
| `Nm` | -e_3 + e_9 + e_17 + e_27 | 16 | 2 | 1 (8), 2 (8) |

The scalar d is the largest Smith invariant of L, so it is the least integer
for which the splitting has integer entries. For each point the file states
`<point>_kernel_vectors`, `<point>_kernel_spanned`,
`<point>_coefficients_recovered` and `<point>_kernel_free_basis` over every
commutative ring D, with h the homomorphism from Z (`IntegerHom`). `Mod7`
instantiates the functor at Zmod 7, where 2 4 = 1 and 50 = 1, and
`<point>_kernel_mod7` discharges the inverse, so the hypotheses have a model.

## Scope

- The theorems describe the kernel at twelve points, one per orbit. No Rocq
  statement here says that the nullity is constant on an orbit, that the
  twelve orbits exhaust the elements of nullity at least 8, or that the
  nullity takes only the values 0, 4, 8, 12 and 16; those rest on the group
  action and the Pfaffian equations of the strata scripts (computed).
- Over a ring in which the image of d is a zero divisor or zero the theorems
  give the containment of the n vectors in the kernel and `kernel_spanned`,
  and no rank. The test below computes the rank of L modulo 2 at every point
  and modulo 5 at the point of V: the nullity there is larger than n
  (computed, not proved in Rocq).
- The point of V is one representative, with y y = -50; another point of the
  orbit has another d. The value 50 is a property of the representative.
- The identity of the pair-tower product with `cd_sign` is the chain of
  proofs named in [cd-tower-ring](../cd-tower-ring/README.md) ("Binding to
  cd_core"). The certificates were computed with `cd_sign` and are accepted
  by the Rocq product on all twelve points; that agreement is a computed
  check of the binding at these inputs, not a further theorem.
- The complex points of the strata (kernels over Q(i) and the complex fiber)
  are covered through base change: Q(i) receives Z and 2 and 50 are
  invertible in it. A point whose own coordinates are not integers needs a
  certificate over its ring of definition, by the same functor.

## Binding to cd_core and to the strata representatives

[certificates.json](certificates.json) holds the integer data of the twelve
certificates. [kernel_certificates.py](kernel_certificates.py) `--check`
recomputes each y from `REPS` and each L from `cd_core.cd_sign`, verifies the
three matrix identities in integer arithmetic, compares the nullity and d
with python-flint's rank and Smith form, and requires
`proofs/CdTowerCanonicalKernels.v` to be the rendering of the JSON, so the
Rocq tables are the checked ones. `--generate` recomputes the certificates
from a unimodular diagonalization and an LLL reduction of the kernel basis
and rewrites both files; the rendering is deterministic, the reduction need
not reproduce the same basis on another python-flint version, and `--check`
does not depend on it.

`tests/gororoba_quantum/test_cd_tower_kernel_certificates.py` runs the same
identities under the `tests` check, compares the nullities with the table
`NULLITY` of the strata script, computes the rank of L modulo 2, 3, 5, 7,
32009 and 32029 (nullity n when the prime does not divide d, larger when it
does), and requires three mutated inputs to fail: the W8 point with the sign
of e_27 flipped, one changed kernel vector entry, and a doubled d.

## Assumptions

[assumptions.txt](assumptions.txt) holds 21 `Print Assumptions` queries on the
Zmod 7 instance, the twelve `<point>_kernel_mod7` and nine statements of
three points; every one reads "Closed under the global context".
[statements.txt](statements.txt) prints the five generic theorems and three
of the instance theorems. [kernel.txt](kernel.txt) is the `rocq check`
context of the two libraries: it lists no axiom. No proof introduces an axiom
or an `Admitted`.

## Replay

```sh
ROCQ="${ROCQ:-rocq}" sh docs/evidence/cd-tower-kernel-certificates/replay_rocq.sh
sha256sum -c docs/evidence/cd-tower-kernel-certificates/source_hashes.sha256
"$PYTHON" -B -W error docs/evidence/cd-tower-kernel-certificates/kernel_certificates.py --check
```

`replay_rocq.sh` requires the banner of [toolchain.txt](toolchain.txt) (Rocq
9.3.0 on OCaml 5.5.1, the switch of `ci/rocq_toolchain.pin`), compiles
`CdTwistedProduct.v`, `CdTowerRing.v`, `CdTowerRingBasis.v`,
`CdTowerRingBaseChange.v`, the two files of this bundle,
[assumptions.v](assumptions.v) and [statements.v](statements.v) in temporary
storage with `-w @all`, fails on any warning or compiler output, runs
`rocq check` over the two libraries, and compares the outputs byte for byte
with the three receipts. Its mutation control replaces the coordinate -1 of
the W8 point by 1 in a copy of the file and requires the compile to fail at
j = 0 of `W8_vectors_annihilated`. The replay takes about three minutes on
the build host, most of it in `rocq check`, which re-reduces the `vm_compute`
steps with its own conversion.
`scripts/rocq_kaggle_replay.py --only cd-tower-kernel-certificates` selects
the replay and `source_hashes.sha256` binds the two sources, the certificate
data, the generator and the receipts.
