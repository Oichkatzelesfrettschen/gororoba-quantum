> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c37b1cf8ae00b53dac61eb23306a37caed9a2278cde919f8861f4ebb44a80271.

# IQMDeviceMetadata

Module: [`iqm.cirq_iqm.devices.iqm_device_metadata`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.devices.iqm_device_metadata.html#module-iqm.cirq_iqm.devices.iqm_device_metadata "iqm.cirq_iqm.devices.iqm_device_metadata")

*class* iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata(*qubits: [Iterable](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")\[NamedQid\]*, *connectivity: [Iterable](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[NamedQid, ...\]\]*, *\**, *operations: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[Gate\], [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[NamedQid, ...\]\]\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *gateset: Gateset \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *resonators: [Iterable](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")\[NamedQid\] = ()*, *architecture: DynamicQuantumArchitecture \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*)  
Bases: `DeviceMetadata`

Hardware metadata for IQM devices.

Parameters:  
- **qubits** (*Iterable\[NamedQid\]*) – qubits on the device

- **connectivity** (*Iterable\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[NamedQid,* *...\]\]*) – qubit connectivity graph of the device

- **operations** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*type*](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")*\[cirq.Gate\],* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[cirq.NamedQid,* *...\]\]\]* *\|* *None*) – Supported quantum operations of the device, mapping op types to their possible loci.

- **gateset** (*cirq.Gateset* *\|* *None*) – Native gateset of the device. If None, a default IQM device gateset will be used.

- **resonators** (*Iterable\[NamedQid\]*) – computational resonators of the device

- **architecture** (*DynamicQuantumArchitecture* *\|* *None*) – architecture from which values of the other arguments were obtained

Attributes

|  |  |
|----|----|
| [`QUBIT_NAME_PREFIX`](#iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata.QUBIT_NAME_PREFIX "iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata.QUBIT_NAME_PREFIX") | prefix for qubit names, to be followed by their numerical index |
| [`RESONATOR_DIMENSION`](#iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata.RESONATOR_DIMENSION "iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata.RESONATOR_DIMENSION") | Dimension abstraction for the resonator Qids |
| [`gateset`](#iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata.gateset "iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata.gateset") | Return the `cirq.Gateset` of supported gates on this device. |
| [`resonator_set`](#iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata.resonator_set "iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata.resonator_set") | Return the set of resonators on the device. |

Methods

|  |  |
|----|----|
| [`from_architecture`](#iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata.from_architecture "iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata.from_architecture") | Return device metadata object created based on dynamic quantum architecture. |
| [`from_qubit_indices`](#iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata.from_qubit_indices "iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata.from_qubit_indices") | Return device metadata object created based on connectivity specified using qubit indices only. |

QUBIT_NAME_PREFIX*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")* *= 'QB'*  
prefix for qubit names, to be followed by their numerical index

RESONATOR_DIMENSION*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")* *= 2*  
Dimension abstraction for the resonator Qids

*property* resonator_set*: [frozenset](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")\[NamedQid\]*  
Return the set of resonators on the device.

Returns:  
Frozenset of resonators on device.

*classmethod* from_architecture(*architecture: DynamicQuantumArchitecture*) → [IQMDeviceMetadata](#iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata "iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata")  
Return device metadata object created based on dynamic quantum architecture.

Parameters:  
**architecture** (*DynamicQuantumArchitecture*)

Return type:  
[*IQMDeviceMetadata*](#iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata "iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata")

*classmethod* from_qubit_indices(*qubit_count: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *connectivity_indices: [Iterable](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")\[[set](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]*, *gateset: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[Gate\]\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [IQMDeviceMetadata](#iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata "iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata")  
Return device metadata object created based on connectivity specified using qubit indices only.

Parameters:  
- **qubit_count** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **connectivity_indices** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]*)

- **gateset** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*type*](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")*\[Gate\]\]* *\|* *None*)

Return type:  
[*IQMDeviceMetadata*](#iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata "iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata")

*property* gateset*: Gateset*  
Return the `cirq.Gateset` of supported gates on this device.

Inheritance

![Inheritance diagram of iqm.cirq_iqm.devices.iqm_device_metadata.IQMDeviceMetadata](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-45d56cdb94eb8de020d69899564c0e64f635805f.png)
