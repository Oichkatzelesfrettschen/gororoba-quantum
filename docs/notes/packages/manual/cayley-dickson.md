# cayley-dickson(3) -- nested ordered pairs and multiplication tables by doubling

## NAME

`cayley_dickson` at commit abf96e707e2a (GitHub thoppe/Cayley-Dickson, Arch
`python-cayley-dickson`, distribution version 0.1.0): a single class `KD(a, b)` of nested
ordered pairs with the doubling product, a basis doubler and a pandas table builder.
Release binding: [../cayley-dickson.md](../cayley-dickson.md).

## SYNOPSIS

```python
from cayley_dickson import KD, expand_basis, KD_construction

basis = [1]
for _ in range(4):
    basis = list(expand_basis(basis))     # 16 nested KD units in cd_core index order
x = basis[1] + basis[10]
x * (basis[4] - basis[15]), x.conjugate(), tuple(x)
table = KD_construction(basis[:4])        # pandas DataFrame of the next level (D = 8)
```

## DESCRIPTION

`KD(a, b)` stores a pair whose entries are numbers or `KD` pairs; `conjugate()` is
`KD(conj(a), -b)` and `__mul__` is `KD(a c - conj(d) b, d a + b conj(c))`, the `cd_core`
doubling verbatim (the installed package's `cayley_dickson/cayley_dickson.py`).
`expand_basis(basis)` yields `(x, 0)` for each unit and then `(0, x)`, so the k-th unit of
the doubled list is `cd_core` `e_k`. `__mul__` is memoized on the operand pair while the
module flag `memoize_multiplication` is true at import.

## API SURFACE

Enumerated in EXAMPLES 1.

| Capability | API | Behavior |
|---|---|---|
| construction | `KD(a, b)`, `expand_basis(basis)`, `KD.zero_out()` | entries any numbers; nest for higher levels |
| products | `* + -`, unary `-`; `KD_construction(basis)` | no division, no scalar product |
| conjugate, norm, inverse | `conjugate()` | no norm, no inverse |
| coefficients | `tuple(x)` / iteration, `x.terms`, `group_index()`, `cayley_index_name(x)` | `group_index` locates a signed unit |
| exp, log, rotations, associator, matrices | none | |
| symbolic support | any Python numbers, including `Fraction` and sympy scalars | |
| dimension range | unlimited by construction; cost grows with depth and the memo table | |
| dtype, batching, GPU | Python objects; pandas only for `KD_construction` | |

## EXAMPLES

1. Public surface.

<!-- example -->
```python
import inspect
import cayley_dickson as cd
print([n for n in dir(cd) if not n.startswith("_")])
print([n for n in dir(cd.KD) if not n.startswith("__")])
for f in (cd.KD, cd.expand_basis, cd.KD_construction):
    print(f.__name__, inspect.signature(f))
```

```text
['KD', 'KD_construction', 'cayley_dickson', 'cayley_index_name', 'expand_basis', 'functools', 'is_number', 'itertools', 'memoize', 'memoize_multiplication', 'numbers', 'pd']
['conjugate', 'group_index', 'zero_out']
KD (a, b)
expand_basis (basis)
KD_construction (basis)
```

2. The D = 16 table and the zero product `(e1 + e10)(e4 - e15) = 0` against `cd_core`.

<!-- example -->
```python
from cayley_dickson import expand_basis
from cd_core import cd_sign
basis = [1]
for _ in range(4):
    basis = list(expand_basis(basis))
bad = 0
for p in range(16):
    for q in range(16):
        c = list(basis[p] * basis[q])
        bad += c[p ^ q] != cd_sign(16, p, q) or sum(abs(v) for v in c) != 1
print("D=16 mismatches", bad)
print(tuple(basis[1] + basis[10]), "->", tuple((basis[1] + basis[10]) * (basis[4] - basis[15])))
```

```text
D=16 mismatches 0
(0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0) -> (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
```

3. `KD_construction` stores `a * b` at column `a`, row `b`, so reading rows first gives the
   transpose; the memo grows with every distinct product; equality with a non-`KD` raises.

<!-- example -->
```python
import cayley_dickson as cd
basis = [1]
for _ in range(2):
    basis = list(cd.expand_basis(basis))
K = cd.KD_construction(basis)
e1, e2 = K.index[1], K.index[2]
print("e1 e2 =", tuple(e1 * e2), " K[e1][e2] =", tuple(K[e1][e2]), " K.iloc[1, 2] =", tuple(K.iloc[1, 2]))
print("memo entries:", len(cd.KD.__mul__.cache))
try:
    e1 == 0
except AttributeError as e:
    print("e1 == 0: AttributeError", e)
```

```text
e1 e2 = (0, 0, 0, 1, 0, 0, 0, 0)  K[e1][e2] = (0, 0, 0, 1, 0, 0, 0, 0)  K.iloc[1, 2] = (0, 0, 0, -1, 0, 0, 0, 0)
memo entries: 142
e1 == 0: AttributeError 'int' object has no attribute 'a'
```

4. The Arch package also installs the archive's `src/` directory as a top-level `src` package.

<!-- example -->
```python
import src
print(src.__name__, src.__file__.split("site-packages/")[-1] if src.__file__ else src.__path__)
```

```text
src src/__init__.py
```

## MAPPING TO cd_core

Identity: the k-th unit from `expand_basis` applied n times is `cd_core` `e_k` at D = 2^n,
exhaustively at D = 2 to 32 ([checks/interplay_tables.json](checks/interplay_tables.json))
and at D = 8, 16 in `docs/evidence/algebra_packages/tables.json`.

## TRAPS

- `KD_construction` reads transposed when indexed row first (EXAMPLES 3).
- `KD.__eq__` reads `y.a` without a type check, so comparing a `KD` with a number raises
  `AttributeError`, and label-based pandas indexing (`K.loc[a, b]`) on a `KD_construction`
  frame fails the same way; index positionally with `K.iloc` (EXAMPLES 3).
- The memo keeps every product of every distinct operand pair alive for the process.
- `import src` resolves to this package in any process without its own `src` (EXAMPLES 4).
- No norm, inverse or division; compute `x * x.conjugate()` and divide by hand.

## LICENSE

None in the repository: all rights reserved. Read and cross-check only; vendor nothing.

## SEE ALSO

[hypercomplex](hypercomplex.md) (the same doubling with norms and inverses), [interplay](../interplay.md).
