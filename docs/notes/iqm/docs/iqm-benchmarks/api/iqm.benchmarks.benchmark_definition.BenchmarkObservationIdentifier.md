> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkObservationIdentifier.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkObservationIdentifier.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 253a98f94f255df5e8c6db45769c5463824dd72031d02b52438effc622157b8a.

# iqm.benchmarks.benchmark_definition.BenchmarkObservationIdentifier

*class* iqm.benchmarks.benchmark_definition.BenchmarkObservationIdentifier(*qubit_indices: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *custom_identifier: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Identifier for observations for ease of use.

Parameters:  
- **qubit_indices** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]* *\|* *None*)

- **custom_identifier** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*)

qubit_indices  
list containing the indices of the qubits the observation was executed on.

Type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\] \| None

custom_identifier  
optional user-defined string identifier.

Type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| None

Attributes

|  |  |
|----|----|
| [`custom_identifier`](#iqm.benchmarks.benchmark_definition.BenchmarkObservationIdentifier.custom_identifier "iqm.benchmarks.benchmark_definition.BenchmarkObservationIdentifier.custom_identifier") |  |
| [`qubit_indices`](#iqm.benchmarks.benchmark_definition.BenchmarkObservationIdentifier.qubit_indices "iqm.benchmarks.benchmark_definition.BenchmarkObservationIdentifier.qubit_indices") |  |
| [`string_identifier`](#iqm.benchmarks.benchmark_definition.BenchmarkObservationIdentifier.string_identifier "iqm.benchmarks.benchmark_definition.BenchmarkObservationIdentifier.string_identifier") | String version of the qubit indices for ease of use, or custom identifier if given. |

Methods

|                 |                     |
|-----------------|---------------------|
| `__eq__`(other) | Return self==value. |
| `__repr__`()    | Return repr(self).  |

*property* string_identifier*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
String version of the qubit indices for ease of use, or custom identifier if given.

Returns:  
A string of the qubit indices
