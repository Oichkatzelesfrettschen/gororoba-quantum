> Full piece: [https://docs.openquantum.com/getting-started/resources/](https://docs.openquantum.com/getting-started/resources/)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 66a06c839af762d46af6b82906398a0816fea096886aa7caf1a884289d92e963.

# Sample Circuits & Notebooks

Open Quantum provides ready-to-run quantum circuits and Jupyter notebooks to help you get started quickly.

## Sample QASM Circuits

The [Sample QASM](https://www.openquantum.com/sample-qasm) page on the portal has downloadable OpenQASM 2.0 circuits covering fundamental quantum algorithms:

| Circuit             | Algorithm              | Qubits |
|---------------------|------------------------|--------|
| `deutsch_n2.qasm`   | Deutsch's Algorithm    | 2      |
| `grover_n2.qasm`    | Grover's Search        | 2      |
| `cat_state_n4.qasm` | Cat State (GHZ)        | 4      |
| `simon_n6.qasm`     | Simon's Algorithm      | 6      |
| `qaoa_n3.qasm`      | QAOA                   | 3      |
| `bell_n4.qasm`      | Bell State Preparation | 4      |

These can be submitted directly through the [web portal](https://docs.openquantum.com/portal/submitting-jobs/) or via the SDK:

[](#__codelineno-0-1)`job`` ``=`` ``scheduler``.``submit_job``(``config``,`` ``file_path``=``"qft.qasm"``)`\

## Sample Notebooks

The [Sample Notebooks](https://www.openquantum.com/notebooks) page has Jupyter notebooks that open directly in Google Colab — no local setup required.

| Notebook | Description |
|----|----|
| **Run a Circuit in Python** | Execute a quantum circuit on real hardware using the Open Quantum Python SDK. Connect to IonQ, Rigetti, IQM, and AQT backends. |
| **Run a Simulation with Quantum Rings SDK** | Use the Quantum Rings SDK to run a quantum simulation without needing access to physical hardware. |

## Using Sample Circuits with the SDK

### Core SDK

[](#__codelineno-1-1)`from`` ``openquantum_sdk.clients`` ``import`` ``SchedulerClient``,`` ``JobSubmissionConfig`\
[](#__codelineno-1-2)\
[](#__codelineno-1-3)`scheduler`` ``=`` ``SchedulerClient``(``auth``=``auth``)`\
[](#__codelineno-1-4)\
[](#__codelineno-1-5)`config`` ``=`` ``JobSubmissionConfig``(`\
[](#__codelineno-1-6)`    ``backend_class_id``=``"ionq:forte-1"``,`\
[](#__codelineno-1-7)`    ``name``=``"Grover Search"``,`\
[](#__codelineno-1-8)`    ``job_subcategory_id``=``"opt:oth"``,``  ``# Optimization`\
[](#__codelineno-1-9)`    ``shots``=``128``,`\
[](#__codelineno-1-10)`)`\
[](#__codelineno-1-11)\
[](#__codelineno-1-12)`job`` ``=`` ``scheduler``.``submit_job``(``config``,`` ``file_path``=``"grover_n2.qasm"``)`\
[](#__codelineno-1-13)`output`` ``=`` ``scheduler``.``download_job_output``(``job``)`\
[](#__codelineno-1-14)`print``(``output``)`\
[](#__codelineno-1-15)`if`` ``job``.``calibration_data_url``:`\
[](#__codelineno-1-16)`    ``print``(``scheduler``.``download_job_calibration``(``job``))`\

### Qiskit Plugin

[](#__codelineno-2-1)`from`` ``qiskit`` ``import`` ``QuantumCircuit`\
[](#__codelineno-2-2)`from`` ``openquantum_sdk_qiskit`` ``import`` ``OpenQuantumService`\
[](#__codelineno-2-3)\
[](#__codelineno-2-4)`service`` ``=`` ``OpenQuantumService``()`\
[](#__codelineno-2-5)`backend`` ``=`` ``service``.``return_backend``(``"ionq:forte-1"``)`\
[](#__codelineno-2-6)\
[](#__codelineno-2-7)`qc`` ``=`` ``QuantumCircuit``.``from_qasm_file``(``"bell_n4.qasm"``)`\
[](#__codelineno-2-8)`job`` ``=`` ``backend``.``run``(``qc``,`` ``shots``=``128``)`\
[](#__codelineno-2-9)`result`` ``=`` ``job``.``result``()`\
[](#__codelineno-2-10)`print``(``result``.``get_counts``())`\

### PennyLane Plugin

[](#__codelineno-3-1)`import`` ``pennylane`` ``as`` ``qml`\
[](#__codelineno-3-2)\
[](#__codelineno-3-3)`dev`` ``=`` ``qml``.``device``(`\
[](#__codelineno-3-4)`    ``"openquantum.device"``,`\
[](#__codelineno-3-5)`    ``wires``=``2``,`\
[](#__codelineno-3-6)`    ``shots``=``128``,`\
[](#__codelineno-3-7)`    ``backend``=``"ionq:forte-1"``,`\
[](#__codelineno-3-8)`)`\
[](#__codelineno-3-9)\
[](#__codelineno-3-10)`@qml``.``qnode``(``dev``)`\
[](#__codelineno-3-11)`def`` ``bell_state``():`\
[](#__codelineno-3-12)`    ``qml``.``Hadamard``(``0``)`\
[](#__codelineno-3-13)`    ``qml``.``CNOT``(``wires``=``[``0``,`` ``1``])`\
[](#__codelineno-3-14)`    ``return`` ``qml``.``counts``()`\
[](#__codelineno-3-15)\
[](#__codelineno-3-16)`print``(``bell_state``())`\

### Cirq Plugin

[](#__codelineno-4-1)`import`` ``cirq`\
[](#__codelineno-4-2)`from`` ``cirq_openquantum`` ``import`` ``OpenQuantumSampler`\
[](#__codelineno-4-3)\
[](#__codelineno-4-4)`sampler`` ``=`` ``OpenQuantumSampler``(``backend``=``"ionq:forte-1"``)`\
[](#__codelineno-4-5)\
[](#__codelineno-4-6)`q`` ``=`` ``cirq``.``LineQubit``.``range``(``2``)`\
[](#__codelineno-4-7)`circuit`` ``=`` ``cirq``.``Circuit``(`\
[](#__codelineno-4-8)`    ``cirq``.``H``(``q``[``0``]),`\
[](#__codelineno-4-9)`    ``cirq``.``CNOT``(``q``[``0``],`` ``q``[``1``]),`\
[](#__codelineno-4-10)`    ``cirq``.``measure``(``*``q``,`` ``key``=``"m"``),`\
[](#__codelineno-4-11)`)`\
[](#__codelineno-4-12)\
[](#__codelineno-4-13)`result`` ``=`` ``sampler``.``run``(``circuit``,`` ``repetitions``=``128``)`\
[](#__codelineno-4-14)`print``(``result``.``histogram``(``key``=``"m"``))`\

### Qrisp Plugin

[](#__codelineno-5-1)`from`` ``qrisp`` ``import`` ``QuantumVariable``,`` ``h``,`` ``cx`\
[](#__codelineno-5-2)`from`` ``qrisp_openquantum`` ``import`` ``OpenQuantumBackend`\
[](#__codelineno-5-3)\
[](#__codelineno-5-4)`oq`` ``=`` ``OpenQuantumBackend``(``backend``=``"ionq:forte-1"``,`` ``shots``=``128``)`\
[](#__codelineno-5-5)\
[](#__codelineno-5-6)`qv`` ``=`` ``QuantumVariable``(``2``)`\
[](#__codelineno-5-7)`h``(``qv``[``0``])`\
[](#__codelineno-5-8)`cx``(``qv``[``0``],`` ``qv``[``1``])`\
[](#__codelineno-5-9)\
[](#__codelineno-5-10)`print``(``qv``.``get_measurement``(``backend``=``oq``,`` ``shots``=``128``))`\

## Related Pages

- [Submitting Jobs](https://docs.openquantum.com/portal/submitting-jobs/) -- Walk through submitting a job in the web UI.
- [Quick Start (SDK)](https://docs.openquantum.com/core-sdk/quickstart/) -- Submit your first job with Python.
- [Backends](https://docs.openquantum.com/concepts/backends/) -- Available quantum hardware.
