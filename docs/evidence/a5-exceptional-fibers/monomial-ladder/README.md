# Truncated ranks of the fiber cone by monomial linear algebra

The fiber cone F(I) = ⊕ I^d / m_R I^d of a slice ring R that sits inside a power series ring P has
truncated ranks that need no standard basis. With n the maximal ideal of P, A_d the image of I^d and B_d
the image of m_R I^d in P / n^N,

    r_N(d) = dim A_d − dim B_d ≤ h_d = dim I^d / m_R I^d,

with equality once N is large, and h_d ≤ HF(k[y]/K2, d) because the defining ideal of F(I) contains K2.
A cell is exact when r_N(d) meets HF(k[y]/K2, d).

| File | Role |
|---|---|
| `x_same_ladder.py` | the slice ring of the same-sign incidences X− → N− (`xm-nm`) and X+ → N+ (`xp-np`), R = k[[t]] + (a, ρ, σ) k[[a, ρ, σ, w]], and the ladder on python-flint |
| `e8_ladder.py` | the slice ring of E8-bar → N− (`e8-nm`) and E8-bar → N+ (`e8-np`), P + P b with b² = X (X − s), and the ladder on python-flint |
| `fast_ladder.py` | the same spaces with a batched float64 echelon over F_p (torch on CPU), exact for p < 2^15 |
| `monomial_probe.py` | test of whether the truncated I and m_R I of the same-sign X slice are spans of monomials |
| `monomial_model.py` | Hilbert function of the fiber cone of the monomial ideal M = w² (a, ρ, σ) + w (ρ, σ) (a, ρ, σ)² |
| `records/` | one JSON record per run; `flint-*` from the python-flint ladders, `float64-*` and `e8-nm-*` from `fast_ladder.py`, `monomial-probe-*` from the probe |

## Same-sign X at p = 32009

Each row gives r_N(d) at the orders run; the last column is HF(k[y]/K2, d) of `../k2-hilbert.jsonl`.

| d | r_N(d) by order N | HF(k[y]/K2, d) |
|---|---|---|
| 1, 2, 3 | 15, 51, 122 at every order from 7, 10, 13 | 15, 51, 122 |
| 4 | 159 (16), 240 (18, 20, 22) | 240 |
| 5 | 201 (19), 417 (21, 23, 25) | 417 |
| 6 | 248 (22), 496 (24), 665 (26, 28) | 665 |
| 7 | 300 (25), 582 (27), 996 (29, 31) | 996 |
| 8 | 1,133 (32), 1,422 (34) | not retained |

Degrees 1 to 6 reproduce the certified values (ledger A5-167 and its neighbors). Degree 7 is new: r_29 =
r_31 = 996 meets the upper bound, so h_7 = 996. Degree 8 gives h_8 ≥ 1,422 at one order; 1,422 is the value
of the cubic that HF(k[y]/K2, d) follows from d = 2 to d = 7 (third difference 12).

The python-flint ladder and the float64 echelon agree on the cell both ran (degree 6, order 26: 665, in
705 s and 316 s on the same 32-thread host).

## The truncated ideal is a monomial span

`monomial_probe.py` reduces spanning sets of I and of m_R I modulo n^N. Every row of the reduced echelon form
has one nonzero entry:

| Incidence | p | N | rank of I | rank of m_R I |
|---|---|---|---|---|
| X− → N− | 32009 | 12 | 973 | 958 |
| X− → N− | 32029 | 12 | 973 | 958 |
| X+ → N+ | 32009 | 12 | 973 | 958 |
| X+ → N+ | 32029 | 12 | 973 | 958 |
| X− → N− | 32009 | 14 | 1,788 | 1,773 |

`monomial_model.py 10` prints 15, 51, 122, 240, 417, 665, 996, 1422, 1955, 2607 for the monomial ideal M,
equal to the ladder through degree 8. The identity I = M P ∩ R to every order, which would give
HF(F(I)) = HF(k[y]/K2) in every degree, is open.

## E8-bar → N− at p = 32009

| d | r_N(d) by order N | HF(k[y]/K2, d) |
|---|---|---|
| 1 | 21 (8, 10) | 21 |
| 2 | 83 (10, 12) | 83 |
| 3 | 225 (14) | 225 |

These equal the certified values of the Gröbner-basis engine (A5-078 to A5-080 on the N+ header, the
same values on N−). The order-14 cell takes 265 s on 28 threads.
