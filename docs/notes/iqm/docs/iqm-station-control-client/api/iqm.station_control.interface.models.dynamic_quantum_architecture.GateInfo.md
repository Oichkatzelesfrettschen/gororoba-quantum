> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.dynamic_quantum_architecture.GateInfo.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.dynamic_quantum_architecture.GateInfo.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 eb0b605ae085a439813e8691a924469b22aa25cd29bd2c0d826656f9d376a06b.

# GateInfo

Module: [`iqm.station_control.interface.models.dynamic_quantum_architecture`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.dynamic_quantum_architecture.html#module-iqm.station_control.interface.models.dynamic_quantum_architecture "iqm.station_control.interface.models.dynamic_quantum_architecture")

*class* GateInfo(*\**, *implementations*, *default_implementation*, *override_default_implementation*)  
Bases: [`PydanticBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.PydanticBase.html#iqm.station_control.interface.pydantic_base.PydanticBase "iqm.station_control.interface.pydantic_base.PydanticBase")

Information about a quantum gate/operation.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`loci`](#iqm.station_control.interface.models.dynamic_quantum_architecture.GateInfo.loci "iqm.station_control.interface.models.dynamic_quantum_architecture.GateInfo.loci") | Returns all loci which are available for at least one of the implementations. |
| [`model_config`](#iqm.station_control.interface.models.dynamic_quantum_architecture.GateInfo.model_config "iqm.station_control.interface.models.dynamic_quantum_architecture.GateInfo.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`implementations`](#iqm.station_control.interface.models.dynamic_quantum_architecture.GateInfo.implementations "iqm.station_control.interface.models.dynamic_quantum_architecture.GateInfo.implementations") | Mapping of available implementation names to information about the implementations. |
| [`default_implementation`](#iqm.station_control.interface.models.dynamic_quantum_architecture.GateInfo.default_implementation "iqm.station_control.interface.models.dynamic_quantum_architecture.GateInfo.default_implementation") | Default implementation for the gate. |
| [`override_default_implementation`](#iqm.station_control.interface.models.dynamic_quantum_architecture.GateInfo.override_default_implementation "iqm.station_control.interface.models.dynamic_quantum_architecture.GateInfo.override_default_implementation") | Mapping of loci to implementation names that override `default_implementation` for those loci. |

Methods

|  |  |
|----|----|
| [`get_default_implementation`](#iqm.station_control.interface.models.dynamic_quantum_architecture.GateInfo.get_default_implementation "iqm.station_control.interface.models.dynamic_quantum_architecture.GateInfo.get_default_implementation") | Default implementation of this gate for the given locus. |
| [`override_default_implementation_validator`](#iqm.station_control.interface.models.dynamic_quantum_architecture.GateInfo.override_default_implementation_validator "iqm.station_control.interface.models.dynamic_quantum_architecture.GateInfo.override_default_implementation_validator") | Converts locus keys to tuples if they are encoded as strings. |

Parameters:  
- **implementations** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*GateImplementationInfo*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.dynamic_quantum_architecture.GateImplementationInfo.html#iqm.station_control.interface.models.dynamic_quantum_architecture.GateImplementationInfo "iqm.station_control.interface.models.dynamic_quantum_architecture.GateImplementationInfo")*\]*)

- **default_implementation** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **override_default_implementation** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\],* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

implementations*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [GateImplementationInfo](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.dynamic_quantum_architecture.GateImplementationInfo.html#iqm.station_control.interface.models.dynamic_quantum_architecture.GateImplementationInfo "iqm.station_control.interface.models.dynamic_quantum_architecture.GateImplementationInfo")\]*  
Mapping of available implementation names to information about the implementations.

default_implementation*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Default implementation for the gate.

Used unless overridden by [`override_default_implementation`](#iqm.station_control.interface.models.dynamic_quantum_architecture.GateInfo.override_default_implementation "iqm.station_control.interface.models.dynamic_quantum_architecture.GateInfo.override_default_implementation"), or unless the user requests a specific implementation for a particular gate in the circuit using `iqm.cocos.app.api.request_models.Instruction.implementation`.

override_default_implementation*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[Locus, [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Mapping of loci to implementation names that override `default_implementation` for those loci.

*classmethod* override_default_implementation_validator(*value*)  
Converts locus keys to tuples if they are encoded as strings.

Parameters:  
**value** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"))

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\], [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]

*property* loci*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\], ...\]*  
Returns all loci which are available for at least one of the implementations.

The loci are sorted first based on the first locus component, then the second, etc. The sorting of individual locus components is first done alphabetically based on their non-numeric part, and then components with the same non-numeric part are sorted numerically. An example of loci sorted this way would be:

> (‘QB1’, ‘QB2’), (‘QB2’, ‘COMPR1’), (‘QB2’, ‘QB3’), (‘QB3’, ‘COMPR1’), (‘QB3’, ‘COMPR2’), (‘QB3’, ‘QB1’), (‘QB10’, ‘QB2’),

get_default_implementation(*locus*)  
Default implementation of this gate for the given locus.

Parameters:  
**locus** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]*) – gate locus

Returns:  
Name of the default implementation of this gate for `locus`.

Return type:  
[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.dynamic_quantum_architecture.GateInfo](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-7192b56cea30c92f4848d76127cc013db580e37d.png)
