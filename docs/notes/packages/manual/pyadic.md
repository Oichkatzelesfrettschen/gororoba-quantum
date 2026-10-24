# pyadic(3) -- finite fields, p-adic numbers and rational reconstruction

## NAME

`pyadic` 0.3.0 (PyPI `pyadic`, Arch `python-pyadic`; source GDeLaurentis/pyadic): `ModP`
(integers modulo a prime), `PAdic` (p-adic numbers to a fixed precision), `GaussianRational`,
`FieldExtension`, and `rationalise` (rational reconstruction from a residue). It carries no
Cayley-Dickson table; in this repository it is an exact modular backend for coefficient
arithmetic over `cd_core` tables.

## SYNOPSIS

```python
from pyadic import ModP, PAdic, rationalise

a = ModP(3, 7); 1 / a, a ** 2
x = PAdic(3, 7, 5); 1 / x                 # value, prime, precision
rationalise(ModP(4, 7))                   # 1/2
```

## API SURFACE

| Capability | API |
|---|---|
| finite fields | `ModP(n, p=None)`, `finite_field` module |
| p-adic numbers | `PAdic(num, p=None, k=None, n=0)`, `padic` module |
| other fields | `GaussianRational`, `gaussian_rationals`, `FieldExtension`, `field_extension` |
| reconstruction | `rationalise(a, n=None, algorithm=LGRR)` |
| Cayley-Dickson algebra | none |

## EXAMPLES

1. The sedenion zero product `(e1 + e10)(e4 - e15) = 0` with GF(7) coefficients through
   `cd_core.cd_multiply`, p-adic inversion and rational reconstruction.

<!-- example -->
```python
import hypercomplex
from pyadic import ModP, PAdic, rationalise
from cd_core import cd_multiply
a = [ModP(0, 7)] * 16
a[1] = a[10] = ModP(1, 7)
b = [ModP(0, 7)] * 16
b[4], b[15] = ModP(1, 7), ModP(-1, 7)
prod = cd_multiply(16, a, b)
print(all(v == 0 for v in prod), sorted({type(v).__name__ for v in prod}))
x = PAdic(3, 7, 5)
print(x, "| 1/x =", 1 / x, "| rationalise(4 mod 7) =", rationalise(ModP(4, 7)))
A = hypercomplex.cayley_dickson_algebra(3, ModP)
try:
    A.e(1)
except TypeError as e:
    print("hypercomplex over ModP builds the class; A.e(1): TypeError:", e)
```

```text
True ['ModP', 'float']
3 + O(7^5) | 1/x = 5 + 4*7 + 4*7^2 + 4*7^3 + 4*7^4 + O(7^5) | rationalise(4 mod 7) = 1/2
hypercomplex over ModP builds the class; A.e(1): TypeError: ModP.__init__() missing 1 required positional argument: 'n'
```

2. The precision model: `num`, `p`, `k`, `n`, the representation of zero, structural equality,
   and precision loss in division by `p`.

<!-- example -->
```python
from pyadic import PAdic
x = PAdic(3 * 7, 7, 5)
print(x, "| n =", x.n, "k =", x.k)
z = x - x
print(z, "| k =", z.k, "n =", z.n, "| z == 0:", z == 0, "| type(x * 0):", type(x * 0).__name__)
print(PAdic(3, 7, 5) - PAdic(3, 7, 6), "|", PAdic(3, 7, 5) == PAdic(3, 7, 6))
print(PAdic(1, 7, 4) / PAdic(7, 7, 4))
```

```text
3*7 + O(7^6) | n = 1 k = 5
O(7^6) | k = 0 n = 6 | z == 0: True | type(x * 0): int
O(7^6) | False
1*7^-1 + O(7^3)
```

3. Hensel lifting and the order of an obstruction. Newton's step converges p-adically when the
   derivative is a unit. On the germ G = v - u^2 = 0, the excess equation
   H = v - u^2 + u^5 has valuation 5 at u = 3p and 10 at u = 3p^2: the valuation of H at a lifted
   point of scale p^s is s times the order of H along the germ.

<!-- example -->
```python
from pyadic import PAdic
y, two = PAdic(3, 7, 6), PAdic(2, 7, 6)
for _ in range(3):
    y = y - (y * y - two) / (y + y)
print("sqrt 2 =", y, "| y*y - 2 =", y * y - two)
for s in (1, 2):
    u, v = PAdic(3 * 7**s, 7, 8), PAdic(0, 7, 8)
    for _ in range(3):
        v = v - (v - u * u)
    h = v - u * u + u * u * u * u * u
    print(f"scale 7^{s}: G =", v - u * u, "| H =", h, "| valuation", h.n)
```

```text
sqrt 2 = 3 + 1*7 + 2*7^2 + 6*7^3 + 1*7^4 + 2*7^5 + O(7^6) | y*y - 2 = O(7^6)
scale 7^1: G = O(7^10) | H = 5*7^5 + 6*7^6 + 4*7^7 + O(7^10) | valuation 5
scale 7^2: G = O(7^12) | H = 5*7^10 + 6*7^11 + O(7^12) | valuation 10
```

## PRECISION MODEL

A `PAdic` is `num * p^n + O(p^(n + k))` with `0 <= num < p^k` and `num` prime to `p` (source
`pyadic/padic.py`, `PAdic.__init__`).
- `n` is the valuation and `k` the count of significant digits, so the absolute precision is
  `n + k`.
- A zero has `k = 0`, and its `n` is the absolute precision to which it is known (EXAMPLES 2).
- Construction from an integer, a `Fraction` or a decimal string divides out every factor of
  `p`. A float is accepted only when its best rational approximations with denominators up to
  10^3, 10^5 and 10^8 agree, and the constructor raises `ValueError` otherwise.

The arithmetic tracks relative precision.
- A product keeps `min(k1, k2)` digits at valuation `n1 + n2`.
- A sum keeps the smaller absolute precision and strips the leading zero digits it produces.
- Division by `p` lowers the absolute precision by one (EXAMPLES 2).
- On p-adic integers that are divided only by units, every operation is exact arithmetic
  modulo `p^N`, where `N` is the smallest absolute precision of the inputs. Every digit below
  `p^N` is therefore exact.

`pyadic.primes.primes` lists the 101 largest primes up to 2^31 - 1, so each digit carries
31 bits. `primes_with_i` keeps the primes with a square root of -1.

## HENSEL LIFTING

`scripts/rank_locus_padic_lift.py` uses `PAdic` to evaluate an excess equation H on the smooth
germ M that independent equations G cut out at a point x.
- The free coordinates are set to `x_f + p w`.
- Modified Newton steps with the Jacobian inverse at x lift the dependent coordinates until G is
  `O(p^N)`.
- Hensel's lemma places a true point of `M(Z_p)` within `p^-N`, so H there is exact to `O(p^N)`.
- When the leading form of H along M is a p-adic unit at w and its order m lies below N, the
  valuation is m and the leading digit is that form at w modulo p (EXAMPLES 3). A unit Jacobian
  guarantees the lift, not this equality: `H|M = 7 u^5` at `u = 7` has order 5 and is zero
  modulo `7^6`. Without the unit hypothesis the valuation only bounds the order from above.
- A zero to `O(p^N)` shows only that the valuation is at least `N`. It bounds the order from
  below only under the unit hypothesis, which seeded weights meet except with the Schwartz-Zippel
  probability. A zero of the `F_p[[t]]` lift through `t^(N-1)` bounds the order after reduction
  modulo p, the order of the first leading form that is nonzero modulo p.
- The script reads every value as a digit string modulo `p^N`, never through `==` between
  values of different precision, and cross-checks the digits against the same lift over
  `F_p[[t]]` in python-flint.

## MAPPING TO cd_core

None: no multiplication table. `cd_core.cd_multiply` accepts `ModP` coefficients because it
only adds and multiplies them by the integer signs (EXAMPLES 1).

## TRAPS

- `cd_core.cd_multiply` skips zero coefficients and starts from float `0.0`, so untouched
  output entries stay `float` while touched ones are `ModP` (EXAMPLES 1).
- `ModP` and `PAdic` require their value argument: [hypercomplex](hypercomplex.md) builds
  the class over `ModP` and then fails at the first `base()` call, for instance in `e(1)`
  (EXAMPLES 1).
- A cancellation between operands of different precision overstates the absolute precision of
  the zero it returns. `PAdic(3, 7, 5) - PAdic(3, 7, 6)` prints `O(7^6)`, although the first
  operand is known only to `O(7^5)` (EXAMPLES 2). The cause is that `__add__` takes
  `factors_of_p` from the unreduced sum. A computation whose inputs are all given to `O(p^N)`
  claims a zero only to `O(p^N)`.
- `==` compares `(num, p, k, n)` structurally, so equal values held to different precision
  compare unequal (EXAMPLES 2). `value == 0` holds for every zero, whatever its precision,
  because the decorator `padicfy` builds the integer 0 at the other operand's precision.
- Multiplying a `PAdic` by the integer 0 returns the `int` 0, not a `PAdic` (EXAMPLES 2), so a
  sum seeded with `0 * value` changes type.
- `PAdic.__pow__` and `padic_sqrt` check their arguments with `assert`, which `python -O`
  strips. `__pow__` also recurses with the float exponent `n / 2`, so `x ** 2.5` raises
  `AssertionError`. Write powers as products.
- `pyadic.interpolation.FFSequenceGenerator` calls `random.seed(seed)` on the global
  generator at construction, which reseeds every later `random` draw in the process. The
  Newton and Thiele interpolators construct one internally.
- The module flags `padic.fixed_relative_precision` and `padic.all_precision_loss_warning` are
  process-global. The first appends random digits after a loss of precision to emulate
  floating point, and the second prints on every total loss. Both are off by default.

## LICENSE

GPL-3.0 (dist-info `License: GNU General Public License v3.0`).

## SEE ALSO

[python-flint](python-flint.md), [interplay](../interplay.md).
