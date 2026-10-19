> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.JobError.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.JobError.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 89027fe9531557d678a6dabb8833616e226b98aa2eb9709b147864517b689ce0.

# JobError

Module: [`iqm.station_control.interface.models.jobs`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.html#module-iqm.station_control.interface.models.jobs "iqm.station_control.interface.models.jobs")

*class* JobError(*\**, *full_error_log*, *user_error_message*)  
Bases: [`PydanticBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.PydanticBase.html#iqm.station_control.interface.pydantic_base.PydanticBase "iqm.station_control.interface.pydantic_base.PydanticBase")

Error message for a job.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.jobs.JobError.model_config "iqm.station_control.interface.models.jobs.JobError.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`full_error_log`](#iqm.station_control.interface.models.jobs.JobError.full_error_log "iqm.station_control.interface.models.jobs.JobError.full_error_log") | Full error message for logging. |
| [`user_error_message`](#iqm.station_control.interface.models.jobs.JobError.user_error_message "iqm.station_control.interface.models.jobs.JobError.user_error_message") | Short, human-readable error message for users. |

Methods

Parameters:  
- **full_error_log** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **user_error_message** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

full_error_log*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Full error message for logging.

user_error_message*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Short, human-readable error message for users.

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.jobs.JobError](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-d9b7f633a8daf6d4d34f90c02a071742fc533c1f.png)
