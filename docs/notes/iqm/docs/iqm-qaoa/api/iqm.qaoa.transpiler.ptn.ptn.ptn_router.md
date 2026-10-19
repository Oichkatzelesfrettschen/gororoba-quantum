> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.ptn.ptn.ptn_router.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.ptn.ptn.ptn_router.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e56378570b0fee9d2dd02c173b15ca4cb74dd9d6d8b00e5a02731e72d1f01183.

# ptn_router

iqm.qaoa.transpiler.ptn.ptn.ptn_router(*problem_bqm*, *qpu*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/ptn/ptn.py#L33-L69)  
Construct a routing object for the ParityTwineNetwork (PTN).

Parameters:  
- **problem_bqm** ([*BinaryQuadraticModel*](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/models.html#dimod.binary.BinaryQuadraticModel "(in D-Wave Quantum Computing Products v9.5.0)")) – The binary quadratic model representing the optimization problem.

- **qpu** ([*QPU*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.QPU.html#iqm.qaoa.transpiler.quantum_hardware.QPU "iqm.qaoa.transpiler.quantum_hardware.QPU")) – QPU instance.

Returns:  
A `CircuitSynthesis` object implementing the requested routing strategy.

Return type:  
[*CircuitSynthesis*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.CircuitSynthesis.html#iqm.qaoa.transpiler.routing.CircuitSynthesis "iqm.qaoa.transpiler.routing.CircuitSynthesis")
