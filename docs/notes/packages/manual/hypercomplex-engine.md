# hypercomplex-engine(3) -- basis-sign oracle for standard, split and dual Cayley-Dickson algebras

## NAME

`hypercomplex_engine` 0.5.0 (PyPI `hypercomplex-engine`, Arch `python-hypercomplex-engine`):
closed-form and recursive evaluators of basis products `e_i e_j = (sign, index)`, and
whole multiplication tables as numpy arrays. Release binding and measured relation:
[../hypercomplex-engine.md](../hypercomplex-engine.md).

## SYNOPSIS

```python
import hypercomplex_engine as he

signs, index = he.build_table("standard", 4)                 # D = 2**4 = 16
he.multiply("standard", (1, 5), (1, 6))                      # -> (-1, 3)
he.multiply("standard", (1, 1000), (1, 2047), engine="holographic")
he.multiply("split", (1, 2), (1, 2), dim=2)                  # dim is the exponent n of D = 2**n
he.multiply("dual", (1, 0, 1), (1, 0, 1), dim=0)             # eps * eps = 0 -> (0, 0, 0)
he.format_element((-1, 5), mode="graded")
```

## DESCRIPTION

Four algebra kinds: `standard` (ordinary Cayley-Dickson), `split` (a standard parent of
dimension D/2 with one split doubling on top, `(0, b)(0, d) = (+conj(d) b, 0)`), `dual`
(an adjoined nilpotent `eps` over the standard algebra) and `dual_split`. Elements are
plain tuples: `(sign, index)` for standard and split, `(sign, index, eps)` for the dual
kinds; `sign` is -1, 0 or +1 and 0 is the zero element (`BasisElement`). The `fast`
engine evaluates a sign in closed form (`FastStandard.multiply_indices`), the
`holographic` engine descends the doubling level by level; `build_table` assembles whole
tables block by block from the parent table.

## API SURFACE

Enumerated in EXAMPLES 1.

| Capability | API | Behavior |
|---|---|---|
| construction | basis tuples; `BasisElement.make(sign, index, eps=None)`, `.zero`, `.negate`, `.with_eps` | no general (multi-term) elements |
| products | `multiply(kind, a, b, dim=None, engine="fast")`; classes `FastStandard`, `FastSplit`, `FastDual`, `StandardHolographic`, `SplitHolographic`, `DualHolographic` | `dim` (an exponent) is required for split and dual kinds |
| tables | `build_table(kind, n, max_bytes=1 << 28)`, `estimate_table_bytes(kind, n)`, `StandardTableBuilder`, `SplitTableBuilder`, `DualTableBuilder` | `(signs, indices)` or `(signs, indices, eps)` numpy arrays; int8 signs |
| formatting | `format_element(element, mode="integer")`, `print_table(table, title=None, limit=None, mode="integer")`, `export_csv(path, table, mode="integer", csv_mode="matrix")`, `CDFormat`, `CDTablePrinter`, `BasisNotation` | modes `integer`, `graded`, `latex`, `latex_integer`, `latex_graded` |
| validation | `Validation.dimension`, `Validation.basis_tuple` | |
| conjugate, norm, inverse, exp, log, rotations | none (see [hypercomplex-algebra](hypercomplex-algebra.md) for conjugate, norm and inverse of expressions) | |
| associator, commutator | none; compose `multiply` | |
| matrix representations | none; a table row is the signed permutation `L_{e_i}` | |
| symbolic support | none; integers only | |
| dimension range | any n for `multiply`; `build_table` up to the `max_bytes` budget (n = 13 standard at the default) | |
| dtype, batching, GPU | numpy integer tables; scalar `multiply`; no GPU | |

## EXAMPLES

1. Public surface and signatures.

<!-- example -->
```python
import inspect
import hypercomplex_engine as he
print(he.__all__)
for f in (he.build_table, he.multiply, he.estimate_table_bytes, he.format_element, he.print_table):
    print(f.__name__, inspect.signature(f))
```

```text
['build_table', 'estimate_table_bytes', 'multiply', 'format_element', 'print_table', 'export_csv', 'BasisElement', 'BasisNotation', 'Validation', 'StandardTableBuilder', 'SplitTableBuilder', 'DualTableBuilder', 'StandardHolographic', 'SplitHolographic', 'DualHolographic', 'FastStandard', 'FastSplit', 'FastDual', 'CDFormat', 'CDTablePrinter']
build_table (kind: str, n: int, max_bytes: int | None = 268435456)
multiply (kind: str, a: tuple, b: tuple, dim: int | None = None, engine: str = 'fast') -> tuple
estimate_table_bytes (kind: str, n: int) -> int
format_element (element: tuple, mode: str = 'integer') -> str
print_table (table, title: str | None = None, limit: int | None = None, mode: str = 'integer')
```

2. Standard kind against `cd_core`: the full D = 16 table, and sampled products at D = 4096 from
   both engines.

<!-- example -->
```python
import random
import hypercomplex_engine as he
from cd_core import cd_sign
signs, index = he.build_table("standard", 4)
print(signs.dtype, index.dtype, signs.shape)
print("D=16 mismatches", sum(int(signs[p, q]) != cd_sign(16, p, q) or int(index[p, q]) != p ^ q
                             for p in range(16) for q in range(16)))
rng = random.Random(7)
pairs = [(rng.randrange(4096), rng.randrange(4096)) for _ in range(2000)]
for engine in ("fast", "holographic"):
    bad = sum(he.multiply("standard", (1, a), (1, b), engine=engine) != (cd_sign(4096, a, b), a ^ b)
              for a, b in pairs)
    print(engine, "D=4096 mismatches", bad)
```

```text
int8 uint8 (16, 16)
D=16 mismatches 0
fast D=4096 mismatches 0
holographic D=4096 mismatches 0
```

3. Split kind: `dim` is the exponent n of D = 2^n, and the top doubling carries the split sign.

<!-- example -->
```python
import hypercomplex_engine as he
for n in (1, 2, 3, 4):
    s, i = he.build_table("split", n)
    print("n", n, "basis squares", [int(s[k, k]) for k in range(2**n)])
print(he.multiply("split", (1, 2), (1, 2), dim=2), he.multiply("split", (1, 2), (1, 2), dim=3))
try:
    he.multiply("split", (1, 1), (1, 1))
except ValueError as e:
    print("ValueError:", e)
```

```text
n 1 basis squares [1, 1]
n 2 basis squares [1, -1, 1, 1]
n 3 basis squares [1, -1, -1, -1, 1, 1, 1, 1]
n 4 basis squares [1, -1, -1, -1, -1, -1, -1, -1, 1, 1, 1, 1, 1, 1, 1, 1]
(1, 0) (-1, 0)
ValueError: dim is required for split multiplication
```

4. Dual kind: `eps` squares to zero; tuples carry the `eps` flag; formatting modes.

<!-- example -->
```python
import hypercomplex_engine as he
print(he.multiply("dual", (1, 0, 1), (1, 0, 1), dim=0), he.multiply("dual", (1, 1, 0), (1, 1, 1), dim=1))
for mode in ("integer", "graded", "latex"):
    print(mode, he.format_element((-1, 5), mode=mode), he.format_element((1, 2, 1), mode=mode))
he.print_table(he.build_table("standard", 2), title="quaternions")
```

```text
(0, 0, 0) (-1, 0, 1)
integer -e5 +e2*eps
graded -o13 +o2*eps
latex -e_{5} +e_{2}\epsilon
quaternions
      e0  e1  e2  e3
e0 | +e0 +e1 +e2 +e3
e1 | +e1 -e0 +e3 -e2
e2 | +e2 -e3 -e0 +e1
e3 | +e3 +e2 -e1 -e0

```

5. The table memory guard.

<!-- example -->
```python
import hypercomplex_engine as he
print(he.estimate_table_bytes("standard", 13), he.estimate_table_bytes("standard", 14))
try:
    he.build_table("standard", 14)
except ValueError as e:
    print("ValueError:", str(e)[:80])
```

```text
201326592 805306368
ValueError: build_table('standard', 14) needs about 768.0 MiB (limit 256.0 MiB). Pass a larg
```

## MAPPING TO cd_core

- `standard`: identity. `multiply("standard", (1, a), (1, b)) == (cd_core.cd_sign(D, a, b), a ^ b)`
  for every D at least the larger index needs (EXAMPLES 2; exhaustive D = 2 to 32 in
  [checks/interplay_tables.json](checks/interplay_tables.json); 6,000 sampled products per
  D from 32 to 4096 in `docs/evidence/algebra_packages/tables.json`).
- `split` with exponent n: identical to the split reference
  `s(p, q) = cd_sign(D, p, q) * (-1 if p, q >= D/2 else 1)` for n = 1 to 4, which is the
  split-complex numbers (n = 1), split-quaternions (n = 2), split-octonions (n = 3) and a split
  sedenion algebra (n = 4) (checks). Its e_0 ... e_{D/2-1} block is the ordinary algebra.
- `dual` with n = 0 is the dual numbers `R[eps]`; it equals Cl(0,0,1) from
  [clifford](clifford.md) and [kingdon](kingdon.md) (checks).

## TRAPS

- `dim` in `multiply` is the exponent n, not the dimension D: `multiply("split", (1, 2), (1, 2), dim=2)`
  is the split-quaternion square `+1` and `dim=3` gives `-1` (EXAMPLES 3).
- The split kind splits only the top doubling, so its basis squares depend on n; the
  ordinary algebra of dimension D/2 sits inside it.
- `multiply` takes and returns basis tuples; linear extension is the caller's job.
- `build_table("standard", 14)` exceeds the default 256 MiB budget and raises `ValueError`;
  pass `max_bytes` or use `multiply` (EXAMPLES 5).
- Agreement with [hypercomplex-algebra](hypercomplex-algebra.md) is not independent
  evidence: that package resolves every basis product through this engine.

## LICENSE

Apache-2.0 (dist-info `License-Expression`).

## SEE ALSO

[hypercomplex-algebra](hypercomplex-algebra.md), [splitoct](splitoct.md), [interplay](../interplay.md).
