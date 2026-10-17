> Full piece: [https://www.quantum-inspire.com/kbase/prep-y/](https://www.quantum-inspire.com/kbase/prep-y/)
> Retrieved 2026-10-16T22:24Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 db3e10cab505a48a5c1790137357eb7f07ff6c05449e7352c15c2ca71956f59e.

# Prep_y

By default, all qubits are initialized in the $`|0 \rangle`$ state. With the `prep_y` instruction, qubits will be [initialized in the y-basis](https://www.quantum-inspire.com/kbase/qubit-basis-states/) in the $`\vert R\rangle =\frac{\vert 0 \rangle + \imath \vert 1 \rangle}{\sqrt{2}}`$ state:

State initialization can be done at the beginning of an algorithm, but it can also be done during an algorithm (re-initialization). Be aware that re-initialization of a qubit will also reset the binary register entry for that qubit to zero.

![Bloch sphere courtesy of http://www.laborsciencenetwork.com](https://www.datocms-assets.com/119587/1534934969-blochspphere.jpg)

Bloch sphere courtesy of http://www.laborsciencenetwork.com
