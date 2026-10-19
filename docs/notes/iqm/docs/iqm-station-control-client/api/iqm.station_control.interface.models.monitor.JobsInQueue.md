> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.monitor.JobsInQueue.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.monitor.JobsInQueue.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a7425ba8c6536a8b8b706b683d8caad77da8a5f03589e56836ed3b49bc843674.

# JobsInQueue

Module: [`iqm.station_control.interface.models.monitor`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.monitor.html#module-iqm.station_control.interface.models.monitor "iqm.station_control.interface.models.monitor")

*class* JobsInQueue(*\**, *jobs=\[\]*, *job_count=0*)  
Bases: [`PydanticBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.PydanticBase.html#iqm.station_control.interface.pydantic_base.PydanticBase "iqm.station_control.interface.pydantic_base.PydanticBase")

List of jobs in a particular queue, corresponding to some job state.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.monitor.JobsInQueue.model_config "iqm.station_control.interface.models.monitor.JobsInQueue.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| `jobs` |  |
| `job_count` |  |

Methods

Parameters:  
- **jobs** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*JobStateTimestamp*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.monitor.JobStateTimestamp.html#iqm.station_control.interface.models.monitor.JobStateTimestamp "iqm.station_control.interface.models.monitor.JobStateTimestamp")*\]*)

- **job_count** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.monitor.JobsInQueue](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-2e0bf058c733908b65add550ea0f66ba9e900eb8.png)
