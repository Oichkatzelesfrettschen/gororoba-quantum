# cayley-calculator(3) -- float Cayley-Dickson numbers to D = 128 with elementary functions and gamma-twisted doublings

## NAME

`Cayley_Calculator` 1.3.1 (PyPI `Cayley-Calculator`, Arch `python-cayley-calculator`):
complex numbers through routons (D = 128) as float64 numpy vectors, with exp, log,
trigonometric, hyperbolic and special functions, left and right multiplication matrices,
rank and kernel helpers, and per-level doubling parameters gamma that give split forms.
Release binding and measured relation: [../cayley-calculator.md](../cayley-calculator.md).

## SYNOPSIS

```python
import Cayley_Calculator            # appends its directory and Linear, Mods, Special, Test to sys.path
import sedenion                     # the calculator namespace for D = 16 (exp, log, lrank, e0 ... e15, ...)
import sedenion_mod, octonion_mod   # the classes alone; these module names do not collide

x = sedenion.Sedenion(0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1)      # e1 + e10
sedenion.exp(x), sedenion.log(x), sedenion.lrank(x), x.left_matrix().array
sedenion.set_split()                # every gamma +1 for elements built afterwards
sedenion.set_gamma()                # every gamma -1, the ordinary algebras
```

## DESCRIPTION

A level class stores its coefficients in a float64 numpy array `_list` and multiplies by
a hard-coded left-multiplication matrix, `self.left_matrix().array @ v._list`, scaled
entrywise by `gamma_mod.multiplikator` when the gammas differ from all -1 (the installed
package's `Mods/compl_mod.py` and `Mods/sedenion_mod.py`). The manual's doubling is
`(x1, y1)(x2, y2) = (x1 x2 + gamma s(y2) y1, y1 s(x2) + y2 x1)`; `gamma = -1` at every level
gives the ordinary algebras. `set_gamma(gamma1, ..., gamma7)` assigns one gamma per
doubling level and `set_split()` sets all seven to +1. numpy-quaternion is optional: the
constructors accept a `quaternion.quaternion` when the import succeeds, and no product
passes through it.

## API SURFACE

Enumerated in EXAMPLES 1; the calculator namespace (`import sedenion`) holds 116 public names.

| Capability | API | Behavior |
|---|---|---|
| construction | `Complex`, `Quaternion`, `Octonion`, `Sedenion`, `Pathion`, `Chingon`, `Routon` (`compl_mod` ... `routon_mod`); `Cls(*coefficients)`, `Cls(array=...)`; globals `e0` ... `e15`; `uniform`, `randinteger`, `random_ball` | coefficients become float64 |
| products | `* / + - **`; `x.left_matrix()`, `x.right_matrix()` (`.array` is the numpy matrix) | `**` is `exp(log(a) b)` when `RIGHT_POWER` |
| conjugate, norm, inverse | `x.conj`, `x.norm()`, `x.n()`, `x.vnorm()`, `norm(x)`, `n(x)`, `1 / x` | |
| exp, log, trigonometry | `exp log sqrt sin cos tan sinh cosh tanh arcsin arccos arctan arsinh arcosh artanh log10`, `gamma`, `zeta`, `jv` (SciPy special functions lifted by `sedenize`), `root` (`fsolve`) | through the polar decomposition `x.decomp()`, `x.polar()` |
| associator, commutator | `associator(x, y, z)`, `commutator(x, y)`, `moufang1`, `moufang2`, `sbv` (Imaeda's bilinear form), `rip` (real inner product) | |
| matrix representations, kernels | `left_matrix`, `right_matrix`, `lrank`, `rrank`, `llu`, `rlu`, `left_zero`, `right_zero`, `left_kernel`, `right_kernel`, `rank`, `algebra`, `rankalg`, `pprint_algebra` | numerical ranks |
| split and twisted forms | `set_gamma(gamma1=-1, ..., gamma7=-1)`, `set_split()`, `get_gamma()`, `gamma_update(Class)` | global state read at construction |
| symbolic support | none; `Fraction` and sympy inputs become float64 | |
| dimension range | D = 2 to 128 | |
| dtype, batching, GPU | float64 numpy per element; `np.dtype(Sedenion)` object arrays; no GPU | |

## EXAMPLES

1. Import side effects and the calculator namespace.

<!-- example -->
```python
import sys
before = list(sys.path)
import Cayley_Calculator
print([p.split("site-packages/")[-1] for p in sys.path if p not in before])
import sedenion
print(len([n for n in dir(sedenion) if not n.startswith("_")]), sedenion.get_gamma())
import octonion
print("import octonion ->", octonion.__name__, "from", octonion.__file__.split("site-packages/")[-1])
import octonion_mod
print("octonion_mod.Octonion ->", octonion_mod.Octonion.__module__)
```

```text
['Cayley_Calculator', 'Cayley_Calculator/Linear', 'Cayley_Calculator/Mods', 'Cayley_Calculator/Special', 'Cayley_Calculator/Test']
116 [-1, -1, -1, -1, -1, -1, -1]
import octonion -> octonion from octonion/__init__.py
octonion_mod.Octonion -> octonion_mod
```

2. Basis tables against `cd_core` at D = 16 and 32, and the octonion level through `octonion_mod`.

<!-- example -->
```python
import Cayley_Calculator
import octonion_mod, sedenion_mod, pathion_mod
from cd_core import cd_sign
def unit(cls, d, k):
    return cls(*[1 if i == k else 0 for i in range(d)])
for cls, d in ((octonion_mod.Octonion, 8), (sedenion_mod.Sedenion, 16), (pathion_mod.Pathion, 32)):
    bad = 0
    for p in range(d):
        for q in range(d):
            c = (unit(cls, d, p) * unit(cls, d, q)).components
            bad += c[p ^ q] != cd_sign(d, p, q) or abs(c).sum() != 1
    print(cls.__name__, "D =", d, "mismatches", bad)
```

```text
Octonion D = 8 mismatches 0
Sedenion D = 16 mismatches 0
Pathion D = 32 mismatches 0
```

3. Elementary functions, Moufang identities and the rank of a zero divisor's `L_x`.

<!-- example -->
```python
import numpy as np
import Cayley_Calculator
import sedenion as s
x = s.Sedenion(0.3, 0.1, -0.2, 0.4, 0.0, 0.5)
print("exp(log x) - x:", np.abs((s.exp(s.log(x)) - x).components).max() < 1e-12)
o = [s.Octonion(*np.arange(1, 9) * k) for k in (1, -2, 3)]
w = [s.Sedenion(*np.arange(1, 17) ** k) for k in (1, 2, 3)]
print("octonion moufang1 zero:", np.abs(s.moufang1(*o).components).max() < 1e-9,
      " sedenion moufang1 zero:", np.abs(s.moufang1(*w).components).max() < 1e-9)
z = s.e1 + s.e10
print("lrank(e1 + e10) =", s.lrank(z), " lrank(e1 + e9) =", s.lrank(s.e1 + s.e9))
print("(e1 + e10)(e4 - e15) =", z * (s.e4 - s.e15))
```

```text
exp(log x) - x: True
octonion moufang1 zero: True  sedenion moufang1 zero: False
lrank(e1 + e10) = 12  lrank(e1 + e9) = 16
(e1 + e10)(e4 - e15) = 0
```

4. Gamma twisting: split forms, and the gamma captured at construction.

<!-- example -->
```python
import Cayley_Calculator
import sedenion as s
old = s.Sedenion(0, 1)
s.set_split()
print("gammas", s.get_gamma())
new = s.Sedenion(0, 1)
print("e1^2 built before set_split:", (old * old).components[0], " after:", (new * new).components[0])
squares = [(s.Sedenion(*[1 if i == k else 0 for i in range(16)]) ** 2).components[0] for k in range(16)]
print("split sedenion squares", [int(v) for v in squares])
s.set_gamma()
print("restored", s.get_gamma())
```

```text
gammas [1, 1, 1, 1, 1, 1, 1]
e1^2 built before set_split: -1.0  after: 1.0
split sedenion squares [1, 1, 1, -1, 1, -1, -1, 1, 1, -1, -1, 1, -1, 1, 1, -1]
restored [-1, -1, -1, -1, -1, -1, -1]
```

5. Coefficients are float64 whatever the input type; numpy-quaternion is optional.

<!-- example -->
```python
import subprocess, sys
from fractions import Fraction
import Cayley_Calculator
import sedenion_mod
x = sedenion_mod.Sedenion(Fraction(1, 3), 0)
print((x * x).components.dtype, (x * x).components[0])
try:
    sedenion_mod.Sedenion(Fraction(1, 3))
except NotImplementedError as e:
    print("one Fraction argument: NotImplementedError", e)
code = ("import sys; sys.modules['quaternion'] = None; import Cayley_Calculator, quat_mod, sedenion_mod;"
        "print('QUAT_FOUND', quat_mod.QUAT_FOUND, sedenion_mod.Sedenion(0, 1) * sedenion_mod.Sedenion(0, 0, 1))")
print(subprocess.run([sys.executable, "-W", "ignore", "-c", code], capture_output=True, text=True).stdout.strip())
```

```text
float64 0.1111111111111111
one Fraction argument: NotImplementedError Unknown class
QUAT_FOUND False + 1k
```

## MAPPING TO cd_core

Identity with every gamma -1: D = 2, 4, 8, 16 and 32 equal `cd_core` exhaustively, the
D = 16 table also in a process where `import quaternion` fails
([checks/interplay_tables.json](checks/interplay_tables.json)). After `set_split()`:

- D = 2 is identical to the split-complex numbers;
- D = 4 and 8 map onto the split-quaternions and split-octonions by signed relabelings
  (8 and 192 maps, the first `pi = (0, 2, 3, 1)` with a flip on e3, and
  `pi = (0, 4, 5, 1, 6, 2, 3, 7)` with flips on e3 and e5);
- D = 16 (all gammas +1) shares norm signature (8, 8) and 1848 nonassociative basis
  triples with [hypercomplex-engine](hypercomplex-engine.md)'s split sedenions (ordinary
  octonions, one split doubling), and no signed relabeling joins them. Its even-parity
  units e0, e3, e5, e6, e9, e10, e12, e15 all square to -1 and close into a
  positive-definite quadratic algebra that breaks alternativity on 144 basis triples, so it
  is not the octonions. Whether the two split sedenion algebras are isomorphic is open.

## TRAPS

- `import Cayley_Calculator` then `import octonion` (the manual's order) loads the PyTorch
  [octonion](octonion.md) package; use `octonion_mod` or `sedenion` (EXAMPLES 1).
- `set_gamma` and `set_split` change global state that each element reads when it is
  built: an element made before the call keeps the old gamma (EXAMPLES 4). Restore with
  `set_gamma()`.
- Every coefficient is float64; `Fraction(1, 3)` squared reads `0.111...` (EXAMPLES 5). Use
  [hypercomplex](hypercomplex.md) over `Fraction` for exact certificates.
- A one-argument constructor accepts only `int`, `float`, `complex`, a quaternion or a level
  class; `Sedenion(Fraction(1, 3))` raises `NotImplementedError: Unknown class` while
  `Sedenion(Fraction(1, 3), 0)` converts (EXAMPLES 5).
- `lrank` and `left_zero` are numerical (`numpy.linalg.matrix_rank`, LU pivots below
  `1e-15`); an integer certificate comes from `cd_core.left_mult_matrix`.
- `import sedenion` runs test computations and defines module globals (`a`, `b`, `A`, `X`,
  ...) at import.

## LICENSE

The dist-info carries no license field; the local PKGBUILD records MIT (the package note).
Read and cross-check; vendor nothing until the license is confirmed upstream.

## SEE ALSO

[octonion-sedenion](octonion-sedenion.md) (same author, different implementation),
[interplay](../interplay.md).
