> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.hubo_qaoa.HUBOQAOA.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.hubo_qaoa.HUBOQAOA.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1e8634f4161ea2a70bbc69eace996e9a9b3fbd12cd868d440474d5c0e2534857.

# HUBOQAOA

Module: [`iqm.qaoa.hubo_qaoa`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.hubo_qaoa.html#module-iqm.qaoa.hubo_qaoa "iqm.qaoa.hubo_qaoa")

*class* iqm.qaoa.hubo_qaoa.HUBOQAOA(*problem*, *num_layers*, *\**, *betas=None*, *gammas=None*, *initial_angles=None*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/hubo_qaoa.py#L38-L85)  
Bases: [`QAOA`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.generic_qaoa.QAOA.html#iqm.qaoa.generic_qaoa.QAOA "iqm.qaoa.generic_qaoa.QAOA")\[[`HUBOInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.hubo.HUBOInstance.html#iqm.applications.hubo.HUBOInstance "iqm.applications.hubo.HUBOInstance")\]

The class for QAOA with higher-order unconstrained binary (HUBO) cost function.

The class inherits a lot of functionality from its parent [`iqm.qaoa.generic_qaoa.QAOA`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.generic_qaoa.QAOA.html#iqm.qaoa.generic_qaoa.QAOA "iqm.qaoa.generic_qaoa.QAOA"). One new addition is the attribute [`hamiltonian_bp`](#iqm.qaoa.hubo_qaoa.HUBOQAOA.hamiltonian_bp "iqm.qaoa.hubo_qaoa.HUBOQAOA.hamiltonian_bp") which stores the coefficient of the problem Hamiltonian.

Parameters:  
- **problem** ([*HUBOInstance*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.hubo.HUBOInstance.html#iqm.applications.hubo.HUBOInstance "iqm.applications.hubo.HUBOInstance")) – A [`HUBOInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.hubo.HUBOInstance.html#iqm.applications.hubo.HUBOInstance "iqm.applications.hubo.HUBOInstance") object describing the HUBO problem to be solved.

- **num_layers** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of QAOA layers, commonly referred to as *p* in the literature.

- **betas** (*Sequence\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]* *\|* *np.ndarray* *\|* *None*) – An optional list of the initial *beta* angles of QAOA. Has to be provided together with `gammas`.

- **gammas** (*Sequence\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]* *\|* *np.ndarray* *\|* *None*) – An optional list of the initial *gamma* angles of QAOA. Has to be provided together with `betas`.

- **initial_angles** (*Sequence\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]* *\|* *np.ndarray* *\|* *None*) – An optional list of the initial QAOA angles as one variable. Shouldn’t be provided together with either `betas` or `gammas`. The *gamma* and *beta* angles are interleaved, so that the first pair of entries corresponds to \\\gamma_1\\ and \\\beta_1\\ (the angles of the first QAOA layer). The second pair of entries corresponds to \\\gamma_2\\ and \\\beta_2\\, etc. …

Attributes

|  |  |
|----|----|
| [`hamiltonian_bp`](#iqm.qaoa.hubo_qaoa.HUBOQAOA.hamiltonian_bp "iqm.qaoa.hubo_qaoa.HUBOQAOA.hamiltonian_bp") | The BP representation of the problem, taken from the input [`HUBOInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.hubo.HUBOInstance.html#iqm.applications.hubo.HUBOInstance "iqm.applications.hubo.HUBOInstance"). |

Methods

*property* hamiltonian_bp*: [BinaryPolynomial](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/models.html#dimod.higherorder.polynomial.BinaryPolynomial "(in D-Wave Quantum Computing Products v9.5.0)")*  
The BP representation of the problem, taken from the input [`HUBOInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.hubo.HUBOInstance.html#iqm.applications.hubo.HUBOInstance "iqm.applications.hubo.HUBOInstance").

Inheritance

![Inheritance diagram of iqm.qaoa.hubo_qaoa.HUBOQAOA](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-23e992f83e19e16ac11c008f7a2b700ae42fcbd3.png)
