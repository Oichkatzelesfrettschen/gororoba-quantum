> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 84987e2b8c88fdd0a665b7e97fbea3cef160d319d80d33cd459189eb41ead546.

# iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult

*class* iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult(*dataset: ~xarray.core.dataset.Dataset*, *circuits: ~iqm.benchmarks.circuit_containers.Circuits \| None = None*, *plots: dict\[str*, *~matplotlib.figure.Figure\] = \<factory\>*, *observations: list\[~iqm.benchmarks.benchmark_definition.BenchmarkObservation\] = \<factory\>*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

A dataclass storing the results of the analysis.

The result consists of a dataset, plots, and observations. Plots are defined as a dictionary that maps a plot name to a figure. Observations are key-value pairs of data that contain the main results of the benchmark.

Attributes

|                |     |
|----------------|-----|
| `circuits`     |     |
| `dataset`      |     |
| `plots`        |     |
| `observations` |     |

Methods

|  |  |
|----|----|
| `__eq__`(other) | Return self==value. |
| `__repr__`() | Return repr(self). |
| [`from_run_result`](#iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult.from_run_result "iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult.from_run_result")(run) | Creates a new `AnalysisResult` from a `RunResult`. |
| [`plot`](#iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult.plot "iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult.plot")(plot_name) | Plots the given figure. |
| [`plot_all`](#iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult.plot_all "iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult.plot_all")() | Plots all the figures defined for the analysis. |

Parameters:  
- **dataset** (*Dataset*)

- **circuits** ([*Circuits*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.circuit_containers.Circuits.html#iqm.benchmarks.circuit_containers.Circuits "iqm.benchmarks.circuit_containers.Circuits") *\|* *None*)

- **plots** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Figure*](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure "(in Matplotlib v3.11.2)")*\]*)

- **observations** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*BenchmarkObservation*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkObservation.html#iqm.benchmarks.benchmark_definition.BenchmarkObservation "iqm.benchmarks.benchmark_definition.BenchmarkObservation")*\]*)

plot(*plot_name: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*) → [Figure](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure "(in Matplotlib v3.11.2)")  
Plots the given figure.

Parameters:  
**plot_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Name of the figure to be plotted.

Return type:  
[*Figure*](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure "(in Matplotlib v3.11.2)")

plot_all() → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Plots all the figures defined for the analysis.

Return type:  
None

*classmethod* from_run_result(*run: [BenchmarkRunResult](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkRunResult.html#iqm.benchmarks.benchmark_definition.BenchmarkRunResult "iqm.benchmarks.benchmark_definition.BenchmarkRunResult")*) → [BenchmarkAnalysisResult](#iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult "iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult")  
Creates a new `AnalysisResult` from a `RunResult`.

Parameters:  
**run** ([*BenchmarkRunResult*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkRunResult.html#iqm.benchmarks.benchmark_definition.BenchmarkRunResult "iqm.benchmarks.benchmark_definition.BenchmarkRunResult")) – A run for which analysis result is created.

Return type:  
[*BenchmarkAnalysisResult*](#iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult "iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult")
