# Exhaustive C881 proof at the latest audited source

The `gororoba-open` HEAD `b977e43f71e8ec22a2eabc83197b649056e63a67`
contains the complete finite minimum-degree proof in
[`proofs/verified/C881_GF2CubicMinDegree.v`](https://github.com/Oichkatzelesfrettschen/gororoba-open/blob/b977e43f71e8ec22a2eabc83197b649056e63a67/proofs/verified/C881_GF2CubicMinDegree.v).
The file rejects every four-variable multilinear polynomial of degree at most
two on the specified fifteen labels and verifies a degree-three
separator. The [fresh replay](../evidence/c881_exhaustive/README.md) compiles
the dependency closure and kernel-checks it using Rocq 9.2 with OCaml 5.5.0.

## Exact change and proof boundary

The earlier [folding audit](open_gororoba_folding_proofs.md) describes source
commit `abbf13c`, where representative quadratic checks leave the exhaustive
lower bound to independent finite code. Upstream commit `85a8ec3c` adds:

- `degree2_monomials_characterization`: the eleven masks are exactly the
  four-variable multilinear monomials of degree at most two, including zero.
- `degree2_candidate_count`: their subsets number 2048.
- `coefficient_support_enumerated`: every Boolean coefficient vector of the
  matching length has a support in that enumeration.
- `degree2_all_candidates_fail` and `degree2_coefficients_fail`: kernel
  reduction rejects the entire finite denominator and the support theorem
  transfers rejection to every eleven-entry coefficient vector.
- `fixed_partition_minimum_separating_degree`: the exhaustive lower bound,
  successful cubic witness, and degree-three calculation hold together.

The label list, class list, and cubic witness remain identical to the values
used by `verify.py`. The local bounded interpolant solver independently
reconstructs the same lower bound. The formal theorem concerns those fixed
lists; it does not parse the runtime Rust dataset, classify all partitions,
or prove quantum query complexity or rank-stratum topology.

Six explicit assumption queries print `Closed under the global context`.
The fresh independent kernel check reports no axioms, type-in-type reliance,
unsafe fixpoints, or assumed positivity. These receipts apply to the complete
finite proof and its `GF2Algebra.v` dependency. Other imported proof families
retain their own compiler and source receipts.

## Replay identities

The latest-source audit reads both files in full, compares the C881 change
against the earlier audited revision, and compiles copied sources in fresh
temporary storage. The replay writes generated proof objects under temporary
storage and reads the source checkout without creating proof objects there.

`verify.py` now requires C881 SHA-256
`e72a6a1ae0ab345e482346c264451abe9acc0b959ac2bee645856d946a461a87`.
The dependency SHA-256 is
`f8e659d01b358c673dd33f2f9eae87285bc165d85b99ec2410f29435c26df7bf`.
The replay checks both the live files and copied inputs. A later change fails
admission until its source and proof receive another joint review.
Earlier manifests and receipts preserve the source versions they actually
checked. They supply historical evidence rather than a reason to select
an obsolete dependency for current validation.
