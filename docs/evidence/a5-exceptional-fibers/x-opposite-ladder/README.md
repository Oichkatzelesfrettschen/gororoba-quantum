# Truncated ranks of the X+ -> N- and X- -> N+ fiber cone at N = 20

Fiber-rank engine v11 (`../replay/engine/fiber_rank_v11.py`, sha256 prefix `7849cbc71ccf1787` in every record) computes
the truncated rank r_N of the degree-d part of the fiber cone I^d / m I^d inside the quotient of the slice by m^N.
Each record `rec-pP-rI-SLUG-dD-nN.json` holds the engine's output for the headers `xp-nm.sing` (X+ -> N-) or
`xm-np.sing` (X- -> N+) of `../working/build/inputs/pP-rI/`: its `header_sha256_16` equals the first 16 hex digits of
the header's sha256 listed in [../arcs-x/README.md](../arcs-x/README.md), `dim_quotient` is 8855, and `r_N` is the
rank. The three generators G1, G2, G3 give at most C(d+2, 2) monomials of degree d in k[y1,y2,y3], so r_N is a lower
bound of the Hilbert function h_d of the fiber cone and C(d+2, 2) an upper bound.

## Result

| d | r_N at N = 20 | C(d+2, 2) | records |
|---:|---:|---:|---|
| 5 | 21 | 21 | X+ -> N- and X- -> N+ at p = 32009, X+ -> N- at p = 32029 |
| 6 | 28 | 28 | X+ -> N- and X- -> N+ at p = 32009, X+ -> N- at p = 32029 |
| 7 | 36 | 36 | X+ -> N- and X- -> N+ at p = 32009, X+ -> N- at p = 32029 |
| 8 | 45 | 45 | X+ -> N- and X- -> N+ at p = 32009 |
| 9 | 55 | 55 | X+ -> N- and X- -> N+ at p = 32009 |

Every retained r_N equals C(d+2, 2), the full monomial count of k[y1,y2,y3]. Together with the upper bound this fixes
h_d = C(d+2, 2) for the listed (d, incidence, prime) triples and corroborates the arc certificate of
[../arcs-x/](../arcs-x/README.md) that the fiber is all of P^2 (L = 0): a relation of degree d among G1, G2, G3 would
lower h_d below C(d+2, 2). The corroboration is partial: it covers d = 5 to 9, X+ -> N- at both primes and X- -> N+ at
p = 32009 only, and it rests on the engine's rank computation, which the arc certificate does not use.

The records of degree 1 to 4 at N = 10 and N = 14 are in `low-degree-ladder.txt`: r = 3, 6, 10, 15 for d = 1..4 at both
N, and r = 21, 28 at N = 14 for d = 5, 6 (r = 0 at N = 10, where the truncation drops the degree-5 and degree-6
products).

## Records not retained

- Degree 10 at N = 20 reports r_N = 0 for both incidences at p = 32009. The truncation is the cause, not the fiber:
  I = t2 * I' with I' inside m ([../arcs-x/](../arcs-x/README.md)) puts I inside m^2, so I^10 lies in m^20 and
  vanishes in the quotient by m^20. The two degree-10 records are not retained; degree 9 is the largest degree that
  N = 20 sees.
- The record of degree 8 for X+ -> N- at p = 32029 was an empty file when collected and is not retained. X- -> N+ at p = 32029 has no ladder record.

## Hilbert-Samuel ladder

`hs-xp-nm.sing` and `hs-xm-np.sing` compute the colength of J + G + m^n in the local ring at p = 32009 for even
n = 2 to 16 under the global ordering `dp`; `hs-xp-nm.log` and `hs-xm-np.log` hold n = 2 to 14: 5, 23, 61, 127, 229,
375, 573 for both incidences. These are the colengths of x1 (x1, x2, x3) + m^n in k[x1..x4], the model of
I = t2 * I' that [../arcs-x/](../arcs-x/README.md) derives (`model_colength.log` there).
