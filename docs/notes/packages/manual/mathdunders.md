# mathdunders(3) -- class decorator that keeps arithmetic closed over a numeric subclass

## NAME

`mathdunders` 0.4.2 (PyPI `mathdunders`, Arch `python-mathdunders`): one decorator that
adds arithmetic dunder methods returning the decorated subclass. It computes no algebra
product. Release binding: [../mathdunders.md](../mathdunders.md).

## SYNOPSIS

```python
from mathdunders import mathdunders

@mathdunders()                 # base defaults to the first base class
class Real(float):
    pass

type(Real(2) + 3) is Real
```

## DESCRIPTION

For each name in `mathdunders.dunders` (7 unary and 16 binary methods), the decorator sets
a method that converts `self` to `base`, calls the base method, and wraps the result in the
decorated class (tuples element-wise for `divmod`); a method the class already defines
stays unless `force=True` (the installed `mathdunders/mathdunders.py`).

## API SURFACE

| Capability | API | Behavior |
|---|---|---|
| decorator | `mathdunders(base=None, dunders=dunders, force=False)` | |
| method list | `dunders` in the submodule `mathdunders.mathdunders` (the package name `mathdunders.mathdunders` resolves to the function) | 23 names |
| algebra capabilities | none | |

## EXAMPLES

1. Signature, method list, and its single use in [hypercomplex](hypercomplex.md): only the
   level-0 `Real` class carries generated methods.

<!-- example -->
```python
import importlib, inspect
module = importlib.import_module("mathdunders.mathdunders")
print(inspect.signature(module.mathdunders), len(module.dunders), module.dunders[:7])
import hypercomplex
def generated(cls):
    return sorted(n for n, v in vars(cls).items() if getattr(v, "__qualname__", "").endswith("make_dunder.<locals>.dunder"))
print("Real", len(generated(hypercomplex.R)), "Complex", generated(hypercomplex.C), "Octonion", generated(hypercomplex.O))
r = hypercomplex.R(2) + 3
print(type(r).__name__, r, type(divmod(hypercomplex.R(7), 2)[0]).__name__)
```

```text
(base=None, dunders=('__abs__', '__ceil__', '__floor__', '__neg__', '__pos__', '__round__', '__trunc__', '__add__', '__divmod__', '__floordiv__', '__mod__', '__mul__', '__pow__', '__sub__', '__truediv__', '__radd__', '__rdivmod__', '__rfloordiv__', '__rmod__', '__rmul__', '__rpow__', '__rsub__', '__rtruediv__'), force=False) 23 ('__abs__', '__ceil__', '__floor__', '__neg__', '__pos__', '__round__', '__trunc__')
Real 22 Complex [] Octonion []
Real (5) Real
```

## MAPPING TO cd_core

None. Its output carries no multiplication table and enters no evidence.

## TRAPS

- `__abs__` is in the list, but `hypercomplex`'s `Numeric.__abs__` already defines it, so
  the decorated `Real` keeps 22 generated methods (EXAMPLES 1).

## LICENSE

MIT (dist-info `License: MIT`).

## SEE ALSO

[hypercomplex](hypercomplex.md), [interplay](../interplay.md).
