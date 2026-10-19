> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkRunResult.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkRunResult.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 01bdd372d10d3e3cbcc1cf31759c602ac17b051f8409ab88f3322b26bf46947a.

# iqm.benchmarks.benchmark_definition.BenchmarkRunResult

*class* iqm.benchmarks.benchmark_definition.BenchmarkRunResult(*dataset: Dataset*, *circuits: [Circuits](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.circuit_containers.Circuits.html#iqm.benchmarks.circuit_containers.Circuits "iqm.benchmarks.circuit_containers.Circuits")*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

A dataclass that stores the results of a single run of a Benchmark.

RunResult should contain enough information that the Benchmark can be analyzed based on those results.

Attributes

|            |     |
|------------|-----|
| `dataset`  |     |
| `circuits` |     |

Methods

|                 |                     |
|-----------------|---------------------|
| `__eq__`(other) | Return self==value. |
| `__repr__`()    | Return repr(self).  |

Parameters:  
- **dataset** (*Dataset*)

- **circuits** ([*Circuits*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.circuit_containers.Circuits.html#iqm.benchmarks.circuit_containers.Circuits "iqm.benchmarks.circuit_containers.Circuits"))
