> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 9459f542002bdb55374e2b519b1e8eda7ffdcb86703f52200ac7bb3c45d3a38b.

# iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit

*class* iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit(*operations*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

A quantum circuit wrapper that supports readout twirling and gate randomization.

This class serves as a mutable working representation for building and manipulating quantum circuits. It tracks single-qubit gates, measurements, and readout twirling state. Use `to_circuit(name)` to convert to the immutable `Circuit`.

Note

We intentionally do **not** store a `Circuit` internally. `Circuit.instructions` is an immutable `tuple`, which would be rebuilt on every `append_operation` call. Instead, `operations` is kept as a mutable `list[CircuitOperation]` throughout circuit construction, and converted to `Circuit` on demand via `to_circuit()`.

Parameters:  
**operations** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*CircuitOperation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "(in iqm.pulse v15.0.0)")*\]*)

operations  
List of operations in the circuit.

rot_dict  
Dictionary for readout twirling rotations, if applied.

sqg_counter  
Counter for single-qubit gates per qubit.

measured_qubits  
List of qubits that are measured.

active_qubits  
List of all qubits involved in the circuit.

Methods

|  |  |
|----|----|
| [`append_operation`](#iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit.append_operation "iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit.append_operation")(operation) | Append a deep copy of the operation to the circuit and update basic analysis. |
| [`basic_analysis`](#iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit.basic_analysis "iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit.basic_analysis")() | Perform basic analysis on quantum circuit operations. |
| [`get_rot_char_per_meas_key`](#iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit.get_rot_char_per_meas_key "iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit.get_rot_char_per_meas_key")() | Get rotation character per measurement key due to readout twirling. |
| [`to_circuit`](#iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit.to_circuit "iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit.to_circuit")(name) | Convert to an immutable `Circuit`. |

basic_analysis()  
Perform basic analysis on quantum circuit operations.

This method analyzes the circuit operations to extract information about single-qubit gates, measurements, and active qubits. It also validates that no mid-circuit measurements are present.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If mid-circuit measurements are detected (when any qubit is measured more than once).

Return type:  
None

Note

This method populates the following instance attributes:

> - `sqg_counter`: Dictionary mapping qubit identifiers to the count of ‘prx’ operations performed on each qubit.
>
> - `measured_qubits`: List of qubit identifiers that have measurement operations.
>
> - `active_qubits`: List of all qubit identifiers that appear in any operation.

The method iterates through all operations in the circuit and:

> 1.  Counts ‘prx’ (parametric rotation) operations per qubit
>
> 2.  Counts measurement operations per qubit
>
> 3.  Collects all qubits involved in any operation
>
> 4.  Validates that no qubit is measured more than once

append_operation(*operation*)  
Append a deep copy of the operation to the circuit and update basic analysis.

A deep copy is made to ensure that no external references to the operation are retained, preventing shared-state bugs when the same source circuit is randomized multiple times.

Parameters:  
**operation** ([*CircuitOperation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "(in iqm.pulse v15.0.0)"))

Return type:  
None

get_rot_char_per_meas_key()  
Get rotation character per measurement key due to readout twirling.

Returns:  
Dictionary mapping measurement keys to rotation characters (‘I’ or ‘X’).

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]

to_circuit(*name*)  
Convert to an immutable `Circuit`.

Parameters:  
**name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Name to assign to the circuit.

Returns:  
A `Circuit` with the current operations as instructions.

Return type:  
[*Circuit*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)")
