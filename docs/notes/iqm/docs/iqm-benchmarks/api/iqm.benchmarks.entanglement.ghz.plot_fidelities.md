> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz.plot_fidelities.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz.plot_fidelities.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 150537a2650c6516ea13d3c1cac0a8dd843367e8938df481102e932621c350d9.

# iqm.benchmarks.entanglement.ghz.plot_fidelities

iqm.benchmarks.entanglement.ghz.plot_fidelities(*observations: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[BenchmarkObservation](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkObservation.html#iqm.benchmarks.benchmark_definition.BenchmarkObservation "iqm.benchmarks.benchmark_definition.BenchmarkObservation")\]*, *dataset: Dataset*, *qubit_layouts: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]*) → [Figure](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure "(in Matplotlib v3.11.2)")  
Plots all the fidelities stored in the observations into a single plot of fidelity vs. number of qubits.

Parameters:  
- **observations** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*BenchmarkObservation*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkObservation.html#iqm.benchmarks.benchmark_definition.BenchmarkObservation "iqm.benchmarks.benchmark_definition.BenchmarkObservation")*\]*) – A list of Observations, each assumed to be a fidelity

- **dataset** (*Dataset*) – The experiment dataset containing results and metadata

- **qubit_layouts** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]*) – The list of qubit layouts as given by the user. This is used to name the layouts in order for identification in the plot.

Returns:  
The figure object with the fidelity plot.

Return type:  
[*Figure*](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure "(in Matplotlib v3.11.2)")
