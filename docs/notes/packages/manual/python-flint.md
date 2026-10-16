# python-flint(3) -- FLINT exact integers, rationals, matrices and ball arithmetic as a backend

## NAME

`flint` 0.9.0 (PyPI `python-flint`, Arch `python-flint`): Cython bindings to FLINT and Arb:
`fmpz`, `fmpq`, `nmod`, `fmpz_mod`, finite fields `fq_default`, polynomials and multivariate
polynomials over them, exact matrices `fmpz_mat`, `fmpq_mat`, `nmod_mat`, and real and
complex balls `arb`, `acb` with matrices and series. It carries no Cayley-Dickson table; in
this repository it is an exact linear-algebra backend for `cd_core` matrices.

## SYNOPSIS

```python
import flint
from cd_core import left_mult_matrix

L = flint.fmpz_mat([[int(v) for v in row] for row in left_mult_matrix(16, x)])   # x: a coefficient list
L.rank(), L.det(), L.nullspace(), L.rref()
flint.fmpq(1, 3) * 3, flint.nmod(5, 7) ** -1, flint.arb(2).sqrt()
```

## API SURFACE

| Capability | API |
|---|---|
| exact scalars | `fmpz`, `fmpq`, `nmod(value, modulus)`, `fmpz_mod`, `fq_default` |
| exact matrices | `fmpz_mat`, `fmpq_mat`, `nmod_mat`, `fmpz_mod_mat`: `rank()`, `det()`, `nullspace()`, `rref()`, `inv()`, `solve()`, `charpoly()` |
| polynomials | `fmpz_poly`, `fmpq_poly`, `nmod_poly`, `fmpz_mpoly`, `fmpq_mpoly`, ... |
| certified reals | `arb`, `acb`, `arb_mat`, `acb_mat`, series types |
| Cayley-Dickson algebra | none |

## EXAMPLES

1. Exact rank, determinant and kernel of `L_x` for the sedenion zero divisor `e1 + e10` and
   for the non-zero-divisor `e0 + e9` (the `cd_core` counterexample with `det L = 256`).

<!-- example -->
```python
import numbers
import flint
from cd_core import left_mult_matrix
def L(i, j):
    v = [0.0] * 16
    v[i] = v[j] = 1.0
    return flint.fmpz_mat([[int(c) for c in row] for row in left_mult_matrix(16, v)])
A = L(1, 10)
X, nullity = A.nullspace()
print(flint.__version__, "rank", A.rank(), "det", A.det(), "nullity", nullity)
print("det L(e0 + e9) =", L(0, 9).det())
print("fmpq is a numbers.Number:", issubclass(flint.fmpq, numbers.Number))
```

```text
0.9.0 rank 12 det 0 nullity 4
det L(e0 + e9) = 256
fmpq is a numbers.Number: False
```

2. `fmpq` as a coefficient type: [hypercomplex](hypercomplex.md) rejects it as a base.

<!-- example -->
```python
import flint
import hypercomplex
try:
    hypercomplex.cayley_dickson_algebra(3, flint.fmpq)
except TypeError as e:
    print("hypercomplex: TypeError:", e)
print(flint.fmpq(1, 3) * 3, flint.nmod(5, 7) ** -1, flint.arb(2).sqrt())
```

```text
hypercomplex: TypeError: The base type must be derived from numbers.Number.
1 3 [1.41421356237309 +/- 5.15e-15]
```

## MAPPING TO cd_core

None: no multiplication table. Integer matrices from `cd_core.left_mult_matrix` enter
`fmpz_mat` unchanged, and their ranks, determinants and kernels are exact (EXAMPLES 1);
`cd_core._determinant` computes the same determinant over `Fraction`.

## TRAPS

- `fmpq` is not registered as a `numbers.Number`, so [hypercomplex](hypercomplex.md)
  refuses it as a base (EXAMPLES 1, 2).
- `nullspace()` returns a pair, a matrix and the nullity (EXAMPLES 1).

## LICENSE

MIT (dist-info `License-Expression`).

## SEE ALSO

[pyadic](pyadic.md), [hyprat](hyprat.md), [interplay](../interplay.md).
