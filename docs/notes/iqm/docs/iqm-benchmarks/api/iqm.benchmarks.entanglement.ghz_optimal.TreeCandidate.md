> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.TreeCandidate.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.TreeCandidate.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d3d1151e83a7ff206e78a9b8f5e9205f8b0967a04c24a1d007ae0112b9346f52.

# iqm.benchmarks.entanglement.ghz_optimal.TreeCandidate

*class* iqm.benchmarks.entanglement.ghz_optimal.TreeCandidate(*root: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *pairs: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]*, *order: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *cost: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*, *stats: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]*, *family: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *rank: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 0*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

One scored spanning tree, as returned by [`rank_ghz_trees()`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.rank_ghz_trees.html#iqm.benchmarks.entanglement.ghz_optimal.rank_ghz_trees "iqm.benchmarks.entanglement.ghz_optimal.rank_ghz_trees").

Attributes

|  |  |
|----|----|
| [`rank`](#iqm.benchmarks.entanglement.ghz_optimal.TreeCandidate.rank "iqm.benchmarks.entanglement.ghz_optimal.TreeCandidate.rank") | Its position in the ranking returned by [`rank_ghz_trees()`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.rank_ghz_trees.html#iqm.benchmarks.entanglement.ghz_optimal.rank_ghz_trees "iqm.benchmarks.entanglement.ghz_optimal.rank_ghz_trees"), `0` being the best. |
| [`root`](#iqm.benchmarks.entanglement.ghz_optimal.TreeCandidate.root "iqm.benchmarks.entanglement.ghz_optimal.TreeCandidate.root") | Qubit holding the initial superposition, i.e. the starting node of the tree. |
| [`pairs`](#iqm.benchmarks.entanglement.ghz_optimal.TreeCandidate.pairs "iqm.benchmarks.entanglement.ghz_optimal.TreeCandidate.pairs") | The `(control, target)` CX pairs, as physical qubit indices, in gate order. |
| [`order`](#iqm.benchmarks.entanglement.ghz_optimal.TreeCandidate.order "iqm.benchmarks.entanglement.ghz_optimal.TreeCandidate.order") | The physical qubits in the order they become entangled, the root first. |
| [`cost`](#iqm.benchmarks.entanglement.ghz_optimal.TreeCandidate.cost "iqm.benchmarks.entanglement.ghz_optimal.TreeCandidate.cost") | Value of the search objective for this candidate; lower is better. |
| [`stats`](#iqm.benchmarks.entanglement.ghz_optimal.TreeCandidate.stats "iqm.benchmarks.entanglement.ghz_optimal.TreeCandidate.stats") | `layers`, `weight`, `idle_cost` and `idle_time`. |
| [`family`](#iqm.benchmarks.entanglement.ghz_optimal.TreeCandidate.family "iqm.benchmarks.entanglement.ghz_optimal.TreeCandidate.family") | Which candidate family produced it, one of `"mst"`, `"subset+dijkstra"`, `"dijkstra"`. |

Methods

|                            |                                       |
|----------------------------|---------------------------------------|
| `__delattr__`(name)        | Implement delattr(self, name).        |
| `__eq__`(other)            | Return self==value.                   |
| `__hash__`()               | Return hash(self).                    |
| `__repr__`()               | Return repr(self).                    |
| `__setattr__`(name, value) | Implement setattr(self, name, value). |

Parameters:  
- **root** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **pairs** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]*)

- **order** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*)

- **cost** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **stats** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*)

- **family** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **rank** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

root*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
Qubit holding the initial superposition, i.e. the starting node of the tree.

pairs*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]*  
The `(control, target)` CX pairs, as physical qubit indices, in gate order.

order*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*  
The physical qubits in the order they become entangled, the root first.

This is the logical-qubit order of the generated circuit: logical index `i` is `order[i]`. Passing it to the transpiler as the initial layout is what keeps the tree edges on real couplings without a layout search.

cost*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*  
Value of the search objective for this candidate; lower is better.

stats*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]*  
`layers`, `weight`, `idle_cost` and `idle_time`.

Type:  
The terms behind [`cost`](#iqm.benchmarks.entanglement.ghz_optimal.TreeCandidate.cost "iqm.benchmarks.entanglement.ghz_optimal.TreeCandidate.cost")

family*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Which candidate family produced it, one of `"mst"`, `"subset+dijkstra"`, `"dijkstra"`.

rank*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")* *= 0*  
Its position in the ranking returned by [`rank_ghz_trees()`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.rank_ghz_trees.html#iqm.benchmarks.entanglement.ghz_optimal.rank_ghz_trees "iqm.benchmarks.entanglement.ghz_optimal.rank_ghz_trees"), `0` being the best.
