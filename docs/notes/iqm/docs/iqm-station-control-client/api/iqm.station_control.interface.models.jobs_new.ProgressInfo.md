> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.ProgressInfo.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.ProgressInfo.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 8076b01ac88fe4506575101e6a39b2e66785e18005e4e143a50bcea845b11b64.

# ProgressInfo

Module: [`iqm.station_control.interface.models.jobs_new`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.html#module-iqm.station_control.interface.models.jobs_new "iqm.station_control.interface.models.jobs_new")

*class* ProgressInfo(*\**, *value*, *max_value*)  
Bases: [`PydanticBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.PydanticBase.html#iqm.station_control.interface.pydantic_base.PydanticBase "iqm.station_control.interface.pydantic_base.PydanticBase")

Progress information about completing an arbitrary task.

Used e.g. for tracking job completion.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.jobs_new.ProgressInfo.model_config "iqm.station_control.interface.models.jobs_new.ProgressInfo.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`value`](#iqm.station_control.interface.models.jobs_new.ProgressInfo.value "iqm.station_control.interface.models.jobs_new.ProgressInfo.value") | Current progress indicator value. |
| [`max_value`](#iqm.station_control.interface.models.jobs_new.ProgressInfo.max_value "iqm.station_control.interface.models.jobs_new.ProgressInfo.max_value") | When we hit this, the task is done. |

Methods

Parameters:  
- **value** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **max_value** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

value*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
Current progress indicator value.

max_value*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
When we hit this, the task is done.

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.jobs_new.ProgressInfo](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-01f23238aff354ec899b1fde1ebf31cbc167c72f.png)
