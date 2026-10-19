> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sweep.SweepData.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sweep.SweepData.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a00a865f5f3b0e9968a968ed006c0e6522d26dafa8d7e47e72414ebf0df20b01.

# SweepData

Module: [`iqm.station_control.interface.models.sweep`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sweep.html#module-iqm.station_control.interface.models.sweep "iqm.station_control.interface.models.sweep")

*class* SweepData(*\**, *sweep_id*, *dut_label*, *settings*, *sweeps*, *return_parameters*, *created_timestamp*, *modified_timestamp*, *begin_timestamp*, *end_timestamp*, *job_status*)  
Bases: [`SweepBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sweep.SweepBase.html#iqm.station_control.interface.models.sweep.SweepBase "iqm.station_control.interface.models.sweep.SweepBase")

The content of the sweep stored in the database.

The raw data for each spot in the sweep is saved as NumPy arrays, and the complete data for the whole sweep is saved as an `xarray.Dataset` which has `SweepBase.sweeps` as coordinates and `SweepBase.return_parameters` data as `xarray.DataArray` s.

Attributes

|  |  |
|----|----|
| [`created_timestamp`](#iqm.station_control.interface.models.sweep.SweepData.created_timestamp "iqm.station_control.interface.models.sweep.SweepData.created_timestamp") | Time when the object was created in the database. |
| [`modified_timestamp`](#iqm.station_control.interface.models.sweep.SweepData.modified_timestamp "iqm.station_control.interface.models.sweep.SweepData.modified_timestamp") | Time when the object was last modified in the database. |
| [`begin_timestamp`](#iqm.station_control.interface.models.sweep.SweepData.begin_timestamp "iqm.station_control.interface.models.sweep.SweepData.begin_timestamp") | Time when the sweep began in the station control. |
| [`end_timestamp`](#iqm.station_control.interface.models.sweep.SweepData.end_timestamp "iqm.station_control.interface.models.sweep.SweepData.end_timestamp") | Time when the sweep ended in the station control. |
| [`job_status`](#iqm.station_control.interface.models.sweep.SweepData.job_status "iqm.station_control.interface.models.sweep.SweepData.job_status") | Status of sweep execution. |
| `sweep_id` | Unique identifier of the sweep. |
| `dut_label` | DUT label of the device being used. |
| `settings` | A tree representation of the initial settings to set before the sweep. |
| `sweeps` | Sweeps that define the swept parameters, i.e. a list of parallel sweeps, where the data values of all sweeps in the tuple are interleaved, and updated simultaneously during the sweep. |
| `return_parameters` | Parameters that will be queried from devices and saved for each spot (variable-tuple) of the N-dimensional sweep. |

Methods

Parameters:  
- **sweep_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)"))

- **dut_label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **settings** ([*SettingNode*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode "(in iqm-exa-common v29.0.0)"))

- **sweeps** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Sweep*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Sweep.html#exa.common.data.parameter.Sweep "(in iqm-exa-common v29.0.0)")*,* *...\]\]*)

- **return_parameters** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

- **created_timestamp** ([*datetime*](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)"))

- **modified_timestamp** ([*datetime*](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)"))

- **begin_timestamp** ([*datetime*](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)") *\|* *None*)

- **end_timestamp** ([*datetime*](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)") *\|* *None*)

- **job_status** ([*JobExecutorStatus*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.JobExecutorStatus.html#iqm.station_control.interface.models.jobs.JobExecutorStatus "iqm.station_control.interface.models.jobs.JobExecutorStatus"))

created_timestamp*: [datetime](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)")*  
Time when the object was created in the database.

modified_timestamp*: [datetime](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)")*  
Time when the object was last modified in the database.

begin_timestamp*: [datetime](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Time when the sweep began in the station control.

end_timestamp*: [datetime](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Time when the sweep ended in the station control.

job_status*: [JobExecutorStatus](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs.JobExecutorStatus.html#iqm.station_control.interface.models.jobs.JobExecutorStatus "iqm.station_control.interface.models.jobs.JobExecutorStatus")*  
Status of sweep execution.

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.sweep.SweepData](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-e4d17d65cc7b3127ec6927b109e39c1f246b9160.png)
