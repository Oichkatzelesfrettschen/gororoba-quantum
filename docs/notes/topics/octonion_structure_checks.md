# Octonion associator codes, box-kite frustration and walk sectors

[scripts/octonion_structure_checks.py](../../../scripts/octonion_structure_checks.py)
recomputes the statements below from `cd_core.cd_sign` and
`predict.associator_phase` in integer, rational or cyclotomic-integer
arithmetic; the whole-operator periods are gated in
[ripple_dynamics.py](../../../gororoba_quantum/ripple_dynamics.py). It runs as a CI
gate. Tags: [P] prior or textbook result, [E]
finite check, [T] proved here, [I] interpretation.

| Statement | Status |
|---|---|
| The 21 associator slices omega_ij(x) of the octonions are the seven nonzero characters of F_2^3, three times each | [E] all 21 slices |
| With the zero character and complements they span RM(1,3), weight enumerator 1 + 14 z^4 + z^8, doubly even and self-orthogonal; Construction A gives 240 norm-2 vectors closed under reflection (all 57600 root-reflection pairs), the E8 root system | [P] RM(1,3) is the extended Hamming [8,4,4] code and Construction A on it is E8 (Conway and Sloane, *Sphere Packings, Lattices and Groups*); [E] the associator slices generate it |
| Each of the seven signed sedenion box-kites has 12 edges and 8 triangles of sign -1; shared vertex signs give frustration minimum 4, shared phases give minimum 3 | [T] below; [E] all 64 sign assignments per kite, the 120-degree phase assignment in rational cosines, and the proof's identity as an exact coefficient comparison of two bilinear forms in the unit phasors, which covers every phase assignment |
| For the walk cores of the pairs (25, 31) and (9, 22) at D = 32, U^120 = I and the weight of the initial state on the primitive-k eigenvalue sector is (1/120) sum_{t<120} <0|U^t|0> c_k(t) | [E] U^120 = I exactly; [T] the sector formula below, Fourier inversion on Z_120 ([P] standard); [E] weights (25, 31): order 6 and 8, 1/2 each; (9, 22): orders 1, 2, 3, 5, 6 with 11/30, 1/6, 1/12, 3/10, 1/12 and zero weight on order 8 |
| The first return of the initial state is the order of the eigenvalue ratios lambda / lambda_0 over the weighted spectrum, which equals the lcm of the weighted orders when lambda = 1 carries weight: 30 for (9, 22). For (25, 31) no weight sits on lambda = 1; its weighted eigenvalues exp(2 pi i n / 120) have n in {15, 45, 75, 105} and {20, 100}, ratio order 24, which equals lcm(6, 8) = 24 | [T] below; [E] both first returns from exact amplitudes; the weighted support from exact zero tests of 120 q_n = sum_t <0&#124;U^t&#124;0> zeta^{-n t} in Z[zeta_120] modulo Phi_120, consistent with the exact sector weights and calibrated on three known spectra |
| The whole operator returns at 120 for (9, 22) and at 24 for (25, 31); the order-8 sector of (9, 22) carries no initial weight, so the state returns at 30 | [E] operator periods gated in [ripple_dynamics.py](../../../gororoba_quantum/ripple_dynamics.py) (`EXPECTED_PERIODS`) |
| The pure embedding a -> (a, 0) multiplies as diag(L_a, R_a); G = L_a^T L_a / &#124;a&#124;^2 has unit diagonal, and Delta = tr(G^2)/d - 1 and the rank ratio are unchanged by the embedding, zero divisors included | [T] below; [E] block structure, L_conj(a) = L_a^T, R_a = C L_conj(a) C, Delta and the ranks in integer and rational arithmetic for 10 integer vectors and the zero divisor e1 + e10 at D = 16 and 32 (rank 12 of 16 and 24 of 32) |
| The doubling (a, b)(c, d) = (ac - d conj(b), conj(a) d + c b) and the repository doubling are intertwined by T(a, b) = (T(a), conj(T(b))) | [E] all 340 basis pairs at D = 2 to 16; bilinearity extends each stage to all real coefficients |
| On each Fano line {p, q, p xor q}, L_p L_q L_{p xor q} = eps_L (-1)^{<x, v_L>} with v_L orthogonal to the line; eps_L = -1 on (1,2,3), (1,4,5), (2,4,6), (2,5,7), (3,4,7) and +1 on (1,6,7), (3,5,6) | [E] all 7 lines through the signed-permutation form L_m e_x = cd_sign(m, x) e_{m xor x}; Levratti's Fano-line duality (Table 1) states the Z-string correspondence |
| 63 of the 105 sedenion pairs have {L_p, L_q} = 0; L_a^T L_a = 2I - t {L_i, L_j} for a = e_i + t e_j, so only the other 42 pairs can carry a zero divisor, and they are exactly the index pairs of the 336-row corpus | [E] counts, the Gram identity for both signs of t on every pair, and set equality; [P] the 63/42 counts are Levratti's Remark 5.4, whose route through L_p L_q = epsilon L_{p xor q} fails (see [the review note](../levratti-2026-fano-css.md)) |

## Proofs

**Frustration minima.** The eight triangles of the octahedron span its cycle
space over F_2 (dimension 12 - 6 + 1 = 7), so a signing whose triangles all
have sign -1 assigns every cycle the sign of the all-negative signing and is
switching-equivalent to it. Switching by that gauge turns every edge sign
into -1 and leaves F unchanged (signs s_v -> g_v s_v, phases
theta_v -> theta_v + pi [g_v = -1]). For phases
theta_v write Z = sum_v e^{i theta_v} and Z_1, Z_2, Z_3 for the sums over the
three opposite (non-adjacent) pairs. The edges are all vertex pairs except the
opposite ones, sum_{u<v} cos(theta_u - theta_v) = (|Z|^2 - 6)/2 and each
opposite pair has cos = (|Z_k|^2 - 2)/2, so

    F = 6 + (1/2) sum_edges cos = 6 + (|Z|^2 - |Z_1|^2 - |Z_2|^2 - |Z_3|^2) / 4.

With |Z_k| <= 2 this gives F >= 3, attained exactly when every opposite pair
shares a phase and the three pair phasors sum to zero (120 degrees apart);
every edge then carries probability 1/4. For signs, Z_k is in {-2, 0, 2}: all
three nonzero force |Z| in {2, 6} and F in {4, 12}, and any zero Z_k makes
sum |Z_k|^2 <= 8 and F >= 4, attained. The continuous minimum lies one below
the discrete one because three pair phasors of length 2 cancel only at 120
degrees, which no sign assignment reaches.

**Walk sectors.** U^120 = I is checked exactly (Gaussian-integer powers of
4U), so every eigenvalue is a 120th root of unity and
<0|U^t|0> = sum_lambda q_lambda lambda^t with q_lambda the initial-state
weight on eigenvalue lambda. Summing q_lambda over the primitive k-th roots
inverts this discrete Fourier series with Ramanujan's sum
c_k(t) = sum over primitive k-th roots of lambda^{-t}, an integer, so the sector
weights are exact rationals from the return amplitudes alone, without an
eigendecomposition.

**First return.** With q_lambda > 0 summing to one, |<0|U^t|0>| = 1 holds
exactly when lambda^t is the same for every weighted lambda (the equality case
of the triangle inequality), that is when (lambda / lambda_0)^t = 1 for a fixed
weighted lambda_0. The first return is therefore the lcm of the orders of the
ratios lambda / lambda_0. When lambda_0 = 1 carries weight these are the
orders of the weighted eigenvalues themselves, so the first return is the lcm
of the weighted sector orders. Without weight on 1 the ratio order can be
smaller: an eigenvector with a primitive eighth-root eigenvalue returns at
t = 1. Sector weights alone therefore fix the first return only when order 1
carries weight; the script reads the weighted support from the per-eigenvalue
weights, each zero or nonzero as an exact element of Z[zeta_120]. The whole
operator returns at the lcm of all orders present.

**Embedding moments.** The repository doubling
(x, y)(z, w) = (xz - conj(w) y, w x + y conj(z)) gives
(a, 0)(z, w) = (a z, w a), so L_(a, 0) = diag(L_a, R_a). Conjugation is an
anti-automorphism, conj(x a) = conj(a) conj(x), so R_a = C L_conj(a) C with
C = diag(1, -1, ..., -1), and L_conj(a) = L_a^T. Hence
R_a^T R_a = C L_a L_a^T C, which shares its spectrum with L_a^T L_a. The
embedded Gram matrix has trace and squared trace twice those of G in twice
the dimension, so Delta is unchanged, and rank L_(a, 0) = 2 rank L_a, zero
divisors included.

## Relation to repository results

- [I] The associator characters are the Fano-plane lines of the octonion
  table read as F_2-linear functionals, so the E8 statement is the classical
  Fano -> Hamming -> E8 chain realized on `cd_core`'s own signs; no priority is
  claimed.
- [I] The box-kite gap (4 for shared signs, 3 for shared phases) is a
  shared-parameter benchmark for the signed kites the
  [switching check](../../sources/open_gororoba/check_signed_kite_switching.py)
  already certifies. It is not a Bell or contextuality inequality, and no
  hardware experiment measures it.
- [I] The walk return periods (24, 24) and (30, 120) are already gated in
  [ripple_dynamics.py](../../../gororoba_quantum/ripple_dynamics.py); the sector
  weights explain them.
- [I] The rank path a(t) = e1 + (t-1)^2 e10 + t(3-t) e18/2 - t(t-1) e25/2, its
  coset blocks and its nullities belong to
  [rank_attachments.py](../../../gororoba_quantum/rank_attachments.py) and the
  rank-stratum topology; only the embedding invariance of Delta is added here.
  Delta measures norm distortion; d / (1 + Delta) bounds the rank from below
  and does not measure it.

## Provenance

The statements were proposed in an external audit bundle (sha256
`da75a085b328e272090dbe4641bd1f25f8a86e63da80c4c3cee2aa8ae06e1a25`) computed
against repository commit bd6533c. The repository retains none of its code,
data or figures; the script above is an independent reimplementation, and the
Ramanujan-sum weight formula and the frustration proof are written here.
