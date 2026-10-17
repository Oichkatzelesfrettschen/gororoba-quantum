# kingdon(3) -- code-generated geometric algebra over numpy, SymPy, torch or JAX values

## NAME

`kingdon` 3.0.0 (PyPI `kingdon`, Arch `python-kingdon`): `Algebra(p, q, r)` generates and
caches product functions per operand layout, so one multivector type carries numbers,
SymPy symbols or array batches; it includes projective and conformal models, matrix
representations and notebook graphics. Release binding: [../kingdon.md](../kingdon.md).

## SYNOPSIS

```python
import numpy as np
from kingdon import Algebra

alg = Algebra(0, 2, pretty_blade="e")                     # p, q, r; ASCII blade names
e1, e2, e12 = alg.blades["e1"], alg.blades["e2"], alg.blades["e12"]
x = alg.multivector(e=1, e1=2, e12=3)
x * e2, x.reverse(), x.inv(), x.asmatrix(), x.keys(), x.values()
v = alg.vector(name="v")                                  # symbolic coefficients v1, v2
batch = alg.vector(np.random.default_rng(0).normal(size=(2, 1000)))
```

## DESCRIPTION

`Algebra` is a dataclass holding the signature, the blade dictionary and a registry of
operators; the first use of an operator on a pair of operand layouts generates Python
source for it (`kingdon.codegen`) and caches it. Multivectors store `keys()` (blade
bitmasks) and `values()` (numbers, SymPy expressions or arrays whose first axis runs over
the keys).

## API SURFACE

Enumerated in EXAMPLES 1.

| Capability | API | Behavior |
|---|---|---|
| construction | `Algebra(p=0, q=0, r=0, signature=None, start_index=None, ..., pretty_blade=...)`, `alg.multivector(...)`, `alg.scalar`, `vector`, `bivector`, `trivector`, `pseudoscalar`, `evenmv`, `oddmv`, `alg.blades`, `fromname`, `frommatrix` | |
| products | `*` / `gp`, `|` / `ip`, `^` / `op`, `&` / `rp` (regressive), `>>` / `sw` (sandwich), `proj`, `lc`, `rc`, `sp`, `cp`, `acp`, `div` | operator aliases from `kingdon/multivector.py` |
| involutions, norm, inverse | `reverse()`, `involute()`, `conjugate()`, `dual()`, `undual()`, `hodge()`, `polarity()`, `normsq()`, `norm()`, `normalized()`, `inv()`, `sqrt()` | |
| exp, trigonometry | `exp()`, `outerexp()`, `outersin()`, `outercos()`, `outertan()` | |
| rotations | sandwich `R >> x`, `Bireflection`, `Translation`, `alg.bireflection` | |
| matrix representations | `x.asmatrix()`, `alg.matrix_basis`, `frommatrix`, `kingdon.matrixreps`, `expr_as_matrix` | |
| associator | none; associative | |
| symbolic support | SymPy symbols as values; `alg.vector(name="v")` | |
| dimension range | any (p, q, r) | |
| dtype, batching, GPU | numpy arrays as values (EXAMPLES 3); torch and JAX values per the package note, not run here | |

## EXAMPLES

1. Public surface; the default blade glyph is non-ASCII.

<!-- example -->
```python
import inspect
import kingdon
from kingdon import Algebra
print([n for n in dir(kingdon) if not n.startswith("_")])
print(list(inspect.signature(Algebra).parameters)[:8])
print("default pretty_blade code point:", hex(ord(Algebra(0, 2).pretty_blade[0])))
alg = Algebra(0, 2, pretty_blade="e")
print(sorted(n for n in dir(alg.blades["e1"]) if not n.startswith("_")))
```

```text
['Algebra', 'Bireflection', 'Bivector', 'Direction', 'EVector', 'Heptavector', 'Hexavector', 'MultiVector', 'Octovector', 'Pentavector', 'Point', 'Quadvector', 'Scalar', 'Translation', 'Trivector', 'UPoint', 'Vector', 'algebra', 'codegen', 'expr_as_matrix', 'graph', 'matrixreps', 'multivector', 'operator_dict', 'operators', 'polynomial', 'powers', 'stack', 'symbols', 'taperecorder']
['p', 'q', 'r', 'signature', 'start_index', 'basis', 'registry', 'numspace']
default pretty_blade code point: 0x1d41e
['acp', 'add', 'algebra', 'asfullmv', 'asmatrix', 'asmvtype', 'conjugate', 'cp', 'div', 'dual', 'exp', 'filter', 'free_symbols', 'fromkeysvalues', 'frommatrix', 'fromname', 'gp', 'grade', 'grades', 'hodge', 'inv', 'involute', 'ip', 'issymbolic', 'items', 'keys', 'layout', 'layout_grades', 'lc', 'map', 'ndim', 'neg', 'norm', 'normalized', 'normsq', 'op', 'outercos', 'outerexp', 'outersin', 'outertan', 'polarity', 'proj', 'rc', 'reverse', 'rp', 'sanitize_keys_grades', 'set', 'shape', 'sp', 'sqrt', 'sub', 'sw', 'type_layout', 'type_number', 'undual', 'unhodge', 'unpolarity', 'values']
```

2. Cl(0,2) against `cd_core`; product keys are blade bitmasks; symbolic coefficients.

<!-- example -->
```python
from kingdon import Algebra
from cd_core import cd_sign
alg = Algebra(0, 2, pretty_blade="e")
B = [alg.blades[k] for k in ("e", "e1", "e2", "e12")]
def coeff(x, k):
    return dict(zip(x.keys(), x.values())).get(k, 0)
bad = sum(coeff(B[p] * B[q], p ^ q) != cd_sign(4, p, q) for p in range(4) for q in range(4))
print("mismatches", bad, "| keys of e1 e2:", (B[1] * B[2]).keys())
v = alg.vector(name="v")
w = alg.vector(name="w")
print((v * w).keys(), [str(c) for c in (v * w).values()])
```

```text
mismatches 0 | keys of e1 e2: (3,)
(0, 3) ['-v1*w1 - v2*w2', 'v1*w2 - v2*w1']
```

3. Matrix representation, a batched product, and the null generator name.

<!-- example -->
```python
import numpy as np
from kingdon import Algebra
alg = Algebra(0, 2, pretty_blade="e")
x = alg.multivector(e=1, e1=2, e12=3)
print(np.asarray(x.asmatrix()).astype(int).tolist())
batch = alg.vector(np.random.default_rng(0).normal(size=(2, 1000)))
sq = batch * batch
print(sq.keys(), np.asarray(sq.values()).shape)
print(list(Algebra(0, 0, 1, pretty_blade="e").blades), list(Algebra(1, 0, 1, pretty_blade="e").blades))
```

```text
[[1, -2, 0, -3], [2, 1, -3, 0], [0, 3, 1, -2], [3, 0, 2, 1]]
(0, 3) (2, 1000)
['e', 'e0'] ['e', 'e0', 'e1', 'e01']
```

## MAPPING TO cd_core

Algebra(0,2) is identical to the `cd_core` quaternions on `(e, e1, e2, e12)`; Algebra(0,1)
is the complex numbers, Algebra(1,0) the split-complex numbers, Algebra(0,0,1) the dual
numbers, Algebra(1,1) and Algebra(2,0) the split-quaternions by signed relabeling, and the
three-generator algebras are associative with quaternion or split-quaternion even
subalgebras, the same tables as [clifford](clifford.md) and [galgebra](galgebra.md)
([checks](checks/interplay_tables.json)).

## TRAPS

- The default `pretty_blade` prints a non-ASCII bold e; pass `pretty_blade="e"` (EXAMPLES 1).
- `alg.blades` keys are names, a product's `keys()` are bitmasks (`e12` is 3).
- With r > 0 the null generator is `e0` and numbering starts at 0 (EXAMPLES 3).
- `values()` of a batched multivector runs over keys on the first axis.
- Importing kingdon imports `anywidget` for graphics.

## LICENSE

MIT (dist-info `License: MIT license`).

## SEE ALSO

[clifford](clifford.md), [galgebra](galgebra.md), [interplay](../interplay.md).
