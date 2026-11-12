# Exact Gram filters and reduced-operator witnesses

The normalized pathion operand `a=(e1-e10+e18+e25)/2` has Gram spectrum
`{0:16, 1:8, 2:4, 4:4}`. Its complete kernel projector is cubic. The canonical reduced operator also distinguishes
two nilpotent Jordan types that share characteristic polynomial `lambda^15`. External coefficient phase and a
real scalar offset supply separate exact controls.

[gram_witnesses.py](gram_witnesses.py) produces [witnesses.json](witnesses.json) from the multiplication specification
[cd_core.py](../../../gororoba_quantum/cd_core.py). Rational matrices use FLINT. Gaussian-rational ranks use the
faithful realification `A+iB -> [[A,-B],[B,A]]`, whose rational rank is twice its Gaussian rank. Characteristic
polynomials are checked directly over `Q(i)` with SymPy and independently after realification with FLINT.
The record binds the producer and every reused arithmetic source by SHA-256.

## Reduced ranks and congruence

For a doubly pure real operand `y=(p,q)`, put `z_k=p_k+i*q_k` for `k=1,...,15`. The canonical `C_z` is the
15-by-15 imaginary block of sedenion left multiplication, built by the existing
[rank-strata implementation](../a5-rank-strata-equations/rederive_strata_equations.py). Its bordered operator is
16-by-16. The coefficient table gives `C_z^T=-C_z` and `C_z^dagger=-C_conj(z)`; a nonreal `z` generally fails the
skew-Hermitian condition. The [Gauss-map note](../../notes/topics/strata-gauss-bottleneck.md#2-the-15--15-complex-matrix-c_z-and-the-bordered-matrix-az-t)
contains the dimension and transpose-skew distinction.

| Real operand | Ranks of `1,C_z,C_z^2,C_z^3` | Jordan block sizes | Real nullity |
| --- | --- | --- | ---: |
| `e1+e18` | `15,8,1,0` | `3,2,2,2,2,2,2` | 12 |
| `e1-e10+e18+e25` | `15,6,1,0` | `3,2,2,2,2,1,1,1,1` | 16 |

Both characteristic polynomials are `lambda^15`. Their kernel filtrations differ. The same distinction applies to
the split-coordinate congruence `D C_z D`, where `D_kk=i^popcount(k)`: on the second operand, the congruent operator
has power ranks `15,6,2,0` and Jordan blocks `3,3,2,2,1,1,1,1,1`. Rank and characteristic polynomial agree with
`C_z`, while the square rank changes from one to two. Congruence therefore transports the rank/Pfaffian questions
used by the strata calculation, and supplies no transport of the kernel filtration by itself.

The replay checks `nullity_R(L_y)=28-2*rank_C(C_z)` and
`rank_R(L_y)=2*rank_C(A(z,conj(z)))` on all 870 signed doubly pure two-support operands, plus the named witnesses.
The denominator is `2*binomial(30,2)`: indices `1,...,31` with index 16 omitted. Six additional named Gaussian
coefficient points test the full characteristic-polynomial identity

```text
Q = u.u + mu^2 + v.v
Delta = (u.u)(v.v) - (u.v)^2
G = Q^2 - 4*Delta
chi_C(lambda) = lambda*(lambda^2+Q)^3*(lambda^4+2*Q*lambda^2+G)^2.
```

The [existing strata proof](../a5-zero-divisor-strata/README.md#theorem-2-nullity-l_y--28---2-rank-c_z) owns the
general reduction theorem. These finite evaluations and the coefficient-skew identity retain its domain.

## Gram moments and complete projectors

For the normalized maximal-nullity operand, `M=L_a^T L_a` has
`tr(M)=32`, `tr(M^2)=88` and `tr(M^3)=296`. The polynomial

```text
P = (1-M)*(1-M/2)*(1-M/4)
  = 1 - 7*M/4 + 7*M^2/8 - M^3/8
```

is symmetric, idempotent, annihilated by `L_a`, and has trace 16. The replay reuses
[kernel_projector](../../../gororoba_quantum/cd_quantum_contracts.py), which also verifies completeness through the
constant term and rejects an omitted positive root. The quadratic candidate `1-3*M/2+M^2/2` has trace 28 and fails
idempotence. A rank-three Vandermonde system with inconsistent fourth condition proves that a degree-two
polynomial cannot equal one at zero and vanish at all three positive roots.

For the input `e1`, `<M>^2=1` and `<M^2>=3/2`; squaring the first moment loses the second moment. The identity input
`e0` gives equality, with both quantities equal to one. The normalized two-term family has positive Gram roots
among one and two and admits the quadratic projector. Its validity does not extend to arbitrary operands.

## Coefficients, embeddings and phase

All 591 unordered imaginary basis pairs in dimensions 8, 16 and 32 run with coefficient ratios `1,-1,2,3`.
For each pair, `L_i^T L_j` is a signed XOR permutation with two-by-two symmetric and skew blocks. If `n` is the
number of symmetric blocks, expansion of those blocks gives, for real weights `alpha,beta`,

```text
spec(M) = {(alpha+beta)^2:[n], (alpha-beta)^2:[n], alpha^2+beta^2:[D-2*n]}
tr(M^2) = D*(alpha^2+beta^2)^2 + 8*n*alpha^2*beta^2.
```

The replay checks the resulting annihilating polynomial, diagonal entries, second moment, rank and quadratic
projector on the four declared coefficient choices. The two-by-two block formula explains the arbitrary-weight
extension: a symmetric block contributes the two squared sums, while a skew block contributes the repeated
sum of squares. The signed pathion census has 930 operands and nullities `0,4,8,12`; the maximum symmetric-block
count is twelve. Support size two therefore excludes the sixteen-dimensional kernel mechanism at every real
coefficient ratio. A uniform basis-input measurement still assigns success one-half to both `e1+e9` and
`e1+e10` under their two-term LCU normalization, despite nullities zero and eight.

The basis checks through dimension 32 establish the ordinary embedding identity
`L_(a,0)=diag(L_a,R_a)`. The named sedenion `e1+e10` has nullity four and embeds with nullity eight.
The special construction `(a,+/-i_n*a)` gives nullity `nullity(a)+D-4` on all 424 declared special-lift cases with
two-support inputs perpendicular to the distinguished complex plane in dimensions 8 and 16. Sedenion zero-divisor inputs lift
to nullity sixteen. Replacing the special lift by an ordinary embedding fails every declared lift check.
The [annihilator source ledger](../../notes/cayley_dickson_annihilator_sources.md) attributes the general theorem
to Biss, Dugger and Isaksen.

| Coefficient-phase control | Nullity at phase 1 | Nullity at phase `i` |
| --- | ---: | ---: |
| Octonion pair `e1,e2` | 0 | 4 |
| Pathion pair `e1,e18` | 12 | 4 |
| Pathion pair `e1,e26` | 4 | 12 |

The phase replay uses the Hermitian Gram operator at phases `1`, `i` and `(3+4i)/5`. Symmetric blocks contribute
`s+/-2*alpha*beta*cos(theta)`, and skew blocks contribute `s+/-2*alpha*beta*sin(theta)`. A transpose in place of
the Hermitian adjoint fails the phase control. These complexified operators preserve the separate domain of the
real division-algebra statements.

For every pure basis direction through dimension 32, `L_p^T=-L_p`. Expanding the product gives
`M_(r+p)=r^2*1+M_p` at those levels. Named rational operands with `r=1` verify the complete Gram shift and full rank
in dimensions 2, 4, 8, 16 and 32; a sign mutation breaks the skewness premise. A normalization by four divides
the Gram operator by sixteen, as the exact selected-block check verifies.

## Reused algebra and attachment checks

The suite reruns the existing
[coefficient-cancellation implementation](../kaplansky-cd-mechanisms/kaplansky_cd_replay.py). The counts use ordered
pairs of disjoint, internally unordered index pairs:

| Dimension | Eligible XOR patterns | Real sign-canceling patterns |
| ---: | ---: | ---: |
| 8 | 42 | 0 |
| 16 | 630 | 168 |
| 32 | 6,510 | 2,520 |

Every single-index basis re-signing preserves the full cross-ratio. An incomplete cross-ratio fails that control.
Reducing the sign table modulo two removes the obstruction. The multiplication convention and attribution live
in the [Kaplansky mechanism note](../../notes/topics/kaplansky-mechanisms-cayley-dickson.md).

Exact inverse checks use every kernel-basis offset for `e1+e10` and the maximal pathion operand. Their inverse
families have dimensions four and sixteen. A sign change of the canonical inverse fails both-sided inversion.
The [one-sided-inverse note](../../notes/topics/cd-one-sided-inverses.md) owns the general theorem and its Rocq
proof references. The coefficient-level quadratic identity is also checked on every ordered basis pair through
dimension 32; its real positive norm excludes a nonzero nilpotent within those real algebras.

The suite calls the existing [kernel-limit contracts](../../../gororoba_quantum/kernel_limit_contracts.py) for
three four-support paths and four additional polynomial paths at `e1+e18`. The first three share a derivative,
have generic nullity four and pairwise orthogonal limiting planes, and sum to the endpoint's twelve-dimensional
kernel. The other four have generic nullity eight and pairwise four-dimensional limiting intersections;
the first two have projector-overlap trace `9/2`. The contracts check the shared-derivative transformation as well
as rational projector identities and rank witnesses on the declared punctured domains. The
[attachment note](../../notes/annihilator_kernel_limits.md#same-derivative-and-different-limiting-fibers) explains
the geometry and retains the scope beyond these paths.

The reused bounded certificate controls reject fourteen altered rank, frame, projector, determinant, exceptional-set
and attachment fields. Invalid approximate coefficients, malformed dimensions and an endpoint partner outside the
limiting kernel also fail the reused admission predicates.

Two exact four-by-four blocks cut from full `cd_core` multiplication give Gram characteristic polynomials
`lambda^2*(lambda-4)*(lambda-12)` and `lambda*(lambda-4)*(lambda^2-12*lambda+16)`. Their ideal bright levels under
the matched normalization are `3/4` and `(3+sqrt(5))/8`. An output orthogonal transformation preserves the Gram
matrix; scaling the output fails that control. The 32,768 ordered pathion basis triples also verify
`L_a*L_b-L_(a*b)=-[a,b,.]`, with explicit violations of the homomorphism replacement counted in the record.

## Scope

The JSON classifies 42 numbered claims: 30 confirmed with the stated coefficient identities or bounded witnesses,
one refuted description of the tracked note, and eleven `not_checked` entries with reasons. The matrix checks
establish neither a new classification theorem nor a new physical primitive. The
[rank and topology source ledger](../../notes/cayley_dickson_rank_topology_sources.md) already records the
published nullity and maximal-locus results. Kernel-bundle nontriviality, stable equivalence, a separate Lean
build, Berry transport and complete attachment classification remain outside the replay.

The calibrated IBM and photonic readings, acquisition counts, mesh variances and repeat correlations remain
owned by their [retained analyses](../a5-photonic-crosschecks/README.md) and reusable readers. This suite performs
ideal operator arithmetic and leaves those physical claims `not_checked`; it duplicates neither raw-acquisition
analysis nor provider calls. The exact input domain, coefficient choice, failed mutation and source binding in
each record field determine the available inference.

[validation.json](validation.json) binds the witness receipt to the pinned tool versions, bounded tests and measured
writer/replay costs. Its RSS readings are maximum process readings; the total cgroup peak remains unmeasured.

## Replay

Use the pinned interpreter from [the Python guide](../../PYTHON.md). The producer consumes deterministic named
operands and finite enumerations, so the replay requires no random draw.

```sh
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 PYTHONDONTWRITEBYTECODE=1
export GOROROBA_WORKERS=4 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MALLOC_ARENA_MAX=2
systemd-run --user --scope -q -p MemoryMax=8G -p MemorySwapMax=0 \
  "$PYTHON" -B -W error docs/evidence/a5-gram-operator-witnesses/gram_witnesses.py --check
sh ci/pr_checks.sh tests tests/test_a5_gram_operator_witnesses.py
```

The bounded tests check the cubic filter, Gaussian Jordan partitions, phase swap, scalar shift, split-congruence
counterexample and a genuinely Gaussian characteristic polynomial. Retained-record replay belongs to an
on-demand gate. A new checkable input that violates an asserted identity, an accepted missing-root filter or a
changed source digest falsifies the corresponding record.
