> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.SamplerRandomBitstrings.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.SamplerRandomBitstrings.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 dc6e4e0592d759283233eb49564b7d5d497321e99c9c70299810f8135df20193.

# SamplerRandomBitstrings

Module: [`iqm.qaoa.backends`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.html#module-iqm.qaoa.backends "iqm.qaoa.backends")

*class* iqm.qaoa.backends.SamplerRandomBitstrings[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/backends.py#L894-L916)  
Bases: [`SamplerBackend`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.SamplerBackend.html#iqm.qaoa.backends.SamplerBackend "iqm.qaoa.backends.SamplerBackend")

A sampler that ignores the QAOA and just produces random bitstrings of the correct length.

Methods

|  |  |
|----|----|
| [`sample`](#iqm.qaoa.backends.SamplerRandomBitstrings.sample "iqm.qaoa.backends.SamplerRandomBitstrings.sample") | Produce random bitstrings to act as samples from the QAOA. |

sample(*qaoa_object*, *shots*, *seed=None*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/backends.py#L897-L916)  
Produce random bitstrings to act as samples from the QAOA.

The `qaoa_object` is used only to get the number of qubits (which corresponds to the length of the bitstrings). The number of uniformly random bitstrings produced is `shots` and they are arranged in a dictionary just like counts from a [`qiskit`](https://quantum.cloud.ibm.com/docs/api/qiskit/index#module-qiskit "(in Qiskit v2.5)") measurement.

This method overrides the dispatching method [`sample()`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.SamplerBackend.html#iqm.qaoa.backends.SamplerBackend.sample "iqm.qaoa.backends.SamplerBackend.sample") of [`SamplerBackend`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.SamplerBackend.html#iqm.qaoa.backends.SamplerBackend "iqm.qaoa.backends.SamplerBackend") because there is no point in doing any kind of dispatching here.

Parameters:  
- **qaoa_object** ([*QAOA*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.generic_qaoa.QAOA.html#iqm.qaoa.generic_qaoa.QAOA "iqm.qaoa.generic_qaoa.QAOA")) – The QAOA object, only used to get the number of qubits.

- **shots** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of random strings to generate.

- **seed** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – The seed to be used in the random bitstring generation. Optional parameter.

Returns:  
A dictionary whose keys are the produced random bitstrings and values their frequencies in the random set.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]

Inheritance

![Inheritance diagram of iqm.qaoa.backends.SamplerRandomBitstrings](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-893321a628d8af9591b793d36bc723fa1aa1449f.png)
