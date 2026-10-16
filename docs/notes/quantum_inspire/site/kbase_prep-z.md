> Full piece: [https://www.quantum-inspire.com/kbase/prep-z/](https://www.quantum-inspire.com/kbase/prep-z/)
> Retrieved 2026-10-16T22:24Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 331fbb464082cd2d7e20322cb535cec45c7cf3c9e5071d53730a76f1e3841352.

# Prep_z

By default, all qubits are initialized in the $`|0\rangle`$ state. With the `prep_z` instruction, qubits will be explicitly initialized in the $`|0\rangle`$ state of the z-basis, i.e. in the same state as the default.

State initialization can be done at the beginning of an algorithm, but it can also be done during an algorithm (re-initialization). Be aware that re-initialization of a qubit will also reset the binary register entry for that qubit to zero.

The instructions `prep_x` and `prep_y` can be used to initialize qubits in other sets of [basis states](https://www.quantum-inspire.com/kbase/qubit-basis-states/).

![Bloch sphere courtesy of http://www.laborsciencenetwork.com](https://www.datocms-assets.com/119587/1534934969-blochspphere.jpg)

Bloch sphere courtesy of http://www.laborsciencenetwork.com
