> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.dut.DutData.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.dut.DutData.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d1464e0bcda25d00df22a85ae640dca0bcee703eab47a8760388b240fecc5fc1.

# DutData

Module: [`iqm.station_control.interface.models.dut`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.dut.html#module-iqm.station_control.interface.models.dut "iqm.station_control.interface.models.dut")

*class* DutData(*\**, *label*, *dut_type*)  
Bases: [`PydanticBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.PydanticBase.html#iqm.station_control.interface.pydantic_base.PydanticBase "iqm.station_control.interface.pydantic_base.PydanticBase")

Represents a Device Under Test, or DUT, for short.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.dut.DutData.model_config "iqm.station_control.interface.models.dut.DutData.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`label`](#iqm.station_control.interface.models.dut.DutData.label "iqm.station_control.interface.models.dut.DutData.label") | DUT label of the device. |
| [`dut_type`](#iqm.station_control.interface.models.dut.DutData.dut_type "iqm.station_control.interface.models.dut.DutData.dut_type") | Type of the device. |

Methods

Parameters:  
- **label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **dut_type** ([*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\['chip',* *'twpa'\]*)

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

label*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
DUT label of the device.

dut_type*: [Literal](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")\['chip', 'twpa'\]*  
Type of the device.

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.dut.DutData](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-3ca65b96e067cf948f5fe74c2b8e32727b528dec.png)
