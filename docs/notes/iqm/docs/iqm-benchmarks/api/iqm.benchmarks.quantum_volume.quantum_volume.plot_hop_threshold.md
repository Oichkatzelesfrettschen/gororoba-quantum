> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.quantum_volume.plot_hop_threshold.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.quantum_volume.plot_hop_threshold.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 9c1f9ccd04cf160822113ce30369165d19c82635088998815fcc4d1e24aa7277.

# iqm.benchmarks.quantum_volume.quantum_volume.plot_hop_threshold

iqm.benchmarks.quantum_volume.quantum_volume.plot_hop_threshold(*qubits: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *depth: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *qv_result: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]*, *qv_results_type: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *num_sigmas: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *execution_info: [ExecutionInfo](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.quantum_volume.ExecutionInfo.html#iqm.benchmarks.quantum_volume.quantum_volume.ExecutionInfo "iqm.benchmarks.quantum_volume.quantum_volume.ExecutionInfo")*, *in_volumetric: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*, *plot_rem: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Figure](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure "(in Matplotlib v3.11.2)")\]  
Generate the figure representing each HOP, the average and the threshold.

Parameters:  
- **qubits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – The list of qubit labels.

- **depth** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The depth of the QV circuit.

- **qv_result** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*) – The list of HOP.

- **qv_results_type** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Whether results come from vanilla or DD execution.

- **num_sigmas** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of sigmas to plot.

- **execution_info** ([*ExecutionInfo*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.quantum_volume.ExecutionInfo.html#iqm.benchmarks.quantum_volume.quantum_volume.ExecutionInfo "iqm.benchmarks.quantum_volume.quantum_volume.ExecutionInfo")) – Container with backend name and execution timestamp.

- **in_volumetric** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether the QV benchmark is being executed in the context of a volumetric benchmark.

- **plot_rem** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether the plot corresponds to REM corrected data.

Returns:  
The name of the figure. The figure.

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Figure*](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure "(in Matplotlib v3.11.2)")\]
