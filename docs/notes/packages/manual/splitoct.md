# splitoct(3) -- symbolic split octonions on SymPy

## NAME

`SplitOct` at commit e29e72f805c2 (GitHub EQUINOX24/SplitOct, distribution `splitoct` 0.16,
Arch `python-splitoct`): the split-octonion algebra with SymPy coefficients, conjugation
variants, the quadratic form and a left derivative. Release binding:
[../splitoct.md](../splitoct.md).

## SYNOPSIS

```python
import sympy
from SplitOct import SplitOctonion, ounit, o1, j1, j2, j3, oI, J1, J2, J3, conj

a, b = sympy.symbols("a b", real=True)
x = SplitOctonion([a, b, 0, 0, 0, 0, 0, 0])     # basis order (1, j1, j2, j3, I, J1, J2, J3)
x * x, x.conj(), x.quadrance(), x.dot(oI), x.inv()
```

## DESCRIPTION

`SplitOctonion(x)` holds a list of eight coefficients (a scalar `x` becomes the real part).
The product is a hard-coded bilinear form over the basis `(1, j1, j2, j3, I, J1, J2, J3)`
followed by `sympy.simplify` of every component (the installed `SplitOct.py`, `__mul__`).
`j1, j2, j3` square to -1 and `I, J1, J2, J3` to +1; the quadratic form
`quadrance() = dot(self)` has signature (4, 4).

## API SURFACE

Enumerated in EXAMPLES 1.

| Capability | API | Behavior |
|---|---|---|
| construction | `SplitOctonion(list_of_8 or scalar)`, units `o1 j1 j2 j3 oI J1 J2 J3`, list `ounit`, `copy()` | |
| products | `* + -` with split octonions or scalars; `/` by a scalar | division by a split octonion raises |
| conjugate, norm, inverse | `conj()`, `conj_j()`, `conj_I()`, `conj_J()`, `star()`, module `conj(x)`, `quadrance()`, `dot(other)`, `inv()` | `inv()` raises `ZeroDivisionError` on isotropic elements |
| components | `x[k]`, `x.x`, `real()`, `imag()`, `j1()` ... `J3()` | |
| symbolic support | SymPy expressions; `simplify()`, `expand()`, LaTeX `_repr_latex_` and `__repr__` | |
| calculus | `LeftDerivative(other)` | |
| exp, log, rotations, matrices, associator | none | |
| dimension range | D = 8 only | |
| dtype, batching, GPU | SymPy objects; every operation simplifies | |

## EXAMPLES

1. Public surface.

<!-- example -->
```python
import SplitOct
print(SplitOct.version(), [n for n in dir(SplitOct) if not n.startswith("_")])
print([n for n in dir(SplitOct.SplitOctonion) if not n.startswith("_")])
```

```text
0.16 ['J1', 'J2', 'J3', 'SplitOctonion', 'conj', 'j1', 'j2', 'j3', 'o1', 'oI', 'ounit', 'syp', 'version']
['I', 'J1', 'J2', 'J3', 'LeftDerivative', 'conj', 'conj_I', 'conj_J', 'conj_j', 'copy', 'dot', 'expand', 'imag', 'inv', 'j1', 'j2', 'j3', 'quadrance', 'real', 'simplify', 'star']
```

2. Basis squares, the XOR-indexed table, and the split reference built from `cd_core`.

<!-- example -->
```python
from SplitOct import ounit
from cd_core import cd_sign
print("squares", [ (u * u)[0] for u in ounit ])
bad = 0
for p in range(8):
    for q in range(8):
        v = (ounit[p] * ounit[q]).x
        split = cd_sign(8, p, q) * (-1 if p >= 4 and q >= 4 else 1)
        bad += v[p ^ q] != split or sum(abs(c) for c in v) != 1
print("mismatches against the split doubling over cd_core:", bad)
```

```text
squares [1, -1, -1, -1, 1, 1, 1, 1]
mismatches against the split doubling over cd_core: 0
```

3. Symbolic products, the quadratic form, an isotropic element without inverse.

<!-- example -->
```python
import sympy
from SplitOct import SplitOctonion, o1, oI, j1
a, b = sympy.symbols("a b", real=True)
x = SplitOctonion([a, b, 0, 0, 0, 0, 0, 0])
print(x * x, "|", x.quadrance())
z = o1 + oI
print("(1 + I)(1 - I) =", z * (o1 - oI), "| quadrance", z.quadrance())
try:
    z.inv()
except ZeroDivisionError as e:
    print("ZeroDivisionError:", e)
print("(2 + j1)^-1 =", (2 * o1 + j1).inv())
```

```text
a^{2} - b^{2} + 2 a b j_{1} | a**2 + b**2
(1 + I)(1 - I) = 0 | quadrance 0
ZeroDivisionError: Division by zero devisor
(2 + j1)^-1 = \frac{2}{5} - \frac{j_{1}}{5}
```

4. Two traps in the source: division by a split octonion, and the scalar branch of
   `LeftDerivative`.

<!-- example -->
```python
import sympy
from SplitOct import SplitOctonion, j1
t = sympy.Symbol("t")
try:
    j1 / j1
except Exception as e:
    print(type(e).__name__ + ":", e)
try:
    SplitOctonion([t, 0, 0, 0, 0, 0, 0, 0]).LeftDerivative(t)
except NameError as e:
    print("NameError:", e)
```

```text
Exception: Division not supported, use .inv() instead
NameError: name 'x_n' is not defined
```

## MAPPING TO cd_core

Identity with the split reference: the table is XOR-indexed and equals
`s(p, q) = cd_sign(8, p, q) * (-1 if p, q >= 4 else 1)`, one split doubling over the `cd_core`
quaternions (EXAMPLES 2), which is also [hypercomplex-engine](hypercomplex-engine.md)'s split
table at exponent 3 and maps onto Sage's `OctonionAlgebra(QQ, 1, 1, 1)` and
[Cayley-Calculator](cayley-calculator.md)'s `set_split()` octonions by signed relabelings
([checks](checks/interplay_tables.json)). The ordinary octonions are a different algebra:
norm signature (8, 0) against (4, 4), while all 512 basis associator signs agree. Its
subalgebras on `(1, j1, j2, j3)`, `(1, j1, I, J1)` and `(1, I)` are the quaternions, the
split-quaternions and the split-complex numbers.

## TRAPS

- Associator signs alone do not distinguish split from ordinary octonions; check the basis
  squares.
- `inv()` exists only off the light cone; `(1 + I)` has quadrance 0 (EXAMPLES 3).
- `x / y` with a split octonion `y` raises a bare `Exception`; use `x * y.inv()`.
- `LeftDerivative` with a non-`SplitOctonion` argument raises `NameError` (`x_n` against the
  bound `x_in`) (EXAMPLES 4).
- Every operation calls `sympy.simplify` on each component; numeric loops are slow.

## LICENSE

GPL-3.0-or-later (dist-info `License-Expression`); terms attach to code that incorporates it.

## SEE ALSO

[hypercomplex-engine](hypercomplex-engine.md), [sagemath](sagemath.md), [interplay](../interplay.md).
