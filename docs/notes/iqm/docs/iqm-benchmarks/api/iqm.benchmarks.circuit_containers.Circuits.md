> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.circuit_containers.Circuits.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.circuit_containers.Circuits.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 382c6f6975de0f1377e53b9ef7f9539beed0cb9ce037b845fad0485ee6372d58.

# iqm.benchmarks.circuit_containers.Circuits

*class* iqm.benchmarks.circuit_containers.Circuits(*benchmark_circuits: list\[~iqm.benchmarks.circuit_containers.BenchmarkCircuit\] = \<factory\>*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Container for all the BenchmarkCircuit that are generated in a single benchmark execution.

Parameters:  
**benchmark_circuits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*BenchmarkCircuit*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.circuit_containers.BenchmarkCircuit.html#iqm.benchmarks.circuit_containers.BenchmarkCircuit "iqm.benchmarks.circuit_containers.BenchmarkCircuit")*\]*)

benchmark_circuits  
List of BenchmarkCircuit contained.

Type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[iqm.benchmarks.circuit_containers.BenchmarkCircuit](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.circuit_containers.BenchmarkCircuit.html#iqm.benchmarks.circuit_containers.BenchmarkCircuit "iqm.benchmarks.circuit_containers.BenchmarkCircuit")\]

Attributes

|  |  |
|----|----|
| [`benchmark_circuits`](#iqm.benchmarks.circuit_containers.Circuits.benchmark_circuits "iqm.benchmarks.circuit_containers.Circuits.benchmark_circuits") |  |

Methods

|  |  |
|----|----|
| `__eq__`(other) | Return self==value. |
| `__getitem__`(key) | Get a benchmark circuit by name. |
| `__repr__`() | Return repr(self). |
| `__setitem__`(key, value) | Set a benchmark circuit with the given key as its name. |
| [`get_benchmark_circuits_by_name`](#iqm.benchmarks.circuit_containers.Circuits.get_benchmark_circuits_by_name "iqm.benchmarks.circuit_containers.Circuits.get_benchmark_circuits_by_name")(name) | Returned the BenchmarkCircuit by name. |

get_benchmark_circuits_by_name(*name: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*) → [BenchmarkCircuit](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.circuit_containers.BenchmarkCircuit.html#iqm.benchmarks.circuit_containers.BenchmarkCircuit "iqm.benchmarks.circuit_containers.BenchmarkCircuit") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Returned the BenchmarkCircuit by name.

Parameters:  
**name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Name of the requested BenchmarkCircuit as a string

Returns:  
The requested BenchmarkCircuit if it exists, None otherwise

Return type:  
[*BenchmarkCircuit*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.circuit_containers.BenchmarkCircuit.html#iqm.benchmarks.circuit_containers.BenchmarkCircuit "iqm.benchmarks.circuit_containers.BenchmarkCircuit") \| None
