> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.run_result.RunResult.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.run_result.RunResult.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4a43e1daf8a4f858a07f5f4478cfcee1df5a950abe98ab5c1086d4f2a1b782d8.

# RunResult

Module: [`iqm.cpc.core.run_result`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.run_result.html#module-iqm.cpc.core.run_result "iqm.cpc.core.run_result")

*class* iqm.cpc.core.run_result.RunResult(*run_data*, *dataset*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

The definitive data structure to represent the execution results of an Experiment.

The run result contains the full dataset and run data.

Attributes

|  |  |
|----|----|
| [`run_data`](#iqm.cpc.core.run_result.RunResult.run_data "iqm.cpc.core.run_result.RunResult.run_data") | Information that defines the Experiment run, after it was executed. |
| [`dataset`](#iqm.cpc.core.run_result.RunResult.dataset "iqm.cpc.core.run_result.RunResult.dataset") | Xarray dataset that has the raw and post-processed data of an execution. |

Methods

Parameters:  
- **run_data** ([*RunData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.run.RunData.html#iqm.station_control.interface.models.run.RunData "(in iqm-station-control-client v14.0.0)"))

- **dataset** (*Dataset*)

run_data*: [RunData](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.run.RunData.html#iqm.station_control.interface.models.run.RunData "(in iqm-station-control-client v14.0.0)")*  
Information that defines the Experiment run, after it was executed.

dataset*: Dataset*  
Xarray dataset that has the raw and post-processed data of an execution.

Inheritance

![Inheritance diagram of iqm.cpc.core.run_result.RunResult](https://docs.iqm.tech/4.7/iqm-pulla/_images/inheritance-2dcdf03e4a8437cf0c27bd659d963cd25c1bc8de.png)
