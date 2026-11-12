# Jets of formal arcs: h_6 of E8-bar -> N-

[jet_rank.py](jet_rank.py) bounds the Hilbert function h_d of the fiber cone F(I) = k[y]/L of E8-bar -> N- from
below by exact linear functionals that come from jets of formal arcs, and the rank of those functionals meets the
upper bound HF(k[y]/K2, d) in every degree from 1 to 6 at p = 32009 and in degrees 5 and 6 at p = 32029. With K2
inside L this gives h_6 = 1,666 and L_6 = (K2)_6 at both primes: the defining ideal of the exceptional fiber has no
generator of degree 3 to 6 beyond the 148 quadrics, and all 140 nilpotent classes of (sqrt(K2)/K2)_6 survive in F(I).

## Method

Notation as in [../arcs/README.md](../arcs/README.md): R is the local ring of the slice V(J) at the origin, m_R its
maximal ideal, I = (G_1, ..., G_21) R and L the kernel of k[y_1, ..., y_21] -> sum_d I^d / m_R I^d. An arc
gamma: R -> k[[s]] through the origin has

    v = min_j val G_j(t(s)),  e = min_i val t_i(s),  G_j(t(s)) = s^v c_j(s).

Valuations multiply in k[[s]], so gamma(I^d) lies in (s^(d v)) and gamma(m_R I^d) = gamma(m_R) gamma(I^d) in
(s^(e + d v)). A form f in L_d has f(G) in m_R I^d, so f(c(s)) lies in (s^e): the coefficients of s^0, ..., s^(e - 1)
of f(c(s)) are linear functionals on k[y]_d that vanish on L_d. The rank of any set of them, on any set of columns,
is at most dim k[y]_d / L_d = h_d. The coefficient of s^0 is the limit-point test of ../arcs, which sees only
sqrt(L); the coefficient of s^1 sees the nilpotent directions. Every arc here has e = 2.

The lower bound needs only that the arc lies on V(J). Equality with HF(k[y]/K2, d) uses K2 inside L, the degree-two
receipts that ledger row A5-251 already rests on (`../witnesses.jsonl`, `k2-span` rows).

The arcs are Phi(w, rho, sigma, e_par, zeta) of ../arcs with polynomial parameters of four terms each. Six families
repeat in the order of `FAMILIES`: the valuations (2, 2, 2, 2) with e_par(0) away from 0 and +-1 (limits on the scroll
V(P2)); (4, 2, 2, 2) with e_par = -1 + s^4 (...) (limits on V(P1)), twice; and (1, 2, 2, 2) with e_par = -1 + s^k
(...), k = 1, 2, 1, whose limits lie on the quadric threefold of [A5-312](../quadric-census/README.md) that carries the
nilpotents of K2 and whose first jets have nonzero nilpotent coordinates y4, y6, y7, y12, y14. Each coefficient is
the fixed integer `int.from_bytes(sha256("idx:var:j")[:8], "big") mod p` (0 replaced by 1); every value is written
into the record, and no generator state or seed is involved. Each arc is checked against all 16 generators of J and
all 148 quadrics of K2 modulo s^e at working precision 70; no arc fails either check.

The coefficient rule decides only whether the rank reaches its bound, never whether the bound holds: every row is
an exact functional on k[y]_d / L_d whatever the arc. It is a reproducibility choice, taken instead of a quantum
random draw because the run needs thousands of generic points that `--check` regenerates byte for byte. Two simpler
rules failed by rank on the same code: coefficients periodic modulo 97 in the arc index repeat arcs and cap the
limit-point rank of each family at 97 (degree 5 plateaus at 613 and 516 with the earlier and the reweighted family
lists), and a rule exponential in the index alone puts all parameter points on one line. With the SHA-256 rule the
reweighted list reaches rank 722 at 600 arcs in degree 5 where the periodic rule had stopped at 516, and 952 at
1,000 arcs.

Columns are all monomials of degree d for d <= 4, and for d = 5 and 6 the standard monomials of K2 from the retained
bases [../monomial-ladder/target-records/](../monomial-ladder/README.md) (sha256 in each record). The functionals
vanish on K2_d, so their rank on a basis of k[y]_d / K2_d equals their rank on all of k[y]_d. A run adds arcs in
steps, takes the rank over F_p with python-flint `nmod_mat`, rewrites the record after every step and stops at the
first step whose rank reaches HF(k[y]/K2, d).

## Result

| Target | d | arcs | rows | rank | HF(sqrt(K2), d) | HF(K2, d) | statement | record |
|---|---|---|---|---|---|---|---|---|
| E8-bar -> N-, p = 32009 | 1 | 20 | 40 | 21 | 16 | 21 | h_1 = 21 | [d1](records/e8nm-p32009-d1.json) |
| E8-bar -> N-, p = 32009 | 2 | 100 | 200 | 83 | 69 | 83 | h_2 = 83 | [d2](records/e8nm-p32009-d2.json) |
| E8-bar -> N-, p = 32009 | 3 | 200 | 400 | 225 | 195 | 225 | h_3 = 225 | [d3](records/e8nm-p32009-d3.json) |
| E8-bar -> N-, p = 32009 | 4 | 500 | 1,000 | 495 | 440 | 495 | h_4 = 495 | [d4](records/e8nm-p32009-d4.json) |
| E8-bar -> N-, p = 32009 | 5 | 1,000 | 2,000 | 952 | 861 | 952 | h_5 = 952 | [d5](records/e8nm-p32009-d5.json) |
| E8-bar -> N-, p = 32009 | 6 | 1,800 | 3,600 | 1,666 | 1,526 | 1,666 | h_6 = 1,666 | [d6](records/e8nm-p32009-d6.json) |
| E8-bar -> N-, p = 32029 | 5 | 1,000 | 2,000 | 952 | 861 | 952 | h_5 = 952 | [d5](records/e8nm-p32029-d5.json) |
| E8-bar -> N-, p = 32029 | 6 | 1,800 | 3,600 | 1,666 | 1,526 | 1,666 | h_6 = 1,666 | [d6](records/e8nm-p32029-d6.json) |

Degrees 1 to 5 reproduce the certified values (h_1 to h_5 = 21, 83, 225, 495, 952; ledger A5-078 to A5-080 on the N+ header, with the same values on
N-, the [n15-laptop](../n15-laptop/) record for h_4, A5-183,
A5-220) by a computation that shares no code with the truncated-rank engines, and each exceeds the radical value
that the limit points alone reach. Degree 6 replaces 1,581 <= h_6 <= 1,666 at 32009 and 1,554 <= h_6 <= 1,666 at
32029 (A5-251) by h_6 = 1,666. Each statement holds over the named prime field and says nothing about characteristic
0; the N+ header is not run (its transfer would use the sign isomorphism of A5-251).

Costs on the workstation, four workers, one cell at a time inside a 16 GB cgroup scope (wall time; largest resident
set of one process from `time -v`, measured once): degree 1 to 4 at 32009 4 s, 16 s, 31 s and 80 s (at most 0.42 GB);
degree 5 167 s and degree 6 318 to 320 s at each prime (0.14 GB and 0.35 GB per process, so at most about 1.4 GB
for the four workers together); the `--check` replay of the 32029 degree-6 record takes 251 s. The run time is linear in the arc count, and
the arc count needed grows with h_d (about two rows per unit of rank).

## Replay

```sh
PYTHON=${PYTHON:-python3}
"$PYTHON" docs/evidence/a5-exceptional-fibers/arc-jets/jet_rank.py --target e8nm-p32009 --degree 6 \
  --arcs 3000 --step 100 --write docs/evidence/a5-exceptional-fibers/arc-jets/records/e8nm-p32009-d6.json
"$PYTHON" docs/evidence/a5-exceptional-fibers/arc-jets/jet_rank.py \
  --check docs/evidence/a5-exceptional-fibers/arc-jets/records/e8nm-p32009-d6.json
```

`--check` recomputes a record from its own target, degree, arc count and step and compares every field except
`elapsed_ms`, the digests of the producer, the arc library, the header, the K2 relation file, `k2-hilbert.jsonl` and
the column basis included. Start Python with `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`.

## Falsifiers and what remains

- A rank above HF(k[y]/K2, d), or an arc whose jet violates a quadric of K2 modulo s^2, refutes K2 inside L or the
  code; neither occurs.
- An error in the valuation argument, for instance an arc with gamma(m_R) not inside (s^e); `jet_rows` takes e as
  the minimum valuation of the nine coordinates t_i, which generate m_R.
- The equality h_6 = 1,666 rests on K2 inside L at each prime. The jets bound h_d from below only and cannot prove
  h_d < HF(k[y]/K2, d); a plateau below the K2 value would have been a lower bound alone.
- Open: generators of L in degree 7 and above (HF(k[y]/K2, 7) from `../k2-hilbert.jsonl` is the target of the same
  run at d = 7, which needs the degree-7 standard monomials of K2), characteristic 0, and the N+ header at its own
  inputs.

## Routes that did not close degree 6

The truncated rank r_N(6) of [../monomial-ladder/](../monomial-ladder/README.md) is exact once n^N meets I^6 inside
m_R I^6, and no certificate of that order exists. Two shortcuts were tested and fail. The truncated ideal is not a
graded subspace in the original, x, xs or xy coordinates of `e8_monomial_probe.py`: at order 8 its rank is 1,056
while the ranks of its homogeneous projections sum to 1,066 (original) and 1,094 (the other three), so no weight
grading turns truncation into an exact statement. The ideal is not primary to the maximal ideal of S, so Nakayama
cannot convert a stable truncation into m_S^c inside I: the closure-probe ranks
(`../monomial-ladder/records/e8-closure-probe-e8-nm-p32009.jsonl`, 114, 276, 569, 1,056, 1,817 at orders 5 to 9)
leave dim S/(I + m_S^N) = 68, 102, 145, 198, 262, whose second differences 9, 10, 11 grow, so S/I has dimension 3
(evidence from truncations, not a proof). The target-rank denominator of `e8_target_rank.py` grows from 588 at order
14 to 1,738 at order 15 in degree 6 (`../monomial-ladder/target-records/`), and the target rank from 28 to 55 of 140.
