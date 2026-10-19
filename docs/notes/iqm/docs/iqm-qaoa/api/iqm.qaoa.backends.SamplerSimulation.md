> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.SamplerSimulation.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.SamplerSimulation.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 247f2e70f3f068275edb652b3d5432ede893cf44f4e6d9a14969252c40e6c3bb.

# SamplerSimulation

Module: [`iqm.qaoa.backends`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.html#module-iqm.qaoa.backends "iqm.qaoa.backends")

*class* iqm.qaoa.backends.SamplerSimulation(*simulator=None*, *transpiler=None*, *\*\*kwargs*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/backends.py#L944-L996)  
Bases: [`SamplerBackend`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.SamplerBackend.html#iqm.qaoa.backends.SamplerBackend "iqm.qaoa.backends.SamplerBackend")

A sampler that simulates the QAOA circuit in [`qiskit`](https://quantum.cloud.ibm.com/docs/api/qiskit/index#module-qiskit "(in Qiskit v2.5)").

Some simulators may need the circuit to be transpiled, so optionally a [`TranspilerOption`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.TranspilerOption.html#iqm.qaoa.circuits.TranspilerOption "iqm.qaoa.circuits.TranspilerOption") may be provided.

Parameters:  
- **simulator** (*BackendV2* *\|* *None*) – A simulator which the simulation can be run on.

- **transpiler** ([*TranspilerOption*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.TranspilerOption.html#iqm.qaoa.circuits.TranspilerOption "iqm.qaoa.circuits.TranspilerOption") *\|* *None*) – A transpilation (routing) strategy to use, if applicable.

- **kwargs** (*Any*)

Methods

Inheritance

![Inheritance diagram of iqm.qaoa.backends.SamplerSimulation](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-fa3e6b2b985c13db82825b0c5249d09278eeb0b7.png)
