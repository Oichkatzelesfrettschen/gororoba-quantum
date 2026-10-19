> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.run.RunConfigurationBase.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.run.RunConfigurationBase.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e5b580366a7a444a1cdf0d11efdd30fb55ea0ea72a599646d3a6e7e898f3efbd.

# RunConfigurationBase

Module: [`iqm.station_control.interface.models.run`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.run.html#module-iqm.station_control.interface.models.run "iqm.station_control.interface.models.run")

*class* RunConfigurationBase(*\**, *additional_run_properties=\<factory\>*, *hard_sweeps=\<factory\>*, *components=\<factory\>*, *default_data_parameters=\<factory\>*, *default_sweep_parameters=\<factory\>*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Abstract base class of the run configuration data.

Attributes

|  |  |
|----|----|
| [`additional_run_properties`](#iqm.station_control.interface.models.run.RunConfigurationBase.additional_run_properties "iqm.station_control.interface.models.run.RunConfigurationBase.additional_run_properties") | A free-form dictionary of data, used to store information that does not fall into other categories. |
| [`hard_sweeps`](#iqm.station_control.interface.models.run.RunConfigurationBase.hard_sweeps "iqm.station_control.interface.models.run.RunConfigurationBase.hard_sweeps") | Maps [`SweepBase.return_parameters`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sweep.SweepBase.html#iqm.station_control.interface.models.sweep.SweepBase.return_parameters "iqm.station_control.interface.models.sweep.SweepBase.return_parameters") to "hardware sweep specification" which specifies how the data measured at each spot should be interpreted and shaped. |
| [`components`](#iqm.station_control.interface.models.run.RunConfigurationBase.components "iqm.station_control.interface.models.run.RunConfigurationBase.components") | Components that participate in this run. |
| [`default_data_parameters`](#iqm.station_control.interface.models.run.RunConfigurationBase.default_data_parameters "iqm.station_control.interface.models.run.RunConfigurationBase.default_data_parameters") | The subset of [`SweepBase.return_parameters`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sweep.SweepBase.html#iqm.station_control.interface.models.sweep.SweepBase.return_parameters "iqm.station_control.interface.models.sweep.SweepBase.return_parameters") that were added by default, not by the user. |
| [`default_sweep_parameters`](#iqm.station_control.interface.models.run.RunConfigurationBase.default_sweep_parameters "iqm.station_control.interface.models.run.RunConfigurationBase.default_sweep_parameters") | The subset of [`SweepBase.sweeps`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sweep.SweepBase.html#iqm.station_control.interface.models.sweep.SweepBase.sweeps "iqm.station_control.interface.models.sweep.SweepBase.sweeps") parameters were added by default, not by the user. |

Methods

Parameters:  
- **additional_run_properties** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*)

- **hard_sweeps** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Sweep*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Sweep.html#exa.common.data.parameter.Sweep "(in iqm-exa-common v29.0.0)")*,* *...\]\]\]*)

- **components** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

- **default_data_parameters** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

- **default_sweep_parameters** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

additional_run_properties*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]*  
A free-form dictionary of data, used to store information that does not fall into other categories.

hard_sweeps*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[Sweep](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Sweep.html#exa.common.data.parameter.Sweep "(in iqm-exa-common v29.0.0)"), ...\]\]\]*  
Maps [`SweepBase.return_parameters`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sweep.SweepBase.html#iqm.station_control.interface.models.sweep.SweepBase.return_parameters "iqm.station_control.interface.models.sweep.SweepBase.return_parameters") to “hardware sweep specification” which specifies how the data measured at each spot should be interpreted and shaped. The hard sweep specification is in the same format as [`SweepBase.sweeps`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sweep.SweepBase.html#iqm.station_control.interface.models.sweep.SweepBase.sweeps "iqm.station_control.interface.models.sweep.SweepBase.sweeps"), which means that the returned data can be interpreted as an N-dimensional sweep inside the spot. An empty list is interpreted such that the return parameter is a scalar. The hard sweep specification can also be None, in which case the shape will be whatever the instrument returns.

components*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Components that participate in this run.

default_data_parameters*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
The subset of [`SweepBase.return_parameters`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sweep.SweepBase.html#iqm.station_control.interface.models.sweep.SweepBase.return_parameters "iqm.station_control.interface.models.sweep.SweepBase.return_parameters") that were added by default, not by the user. Used to select which data to analyze and plot.

default_sweep_parameters*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
The subset of [`SweepBase.sweeps`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sweep.SweepBase.html#iqm.station_control.interface.models.sweep.SweepBase.sweeps "iqm.station_control.interface.models.sweep.SweepBase.sweeps") parameters were added by default, not by the user. Used to select which data to analyze and plot.

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.run.RunConfigurationBase](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-27486ca1414e0f6049f2e90b73c4914706933bd8.png)
