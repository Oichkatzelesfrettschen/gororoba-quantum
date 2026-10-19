> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.hardwired.hardwired.hardwired_router.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.hardwired.hardwired.hardwired_router.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 56f50d03e9d0d34430a97a2c85816b20aeeba61acb4a21e123181c0e214c1fef.

# hardwired_router

iqm.qaoa.transpiler.hardwired.hardwired.hardwired_router(*problem_bqm*, *qpu*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/hardwired/hardwired.py#L37-L800)  
The function that creates an optimal routing for all-to-all connected problems, designed by hand.

The original code was written for hand-picked qubits from the Apollo QPU. When this was expanded to be used on any QPU, the algorithm had to be adjusted. Here is how it works now:

1.  First, the `BinaryQuadraticModel` representation of the problem is padded with extra interactions (of strength 0), to make it trully all-to-all connected.

2.  Then, based on the number of variables of the problem, we construct a dummy graph `underlying_graph` which represents the part of the QPU on which the circuit acts.

3.  We find a suitable mapping between `underlying_graph` and the QPU graph [`hardware_graph`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.QPU.html#iqm.qaoa.transpiler.quantum_hardware.QPU.hardware_graph "iqm.qaoa.transpiler.quantum_hardware.QPU.hardware_graph"). This mapping `inverse_iso` is used in the [`apply_int()`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Routing.html#iqm.qaoa.transpiler.routing.Routing.apply_int "iqm.qaoa.transpiler.routing.Routing.apply_int") and [`apply_swap()`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Routing.html#iqm.qaoa.transpiler.routing.Routing.apply_swap "iqm.qaoa.transpiler.routing.Routing.apply_swap") method calls.

4.  Using the [`apply_int()`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Routing.html#iqm.qaoa.transpiler.routing.Routing.apply_int "iqm.qaoa.transpiler.routing.Routing.apply_int") and [`apply_swap()`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Routing.html#iqm.qaoa.transpiler.routing.Routing.apply_swap "iqm.qaoa.transpiler.routing.Routing.apply_swap") methods, the hardwired routing is constructed.

Parameters:  
- **problem_bqm** ([*BinaryQuadraticModel*](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/models.html#dimod.binary.BinaryQuadraticModel "(in D-Wave Quantum Computing Products v9.5.0)")) – The `BinaryQuadraticModel` representation of the problem, needed only to instantiate the [`Routing`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Routing.html#iqm.qaoa.transpiler.routing.Routing "iqm.qaoa.transpiler.routing.Routing").

- **qpu** ([*CrystalQPUFromBackend*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.CrystalQPUFromBackend.html#iqm.qaoa.transpiler.quantum_hardware.CrystalQPUFromBackend "iqm.qaoa.transpiler.quantum_hardware.CrystalQPUFromBackend")) – The [`CrystalQPUFromBackend`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.CrystalQPUFromBackend.html#iqm.qaoa.transpiler.quantum_hardware.CrystalQPUFromBackend "iqm.qaoa.transpiler.quantum_hardware.CrystalQPUFromBackend") object.

Returns:  
A [`Routing`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Routing.html#iqm.qaoa.transpiler.routing.Routing "iqm.qaoa.transpiler.routing.Routing") object containing the entire routing schedule.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the number of variables of the problem is not between 4 and 15 (inclusive).

Return type:  
[*Routing*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Routing.html#iqm.qaoa.transpiler.routing.Routing "iqm.qaoa.transpiler.routing.Routing")
