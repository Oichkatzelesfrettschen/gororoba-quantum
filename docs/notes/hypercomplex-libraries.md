** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
# Hypercomplex and Clifford libraries: which one to import

[packages/README.md](packages/README.md) holds each package's measured relation to `gororoba_quantum/cd_core.py`, and [packages/interplay.md](packages/interplay.md) holds the maps. This note selects: for a dimension and a purpose it names the library, its measured speed, its hosts and its role. The speeds come from one audit (a single run per library on the compute workstation, 2026-11-28, a loop of 10^5 products); they rank libraries and carry no tolerance.

## The rule

A package result enters evidence only through a declared map onto `cd_core`, checked on every basis pair ([AGENTS.md](../../AGENTS.md#grounding-and-algebra)). Every row below that reads "identity" holds that map: the audit found 0 mismatching pairs, and [test_hypercomplex_library_maps.py](../../tests/gororoba_quantum/test_hypercomplex_library_maps.py) rechecks it on every pair wherever the package imports and skips with the import name where it does not. Agreement between two packages is no evidence unless they are independent ([packages/README.md](packages/README.md#rules)).

## Audit table

| Library | Dimensions | Map onto `cd_core` | Speed, 10^5 products | Hosts | Role |
| --- | --- | --- | --- | --- | --- |
| [hypercomplex-engine](packages/hypercomplex-engine.md) `build_table("standard", n)` | 4 to 32 audited; the test covers 4 to 64 | identity | 1.6 s | build host; not in `gq-max` | evidence through the identity map; first choice for a sign or a full table at any dimension |
| [Octonion-Sedenion](packages/octonion-sedenion.md) | 8 and 16 | identity | 0.05 s (D = 8), 0.35 s (D = 16) | build host; not in `gq-max` | evidence through the identity map; fastest for float coefficients at D = 8 and 16; its sedenion module needs the import binding in [octonion-sedenion.md](packages/octonion-sedenion.md) |
| [pyoctonion](packages/pyoctonion.md) | 8 | identity | 2.9 s | build host; not in `gq-max` | evidence through the identity map; slow |
| [numpy-quaternion](packages/numpy-quaternion.md) | 4 | identity | 0.01 s | both | evidence through the identity map; first choice at D = 4 |
| [pyquaternion](packages/pyquaternion.md) | 4 | identity | 0.34 s | both | evidence through the identity map |
| [quaternionic](packages/quaternionic.md) | 4 | identity | 0.41 s | both | evidence through the identity map |
| [hypercomplex](packages/hypercomplex.md) `cayley_dickson_algebra(n)` | 4 to 32 | identity | 48 s | both | cross-check; exact `Fraction` coefficients ([packages/README.md](packages/README.md#rules), rule 5) |
| [hypercomplex-algebra](packages/hypercomplex-algebra.md) | below 64 | identity | cached | build host | cross-check only; it wraps the engine and caches, so its throughput says nothing |
| [cayley-dickson](packages/cayley-dickson.md) | 8 and 16 | identity | cached | build host | cross-check only; it caches |
| [splitoct](packages/splitoct.md) | 8 | none: split octonions (e4 to e7 square to +1) | not measured | build host | incompatible; a negative control only |
| [Cayley-Calculator](packages/cayley-calculator.md) | 16 | identity in the retained table | not measured | build host | open: the audit's PyPI install fails on import (missing `gamma_mod`), while the digest-bound table read from the pinned build equals `cd_core`; read the import there before a new use |
| [octonion](packages/octonion.md) | 8 | signed relabeling (`pi`, `eta` in [packages/README.md](packages/README.md)) | not measured | build host | needs torch to import; usable only on an interpreter that holds it |
| [clifford](packages/clifford.md), [kingdon](packages/kingdon.md), [galgebra](packages/galgebra.md) | Cl(0,2) = D = 4 | identity | not measured | both | geometric algebra: rotors, spinors, versors. Every Clifford product is associative, so none carries the octonion or sedenion product; cross-check only |

The "both" hosts are the build host's Arch packages and `gq-max` ([gq-max.lock.txt](gq-max.lock.txt)). A Kaggle kernel rebuilds the hypercomplex stack from pinned archives ([kaggle/hypercomplex-stack.md](kaggle/hypercomplex-stack.md)).

## Choose by dimension and purpose

- D = 4 products: numpy-quaternion.
- D = 8 or 16 floating-point products: Octonion-Sedenion.
- Signs and tables from D = 32 to 4096: hypercomplex-engine; the fast and holographic evaluators agree on 6000 sampled products per dimension in [tables.json](../evidence/algebra_packages/tables.json).
- Exact rational products and inverses: hypercomplex with `base=fractions.Fraction`.
- Kernel and rank statements: `cd_core.left_mult_matrix`; a package `inverse()` is no invertible operator ([packages/README.md](packages/README.md#rules), rule 4).
- Spin(7), G2 actions and Clifford realizations of triality: clifford, kingdon or galgebra as an associative cross-check of the action; the octonion product itself stays on `cd_core`.

## Broken, incompatible and misleading

- splitoct and the engine's split kind square three of seven imaginary units to -1 and four to +1 yet carry the ordinary associator signs; check basis squares, not only associators.
- Caching packages report a throughput of the cache.
- Importing octonion needs torch.
- A Clifford package cannot be extended to the octonions, since the algebra is associative.

The generalized procedure for qualifying a library is in the skill `write-exact-research-python` (`references/hypercomplex.md`).
