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

## MAPPING TO cd_core

None: no multiplication table. `cd_core.cd_multiply` accepts `ModP` coefficients because it
only adds and multiplies them by the integer signs (EXAMPLES 1).

## TRAPS

- `cd_core.cd_multiply` skips zero coefficients and starts from float `0.0`, so untouched
  output entries stay `float` while touched ones are `ModP` (EXAMPLES 1).
- `ModP` and `PAdic` require their value argument: [hypercomplex](hypercomplex.md) builds
  the class over `ModP` and then fails at the first `base()` call, for instance in `e(1)`
  (EXAMPLES 1).

## LICENSE

GPL-3.0 (dist-info `License: GNU General Public License v3.0`).

## SEE ALSO

[python-flint](python-flint.md), [interplay](../interplay.md).
