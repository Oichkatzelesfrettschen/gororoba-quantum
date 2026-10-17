> Full piece: [https://www.quantum-inspire.com/kbase/prep-x/](https://www.quantum-inspire.com/kbase/prep-x/)
> Retrieved 2026-10-16T22:24Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 4c00a5c28e6170d7d9c733db41288791a40f10bfa67be0619d16d21f626ed687.

# Prep_x

By default, all qubits are initialized in the $`|0\rangle`$ state. With the `prep_x` instruction, qubits will be [initialized in the x-basis](https://www.quantum-inspire.com/kbase/qubit-basis-states/) in the $`|+\rangle =\frac{\vert 0 \rangle + \vert 1 \rangle}{\sqrt{2}}`$ state:

State initialization can be done at the beginning of an algorithm, but it can also be done during an algorithm (re-initialization). Be aware that re-initialization of a qubit will also reset the binary register entry for that qubit to zero.

![Bloch sphere courtesy of http://www.laborsciencenetwork.com](https://www.datocms-assets.com/119587/1534934969-blochspphere.jpg)

Bloch sphere courtesy of http://www.laborsciencenetwork.com
