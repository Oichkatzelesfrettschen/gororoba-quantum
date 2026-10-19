> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 bcce98a11d6b803106e5ea951136f4aa401d321364124c061df4bacbf1a7b195.

# iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions

*class* iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions(*objective: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") = 'estimated_fidelity'*, *idle_penalty: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") = 1.0*, *depth_penalty: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") = 0.05*, *cz_duration: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") = 4e-08*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

How the tree search trades gate fidelity against circuit depth.

Attributes

|  |  |
|----|----|
| [`cz_duration`](#iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions.cz_duration "iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions.cz_duration") | Duration of one CZ layer in seconds, used by the idle term of `"estimated_fidelity"`. |
| [`depth_penalty`](#iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions.depth_penalty "iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions.depth_penalty") | Cost of one CZ layer for the `"depth_penalty"` objective, in units of `-log fidelity`. |
| [`idle_penalty`](#iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions.idle_penalty "iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions.idle_penalty") | Weight of the idle-decoherence term of the `"estimated_fidelity"` objective. |
| [`objective`](#iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions.objective "iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions.objective") | Which cost to minimize, one of [`TREE_OBJECTIVES`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.TREE_OBJECTIVES.html#iqm.benchmarks.entanglement.ghz_optimal.TREE_OBJECTIVES "iqm.benchmarks.entanglement.ghz_optimal.TREE_OBJECTIVES"). |

Methods

|                            |                                       |
|----------------------------|---------------------------------------|
| `__delattr__`(name)        | Implement delattr(self, name).        |
| `__eq__`(other)            | Return self==value.                   |
| `__hash__`()               | Return hash(self).                    |
| `__repr__`()               | Return repr(self).                    |
| `__setattr__`(name, value) | Implement setattr(self, name, value). |

Parameters:  
- **objective** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **idle_penalty** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **depth_penalty** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **cz_duration** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

objective*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")* *= 'estimated_fidelity'*  
Which cost to minimize, one of [`TREE_OBJECTIVES`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.TREE_OBJECTIVES.html#iqm.benchmarks.entanglement.ghz_optimal.TREE_OBJECTIVES "iqm.benchmarks.entanglement.ghz_optimal.TREE_OBJECTIVES").

`"estimated_fidelity"` scores a candidate by its estimated GHZ infidelity, `gate_cost + idle_penalty * sum(idle time * (1/T1 + 1/T2))`, where `gate_cost` is `_gate_cost()`: the `-log` fidelity of the tree’s CZs plus that of the single-qubit gates around them. `"depth_penalty"` uses the simpler `gate_cost + depth_penalty * number of CZ layers`, which needs no coherence times. `"min_error"` scores by the gate fidelity alone, which is what this routine did before the idle term existed: it selects the same edges as a minimum spanning tree, so it is the setting to use to reproduce older results.

idle_penalty*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")* *= 1.0*  
Weight of the idle-decoherence term of the `"estimated_fidelity"` objective.

`0.0` disables it (leaving the gate fidelity product), values above `1.0` buy depth more aggressively than the T1 and T2 estimate alone would justify.

depth_penalty*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")* *= 0.05*  
Cost of one CZ layer for the `"depth_penalty"` objective, in units of `-log fidelity`.

The scale that matters is what a layer costs the whole register, roughly `num_qubits * layer duration / T2`; on a 45-qubit chip with 100 ns layers and T2 = 40 us that is about `0.05`, which is the default. Values well below it never buy depth, since one layer of a 45-qubit tree is worth several CZ gates’ worth of error.

cz_duration*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")* *= 4e-08*  
Duration of one CZ layer in seconds, used by the idle term of `"estimated_fidelity"`.
