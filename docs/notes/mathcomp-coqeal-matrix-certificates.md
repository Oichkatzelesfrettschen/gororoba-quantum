# MathComp and CoqEAL: sound exact matrix certificates

Primary software sources inspected:

- Mathematical Components team, [MathComp commit
  `9931c887da3d50ffb2a2e1b2e33b52ec9178a755`](https://github.com/math-comp/math-comp/tree/9931c887da3d50ffb2a2e1b2e33b52ec9178a755).
- Guillaume Cano, Cyril Cohen, Maxime Dénès, Érik Martin-Dorel, Anders
  Mörtberg, Damien Rouhling, Pierre Roux, and Vincent Siles, [CoqEAL commit
  `8fd26cf416ce0dfb5e9a9745293bdedf63b56d39`](https://github.com/coq-community/coqeal/tree/8fd26cf416ce0dfb5e9a9745293bdedf63b56d39).

These are pinned development snapshots, not claimed released packages.
MathComp supplies the mathematical matrix statements; CoqEAL supplies
representation-refinement interfaces for efficient exact computations.

## Inspected matrix theorem APIs

[P] In MathComp `algebra/mxalgebra.v`, over a `fieldType`:

| API | Exact useful content |
| --- | --- |
| `mulmx1_min_rank` | `M * A * N = I_r` implies `r <= rank(A)` |
| `mulmx_max_rank` | For `B:m*r`, `C:r*n`, `rank(B*C) <= r` |
| `mxrank_tr` | Transposition preserves rank |
| `mulmx_ker` | `kermx(A) * A = 0` |
| `sub_kermxP` | Reflection between `B*A=0` and row-space inclusion in `kermx(A)` |
| `mxrank_ker` | `rank(kermx(A)) = m-rank(A)` for `A:m*n` |
| `mulmx_coker`, `mxrank_coker` | `A*cokermx(A)=0` and its rank is `n-rank(A)` |
| `rank_diag_block_mx` | A block-diagonal matrix has the sum of block ranks |

[P] MathComp's `kermx` describes the **left** kernel through row spaces. The
repository's `L_x y=0` convention uses column vectors. A bridge must transpose
the problem or explicitly use the right-nullspace identities; copying a
`kermx` name into a column-vector claim would change the statement.

[I] A compact certificate for `rank(A)=r` can provide `B,C,M,N` satisfying
`A=B*C` and `M*A*N=I_r`. The two named rank lemmas give matching upper and
lower bounds. The checker only needs to validate dimensions and exact matrix
equalities. External Gaussian elimination can propose the witnesses without
joining the trusted computing base. This scheme is a proposed repository
checker, not an upstream theorem that already parses repository records.

[I] For a full nullspace basis, also check `A*V=0`, independence of the columns
of `V`, and the certified dimension `n-r`. A zero residual alone proves only
inclusion in the kernel. Kernel completeness, block-sector covers, and every
pivot inequation must remain explicit when transporting a certificate into
the principal skew atlas and its overlap maps.

## Efficient representation bridge

[P] CoqEAL `refinements/binrat.v` relates MathComp `rat` to BigNums `bigQ`
through `r_ratBigQ`. Inspected instances include `refine_ratBigQ_add`,
`refine_ratBigQ_mul`, `refine_ratBigQ_inv`, and `refine_ratBigQ_eq`.
`refinements/seqmx.v:RseqmxC` relates typed matrices to sequence matrices,
given the scalar and index refinement hypotheses. `refine_mul_seqmx` proves
the multiplication refinement; the neighboring equality instance relates
the Boolean equality test to its abstract matrix counterpart.

[I] Compose those bridges with a proved rational-number decoder and matrix
shape checker, then prove `checker=true -> certificate_equations`. Shape
checks must reject truncated/ragged matrices and incorrect declared sizes.
The repository's signed basis recursion must be proved to generate the same
matrix as the mathematical multiplication operator. A source hash binds a
particular generated matrix, but cannot replace that correspondence theorem.

[I] The first implementation should specialize to one retained finite matrix
and exact rational field. General real parameter families need polynomial
identities, domain assumptions, specialization/field-embedding arguments,
and rank-changing pivot conditions. Checking many rational matrices cannot
prove a statement about every real point in a stratum.

## Compatibility, foundations, rights, and scope

[P] The inspected MathComp development's `rocq-mathcomp-boot.opam` requires
Rocq >=9.1 and Hierarchy Builder >=1.9.0. CoqEAL's `rocq-coqeal.opam` requires
Rocq >=9.0 and <9.3 (or dev), Hierarchy Builder >=1.9.0, MathComp ssreflect
>=2.5, Multinomials >=2.4, and real-closed >=2.0.3. Its generated README lists
some older minimums; use the pinned package metadata for dependency solving.
The pass did not build either snapshot with Rocq 9.1.1 or establish that the
two snapshots form a jointly installable release configuration.

[I] Retain `Print Assumptions` for the actual closed checker theorem and an
independent kernel check. Upstream source reading is not a proof replay.
Mathematical structure parameters such as `fieldType`, validated scalar
refinement instances, classical foundations if imported, arithmetic
evaluation, external data parsing, and extraction belong to distinct trust
boundaries. Require a closed instantiated checker rather than interpreting a
generic refinement theorem with uninstantiated hypotheses as final evidence.

MathComp's pinned `LICENCE` and package metadata identify CeCILL-B. CoqEAL's
pinned `LICENSE` identifies MIT, with its copyright and notice conditions.
Those grants apply to their software; related research papers require their
own rights evidence. This note uses primary source code as the reference and
does not assign either software license to a paper.

Reading scope: source READMEs/package metadata/licenses; the listed MathComp
matrix definitions/statements/proofs; CoqEAL `RseqmxC` context, multiplication
and equality refinement instances, and named rational instances. Full
Gaussian elimination, Smith normal form, all imported dependencies, and
extracted implementation validation remain outside the inspected scope.

Unchanged source archive: [mathcomp-9931c88.tar.gz](../source_archives/mathcomp-9931c88.tar.gz).
Retrieval: https://codeload.github.com/math-comp/math-comp/tar.gz/9931c887da3d50ffb2a2e1b2e33b52ec9178a755

Archive SHA-256: `f38e8146ff310acbf286cc50f6258f29f72a8ed92f2af788921befcd817c875e`.

Unchanged source archive: [coqeal-8fd26cf.tar.gz](../source_archives/coqeal-8fd26cf.tar.gz).
Retrieval: https://codeload.github.com/coq-community/coqeal/tar.gz/8fd26cf416ce0dfb5e9a9745293bdedf63b56d39

Archive SHA-256: `46705ae13ab008ad6f5492c3a703f871ea12a1249c9dc92a6bd8bbcb313494fe`.
