> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.JobMessage.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.JobMessage.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c6b15fc4686a133452ec300103f618897d0c04f449b95a291ddbb5b7b9280dbe.

# JobMessage

Module: [`iqm.station_control.interface.models.jobs_new`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.html#module-iqm.station_control.interface.models.jobs_new "iqm.station_control.interface.models.jobs_new")

*class* JobMessage(*\**, *source*, *message*)  
Bases: [`PydanticBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.PydanticBase.html#iqm.station_control.interface.pydantic_base.PydanticBase "iqm.station_control.interface.pydantic_base.PydanticBase")

Message log for a job.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.jobs_new.JobMessage.model_config "iqm.station_control.interface.models.jobs_new.JobMessage.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`source`](#iqm.station_control.interface.models.jobs_new.JobMessage.source "iqm.station_control.interface.models.jobs_new.JobMessage.source") | Source of the message. |
| [`message`](#iqm.station_control.interface.models.jobs_new.JobMessage.message "iqm.station_control.interface.models.jobs_new.JobMessage.message") | Content of the message. |

Methods

Parameters:  
- **source** ([*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\['iqm-server',* *'iqm-station-control'\]* *\|* *str*)

- **message** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

source*: Source*  
Source of the message.

message*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Content of the message.

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.jobs_new.JobMessage](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-be163333703dacf75762e98316b5c399a85ab82d.png)
