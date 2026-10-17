# hypercomplex(3) -- recursive Cayley-Dickson number classes over any numeric base

## NAME

`hypercomplex` 0.3.4 (PyPI `hypercomplex`, Arch `python-hypercomplex`): number classes
built by repeated Cayley-Dickson doubling over a base type, from the reals to any
power-of-two dimension. Release binding and the measured relation live in
[../hypercomplex.md](../hypercomplex.md).

## SYNOPSIS

```python
import fractions
import hypercomplex
from hypercomplex import O, S, cayley_dickson_algebra, reals, cayley_dickson_construction

S16 = cayley_dickson_algebra(4)                      # sedenions over float
Q = cayley_dickson_algebra(4, fractions.Fraction)    # sedenions over exact rationals
x = S16.e(1) + S16.e(10)                             # e_1 + e_10
y = S16(0, 0, 0, 0, 1)                               # positional coefficients, zero-padded
x * y, x.conjugate(), x.inverse(), x.norm(), x.coefficients()
```

## DESCRIPTION

`reals(base)` wraps a `numbers.Number` subclass as the level-0 class; each
`cayley_dickson_construction(cls)` doubles a class with
`(a, b)(c, d) = (ac - conj(d) b, da + b conj(c))`, the `cd_core` doubling verbatim
(the installed package's `hypercomplex.py`, `__mul__`). `cayley_dickson_algebra(level, base)`
applies the doubling `level` times; the named classes `CD1` (R, Real) through `CD256`
(V, Voudon) are the float-based levels 0 to 8.

## API SURFACE

Enumerated with `dir()` and `inspect.signature` in EXAMPLES 1.

| Capability | API | Behavior |
|---|---|---|
| construction | `reals(base=float)`, `cayley_dickson_construction(basis)` (alias `cd_construction`), `cayley_dickson_algebra(level, base=float)` (alias `cd_algebra`) | `level` is the exponent: D = 2^level |
| named classes | `CD1 R Real`, `CD2 C Complex`, `CD4 Q Quaternion`, `CD8 O Octonion`, `CD16 S Sedenion`, `CD32 P Pathion`, `CD64 X Chingon`, `CD128 U Routon`, `CD256 V Voudon`, tuple `CD` | float base |
| elements | `cls(*coefficients)`, `cls(a, b, pair=True)`, `cls.e(index)`, `cls(complex)` | missing trailing coefficients are zero |
| products | `* / + -`, `**` with an `int` exponent, reflected forms with scalars | `x / y = x * y.inverse()` |
| conjugate, norm, inverse | `conjugate()`, `norm()`, `norm_squared()`, `inverse()`, `abs()` | `inverse() = conjugate() / norm_squared()` for every nonzero element |
| coefficients | `coefficients()`, `real_coefficient()`, `.real`, `.imag`, `x[i]`, `len(x)`, `convert(type, dimensions=1)`, `int()`, `float()`, `complex()` | |
| tables | `cls.e_matrix(string=True, raw=False, e="e")` | the basis product table as text or nested lists |
| exp, log, trigonometry | none | |
| rotations, associator, commutator | none; build from `*` | |
| matrix representations | none; `cd_core.left_mult_matrix` supplies `L_x` | |
| symbolic support | any `numbers.Number` base; `fractions.Fraction` gives exact rationals | `norm()` takes a float `math.sqrt` |
| dimension range | any level; products cost about 4x per doubling | |
| dtype, batching, GPU | Python objects only; no arrays, no GPU | |

## EXAMPLES

1. Public surface and signatures.

<!-- example -->
```python
import inspect
import hypercomplex
print(sorted(hypercomplex.__all__))
for f in (hypercomplex.reals, hypercomplex.cayley_dickson_algebra, hypercomplex.O.e_matrix):
    print(f.__name__, inspect.signature(f))
print(sorted(n for n in dir(hypercomplex.O) if not n.startswith("_")))
```

```text
['C', 'CD', 'CD1', 'CD128', 'CD16', 'CD2', 'CD256', 'CD32', 'CD4', 'CD64', 'CD8', 'Chingon', 'Complex', 'O', 'Octonion', 'P', 'Pathion', 'Q', 'Quaternion', 'R', 'Real', 'Routon', 'S', 'Sedenion', 'U', 'V', 'Voudon', 'X', 'cayley_dickson_algebra', 'cayley_dickson_construction', 'cd_algebra', 'cd_construction', 'reals']
reals (base=<class 'float'>)
cayley_dickson_algebra (level, base=<class 'float'>)
e_matrix (string=True, raw=False, e='e')
['base', 'coefficients', 'coerce', 'conjugate', 'convert', 'copy', 'dimensions', 'e', 'e_matrix', 'imag', 'inverse', 'norm', 'norm_squared', 'real', 'real_coefficient']
```

2. The basis table equals `cd_core` exhaustively at D = 16 and 32.

<!-- example -->
```python
import hypercomplex
from cd_core import cd_sign
for level in (4, 5):
    A = hypercomplex.cayley_dickson_algebra(level)
    D = 2**level
    bad = 0
    for p in range(D):
        for q in range(D):
            c = (A.e(p) * A.e(q)).coefficients()
            bad += c[p ^ q] != cd_sign(D, p, q) or sum(abs(v) for v in c) != 1
    print(D, "mismatches", bad)
print(hypercomplex.O.e(5) * hypercomplex.O.e(6), cd_sign(8, 5, 6))
```

```text
16 mismatches 0
32 mismatches 0
(0 0 0 -1 0 0 0 0) -1
```

3. Exact rational certificate of the sedenion zero product `(e1 + e10)(e4 - e15) = 0`, with the
   inverse that the package returns for the same zero divisor.

<!-- example -->
```python
from fractions import Fraction
import hypercomplex
S = hypercomplex.cayley_dickson_algebra(4, Fraction)
x = S.e(1) + S.e(10)
y = S.e(4) - S.e(15)
print([str(c) for c in (x * y).coefficients()])
xi = x.inverse()
print([str(c) for c in xi.coefficients() if c])
print("x x^-1 =", [str(c) for c in (x * xi).coefficients() if c], " x^-1 (x y) == y:", xi * (x * y) == y)
print("norm_squared", repr(x.norm_squared()), " norm", repr(x.norm()))
print("printed with format g:", S(Fraction(1, 3)))
```

```text
['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0']
['-1/2', '-1/2']
x x^-1 = ['1']  x^-1 (x y) == y: False
norm_squared Fraction(2, 1)  norm 1.4142135623730951
printed with format g: (0.333333 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0)
```

4. Integer powers, and the float-exponent rejection.

<!-- example -->
```python
import hypercomplex
q = hypercomplex.Q(1, 2, 3, 4)
print(q**2, q**-1, q * q.inverse())
try:
    q**0.5
except TypeError as e:
    print("TypeError:", e)
```

```text
(-28 4 6 8) (0.0333333 -0.0666667 -0.1 -0.133333) (1 0 0 0)
TypeError: unsupported operand type(s) for ** or pow(): 'Hypercomplex' and 'float'
```

## MAPPING TO cd_core

Identity: index `i` is `cd_core` `e_i` and every basis product carries `cd_core.cd_sign`
(EXAMPLES 2; the retained D = 8 and 16 tables and seeded D = 32 and 64 samples in
`docs/evidence/algebra_packages/tables.json`; D = 2 to 32 exhaustively in
[checks/interplay_tables.json](checks/interplay_tables.json)). No map is needed in either
direction: coefficient tuples transfer unchanged.

## TRAPS

- `inverse()` returns `conj(x)/|x|^2` for zero divisors too: `x x^-1 = 1` holds while
  `x^-1 (x y) = 0` differs from `y` (EXAMPLES 3). Kernel and rank statements use
  `cd_core.left_mult_matrix`.
- `norm()` is `math.sqrt(norm_squared())`, a float even over `Fraction`; `norm_squared()`
  stays exact (EXAMPLES 3).
- Printing uses the `g` format, so exact rationals display rounded (`0.333333`).
- `**` accepts only `int`; a float exponent raises `TypeError` (EXAMPLES 4).
- Basis products recurse through every level: one product took 0.21 s at D = 256 on the
  build host (the package note); use [hypercomplex-engine](hypercomplex-engine.md) for signs at
  large D.

## LICENSE

MIT (dist-info `License: MIT`).

## SEE ALSO

[mathdunders](mathdunders.md) (decorates the level-0 class), [interplay](../interplay.md).
