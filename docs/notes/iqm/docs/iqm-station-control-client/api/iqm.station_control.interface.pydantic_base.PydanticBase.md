> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.PydanticBase.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.PydanticBase.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 38758e29fd13492bf2f6f2693513c0fd07dc93b13f91ff69a9ea414492465edf.

# PydanticBase

Module: [`iqm.station_control.interface.pydantic_base`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.html#module-iqm.station_control.interface.pydantic_base "iqm.station_control.interface.pydantic_base")

*class* PydanticBase  
Bases: `BaseModel`

Pydantic base model to change the behaviour of pydantic globally.

Note that setting model_config in child classes will merge the configs rather than override this one. [https://docs.pydantic.dev/latest/concepts/config/#change-behaviour-globally](https://docs.pydantic.dev/latest/concepts/config/#change-behaviour-globally)

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.pydantic_base.PydanticBase.model_config "iqm.station_control.interface.pydantic_base.PydanticBase.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |

Methods

&nbsp;

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.interface.pydantic_base.PydanticBase](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-ecb1bb9806991fc45504b52ad998bef832541ed4.png)
