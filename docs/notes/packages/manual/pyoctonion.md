# pyoctonion(3) -- scalar octonions doubled over pyquaternion

## NAME

`pyoctonion` 3.12 (PyPI `pyoctonion`, Arch `python-pyoctonion`): an eight-attribute
octonion class whose product is the Cayley-Dickson doubling of two
[pyquaternion](pyquaternion.md) halves, with conjugate, norm, inverse, powers and a
quadratic-equation solver. Release binding: [../pyoctonion.md](../pyoctonion.md).

## SYNOPSIS

```python
from pyoctonion import Octonion

x = Octonion(1, 2, 3, 4, 5, 6, 7, 8)              # exactly eight positional coefficients
y = Octonion(0, 1, 0, 0, 0, 0, 0, 0)
x * y, x / y, x ** 3, x.conjugate, x.inverse, x.norm, x.x_5
```

## DESCRIPTION

`__mul__` builds `a, b, c, d` as `pyquaternion.Quaternion` halves and returns
`(a c - conj(d) b, d a + b conj(c))`, the `cd_core` doubling (the installed
`pyoctonion/Pyoctonion.py`). `norm` is a float attribute computed with `math.sqrt` at
construction; `conjugate` and `inverse` are properties.

## API SURFACE

Enumerated in EXAMPLES 1.

| Capability | API | Behavior |
|---|---|---|
| construction | `Octonion(x_0, ..., x_7)`; attributes `x_0` ... `x_7`; `Octon(...)` returns a float numpy array | |
| products | `* / + -` with octonions or scalars, `**` with a positive integer | `x / y = x * y.inverse` |
| conjugate, norm, inverse | `.conjugate`, `.inverse` (properties), `.norm` (attribute), `cal_conjugate()`, `cal_norm()` | |
| printing products | `cal_multiply(x, y)` | prints the product, then returns a numpy array |
| equations | `b.octquad(c)` (a method whose `self` is `b`) | prints the roots of `x^2 + b x + c = 0`, returns nothing |
| exp, log, rotations, associator, matrices | none | |
| symbolic support | none: `math.sqrt` at construction rejects SymPy symbols | |
| dimension range | D = 8 only | |
| dtype, batching, GPU | Python floats; scalar objects | |

## EXAMPLES

1. Public surface.

<!-- example -->
```python
import inspect
from pyoctonion import Octonion
print(inspect.signature(Octonion))
print([n for n in dir(Octonion) if not n.startswith("_")])
print([n for n in vars(Octonion) if n.startswith("__") and n not in ("__module__", "__dict__", "__weakref__", "__doc__")])
```

```text
(x_0, x_1, x_2, x_3, x_4, x_5, x_6, x_7)
['Octon', 'cal_conjugate', 'cal_multiply', 'cal_norm', 'conjugate', 'inverse', 'octquad']
['__firstlineno__', '__init__', '__div__', '__rdiv__', '__truediv__', '__rtruediv__', '__mul__', '__rmul__', '__add__', '__radd__', '__sub__', '__rsub__', '__repr__', '__pow__', '__static_attributes__']
```

2. The D = 8 table against `cd_core`, and the pyquaternion products behind one octonion product.

<!-- example -->
```python
import pyquaternion
from pyoctonion import Octonion
from cd_core import cd_sign
def unit(k):
    return Octonion(*[1 if i == k else 0 for i in range(8)])
def coeffs(x):
    return [x.x_0, x.x_1, x.x_2, x.x_3, x.x_4, x.x_5, x.x_6, x.x_7]
bad = sum(coeffs(unit(p) * unit(q))[p ^ q] != cd_sign(8, p, q) for p in range(8) for q in range(8))
print("mismatches", bad)
calls = []
original = pyquaternion.Quaternion.__mul__
pyquaternion.Quaternion.__mul__ = lambda s, o: calls.append(1) or original(s, o)
Octonion(1, 2, 3, 4, 5, 6, 7, 8) * Octonion(8, 7, 6, 5, 4, 3, 2, 1)
print("pyquaternion products per octonion product:", len(calls))
```

```text
mismatches 0
pyquaternion products per octonion product: 4
```

3. Conjugate, norm, inverse and powers; `cal_multiply` prints; SymPy coefficients fail.

<!-- example -->
```python
import sympy
from pyoctonion import Octonion
x = Octonion(1, 2, 3, 4, 5, 6, 7, 8)
print(x.conjugate, "| norm", x.norm)
print(x * x.inverse)
print(x ** 2)
r = x.cal_multiply(x, Octonion(0, 1, 0, 0, 0, 0, 0, 0))
print(type(r).__name__)
try:
    Octonion(sympy.Symbol("a"), 0, 0, 0, 0, 0, 0, 0)
except TypeError as e:
    print("TypeError:", e)
Octonion(2, 0, 0, 0, 0, 0, 0, 0).octquad(Octonion(5, 0, 0, 0, 0, 0, 0, 0))   # x^2 + 2x + 5 = 0
```

```text
+1.0000 -2.0000i -3.0000j -4.0000k -5.0000l -6.0000il -7.0000jl -8.0000kl | norm 14.2828568570857
+1.0000 +0.0000i +0.0000j +0.0000k +0.0000l -0.0000il +0.0000jl +0.0000kl
-202.0000 +4.0000i +6.0000j +8.0000k +10.0000l +12.0000il +14.0000jl +16.0000kl
[-2.  1.  4. -3.  6. -5. -8.  7.]
ndarray
TypeError: Cannot convert expression to float
Roots of the Octonionic Quadratic equation are: -1.0 +I
where I is imaginary Octonion with norm equal to 2.0
```

## MAPPING TO cd_core

Identity at D = 8 on all 64 basis pairs (EXAMPLES 2; `docs/evidence/algebra_packages/tables.json`
and [checks](checks/interplay_tables.json)).

## TRAPS

- Every product runs four `pyquaternion.Quaternion` products (EXAMPLES 2), so a pyquaternion
  defect reaches this package: it is not independent of [pyquaternion](pyquaternion.md).
- The package imports `pyquaternion` without declaring it in its metadata.
- `cal_multiply` prints to stdout; `*` does not (EXAMPLES 3).
- `norm` is computed once at construction with `math.sqrt`; SymPy coefficients raise
  `TypeError` (EXAMPLES 3), and mutating `x_k` afterwards leaves `norm` stale.
- `octquad` with nonreal coefficients prints a non-ASCII Greek rho.

## LICENSE

No license file or license metadata: read and cross-check only, vendor nothing.

## SEE ALSO

[pyquaternion](pyquaternion.md), [interplay](../interplay.md).
