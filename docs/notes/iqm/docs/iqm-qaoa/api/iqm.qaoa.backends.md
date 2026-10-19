> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 db40938a0adde03ae1bf35742a19a625047db94e8b5c9e2c70987144506aa5b4.

# backends

Full path: iqm.qaoa.backends

Backends for calculating expectation values and generating samples from QAOA instances.

The backends are divided into two main categories:

- **EstimatorBackends**: Used for calculating expectation values of Hamiltonians and arbitrary ZZ…Z terms.

- **SamplerBackends**: Used for generating samples.

**Key Features:**

- **Dispatcher Methods**: The [`estimate()`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.EstimatorBackend.html#iqm.qaoa.backends.EstimatorBackend.estimate "iqm.qaoa.backends.EstimatorBackend.estimate") and [`sample()`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.SamplerBackend.html#iqm.qaoa.backends.SamplerBackend.sample "iqm.qaoa.backends.SamplerBackend.sample") methods use `@singledispatchmethod` to dynamically route calls to the appropriate implementation based on the type of the input QAOA object (e.g., [`QUBOQAOA`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.qubo_qaoa.QUBOQAOA.html#iqm.qaoa.qubo_qaoa.QUBOQAOA "iqm.qaoa.qubo_qaoa.QUBOQAOA"), [`HUBOQAOA`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.hubo_qaoa.HUBOQAOA.html#iqm.qaoa.hubo_qaoa.HUBOQAOA "iqm.qaoa.hubo_qaoa.HUBOQAOA")).

- **Extensibility**: New backends can be added by subclassing [`EstimatorBackend`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.EstimatorBackend.html#iqm.qaoa.backends.EstimatorBackend "iqm.qaoa.backends.EstimatorBackend") or [`SamplerBackend`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.SamplerBackend.html#iqm.qaoa.backends.SamplerBackend "iqm.qaoa.backends.SamplerBackend") and implementing the required methods.

Classes

|  |  |
|----|----|
| [`EstimatorBackend`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.EstimatorBackend.html#iqm.qaoa.backends.EstimatorBackend "iqm.qaoa.backends.EstimatorBackend") | The template class for estimator backends, i.e., those calculating the expected value of the Hamiltonian. |
| [`EstimatorFromSampler`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.EstimatorFromSampler.html#iqm.qaoa.backends.EstimatorFromSampler "iqm.qaoa.backends.EstimatorFromSampler") | The estimator class for calculating the expectation value using counts obtained from a sampler. |
| [`EstimatorQUIMB`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.EstimatorQUIMB.html#iqm.qaoa.backends.EstimatorQUIMB "iqm.qaoa.backends.EstimatorQUIMB") | The estimator class for calculating the expectation value using the tensor network package [`quimb`](https://quimb.readthedocs.io/en/latest/autoapi/quimb/index.html#module-quimb "(in quimb v0.1)"). |
| [`EstimatorSingleLayer`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.EstimatorSingleLayer.html#iqm.qaoa.backends.EstimatorSingleLayer "iqm.qaoa.backends.EstimatorSingleLayer") | Analytical estimator for \\p=1\\ QAOA using the closed-form expressions from \[[2](https://docs.iqm.tech/4.7/iqm-qaoa/references.html#id3 "Asier Ozaeta, Wim van Dam, and Peter L McMahon. Expectation values from the single-layer quantum approximate optimization algorithm on ising problems. Quantum Science and Technology, Dec 2020. arXiv:2012.03421.")\]. |
| [`EstimatorStateVector`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.EstimatorStateVector.html#iqm.qaoa.backends.EstimatorStateVector "iqm.qaoa.backends.EstimatorStateVector") | Exact estimator using Qiskit statevector simulation. |
| [`SamplerBackend`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.SamplerBackend.html#iqm.qaoa.backends.SamplerBackend "iqm.qaoa.backends.SamplerBackend") | The template for sampler backends, i.e., those returning samples from the QAOA. |
| [`SamplerRandomBitstrings`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.SamplerRandomBitstrings.html#iqm.qaoa.backends.SamplerRandomBitstrings "iqm.qaoa.backends.SamplerRandomBitstrings") | A sampler that ignores the QAOA and just produces random bitstrings of the correct length. |
| [`SamplerResonance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.SamplerResonance.html#iqm.qaoa.backends.SamplerResonance "iqm.qaoa.backends.SamplerResonance") | A sampler that runs the circuit on IQM Resonance and returns the result. |
| [`SamplerSimulation`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.SamplerSimulation.html#iqm.qaoa.backends.SamplerSimulation "iqm.qaoa.backends.SamplerSimulation") | A sampler that simulates the QAOA circuit in [`qiskit`](https://quantum.cloud.ibm.com/docs/api/qiskit/index#module-qiskit "(in Qiskit v2.5)"). |

Inheritance

![Inheritance diagram of iqm.qaoa.backends](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-4cab9f9195744d0c217c24f02820221cb4114d70.png)
