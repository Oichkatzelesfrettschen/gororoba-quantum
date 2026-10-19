> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.run.RunBase.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.run.RunBase.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 40fd66502a097f6da9afdc688dc45d909d490c23401cd2578ccf03db700b2dcb.

# RunBase

Module: [`iqm.station_control.interface.models.run`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.run.html#module-iqm.station_control.interface.models.run "iqm.station_control.interface.models.run")

*class* RunBase(*\**, *run_id*, *username*, *experiment_name*, *experiment_label*, *options=\<factory\>*, *software_version_set_id=0*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Abstract base class of run data.

Attributes

|  |  |
|----|----|
| [`software_version_set_id`](#iqm.station_control.interface.models.run.RunBase.software_version_set_id "iqm.station_control.interface.models.run.RunBase.software_version_set_id") | Unique identifier of the software version set of the current Python runtime. |
| [`run_id`](#iqm.station_control.interface.models.run.RunBase.run_id "iqm.station_control.interface.models.run.RunBase.run_id") | Unique identifier of the run. |
| [`username`](#iqm.station_control.interface.models.run.RunBase.username "iqm.station_control.interface.models.run.RunBase.username") | User who defined the run. |
| [`experiment_name`](#iqm.station_control.interface.models.run.RunBase.experiment_name "iqm.station_control.interface.models.run.RunBase.experiment_name") | Identifier of the Experiment (`Experiment.name`). |
| [`experiment_label`](#iqm.station_control.interface.models.run.RunBase.experiment_label "iqm.station_control.interface.models.run.RunBase.experiment_label") | Freeform label of the Experiment. |
| [`options`](#iqm.station_control.interface.models.run.RunBase.options "iqm.station_control.interface.models.run.RunBase.options") | Experiment-specific options or toggles that generated the run. |

Methods

Parameters:  
- **run_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)"))

- **username** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **experiment_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **experiment_label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **options** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*)

- **software_version_set_id** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

run_id*: [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")*  
Unique identifier of the run.

username*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
User who defined the run.

experiment_name*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Identifier of the Experiment (`Experiment.name`).

experiment_label*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Freeform label of the Experiment. As opposed to experiment_name, no core logic relies on this value.

options*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]*  
Experiment-specific options or toggles that generated the run.

software_version_set_id*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")* *= 0*  
Unique identifier of the software version set of the current Python runtime.

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.run.RunBase](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-fe538da201ffaa5fc4fb1191007c31740848a44d.png)
