> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.quantum_volume.ExecutionInfo.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.quantum_volume.ExecutionInfo.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1c9e075c56711b94c0b1ea2d76a66598e04f525d298b1c31c223155308b7293b.

# iqm.benchmarks.quantum_volume.quantum_volume.ExecutionInfo

*class* iqm.benchmarks.quantum_volume.quantum_volume.ExecutionInfo(*backend_name: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *timestamp: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*)  
Bases: [`NamedTuple`](https://docs.python.org/3.11/library/typing.html#typing.NamedTuple "(in Python v3.11)")

Container for execution information of a QV job.

Attributes

|  |  |
|----|----|
| [`backend_name`](#iqm.benchmarks.quantum_volume.quantum_volume.ExecutionInfo.backend_name "iqm.benchmarks.quantum_volume.quantum_volume.ExecutionInfo.backend_name") | Alias for field number 0 |
| [`timestamp`](#iqm.benchmarks.quantum_volume.quantum_volume.ExecutionInfo.timestamp "iqm.benchmarks.quantum_volume.quantum_volume.ExecutionInfo.timestamp") | Alias for field number 1 |

Methods

|  |  |
|----|----|
| `__getnewargs__`() | Return self as a plain tuple. |
| `__new__`(\_cls, backend_name, timestamp) | Create new instance of ExecutionInfo(backend_name, timestamp) |
| `__repr__`() | Return a nicely formatted representation string |
| `_asdict`() | Return a new dict which maps field names to their values. |
| `_make`(iterable) | Make a new ExecutionInfo object from a sequence or iterable |
| `_replace`(\*\*kwds) | Return a new ExecutionInfo object replacing specified fields with new values |

Parameters:  
- **backend_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **timestamp** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

backend_name*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Alias for field number 0

timestamp*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Alias for field number 1
