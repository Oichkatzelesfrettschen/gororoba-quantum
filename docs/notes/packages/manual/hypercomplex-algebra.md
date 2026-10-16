# hypercomplex-algebra(3) -- string expressions over hypercomplex-engine

## NAME

`hypercomplex_algebra` 0.2.0.2 (PyPI `hypercomplex-algebra`, Arch `python-hypercomplex-algebra`):
parses sums of signed basis terms, multiplies them through
[hypercomplex-engine](hypercomplex-engine.md), and formats the result. Release binding:
[../hypercomplex-algebra.md](../hypercomplex-algebra.md).

## SYNOPSIS

```python
import hypercomplex_algebra as ha

ha.multiply_expressions("3e1 + 2e2", "e1 - e2")              # standard algebra, any index
ha.multiply_many_expressions(["e1", "e2", "e4"])             # ((e1 e2) e4)
ha.multiply_split_expressions("e2", "e2", 2)                 # split, exponent n = 2
ha.multiply_dual_expressions("e1 + eps", "e1 - eps")         # dual numbers over the standard algebra
ha.multiply_tensor_expressions("e[1,2]", "e[1,2]", ["standard", "standard"])
m = ha.ExpressionMultiplier(kind="standard")
m.conjugate("e1 + e10"), m.norm("e1 + e10"), m.inverse("e1 + e10")
```

## DESCRIPTION

Expressions are strings of integer or decimal coefficients times basis labels `e<k>`
(`1` and `e0` are the identity; `eps` is the dual unit; `e[i,j,...]` is a tensor-slot label).
`ExpressionMultiplier(kind, dim=None, slots=None, resolver=None)` holds a parser, a formatter
and a sparse multiplier; its resolver adapters (`StandardResolver`, `SplitResolver`,
`DualStandardResolver`, `DualSplitResolver`) call the engine's `FastStandard`, `FastSplit`
and `FastDual` for every basis product (the installed package's `adapters/` modules).

## API SURFACE

Enumerated in EXAMPLES 1.

| Capability | API | Behavior |
|---|---|---|
| construction | expression strings; `ElementParser`, `DualElementParser`, `TensorElementParser`; formatters of the same names | |
| products | `multiply_expressions`, `multiply_many_expressions` and the `split`, `dual`, `dual_split` and `tensor` variants; `ExpressionMultiplier.multiply`, `.multiply_many` | `multiply_many` folds from the left |
| conjugate, norm, inverse | `ExpressionMultiplier.conjugate(expr, mode="hypercomplex")`, `.norm(expr, mode=...)`, `.inverse(expr, mode=...)` | `norm` is `x x*`; dual modes `hypercomplex`, `dual`, `total` |
| resolvers | `create_resolver(kind, dim)`, `create_tensor_resolver(slots)`, `BasisProductResolver`, `SparseMultiplier`, `DualResolver`, `DualSparseMultiplier`, `TensorResolver`, `TensorSparseMultiplier` | |
| exp, log, rotations, matrices | none | |
| symbolic support | none; decimal coefficients only (`0.5e1` parses, `1/2e1` raises `ValueError`, EXAMPLES 5) | |
| dimension range | any index for `standard` and `dual`; fixed exponent for `split` | |
| dtype, batching, GPU | strings and Python numbers only | |

## EXAMPLES

1. Public surface.

<!-- example -->
```python
import inspect
import hypercomplex_algebra as ha
print(ha.__all__)
print(inspect.signature(ha.ExpressionMultiplier))
print([n for n in dir(ha.ExpressionMultiplier) if not n.startswith("_")])
```

```text
['BasisProductResolver', 'SparseMultiplier', 'DualResolver', 'DualSparseMultiplier', 'TensorResolver', 'TensorSparseMultiplier', 'StandardResolver', 'SplitResolver', 'DualStandardResolver', 'DualSplitResolver', 'create_resolver', 'create_tensor_resolver', 'ElementParser', 'ElementFormatter', 'DualElementParser', 'DualElementFormatter', 'TensorElementParser', 'TensorElementFormatter', 'ExpressionMultiplier', 'multiply_expressions', 'multiply_many_expressions', 'multiply_split_expressions', 'multiply_many_split_expressions', 'multiply_dual_expressions', 'multiply_many_dual_expressions', 'multiply_dual_split_expressions', 'multiply_many_dual_split_expressions', 'multiply_tensor_expressions', 'multiply_many_tensor_expressions']
(kind: str = 'standard', dim: int | None = None, slots=None, resolver=None)
['conjugate', 'inverse', 'kind', 'multiply', 'multiply_many', 'norm']
```

2. Products against `cd_core.cd_multiply`, and the engine call behind each basis product.

<!-- example -->
```python
import hypercomplex_algebra as ha
import hypercomplex_engine as he
from cd_core import cd_multiply
print(ha.multiply_expressions("e5", "e6"), ha.multiply_expressions("3e1 + 2e2", "e1 - e2"))
a = [0, 3, 2, 0, 0, 0, 0, 0]
b = [0, 1, -1, 0, 0, 0, 0, 0]
print(cd_multiply(8, [float(v) for v in a], [float(v) for v in b]))
calls = []
original = he.FastStandard.multiply_indices
he.FastStandard.multiply_indices = lambda self, i, j: calls.append((i, j)) or original(self, i, j)
ha.ExpressionMultiplier(kind="standard").multiply("e1 + e2", "e3 - e4")
print("engine calls", calls)
```

```text
-e3 -1 - 5e3
[-1.0, 0.0, 0.0, -5.0, 0.0, 0.0, 0.0, 0.0]
engine calls [(1, 3), (1, 4), (2, 3), (2, 4)]
```

3. The left fold is a bracketing choice in a nonassociative algebra.

<!-- example -->
```python
import hypercomplex_algebra as ha
left = ha.multiply_many_expressions(["e1", "e2", "e4"])
right = ha.multiply_expressions("e1", ha.multiply_expressions("e2", "e4"))
print("((e1 e2) e4) =", left, "  e1 (e2 e4) =", right)
```

```text
((e1 e2) e4) = e7   e1 (e2 e4) = -e7
```

4. Conjugate, norm and inverse of the sedenion zero divisor `e1 + e10`, and its zero product.

<!-- example -->
```python
import hypercomplex_algebra as ha
m = ha.ExpressionMultiplier(kind="standard")
print(m.conjugate("e1 + e10"), "|", m.norm("e1 + e10"), "|", m.inverse("e1 + e10"))
print(ha.multiply_expressions("e1 + e10", "e4 - e15"))
```

```text
-e1 - e10 | 2 | -0.5e1 - 0.5e10
0
```

5. Split, dual and tensor algebras.

<!-- example -->
```python
import hypercomplex_algebra as ha
print([ha.multiply_split_expressions(f"e{k}", f"e{k}", 2) for k in range(4)])
print(ha.multiply_dual_expressions("eps", "eps"), "|", ha.multiply_dual_expressions("e1 + eps", "e1 - eps"))
print(ha.multiply_tensor_expressions("e[1,2]", "e[1,2]", ["standard", "standard"]),
      ha.multiply_tensor_expressions("e[1,0]", "e[2,0]", ["standard", "standard"]))
for text in ("0.5e1", "1/2e1"):
    try:
        print(text, "->", ha.multiply_expressions(text, "e1"))
    except ValueError as e:
        print(text, "-> ValueError:", e)
try:
    ha.multiply_split_expressions("e5", "e1", 2)
except ValueError as e:
    print("ValueError:", e)
```

```text
['1', '-1', '1', '1']
0 | -1
1 e[3,0]
0.5e1 -> -0.5
1/2e1 -> ValueError: could not convert string to float: '1/2'
ValueError: Index out of range for split dim=2 (valid: 0..3). Split dimensions cannot be mixed. Create a new SplitResolver with the dimension you need.
```

## MAPPING TO cd_core

Identity for the standard kind: `multiply_expressions("e<a>", "e<b>")` is
`cd_sign(D, a, b) e_{a xor b}` (EXAMPLES 2; the full D = 8 table and the split exponent-2
table in [checks/interplay_tables.json](checks/interplay_tables.json); 200 seeded products
below 64 in `docs/evidence/algebra_packages/tables.json`). The split, dual and tensor kinds
inherit the engine's maps.

## TRAPS

- Not an independent witness: every basis product is an engine call (EXAMPLES 2), so
  agreement with the engine tests only the parser and formatter.
- `multiply_many_*` folds from the left; state the bracketing (EXAMPLES 3).
- `inverse` returns `x* / N(x)` for zero divisors as well (EXAMPLES 4).
- A split multiplier is pinned to one exponent and rejects larger indices (EXAMPLES 5).
- Coefficients parse as floats: fractions such as `1/2e1` raise `ValueError` (EXAMPLES 5).
- Tensor products multiply slot by slot with the signs multiplied; the result is not a
  Cayley-Dickson level.

## LICENSE

Apache-2.0 (dist-info `License-Expression`).

## SEE ALSO

[hypercomplex-engine](hypercomplex-engine.md), [interplay](../interplay.md).
