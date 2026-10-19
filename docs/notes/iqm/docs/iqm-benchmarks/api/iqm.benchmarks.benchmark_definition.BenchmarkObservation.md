> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkObservation.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkObservation.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4d877c66848f11745d745d25a5cee1997cd4759dbd989bba3436e8a051b3fe18.

# iqm.benchmarks.benchmark_definition.BenchmarkObservation

*class* iqm.benchmarks.benchmark_definition.BenchmarkObservation(*name: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *value: [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*, *identifier: [BenchmarkObservationIdentifier](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkObservationIdentifier.html#iqm.benchmarks.benchmark_definition.BenchmarkObservationIdentifier "iqm.benchmarks.benchmark_definition.BenchmarkObservationIdentifier")*, *uncertainty: [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Dataclass to store the main results of a single run of a Benchmark.

Parameters:  
- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **value** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"))

- **identifier** ([*BenchmarkObservationIdentifier*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkObservationIdentifier.html#iqm.benchmarks.benchmark_definition.BenchmarkObservationIdentifier "iqm.benchmarks.benchmark_definition.BenchmarkObservationIdentifier"))

- **uncertainty** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)") *\|* *None*)

name  
name of the observation

Type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

value  
value of the observation

Type:  
Any

identifier  
identifier, which should be a string of the qubit layout

Type:  
[iqm.benchmarks.benchmark_definition.BenchmarkObservationIdentifier](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkObservationIdentifier.html#iqm.benchmarks.benchmark_definition.BenchmarkObservationIdentifier "iqm.benchmarks.benchmark_definition.BenchmarkObservationIdentifier")

uncertainty  
uncertainty of the observation

Type:  
Any \| None

Attributes

|  |  |
|----|----|
| [`uncertainty`](#iqm.benchmarks.benchmark_definition.BenchmarkObservation.uncertainty "iqm.benchmarks.benchmark_definition.BenchmarkObservation.uncertainty") |  |
| [`name`](#iqm.benchmarks.benchmark_definition.BenchmarkObservation.name "iqm.benchmarks.benchmark_definition.BenchmarkObservation.name") |  |
| [`value`](#iqm.benchmarks.benchmark_definition.BenchmarkObservation.value "iqm.benchmarks.benchmark_definition.BenchmarkObservation.value") |  |
| [`identifier`](#iqm.benchmarks.benchmark_definition.BenchmarkObservation.identifier "iqm.benchmarks.benchmark_definition.BenchmarkObservation.identifier") |  |

Methods

|                 |                     |
|-----------------|---------------------|
| `__eq__`(other) | Return self==value. |
| `__repr__`()    | Return repr(self).  |
