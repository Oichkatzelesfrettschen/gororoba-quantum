> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.SamplerResonance.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.SamplerResonance.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3343f4de98457863ef06ae6b5d8cde5d40b1a2dbd544491ce8559d0a99b6f4ec.

# SamplerResonance

Module: [`iqm.qaoa.backends`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.html#module-iqm.qaoa.backends "iqm.qaoa.backends")

*class* iqm.qaoa.backends.SamplerResonance(*token*, *server_url='https://resonance.iqm.tech'*, *quantum_computer='garnet'*, *transpiler=TranspilerOption.SPARSE*, *\*\*kwargs*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/backends.py#L999-L1046)  
Bases: [`SamplerBackend`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.SamplerBackend.html#iqm.qaoa.backends.SamplerBackend "iqm.qaoa.backends.SamplerBackend")

A sampler that runs the circuit on IQM Resonance and returns the result.

Parameters:  
- **token** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The API token to be used to connect to IQM Resonance.

- **server_url** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The Resonance URL.

- **quantum_computer** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The name of the quantum computer to be used (defaults to Garnet).

- **transpiler** ([*TranspilerOption*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.TranspilerOption.html#iqm.qaoa.circuits.TranspilerOption "iqm.qaoa.circuits.TranspilerOption")) – The transpiling strategy to be used when building the quantum circuit for the QC. Defaults to TranspilerOption.SPARSE

- **kwargs** (*Any*) – The keyword arguments to be passed to the inner call to Qiskit `transpile()`.

Methods

Inheritance

![Inheritance diagram of iqm.qaoa.backends.SamplerResonance](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-3d3768f129b06fa2f01e4c3d8a37162daa01e3e8.png)
