> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ExperimentConfiguration.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ExperimentConfiguration.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f76de20ef18a939ebd8e2a17e3e4a0516c61cd9ee530f7fc3db8238d22980414.

# ExperimentConfiguration

Module: [`iqm.cpc.core.config`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.html#module-iqm.cpc.core.config "iqm.cpc.core.config")

*class* iqm.cpc.core.config.ExperimentConfiguration(*config*)  
Bases: [`Serializable`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.serializable.Serializable.html#iqm.station_control.interface.serializable.Serializable "(in iqm-station-control-client v14.0.0)")

General configuration for `Experiment` objects.

- Top-level keys `'user'`, `'dut_label'`, `'settings'`, `'components'`, and `'component_groups'`  
  are reserved for the attributes below, and are optional.

- Any other top-level keys generate [`ExperimentDefaultsConfiguration`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ExperimentDefaultsConfiguration.html#iqm.cpc.core.config.ExperimentDefaultsConfiguration "iqm.cpc.core.config.ExperimentDefaultsConfiguration") instances for specific  
  `Experiment` classes.

Parameters:  
**config** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *Any\]*) – Top-level experiment configuration tree.

Attributes

|  |  |
|----|----|
| [`component_names`](#iqm.cpc.core.config.ExperimentConfiguration.component_names "iqm.cpc.core.config.ExperimentConfiguration.component_names") | Property to return list of component names in experiment configuration. |
| [`id`](#iqm.cpc.core.config.ExperimentConfiguration.id "iqm.cpc.core.config.ExperimentConfiguration.id") | Unique identifier for this ExperimentConfiguration. |
| [`user`](#iqm.cpc.core.config.ExperimentConfiguration.user "iqm.cpc.core.config.ExperimentConfiguration.user") | Username. |
| [`dut_label`](#iqm.cpc.core.config.ExperimentConfiguration.dut_label "iqm.cpc.core.config.ExperimentConfiguration.dut_label") | DUT label. |
| [`components`](#iqm.cpc.core.config.ExperimentConfiguration.components "iqm.cpc.core.config.ExperimentConfiguration.components") | Mapping from chip component names to the station control controllers they use. |
| [`component_groups`](#iqm.cpc.core.config.ExperimentConfiguration.component_groups "iqm.cpc.core.config.ExperimentConfiguration.component_groups") | Mapping from component group names to their definitions. |
| [`controllers`](#iqm.cpc.core.config.ExperimentConfiguration.controllers "iqm.cpc.core.config.ExperimentConfiguration.controllers") | Controller settings. |
| [`gate_definitions`](#iqm.cpc.core.config.ExperimentConfiguration.gate_definitions "iqm.cpc.core.config.ExperimentConfiguration.gate_definitions") | Defined quantum operations |
| [`gates`](#iqm.cpc.core.config.ExperimentConfiguration.gates "iqm.cpc.core.config.ExperimentConfiguration.gates") | Gate implementation calibration data. |
| [`characterization`](#iqm.cpc.core.config.ExperimentConfiguration.characterization "iqm.cpc.core.config.ExperimentConfiguration.characterization") | Experiment characterization data. |
| [`stages`](#iqm.cpc.core.config.ExperimentConfiguration.stages "iqm.cpc.core.config.ExperimentConfiguration.stages") | The stage settings data. |

Methods

|  |  |
|----|----|
| [`add_conventional_controller_mapping`](#iqm.cpc.core.config.ExperimentConfiguration.add_conventional_controller_mapping "iqm.cpc.core.config.ExperimentConfiguration.add_conventional_controller_mapping") | Add conventional controller mapping if `controller_mapping` is `"qpu_convention"`. |
| [`deserialize`](#iqm.cpc.core.config.ExperimentConfiguration.deserialize "iqm.cpc.core.config.ExperimentConfiguration.deserialize") | Reconstruct an instance from a dictionary payload. |
| [`filter_components`](#iqm.cpc.core.config.ExperimentConfiguration.filter_components "iqm.cpc.core.config.ExperimentConfiguration.filter_components") | Helper method for filtering components based on what operations they have defined. |
| [`register_gate_implementation`](#iqm.cpc.core.config.ExperimentConfiguration.register_gate_implementation "iqm.cpc.core.config.ExperimentConfiguration.register_gate_implementation") | Register a new gate implementation for this session. |
| [`serialize`](#iqm.cpc.core.config.ExperimentConfiguration.serialize "iqm.cpc.core.config.ExperimentConfiguration.serialize") | Serialize the object instance into a dictionary payload. |
| [`set_calibration_data_for_gate_implementation`](#iqm.cpc.core.config.ExperimentConfiguration.set_calibration_data_for_gate_implementation "iqm.cpc.core.config.ExperimentConfiguration.set_calibration_data_for_gate_implementation") | Set calibration data for this session. |
| [`set_gate_implementation_as_default`](#iqm.cpc.core.config.ExperimentConfiguration.set_gate_implementation_as_default "iqm.cpc.core.config.ExperimentConfiguration.set_gate_implementation_as_default") | Set this gate implementation as default for this session. |
| [`validate_controllers`](#iqm.cpc.core.config.ExperimentConfiguration.validate_controllers "iqm.cpc.core.config.ExperimentConfiguration.validate_controllers") | Validate controller maps against controller names in executor\`. |

id  
Unique identifier for this ExperimentConfiguration.

user*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Username.

dut_label*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
DUT label.

components*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]*  
Mapping from chip component names to the station control controllers they use.

component_groups*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [ComponentGroup](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ComponentGroup.html#iqm.cpc.core.config.ComponentGroup "iqm.cpc.core.config.ComponentGroup")\]*  
Mapping from component group names to their definitions.

controllers*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]*  
Controller settings.

gate_definitions  
Defined quantum operations

gates*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]*  
Gate implementation calibration data.

characterization*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]*  
Experiment characterization data.

stages*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]*  
The stage settings data.

add_conventional_controller_mapping(*executor*)  
Add conventional controller mapping if `controller_mapping` is `"qpu_convention"`.

If the configuration is set to follow the standard QPU controller naming convention, extend the [`controllers`](#iqm.cpc.core.config.ExperimentConfiguration.controllers "iqm.cpc.core.config.ExperimentConfiguration.controllers") and [`component_groups`](#iqm.cpc.core.config.ExperimentConfiguration.component_groups "iqm.cpc.core.config.ExperimentConfiguration.component_groups") based on the convention. Components given explicitly have priority.

The convention is that components map their functions to controller names with the following pattern:

For qubits:

- `drive: <qubit_name>__drive`

- `flux: <qubit_name>__flux`

For couplers:

- `flux: <coupler_name>__flux`

For probelines:

- `readout: <probeline_name>__readout`

- `twpa: <probeline_name>__twpa`

Parameters:  
**executor** ([*ExecutorInterface*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.executor_interface.ExecutorInterface.html#iqm.station_control.interface.executor_interface.ExecutorInterface "(in iqm-station-control-client v14.0.0)")) – Interface for managing and executing quantum jobs on the backend.

Return type:  
None

validate_controllers(*executor*)  
Validate controller maps against controller names in executor\`.

Parameters:  
**executor** ([*ExecutorInterface*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.executor_interface.ExecutorInterface.html#iqm.station_control.interface.executor_interface.ExecutorInterface "(in iqm-station-control-client v14.0.0)")) – Interface for managing and executing quantum jobs on the backend.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – if the executor does not have a controller required by the naming convention.

Return type:  
None

*property* component_names*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Property to return list of component names in experiment configuration.

filter_components(*\*filter_groups*)  
Helper method for filtering components based on what operations they have defined.

The user can define several groups of operation requirements. Requirement groups can contain requirements that are either of the type `str` or any function of the type `Callable[str, bool]`. If a `str` requirement is given, it will be interpreted as a check whether this particular operation name is defined for a given component.

For example, the group `[lambda c: c != 'readout, 'flux']` resolves to the components that do not have a `readout` operation but have a `flux` operation.

Requirement groups that contain just one requirement (of either type) can be given as a plain value instead of wrapping it into a list.

Parameters:  
**\*filter_groups** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *Callable\[...,* [*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")*\]* *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *Callable\[...,* [*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")*\]\]*) – requirement groups.

Returns:  
- Tuple of filtered components corresponding to the provided filter_groups.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\] \| [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\], …\]

register_gate_implementation(*gate_name*, *impl_name*, *impl_class*, *\**, *set_as_default=False*, *quantum_op=None*)  
Register a new gate implementation for this session. See `register_implementation()`.

Parameters:  
- **gate_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **impl_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **impl_class** ([*type*](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")*\[*[*GateImplementation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "(in iqm.pulse v15.0.0)")*\]*)

- **set_as_default** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **quantum_op** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "(in iqm.pulse v15.0.0)") *\|* *None*)

Return type:  
None

set_calibration_data_for_gate_implementation(*gate_name*, *impl_name*, *calib_data*)  
Set calibration data for this session.

Parameters:  
- **gate_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **impl_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **calib_data** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\],* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*)

Return type:  
None

set_gate_implementation_as_default(*gate_name*, *impl_name*)  
Set this gate implementation as default for this session.

Parameters:  
- **gate_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **impl_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

Return type:  
None

serialize()  
Serialize the object instance into a dictionary payload.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

*classmethod* deserialize(*data*)  
Reconstruct an instance from a dictionary payload.

Parameters:  
**data** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*)

Return type:  
[*ExperimentConfiguration*](#iqm.cpc.core.config.ExperimentConfiguration "iqm.cpc.core.config.ExperimentConfiguration")

Inheritance

![Inheritance diagram of iqm.cpc.core.config.ExperimentConfiguration](https://docs.iqm.tech/4.7/iqm-pulla/_images/inheritance-24855645d8d6f62d5d8e25c301ed3d2bc9b3234a.png)
