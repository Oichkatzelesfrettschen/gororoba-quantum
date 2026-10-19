> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.interface.circuit_execution.CircuitCompilationResult.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.interface.circuit_execution.CircuitCompilationResult.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b63cbe243f3ca00773b2ba90b95304cd3ab5fbce29403e0be90a7b6e1c068905.

# CircuitCompilationResult

Module: [`iqm.cpc.interface.circuit_execution`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.interface.circuit_execution.html#module-iqm.cpc.interface.circuit_execution "iqm.cpc.interface.circuit_execution")

*class* iqm.cpc.interface.circuit_execution.CircuitCompilationResult(*playlist*, *readout_mappings*, *settings*, *circuit_metrics*)  
Bases: [`Generic`](https://docs.python.org/3.11/library/typing.html#typing.Generic "(in Python v3.11)")\[`T_settings`\]

Compiled circuit and associated settings returned by CPC to Station Control.

Attributes

|  |  |
|----|----|
| [`playlist`](#iqm.cpc.interface.circuit_execution.CircuitCompilationResult.playlist "iqm.cpc.interface.circuit_execution.CircuitCompilationResult.playlist") | sequence of instruction schedules corresponding to the batch of circuits to be executed |
| [`readout_mappings`](#iqm.cpc.interface.circuit_execution.CircuitCompilationResult.readout_mappings "iqm.cpc.interface.circuit_execution.CircuitCompilationResult.readout_mappings") | For each circuit in the batch, mapping from measurement keys to the names of readout controller result parameters that will hold the measurement results. |
| [`settings`](#iqm.cpc.interface.circuit_execution.CircuitCompilationResult.settings "iqm.cpc.interface.circuit_execution.CircuitCompilationResult.settings") | Station Control settings for circuit execution. |
| [`circuit_metrics`](#iqm.cpc.interface.circuit_execution.CircuitCompilationResult.circuit_metrics "iqm.cpc.interface.circuit_execution.CircuitCompilationResult.circuit_metrics") | metrics describing the circuit and its compilation result for each circuit in the batch |

Methods

Parameters:  
- **playlist** (*Playlist*)

- **readout_mappings** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]\],* *...\]*)

- **settings** (*T_settings*)

- **circuit_metrics** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*CircuitMetrics*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.interface.circuit_execution.CircuitMetrics.html#iqm.cpc.interface.circuit_execution.CircuitMetrics "iqm.cpc.interface.circuit_execution.CircuitMetrics")*,* *...\]*)

playlist*: Playlist*  
sequence of instruction schedules corresponding to the batch of circuits to be executed

readout_mappings*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\]\], ...\]*  
For each circuit in the batch, mapping from measurement keys to the names of readout controller result parameters that will hold the measurement results. If heralding is enabled, qubits which are not measured in the circuit itself but are heralded appear under the reserved key “\_\_herald.

settings*: T_settings*  
Station Control settings for circuit execution. Either a settings tree or a mapping of setting names to their values. If a mapping, must only contain non-None, non-readonly controller settings.

circuit_metrics*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[CircuitMetrics](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.interface.circuit_execution.CircuitMetrics.html#iqm.cpc.interface.circuit_execution.CircuitMetrics "iqm.cpc.interface.circuit_execution.CircuitMetrics"), ...\]*  
metrics describing the circuit and its compilation result for each circuit in the batch

Inheritance

![Inheritance diagram of iqm.cpc.interface.circuit_execution.CircuitCompilationResult](https://docs.iqm.tech/4.7/iqm-pulla/_images/inheritance-eb88fe6b8a3d9b1ed535de6eef6d5b857c2a7d42.png)
