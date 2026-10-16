# Handoff to open_gororoba: corrected claims and bounded deliverables

open_gororoba is read-only from this repository. This note carries what
this repository established or refuted about claims that live there, each
with the artifact here that checks it and the acceptance test the receiving
change needs. Pinned revisions: gororoba-quantum main after the adjudication
of the first hardware record; open_gororoba
`127816214c3f96cc1777bd4bd9ba1b286ccc5917`.

## Upstream status

| section | upstream record |
|---|---|
| Sign kernel and the normalized associator code | landed in [open_gororoba PR 205](https://github.com/Oichkatzelesfrettschen/open_gororoba/pull/205) (Schreier-span characterization, normalized code, ANF basis and cardinality, quaternion exception, controlled phase) |
| Sedenion zero-divisor predicate | landed in [open_gororoba PR 205](https://github.com/Oichkatzelesfrettschen/open_gororoba/pull/205) (exact, proximity and annihilator domains; e_0 + e_9 and e_1 + e_9 retained) and [PR 208](https://github.com/Oichkatzelesfrettschen/open_gororoba/pull/208) (scalar constraints) |
| Frontier deliverables and the A_infinity refutation | landed in [open_gororoba PR 205](https://github.com/Oichkatzelesfrettschen/open_gororoba/pull/205); the A_5 chart is a fixed-pivot Schur chart, and smoothness of the complete stratum stays open |
| Vacuum-model code checks | filed as open_gororoba issues [209](https://github.com/Oichkatzelesfrettschen/open_gororoba/issues/209) through [214](https://github.com/Oichkatzelesfrettschen/open_gororoba/issues/214) |
| Degree of sign rows and associator phases ([cd_phase_degree.md](cd_phase_degree.md#formalization-statement)) | filed as [open_gororoba issue 217](https://github.com/Oichkatzelesfrettschen/open_gororoba/issues/217) |

## Sign kernel and the normalized associator code

The Schreier sign vectors of the Cayley-Dickson left-multiplication group
satisfy [omega_{a,b} = -1] = P(s_{a,b}) with P(v) = v + v(0) 1, the
projection that removes the scalar direction. Because 1 lies in H_n, P
preserves H_n with kernel <1>, so

    C_n = P(H_n) = H_n cap ker(ev_0),   H_n = C_n (+) <1>,

and with the characterization of H_n (literature/notes/left_mult_sign_rank.md),
for n >= 3

    C_n = { g(x_0..x_{n-2}) + c x_{n-1} : wt(g) even, g(0) = 0 },
    dim C_n = 2^(n-1) - 1,

with the explicit ANF basis { x^S : S a nonempty proper subset of
{0..n-2} } together with { x_{n-1} }. `scripts/left_mult_sign_rank.py`
checks both containments, the rank, and the basis through n = 8
(`_check_normalized_code`); C_2 = 0. Addition of binary sign functions
corresponds to multiplication of diagonal sign matrices. The direct sum
therefore identifies the sign-kernel group as `H_n = C_n x <-I>`.
Kirshtein's Theorem 35 and its proof identify `H_n` with
`Inn_l(Q_n) x Z(Q_n)` and, for `n >= 3`, the full left-multiplication
group with `(C_n x Z_2) semidirect (Z_2)^n`; the
[source note](1207.4230.md#mapping-to-this-repository) supplies the
convention map and explains the printed theorem's `n=2` discrepancy.
The quaternion case has `G_2=Q8` and `C_2=0` and stays separate from
that split-extension formula.

For phase synthesis, a sign-kernel operation is a normalized codeword
plus the scalar-sign bit from the central factor `Z(Q_n)=<-I>`.
Coherent control turns that scalar sign into a relative phase on the
control, so a controlled implementation must carry it.

Formalization order: the characterization of H_n; P with its image, kernel,
and direct sum; the basis and cardinality; the quaternion exception kept
separate; the phase-exact controlled implementation; `Print Assumptions` on
every theorem.

## Sedenion zero-divisor predicate

Two elements refute the predicate that reads only the equal norms of the two
octonion halves, and the polynomial that vanishes on e_0 + e_9:

| element | det L_v | L_v^2 |
|---|---:|---|
| e_0 + e_9 | 256 | not scalar (v is not purely imaginary) |
| e_1 + e_9 | 256 | -2 I (the imaginary halves are parallel) |

`gororoba_quantum/cd_core.py` (`sedenion_counterexamples`,
`_check_sedenion_counterexamples`) computes both and checks that every
corpus zero divisor has det L_v = 0. The equal-norm theorem of
`proofs/verified/C1465_KoebisuEqualNorm.v` is true; its surrounding
zero-divisor interpretation is wrong for e_1 + e_9, which is the case for a
statement review beside the proof.

The corrected membership condition: write v = (x_1 + u, x_2 + w) with u, w
imaginary octonions, s = x_1^2 + x_2^2, A = |u|^2, B = |w|^2, gamma = <u, w>;
then D_2 = s^2 + 2 s (A + B) + (A - B)^2 + 4 gamma^2 vanishes over the reals
exactly when x_1 = x_2 = 0, A = B, gamma = 0, which with v != 0 is zero-divisor
membership. Repair the API with three explicit domains: exact membership on
16 exact coordinates with the nonzero condition; numerical proximity with
scale normalization, documented residuals, and an indeterminate region; a
matrix-based annihilator API for other dimensions. Add invalid-domain
fixtures (the two elements above) deliberately: the standard-factor tests
pass because their fixtures already satisfy the omitted scalar constraints.
The gradient of D_2 vanishes on its zero locus, so D_2 alone cannot decide
smoothness of that locus; use the component constraints.

## Frontier deliverables, each with a finite acceptance test

| project | deliverable | boundary |
|---|---|---|
| sedenion certificates | exact L_v matrices, kernel bases, rank bounds, partner-span checks, explicit scaling | unit-input normalization differs from block-encoding normalization |
| A_5 geometry | integrate the local [rank_charts.py](../../gororoba_quantum/rank_charts.py) construction and [retained chart checks](../../results/hw_estimate/rank_charts.json) into the receiving tree: L_a = [[P, Q], [R, S]], det P != 0, S - R P^-1 Q = 0, K(a) = [[-P^-1 Q], [I]] | local charts and transitions exist; receiving-tree integration remains open, and full continuous classification follows the [local roadmap](../../gororoba_quantum/RANK_STRATUM_TOPOLOGY.md#global-classification-roadmap-and-admission-gates) |
| graph topology | one flag complex with verified boundary maps and homology certificates | no continuous-topology conclusion without a proved bridge |
| cochains | structural proofs that the differential preserves the ANF-degree filtration (substitution of linear XOR expressions and addition never raise total degree) | F is a 2-cochain; dF is an ordinary coboundary |
| Boolean functions | a defined family's exact metrics and counterexamples; f(u, t) = [u != 0] + t stays the permanent negative control (degree n - 1, nonlinearity 2, algebraic immunity 2, verified through n = 11 in the replay) | degree alone carries no security claim |
| hidden oracle | a fully specified observable oracle model and recovery task; quotient by observational equivalence (uncontrolled phase access identifies f and f + 1; controlled access is an extra resource); the corrected n = 3 linear code is a decisive negative control | simulation gives upper-bound evidence, not query complexity |
| Albert observables | one verified linearized observable T_{A,B}(X) = (A o B) o X - A o (B o X) with fixed A, B and independent fixtures; the 27-coordinate description needs an orthonormal basis or the coordinate Gram matrix before proving alpha >= ||T_{A,B}|| | Jordan nonassociativity does not establish exceptionality |

The minimal uncurved A_infinity claim is refuted as stated: m_1 = 0 forces
m_2 associative, so a replacement must change the structure
(Albuquerque-Majid quasiassociativity is the existing alternative).

## Vacuum-model code checks

Read at open_gororoba commit `b977e43f`. Each row names the file and line,
the defect, the check that confirms it, and the acceptance test for a fix.

| Location | Finding | Confirming check | Acceptance test |
|---|---|---|---|
| `crates/casimir_core/src/energy.rs:264-270`, `geometry.rs:36-39` | `casimir_parallel_plates_exact` returns -pi^2/(720 a^3) and labels it the massless scalar result (Casimir 1948). That coefficient is the perfect-conductor electromagnetic energy per area; a Dirichlet scalar gives -pi^2/(1440 a^3), and Casimir 1948 treats the electromagnetic field. | Mode-sum identity: the electromagnetic field between ideal conductors is one Dirichlet and one Neumann scalar, each contributing half ([0902.4022](0902.4022.md) carries the electromagnetic formula; [2604.13237](2604.13237.md) recovers the Dirichlet scalar limit). | A scalar benchmark returns -pi^2/1440 and a separately named electromagnetic benchmark returns -pi^2/720. |
| `energy.rs:83` with `geometry.rs:47-68` | The loop indicator is 1 when a loop crosses either plate, so isolated single-surface self-energy enters the average. The interaction energy counts loops that intersect both surfaces. | `intersects_count` sums crossings of z = 0 and z = a independently; `n_crossings > 0` accepts a loop touching one plate. | The parallel-plate interaction energy uses the both-surfaces indicator and its separation derivative reproduces the Casimir pressure. |
| `energy.rs:1-14, 105, 137` | The integrand (4 pi)^(-3/2) T^(-5/2) has dimension length^-3 (T is length squared), not the length^-4 of a 3+1D local energy density, while the module documents a local energy density and compares it with an energy per area. | Dimensional count of the proper-time integral. | The documented quantity, its spacetime dimension and the analytic comparison carry matching units. |
| `energy.rs:145` | `error: prefactor * error_sq.sqrt()` with a negative prefactor reports a negative standard error. | `prefactor = -1/(2 (4 pi)^1.5) < 0`. | The error field is `prefactor.abs() * error_sq.sqrt()` and a test asserts it is nonnegative. |
| `crates/sign_imbalance/src/imbalance_energy.rs:16-17, 92` | `E_frust = F * C(N,3) * E_0` increases strictly with the imbalance F for E_0 > 0, yet F = 3/8 is documented as a local energy minimum. | The energy law is linear in F with a positive slope. | Either a stabilizing term with a derived minimum at 3/8, or the attractor claim removed from the energy documentation. |
| `crates/algebra_experimental/src/leech_pathion.rs:8-18` | The 8D "dark sector" is the coordinate complement of a 24-index block. With that block fixed at every doubling, ordered complement pairs whose product index lands in the block number 24D - 704 for D >= 32, and block pairs landing in the complement number 128 (e_8 e_16 = e_24 already leaves the block). | Exhaustive XOR count from 32 to 4096 in [scripts/cd_associator_defect_census.py](../../scripts/cd_associator_defect_census.py). Proof: an index i >= 24 meets a block index k < 8 in the complement always, and k in [8, 24) only when i >= 32, so 8(D - 24) + 16(D - 32) = 24D - 704. | The module names the complement a coordinate complement, and any physical-sector reading carries its own field content and dynamics. |
