> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.dynamic_quantum_architecture.GateImplementationInfo.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.dynamic_quantum_architecture.GateImplementationInfo.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 687e2466548b602eec060bdf677d41cbc14711b9b7da8962056fe19c541ab8a9.

# GateImplementationInfo

Module: [`iqm.station_control.interface.models.dynamic_quantum_architecture`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.dynamic_quantum_architecture.html#module-iqm.station_control.interface.models.dynamic_quantum_architecture "iqm.station_control.interface.models.dynamic_quantum_architecture")

*class* GateImplementationInfo(*\**, *loci*)  
Bases: [`PydanticBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.PydanticBase.html#iqm.station_control.interface.pydantic_base.PydanticBase "iqm.station_control.interface.pydantic_base.PydanticBase")

Information about an implementation of a quantum gate/operation.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.dynamic_quantum_architecture.GateImplementationInfo.model_config "iqm.station_control.interface.models.dynamic_quantum_architecture.GateImplementationInfo.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`loci`](#iqm.station_control.interface.models.dynamic_quantum_architecture.GateImplementationInfo.loci "iqm.station_control.interface.models.dynamic_quantum_architecture.GateImplementationInfo.loci") | Loci for which this gate implementation has been calibrated. |

Methods

Parameters:  
**loci** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\],* *...\]*)

loci*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[Locus, ...\]*  
Loci for which this gate implementation has been calibrated.

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.dynamic_quantum_architecture.GateImplementationInfo](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-b029f5a37dbfb45f9e8989a1d315cb3d24a74dc5.png)
