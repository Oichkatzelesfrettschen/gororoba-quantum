> Full piece: [https://docs.openquantum.com/pennylane-plugin/examples/basic-circuits/](https://docs.openquantum.com/pennylane-plugin/examples/basic-circuits/)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 9f9e5751d3c84008150c99a59818c1de3b63b4db12e45404968a48a529e61de2.

# Basic Circuits

This page demonstrates common circuit patterns using the Open Quantum PennyLane plugin.

Note

All examples assume you have set the `OPENQUANTUM_CLIENT_ID`, `OPENQUANTUM_CLIENT_SECRET`, and `OPENQUANTUM_ORGANIZATION_ID` environment variables. See [Authentication](https://docs.openquantum.com/core-sdk/authentication/) for details.

## Bell State with Counts

Create a maximally entangled two-qubit state and measure bitstring counts:

[](#__codelineno-0-1)`import`` ``pennylane`` ``as`` ``qml`\
[](#__codelineno-0-2)\
[](#__codelineno-0-3)`dev`` ``=`` ``qml``.``device``(``"openquantum.device"``,`` ``wires``=``2``,`` ``shots``=``128``,`` ``backend``=``"rigetti:cepheus-1-108q"``)`\
[](#__codelineno-0-4)\
[](#__codelineno-0-5)`@qml``.``qnode``(``dev``)`\
[](#__codelineno-0-6)`def`` ``bell_state``():`\
[](#__codelineno-0-7)`    ``qml``.``Hadamard``(``wires``=``0``)`\
[](#__codelineno-0-8)`    ``qml``.``CNOT``(``wires``=``[``0``,`` ``1``])`\
[](#__codelineno-0-9)`    ``return`` ``qml``.``counts``()`\
[](#__codelineno-0-10)\
[](#__codelineno-0-11)`result`` ``=`` ``bell_state``()`\
[](#__codelineno-0-12)`print``(``result``)`\

Expected output:

[](#__codelineno-1-1)`{``'00'``:`` ``507``,`` ``'11'``:`` ``517``}`\

The Bell state \\\|\Phi^+\rangle = \frac{1}{\sqrt{2}}(\|00\rangle + \|11\rangle)\\ produces only the bitstrings `00` and `11`, each with approximately 50% probability.

## GHZ State with Probabilities

Create a 3-qubit GHZ state and measure the probability distribution:

[](#__codelineno-2-1)`import`` ``pennylane`` ``as`` ``qml`\
[](#__codelineno-2-2)\
[](#__codelineno-2-3)`dev`` ``=`` ``qml``.``device``(``"openquantum.device"``,`` ``wires``=``3``,`` ``shots``=``4096``,`` ``backend``=``"rigetti:cepheus-1-108q"``)`\
[](#__codelineno-2-4)\
[](#__codelineno-2-5)`@qml``.``qnode``(``dev``)`\
[](#__codelineno-2-6)`def`` ``ghz_state``():`\
[](#__codelineno-2-7)`    ``qml``.``Hadamard``(``wires``=``0``)`\
[](#__codelineno-2-8)`    ``qml``.``CNOT``(``wires``=``[``0``,`` ``1``])`\
[](#__codelineno-2-9)`    ``qml``.``CNOT``(``wires``=``[``1``,`` ``2``])`\
[](#__codelineno-2-10)`    ``return`` ``qml``.``probs``(``wires``=``[``0``,`` ``1``,`` ``2``])`\
[](#__codelineno-2-11)\
[](#__codelineno-2-12)`probs`` ``=`` ``ghz_state``()`\
[](#__codelineno-2-13)`print``(``probs``)`\

Expected output:

[](#__codelineno-3-1)`[``0.502``,`` ``0.0``,`` ``0.0``,`` ``0.0``,`` ``0.0``,`` ``0.0``,`` ``0.0``,`` ``0.498``]`\

The GHZ state \\\frac{1}{\sqrt{2}}(\|000\rangle + \|111\rangle)\\ has non-zero probabilities only at indices 0 (`000`) and 7 (`111`).

## Parameterized Rotation Circuit with Expectation Value

Use parameterized gates and measure an observable's expectation value:

[](#__codelineno-4-1)`import`` ``pennylane`` ``as`` ``qml`\
[](#__codelineno-4-2)`import`` ``numpy`` ``as`` ``np`\
[](#__codelineno-4-3)\
[](#__codelineno-4-4)`dev`` ``=`` ``qml``.``device``(``"openquantum.device"``,`` ``wires``=``1``,`` ``shots``=``4096``,`` ``backend``=``"rigetti:cepheus-1-108q"``)`\
[](#__codelineno-4-5)\
[](#__codelineno-4-6)`@qml``.``qnode``(``dev``)`\
[](#__codelineno-4-7)`def`` ``rotation_circuit``(``angle``):`\
[](#__codelineno-4-8)`    ``qml``.``RX``(``angle``,`` ``wires``=``0``)`\
[](#__codelineno-4-9)`    ``return`` ``qml``.``expval``(``qml``.``PauliZ``(``0``))`\
[](#__codelineno-4-10)\
[](#__codelineno-4-11)`# Sweep over angles from 0 to 2*pi`\
[](#__codelineno-4-12)`angles`` ``=`` ``np``.``linspace``(``0``,`` ``2`` ``*`` ``np``.``pi``,`` ``8``)`\
[](#__codelineno-4-13)`for`` ``angle`` ``in`` ``angles``:`\
[](#__codelineno-4-14)`    ``result`` ``=`` ``rotation_circuit``(``angle``)`\
[](#__codelineno-4-15)`    ``print``(``f``"RX(``{``angle``:``.2f``}``): <Z> = ``{``result``:``.4f``}``"``)`\

Expected output:

[](#__codelineno-5-1)`RX(0.00): <Z> = 1.0000`\
[](#__codelineno-5-2)`RX(0.90): <Z> = 0.6235`\
[](#__codelineno-5-3)`RX(1.80): <Z> = -0.2272`\
[](#__codelineno-5-4)`RX(2.69): <Z> = -0.9010`\
[](#__codelineno-5-5)`RX(3.59): <Z> = -0.9010`\
[](#__codelineno-5-6)`RX(4.49): <Z> = -0.2272`\
[](#__codelineno-5-7)`RX(5.39): <Z> = 0.6235`\
[](#__codelineno-5-8)`RX(6.28): <Z> = 1.0000`\

The expectation value of \\\langle Z \rangle\\ after an \\R_X(\theta)\\ rotation follows \\\cos(\theta)\\.

Tip

Using more shots (e.g., 4096 instead of 1024) reduces statistical noise in expectation value estimates.

## Multiple Measurements in One Circuit

Return multiple measurement types from a single circuit execution:

[](#__codelineno-6-1)`import`` ``pennylane`` ``as`` ``qml`\
[](#__codelineno-6-2)\
[](#__codelineno-6-3)`dev`` ``=`` ``qml``.``device``(``"openquantum.device"``,`` ``wires``=``2``,`` ``shots``=``2048``,`` ``backend``=``"rigetti:cepheus-1-108q"``)`\
[](#__codelineno-6-4)\
[](#__codelineno-6-5)`@qml``.``qnode``(``dev``)`\
[](#__codelineno-6-6)`def`` ``multi_measurement``():`\
[](#__codelineno-6-7)`    ``qml``.``Hadamard``(``wires``=``0``)`\
[](#__codelineno-6-8)`    ``qml``.``CNOT``(``wires``=``[``0``,`` ``1``])`\
[](#__codelineno-6-9)`    ``return`` ``(`\
[](#__codelineno-6-10)`        ``qml``.``expval``(``qml``.``PauliZ``(``0``)),`\
[](#__codelineno-6-11)`        ``qml``.``expval``(``qml``.``PauliZ``(``1``)),`\
[](#__codelineno-6-12)`        ``qml``.``probs``(``wires``=``[``0``,`` ``1``]),`\
[](#__codelineno-6-13)`    ``)`\
[](#__codelineno-6-14)\
[](#__codelineno-6-15)`z0``,`` ``z1``,`` ``probs`` ``=`` ``multi_measurement``()`\
[](#__codelineno-6-16)`print``(``f``"<Z0> = ``{``z0``:``.4f``}``"``)`\
[](#__codelineno-6-17)`print``(``f``"<Z1> = ``{``z1``:``.4f``}``"``)`\
[](#__codelineno-6-18)`print``(``f``"P(00, 01, 10, 11) = ``{``probs``}``"``)`\

Expected output:

[](#__codelineno-7-1)`<Z0> = 0.0039`\
[](#__codelineno-7-2)`<Z1> = -0.0059`\
[](#__codelineno-7-3)`P(00, 01, 10, 11) = [0.499 0.001 0.003 0.497]`\

Note

All measurement results in a single QNode call are computed from the same set of shots. PennyLane handles the post-processing to extract each measurement from the raw counts.

## Tensor Product Observables

Measure correlations between qubits using tensor product observables:

[](#__codelineno-8-1)`import`` ``pennylane`` ``as`` ``qml`\
[](#__codelineno-8-2)\
[](#__codelineno-8-3)`dev`` ``=`` ``qml``.``device``(``"openquantum.device"``,`` ``wires``=``2``,`` ``shots``=``4096``,`` ``backend``=``"rigetti:cepheus-1-108q"``)`\
[](#__codelineno-8-4)\
[](#__codelineno-8-5)`@qml``.``qnode``(``dev``)`\
[](#__codelineno-8-6)`def`` ``correlation``():`\
[](#__codelineno-8-7)`    ``qml``.``Hadamard``(``wires``=``0``)`\
[](#__codelineno-8-8)`    ``qml``.``CNOT``(``wires``=``[``0``,`` ``1``])`\
[](#__codelineno-8-9)`    ``return`` ``qml``.``expval``(``qml``.``PauliZ``(``0``)`` ``@`` ``qml``.``PauliZ``(``1``))`\
[](#__codelineno-8-10)\
[](#__codelineno-8-11)`result`` ``=`` ``correlation``()`\
[](#__codelineno-8-12)`print``(``f``"<Z0 Z1> = ``{``result``:``.4f``}``"``)`\

Expected output:

[](#__codelineno-9-1)`<Z0 Z1> = 1.0000`\

For a Bell state, the \\Z \otimes Z\\ correlation is exactly 1 because qubits 0 and 1 are always measured in the same state.

## Next Steps

- [VQE Example](https://docs.openquantum.com/pennylane-plugin/examples/vqe/) -- Variational quantum eigensolver on Open Quantum.
- [QML Workflow](https://docs.openquantum.com/pennylane-plugin/examples/qml-workflow/) -- Quantum machine learning classification.
- [Backend Selection](https://docs.openquantum.com/pennylane-plugin/examples/backend-selection/) -- Choosing the right backend.
