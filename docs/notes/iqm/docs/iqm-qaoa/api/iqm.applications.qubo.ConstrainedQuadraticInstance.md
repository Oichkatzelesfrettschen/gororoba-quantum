> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.qubo.ConstrainedQuadraticInstance.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.qubo.ConstrainedQuadraticInstance.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b247d7c90b589d6688326c2fdbc0305470a27465f77acb92c4a5e88ea55afd40.

# ConstrainedQuadraticInstance

Module: [`iqm.applications.qubo`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.qubo.html#module-iqm.applications.qubo "iqm.applications.qubo")

*class* iqm.applications.qubo.ConstrainedQuadraticInstance(*cqm*, *penalty=1.0*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/qubo.py#L297-L588)  
Bases: [`ProblemInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.applications.ProblemInstance.html#iqm.applications.applications.ProblemInstance "iqm.applications.applications.ProblemInstance")

A class for constrainted quadratic binary problems.

The class saves the problem as a [`ConstrainedQuadraticModel`](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/models.html#dimod.ConstrainedQuadraticModel "(in D-Wave Quantum Computing Products v9.5.0)") and uses this object for its various methods. When the problem needs to be transformed into a QUBO, a private method `_recalculate_bqm()` is used to return a `BinaryQuadraticModel` formulation of the problem, making the constraints soft and penalizing their breaking with [`penalty`](#iqm.applications.qubo.ConstrainedQuadraticInstance.penalty "iqm.applications.qubo.ConstrainedQuadraticInstance.penalty").

Parameters:  
- **cqm** ([*ConstrainedQuadraticModel*](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/models.html#dimod.ConstrainedQuadraticModel "(in D-Wave Quantum Computing Products v9.5.0)")) – The problem encoded as a [`ConstrainedQuadraticModel`](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/models.html#dimod.ConstrainedQuadraticModel "(in D-Wave Quantum Computing Products v9.5.0)"), passed over from a subclass.

- **penalty** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – The numerical penalty incurred by violating each constraint of the problem, to be used when the problem is transformed into a BQM.

Attributes

|  |  |
|----|----|
| [`bqm`](#iqm.applications.qubo.ConstrainedQuadraticInstance.bqm "iqm.applications.qubo.ConstrainedQuadraticInstance.bqm") | The BQM representation of the problem, penalizing constraint violation. |
| [`cqm`](#iqm.applications.qubo.ConstrainedQuadraticInstance.cqm "iqm.applications.qubo.ConstrainedQuadraticInstance.cqm") | The [`ConstrainedQuadraticModel`](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/models.html#dimod.ConstrainedQuadraticModel "(in D-Wave Quantum Computing Products v9.5.0)") representation of the problem instance. |
| [`dim`](#iqm.applications.qubo.ConstrainedQuadraticInstance.dim "iqm.applications.qubo.ConstrainedQuadraticInstance.dim") | The dimension of the problem (i.e., the number of binary variables). |
| [`penalty`](#iqm.applications.qubo.ConstrainedQuadraticInstance.penalty "iqm.applications.qubo.ConstrainedQuadraticInstance.penalty") | The penalty for breaking the constraints. |
| [`qubo_graph`](#iqm.applications.qubo.ConstrainedQuadraticInstance.qubo_graph "iqm.applications.qubo.ConstrainedQuadraticInstance.qubo_graph") | The QUBO graph of the problem instance. |
| [`qubo_matrix`](#iqm.applications.qubo.ConstrainedQuadraticInstance.qubo_matrix "iqm.applications.qubo.ConstrainedQuadraticInstance.qubo_matrix") | The QUBO matrix of the problem instance. |

Methods

|  |  |
|----|----|
| [`constraints_checker`](#iqm.applications.qubo.ConstrainedQuadraticInstance.constraints_checker "iqm.applications.qubo.ConstrainedQuadraticInstance.constraints_checker") | Checks whether the constrains of the problem are satisfied. |
| [`fix_constraint_violation`](#iqm.applications.qubo.ConstrainedQuadraticInstance.fix_constraint_violation "iqm.applications.qubo.ConstrainedQuadraticInstance.fix_constraint_violation") | Take a dictionary and change the bitstrings in it in some minimal way so that they satisfy the constraints. |
| [`fix_constraint_violation_bitstring`](#iqm.applications.qubo.ConstrainedQuadraticInstance.fix_constraint_violation_bitstring "iqm.applications.qubo.ConstrainedQuadraticInstance.fix_constraint_violation_bitstring") | Take a solution bitstring and change it in some minimal way so that it satisfies the constraints. |
| [`initialize_properties`](#iqm.applications.qubo.ConstrainedQuadraticInstance.initialize_properties "iqm.applications.qubo.ConstrainedQuadraticInstance.initialize_properties") | The initialization method for upper/lower bound, average/best quality and the corresponding bitstrings. |
| [`loss`](#iqm.applications.qubo.ConstrainedQuadraticInstance.loss "iqm.applications.qubo.ConstrainedQuadraticInstance.loss") | The loss function calculated for a given solution. |
| [`quality`](#iqm.applications.qubo.ConstrainedQuadraticInstance.quality "iqm.applications.qubo.ConstrainedQuadraticInstance.quality") | The quality function overridden for constrainted problems. |
| [`satisfy_constraints`](#iqm.applications.qubo.ConstrainedQuadraticInstance.satisfy_constraints "iqm.applications.qubo.ConstrainedQuadraticInstance.satisfy_constraints") | Take a dictionary of counts and removes the bitstrings which don't satisfy the constraints. |

*property* cqm*: [ConstrainedQuadraticModel](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/models.html#dimod.ConstrainedQuadraticModel "(in D-Wave Quantum Computing Products v9.5.0)")*  
The [`ConstrainedQuadraticModel`](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/models.html#dimod.ConstrainedQuadraticModel "(in D-Wave Quantum Computing Products v9.5.0)") representation of the problem instance.

*property* dim*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
The dimension of the problem (i.e., the number of binary variables).

*property* bqm*: [BinaryQuadraticModel](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/models.html#dimod.binary.BinaryQuadraticModel "(in D-Wave Quantum Computing Products v9.5.0)")*  
The BQM representation of the problem, penalizing constraint violation.

The problem represented as `BinaryQuadraticModel`. This is calculated using `_recalculate_bqm()` by inserting the constraints as penalties to the cost function.

*property* penalty*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*  
The penalty for breaking the constraints.

*property* qubo_matrix*: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*  
The QUBO matrix of the problem instance.

The matrix is obtained from the internal attribute [`bqm`](#iqm.applications.qubo.ConstrainedQuadraticInstance.bqm "iqm.applications.qubo.ConstrainedQuadraticInstance.bqm").

- The i,i diagonal entry corresponds to the local field acting on the i-th variable.

- The i,j entry above the diagonal corresponds to the interaction between the i-th and j-th variables.

- The entries below the diagonal are empty.

*property* qubo_graph*: [Graph](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)")*  
The QUBO graph of the problem instance.

The nodes / edges of the graph have a `bias` parameter containing the local field / interaction strength of the corresponding variable(s). Variables without interaction aren’t connected by edges in the graph.

constraints_checker(*bit_str*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/qubo.py#L425-L435)  
Checks whether the constrains of the problem are satisfied.

Parameters:  
**bit_str** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – A bitstring representing a solution.

Returns:  
Bool indicating whether the solution satisfies the constraints or not.

Return type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

loss(*bit_str*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/qubo.py#L437-L451)  
The loss function calculated for a given solution.

It is equivalent to the quality of the solution, but with extra penalties for breaking the constraints.

Parameters:  
**bit_str** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – A bitstring representing a solution.

Returns:  
The loss of the solution.

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

quality(*bit_str*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/qubo.py#L453-L466)  
The quality function overridden for constrainted problems.

Technically, for solutions violating the constraints, the “quality” isn’t defined. The corresponding quantity is [`loss()`](#iqm.applications.qubo.ConstrainedQuadraticInstance.loss "iqm.applications.qubo.ConstrainedQuadraticInstance.loss"). However, for simplicity, if a user calls this method, it just redirects to [`loss()`](#iqm.applications.qubo.ConstrainedQuadraticInstance.loss "iqm.applications.qubo.ConstrainedQuadraticInstance.loss").

Parameters:  
**bit_str** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – A bitstring representing a solution.

Returns:  
The loss of the solution and a printed warning if the solution violates the constraints.

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

initialize_properties(*max_size=30*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/qubo.py#L468-L519)  
The initialization method for upper/lower bound, average/best quality and the corresponding bitstrings.

This is the method from the parent class [`ProblemInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.applications.ProblemInstance.html#iqm.applications.applications.ProblemInstance "iqm.applications.applications.ProblemInstance"), overridden so that the bruteforce search only includes solutions which satisfy the constraints.

Parameters:  
**max_size** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – The maximum size of problems for which the properties may be calculated.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If [`initialize_properties()`](#iqm.applications.qubo.ConstrainedQuadraticInstance.initialize_properties "iqm.applications.qubo.ConstrainedQuadraticInstance.initialize_properties") was called on a [`ConstrainedQuadraticInstance`](#iqm.applications.qubo.ConstrainedQuadraticInstance "iqm.applications.qubo.ConstrainedQuadraticInstance") object with dimension larger than `max_size`.

Return type:  
None

fix_constraint_violation(*counts*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/qubo.py#L521-L547)  
Take a dictionary and change the bitstrings in it in some minimal way so that they satisfy the constraints.

Iterates through the dictionary `counts` and for each key calls [`fix_constraint_violation_bitstring()`](#iqm.applications.qubo.ConstrainedQuadraticInstance.fix_constraint_violation_bitstring "iqm.applications.qubo.ConstrainedQuadraticInstance.fix_constraint_violation_bitstring"). In case that multiple bitstrings get mapped to the same bitstring, their respective frequencies (values) are added.

Warning

The bitstrings in the `counts` need to be ordered the same way as the variables of the problem. If you’re using a dictionary of counts obtained directly from a Qiskit experiment, you need to reverse the order of the bitstrings (keys of the `counts` dictionary) first.

Parameters:  
**counts** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – The dictionary of bitstrings with their frequencies as values.

Returns:  
The input dictionary modified so that the keys now satisfy the problem constraints.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]

fix_constraint_violation_bitstring(*bit_str*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/qubo.py#L549-L566)  
Take a solution bitstring and change it in some minimal way so that it satisfies the constraints.

This is not possible to do generally, so this method is not implemented for :class:ConstrainedQuadraticInstance\` and it needs to be defined for the individual subclasses of [`ConstrainedQuadraticInstance`](#iqm.applications.qubo.ConstrainedQuadraticInstance "iqm.applications.qubo.ConstrainedQuadraticInstance") (if it’s possible to do). If the input bitstring `bit_str` already satisfies the problem constraints, it should be returned unchanged.

Parameters:  
**bit_str** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The bitstring to be modified to satisfy the constraints.

Returns:  
The bitstring modified in some minimal way to satisfy the constraints.

Return type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

satisfy_constraints(*counts*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/qubo.py#L568-L588)  
Take a dictionary of counts and removes the bitstrings which don’t satisfy the constraints.

If none of the counts satisfy the constraints, the returned dictionary will be empty.

Warning

The bitstrings in the `counts` need to be ordered the same way as the variables of the problem. If you’re using a dictionary of counts obtained directly from a Qiskit experiment, you need to reverse the order of the bitstrings (keys of the `counts` dictionary) first.

Parameters:  
**counts** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – A dictionary of counts, with solution strings as keys and their frequencies as values.

Returns:  
The same dictionary as inputted, except with removed entries whose keys don’t satisfy the problem constraints.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]

Inheritance

![Inheritance diagram of iqm.applications.qubo.ConstrainedQuadraticInstance](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-3d2f73315f8794d9a9939edf5f20d3c74797f0d7.png)
