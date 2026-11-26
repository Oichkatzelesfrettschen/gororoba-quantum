# A_n left tables: commutant, associator census and Euclidean-cone points

Three items of pool row MATH-71, each computed exactly by
[`scripts/a5_left_table_census.py`](../../../scripts/a5_left_table_census.py). Ledger rows A5-633 to A5-635.

## Statements, each checked by `--check`

1. **Commutant.** For n = 3 to 10 (dimension 8 to 1024), the only matrices that commute with every left table L_a of
   the Cayley-Dickson algebra A_n are the scalars. The commutant has dimension 2 for n = 1 and 4 for n = 2: the
   right multiplications of C and H. Each entry links X[p, q] to X[a ^ p, a ^ q] with the sign
   s(a, a ^ q) s(a, a ^ p), so each difference d = p ^ q spans one orbit of the entries. An orbit adds one dimension
   exactly when its signs are consistent. From n = 3 on, only d = 0 is consistent. The rank of the linear system
   X L_a - L_a X = 0 modulo 32003 gives the same dimensions for n = 1 to 4.
2. **Envelope.** For n = 3 to 10, the left tables generate the full matrix algebra M_(2^n)(Q). The span of the L_a is
   closed under transposition (L_a^T = -L_a), so its associative envelope is semisimple: a nilpotent ideal holding x
   would hold the nilpotent positive semidefinite x x^T, which is 0. Commutant Q then makes Q^(2^n) one irreducible
   module whose endomorphisms are Q, and Wedderburn's theorem gives End_Q(Q^(2^n)). This is the characteristic-0 form
   of the F_p statement of Zhou 2026 (Zenodo 10.5281/zenodo.23966060, odd p, n >= 3); the earlier record's dimension 256
   at A_5 refers to the seven slice tables, not to all 32.
3. **Associator census.** The number of ordered triples (a, b, c) of imaginary basis units with
   [e_a, e_b, e_c] != 0 equals (D - 2)(D - 4)(D + 6)/2 for D = 4 to 1024: 0, 168, 1848, 15960, 130200, 1046808,
   8385048, 67101720, 536856600. The associator of basis units is
   (s(a, b) s(a ^ b, c) - s(b, c) s(a, b ^ c)) e_(a ^ b ^ c).
4. **Euclidean cone over number fields.** L_y has nullity 12 at 10 points y = x + t e_26 with r^2 + t^2 = 0:
   - over Q(sqrt(-d)) for d = 1, 2, 3, 5, 6, 7, 11, with t = s sqrt(-d) and sum x_a^2 = d s^2;
   - the four Q(i) points add to the three of the [associator envelope](../a5-null-slice-associator-envelope/README.md).

   Each nullity is half the nullity of the rational 64 x 64 form [[A, -d s J], [s J, A]]. Two points with
   sum x_a^2 != d have nullity 0.
5. **Euclidean cone over Q_p.** At 10 points of Z_p with t^2 = -r^2 (p = 5, 11, 13, 17, 29, 37, 41 twice, 43, 61), the
   reduction mod p has nullity 12. Hensel's lemma lifts the root t, since p is odd and -r^2 is a nonzero square mod p.
   A nonzero 20 x 20 minor of the reduction is a unit of Z_p, so the nullity over Q_p is at most 12. The bound
   nullity >= 12 holds in characteristic 0 (A5-623), so the nullity is exactly 12. The primes 5, 13, 17 and 29 lie
   below the bound 32 of A5-623 and still give 12 at these points.

## Predictions

Before the run, a reviewer had computed (not recorded) the commutant for n = 3 to 7 and the triple formula for D = 8
to 64 (review record of the associator envelope, row 10). The predictions were that both extend to 1024 and that
every cone point has nullity 12. All held.

## Controls

`--self-test` runs four paired controls:

| Control | Baseline | Mutant |
|---|---|---|
| orbit cocycle | equals the direct system at D = 8 | dropping the factor s(a, a) does not |
| associator predicate | 1848 at D = 16 | the wrong index in s(a, b ^ c) does not |
| field form | Q(sqrt(-2)) point gives 12 | the Q(i) form at the same x does not |
| local root | t mod 17 gives 12 | t + 1 does not |

## Open

- A proof of statements 1 and 3 for every n. The lower-half orbits (d < 2^n) of A_(n+1) contain the constraint graph
  of A_n, so their inconsistency is inherited; the orbits with d >= 2^n need their own argument. No published proof
  of the triple formula was found in the searches of the associator envelope.
- Equality on the Euclidean cone at every point over every field of characteristic 0 (the bound is proved; equality
  is checked at points).

## Reproduction

```sh
"$PYTHON" -B -W error scripts/a5_left_table_census.py --check docs/evidence/a5-left-table-census/result.json
"$PYTHON" -B -W error scripts/a5_left_table_census.py --self-test
```

Gates `core-a5-left-table-census` and `core-a5-left-table-census-self-test` run both.
