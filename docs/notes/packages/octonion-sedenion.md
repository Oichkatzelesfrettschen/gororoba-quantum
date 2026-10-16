# Octonion-Sedenion 1.0.0

- Release: [PyPI Octonion-Sedenion 1.0.0](https://pypi.org/project/Octonion-Sedenion/1.0.0/), published only as the wheel `octonion_sedenion-1.0.0-py3-none-any.whl`, sha256 `365374433649809b50c542b28cc60ec8433cfdd61d19b90c233ec631bb5cf00e`; no license file or license metadata, and its project URLs point at a packaging template (github.com/pypa/Octonion_Sedenion).
- Module: `Octonion_Sedenion` (submodules `complex`, `octonion`, `sedenion`); depends on numpy-quaternion. Arch package python-octonion-sedenion (local PKGBUILD installing the wheel).

## What it implements

`Octonion` built from two numpy-quaternion halves and `Sedenion` from two
octonions, with conjugate, norm, exp, log and trigonometric functions, plus
small associativity, Moufang and zero-divisor test scripts.

## Relation to cd_core

`Octonion_Sedenion.octonion` (D = 8) and `Octonion_Sedenion.sedenion`
(D = 16) are identical to `cd_core` on every basis pair.

## Correct use

- A fourth independent sedenion table beside hypercomplex, Cayley-Calculator
  and cayley-dickson, read through the import below.

## Pitfalls

- `Octonion_Sedenion/sedenion.py` runs `from octonion import Octonion`, an
  absolute import that resolves to python-octonion's top-level `octonion`
  module; as installed, importing it raises
  `AttributeError: 'int' object has no attribute 'shape'`.
  `scripts/algebra_package_tables.py` binds `sys.modules["octonion"]` to
  `Octonion_Sedenion.octonion` for that import and restores it, and retains
  the as-installed failure in `import_note`.
- `components` is an attribute holding the coefficient array, not a method.
- No license accompanies the code: read and cross-check only, vendor nothing.
