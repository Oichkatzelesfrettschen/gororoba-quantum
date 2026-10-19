> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.SamplerBackend.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.SamplerBackend.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 bd8c6bb13fce7c2ba7bd94ea0a1166b1f6751a1fc051ed44a69120f1404c1303.

# SamplerBackend

Module: [`iqm.qaoa.backends`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.html#module-iqm.qaoa.backends "iqm.qaoa.backends")

*class* iqm.qaoa.backends.SamplerBackend[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/backends.py#L194-L248)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

The template for sampler backends, i.e., those returning samples from the QAOA.

Methods

|  |  |
|----|----|
| [`sample`](#iqm.qaoa.backends.SamplerBackend.sample "iqm.qaoa.backends.SamplerBackend.sample") | Sample bitstrings from the QAOA circuit. |

sample(*qaoa_object*, *shots*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/../../../../../../root/.local/share/uv/python/cpython-3.11.14-linux-x86_64-gnu/lib/python3.11/functools.py#L197-L217)\
sample(*qaoa_object*, *shots*)\
sample(*qaoa_object*, *shots*)  
Sample bitstrings from the QAOA circuit.

This method uses `singledispatchmethod()` to dispatch to a type-specific implementation based on the runtime type of `qaoa_object`. If no registered implementation matches, it falls back to `_sample_unsupported()`. Subclasses should override the type-specific private methods rather than this one.

Parameters:  
- **qaoa_object** ([*QAOA*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.generic_qaoa.QAOA.html#iqm.qaoa.generic_qaoa.QAOA "iqm.qaoa.generic_qaoa.QAOA")) – A [`QAOA`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.generic_qaoa.QAOA.html#iqm.qaoa.generic_qaoa.QAOA "iqm.qaoa.generic_qaoa.QAOA") object to be sampled from.

- **shots** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of individual samples to take.

Returns:  
A dictionary of samples. The keys are bitstrings and the values are their counts (which should add up to `shots`)

Raises:  
[**TypeError**](https://docs.python.org/3.11/library/exceptions.html#TypeError "(in Python v3.11)") – If no registered implementation exists for the type of `qaoa_object`.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]

Inheritance

![Inheritance diagram of iqm.qaoa.backends.SamplerBackend](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-20523b3b95090d3dc9a8e811418443692e06f50b.png)
