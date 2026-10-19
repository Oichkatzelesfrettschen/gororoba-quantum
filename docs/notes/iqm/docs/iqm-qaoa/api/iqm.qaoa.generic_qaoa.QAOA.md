> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.generic_qaoa.QAOA.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.generic_qaoa.QAOA.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 9dd5545edb69a38ed7909f2a9ead42373a60870b30024049f46705a95bdab525.

# QAOA

Module: [`iqm.qaoa.generic_qaoa`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.generic_qaoa.html#module-iqm.qaoa.generic_qaoa "iqm.qaoa.generic_qaoa")

*class* iqm.qaoa.generic_qaoa.QAOA(*problem*, *num_layers*, *\**, *betas=None*, *gammas=None*, *initial_angles=None*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/generic_qaoa.py#L41-L345)  
Bases: [`ABC`](https://docs.python.org/3.11/library/abc.html#abc.ABC "(in Python v3.11)"), [`Generic`](https://docs.python.org/3.11/library/typing.html#typing.Generic "(in Python v3.11)")\[`ProblemType`\]

The most generic QAOA abstract base class.

This abstract base class contains methods such as `_internal_angle_logic()` or [`linear_ramp_schedule()`](#iqm.qaoa.generic_qaoa.QAOA.linear_ramp_schedule "iqm.qaoa.generic_qaoa.QAOA.linear_ramp_schedule") that can be used by any type / flavor of QAOA.

Parameters:  
- **problem** (*ProblemType*) – The problem to be solved by the QAOA, its type narrowed-down by the specific type of QAOA used.

- **num_layers** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of QAOA layers.

- **betas** (*Sequence\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]* *\|* *np.ndarray* *\|* *None*) – An optional list of the initial *beta* angles of QAOA. Has to be provided together with `gammas`.

- **gammas** (*Sequence\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]* *\|* *np.ndarray* *\|* *None*) – An optional list of the initial *gamma* angles of QAOA. Has to be provided together with `betas`.

- **initial_angles** (*Sequence\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]* *\|* *np.ndarray* *\|* *None*) – An optional list of the initial QAOA angles as one variable. Shouldn’t be provided together with either `betas` or `gammas`. The *gamma* and *beta* angles are interleaved, so that the first pair of entries corresponds to \\\gamma_1\\ and \\\beta_1\\ (the angles of the first QAOA layer). The second pair of entries corresponds to \\\gamma_2\\ and \\\beta_2\\, etc. …

Raises:  
- [**TypeError**](https://docs.python.org/3.11/library/exceptions.html#TypeError "(in Python v3.11)") – If the provided `num_layers` is not an integer.

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the provided `num_layers` is not positive.

Attributes

|  |  |
|----|----|
| [`angles`](#iqm.qaoa.generic_qaoa.QAOA.angles "iqm.qaoa.generic_qaoa.QAOA.angles") | The angles in the QAOA, including [`betas`](#iqm.qaoa.generic_qaoa.QAOA.betas "iqm.qaoa.generic_qaoa.QAOA.betas") and [`gammas`](#iqm.qaoa.generic_qaoa.QAOA.gammas "iqm.qaoa.generic_qaoa.QAOA.gammas") in one [`ndarray`](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"). |
| [`betas`](#iqm.qaoa.generic_qaoa.QAOA.betas "iqm.qaoa.generic_qaoa.QAOA.betas") | The beta angles in the QAOA, controlling the mixer Hamiltonian terms. |
| [`gammas`](#iqm.qaoa.generic_qaoa.QAOA.gammas "iqm.qaoa.generic_qaoa.QAOA.gammas") | The gamma angles in the QAOA, controlling the problem Hamiltonian terms. |
| [`num_layers`](#iqm.qaoa.generic_qaoa.QAOA.num_layers "iqm.qaoa.generic_qaoa.QAOA.num_layers") | The number of QAOA layers. |
| [`num_qubits`](#iqm.qaoa.generic_qaoa.QAOA.num_qubits "iqm.qaoa.generic_qaoa.QAOA.num_qubits") | The number of qubits, equal to the number of problem variables if no special encoding is used. |
| [`problem`](#iqm.qaoa.generic_qaoa.QAOA.problem "iqm.qaoa.generic_qaoa.QAOA.problem") | The problem instance associated with the QAOA. |
| [`trained`](#iqm.qaoa.generic_qaoa.QAOA.trained "iqm.qaoa.generic_qaoa.QAOA.trained") | A boolean flag indicating whether the QAOA has been trained at all or not. |

Methods

|  |  |
|----|----|
| [`estimate`](#iqm.qaoa.generic_qaoa.QAOA.estimate "iqm.qaoa.generic_qaoa.QAOA.estimate") | The method for taking estimates of the expected value of the Hamiltonian from the QAOA circuit. |
| [`linear_ramp_schedule`](#iqm.qaoa.generic_qaoa.QAOA.linear_ramp_schedule "iqm.qaoa.generic_qaoa.QAOA.linear_ramp_schedule") | The "linear ramp schedule" for setting the QAOA angles. |
| [`sample`](#iqm.qaoa.generic_qaoa.QAOA.sample "iqm.qaoa.generic_qaoa.QAOA.sample") | The method for taking samples (i.e., measurement results) from the QAOA circuit. |
| [`train`](#iqm.qaoa.generic_qaoa.QAOA.train "iqm.qaoa.generic_qaoa.QAOA.train") | The function that performs the training of the angles. |

*property* trained*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")*  
A boolean flag indicating whether the QAOA has been trained at all or not.

*property* num_layers*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
The number of QAOA layers.

At first this is set to the value given at initialization, but it may be modified later (which has an effect on [`angles`](#iqm.qaoa.generic_qaoa.QAOA.angles "iqm.qaoa.generic_qaoa.QAOA.angles")).

*property* problem*: ProblemType*  
The problem instance associated with the QAOA.

*property* num_qubits*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
The number of qubits, equal to the number of problem variables if no special encoding is used.

*property* betas*: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*  
The beta angles in the QAOA, controlling the mixer Hamiltonian terms.

*property* gammas*: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*  
The gamma angles in the QAOA, controlling the problem Hamiltonian terms.

*property* angles*: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*  
The angles in the QAOA, including [`betas`](#iqm.qaoa.generic_qaoa.QAOA.betas "iqm.qaoa.generic_qaoa.QAOA.betas") and [`gammas`](#iqm.qaoa.generic_qaoa.QAOA.gammas "iqm.qaoa.generic_qaoa.QAOA.gammas") in one [`ndarray`](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)").

linear_ramp_schedule(*delta_beta*, *delta_gamma*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/generic_qaoa.py#L240-L259)  
The “linear ramp schedule” for setting the QAOA angles.

Formulas adapted from \[[3](https://docs.iqm.tech/4.7/iqm-qaoa/references.html#id2 "J. A. Montanez-Barrera and Kristel Michielsen. Towards a universal QAOA protocol: evidence of a scaling advantage in solving some combinatorial optimization problems. https://arxiv.org/abs/2405.09169, May 2024.")\]. It can be used either instead of training the QAOA or as a starting set of angles. The above work uses `delta_beta` and `delta_gamma` values around 0.5, but the best choice for these values depends on the problem Hamiltonian.

Parameters:  
- **delta_beta** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – The maximum beta angle.

- **delta_gamma** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – The maximum gamma angle.

Return type:  
None

train(*estimator=None*, *\*\*kwargs*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/generic_qaoa.py#L261-L303)  
The function that performs the training of the angles.

The training modifies [`angles`](#iqm.qaoa.generic_qaoa.QAOA.angles "iqm.qaoa.generic_qaoa.QAOA.angles") in-place using the [`minimize()`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html#scipy.optimize.minimize "(in SciPy v1.17.0)") function from [`scipy`](https://docs.scipy.org/doc/scipy/index.html#module-scipy "(in SciPy v1.17.0)"). The training uses the provided `estimator` or a default one (implemented by QAOA’s subclasses).

Parameters:  
- **estimator** ([*EstimatorBackend*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.EstimatorBackend.html#iqm.qaoa.backends.EstimatorBackend "iqm.qaoa.backends.EstimatorBackend") *\|* *None*) – An estimator [`EstimatorBackend`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.EstimatorBackend.html#iqm.qaoa.backends.EstimatorBackend "iqm.qaoa.backends.EstimatorBackend") to be used to calculate expectation values for the minimization. If `None`, a default one is picked, but this is depends on the QAOA subclass.

- **\*\*kwargs** (*Any*) – The keyword arguments to pass to the inner minimization [`scipy.optimize.minimize()`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html#scipy.optimize.minimize "(in SciPy v1.17.0)").

Return type:  
None

sample(*sampler*, *shots=20000*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/generic_qaoa.py#L305-L324)  
The method for taking samples (i.e., measurement results) from the QAOA circuit.

Takes a [`SamplerBackend`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.SamplerBackend.html#iqm.qaoa.backends.SamplerBackend "iqm.qaoa.backends.SamplerBackend") and uses it to get `shots` samples. The backend is responsible for building the quantum circuit and taking the measurements (or obtaining the samples some other way), using information from the [`QAOA`](#iqm.qaoa.generic_qaoa.QAOA "iqm.qaoa.generic_qaoa.QAOA") object that is passed to its method [`sample()`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.SamplerBackend.html#iqm.qaoa.backends.SamplerBackend.sample "iqm.qaoa.backends.SamplerBackend.sample").

Parameters:  
- **sampler** ([*SamplerBackend*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.SamplerBackend.html#iqm.qaoa.backends.SamplerBackend "iqm.qaoa.backends.SamplerBackend")) – The sampler to use to generate samples. The sampler is an instance of a subclass of [`SamplerBackend`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.SamplerBackend.html#iqm.qaoa.backends.SamplerBackend "iqm.qaoa.backends.SamplerBackend") with a [`sample()`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.SamplerBackend.html#iqm.qaoa.backends.SamplerBackend.sample "iqm.qaoa.backends.SamplerBackend.sample") method.

- **shots** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of shots to be taken.

Returns:  
A dictionary whose keys are bitstrings representing the samples and whose values are their respective frequencies, so that the sum of the values of the dictionary equals to `shots`.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]

estimate(*estimator*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/generic_qaoa.py#L326-L342)  
The method for taking estimates of the expected value of the Hamiltonian from the QAOA circuit.

Takes a [`EstimatorBackend`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.EstimatorBackend.html#iqm.qaoa.backends.EstimatorBackend "iqm.qaoa.backends.EstimatorBackend") and uses it to get estimates of the expected value. The backend takes all the necessary information from the [`QAOA`](#iqm.qaoa.generic_qaoa.QAOA "iqm.qaoa.generic_qaoa.QAOA") object that is passed to its method [`estimate()`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.EstimatorBackend.html#iqm.qaoa.backends.EstimatorBackend.estimate "iqm.qaoa.backends.EstimatorBackend.estimate").

Parameters:  
**estimator** ([*EstimatorBackend*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.EstimatorBackend.html#iqm.qaoa.backends.EstimatorBackend "iqm.qaoa.backends.EstimatorBackend")) – The estimator used to get the expected value. The estimator is an instance of a subclass of [`EstimatorBackend`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.EstimatorBackend.html#iqm.qaoa.backends.EstimatorBackend "iqm.qaoa.backends.EstimatorBackend") with a method [`estimate()`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.EstimatorBackend.html#iqm.qaoa.backends.EstimatorBackend.estimate "iqm.qaoa.backends.EstimatorBackend.estimate") of the appropriate signature.

Returns:  
An estimate of the expectation value fo the Hamiltonian. Not normalized in any way.

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

Inheritance

![Inheritance diagram of iqm.qaoa.generic_qaoa.QAOA](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-e61838c227929b999e6e4af4003e189b965910f0.png)
