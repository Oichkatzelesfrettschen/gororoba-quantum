> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.register_operation.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.register_operation.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 acc202aff6c3e5e2f0aafdea03efd6e99d7721f015d58d6dbe54ac5146ad82d2.

# iqm.pulse.gates.register_operation

iqm.pulse.gates.register_operation(*operations*, *op*, *overwrite=False*)  
Register a new QuantumOp to the given operations table.

Parameters:  
- **operations** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp")*\]*) – Known operations, to which the new operation is added.

- **op** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp")) – Definition for the new operation.

- **overwrite** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If True, allows replacing an existing operation in `operations`.

Raises:  
- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – `op.name` exists in `operations` and `overwrite==False`.

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – `op.name` is the name of a canonical operation in iqm-pulse.

Return type:  
*None*
