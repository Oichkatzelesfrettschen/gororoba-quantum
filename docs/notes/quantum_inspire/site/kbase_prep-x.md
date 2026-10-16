> Full piece: [https://www.quantum-inspire.com/kbase/prep-x/](https://www.quantum-inspire.com/kbase/prep-x/)
> Retrieved 2026-10-16T22:10Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 75b4bf1c542b555c846a748d56784c687698300ff013711888d89a49743be555.

# Prep_x

By default, all qubits are initialized in the $`|0\rangle`$ state. With the `prep_x` instruction, qubits will be [initialized in the x-basis](https://www.quantum-inspire.com/kbase/qubit-basis-states/) in the $`|+\rangle =\frac{\vert 0 \rangle + \vert 1 \rangle}{\sqrt{2}}`$ state:

State initialization can be done at the beginning of an algorithm, but it can also be done during an algorithm (re-initialization). Be aware that re-initialization of a qubit will also reset the binary register entry for that qubit to zero.

![Bloch sphere courtesy of http://www.laborsciencenetwork.com](https://www.datocms-assets.com/119587/1534934969-blochspphere.jpg)

Bloch sphere courtesy of http://www.laborsciencenetwork.com
