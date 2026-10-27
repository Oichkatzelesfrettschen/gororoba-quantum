# Primorial cover defects: missing wheel gaps as restricted covers and diagonal Hamiltonians

This note holds the mathematics behind the missing gaps 20, 32, 86 and 88 of
the primorial wheels, every statement checked by
`gororoba_quantum/primorial_cover.py` and retained in
[certificates.json](../../evidence/primorial_cover/certificates.json) (gate
`core-688`). The literature baseline is Ziller's restricted-covering reduction
and his Table 1 of missing differences for `k <= 44`
([2007.01808.md](../papers/2007.01808.md)); the problem is Erdos Problem 854,
open at retrieval ([erdos-854-consecutive-coprime-gaps.md](../papers/erdos-854-consecutive-coprime-gaps.md)).
The circuits these instances feed and their simulated hardware response are in
[primorial-cover-defect-probes.md](../../design/primorial-cover-defect-probes.md).

## Reduction

Write `P_k` for the product of the first `k` primes and `U_L = {1, ..., L - 1}`.
For each odd prime `p | P_k` the allowed residues are
`A_p(L) = Z/p \ {0, L mod p}`, of size `p - 1` when `p | L` and `p - 2`
otherwise, and `R_{p,r} = {t in U_L : t = r mod p}`. The defect is

`delta_k(L) = min over r_p in A_p(L) of |U_L \ union_p R_{p, r_p}|`.

- An adjacent gap `2L` between integers coprime to `P_k` exists iff
  `delta_k(L) = 0`. Given a cover, the Chinese remainder theorem picks an odd
  `x` with `x = -2 r_p mod p`; then `p | x + 2t` iff `t = r_p mod p`, the
  endpoint restrictions keep `x` and `x + 2L` coprime, and 2 removes every
  even number between them. This is Ziller's Corollary 3.2 (p. 10) with the
  prime 2 split off.
- An assignment with `d` uncovered points leaves `d` survivors between the
  endpoints, so `delta_k(L) + 1` is the fewest consecutive wheel gaps summing
  to `2L`.
- Singleton repair: a new prime `q >= L` meets `U_L` in at most one point per
  class and can take any uncovered `t` as its residue (`1 <= t < L <= q`
  avoids both endpoints), so `delta_{Q + q}(L) = max(delta_Q(L) - 1, 0)`. The
  bound fails for `q < L`, where one class can hold several points.

## Certified instances

Residues list the odd primes 3, 5, ..., `p_k` in ascending order.

| k | gap 2L | witness residues | uncovered | CRT start x (mod 2 prod p) | wheel gaps | branch primes, branches | repair |
|---:|---:|---|---:|---|---|---|---|
| 6 | 20 | 2,4,6,1,7 | 3 | 18797 (30030) | 6 + 14 | 3, 5: 4 | 17 |
| 8 | 32 | 2,4,6,1,10,15,7 | 3 | 2109347 (9699690) | 6 + 26 | 3, 5, 7: 15 | 23 |
| 14 | 86 | 2,4,4,5,2,13,12,10,7,6,3,1,21 | 22 | 1521251317636007 | 44 + 42 | 3..13: 1485 | 47 |
| 14 | 88 | 1,3,6,3,4,9,5,12,3,11,2,21,15 | 29 | 11092219445984539 | 58 + 30 | 3..11: 150 | 47 |

The lower bound `delta_k(L) >= 1` is exhaustive: every assignment of the
branch primes leaves a residual set that a depth-first search over the
remaining primes, pruned by the sum of their largest class intersections,
cannot cover. The same search finds covers at `L = 9, 11` (k = 6), `15, 17`
(k = 8) and `42, 45` (k = 14), whose gaps exist, and with the repair prime
added. These four gaps are exactly the missing differences Ziller's Table 1
(p. 12) lists at these `k`; 20, 32 and 86 are the smallest missing difference
at `k = 6, 8, 14`. The whole run takes about one second.

## Capacity bounds and the relaxation

For `S` in `U_L` let `c_p(S) = max_r |S cap R_{p,r}|`. Every assignment covers
at most `sum_p c_p(S)` points of `S`, so
`delta_k(L) >= max_S (|S| - sum_p c_p(S))`. This is a necessary capacity
condition, weaker than Hall's matching condition, because one prime covers a
whole class at once.

- `S = {1,3,4,6,7,9}` at (6, 10) has capacities (0, 2, 1, 1, 1) for primes
  3..13 and deficiency 1; `S = {1,3,4,6,7,9,10,12,13,15}` at (8, 16) has
  (0, 2, 2, 2, 1, 1, 1) and deficiency 1. Each alone proves the lower bound.
- At k = 14 the whole residual set of a branch is too coarse a witness: in 20
  of the 1485 branches at L = 43 and 20 of the 150 at L = 44, `|U_rho|`
  minus the remaining primes' capacities is at most zero, so a proper subset
  is needed. The exhaustive search above sidesteps subset certificates.
- The linear relaxation (class weights per prime summing to one, every point
  covered to weight one, uncovered slack minimized) has optimum 0 at both
  k = 14 instances: HiGHS returns weights that, rounded to rationals,
  satisfy every constraint exactly. With `delta = 1` this is an additive
  integrality gap of one. Fixing primes in a branch only raises the capacity
  bound (a child keeps `S \ C` of its parent's witness), and with every prime
  fixed it equals the residual count.

## Cost Hamiltonians

On one register state per allowed residue,
`H_D = sum_t prod_p (I - Pi_{p,t})` has eigenvalue `d(r)` (the uncovered
count) on each assignment, so its ground energy is `delta_k(L)` and
`Tr(rho H_D) >= delta_k(L)` for every state: no superposition evades the
integrality gap. Unreduced, (14, 43) has 254 one-hot variables, 55 binary
bits and 356,968,284,923,250 assignments, so the circuits use exact
reductions instead.

- **Gap-20 quotient.** After the forced prime-3 class, primes 5 and 7 choose
  among (1, 2, 3, 4) and (1, 2, 4, 6) (residue 5 mod 7 covers no residual
  point), and 11 and 13 each remove one point. The 16-entry table
  (2,2,2,1, 1,2,2,2, 1,2,2,2, 2,2,2,1) has Walsh form
  `7/4 - Z0 Z1/4 + Z0 Z2 Z3/4 + Z1 Z2 Z3/4`, a function of the parities
  `a = b0 + b1` and `b = b0 + b2 + b3` only:
  `H_2 = 2 I - |a=0, b=1><a=0, b=1|`, little-endian spectrum (2, 2, 1, 2).
- **Three-bit slices.** Freezing a witness except a two-valued choice for
  5, 7, 11 (domains (4,1), (4,2), (5,1) at L = 43; (3,1), (6,1), (3,1) at
  L = 44) gives `E_86 = (1,5,3,8,3,5,4,8)` and `E_88 = (1,6,4,6,3,6,5,6)`,
  with every coefficient a multiple of 1/8:
  - `8 H_86 = 37 - 15 Z0 - 9 Z1 + 3 Z0Z1 - 3 Z2 - 3 Z0Z2 - Z1Z2 - Z0Z1Z2`;
  - `8 H_88 = 37 - 11 Z0 - 5 Z1 - 5 Z0Z1 - 3 Z2 - 3 Z0Z2 - Z1Z2 - Z0Z1Z2`.
- **Repairs.** The class 22 mod 47 covers the point 22 every gap-86 slice
  state leaves, so `H_86^rep = H_86 - I`: a global phase, invisible to any
  measurement at any QAOA depth. The class 29 mod 47 covers 29 only where
  `b1 = 0`, so `H_88^rep = H_88 - (I + Z1)/2` changes a nonconstant
  coefficient.
- **Parity network.** `(CX_{0,1} CX_{1,2})^4` on a path writes the parities
  3, 7, 5, 6 (and repeats 2, 3, 2, 4) and returns to the identity map, so eight
  adjacent CNOTs and seven RZ implement any three-bit diagonal phase. A
  breadth-first search over adjacent-CNOT parity maps finds eight minimal
  among networks that visit all seven parities and end at the identity; that
  bound holds for this model only.
- **Grid.** With `gamma = g pi/9` and `beta = b pi/72`, every cost angle
  `2 gamma c_S` and mixer angle `2 beta` is a multiple of pi/36, the Tuna
  rotation grid ([quantum_inspire/README.md](../quantum_inspire/README.md)).

## Table 1 through k = 20

The same search, run over every even difference from 2 to Ziller's `h(k)`
for `k = 1..20`, reproduces the missing set and `N_min(k)` of every row of
Table 1: 20, 32, 86, 88, 98, 146, 166, 170 and 172 are the only missing
differences, each excluded exhaustively at the first level its range
reaches, and every other difference has a verified cover
([ziller_table.json](../../evidence/primorial_cover/ziller_table.json); method
in the [evidence README](../../evidence/primorial_cover/README.md#ziller-table-1-through-k--20)).

## The primorial maximum at k = 24

Hajdu and Saradha found `j(P_24) = 234 < 236 = h(24)`, the first `k` at which
the primorial fails to attain the Jacobsthal maximum
([openai-2026-jacobsthal-quadratic-bound.md](../papers/openai-2026-jacobsthal-quadratic-bound.md),
History). The same cover search decides both halves of that value at the
primorial: `cover_exists(117, odd_primes(24))` returns True, so the wheel of
`P_24` has a gap 234, and `cover_exists(118, odd_primes(24))` returns False,
so it has no gap 236 ([E], 612 s and 536 s on the build host, not gated):

```sh
export PYTHON="${PYTHON:-python3}"
cd gororoba_quantum && "$PYTHON" -B -c 'import primorial_cover as pc; p = pc.odd_primes(24); print(pc.cover_exists(117, p), pc.cover_exists(118, p))'
```

The two calls establish `j(P_24) >= 234` and the absence of 236; the
maximum itself needs every larger even gap excluded, which the search here
does not run. A set of 24 primes with a gap 236, the other half of
`h(24) = 236`, lies outside the primorial reduction of this note.

## Limits

The certificates settle four finite instances, and the table reproduction
the rows `k <= 20` below Ziller's `h(k)`. They prove no bound on the
branching depth needed as `k` grows, no growth law for the smallest missing
gap or the count of distinct gaps, and nothing about Ziller's Conjecture 4.1
(`h(k - 1) <= N_min(k)`). A counterexample to that conjecture needs only a
parent gap `2M >= 2L` at level `k - 1` (a witness, not the exact Jacobsthal
value) and an exclusion certificate for `2L` at level `k`; the search here
supplies the second kind.
