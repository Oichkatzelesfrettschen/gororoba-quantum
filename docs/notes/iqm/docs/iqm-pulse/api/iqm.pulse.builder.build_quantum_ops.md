> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.build_quantum_ops.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.build_quantum_ops.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3e16141ab07721ea8abdb2ec1ca9741b1dc314cd8d738bd71c35b845fc5c6f04.

# iqm.pulse.builder.build_quantum_ops

iqm.pulse.builder.build_quantum_ops(*ops*)  
Builds the table of known quantum operations.

Hardcoded canonical ops table is extended by the ones in `ops`. In case of name collisions, the content of `ops` takes priority over the defaults, with the following caveats:

- canonical implementation names cannot be redefined, and

- for canonical operations you can only change `implementations` and `defaults_for_locus`.

Parameters:  
**ops** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]\]*) – Contents of the `gate_definitions` section defining the quantum operations in the configuration YAML file. Implementation names must be mapped to either exposed GateImplementation class names, or actual GateImplementation classes. NOTE: Modified by the function.

Returns:  
Mapping from quantum operation names to their definitions.

Raises:  
- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – Requested implementation class is not exposed.

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – A canonical implementation name is being redefined.

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – Locus default references an undefined implementation.

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – Operation attributes don’t match defaults or are invalid.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp")\]
