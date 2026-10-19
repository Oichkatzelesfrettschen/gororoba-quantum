> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.EstimatorFromSampler.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.EstimatorFromSampler.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f3997e1853b81d28dca530e23c73b96e16f78223c3d21e1fa4aa16feceba3c6d.

# EstimatorFromSampler

Module: [`iqm.qaoa.backends`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.html#module-iqm.qaoa.backends "iqm.qaoa.backends")

*class* iqm.qaoa.backends.EstimatorFromSampler(*sampler*, *shots*, *cvar=None*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/backends.py#L597-L764)  
Bases: [`EstimatorBackend`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.EstimatorBackend.html#iqm.qaoa.backends.EstimatorBackend "iqm.qaoa.backends.EstimatorBackend")

The estimator class for calculating the expectation value using counts obtained from a sampler.

Takes an instance of a subclass of [`SamplerBackend`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.SamplerBackend.html#iqm.qaoa.backends.SamplerBackend "iqm.qaoa.backends.SamplerBackend") and uses it to generate samples from the QAOA. These energy of these samples is then calculated classically and averaged-out to produce an estimate of the expectation value of the Hamiltonian. If `cvar` is provided, the estimator returns not the average of the energies, but its CVaR at the `cvar` threshold.

Parameters:  
- **sampler** ([*SamplerBackend*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.SamplerBackend.html#iqm.qaoa.backends.SamplerBackend "iqm.qaoa.backends.SamplerBackend")) – The sampler to produce the samples.

- **shots** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of shots that should be produced with the sampler.

- **cvar** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* *None*) – The threshold used to calculate CVaR (if provided).

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If `cvar` is provided, but it’s not between 0 (excluded) and 1 (included).

Methods

Inheritance

![Inheritance diagram of iqm.qaoa.backends.EstimatorFromSampler](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-a77f77a3e37205ab5bfa85a56a79c065724499d4.png)
