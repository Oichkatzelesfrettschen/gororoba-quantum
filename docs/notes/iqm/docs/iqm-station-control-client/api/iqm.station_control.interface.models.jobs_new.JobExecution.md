> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.JobExecution.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.JobExecution.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a3a51ff7b27134aaebf1c6eda090c05a27b533451c7abfb264970ee2eedb4ad7.

# JobExecution

Module: [`iqm.station_control.interface.models.jobs_new`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.html#module-iqm.station_control.interface.models.jobs_new "iqm.station_control.interface.models.jobs_new")

*class* JobExecution(*\**, *progress*)  
Bases: [`PydanticBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.PydanticBase.html#iqm.station_control.interface.pydantic_base.PydanticBase "iqm.station_control.interface.pydantic_base.PydanticBase")

Progress information about job execution.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.jobs_new.JobExecution.model_config "iqm.station_control.interface.models.jobs_new.JobExecution.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`progress`](#iqm.station_control.interface.models.jobs_new.JobExecution.progress "iqm.station_control.interface.models.jobs_new.JobExecution.progress") | Mapping from label to its progress information (value, max_value). |

Methods

Parameters:  
**progress** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*ProgressInfo*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.ProgressInfo.html#iqm.station_control.interface.models.jobs_new.ProgressInfo "iqm.station_control.interface.models.jobs_new.ProgressInfo")*\]*)

progress*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [ProgressInfo](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.ProgressInfo.html#iqm.station_control.interface.models.jobs_new.ProgressInfo "iqm.station_control.interface.models.jobs_new.ProgressInfo")\]*  
Mapping from label to its progress information (value, max_value).

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.jobs_new.JobExecution](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-c0c44c668723210bb884845b8cac29ba658f7bd8.png)
