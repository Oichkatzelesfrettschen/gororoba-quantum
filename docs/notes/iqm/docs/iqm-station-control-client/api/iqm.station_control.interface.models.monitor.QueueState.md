> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.monitor.QueueState.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.monitor.QueueState.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 701921058b9d3baa2e5ede9984acf425655f9fe34ab1ed2d705ebe1ca9e664fc.

# QueueState

Module: [`iqm.station_control.interface.models.monitor`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.monitor.html#module-iqm.station_control.interface.models.monitor "iqm.station_control.interface.models.monitor")

*class* QueueState(*\**, *queue*, *jobs_in_queue*, *completed_jobs*)  
Bases: [`PydanticBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.PydanticBase.html#iqm.station_control.interface.pydantic_base.PydanticBase "iqm.station_control.interface.pydantic_base.PydanticBase")

Describes the state of a single job queue.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.monitor.QueueState.model_config "iqm.station_control.interface.models.monitor.QueueState.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| `queue` |  |
| `jobs_in_queue` |  |
| `completed_jobs` |  |

Methods

Parameters:  
- **queue** ([*JobExecutorStatus*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.JobExecutorStatus.html#iqm.station_control.interface.models.jobs.JobExecutorStatus "iqm.station_control.interface.models.jobs.JobExecutorStatus"))

- **jobs_in_queue** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **completed_jobs** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.monitor.QueueState](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-29763ca55f8b7384c09e8266abe9848408108a5f.png)
