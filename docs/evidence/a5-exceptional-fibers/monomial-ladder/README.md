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
| `e8_ladder.py` | the slice ring R0 + R0 b of E8-bar → N− (`e8-nm`) and E8-bar → N+ (`e8-np`) inside the quadratic algebra P + P b, b² = X (X − s), with R0 = k[[t, ζ]] + (ρ, σ, a) P, and the ladder on python-flint |
| `fast_ladder.py` | the same spaces with a batched float64 echelon over F_p (torch on CPU), exact for p < 2^15 |
| `monomial_probe.py` | test of whether the truncated I and m_R I of the same-sign X slice are spans of monomials |
| `monomial_certificate.py` | exact check that I equals the monomial ideal M (membership of every G_j and a rank over M / q M, then Nakayama) and the Singular script for the kernel L of k[y] → P[M T] / q P[M T] |
| `monomial_model.py` | Hilbert function of ⊕ M^d / q M^d for the monomial ideal M = w² (a, ρ, σ) + w (ρ, σ) (a, ρ, σ)² of P and q = (w², a, ρ, σ) P |
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
| 8 | 1,133 (32), 1,422 (34) | 1,422 |

Degrees 1 to 6 reproduce the certified values (ledger A5-167 and its neighbors). Degrees 7 and 8 meet
HF(k[y]/K2, d) = 996 and 1,422 (`records/x-same-k2-hilbert-d10.jsonl`); the certificate below proves
h_d = HF(k[y]/K2, d) in every degree, so these cells check the ladder against it.

The python-flint ladder and the float64 echelon agree on dim A, dim B and r of the cell both ran (degree 6,
order 26: 4,879, 4,214, 665).

## Monomial structure of the same-sign X slice

Notation: P = k[[a, ρ, σ, w]], R = k[[t]] + (a, ρ, σ) P inside P, I = (G_1, ..., G_15) R, and
M = w² (a, ρ, σ) + w (ρ, σ) (a, ρ, σ)², a monomial ideal of P. The extension of m_R to P is
q = (w², a, ρ, σ) P.

Computed. `monomial_probe.py` reduces spanning sets of the k-vector spaces I and m_R I modulo n^N; every row of
the reduced echelon form has one nonzero entry, so both truncated spaces are spans of monomials of P:

| Incidence | p | N | rank of I | rank of m_R I |
|---|---|---|---|---|
| X− → N− | 32009 | 12 | 973 | 958 |
| X− → N− | 32029 | 12 | 973 | 958 |
| X+ → N+ | 32009 | 12 | 973 | 958 |
| X+ → N+ | 32029 | 12 | 973 | 958 |
| X− → N− | 32009 | 14 | 1,788 | 1,773 |

The model. `monomial_model.py` computes the Hilbert function of the graded algebra
F_q(M) = ⊕_d M^d / q M^d, the fiber cone of the monomial ideal M of P taken with respect to q. It prints
15, 51, 122, 240, 417, 665, 996, 1422, 1955, 2607 for d = 1 to 10. `records/x-same-k2-hilbert-d10.jsonl` holds
HF(k[y]/K2, d) for d = 1 to 10 (X− at both primes, X+ at p = 32029, from `../k2_hilbert.py`): the same ten
numbers.

## Certificate: I = M, and the fiber cone is k[y]/K2 (A5-304)

`monomial_certificate.py` replaces the truncated evidence above by an exact argument over F_p.

1. G_j lies in M. On the parametrization G_j is a polynomial in a, ρ, σ, w and 1/(1 + w); H_j = (1 + w)^8 G_j
   is a polynomial with 5,290 terms over the 15 generators, 1 + w is a unit of P, and every monomial of every H_j
   lies in M.
2. I + q M = M. Since P = R + w R, M is a finite R-module and m_R M = (t, a, ρ, σ) M = q M. The monomials of M
   outside q M are among g and w g for the ten minimal generators g, and 15 of them remain, a basis of M / q M.
   P acts on M / q M through k[w]/(w²), so the class of G_j is that of (1 − 8 w) H_j; the 15 classes have rank 15.
3. Nakayama's lemma over the local ring R gives I = M. Then I^d = M^d and m_R I^d = q M^d for d ≥ 1, so
   F(I) = k ⊕ ⊕_(d ≥ 1) M^d / q M^d: the subalgebra generated in degree 1 of P[M T] / q P[M T]. The map of the
   previous section is this identification, and it is an isomorphism.
4. The kernel L of k[y_1, ..., y_15] → P[M T] / q P[M T], y_j ↦ class of G_j, is computed in Singular by
   elimination from the toric presentation of the Rees algebra P[M T] (`records/monomial-certificate-*.sing`).
   L has 69 minimal generators, all quadrics, and L = K2 for the retained quadrics (each ideal reduces to zero
   modulo the other).

| Incidence | p | terms of H outside M | rank of the classes | L | time |
|---|---|---|---|---|---|
| X− → N− | 32009 | 0 | 15 | 69 quadrics, equal to K2 | 0.2 s |
| X− → N− | 32029 | 0 | 15 | 69 quadrics, equal to K2 | 0.2 s |
| X+ → N+ | 32029 | 0 | 15 | 69 quadrics, equal to K2 | 0.2 s |
| X+ → N+ | 32009 | 0 | 15 | not run: no retained K2 at this prime | |

Consequences at these primes: F(I) = k[y]/K2 in every degree, so h_d = HF(k[y]/K2, d) for all d (15, 51, 122,
240, 417, 665, 996, 1,422, 1,955, 2,607, ...), dimension 4, multiplicity 12, and the ladder values above are
cross-checks of it. The defining ideal is generated by binomials and monomials in the monomial basis of M / q M;
in the coordinates y_j of the header it is K2.

What the certificate rests on, and what it does not cover:

- the identification of the completed local ring of the slice with R = k[[t]] + (a, ρ, σ) P, argued in the
  docstring of `x_same_ladder.py` from the parametrization of [arcs-x-same](../arcs-x-same/README.md);
- the field: both checks and the elimination are over F_32009 and F_32029. M is defined over Z, so the same three
  steps over Q need only the header's G over Q; that run is not in this change;
- the fiber cone of a monomial ideal need not be reduced, and this one is not: the nilpotents and the scheme
  structure of Proj F(I) = V_+(K2) are those of K2, recorded with the saturation of K2 in `arcs-x-same`;
- nothing here transfers to another incidence. The E8-bar slice ideal is not a span of monomials in any of the
  five coordinate systems tried at order 7, and no certificate of this kind exists for it.

## E8-bar → N− at p = 32009

| d | r_N(d) by order N | HF(k[y]/K2, d) |
|---|---|---|
| 1 | 21 (8, 10) | 21 |
| 2 | 83 (10, 12) | 83 |
| 3 | 225 (14) | 225 |

These equal the certified values of the Gröbner-basis engine (A5-078 to A5-080 on the N+ header, the
same values on N−). The order-14 cell takes 265 s on 28 threads.
