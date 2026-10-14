# octonion 0.1.0 (PyTorch)

- Release: [PyPI octonion 0.1.0](https://pypi.org/project/octonion/0.1.0/), sdist sha256 `01788b55497dd6be79411aa03ba17762211e73dafbd014b5f54e66934c98bfcc`; source [realnedsanders/octonion](https://github.com/realnedsanders/octonion); AGPL-3.0-or-later.
- Module: `octonion`; requires PyTorch.

## What it implements

PyTorch tensors for real, complex, quaternion and octonion arithmetic
(`octonion_mul`, `associator`, `left_mul_matrix`, `right_mul_matrix`,
`octonion_exp`, `octonion_log`), the `FANO_PLANE`, and `STRUCTURE_CONSTANTS`
of shape (8, 8, 8); the project uses them for an octonionic trie classifier.

## Relation to cd_core

The structure constants use a Fano labeling (`e1 e2 = e4`), not the XOR
indexing of `cd_core`. The signed relabeling
`pi = (0, 1, 2, 4, 3, 6, 7, 5)` with one sign flip on its `e6` carries every
product onto `cd_core`, verified on all 64 basis pairs; the algebras are
isomorphic and the basis numbering differs.

## Correct use

- Batched floating-point octonion arithmetic on tensors when a workflow is
  already in PyTorch, after mapping indices through `pi` and `eta`.
- Octonions only; there is no sedenion or higher level.

## Pitfalls

- Index `i` here is not `e_i` of `cd_core`; translate through the map before
  comparing any coefficient, associator or Fano line.
- It owns the top-level module name `octonion`, which shadows
  [Cayley-Calculator](cayley-calculator.md)'s `octonion` module.
- AGPL terms attach to code that incorporates it; repository code does not
  import it in CI.
