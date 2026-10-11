# Cayley-Dickson rank loci and attachment topology: source ledger

The review checked primary sources for spectral multiplicity, exact rank
polynomials, kernel doubling, and homotopy of attached cylinders. The resulting
[RANK_STRATUM_TOPOLOGY.md](../../gororoba_quantum/RANK_STRATUM_TOPOLOGY.md)
separates exhaustive algebraic membership tests from complete geometric
classification. Source claims and local deductions are identified below.

## Primary statements used

| Source and version | Checked locator | Statement and boundary |
| --- | --- | --- |
| Daniel K. Biss, J. Daniel Christensen, Daniel Dugger, Daniel C. Isaksen, [Eigentheory of Cayley-Dickson algebras, 0905.2987v1](https://arxiv.org/html/0905.2987v1), 19 May 2009; Forum Mathematicum 21 (2009), 833-851, DOI `10.1515/FORUM.2009.041` | Lemma 2.3; Lemma 3.8; Propositions 3.9, 3.13, 3.20; Lemma 3.16 | `L_x^T=L_conj(x)`; `ker(L_x^T L_x)=ker L_x`; nonnegative spectrum; normalized eigenvalue one; every real eigenspace dimension divisible by four for `n>=2`; trace equals `2^n*||x||^2` |
| Shoot Koebisu, [Determinant Factorization of Left Multiplication in the 32-Dimensional Cayley-Dickson Algebra, 2608.08232v1](https://arxiv.org/html/2608.08232v1), 8 August 2026 | Definitions 3.1/3.3; Proposition 4.3; Theorem 5.3; Corollary 7.1 | Exact trace/Newton construction; `E_7` has degree 14 and `det L_x=N^2*E_7^2`; nonzero `x` is a zero divisor exactly when `E_7=0` |
| Same Koebisu paper | Theorem 9.1 | For every `n>=2`, remove one fourfold block `N`, use `m=2^(n-2)-1`, and obtain `det L_x=N^2*E_m^2`; this is a determinant identity, rather than a topological classification |
| Same Koebisu paper | Proposition 8.3 and Appendix B | The complexified witness `e4+e10-e23+i*(e11-e16+e18)` has `N=0` and `E_7=-512`; the real norm polynomial does not divide `E_7` |
| Biss, Dugger, Isaksen, [Large annihilators in Cayley-Dickson algebras, math/0511691v1](https://arxiv.org/html/math/0511691v1) | Theorem 10.1 | For `a` perpendicular to `C_n` and `alpha^2+beta^2!=0`, `Ann(alpha*a,beta*a)=Ann(a) x Ann(a)`; the choice `(alpha,beta)=(1,0)` gives the full kernel-doubling identity used in the restricted all-dimensional construction |
| Same annihilator paper | Theorem 9.8; Proposition 9.10; Theorem 13.2 | Nonzero-element nullity is a multiple of four at most `2^n-4n+4`; every allowed multiple occurs |
| Same annihilator paper; 2009 Eigentheory paper | Corollary 9.3 and Lemma 9.5; Section 2.1 | Zero products are symmetric; every zero divisor and its annihilator lie in `C_n^perp`; the complex inner product is the projection of `x*conj(y)` onto `C_n` |
| Biss, Christensen, Dugger, Isaksen, [Large annihilators in Cayley-Dickson algebras II, math/0702075v2](https://arxiv.org/html/math/0702075v2) | Theorems 7.5 and 8.12 | A constrained `A5` D-locus is an `S5`-bundle; fixed-deficit near-maximum element families satisfy a stability theorem. Neither statement identifies the complete normalized pair space |
| Allen Hatcher, [Algebraic Topology, Chapter 0](https://pi.math.cornell.edu/~hatcher/AT/ATch0.pdf), printed pages 15-16 | Propositions 0.17 and 0.18 | Collapsing a contractible subspace with the homotopy extension property preserves homotopy type; homotopic attaching maps for a CW pair produce homotopy-equivalent adjunction spaces |

The 2009 paper's proof of Proposition 3.20 reduces to a vector perpendicular
to `C_n` using Proposition 3.10, then uses a conjugate-linear anti-Hermitian
operator to obtain even complex eigenspace dimensions. The theorem applies
to arbitrary real coefficient vectors; restricting to sparse vectors or to
already-known zero divisors would weaken its stated domain unnecessarily.

The Koebisu paper uses the repository's multiplication convention. The full
main text, Newton formula, and complexified certificate were read. Its
Discussion, question 4, explicitly asks for the geometric description of the
zero-divisor strata according to kernel dimension. The present polynomial
rank predicates supply an exact membership description; their derivation
alone supplies no connected-component or attachment classification.
Its complexified certificate extends the Cayley-Dickson conjugation linearly
over the complex coefficient field: `N=sum z_i^2` and `B=L_z^T*L_z` use
bilinear transpose, rather than Hermitian conjugation. Spectral positivity and
the repository's exact point evaluator retain their real-domain hypotheses;
the complex witness remains a separately identified source certificate.

A wording caveat in Koebisu's Remark 4.2 is immaterial to the construction:
ordered eigenvalues of real symmetric matrices admit continuous labeling.
Eigenvectors and a chosen distinguished eigenvalue block need more care at
collisions. The trace/Newton derivation uses symmetric functions and avoids
making any labeling assumption; the repository does not adopt the stronger
claim that continuous eigenvalue labeling is impossible.

## Deductions used by the repository

The following statements follow from the source theorems and the written
algebraic arguments. They are recorded as deductions, without a novelty claim.

- `E_j` is the elementary symmetric sum of nonnegative residual spectral
  blocks. For nonzero `x`, nullity `4*k` is equivalent to
  `E_(m-k)>0` and `E_(m-k+1)=0`. The argument applies to every real vector.
- All `E_j` are nonnegative on real coefficient space. At a zero,
  `grad(E_j)=0`. The scalar equations therefore cannot establish smoothness
  through a regular-value Jacobian test; the underlying locus may still be
  smooth after using appropriate independent equations.
- Unit zero-product pairs are doubly pure and complex-orthogonal. Eliminating
  their four scalar/distinguished coordinates gives an equivalent incidence
  presentation. In dimension 32, the pair space lies in `V_2(C^15)`, whose
  real dimension is 56. This identifies a smooth ambient constraint space;
  smoothness or transversality of the multiplication zero set remains separate.
- An invertible rank-sized pivot and a zero Schur complement give a rational
  kernel frame. Free-coordinate restrictions give transition matrices,
  cocycles, and exact metric compatibility. Coverage follows because every
  matrix of the specified rank has a nonzero pivot minor.
- Rank can decrease at a limit, so the closure of a nullity-`k` locus lies
  within the union of loci of nullity at least `k`. Equality of that closure
  with the union requires a separate density or path argument.
- The dimension-32 polynomial path in `RANK_STRATUM_TOPOLOGY.md` has a
  constant four-dimensional generic kernel and exceptional kernels of
  dimensions 8, 12, and 16. Exact block identities establish the claim over
  the entire real parameter line. They establish specific closure incidences.
- Over the closed parameter interval, the complete partner incidence is a
  compact quotient of three endpoint spheres and two cylinders. Explicit
  orthogonal-vector nullhomotopies and Hatcher's propositions give a sphere
  wedge as its homotopy type.
- Theorem 10.1 doubles the full kernel after every zero-padding embedding.
  It therefore extends that restricted quotient and sphere-wedge formula to
  every `n>=5`. The proof concerns the specified embedded path and all of its
  partners, rather than every base point of `Z_n`.

## Follow-up search and its scope

The online search used arXiv queries for Cayley-Dickson zero divisors,
annihilators, and topology, sorted by newest announcement. That search found
the 2026 determinant paper and the following additional papers. Search results
are discovery evidence; their presence or absence is not an exhaustive
literature theorem.

| Follow-up | Inspection performed | Relevance and boundary |
| --- | --- | --- |
| Svetlana Zhilina, [On doubly alternative zero divisors in Cayley-Dickson algebras, 2608.26893v1](https://arxiv.org/html/2608.26893v1) | Abstract and Section 6, including Lemma 6.10 and Theorem 6.11 | Extends mod-four annihilator results to anisotropic norms over other fields; supplies counterexamples for split/isotropic settings. The repository uses the real positive-definite construction |
| Svetlana Zhilina, [Orthogonality graphs of real Cayley-Dickson algebras, Part I, 2608.28176v1](https://arxiv.org/html/2608.28176v1) | Abstract and scope | Doubly alternative elements and graph structures; the source was not used to infer full continuous pair-space topology |
| Svetlana Zhilina, [Orthogonality graphs of real Cayley-Dickson algebras, Part II, 2608.28163v1](https://arxiv.org/html/2608.28163v1) | Abstract and scope | An inductive graph on pairs of basis elements; its finite support restriction differs from arbitrary real rank loci |

The search also returned Moreno's earlier constructions and de Marrais's
basis-supported graph work. The source ledger from the prior audit supplies
the scope of the original annihilator papers. The reviewed results establish
specified strata and algebraic mechanisms; the review does not assert that
every later publication has been excluded from providing additional topology.

## Retrieval identities

The following SHA-256 values identify the retrieved primary-source HTML bytes,
except for Hatcher's PDF, on 2026-10-11. They identify the rendering inspected,
not an arXiv source archive. Versioned arXiv identifiers fix the cited paper
versions.

```text
0905.2987v1 HTML     68e52e0c408e8bbfd663c921188acb6f6f01cbd53bce99ac441ea5bfc5ac66d0
2608.08232v1 HTML    e7cb0aace6a034943a1ee99ece0796d3f05fc777ac1ecf4803b4e722bcc507c9
2608.26893v1 HTML    0927516444510ef2fc7b9580677f0be436e23494a0dfbac2504dc7f7bee63e1b
2608.28176v1 HTML    4c2ac19c06ce21c6b0194e5660f03d48b259d863a17abc62e79e2a1d4d806204
2608.28163v1 HTML    cb9cff03c06aba04bedb8486dd277cf1f28079e647431762f4465acc71ee5938
Hatcher ATch0.pdf    3c390bac0b166d5e084bc723c8593dcc7fc6b9bef54dbcae0784a3d348c3c73e
```

Earlier annihilator-paper rendering hashes and theorem transcription cautions
remain in the
[annihilator source ledger](cayley_dickson_annihilator_sources.md).
