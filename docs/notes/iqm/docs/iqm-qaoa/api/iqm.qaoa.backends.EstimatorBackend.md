> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.EstimatorBackend.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.EstimatorBackend.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 76ba24562177f5a7fc02314d1e299e9c5a7ea14f6db54c98f06a848497950f53.

# EstimatorBackend

Module: [`iqm.qaoa.backends`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.html#module-iqm.qaoa.backends "iqm.qaoa.backends")

*class* iqm.qaoa.backends.EstimatorBackend[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/backends.py#L71-L191)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

The template class for estimator backends, i.e., those calculating the expected value of the Hamiltonian.

Methods

|  |  |
|----|----|
| [`estimate`](#iqm.qaoa.backends.EstimatorBackend.estimate "iqm.qaoa.backends.EstimatorBackend.estimate") | Estimate the expected value of the Hamiltonian. |
| [`estimate_correlations_z`](#iqm.qaoa.backends.EstimatorBackend.estimate_correlations_z "iqm.qaoa.backends.EstimatorBackend.estimate_correlations_z") | Estimate the expected value of products of Z operators on `target_qubits`. |

estimate(*qaoa_object*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/../../../../../../root/.local/share/uv/python/cpython-3.11.14-linux-x86_64-gnu/lib/python3.11/functools.py#L74-L96)\
estimate(*qaoa_object*)\
estimate(*qaoa_object*)  
Estimate the expected value of the Hamiltonian.

This method uses `singledispatchmethod()` to dispatch to a type-specific implementation based on the runtime type of `qaoa_object`. If no registered implementation matches, it falls back to `_estimate_unsupported()`. Subclasses should override the type-specific private methods (e.g., `_estimate_qubo()`) rather than this one.

The input `qaoa_object` includes the training parameters ([`angles`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.generic_qaoa.QAOA.html#iqm.qaoa.generic_qaoa.QAOA.angles "iqm.qaoa.generic_qaoa.QAOA.angles")), which are typically used in estimation of the energy.

Parameters:  
**qaoa_object** ([*QAOA*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.generic_qaoa.QAOA.html#iqm.qaoa.generic_qaoa.QAOA "iqm.qaoa.generic_qaoa.QAOA")) – The [`QAOA`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.generic_qaoa.QAOA.html#iqm.qaoa.generic_qaoa.QAOA "iqm.qaoa.generic_qaoa.QAOA") object whose energy is to be estimated.

Returns:  
The estimated expected value of the Hamiltonian with the quantum state implied by the QAOA object.

Raises:  
[**TypeError**](https://docs.python.org/3.11/library/exceptions.html#TypeError "(in Python v3.11)") – If no registered implementation exists for the type of `qaoa_object`.

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

estimate_correlations_z(*qaoa_object*, *target_qubits*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/../../../../../../root/.local/share/uv/python/cpython-3.11.14-linux-x86_64-gnu/lib/python3.11/functools.py#L132-L163)\
estimate_correlations_z(*qaoa_object*, *target_qubits*)\
estimate_correlations_z(*qaoa_object*, *target_qubits*)  
Estimate the expected value of products of Z operators on `target_qubits`.

This method uses `singledispatchmethod()` to dispatch to a type-specific implementation based on the runtime type of `qaoa_object`. If no registered implementation matches, it falls back to `_estimate_unsupported()`. Subclasses should override the type-specific private methods rather than this one.

The input `qaoa_object` includes the training parameters ([`angles`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.generic_qaoa.QAOA.html#iqm.qaoa.generic_qaoa.QAOA.angles "iqm.qaoa.generic_qaoa.QAOA.angles")), which are used in estimation of the correlations. Some estimators (subclasses of [`EstimatorBackend`](#iqm.qaoa.backends.EstimatorBackend "iqm.qaoa.backends.EstimatorBackend")) may only be able to estimate the expectation values of at most quadratic products of Z’s.

Parameters:  
- **qaoa_object** ([*QAOA*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.generic_qaoa.QAOA.html#iqm.qaoa.generic_qaoa.QAOA "iqm.qaoa.generic_qaoa.QAOA")) – The [`QAOA`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.generic_qaoa.QAOA.html#iqm.qaoa.generic_qaoa.QAOA "iqm.qaoa.generic_qaoa.QAOA") object whose correlations are to be estimated.

- **target_qubits** ([*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")*\[LogQubit\]* *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")*\[LogQubit\]\]*) – The set of qubits on which the operators act. For example if one is interested in \\\langle Z_1 Z_4 Z_5 \rangle\\, then `target_qubits == {1, 4, 5}`. If one is interested in multiple different correlations, they may set `target_qubits` as a list of sets and get out a list of correlations. This is likely to be more efficient than repeatedly calling [`estimate_correlations_z()`](#iqm.qaoa.backends.EstimatorBackend.estimate_correlations_z "iqm.qaoa.backends.EstimatorBackend.estimate_correlations_z") with each one set of qubits at a time.

Returns:  
The estimated expected value of product of Z operators on given `target_qubits`. Or a list of those, if `target_qubits` was given as a list.

Raises:  
[**TypeError**](https://docs.python.org/3.11/library/exceptions.html#TypeError "(in Python v3.11)") – If no registered implementation exists for the type of `qaoa_object`.

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") \| [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]

Inheritance

![Inheritance diagram of iqm.qaoa.backends.EstimatorBackend](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-32911ab9512514e4acf48800d7e141c3c774244d.png)
