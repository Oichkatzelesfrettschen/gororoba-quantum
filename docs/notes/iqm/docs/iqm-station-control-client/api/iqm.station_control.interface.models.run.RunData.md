> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.run.RunData.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.run.RunData.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 68fc9cfeabaf344ca21c5cccefdc42a8af1cfb6d4a2a366b397501c69ea85777.

# RunData

Module: [`iqm.station_control.interface.models.run`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.run.html#module-iqm.station_control.interface.models.run "iqm.station_control.interface.models.run")

*class* RunData(*\**, *created_timestamp*, *modified_timestamp*, *begin_timestamp*, *end_timestamp*, *additional_run_properties=\<factory\>*, *hard_sweeps=\<factory\>*, *components=\<factory\>*, *default_data_parameters=\<factory\>*, *default_sweep_parameters=\<factory\>*, *run_id*, *username*, *experiment_name*, *experiment_label*, *options=\<factory\>*, *software_version_set_id=0*, *sweep_data*)  
Bases: [`RunBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.run.RunBase.html#iqm.station_control.interface.models.run.RunBase "iqm.station_control.interface.models.run.RunBase"), [`RunConfigurationBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.run.RunConfigurationBase.html#iqm.station_control.interface.models.run.RunConfigurationBase "iqm.station_control.interface.models.run.RunConfigurationBase"), `_RunTimestamps`

The content of the run and its configuration stored in the database.

Attributes

|  |  |
|----|----|
| [`sweep_data`](#iqm.station_control.interface.models.run.RunData.sweep_data "iqm.station_control.interface.models.run.RunData.sweep_data") | The content of the associated sweep stored in the database. |
| `run_id` | Unique identifier of the run. |
| `username` | User who defined the run. |
| `experiment_name` | Identifier of the Experiment (`Experiment.name`). |
| `experiment_label` | Freeform label of the Experiment. |
| `options` | Experiment-specific options or toggles that generated the run. |
| `additional_run_properties` | A free-form dictionary of data, used to store information that does not fall into other categories. |
| `hard_sweeps` | Maps [`SweepBase.return_parameters`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sweep.SweepBase.html#iqm.station_control.interface.models.sweep.SweepBase.return_parameters "iqm.station_control.interface.models.sweep.SweepBase.return_parameters") to "hardware sweep specification" which specifies how the data measured at each spot should be interpreted and shaped. |
| `components` | Components that participate in this run. |
| `default_data_parameters` | The subset of [`SweepBase.return_parameters`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sweep.SweepBase.html#iqm.station_control.interface.models.sweep.SweepBase.return_parameters "iqm.station_control.interface.models.sweep.SweepBase.return_parameters") that were added by default, not by the user. |
| `default_sweep_parameters` | The subset of [`SweepBase.sweeps`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sweep.SweepBase.html#iqm.station_control.interface.models.sweep.SweepBase.sweeps "iqm.station_control.interface.models.sweep.SweepBase.sweeps") parameters were added by default, not by the user. |
| `created_timestamp` | Time when the object was created in the database. |
| `modified_timestamp` | Time when the object was last modified in the database. |
| `begin_timestamp` | Time when the run began in the station control. |
| `end_timestamp` | Time when the run ended in the station control. |

Methods

Parameters:  
- **created_timestamp** ([*datetime*](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)"))

- **modified_timestamp** ([*datetime*](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)"))

- **begin_timestamp** ([*datetime*](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)"))

- **end_timestamp** ([*datetime*](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)") *\|* *None*)

- **additional_run_properties** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*)

- **hard_sweeps** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Sweep*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Sweep.html#exa.common.data.parameter.Sweep "(in iqm-exa-common v29.0.0)")*,* *...\]\]\]*)

- **components** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

- **default_data_parameters** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

- **default_sweep_parameters** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

- **run_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)"))

- **username** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **experiment_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **experiment_label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **options** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*)

- **software_version_set_id** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **sweep_data** ([*SweepData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sweep.SweepData.html#iqm.station_control.interface.models.sweep.SweepData "iqm.station_control.interface.models.sweep.SweepData"))

sweep_data*: [SweepData](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sweep.SweepData.html#iqm.station_control.interface.models.sweep.SweepData "iqm.station_control.interface.models.sweep.SweepData")*  
The content of the associated sweep stored in the database.

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.run.RunData](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-c4ce5f7a7dc3a3c88be00185d0fbb8cdf0af681d.png)
