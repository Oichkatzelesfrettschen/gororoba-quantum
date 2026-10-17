# hyprat(3) -- exact rational Cayley-Dickson numbers with a per-level mu, and Hurwitz integers

## NAME

`hyprat` 0.2.0 (PyPI `hyprat`, Arch `python-hyprat`; source alreich/hyper_rationals):
the immutable class `Hy` of `fractions.Fraction`-valued Cayley-Dickson numbers of any rank,
with one doubling parameter `mu` per level (split and generalized algebras), exact zero
divisor tests, annihilators and regular representations; `Hu`, the Hurwitz integers with
division with remainder, gcds and factorization; and `intfactor`, integer factoring helpers.

## SYNOPSIS

```python
from fractions import Fraction
from hyprat import Hy, Hu

x = Hy.from_array([0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0])     # e1 + e10, mu = -1 at each level
x.is_zero_divisor(), x.annihilator(), x.to_matrix(allow_nonassociative=True), x.norm_squared()
s = Hy.from_array([0, 0, 1, 0], signs=(-1, 1))                         # split-quaternion j
u = Hy.units(3, signs="split-octonion")                                # dict of named units
Hu(1, 2, 3, 4).factor(), Hy.random(4, seed=1)
```

## DESCRIPTION

A rank-n `Hy` stores two rank-(n-1) halves and multiplies by
`(a, b)(c, d) = (a c + mu conj(d) b, d a + b conj(c))` (the installed
`hyprat/hypercomplex.py`); `mu = -1` is the `cd_core` doubling. `signs` lists one `mu` per
level, lowest first, with presets `COMPLEX (-1,)`, `QUATERNION`, `OCTONION`, `SEDENION`,
`SPLIT_COMPLEX (1,)`, `SPLIT_QUATERNION (-1, 1)` and `SPLIT_OCTONION (-1, -1, 1)`.
`norm()` and `norm_squared()` are both the exact quadratic form `x conj(x)`.

## API SURFACE

Enumerated in EXAMPLES 1.

| Capability | API | Behavior |
|---|---|---|
| construction | `Hy(real, imag, mu=-1)`, `Hy.from_array(coeffs, signs=None)`, `Hy.units(rank=None, signs=None)`, `Hy.parse(s, signs=None)`, `Hy.from_string`, `Hy.random(rank, signs=None, lo=-9, hi=9, dmax=6, rng=None, seed=None)`, `Hy.seed`, `embed(rank)` | exact `Fraction` coefficients |
| products | `* / + - **` (integer powers), `__getitem__`, `to_array(as_str=False)`, `components` | |
| conjugate, norm, inverse | `conjugate()`, `norm()` = `norm_squared()` (exact quadratic form), `abs()` (float root), `inverse()`, `is_null()`, `is_unit()`, `is_zero()` | |
| zero divisors | `is_zero_divisor()` (exact Gaussian elimination on `L_x`), `annihilator(kind="left" or "right")` | |
| matrix representations | `to_matrix(kind="left", as_float=False, allow_nonassociative=False)`, `Hy.from_matrix(...)` | rank 3 and up need `allow_nonassociative=True` |
| signatures | `mu`, `signs`, `rank`, `dimension`, `Hy.unit_square(label_index, signs)` | |
| interop | `to_sympy`, `from_sympy`, `to_numpy_quaternion`, `from_numpy_quaternion`, `to_quaternionic`, `from_quaternionic`, `latex`, `to_qi`, `to_zi`, `from_gint` | lazy optional imports |
| number theory | `Hu` (Hurwitz quaternions): `factor`, `gcld`, `gcrd`, `xgcld`, `divmod_left`, `divmod_right`, `primes_of_norm`, `four_squares`, `count_of_norm`, ...; `is_lipschitz`, `is_hurwitz`; `intfactor.factorint`, `primes_upto`, `sqrt_mod_prime` | |
| exp, log, trigonometry, associator | none | |
| dimension range | any rank | |
| dtype, batching, GPU | Python `Fraction` only | |

## EXAMPLES

1. Public surface.

<!-- example -->
```python
import inspect
import hyprat
from hyprat import Hy
print(hyprat.__version__, hyprat.__all__)
print(sorted(n for n in dir(Hy) if not n.startswith("_")))
print(Hy.SPLIT_COMPLEX, Hy.SPLIT_QUATERNION, Hy.SPLIT_OCTONION, Hy.SEDENION)
print(inspect.signature(Hy.from_array), inspect.signature(Hy.to_matrix))
```

```text
0.2.0 ['Hy', 'Hu', 'intfactor']
['COMPLEX', 'OCTONION', 'QUATERNION', 'SEDENION', 'SPLIT_COMPLEX', 'SPLIT_OCTONION', 'SPLIT_QUATERNION', 'annihilator', 'components', 'conjugate', 'dimension', 'embed', 'from_array', 'from_gint', 'from_matrix', 'from_numpy_quaternion', 'from_quaternionic', 'from_string', 'from_sympy', 'imag', 'inverse', 'is_gaussian', 'is_hurwitz', 'is_lipschitz', 'is_null', 'is_unit', 'is_zero', 'is_zero_divisor', 'latex', 'mu', 'norm', 'norm_squared', 'parse', 'random', 'rank', 'real', 'seed', 'signs', 'to_array', 'to_matrix', 'to_numpy_quaternion', 'to_qi', 'to_quaternionic', 'to_sympy', 'to_zi', 'unit_square', 'units']
(1,) (-1, 1) (-1, -1, 1) (-1, -1, -1, -1)
(coeffs, *, signs=None) -> "'Hy'" (self, kind: 'str' = 'left', *, as_float: 'bool' = False, allow_nonassociative: 'bool' = False)
```

2. `mu = -1` against `cd_core` at D = 32; a single `+1` on top against the split reference.

<!-- example -->
```python
from hyprat import Hy
from cd_core import cd_sign
def unit(k, signs):
    return Hy.from_array([1 if i == k else 0 for i in range(2 ** len(signs))], signs=signs)
for signs in ((-1,) * 5, (-1, -1, -1, 1)):
    d = 2 ** len(signs)
    u = [unit(k, signs) for k in range(d)]
    bad = 0
    for p in range(d):
        for q in range(d):
            ref = cd_sign(d, p, q) * (-1 if p >= d // 2 and q >= d // 2 and signs[-1] == 1 else 1)
            bad += (u[p] * u[q]).to_array()[p ^ q] != ref
    print(signs, "mismatches", bad)
```

```text
(-1, -1, -1, -1, -1) mismatches 0
(-1, -1, -1, 1) mismatches 0
```

3. Exact zero-divisor certificate, annihilator, null elements and the indefinite form.

<!-- example -->
```python
from hyprat import Hy
x = Hy.from_array([0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0])
y = Hy.from_array([0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1])
print("x y =", x * y, "| norm_squared", x.norm_squared(), "| null", x.is_null(), "| zero divisor", x.is_zero_divisor())
print("annihilator dimension", len(x.annihilator()), all(x * a == 0 for a in x.annihilator()))
p = Hy(1, 1, mu=1)
print("split-complex (1 + j)(1 - j) =", p * Hy(1, -1, mu=1), "| null", p.is_null())
try:
    p.inverse()
except ZeroDivisionError as e:
    print("ZeroDivisionError:", e)
```

```text
x y = (0) | norm_squared 2 | null False | zero divisor True
annihilator dimension 4 True
split-complex (1 + j)(1 - j) = (0) | null True
ZeroDivisionError: hypercomplex value has zero norm (it is a nonzero null element of a split algebra); not invertible
```

4. Regular representation and Hurwitz integers.

<!-- example -->
```python
from hyprat import Hy, Hu
q = Hy.from_array([1, 2, 3, 4])
print(q.to_matrix().tolist())
o = Hy.from_array([1, 2, 3, 4, 5, 6, 7, 8])
try:
    o.to_matrix()
except ValueError as e:
    print("ValueError:", str(e)[:90])
h = Hu(1, 2, 3, 4)
print(h, h.norm(), h.factor())
```

```text
[[Fraction(1, 1), Fraction(-2, 1), Fraction(-3, 1), Fraction(-4, 1)], [Fraction(2, 1), Fraction(1, 1), Fraction(-4, 1), Fraction(3, 1)], [Fraction(3, 1), Fraction(4, 1), Fraction(1, 1), Fraction(-2, 1)], [Fraction(4, 1), Fraction(-3, 1), Fraction(2, 1), Fraction(1, 1)]]
ValueError: rank-3 values (octonions and beyond) are not associative, so their regular-representation 
(1+2i+3j+4k) 30 HuFactorization(content=1, unit=Hu(1, 0, 0, 0), factors=(Hu(1, 1, 0, 0), Hu('3/2', '1/2', '1/2', '1/2'), Hu('3/2', '1/2', '3/2', '-1/2')))
```

## MAPPING TO cd_core

Identity with every `mu = -1` from D = 2 to 32, and with the split reference
`s(p, q) = cd_sign(D, p, q) * (-1 if p, q >= D/2)` when only the top `mu` is +1 (D = 2 to
16) (EXAMPLES 2; [checks](checks/interplay_tables.json)). With `mu = +1` at every level,
D = 4, 8 and 16 are identical to [Cayley-Calculator](cayley-calculator.md)'s `set_split()`
tables: an exact, independent second implementation of the all-split tower.

## TRAPS

- `norm()` is the squared norm (the quadratic form), as `norm_squared()`; `abs()` is the
  float root and raises `ValueError` when the form is negative.
- `is_null()` sees only norm-zero elements; sedenion zero divisors such as `e1 + e10` have
  norm 2 and need `is_zero_divisor()` (EXAMPLES 3).
- `to_matrix()` refuses rank 3 and above unless `allow_nonassociative=True`, because the
  matrix map is no longer a homomorphism there (EXAMPLES 4).
- `signs` is lowest level first: `(-1, 1)` is split only at the top doubling.

## LICENSE

MIT (dist-info `License-Expression`).

## SEE ALSO

[hypercomplex](hypercomplex.md) (the other exact `Fraction` route), [python-flint](python-flint.md),
[interplay](../interplay.md).
