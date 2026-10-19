> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sweep.SweepDefinition.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sweep.SweepDefinition.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 493cb84d23a7077dc0616a1dd45e38ecb81bff235ef8cbb56252e80ce5752815.

# SweepDefinition

Module: [`iqm.station_control.interface.models.sweep`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sweep.html#module-iqm.station_control.interface.models.sweep "iqm.station_control.interface.models.sweep")

*class* SweepDefinition(*\**, *sweep_id*, *dut_label*, *settings*, *sweeps*, *return_parameters*, *playlist*)  
Bases: [`SweepBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sweep.SweepBase.html#iqm.station_control.interface.models.sweep.SweepBase "iqm.station_control.interface.models.sweep.SweepBase")

The content of the sweep object when creating it.

Attributes

|  |  |
|----|----|
| `qpu_runtime` |  |
| [`playlist`](#iqm.station_control.interface.models.sweep.SweepDefinition.playlist "iqm.station_control.interface.models.sweep.SweepDefinition.playlist") | A `Playlist` that should be uploaded to the controllers. |
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

- **playlist** ([*Playlist*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.playlist.Playlist.html#iqm.models.playlist.playlist.Playlist "(in IQM data definitions v3.1.0)") *\|* *None*)

playlist*: [Playlist](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.playlist.Playlist.html#iqm.models.playlist.playlist.Playlist "(in IQM data definitions v3.1.0)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
A `Playlist` that should be uploaded to the controllers.

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.sweep.SweepDefinition](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-a10da80ef8c91ff882609d6db43e17763f341202.png)
