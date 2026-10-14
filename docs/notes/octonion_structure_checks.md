# Octonion associator codes, box-kite frustration and walk sectors

[scripts/octonion_structure_checks.py](../../scripts/octonion_structure_checks.py)
recomputes every statement below from `cd_core.cd_sign` and
`predict.associator_phase` in integer or rational arithmetic; its CI gate runs
in normal and optimized Python. Tags: [P] prior or textbook result, [E] finite
check, [T] proved here, [I] interpretation.

| Statement | Status |
|---|---|
| The 21 associator slices omega_ij(x) of the octonions are the seven nonzero characters of F_2^3, three times each | [E] all 21 slices |
| With the zero character and complements they span RM(1,3), weight enumerator 1 + 14 z^4 + z^8, doubly even and self-orthogonal; Construction A gives 240 norm-2 vectors closed under all 57600 root reflections, the E8 root system | [P] RM(1,3) is the extended Hamming [8,4,4] code and Construction A on it is E8 (Conway and Sloane, *Sphere Packings, Lattices and Groups*, ch. 5 and 7); [E] the associator slices generate it |
| Each of the seven signed sedenion box-kites has 12 edges and 8 triangles of sign -1; shared vertex signs give frustration minimum 4, shared phases give minimum 3 | [T] below; [E] all 64 sign assignments per kite and the 120-degree phase assignment |
| For the walk cores of the pairs (25, 31) and (9, 22) at D = 32, U^120 = I and the weight of the initial state on the primitive-k eigenvalue sector is (1/120) sum_{t<120} <0|U^t|0> c_k(t) | [T] below; [E] weights (25, 31): order 6 and 8, 1/2 each; (9, 22): orders 1, 2, 3, 5, 6 with 11/30, 1/6, 1/12, 3/10, 1/12 and zero weight on order 8 |
| The first return of the initial state is the lcm of the orders that carry weight: 24 for (25, 31) and 30 for (9, 22), while the whole operator returns at 120 for (9, 22) because its order-8 sector carries no initial weight | [T]; [E] |
| G = L_a^T L_a / &#124;a&#124;^2 has unit diagonal; Delta = tr(G^2)/d - 1 and the rank ratio are unchanged by the pure embedding a -> (a, 0) | [E] 20 random a at D = 16 and 32 |
| The doubling (a, b)(c, d) = (ac - d conj(b), conj(a) d + c b) and the repository doubling are intertwined by T(a, b) = (T(a), conj(T(b))) | [E] all 340 basis pairs at D = 2 to 16; bilinearity extends each stage to all real coefficients |

## Proofs

**Frustration minima.** Switching by the kite's gauge (its triangles all have
sign -1, so it is switching-equivalent to the all-negative octahedron
K(2,2,2)) turns every edge sign into -1 and leaves F unchanged. For phases
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
the discrete one because three unit-length pair phasors can cancel only off
the real axis.

**Walk sectors.** U^120 = I is checked exactly (Gaussian-integer powers of
4U), so every eigenvalue is a 120th root of unity and
<0|U^t|0> = sum_lambda q_lambda lambda^t with q_lambda the initial-state
weight on eigenvalue lambda. Summing q_lambda over the primitive k-th roots
inverts this discrete Fourier series with Ramanujan's sum
c_k(t) = sum over primitive k-th roots of lambda^{-t}, an integer, so the sector
weights are exact rationals from the return amplitudes alone, without an
eigendecomposition. The return probability |<0|U^t|0>|^2 equals one exactly
when lambda^t = lambda_0^t on every weighted eigenvalue, which first happens at
the lcm of the weighted orders; the whole operator returns at the lcm of all
orders present.

## Relation to repository results

- [I] The associator characters are the Fano-plane lines of the octonion
  table read as F_2-linear functionals, so the E8 statement is the classical
  Fano -> Hamming -> E8 chain realized on `cd_core`'s own signs; no priority is
  claimed.
- [I] The box-kite gap (4 for shared signs, 3 for shared phases) is a
  shared-parameter benchmark for the signed kites the
  [switching check](../sources/open_gororoba/check_signed_kite_switching.py)
  already certifies. It is not a Bell or contextuality inequality, and no
  hardware experiment measures it.
- [I] The walk return periods (24, 24) and (30, 120) are already gated in
  [ripple_dynamics.py](../../gororoba_quantum/ripple_dynamics.py); the sector
  weights explain them.
- [I] The rank path a(t) = e1 + (t-1)^2 e10 + t(3-t) e18/2 - t(t-1) e25/2, its
  coset blocks and its nullities belong to
  [rank_attachments.py](../../gororoba_quantum/rank_attachments.py) and the
  rank-stratum topology; only the embedding invariance of Delta is added here.
  Delta measures norm distortion; d / (1 + Delta) bounds the rank from below
  and does not measure it.

## Provenance

The statements were proposed in an external audit bundle (sha256
`da75a085b328e272090dbe4641bd1f25f8a86e63da80c4c3cee2aa8ae06e1a25`) computed
against repository commit bd6533c. The repository retains none of its code,
data or figures; the script above is an independent reimplementation, and the
Ramanujan-sum weight formula and the frustration proof are written here.
