> Full piece: [https://docs.openquantum.com/qbraid/examples/](https://docs.openquantum.com/qbraid/examples/)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3327312948dadff542c83b058e0369d5281fd01a9d7ab6a97899f9c57e7f6487.

# Examples

Common quantum circuits utilizing a range of qBraid-compatible frameworks, ready to run in qBraid Lab or your preferred local code editor.

Note

In [qBraid Lab](https://www.qbraid.com/lab), the qBraid SDK is preinstalled and your API key is detected automatically, so you can drop the `api_key` argument: `provider = QbraidProvider()`.

## Bell State (Qiskit)

Target an Open Quantum backend from the qBraid runtime, build a Bell state with Qiskit, run it, and print the measurement counts.

[](#__codelineno-0-1)`from`` ``qbraid.runtime`` ``import`` ``QbraidProvider`\
[](#__codelineno-0-2)`from`` ``qiskit`` ``import`` ``QuantumCircuit`\
[](#__codelineno-0-3)\
[](#__codelineno-0-4)`# Your qBraid API key (auto-detected inside qBraid Lab)`\
[](#__codelineno-0-5)`provider`` ``=`` ``QbraidProvider``(``api_key``=``"YOUR_QBRAID_API_KEY"``)`\
[](#__codelineno-0-6)\
[](#__codelineno-0-7)`# Target an Open Quantum backend`\
[](#__codelineno-0-8)`device`` ``=`` ``provider``.``get_device``(``"openquantum:iqm:qpu:garnet"``)`\
[](#__codelineno-0-9)\
[](#__codelineno-0-10)`# Build a Bell state with standard Qiskit`\
[](#__codelineno-0-11)`circuit`` ``=`` ``QuantumCircuit``(``2``,`` ``2``)`\
[](#__codelineno-0-12)`circuit``.``h``(``0``)`\
[](#__codelineno-0-13)`circuit``.``cx``(``0``,`` ``1``)`\
[](#__codelineno-0-14)`circuit``.``measure``([``0``,`` ``1``],`` ``[``0``,`` ``1``])`` `\
[](#__codelineno-0-15)\
[](#__codelineno-0-16)`# Run on real quantum hardware`\
[](#__codelineno-0-17)`job`` ``=`` ``device``.``run``(``circuit``,`` ``shots``=``1024``)`\
[](#__codelineno-0-18)`result`` ``=`` ``job``.``result``()`\
[](#__codelineno-0-19)`print``(``result``.``data``.``get_counts``())`\
[](#__codelineno-0-20)`# e.g. {'00': 503, '11': 521}`\

Note

When submitting jobs through the `QbraidProvider`, you can specify optional parameters using the `runtime_options` argument: `runtime_options={"parameter": "value"}`. The `runtime_options` dictionary is passed directly to the backend, so you can use any parameters supported by the Open Quantum SDK.

## Bell State (Cirq)

The same Bell state, built in Cirq.

[](#__codelineno-1-1)`from`` ``qbraid.runtime`` ``import`` ``QbraidProvider`\
[](#__codelineno-1-2)`import`` ``cirq`\
[](#__codelineno-1-3)\
[](#__codelineno-1-4)`provider`` ``=`` ``QbraidProvider``(``api_key``=``"YOUR_QBRAID_API_KEY"``)`\
[](#__codelineno-1-5)`device`` ``=`` ``provider``.``get_device``(``"openquantum:iqm:qpu:garnet"``)`\
[](#__codelineno-1-6)\
[](#__codelineno-1-7)`# Build a Bell state with Cirq`\
[](#__codelineno-1-8)`q0``,`` ``q1`` ``=`` ``cirq``.``LineQubit``.``range``(``2``)`\
[](#__codelineno-1-9)`circuit`` ``=`` ``cirq``.``Circuit``(`\
[](#__codelineno-1-10)`    ``cirq``.``H``(``q0``),`\
[](#__codelineno-1-11)`    ``cirq``.``CNOT``(``q0``,`` ``q1``),`\
[](#__codelineno-1-12)`    ``cirq``.``measure``(``q0``,`` ``q1``,`` ``key``=``"result"``),`\
[](#__codelineno-1-13)`)`\
[](#__codelineno-1-14)\
[](#__codelineno-1-15)`job`` ``=`` ``device``.``run``(`\
[](#__codelineno-1-16)`    ``circuit``,`` `\
[](#__codelineno-1-17)`    ``shots``=``1024``,`\
[](#__codelineno-1-18)`    ``runtime_options``=``{`` ``# Optional parameters`\
[](#__codelineno-1-19)`        ``"organization_id"``:`` ``"None"``,`` ``# Organization UUID`\
[](#__codelineno-1-20)`        ``"execution_plan"``:`` ``"public"``,`` ``# Execution plan ('public', 'private', 'auto') `\
[](#__codelineno-1-21)`        ``"queue_priority"``:`` ``"standard"``,`` ``# Queue priority ('standard', 'priority', 'auto') `\
[](#__codelineno-1-22)`        ``"job_subcategory_id"``:`` ``"oth:oth"``,`` ``# Job subcategory short code (list possible ids with the Open Quantum SDK 'SchedulerClient')`\
[](#__codelineno-1-23)`        ``"job_timeout_seconds"``:`` ``"86400"`` ``# Maximum time to wait for a job to complete`\
[](#__codelineno-1-24)`        ``}`\
[](#__codelineno-1-25)`    ``)`\
[](#__codelineno-1-26)`result`` ``=`` ``job``.``result``()`\
[](#__codelineno-1-27)`print``(``result``.``data``.``get_counts``())`\

## GHZ State (Qiskit)

3-qubit GHZ State using Qiskit.

[](#__codelineno-2-1)`from`` ``qbraid.runtime`` ``import`` ``QbraidProvider`\
[](#__codelineno-2-2)`from`` ``qiskit`` ``import`` ``QuantumCircuit`\
[](#__codelineno-2-3)\
[](#__codelineno-2-4)`provider`` ``=`` ``QbraidProvider``(``api_key``=``"YOUR_QBRAID_API_KEY"``)`\
[](#__codelineno-2-5)`device`` ``=`` ``provider``.``get_device``(``"openquantum:iqm:qpu:garnet"``)`\
[](#__codelineno-2-6)\
[](#__codelineno-2-7)`# 3-qubit GHZ state`\
[](#__codelineno-2-8)`circuit`` ``=`` ``QuantumCircuit``(``3``,`` ``3``)`\
[](#__codelineno-2-9)`circuit``.``h``(``0``)`\
[](#__codelineno-2-10)`circuit``.``cx``(``0``,`` ``1``)`\
[](#__codelineno-2-11)`circuit``.``cx``(``1``,`` ``2``)`\
[](#__codelineno-2-12)`circuit``.``measure``([``0``,`` ``1``,`` ``2``],`` ``[``0``,`` ``1``,`` ``2``])`\
[](#__codelineno-2-13)\
[](#__codelineno-2-14)`job`` ``=`` ``device``.``run``(``circuit``,`` ``shots``=``1024``)`\
[](#__codelineno-2-15)`result`` ``=`` ``job``.``result``()`\
[](#__codelineno-2-16)`print``(``result``.``data``.``get_counts``())`\
[](#__codelineno-2-17)`# e.g. {'000': 490, '111': 502, '010': 16, '101': 16}`\

## Parameterized Rotation with Expectation Value (PennyLane)

Use qBraid's PennyLane plugin to sweep an `RX` rotation angle and measure the expectation value of `PauliZ`.

[](#__codelineno-3-1)`import`` ``numpy`` ``as`` ``np`\
[](#__codelineno-3-2)`import`` ``pennylane`` ``as`` ``qml`\
[](#__codelineno-3-3)`from`` ``pennylane.tape`` ``import`` ``QuantumTape`\
[](#__codelineno-3-4)\
[](#__codelineno-3-5)`from`` ``qbraid`` ``import`` ``QbraidProvider`\
[](#__codelineno-3-6)\
[](#__codelineno-3-7)`provider`` ``=`` ``QbraidProvider``(``api_key``=``"YOUR_QBRAID_API_KEY"``)`\
[](#__codelineno-3-8)`device`` ``=`` ``provider``.``get_device``(``"openquantum:iqm:qpu:garnet"``)`\
[](#__codelineno-3-9)\
[](#__codelineno-3-10)`def`` ``rotation_circuit``(``angle``,`` ``shots``=``10``):`\
[](#__codelineno-3-11)`    ``with`` ``QuantumTape``()`` ``as`` ``tape``:`\
[](#__codelineno-3-12)`        ``qml``.``RX``(``angle``,`` ``wires``=``0``)`\
[](#__codelineno-3-13)`        ``qml``.``sample``(``wires``=``0``)`\
[](#__codelineno-3-14)\
[](#__codelineno-3-15)`    ``job`` ``=`` ``device``.``run``(``tape``,`` ``shots``=``shots``)`\
[](#__codelineno-3-16)`    ``result`` ``=`` ``job``.``result``()`\
[](#__codelineno-3-17)`    ``counts`` ``=`` ``result``.``data``.``get_counts``()`\
[](#__codelineno-3-18)\
[](#__codelineno-3-19)`    ``# Compute <Z> manually from measured bitstrings: +1 for '0', -1 for '1'`\
[](#__codelineno-3-20)`    ``total`` ``=`` ``sum``(``counts``.``values``())`\
[](#__codelineno-3-21)`    ``expval`` ``=`` ``sum``((``1`` ``if`` ``bit`` ``==`` ``"0"`` ``else`` ``-``1``)`` ``*`` ``n`` ``for`` ``bit``,`` ``n`` ``in`` ``counts``.``items``())`` ``/`` ``total`\
[](#__codelineno-3-22)`    ``return`` ``expval`\
[](#__codelineno-3-23)\
[](#__codelineno-3-24)`# Sweep over angles from 0 to 2*pi`\
[](#__codelineno-3-25)`angles`` ``=`` ``np``.``linspace``(``0``,`` ``2`` ``*`` ``np``.``pi``,`` ``8``)`\
[](#__codelineno-3-26)`for`` ``angle`` ``in`` ``angles``:`\
[](#__codelineno-3-27)`    ``result`` ``=`` ``rotation_circuit``(``angle``)`\
[](#__codelineno-3-28)`    ``print``(``f``"RX(``{``angle``:``.2f``}``):  = ``{``result``:``.4f``}``"``)`\
[](#__codelineno-3-29)\
[](#__codelineno-3-30)`# e.g.`\
[](#__codelineno-3-31)`# RX(0.00):  = 1.0000`\
[](#__codelineno-3-32)`# RX(0.90):  = 0.6235`\
[](#__codelineno-3-33)`# RX(1.80):  = -0.2272`\
[](#__codelineno-3-34)`# RX(2.69):  = -0.9010`\
[](#__codelineno-3-35)`# RX(3.59):  = -0.9010`\
[](#__codelineno-3-36)`# RX(4.49):  = -0.2272`\
[](#__codelineno-3-37)`# RX(5.39):  = 0.6235`\
[](#__codelineno-3-38)`# RX(6.28):  = 1.0000`\

Tip

Simply change the device id to run the same circuit on different hardware, for example `provider.get_device("openquantum:ionq:qpu:forte-1")`. See [Backends & Targets](https://docs.openquantum.com/qbraid/backends-targets/) for the full list.

## Next Steps

- [Backends & Targets](https://docs.openquantum.com/qbraid/backends-targets/) -- all Open Quantum device ids.
- [Installation & Authentication](https://docs.openquantum.com/qbraid/installation/) -- account linking and credentials.
