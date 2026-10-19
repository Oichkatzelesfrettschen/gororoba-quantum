> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.CircuitExecutionResults.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.CircuitExecutionResults.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7d3ea55f70df899759800983262f5444b1f88a06f838491efde7d13ae0ff96dc.

# CircuitExecutionResults

Module: [`iqm.cpc.compiler.post_process`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.html#module-iqm.cpc.compiler.post_process "iqm.cpc.compiler.post_process")

*class* iqm.cpc.compiler.post_process.CircuitExecutionResults(*circuit_measurement_results*, *readout_mappings*, *sweep_results*, *run_data*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Old Pulla style circuit execution results.

Attributes

|  |  |
|----|----|
| [`circuit_measurement_results`](#iqm.cpc.compiler.post_process.CircuitExecutionResults.circuit_measurement_results "iqm.cpc.compiler.post_process.CircuitExecutionResults.circuit_measurement_results") | Circuit measurement results. |
| [`readout_mappings`](#iqm.cpc.compiler.post_process.CircuitExecutionResults.readout_mappings "iqm.cpc.compiler.post_process.CircuitExecutionResults.readout_mappings") | Readout mappings. |
| [`sweep_results`](#iqm.cpc.compiler.post_process.CircuitExecutionResults.sweep_results "iqm.cpc.compiler.post_process.CircuitExecutionResults.sweep_results") | Raw sweep results. |
| [`run_data`](#iqm.cpc.compiler.post_process.CircuitExecutionResults.run_data "iqm.cpc.compiler.post_process.CircuitExecutionResults.run_data") | Run data. |

Methods

Parameters:  
- **circuit_measurement_results** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]\]\]*)

- **readout_mappings** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]\],* *...\]*)

- **sweep_results** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\]\]*)

- **run_data** ([*RunData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.run.RunData.html#iqm.station_control.interface.models.run.RunData "(in iqm-station-control-client v14.0.0)") *\|* *None*)

circuit_measurement_results*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]\]\]*  
Circuit measurement results.

readout_mappings*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\]\], ...\]*  
Readout mappings.

sweep_results*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]\]*  
Raw sweep results.

run_data*: [RunData](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.run.RunData.html#iqm.station_control.interface.models.run.RunData "(in iqm-station-control-client v14.0.0)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Run data.

Inheritance

![Inheritance diagram of iqm.cpc.compiler.post_process.CircuitExecutionResults](https://docs.iqm.tech/4.7/iqm-pulla/_images/inheritance-bfbc52c7362d1615461059faa55eb25c912c9d50.png)
