# SageMath 10.10 octonions

- Release: SageMath 10.10 (release date 2026-09-28), installed as the CachyOS
  package `sagemath 10.10-2.1` from [sagemath.org](https://www.sagemath.org);
  GPL-2.0-or-later.
- Module: `OctonionAlgebra(QQ)` in the Sage library; exact rational coefficients.

## What it implements

Sage's octonion algebra over any ring, with basis `1, i, j, k, l, li, lj, lk`,
exact arithmetic, and the surrounding quadratic-form and `G_2` machinery of
the Sage library.

## Relation to cd_core

In its natural basis order, mapped to `e0` through `e7`, Sage's octonion
algebra is the opposite of `cd_core` at D = 8: `e_a *_Sage e_b = e_b *_cd e_a`
on all 64 basis pairs, with no sign change. Flipping the signs of `e3`, `e5`
and `e6` is an isomorphism onto `cd_core`. Each relation is realized by 1344
signed relabelings, the signed-permutation automorphisms of the octonion
basis. Code ported from Sage therefore reverses every product unless it maps
through the sign flip.

[scripts/algebra_circuit_fixtures.py](../../../scripts/algebra_circuit_fixtures.py)
checks both relations and both counts from the retained export
[sagemath_octonion_table.json](../../evidence/algebra_packages/sagemath_octonion_table.json)
(SHA-256 `7453cb4738a2a741d57b9c3b9bd75d40416abde3935e73fab23fa5a9d0fead33`), written by
[sagemath_octonion_table.sage](../../evidence/algebra_packages/sagemath_octonion_table.sage)
(SHA-256 `af0d9ba729a0ba6826a1ae676b3875a3206c05a1ef51d9f710b94f2975e1f6a8`); the CI gate needs no Sage installation.

## Correct use

- An independent exact octonion reference for identities that cd_core
  checks in integers, after the sign flip on `e3`, `e5`, `e6`.
- Octonions only in this note; higher Cayley-Dickson levels are not part of
  the measured relation.
