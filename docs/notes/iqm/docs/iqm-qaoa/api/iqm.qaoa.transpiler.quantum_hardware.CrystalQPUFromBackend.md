> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.CrystalQPUFromBackend.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.CrystalQPUFromBackend.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d969c83d4a4729419633fba153da282e06f8999ec29f4db18cd31e87b607108d.

# CrystalQPUFromBackend

Module: [`iqm.qaoa.transpiler.quantum_hardware`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.html#module-iqm.qaoa.transpiler.quantum_hardware "iqm.qaoa.transpiler.quantum_hardware")

*class* iqm.qaoa.transpiler.quantum_hardware.CrystalQPUFromBackend(*backend*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/quantum_hardware.py#L180-L443)  
Bases: [`QPU`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.QPU.html#iqm.qaoa.transpiler.quantum_hardware.QPU "iqm.qaoa.transpiler.quantum_hardware.QPU")

Class for a QPU with square lattice topology, initialited from a Qiskit backend object.

Since the topology is square lattice, the qubits can be identified with 2D integer coordinates (up to a global shift). The 2D coordinates are calculated from the connectivity topology (provided as the `StaticQuantumArchitecture` of the input `backend`).

If the provided `backend` is an instance of [`IQMBackend`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend "(in IQM client v36.0.0)") and it was created by `IQMProvider.get_backend(use_metrics=True)`, then it contains the calibration metrics. The CZ gate errors from these are converted to gate fidelities and saved as edge attributes of the hardware graph.

Parameters:  
**backend** (*IQMBackendBase*) – The backend containing information about the QPU.

Raises:  
- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the `backend` is [`IQMBackend`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend "(in IQM client v36.0.0)") and it contains multiple different CZ gate fidelity entries for a pair of coupled qubits.

- [**TypeError**](https://docs.python.org/3.11/library/exceptions.html#TypeError "(in Python v3.11)") – If an unknown type of backend is provided (neither [`IQMBackend`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend "(in IQM client v36.0.0)") nor `IQMFakeBackend`).

Attributes

Methods

Inheritance

![Inheritance diagram of iqm.qaoa.transpiler.quantum_hardware.CrystalQPUFromBackend](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-c05adff71fb38c58e7a87bc67fec1382d49257a4.png)
