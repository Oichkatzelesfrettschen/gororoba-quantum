> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.graph_states.plot_max_negativities.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.graph_states.plot_max_negativities.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1e0e5f92f251ab820674cd802fba7529c283d768352388d71dec6334ed95a95b.

# iqm.benchmarks.entanglement.graph_states.plot_max_negativities

iqm.benchmarks.entanglement.graph_states.plot_max_negativities(*negativities: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]\]*, *backend_name: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *qubit_names: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*, *timestamp: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *tomography: [TomographyType](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.graph_states.TomographyType.html#iqm.benchmarks.entanglement.graph_states.TomographyType "iqm.benchmarks.entanglement.graph_states.TomographyType")*, *num_shots: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *num_bootstraps: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *num_RM_samples: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *num_MoMs_samples: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Figure](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure "(in Matplotlib v3.11.2)")\]  
Plots the maximum negativity for each corresponding pair of qubits.

Parameters:  
- **negativities** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]\]*) – A dictionary (str qubit keys) of dictionaries (keys “value”/”uncertainty”) of negativities (float) to plot.

- **backend_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The name of the backend for the corresponding experiment.

- **qubit_names** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – A dictionary of qubit names corresponding to qubit indices.

- **timestamp** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The timestamp of the corresponding experiment.

- **tomography** ([*TomographyType*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.graph_states.TomographyType.html#iqm.benchmarks.entanglement.graph_states.TomographyType "iqm.benchmarks.entanglement.graph_states.TomographyType")) – The type of tomography that was used.

- **num_shots** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of shots used in the corresponding experiment.

- **num_bootstraps** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – The number of bootstraps used if tomography corresponds to state tomography.

- **num_RM_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – The number of randomized measurement samples used if tomography corresponds to shadow tomography.

- **num_MoMs_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – The number of Median of Means samples per randomized measurement used if tomography corresponds to shadow tomography.

Returns:  
The figure label and the max negativities plot figure.

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Figure*](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure "(in Matplotlib v3.11.2)")\]
