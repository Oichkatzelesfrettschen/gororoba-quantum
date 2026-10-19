> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sweep.SweepBase.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sweep.SweepBase.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f6d2308f4b5f8e5d8420533f9b89b8d9135676791511b0ac2902e325e32a96a3.

# SweepBase

Module: [`iqm.station_control.interface.models.sweep`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sweep.html#module-iqm.station_control.interface.models.sweep "iqm.station_control.interface.models.sweep")

*class* SweepBase(*\**, *sweep_id*, *dut_label*, *settings*, *sweeps*, *return_parameters*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Abstract base class of the sweep definition and data.

Attributes

|  |  |
|----|----|
| [`sweep_id`](#iqm.station_control.interface.models.sweep.SweepBase.sweep_id "iqm.station_control.interface.models.sweep.SweepBase.sweep_id") | Unique identifier of the sweep. |
| [`dut_label`](#iqm.station_control.interface.models.sweep.SweepBase.dut_label "iqm.station_control.interface.models.sweep.SweepBase.dut_label") | DUT label of the device being used. |
| [`settings`](#iqm.station_control.interface.models.sweep.SweepBase.settings "iqm.station_control.interface.models.sweep.SweepBase.settings") | A tree representation of the initial settings to set before the sweep. |
| [`sweeps`](#iqm.station_control.interface.models.sweep.SweepBase.sweeps "iqm.station_control.interface.models.sweep.SweepBase.sweeps") | Sweeps that define the swept parameters, i.e. a list of parallel sweeps, where the data values of all sweeps in the tuple are interleaved, and updated simultaneously during the sweep. |
| [`return_parameters`](#iqm.station_control.interface.models.sweep.SweepBase.return_parameters "iqm.station_control.interface.models.sweep.SweepBase.return_parameters") | Parameters that will be queried from devices and saved for each spot (variable-tuple) of the N-dimensional sweep. |

Methods

Parameters:  
- **sweep_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)"))

- **dut_label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **settings** ([*SettingNode*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode "(in iqm-exa-common v29.0.0)"))

- **sweeps** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Sweep*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Sweep.html#exa.common.data.parameter.Sweep "(in iqm-exa-common v29.0.0)")*,* *...\]\]*)

- **return_parameters** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

sweep_id*: [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")*  
Unique identifier of the sweep.

dut_label*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
DUT label of the device being used.

settings*: [SettingNode](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode "(in iqm-exa-common v29.0.0)")*  
A tree representation of the initial settings to set before the sweep.

sweeps*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[Sweep](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Sweep.html#exa.common.data.parameter.Sweep "(in iqm-exa-common v29.0.0)"), ...\]\]*  
Sweeps that define the swept parameters, i.e. a list of parallel sweeps, where the data values of all sweeps in the tuple are interleaved, and updated simultaneously during the sweep.

return_parameters*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Parameters that will be queried from devices and saved for each spot (variable-tuple) of the N-dimensional sweep. Each item must correspond to a setting name in settings.

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.sweep.SweepBase](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-4511a59864050429272a5f938e288c93253fb0a2.png)
