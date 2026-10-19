> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.devices.iqm_device.IQMDevice.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.devices.iqm_device.IQMDevice.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 da00daff920ca771ca7ed68ce4ac0d1affc392168647f0ef797a92a3ad4b4dda.

# IQMDevice

Module: [`iqm.cirq_iqm.devices.iqm_device`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.devices.iqm_device.html#module-iqm.cirq_iqm.devices.iqm_device "iqm.cirq_iqm.devices.iqm_device")

*class* iqm.cirq_iqm.devices.iqm_device.IQMDevice(*metadata: [IQMDeviceMetadata](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata.html#iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata "iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata")*)  
Bases: `Device`

ABC for the properties of a specific IQM quantum architecture.

Adds extra functionality on top of the basic `cirq.Device` class for decomposing gates, optimizing circuits and mapping qubits.

Parameters:  
**metadata** ([*IQMDeviceMetadata*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata.html#iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata "iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata")) – device metadata which contains the qubits, their connectivity, and the native gateset

Attributes

|  |  |
|----|----|
| [`metadata`](#iqm.cirq_iqm.devices.iqm_device.IQMDevice.metadata "iqm.cirq_iqm.devices.iqm_device.IQMDevice.metadata") | Returns metadata for the device. |

Methods

|  |  |
|----|----|
| [`check_qubit_connectivity`](#iqm.cirq_iqm.devices.iqm_device.IQMDevice.check_qubit_connectivity "iqm.cirq_iqm.devices.iqm_device.IQMDevice.check_qubit_connectivity") | Raises a ValueError if operation acts on qubits that are not connected. |
| [`decompose_circuit`](#iqm.cirq_iqm.devices.iqm_device.IQMDevice.decompose_circuit "iqm.cirq_iqm.devices.iqm_device.IQMDevice.decompose_circuit") | Decomposes the given circuit to the native gate set of the device. |
| [`decompose_operation`](#iqm.cirq_iqm.devices.iqm_device.IQMDevice.decompose_operation "iqm.cirq_iqm.devices.iqm_device.IQMDevice.decompose_operation") | Decompose a single quantum operation into the native operation set. |
| [`get_qubit`](#iqm.cirq_iqm.devices.iqm_device.IQMDevice.get_qubit "iqm.cirq_iqm.devices.iqm_device.IQMDevice.get_qubit") | The device qubit corresponding to the given numeric index. |
| [`get_qubit_index`](#iqm.cirq_iqm.devices.iqm_device.IQMDevice.get_qubit_index "iqm.cirq_iqm.devices.iqm_device.IQMDevice.get_qubit_index") | The numeric index of the given qubit on the device. |
| [`has_valid_operation_targets`](#iqm.cirq_iqm.devices.iqm_device.IQMDevice.has_valid_operation_targets "iqm.cirq_iqm.devices.iqm_device.IQMDevice.has_valid_operation_targets") | Predicate, True iff the given operation is native and its targets are valid. |
| [`is_native_operation`](#iqm.cirq_iqm.devices.iqm_device.IQMDevice.is_native_operation "iqm.cirq_iqm.devices.iqm_device.IQMDevice.is_native_operation") | Predicate, True iff the given operation is considered native for the architecture. |
| [`operation_decomposer`](#iqm.cirq_iqm.devices.iqm_device.IQMDevice.operation_decomposer "iqm.cirq_iqm.devices.iqm_device.IQMDevice.operation_decomposer") | Decomposes operations into the native operation set. |
| [`route_circuit`](#iqm.cirq_iqm.devices.iqm_device.IQMDevice.route_circuit "iqm.cirq_iqm.devices.iqm_device.IQMDevice.route_circuit") | Routes the given circuit to the device connectivity and qubit names. |
| [`validate_circuit`](#iqm.cirq_iqm.devices.iqm_device.IQMDevice.validate_circuit "iqm.cirq_iqm.devices.iqm_device.IQMDevice.validate_circuit") | Raise an error if `circuit` is not compatible with this device. |
| [`validate_move`](#iqm.cirq_iqm.devices.iqm_device.IQMDevice.validate_move "iqm.cirq_iqm.devices.iqm_device.IQMDevice.validate_move") | Validate whether the IQMMoveGate is between qubit and resonator registers. |
| [`validate_moves`](#iqm.cirq_iqm.devices.iqm_device.IQMDevice.validate_moves "iqm.cirq_iqm.devices.iqm_device.IQMDevice.validate_moves") | Validate whether the IQMMoveGates are correctly applied in the circuit. |
| [`validate_operation`](#iqm.cirq_iqm.devices.iqm_device.IQMDevice.validate_operation "iqm.cirq_iqm.devices.iqm_device.IQMDevice.validate_operation") | Raise an error if `operation` is not supported on this device. |

*property* metadata*: [IQMDeviceMetadata](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata.html#iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata "iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata")*  
Returns metadata for the device.

*classmethod* get_qubit_index(*qubit: NamedQubit*) → [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")  
The numeric index of the given qubit on the device.

Parameters:  
**qubit** (*NamedQubit*)

Return type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

get_qubit(*index: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → Qid  
The device qubit corresponding to the given numeric index.

Parameters:  
**index** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

Return type:  
*Qid*

check_qubit_connectivity(*operation: Operation*) → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Raises a ValueError if operation acts on qubits that are not connected.

Parameters:  
**operation** (*Operation*)

Return type:  
None

is_native_operation(*op: Operation*) → [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")  
Predicate, True iff the given operation is considered native for the architecture.

Parameters:  
**op** (*Operation*)

Return type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

has_valid_operation_targets(*op: Operation*) → [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")  
Predicate, True iff the given operation is native and its targets are valid.

Parameters:  
**op** (*Operation*)

Return type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

operation_decomposer(*op: Operation*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[Operation\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Decomposes operations into the native operation set.

All the decompositions below keep track of global phase (required for decomposing controlled gates).

Parameters:  
**op** (*Operation*) – operation to decompose

Returns:  
decomposition, or None to pass `op` to the Cirq native decomposition machinery instead

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[*Operation*\] \| None

decompose_operation(*operation: cirq.Operation*) → cirq.OP_TREE  
Decompose a single quantum operation into the native operation set.

Parameters:  
**operation** (*cirq.Operation*)

Return type:  
cirq.OP_TREE

route_circuit(*circuit: Circuit*, *\**, *initial_mapper: AbstractInitialMapper \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *qubit_subset: [Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[Qid\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[Circuit, [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[Qid, Qid\], [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[Qid, Qid\]\]  
Routes the given circuit to the device connectivity and qubit names.

The routed circuit uses the device qubits, and may have additional SWAP gates inserted to perform the qubit routing. The transformer `cirq.RouterCQC` is used for routing. Note that only gates of one or two qubits, and measurement operations of arbitrary size are supported.

Adds the attribute `iqm_calibration_set_id` to the routed circuit, with value taken from `self.metadata.architecture.calibration_set_id` if available, otherwise None.

Parameters:  
- **circuit** (*Circuit*) – Circuit to route.

- **initial_mapper** (*AbstractInitialMapper* *\|* *None*) – Initial mapping from `circuit` qubits to device qubits, to serve as the starting point of the routing. `None` means it will be generated automatically.

- **qubit_subset** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[Qid\]* *\|* *None*) – Restrict the routing to this subset of the device qubits. If `None`, use the entire device.

Returns:  
routed circuit, initial mapping before inserting SWAP gates (see `cirq.RouterCQC.route_circuit()`), final mapping from physical qubits to physical qubits (see `cirq.RouterCQC.route_circuit()`)

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – routing is impossible

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[*Circuit*, [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[*Qid*, *Qid*\], [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[*Qid*, *Qid*\]\]

decompose_circuit(*circuit: Circuit*) → Circuit  
Decomposes the given circuit to the native gate set of the device.

Adds the attribute `iqm_calibration_set_id` to the decomposed circuit, with value taken from `self.metadata.architecture.calibration_set_id` if available, otherwise None.

Parameters:  
**circuit** (*Circuit*) – circuit to decompose

Returns:  
decomposed circuit

Return type:  
*Circuit*

validate_circuit(*circuit: AbstractCircuit*) → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Raise an error if `circuit` is not compatible with this device.

Parameters:  
**circuit** (*AbstractCircuit*)

Return type:  
None

validate_operation(*operation: Operation*) → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Raise an error if `operation` is not supported on this device.

Parameters:  
**operation** (*Operation*)

Return type:  
None

validate_move(*operation: Operation*) → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Validate whether the IQMMoveGate is between qubit and resonator registers.

Parameters:  
**operation** (*cirq.Operation*) – Operation to check

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – In case the first argument of the IQMMoveGate is not a qubit, or if the second argument is not a resonator on this device.

Returns:  
None when the IQMMoveGate is used correctly.

Return type:  
None

validate_moves(*circuit: AbstractCircuit*) → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Validate whether the IQMMoveGates are correctly applied in the circuit.

Parameters:  
**circuit** (*cirq.AbstractCircuit*) – The circuit to validate.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the IQMMoveGate is applied incorrectly.

Returns:  
None if the IQMMoveGates are applied correctly.

Return type:  
None

Inheritance

![Inheritance diagram of iqm.cirq_iqm.devices.iqm_device.IQMDevice](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-54292cc4e32d3e64a5a485e4d7f896840b87e931.png)
