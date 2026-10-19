> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 78e2a2365ad36128777d10555b64f066827dcf31779e9f7a3c12f9e58109c182.

# qiskit_iqm

Full path: iqm.qiskit_iqm

Qiskit adapter for IQM’s quantum computers.

Subpackages and modules

|  |  |
|----|----|
| [`examples`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.examples.html#module-iqm.qiskit_iqm.examples "iqm.qiskit_iqm.examples") | Example code. |
| [`fake_backends`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.fake_backends.html#module-iqm.qiskit_iqm.fake_backends "iqm.qiskit_iqm.fake_backends") | Fake backends for simulating IQM quantum computers. |
| [`iqm_backend`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.html#module-iqm.qiskit_iqm.iqm_backend "iqm.qiskit_iqm.iqm_backend") | Qiskit backend for IQM quantum computers. |
| [`iqm_circuit`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.html#module-iqm.qiskit_iqm.iqm_circuit "iqm.qiskit_iqm.iqm_circuit") | Extension of the QuantumCircuit class that adds the .move(qubit, resonator) shortcut for the MOVE gate. |
| [`iqm_circuit_validation`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit_validation.html#module-iqm.qiskit_iqm.iqm_circuit_validation "iqm.qiskit_iqm.iqm_circuit_validation") | Helper functions for circuit validation. |
| [`iqm_job`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_job.html#module-iqm.qiskit_iqm.iqm_job "iqm.qiskit_iqm.iqm_job") | Circuit execution jobs. |
| [`iqm_move_layout`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_move_layout.html#module-iqm.qiskit_iqm.iqm_move_layout "iqm.qiskit_iqm.iqm_move_layout") | Generate an initial layout for a quantum circuit containing MOVE gates. |
| [`iqm_naive_move_pass`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_naive_move_pass.html#module-iqm.qiskit_iqm.iqm_naive_move_pass "iqm.qiskit_iqm.iqm_naive_move_pass") | Naive transpilation for the IQM Star architecture. |
| [`iqm_provider`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.html#module-iqm.qiskit_iqm.iqm_provider "iqm.qiskit_iqm.iqm_provider") | Qiskit backend provider for IQM backends. |
| [`iqm_target`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_target.html#module-iqm.qiskit_iqm.iqm_target "iqm.qiskit_iqm.iqm_target") | Transpilation target for IQM quantum computers. |
| [`iqm_transpilation`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_transpilation.html#module-iqm.qiskit_iqm.iqm_transpilation "iqm.qiskit_iqm.iqm_transpilation") | Transpilation tool to optimize the decomposition of single-qubit gates tailored to IQM hardware. |
| [`move_gate`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.move_gate.html#module-iqm.qiskit_iqm.move_gate "iqm.qiskit_iqm.move_gate") | MOVE gate to be used on the IQM Star architecture. |
| [`pulse_level_utils`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.pulse_level_utils.html#module-iqm.qiskit_iqm.pulse_level_utils "iqm.qiskit_iqm.pulse_level_utils") | Utilities for running pulse-level jobs using Qiskit classes. |
| [`qir_utils`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.qir_utils.html#module-iqm.qiskit_iqm.qir_utils "iqm.qiskit_iqm.qir_utils") | Utilities for working with QIR modules. |
| [`qiskit_to_iqm`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.qiskit_to_iqm.html#module-iqm.qiskit_iqm.qiskit_to_iqm "iqm.qiskit_iqm.qiskit_to_iqm") | Conversion tools from Qiskit to IQM representation. |
| [`transpiler_plugins`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.transpiler_plugins.html#module-iqm.qiskit_iqm.transpiler_plugins "iqm.qiskit_iqm.transpiler_plugins") | Collection of Qiskit transpiler plugins for native use of specialized transpiler passes by our devices. |
