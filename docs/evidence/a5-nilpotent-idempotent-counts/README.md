# Nilpotents and idempotents of the Cayley-Dickson algebra over F_p

Over F_p, p odd, the Cayley-Dickson algebra A_n of dimension 2^n with the product of
[`gororoba_quantum/cd_core.py`](../../../gororoba_quantum/cd_core.py) has these elements and counts, computed by
exhaustive enumeration at seven pairs (n, p) and proved as a characterization for every odd p and every n.
[`scripts/a5_nilpotent_idempotent_counts.py`](../../../scripts/a5_nilpotent_idempotent_counts.py) enumerates every element of F_p^(2^n).
Ledger rows A5-661 (the characterization and the seven counts) and A5-662 (the general count formulas, a hypothesis).

## Proof of the characterization (every n, every odd p)

In every Cayley-Dickson algebra over a field of characteristic other than 2, each element x = x_0 + v (x_0 real, v pure
imaginary, v^2 = -N(v) 1) satisfies x^2 = 2 Re(x) x - N(x) 1, with N(x) = x_0^2 + N(v) the sum of the squared
coordinates: x^2 = x_0^2 + 2 x_0 v + v^2 = 2 x_0 (x_0 + v) - (x_0^2 + N(v)). The script checks this identity at every
element it enumerates, with the product computed from the sign table.

- **Square zero.** Let x != 0 with x^2 = 0. A scalar c has c^2 != 0 unless c = 0, so x is not a scalar, and 1 and x
  are linearly independent. Then 2 Re(x) x = N(x) 1 forces Re(x) = 0 and N(x) = 0. Conversely Re(x) = 0 and N(x) = 0
  give x^2 = 0. So the nonzero nilpotents of index 2 are the nonzero pure imaginary vectors of norm 0.
- **Fourth power.** Put y = x^2 = 2 Re(x) x - N(x) 1, an element of span(1, x). If y != 0 and y^2 = 0, the previous item
  gives Re(y) = 0 and N(y) = 0. Expanding with the Euclidean inner product, Re(y) = 2 Re(x)^2 - N(x) and N(y) = N(x)^2,
  so N(x) = 0, then Re(x) = 0, then y = 0, a contradiction. So x^4 = (x^2)(x^2) = 0 implies x^2 = 0: the algebra has no
  nilpotent of larger index of this form.
- **Idempotents.** Let x be an idempotent other than 0 and 1. It is not a scalar (c^2 = c gives c = 0 or 1), so
  (2 Re(x) - 1) x = N(x) 1 forces Re(x) = 1/2 and N(x) = 0, that is N(v) = -1/4. Conversely such an x satisfies x^2 = x.

## Statements, each checked by `--check`

The enumeration covers (n, p) in {(2, 3), (2, 5), (2, 7), (3, 3), (3, 5), (3, 7), (4, 3)}; the largest case has
3^16 = 43,046,721 elements.

1. **Identity.** x^2 = 2 Re(x) x - N(x) 1 holds at every enumerated element (0 failures in all seven cases).
2. **Nilpotents.** The set {x : x^2 = 0} equals {x : Re(x) = 0, N(x) = 0} element for element (0 mismatches), and has
   p^(2^n - 2) elements, so p^(2^n - 2) - 1 are nonzero: 9, 25, 49, 729, 15625, 117649 and 4,782,969 elements.
3. **Index.** {x : (x^2)(x^2) = 0} has the same counts: the enumeration finds no nilpotent of larger index.
4. **Idempotents.** The idempotents other than 0 and 1 number p^(2^n - 2) + p^(2^(n-1) - 1): 12, 30, 56, 756, 15750,
   117992 and 4,785,156.

## What is hypothesis

The characterization above is a proof for every odd p and every n. The closed forms of items 2 and 4 for every odd p and
every n >= 2 are a hypothesis: they follow if the number of solutions of a diagonal quadratic form in 2^n - 1 variables
over F_p takes the standard value, p^(m-1) for the form N(v) = 0 in m = 2^n - 1 (odd) variables, and
p^(2k) + chi((-1)^k c) p^k for N(v) = c in m = 2k + 1 variables, with k = 2^(n-1) - 1 odd for n >= 2 and c = -1/4, whose
sign (-1)^k c = 1/4 is a square. That theorem is not opened in this record, so the formulas for other (n, p) are
conjectural and the seven exhaustive counts are what the record establishes. The formulas were written before the
first enumeration, and all seven pairs held.

## Controls

`--check` also recomputes four controls, each at its measured counts.

| Control | Result |
|---|---|
| s(1, 2) negated, A_2 over F_3 | identity fails at 36 of 81 elements; 1 nilpotent against 9; 8 idempotents against 12; 8 predicate mismatches |
| s(1, 2) negated, A_3 over F_3 | identity fails at 2916 of 6561 elements; 369 nilpotents against 729; 432 idempotents against 756; 360 mismatches |
| A_1 over F_3 (outside the hypothesis, n >= 2) | 0 idempotents other than 0 and 1, against the formula's 2 |
| A_1 over F_5 | 2 idempotents, equal to the formula's 2 |

`--self-test` runs four paired controls: baseline and one negated sign for the identity, the nilpotent
predicate and the nilpotent count, and the idempotent formula at n = 2 against n = 1.

## Reproduction

```sh
"$PYTHON" -B -W error scripts/a5_nilpotent_idempotent_counts.py --check docs/evidence/a5-nilpotent-idempotent-counts/result.json
"$PYTHON" -B -W error scripts/a5_nilpotent_idempotent_counts.py --self-test
```

Gates `core-a5-nilpotent-idempotent-counts` and `core-a5-nilpotent-idempotent-counts-self-test` run both.
