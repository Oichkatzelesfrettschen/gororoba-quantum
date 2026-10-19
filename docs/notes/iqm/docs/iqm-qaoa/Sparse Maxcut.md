> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/Sparse%20Maxcut.html](https://docs.iqm.tech/4.7/iqm-qaoa/Sparse%20Maxcut.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 95dc50850a147c4f42ce0186cedb8988a4ef474e78d52eb30801db60b8501f8b.

# Sparse Maxcut

The purpose of this notebook is to showcase the QAOA library working from the problem definition all the way to execution on a real hardware.

In particular, here we use QAOA to solve an instance of a random sparsely-connected max-cut problem.

```
from iqm.applications.maxcut import maxcut_generator
from iqm.qaoa.backends import EstimatorFromSampler, SamplerResonance
from iqm.qaoa.qubo_qaoa import QUBOQAOA
```

Maxcut is a graph problem, but internally the QAOA library converts it to a quadratic binary optimization problem (QUBO). We will solve a problem of size `problem_size`, i.e., this will be the size of the graph, the number of binary variables and also the number of qubits that we use. The number of `shots` is set to default maximum on Resonance.

```
problem_size = 14
shots = 20000
```

We create an instance of the max-cut problem of size `problem_size`, on a 3-regular random graph. We print out the largest, lowest and average energy of the model, calculated by brute-forcing over all possible bitstrings of length `problem_size`. This may be slow if `problem_size` has been set higher than ~30.

```
my_maxcut_problem = next(maxcut_generator(n=problem_size, n_instances=1, graph_family="regular", d=3))
print("Problem upper bound: ", my_maxcut_problem.upper_bound)
print("Problem lower bound: ", my_maxcut_problem.lower_bound)
print("Problem average energy: ", my_maxcut_problem.average_quality)
```

In the following, we set up the connection to Resonance and define a simulator backend of the Garnet and Sirius QPUs. We will run the QAOA on both and compare the results.

Note: in general, you also need to specify the ‘usage mode’. For running on a real machine (in pay-as-you-go usage mode), the url would change to https://resonance.iqm.tech/garnet. For a specific timeslot the url would change to https://resonance.iqm.tech/garnet:timeslot

```
import os

SERVER_URL = "https://resonance.iqm.tech"
QC_CRYSTAL = "garnet:mock"
QC_STAR = "sirius:mock"

# If the token isn't saved in the environment, replace this by the token as a string.
API_TOKEN = os.environ.get("IQM_RESONANCE_API_TOKEN")
```

Create the QUBO QAOA instance from the problem instance and train it. The `train` method has several possible parameters, but here the default setting is used (which uses analytical formulas since the QAOA has one layer).

```
my_qaoa = QUBOQAOA(problem=my_maxcut_problem, num_layers=1, initial_angles=[0.1, 0.2])
my_qaoa.train()
```

Once the QAOA is trained, we can use the QPU to sample from it and to use the samples for estimating the expected value of the Hamiltonian.

For that we need to define a *sampler* and an *estimator*. There are several other samplers and estimators available in the QAOA library. Here we use the sampler which samples from a given QPU (via Resonance) and the estimator which uses this sampler to provide samples from which the expected value of the Hamiltonian is calculated.

We don’t need the samples here for anything, so we’ll discard them.

```
crystal_qpu_sampler = SamplerResonance(token=API_TOKEN, server_url=SERVER_URL, quantum_computer=QC_CRYSTAL, transpiler="SparseTranspiler")
crystal_qpu_estimator = EstimatorFromSampler(crystal_qpu_sampler, shots=shots)
_ = my_qaoa.sample(crystal_qpu_sampler, shots=shots)  # This line is just to test if sampling works.
energy_on_crystal = my_qaoa.estimate(crystal_qpu_estimator)
print("Energy on crystal QPU:", energy_on_crystal)
```

Same as the above, except on the star QPU.

```
star_qpu_sampler = SamplerResonance(token=API_TOKEN, server_url=SERVER_URL, quantum_computer=QC_STAR, transpiler="MinimumVertexCover")
star_qpu_estimator = EstimatorFromSampler(star_qpu_sampler, shots=shots)
_ = my_qaoa.sample(star_qpu_sampler, shots=shots)  # This line is just to test if sampling works.
energy_on_star = my_qaoa.estimate(star_qpu_estimator)
print("Energy on star QPU:", energy_on_star)
```

Running circuits on the star uses fewer 2QB gates, but requires considerably larger circuit depth (because only one 2QB gate can be done at a time).
