> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.run.RunLite.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.run.RunLite.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 40874e12311dbfad54de293912e057fee8c4b0884a2454bc6c7d7c250161888c.

# RunLite

Module: [`iqm.station_control.interface.models.run`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.run.html#module-iqm.station_control.interface.models.run "iqm.station_control.interface.models.run")

*class* RunLite(*\**, *created_timestamp*, *modified_timestamp*, *begin_timestamp*, *end_timestamp*, *run_id*, *username*, *experiment_name*, *experiment_label*, *options=\<factory\>*, *software_version_set_id=0*, *sweep_id*)  
Bases: [`RunBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.run.RunBase.html#iqm.station_control.interface.models.run.RunBase "iqm.station_control.interface.models.run.RunBase"), `_RunTimestamps`

The data of the run stored in the database, excluding run configuration data.

Attributes

|  |  |
|----|----|
| [`sweep_id`](#iqm.station_control.interface.models.run.RunLite.sweep_id "iqm.station_control.interface.models.run.RunLite.sweep_id") | Unique identifier of the associated sweep. |
| `run_id` | Unique identifier of the run. |
| `username` | User who defined the run. |
| `experiment_name` | Identifier of the Experiment (`Experiment.name`). |
| `experiment_label` | Freeform label of the Experiment. |
| `options` | Experiment-specific options or toggles that generated the run. |
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

- **run_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)"))

- **username** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **experiment_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **experiment_label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **options** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*)

- **software_version_set_id** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **sweep_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") *\|* *None*)

sweep_id*: [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Unique identifier of the associated sweep.

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.run.RunLite](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-7c0c450afb5926269eee096668fb9a35f33b70b7.png)
