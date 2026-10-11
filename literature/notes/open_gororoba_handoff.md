# Handoff to open_gororoba: corrected claims and bounded deliverables

open_gororoba is read-only from this repository. This note carries what
this repository established or refuted about claims that live there, each
with the artifact here that checks it and the acceptance test the receiving
change needs. Pinned revisions: gororoba-quantum main after the adjudication
of the first hardware record; open_gororoba
`127816214c3f96cc1777bd4bd9ba1b286ccc5917`.

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
(`_check_normalized_code`); C_2 = 0. This is a direct-sum statement about
binary codes; it says nothing about a direct-product decomposition of the
multiplication group. For phase synthesis, a sign-kernel operation is a
normalized codeword plus a separate scalar-sign bit; under coherent control
that bit is a relative phase on the control, so a controlled implementation
must carry it.

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
| A_5 geometry | one certified constant-rank chart with explicit domain and kernel frame, via the Schur complement: L_a = [[P, Q], [R, S]], det P != 0, S - R P^-1 Q = 0, K(a) = [[-P^-1 Q], [I]] | a rank jump marks a chart boundary and refutes nothing else |
| graph topology | one flag complex with verified boundary maps and homology certificates | no continuous-topology conclusion without a proved bridge |
| cochains | structural proofs that the differential preserves the ANF-degree filtration (substitution of linear XOR expressions and addition never raise total degree) | F is a 2-cochain; dF is an ordinary coboundary |
| Boolean functions | a defined family's exact metrics and counterexamples; f(u, t) = [u != 0] + t stays the permanent negative control (degree n - 1, nonlinearity 2, algebraic immunity 2, verified through n = 11 in the replay) | degree alone carries no security claim |
| hidden oracle | a fully specified observable oracle model and recovery task; quotient by observational equivalence (uncontrolled phase access identifies f and f + 1; controlled access is an extra resource); the corrected n = 3 linear code is a decisive negative control | simulation gives upper-bound evidence, not query complexity |
| Albert observables | one verified linearized observable T_{A,B}(X) = (A o B) o X - A o (B o X) with fixed A, B and independent fixtures; the 27-coordinate description needs an orthonormal basis or the coordinate Gram matrix before proving alpha >= ||T_{A,B}|| | Jordan nonassociativity does not establish exceptionality |

The minimal uncurved A_infinity claim is refuted as stated: m_1 = 0 forces
m_2 associative, so a replacement must change the structure
(Albuquerque-Majid quasiassociativity is the existing alternative).
