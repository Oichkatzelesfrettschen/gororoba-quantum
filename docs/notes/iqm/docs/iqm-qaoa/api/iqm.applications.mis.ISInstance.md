> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.ISInstance.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.ISInstance.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 01ec3b919ef64187034ada855090579e7e91d59ed2f98b28c5fc38655e6fdefe.

# ISInstance

Module: [`iqm.applications.mis`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.html#module-iqm.applications.mis "iqm.applications.mis")

*class* iqm.applications.mis.ISInstance(*graph*, *penalty*, *objective*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/mis.py#L63-L208)  
Bases: [`ConstrainedQuadraticInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.qubo.ConstrainedQuadraticInstance.html#iqm.applications.qubo.ConstrainedQuadraticInstance "iqm.applications.qubo.ConstrainedQuadraticInstance")

The instance class for independent set problems on a graph with a custom cost function.

The objective of this class of problems is selecting a subset of nodes in a graph, such that no two nodes in the selected subset are connected by an edge, while minimizing some cost function. This class can be instantiated by giving it a graph, a penalty to the cost function to be incurred for each violation of the constraint (when the problem is converted to QUBO) and an objective function as a `BinaryQuadraticModel`. This class is not intended to be instantiated directly, but rather by its subclasses [`MISInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.MISInstance.html#iqm.applications.mis.MISInstance "iqm.applications.mis.MISInstance") and [`MaximumWeightISInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.MaximumWeightISInstance.html#iqm.applications.mis.MaximumWeightISInstance "iqm.applications.mis.MaximumWeightISInstance"). But if the user does the work of defining their own `objective` function, there is no harm in instantiating an object of [`ISInstance`](#iqm.applications.mis.ISInstance "iqm.applications.mis.ISInstance") directly.

Parameters:  
- **graph** ([*Graph*](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)")) – The graph from which independent sets are to be picked.

- **penalty** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The penalty to be incurred per each edge present in the solution. This is needed when the problem formulation is transformed into QUBO.

- **objective** ([*BinaryQuadraticModel*](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/models.html#dimod.binary.BinaryQuadraticModel "(in D-Wave Quantum Computing Products v9.5.0)")) – The objective function to be minimized by the independent set.

Attributes

|  |  |
|----|----|
| [`graph`](#iqm.applications.mis.ISInstance.graph "iqm.applications.mis.ISInstance.graph") | The graph corresponding to the problem. |

Methods

|  |  |
|----|----|
| [`draw_problem`](#iqm.applications.mis.ISInstance.draw_problem "iqm.applications.mis.ISInstance.draw_problem") | The method to draw an instance of independent set, with the solution highlighted. |
| [`fix_variables`](#iqm.applications.mis.ISInstance.fix_variables "iqm.applications.mis.ISInstance.fix_variables") | A method to fix (assign) some of the problem variables. |

*property* graph*: [Graph](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)")*  
The graph corresponding to the problem.

Equals the graph that was given on initialization of [`MISInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.MISInstance.html#iqm.applications.mis.MISInstance "iqm.applications.mis.MISInstance") and shouldn’t be modified. Instead of modifying the graph, the user should instantiate a new object of [`MISInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.MISInstance.html#iqm.applications.mis.MISInstance "iqm.applications.mis.MISInstance").

fix_variables(*variables*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/mis.py#L106-L154)  
A method to fix (assign) some of the problem variables.

When a variable is fixed to 1, all of its neighboring variables are fixed to 0 (because of the constraints).

Parameters:  
**variables** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*Hashable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Hashable "(in Python v3.11)")*\]* *\|* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*Hashable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Hashable "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – Either an iterable of variables (which get all fixed to the value 1) or a dictionary with keys equal to the variables to fix and whose values are equal to the values to fix them to (either 1 or 0).

Raises:  
- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the user is trying to fix two neighbouring nodes to 1, violating the independence constraint.

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If one of the variables has already been fixed previously to a different value.

Return type:  
None

draw_problem(*solution_bitstring=None*, *seed=None*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/mis.py#L182-L208)  
The method to draw an instance of independent set, with the solution highlighted.

Parameters:  
- **solution_bitstring** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – A bitstring representing a solution to the problem. Selected nodes are represented as 1’s, the other nodes are represented as 0’s. This skips nodes that have been fixed. The full bitstring including the fixed nodes is restored internally by calling [`restore_fixed_variables_bitstring()`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.applications.ProblemInstance.html#iqm.applications.applications.ProblemInstance.restore_fixed_variables_bitstring "iqm.applications.applications.ProblemInstance.restore_fixed_variables_bitstring").

- **seed** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – The seed to derandomize the layout of the graph.

Return type:  
None

Inheritance

![Inheritance diagram of iqm.applications.mis.ISInstance](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-4c6a0b5a34ffff68135d6d946dbaf9831be22025.png)
