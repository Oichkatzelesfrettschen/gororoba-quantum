> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.JobArtifactInfo.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.JobArtifactInfo.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6219607e7ed7e0704a9bc7c91a923eda13bbff21cea3d5112e6297ad0a7f56fd.

# JobArtifactInfo

Module: [`iqm.station_control.interface.models.jobs_new`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.html#module-iqm.station_control.interface.models.jobs_new "iqm.station_control.interface.models.jobs_new")

*class* JobArtifactInfo(*\**, *type*)  
Bases: [`PydanticBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.PydanticBase.html#iqm.station_control.interface.pydantic_base.PydanticBase "iqm.station_control.interface.pydantic_base.PydanticBase")

Description of an artifact for a job, currently available on the server.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.jobs_new.JobArtifactInfo.model_config "iqm.station_control.interface.models.jobs_new.JobArtifactInfo.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`type`](#iqm.station_control.interface.models.jobs_new.JobArtifactInfo.type "iqm.station_control.interface.models.jobs_new.JobArtifactInfo.type") | Name of the available artifact type. |

Methods

Parameters:  
**type** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

type*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Name of the available artifact type.

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.jobs_new.JobArtifactInfo](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-16604d73ee796bc76f627512aee1f0ec3a07bb7e.png)
