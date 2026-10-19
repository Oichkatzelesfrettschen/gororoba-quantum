> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.dut.DutFieldData.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.dut.DutFieldData.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c98719ea6e1439ab40ea9d2c7e8417fd087688daa1a67fb7f748214f922d69a4.

# DutFieldData

Module: [`iqm.station_control.interface.models.dut`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.dut.html#module-iqm.station_control.interface.models.dut "iqm.station_control.interface.models.dut")

*class* DutFieldData(*\**, *path*, *unit*)  
Bases: [`PydanticBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.PydanticBase.html#iqm.station_control.interface.pydantic_base.PydanticBase "iqm.station_control.interface.pydantic_base.PydanticBase")

A DUT field or path and its unit.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.dut.DutFieldData.model_config "iqm.station_control.interface.models.dut.DutFieldData.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`path`](#iqm.station_control.interface.models.dut.DutFieldData.path "iqm.station_control.interface.models.dut.DutFieldData.path") | DUT field or path. |
| [`unit`](#iqm.station_control.interface.models.dut.DutFieldData.unit "iqm.station_control.interface.models.dut.DutFieldData.unit") | SI unit of the value. |

Methods

Parameters:  
- **path** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **unit** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

path*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
DUT field or path.

unit*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
SI unit of the value. Empty string means the value is dimensionless.

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.dut.DutFieldData](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-a72fe6d381fa09ca4e87b7afd8ad646e78343438.png)
