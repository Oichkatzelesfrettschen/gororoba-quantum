> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.tree_qaoa.TreeQAOA.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.tree_qaoa.TreeQAOA.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 27088fc23759bd6c85a602fefe5a00529d2c9b1e6d5d4a4c77c33b1b04dfcc21.

# TreeQAOA

Module: [`iqm.qaoa.tree_qaoa`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.tree_qaoa.html#module-iqm.qaoa.tree_qaoa "iqm.qaoa.tree_qaoa")

*class* iqm.qaoa.tree_qaoa.TreeQAOA(*problem*, *num_layers*, *\**, *betas=None*, *gammas=None*, *initial_angles=None*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/tree_qaoa.py#L54-L190)  
Bases: [`QUBOQAOA`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.qubo_qaoa.QUBOQAOA.html#iqm.qaoa.qubo_qaoa.QUBOQAOA "iqm.qaoa.qubo_qaoa.QUBOQAOA")

The class for tree QAOA with QUBO cost function.

The class inherits everything from [`QUBOQAOA`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.qubo_qaoa.QUBOQAOA.html#iqm.qaoa.qubo_qaoa.QUBOQAOA "iqm.qaoa.qubo_qaoa.QUBOQAOA"), but adds one more method [`set_tree_angles()`](#iqm.qaoa.tree_qaoa.TreeQAOA.set_tree_angles "iqm.qaoa.tree_qaoa.TreeQAOA.set_tree_angles"), which sets [`angles`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.generic_qaoa.QAOA.html#iqm.qaoa.generic_qaoa.QAOA.angles "iqm.qaoa.generic_qaoa.QAOA.angles") according to the tree schedule. The tree schedule uses QAOA angles precalculated numerically for a class of high-girth regular graph problems with uniform Hamiltonian. For more details see \[[8](https://docs.iqm.tech/4.7/iqm-qaoa/references.html#id8 "Elisabeth Wybo and Martin Leib. Missing puzzle pieces in the performance landscape of the quantum approximate optimization algorithm. 2024. URL: https://arxiv.org/abs/2406.14618, arXiv:2406.14618.")\].

Parameters:  
- **problem** ([*QUBOInstance*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.qubo.QUBOInstance.html#iqm.applications.qubo.QUBOInstance "iqm.applications.qubo.QUBOInstance") *\|* [*ConstrainedQuadraticInstance*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.qubo.ConstrainedQuadraticInstance.html#iqm.applications.qubo.ConstrainedQuadraticInstance "iqm.applications.qubo.ConstrainedQuadraticInstance")) – A [`QUBOInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.qubo.QUBOInstance.html#iqm.applications.qubo.QUBOInstance "iqm.applications.qubo.QUBOInstance") object describing the QUBO problem to be solved.

- **num_layers** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of QAOA layers, commonly referred to as *p* in the literature.

- **betas** (*Sequence\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]* *\|* *np.ndarray* *\|* *None*) – An optional list of the initial *beta* angles of QAOA. Has to be provided together with `gammas`.

- **gammas** (*Sequence\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]* *\|* *np.ndarray* *\|* *None*) – An optional list of the initial *gamma* angles of QAOA. Has to be provided together with `betas`.

- **initial_angles** (*Sequence\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]* *\|* *np.ndarray* *\|* *None*) – An optional list of the initial QAOA angles as one variable. Shouldn’t be provided together with either `betas` or `gammas`.

Attributes

Methods

|  |  |
|----|----|
| [`set_tree_angles`](#iqm.qaoa.tree_qaoa.TreeQAOA.set_tree_angles "iqm.qaoa.tree_qaoa.TreeQAOA.set_tree_angles") | A method for setting [`iqm.qaoa.generic_qaoa.QAOA.angles`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.generic_qaoa.QAOA.html#iqm.qaoa.generic_qaoa.QAOA.angles "iqm.qaoa.generic_qaoa.QAOA.angles") according to the tree schedule. |

set_tree_angles(*verbose=True*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/tree_qaoa.py#L72-L190)  
A method for setting [`iqm.qaoa.generic_qaoa.QAOA.angles`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.generic_qaoa.QAOA.html#iqm.qaoa.generic_qaoa.QAOA.angles "iqm.qaoa.generic_qaoa.QAOA.angles") according to the tree schedule.

The tree schedule is designed for problems with uniform 1-body local field, unit 2-body interactions and uniform node degree. Therefore, when given a generic problem, the algorithm first calculates the average degree `d_av`, the average local field `h_av` and the average interaction strength `j_av` (which is used to renormalize the local field). The angles are then looked up in the saved files for the nearest implemented degree and local field. For \\p \> 6\\ QAOA, the angles are interpolated from the calculated angles for \\p = 6\\. The method doesn’t output anything, but it modifies [`iqm.qaoa.generic_qaoa.QAOA.angles`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.generic_qaoa.QAOA.html#iqm.qaoa.generic_qaoa.QAOA.angles "iqm.qaoa.generic_qaoa.QAOA.angles") in-place.

Parameters:  
**verbose** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Should the method print out informative text about what it did?

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the Hamiltonian contains ferromagnetic (i.e., negative) interactions between qubits. The tree schedule shouldn’t be used for such cases.

Return type:  
None

Inheritance

![Inheritance diagram of iqm.qaoa.tree_qaoa.TreeQAOA](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-d6ff9a529ae0801793e59202d5b9400cfbc65c0b.png)
