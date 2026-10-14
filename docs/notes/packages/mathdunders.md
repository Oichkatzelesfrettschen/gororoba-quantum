# mathdunders 0.4.2

- Release: [PyPI mathdunders 0.4.2](https://pypi.org/project/mathdunders/0.4.2/), sdist sha256 `ff9b624725fafd34c51decbe3e661eb91b79bbd3841ab04d2256704df0845ce5`; source [discretegames/mathdunders](https://github.com/discretegames/mathdunders); MIT.
- Module: `mathdunders`.

## What it implements

The class decorator `@mathdunders(base=None, force=False, dunders=...)` adds
23 arithmetic dunder methods so that operations on a subclass of a numeric
type return that subclass.

## Relation to cd_core

None. It computes no algebra products; [hypercomplex](hypercomplex.md) uses
it to keep its `reals(base)` class closed under arithmetic.

## Correct use

Infrastructure only. It contributes no evidence to any multiplication,
census or proof check.
