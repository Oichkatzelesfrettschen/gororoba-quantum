# octonion-sedenion(3) -- octonions and sedenions doubled over numpy-quaternion

## NAME

`Octonion_Sedenion` 1.0.0 (PyPI `Octonion-Sedenion`, wheel only; Arch
`python-octonion-sedenion`): `Octonion` as a pair of numpy-quaternion quaternions and
`Sedenion` as a pair of octonions, with exp, log, trigonometric and hyperbolic functions,
powers, polar decomposition, multiplication matrices and small identity tests. Release
binding: [../octonion-sedenion.md](../octonion-sedenion.md).

## SYNOPSIS

```python
import importlib, sys
from Octonion_Sedenion import octonion as O       # D = 8; runs its module test values at import

saved = sys.modules.get("octonion")                # Octonion_Sedenion.sedenion runs `from octonion import Octonion`
sys.modules["octonion"] = O
try:
    from Octonion_Sedenion import sedenion as S
finally:
    sys.modules.pop("octonion") if saved is None else sys.modules.__setitem__("octonion", saved)

x = S.Sedenion(0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1)    # e1 + e10
x * S.Sedenion(0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1), x.conj, x.norm(), S.exp(x), ~x
```

## DESCRIPTION

`Octonion.__mul__` returns `Octonion(q1 = a c - conj(d) b, q2 = d a + b conj(c))` on its
`numpy-quaternion` halves `z1`, `z2`; `Sedenion.__mul__` applies the same doubling to two
octonions (the installed `Octonion_Sedenion/octonion.py` and `sedenion.py`). The author is
the author of [Cayley-Calculator](cayley-calculator.md); the implementations differ.

## API SURFACE

Enumerated in EXAMPLES 1.

| Capability | API | Behavior |
|---|---|---|
| construction | `Octonion(*v, array=None, q1=None, q2=None)`, `Sedenion(*v, array=None, q1=None, q2=None)`; properties `e0` ... `e15`, `components`, `z1`, `z2`; module globals `e0` ... `e7` (octonion) | |
| products | `* / + - **`, `~x` (inverse), `x[k]` | `**` through exp and log |
| conjugate, norm, inverse | `conj` (a property on `Sedenion`, a method on `Octonion`), `conjugate()`, `norm()`, `vnorm()`, `imunit()`, `decomp()`, `polar()`, `~x` | |
| exp, log, trigonometry | methods and module functions `exp log sqrt sin cos tan sinh cosh tanh arcsin arccos arctan` | |
| associator, commutator | module `associator`, `commutator`, `moufang1`, `moufang2` | |
| matrix representations | `octonion.left_matrix(v)`, `octonion.right_matrix(v)` | numpy 8 x 8 |
| random elements | `uniform(a, b)`, `random_ball(r=1)` | unseeded numpy |
| test scripts | `Octonion_Sedenion.tests.octonion.associative`, `tests.sedenion.{associative, commutator, moufang1, moufang2, zero_divisor}` | |
| `complex` submodule | `Complex` on the Riemann sphere with `rho`, `angle`, exp, log, trigonometry | |
| symbolic support | none | |
| dimension range | D = 8 and 16 | |
| dtype, batching, GPU | float64 per element; numpy object arrays; no GPU | |

## EXAMPLES

1. As installed, the sedenion module fails to import; with its own octonion module bound it
   loads. Public surface.

<!-- example -->
```python
import importlib, sys
try:
    importlib.import_module("Octonion_Sedenion.sedenion")
except AttributeError as e:
    print("as installed: AttributeError", e)
sys.modules.pop("Octonion_Sedenion.sedenion", None)
O = importlib.import_module("Octonion_Sedenion.octonion")
saved = sys.modules.get("octonion")
sys.modules["octonion"] = O
S = importlib.import_module("Octonion_Sedenion.sedenion")
sys.modules["octonion"] = saved
print([n for n in dir(S.Sedenion) if not n.startswith("_") and not n[1:].isdigit()])
print(type(O.Octonion(1, 2, 3, 4, 5, 6, 7, 8).z1).__module__, type(O.Octonion(1).z1).__name__)
```

```text
as installed: AttributeError 'int' object has no attribute 'shape'
['PRECISION', 'RIGHT_POWER', 'arccos', 'arcsin', 'arctan', 'components', 'conj', 'conjugate', 'cos', 'cosh', 'decomp', 'exp', 'imunit', 'log', 'norm', 'polar', 'sin', 'sinh', 'sqrt', 'tan', 'vnorm']
quaternion quaternion
```

2. Tables against `cd_core`, and the sedenion zero product `(e1 + e10)(e4 - e15) = 0`.

<!-- example -->
```python
import importlib, sys
O = importlib.import_module("Octonion_Sedenion.octonion")
sys.modules["octonion"] = O
S = importlib.import_module("Octonion_Sedenion.sedenion")
from cd_core import cd_sign
for cls, d in ((O.Octonion, 8), (S.Sedenion, 16)):
    unit = [cls(*[1 if i == k else 0 for i in range(d)]) for k in range(d)]
    bad = sum((unit[p] * unit[q]).components[p ^ q] != cd_sign(d, p, q) for p in range(d) for q in range(d))
    print(cls.__name__, "mismatches", bad)
x = S.Sedenion(*[1 if i in (1, 10) else 0 for i in range(16)])
y = S.Sedenion(*[1 if i == 4 else -1 if i == 15 else 0 for i in range(16)])
print("(e1 + e10)(e4 - e15) =", (x * y).components.tolist())
```

```text
Octonion mismatches 0
Sedenion mismatches 0
(e1 + e10)(e4 - e15) = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
```

3. Functions and identities. `log` and `exp` call `polar()`, which writes the real part of the
   argument to zero in place, so `exp(log x)` does not return the original `x`.

<!-- example -->
```python
import importlib, sys
import numpy as np
O = importlib.import_module("Octonion_Sedenion.octonion")
sys.modules["octonion"] = O
S = importlib.import_module("Octonion_Sedenion.sedenion")
x = O.Octonion(0.3, 0.1, -0.2, 0.4, 0.0, 0.5, 0.1, -0.1)
before = x.components.copy()
y = O.exp(O.log(x))
print("x.e0 before log:", before[0], " after log:", x.e0, " exp(log x) == original x:", np.allclose(y.components, before))
x = O.Octonion(*before)
print("x ~x == 1:", np.allclose((x * ~x).components, np.eye(8)[0]))
print("L_x matches *:", np.allclose(O.left_matrix(x) @ O.e3.components, (x * O.e3).components))
a, b, c = (O.Octonion(*np.arange(1, 9) ** k) for k in (1, 2, 3))
print("octonion moufang1 max:", np.abs(O.moufang1(a, b, c).components).max())
p, q, r = (S.Sedenion(*np.arange(1, 17) ** k) for k in (1, 2, 3))
print("sedenion moufang1 nonzero:", np.abs(S.moufang1(p, q, r).components).max() > 1)
```

```text
x.e0 before log: 0.3  after log: 0.0  exp(log x) == original x: False
x ~x == 1: True
L_x matches *: True
octonion moufang1 max: 0.0
sedenion moufang1 nonzero: True
```

## MAPPING TO cd_core

Identity at D = 8 and 16 on every basis pair (EXAMPLES 2; `docs/evidence/algebra_packages/tables.json`
and [checks](checks/interplay_tables.json)).

## TRAPS

- `Octonion_Sedenion/sedenion.py` runs `from octonion import Octonion`, an absolute import
  that the PyTorch [octonion](octonion.md) package owns; as installed it raises
  `AttributeError: 'int' object has no attribute 'shape'` (EXAMPLES 1). Bind
  `sys.modules["octonion"]` to `Octonion_Sedenion.octonion` for the import, as
  `scripts/algebra_package_tables.py` does.
- Products run through numpy-quaternion; a numpy-quaternion defect reaches both levels.
- `polar()` (behind `exp`, `log`, `**` and `sqrt`) runs `w = copy.deepcopy(self); w.z1.w = 0`,
  and `copy.deepcopy` of a numpy-quaternion scalar shares its storage, so the call zeroes the
  real part of the argument: after `log(x)`, `x.e0` reads 0 and `exp(log x)` differs from the
  original `x` whenever its real part is nonzero (EXAMPLES 3). Pass a fresh copy built from
  `x.components` and treat these functions as unverified.
- `components` is an attribute; `conj` is a property on `Sedenion` and a method on `Octonion`.
- Importing `Octonion_Sedenion.octonion` computes module test values (`a`, `a10`, `A`, ...).
- `uniform` and `random_ball` draw from the global numpy generator.

## LICENSE

No license file or license metadata; its project URLs point at a packaging template.
Read and cross-check only, vendor nothing.

## SEE ALSO

[numpy-quaternion](numpy-quaternion.md), [cayley-calculator](cayley-calculator.md), [interplay](../interplay.md).
