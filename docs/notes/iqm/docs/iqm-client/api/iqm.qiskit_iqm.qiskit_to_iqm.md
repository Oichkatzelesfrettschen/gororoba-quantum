> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.qiskit_to_iqm.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.qiskit_to_iqm.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1004db2ec76283ef620835ab42262485bcf6f2259eaf95a6816413f3656c3caa.

# qiskit_to_iqm

Full path: iqm.qiskit_iqm.qiskit_to_iqm

Conversion tools from Qiskit to IQM representation.

Functions

|  |  |
|----|----|
| [`deserialize_instructions`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.qiskit_to_iqm.deserialize_instructions.html#iqm.qiskit_iqm.qiskit_to_iqm.deserialize_instructions "iqm.qiskit_iqm.qiskit_to_iqm.deserialize_instructions")(instructions, ...) | Turn a list of IQM Instructions into a Qiskit QuantumCircuit. |
| [`serialize_instructions`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.qiskit_to_iqm.serialize_instructions.html#iqm.qiskit_iqm.qiskit_to_iqm.serialize_instructions "iqm.qiskit_iqm.qiskit_to_iqm.serialize_instructions")(circuit, ...\[, ...\]) | Serialize a quantum circuit into the IQM data transfer format. |

Classes

|  |  |
|----|----|
| [`MeasurementKey`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.qiskit_to_iqm.MeasurementKey.html#iqm.qiskit_iqm.qiskit_to_iqm.MeasurementKey "iqm.qiskit_iqm.qiskit_to_iqm.MeasurementKey") | Unique key associated with a measurement instruction. |

Exceptions

|  |  |
|----|----|
| [`InstructionNotSupportedError`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.qiskit_to_iqm.InstructionNotSupportedError.html#iqm.qiskit_iqm.qiskit_to_iqm.InstructionNotSupportedError "iqm.qiskit_iqm.qiskit_to_iqm.InstructionNotSupportedError") | Raised when a given instruction is not supported by the IQM Server. |

Inheritance

![Inheritance diagram of iqm.qiskit_iqm.qiskit_to_iqm](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-1cf0bd2e13b73529709848757a40083e10a36ed7.png)
