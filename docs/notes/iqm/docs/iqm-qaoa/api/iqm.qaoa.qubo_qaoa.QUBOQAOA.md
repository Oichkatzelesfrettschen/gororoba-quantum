> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.qubo_qaoa.QUBOQAOA.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.qubo_qaoa.QUBOQAOA.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 394b518a43bd8078fc79a1c483efdf2e69e0ed56136a631474c5c2a6ed7b141c.

# QUBOQAOA

Module: [`iqm.qaoa.qubo_qaoa`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.qubo_qaoa.html#module-iqm.qaoa.qubo_qaoa "iqm.qaoa.qubo_qaoa")

*class* iqm.qaoa.qubo_qaoa.QUBOQAOA(*problem*, *num_layers*, *\**, *betas=None*, *gammas=None*, *initial_angles=None*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/qubo_qaoa.py#L45-L131)  
Bases: [`QAOA`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.generic_qaoa.QAOA.html#iqm.qaoa.generic_qaoa.QAOA "iqm.qaoa.generic_qaoa.QAOA")\[[`QUBOInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.qubo.QUBOInstance.html#iqm.applications.qubo.QUBOInstance "iqm.applications.qubo.QUBOInstance") \| [`ConstrainedQuadraticInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.qubo.ConstrainedQuadraticInstance.html#iqm.applications.qubo.ConstrainedQuadraticInstance "iqm.applications.qubo.ConstrainedQuadraticInstance")\]

The class for QAOA with quadratic unconstrained binary (QUBO) cost function.

The class inherits a lot of functionality from its parent [`iqm.qaoa.generic_qaoa.QAOA`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.generic_qaoa.QAOA.html#iqm.qaoa.generic_qaoa.QAOA "iqm.qaoa.generic_qaoa.QAOA"). One new addition is the attribute [`hamiltonian_bqm`](#iqm.qaoa.qubo_qaoa.QUBOQAOA.hamiltonian_bqm "iqm.qaoa.qubo_qaoa.QUBOQAOA.hamiltonian_bqm") which stores the coefficient of the problem Hamiltonian.

Parameters:  
- **problem** ([*QUBOInstance*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.qubo.QUBOInstance.html#iqm.applications.qubo.QUBOInstance "iqm.applications.qubo.QUBOInstance") *\|* [*ConstrainedQuadraticInstance*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.qubo.ConstrainedQuadraticInstance.html#iqm.applications.qubo.ConstrainedQuadraticInstance "iqm.applications.qubo.ConstrainedQuadraticInstance")) – A [`QUBOInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.qubo.QUBOInstance.html#iqm.applications.qubo.QUBOInstance "iqm.applications.qubo.QUBOInstance") object describing the QUBO problem to be solved.

- **num_layers** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of QAOA layers, commonly referred to as *p* in the literature.

- **betas** (*Sequence\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]* *\|* *np.ndarray* *\|* *None*) – An optional list of the initial *beta* angles of QAOA. Has to be provided together with `gammas`.

- **gammas** (*Sequence\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]* *\|* *np.ndarray* *\|* *None*) – An optional list of the initial *gamma* angles of QAOA. Has to be provided together with `betas`.

- **initial_angles** (*Sequence\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]* *\|* *np.ndarray* *\|* *None*) – An optional list of the initial QAOA angles as one variable. Shouldn’t be provided together with either `betas` or `gammas`. The *gamma* and *beta* angles are interleaved, so that the first pair of entries corresponds to \\\gamma_1\\ and \\\beta_1\\ (the angles of the first QAOA layer). The second pair of entries corresponds to \\\gamma_2\\ and \\\beta_2\\, etc. …

Attributes

|  |  |
|----|----|
| [`hamiltonian_bqm`](#iqm.qaoa.qubo_qaoa.QUBOQAOA.hamiltonian_bqm "iqm.qaoa.qubo_qaoa.QUBOQAOA.hamiltonian_bqm") | The BQM representation of the problem, taken from the input [`QUBOInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.qubo.QUBOInstance.html#iqm.applications.qubo.QUBOInstance "iqm.applications.qubo.QUBOInstance"). |
| [`hamiltonian_graph`](#iqm.qaoa.qubo_qaoa.QUBOQAOA.hamiltonian_graph "iqm.qaoa.qubo_qaoa.QUBOQAOA.hamiltonian_graph") | The graph whose edges / nodes have weights `bias` equal to the coefficients in the problem Hamiltonian. |
| [`interactions`](#iqm.qaoa.qubo_qaoa.QUBOQAOA.interactions "iqm.qaoa.qubo_qaoa.QUBOQAOA.interactions") | Returns an upper-triangular matrix of the *ZZ* interactions between the variables. |
| [`local_fields`](#iqm.qaoa.qubo_qaoa.QUBOQAOA.local_fields "iqm.qaoa.qubo_qaoa.QUBOQAOA.local_fields") | Returns a [`ndarray`](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)") of the local fields of the model (*Z* coefficients). |

Methods

*property* hamiltonian_bqm*: [BinaryQuadraticModel](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/models.html#dimod.binary.BinaryQuadraticModel "(in D-Wave Quantum Computing Products v9.5.0)")*  
The BQM representation of the problem, taken from the input [`QUBOInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.qubo.QUBOInstance.html#iqm.applications.qubo.QUBOInstance "iqm.applications.qubo.QUBOInstance").

*property* hamiltonian_graph*: [Graph](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)")*  
The graph whose edges / nodes have weights `bias` equal to the coefficients in the problem Hamiltonian.

*property* interactions*: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*  
Returns an upper-triangular matrix of the *ZZ* interactions between the variables.

If the Hamiltonian representing the problem is

\\H = \sum\_{i\<j} J\_{ij} Z_i Z_j + \sum_i h_i Z_i\\

then this method outputs \\J\_{ij}\\ as upper-triangular square matrix [`ndarray`](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"). Note that these are different from the off-diagonal elements of [`qubo_matrix`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.qubo.QUBOInstance.html#iqm.applications.qubo.QUBOInstance.qubo_matrix "iqm.applications.qubo.QUBOInstance.qubo_matrix") of the input `problem` because the QUBO cost function has different coefficients than the Hamiltonian.

*property* local_fields*: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*  
Returns a [`ndarray`](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)") of the local fields of the model (*Z* coefficients).

If the Hamiltonian representing the problem is

\\H = \sum\_{i\<j} J\_{ij} Z_i Z_j + \sum_i h_i Z_i\\

then this method outputs \\h\_{i}\\ as 1-dimensional [`ndarray`](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"). Note that these are different from the diagonal elements of [`qubo_matrix`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.qubo.QUBOInstance.html#iqm.applications.qubo.QUBOInstance.qubo_matrix "iqm.applications.qubo.QUBOInstance.qubo_matrix") of the input `problem` because the QUBO cost function has different coefficients than the Hamiltonian.

Inheritance

![Inheritance diagram of iqm.qaoa.qubo_qaoa.QUBOQAOA](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-6f229c412bc4b7be6bd44879f51cbcf40118aed9.png)
