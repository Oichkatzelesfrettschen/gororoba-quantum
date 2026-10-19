> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.sn.sn.sn_router.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.sn.sn.sn_router.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 bcf07a97e7c1dae493a69e1ddec81da58b3d5605ccd43c402e2502689c942ff9.

# sn_router

iqm.qaoa.transpiler.sn.sn.sn_router(*problem_bqm*, *qpu*, *do_line_swapping=None*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/sn/sn.py#L37-L146)  
The function that implements the ‘swap network’ swapping strategies.

Implements the swap network approach from \[[5](https://docs.iqm.tech/4.7/iqm-qaoa/references.html#id7 "Johannes Weidenfeller, Lucia C. Valor, Julien Gacon, Caroline Tornow, Luciano Bello, Stefan Woerner, and Daniel J. Egger. Scaling of the quantum approximate optimization algorithm on superconducting qubit based hardware. Quantum, 6:870, Dec 2022. URL: http://dx.doi.org/10.22331/q-2022-12-07-870, doi:10.22331/q-2022-12-07-870.")\]. If the input BQM is not all-to-all connected, dummy interactions (of strength 0) are added to make it all-to-all connected. By default, it implements the grid swapping strategy (adapted for a generic rectangle, not just a square as shown in the paper). The grid swapping strategy tries to find a sufficient rectangle in the provided Crystal QPU (square lattice topology required). If there is no rectangle of suitable size in the QPU, the default behavior is to switch to the line swapping strategy as a fallback (corresponding to a rectangle of width 1). The optional input boolean `do_line_swapping` allows to configure whether the line swapping strategy should be used preferentially instead of the grid strategy or not at all.

Parameters:  
- **problem_bqm** ([*BinaryQuadraticModel*](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/models.html#dimod.binary.BinaryQuadraticModel "(in D-Wave Quantum Computing Products v9.5.0)")) – The `BinaryQuadraticModel` description of the problem, necessary to create an instance of [`Routing`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Routing.html#iqm.qaoa.transpiler.routing.Routing "iqm.qaoa.transpiler.routing.Routing").

- **qpu** ([*QPU*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.QPU.html#iqm.qaoa.transpiler.quantum_hardware.QPU "iqm.qaoa.transpiler.quantum_hardware.QPU")) – The QPU, necessary to create an instance of [`Routing`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Routing.html#iqm.qaoa.transpiler.routing.Routing "iqm.qaoa.transpiler.routing.Routing") and to get the topology of the qubits. The `qpu` also needs to contain the layout of the qubits with integer coordinates as an attribute.

- **do_line_swapping** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") *\|* *None*) – If set to `True`, the line swapping strategy is used instead of the grid swapping strategy. If set to `False`, the line swapping strategy is not used at all (raising an error in case the grid swapping strategy fails). If set to `None` (the default), the line swapping strategy is used as a fallback in case the grid swapping strategy fails.

Returns:  
A [`Routing`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Routing.html#iqm.qaoa.transpiler.routing.Routing "iqm.qaoa.transpiler.routing.Routing") object containing the routing created by using swap networks.

Raises:  
- [**TypeError**](https://docs.python.org/3.11/library/exceptions.html#TypeError "(in Python v3.11)") – If the QPU’s layout doesn’t have integer coordinates and `do_line_swapping` is `False`. Integer coordinates are necessary to correctly identify where the swap and interaction gates need to be applied in the grid swap network strategy.

- [**RuntimeError**](https://docs.python.org/3.11/library/exceptions.html#RuntimeError "(in Python v3.11)") – If the algorithm doesn’t find a sufficiently large rectangle of qubits in the QPU and `do_line_swapping` is `False`

Warns:  
**UserWarning** – If the QPU’s layout doesn’t have integer coordinates and `do_line_swapping` is `None`. In this case, the algorithm immediately switches to the line swapping strategy because integer layout coordinates are necessary for the grid swapping strategy.

Return type:  
[*Routing*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Routing.html#iqm.qaoa.transpiler.routing.Routing "iqm.qaoa.transpiler.routing.Routing")
