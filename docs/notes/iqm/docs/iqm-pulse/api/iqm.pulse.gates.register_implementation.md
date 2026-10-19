> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.register_implementation.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.register_implementation.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 307d7a9fc5702ed5df967a5915f1a1085f140f09c64fc0df84d501e91a733e71.

# iqm.pulse.gates.register_implementation

iqm.pulse.gates.register_implementation(*operations*, *op_name*, *impl_name*, *impl_class*, *\**, *set_as_default=False*, *overwrite=False*)  
Register a new GateImplementation.

Parameters:  
- **operations** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp")*\]*) – Known operations, to which the new implementation is added.

- **op_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Name of the operation under which the implementation is registered.

- **impl_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Name of the implementation to register.

- **impl_class** ([*type*](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")*\[*[*GateImplementation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")*\]*) – Implementation class to register.

- **set_as_default** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to set as the default implementation for `op_name`.

- **overwrite** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If True, allows replacing an existing implementation.

Raises:  
- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – `op_name` does not exist in `operations`.

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – The implementation exists and `overwrite==False`.

Return type:  
*None*
