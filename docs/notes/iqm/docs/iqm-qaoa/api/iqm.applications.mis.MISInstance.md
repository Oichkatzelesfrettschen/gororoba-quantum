> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.MISInstance.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.MISInstance.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 add0cfcbc38096dba0f53d998901fc425c00068aef1ee8d6cd59284c42450a6a.

# MISInstance

Module: [`iqm.applications.mis`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.html#module-iqm.applications.mis "iqm.applications.mis")

*class* iqm.applications.mis.MISInstance(*graph*, *penalty=1*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/mis.py#L211-L318)  
Bases: [`ISInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.ISInstance.html#iqm.applications.mis.ISInstance "iqm.applications.mis.ISInstance")

The instance class for maximum independent set problems.

The maximum independent set problem refers to finding the largest subset of nodes of a graph, such that no nodes in the subset are connected by an edge. It is completely equivalent to finding the largest clique on the complement graph. The class is initialized by initializing its parent class [`ISInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.ISInstance.html#iqm.applications.mis.ISInstance "iqm.applications.mis.ISInstance") with a simple objective function (aiming at maximizing the number of “selected” nodes).

Parameters:  
- **graph** ([*Graph*](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)")) – The [`Graph`](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)") describing the MIS problem.

- **penalty** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – The penalty to be incurred per each edge present in the solution, sometimes referred to as \\\lambda\\ in the literature. The higher it is, the less likely the algorithm is to include an edge in the solution. It needs to be set above 1 to insure that the solution is a maximum independent set. It’s typically set at 2. At 1, the correct solution will be degenerate with non-independent sets.

Attributes

|  |  |
|----|----|
| [`best_quality`](#iqm.applications.mis.MISInstance.best_quality "iqm.applications.mis.MISInstance.best_quality") | The best quality for the MIS problem. |
| [`highest_quality_bitstrings`](#iqm.applications.mis.MISInstance.highest_quality_bitstrings "iqm.applications.mis.MISInstance.highest_quality_bitstrings") | The worst bitstring for the MIS problem, determined trivially. |
| [`lower_bound`](#iqm.applications.mis.MISInstance.lower_bound "iqm.applications.mis.MISInstance.lower_bound") | The lowest quality value among all possible bitstrings. |
| [`lowest_quality_bitstrings`](#iqm.applications.mis.MISInstance.lowest_quality_bitstrings "iqm.applications.mis.MISInstance.lowest_quality_bitstrings") | The best bitstrings for the MIS problem. |

Methods

|  |  |
|----|----|
| [`fix_constraint_violation_bitstring`](#iqm.applications.mis.MISInstance.fix_constraint_violation_bitstring "iqm.applications.mis.MISInstance.fix_constraint_violation_bitstring") | Postprocessing function that fixes a single bitstring, making it satisfy the constraints. |
| [`solve_with_bron_kerbosch`](#iqm.applications.mis.MISInstance.solve_with_bron_kerbosch "iqm.applications.mis.MISInstance.solve_with_bron_kerbosch") | Solve the MIS problem using Bron-Kerbosch algorithm and save some properties of the solution. |

*property* best_quality*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*  
The best quality for the MIS problem.

Can be calculated together with other properties of the solution using the exhaustive Bron-Kerbosch algorithm.

*property* lowest_quality_bitstrings*: [set](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
The best bitstrings for the MIS problem.

Can be calculated together with other properties of the solution using the exhaustive Bron-Kerbosch algorithm.

*property* lower_bound*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*  
The lowest quality value among all possible bitstrings.

Can be calculated together with other properties of the solution using the exhaustive Bron-Kerbosch algorithm.

solve_with_bron_kerbosch()[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/mis.py#L270-L277)  
Solve the MIS problem using Bron-Kerbosch algorithm and save some properties of the solution.

Return type:  
None

*property* highest_quality_bitstrings*: [set](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
The worst bitstring for the MIS problem, determined trivially.

The worst bitstring satisfying all constraints is always selecting no nodes.

fix_constraint_violation_bitstring(*bit_str*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/mis.py#L287-L318)  
Postprocessing function that fixes a single bitstring, making it satisfy the constraints.

It works in the following way:

1.  Get the subgraph induced by the bitstring `bit_str`.

2.  Find the node with the highest degree, with ties broken at random.

3.  Remove the node from the subgraph (i.e., flip the corresponding bit from “1” to “0”).

4.  Repeat 2-3 until the subgraph contains no edges.

5.  Return the bitstring corresponding to the remaining subgraph (which is an independent subset of the original graph).

For `penalty = 1`, this guarantees that the output bitstring has energy at least as low as the input bitstring. For `penalty > 1`, the energy is expected to be even lower.

Parameters:  
**bit_str** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The bitstring to be modified to satisfy the independence constraint.

Returns:  
The modified bitstring, corresponding to an independent set of the problem graph.

Return type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

Inheritance

![Inheritance diagram of iqm.applications.mis.MISInstance](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-600136b5a74b934d520a16435cd4d8441862501a.png)
