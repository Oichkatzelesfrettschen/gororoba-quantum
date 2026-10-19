> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.star.star.star_router.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.star.star.star_router.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 006e7831489cdd82ec4e9dff42b00deaf69e9a7bd0471c4f3740bbb6f038bfae.

# star_router

iqm.qaoa.transpiler.star.star.star_router(*problem_bqm*, *qpu*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/star/star.py#L289-L330)  
The function that implements the optimal swapping strategy on the star QPU.

Looks for the minimum vertex cover set on the problem graph and then swaps the nodes belonging to this cover into the center of the star (adding the interaction gates in between).

Parameters:  
- **problem_bqm** ([*BinaryQuadraticModel*](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/models.html#dimod.binary.BinaryQuadraticModel "(in D-Wave Quantum Computing Products v9.5.0)")) – The `BinaryQuadraticModel` description of the problem, necessary to create an instance of [`RoutingStar`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.star.star.RoutingStar.html#iqm.qaoa.transpiler.star.star.RoutingStar "iqm.qaoa.transpiler.star.star.RoutingStar").

- **qpu** ([*StarQPU*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.StarQPU.html#iqm.qaoa.transpiler.quantum_hardware.StarQPU "iqm.qaoa.transpiler.quantum_hardware.StarQPU")) – The QPU, necessary to create an instance of [`RoutingStar`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.star.star.RoutingStar.html#iqm.qaoa.transpiler.star.star.RoutingStar "iqm.qaoa.transpiler.star.star.RoutingStar").

Returns:  
A [`RoutingStar`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.star.star.RoutingStar.html#iqm.qaoa.transpiler.star.star.RoutingStar "iqm.qaoa.transpiler.star.star.RoutingStar") object containing the optimal star swapping strategy.

Return type:  
[*RoutingStar*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.star.star.RoutingStar.html#iqm.qaoa.transpiler.star.star.RoutingStar "iqm.qaoa.transpiler.star.star.RoutingStar")
