> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/Training%20the%20QAOA.html](https://docs.iqm.tech/4.7/iqm-qaoa/Training%20the%20QAOA.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6bf90ef87662b58473c4e079150a03c27af0c874b7fdb719e6b71da2991c0069.

# Training the QAOA

In this notebook we showcase (and compare) various strategies of training the QAOA, that is finding the optimal values for the variational parameters (also known as QAOA *angles*).

We start by generating a quasi-random instance of the maxcut problem (with 10 nodes).

```
from iqm.applications.maxcut import maxcut_generator

maxcut = next(maxcut_generator(n=10, n_instances=1, graph_family="erdos-renyi", p=0.5, seed=420))
```

Generate a QAOA instance from the problem instance. We use the `TreeQAOA` class, which is identical to the `QUBOQAOA` class, but it contains one extra way to “train” the QAOA parameters.

```
from iqm.qaoa.tree_qaoa import TreeQAOA

# Using the standard notation for QAOA angles, the ``initial_angles`` are [gamma, beta] respectively.
qaoa = TreeQAOA(problem=maxcut, num_layers=1, initial_angles=[0.1, 0.1])
```

For training the QAOA, we will use various *estimators*. An estimator is a function (technically a class with a method) which takes a QAOA object and calculates/estimates the expectation value of the Hamiltonian. Similarly, a *sampler* takes a QAOA object and generates samples (measurement results) of possible solutions.

Here we also set up a variable `results` to store the results of our experiments, for comparison. It’s a dictionary of dictionaries, keyed first by the training method and then by the QAOA number of layers.

```
from iqm.qaoa.backends import (
    EstimatorFromSampler,
    EstimatorSingleLayer,
    EstimatorStateVector,
    SamplerResonance,
    SamplerSimulation,
)

results: dict[str, dict[int, float]] = (
    {}
)  # A dictionary for storing the results (to make comparison easier at the end).
results["sl"] = {}  # Single-layer estimator.
results["sv"] = {}  # Statevector estimator.
results["sim"] = {}  # Estimator from sampler, samples obtained by simulation.
results["sim_cvar"] = {}  # Estimator from sampler, samples obtained by simulation, using CVaR instead of mean.
results["res"] = {}  # Estimator from sampler, samples obtained from Resonance.
results["tree"] = {}  # Angles set by the tree schedule (no real training).
```

We start with `EstimatorSingleLayer`. For single-layer QAOA, the expectation values of 1- and 2-qubit operators can be calculated analytically. This estimator does the calculation.

```
estimator_single_layer = EstimatorSingleLayer()

qaoa.train(estimator=estimator_single_layer)  # Here the QAOA is trained.
results["sl"][1] = estimator_single_layer.estimate(qaoa)
print("Expected value of the Hamiltonian after training with ``EstimatorSingleLayer``:", results["sl"][1])
```

Next, we train using `EstimatorStateVector`. This estimator runs the statevector simulation of the QAOA circuit to calculate the expectation value of the Hamiltonian.

```
estimator_statevector = EstimatorStateVector()

qaoa.angles = [0.1, 0.1]  # Reset the QAOA angles (to make comparison of training methods fair).
qaoa.train(estimator=estimator_statevector)  # Here the QAOA is trained.
results["sv"][1] = estimator_statevector.estimate(qaoa)
print("Expected value of the Hamiltonian after training with ``EstimatorStateVector``:", results["sv"][1])
```

Next, we train using `EstimatorFromSampler` together with `SamplerSimulation`. This estimator calls a given sampler and uses the obtained samples to estimate the expectation value (by calculating the energy of each of the samples and averaging them out). The `SamplerSimulation` runs the simulation of the QAOA circuit, including the measurements.

```
sampler_from_simulation = SamplerSimulation()  # By default, it initializes with AerSimulator(method="statevector")
estimator_from_simulation = EstimatorFromSampler(sampler=sampler_from_simulation, shots=20000)

qaoa.angles = [0.1, 0.1]  # Reset the QAOA angles (to make comparison of training methods fair).
qaoa.train(estimator=estimator_from_simulation)  # Here the QAOA is trained.
results["sim"][1] = estimator_from_simulation.estimate(qaoa)
print("Expected value using ``EstimatorFromSampler`` with ``SamplerSimulation``:", results["sim"][1])
```

Next, we again use `EstimatorFromSampler` together with `SamplerSimulation`. But this time we calculate not the *expectation value*, but the *conditional value at risk* at `0.1` level. We use this value in training the QAOA, possibly changing the performance.

```
estimator_from_simulation_cvar = EstimatorFromSampler(sampler=sampler_from_simulation, shots=20000, cvar=0.1)

qaoa.angles = [0.1, 0.1]  # Reset the QAOA angles (to make comparison of training methods fair).
qaoa.train(estimator=estimator_from_simulation_cvar)  # Here the QAOA is trained.
results["sim_cvar"][1] = estimator_from_simulation_cvar.estimate(qaoa)
print(
    "Conditional value at risk at 0.1 level using ``EstimatorFromSampler`` with ``SamplerSimulation``:",
    results["sim_cvar"][1],
)
```

Next, we train using `EstimatorFromSampler` again, but this time together with `SamplerResonance`. This sampler actually runs the circuit via Resonance, IQM’s cloud quantum computing platform.

**WARNING**

When running training using this estimator, Resonance is used for every training cycle, potentially taking a lot of time (even when using a mock QC)!

The `if` clause surrounding the cell makes sure that it’s skipped during testing (because it’s too slow).

```
import os  # Needed to get the Resonance token from the environmental variable.

if "END_TO_END_TESTING" not in os.environ:
    sampler_from_resonance = SamplerResonance(
        token=os.environ.get("IQM_RESONANCE_API_TOKEN"),
        # Remove the ':mock' part to run on real QC.
        server_url="https://resonance.iqm.tech",
        quantum_computer="garnet:mock",
        transpiler="SparseTranspiler",
    )
    estimator_from_resonance = EstimatorFromSampler(sampler=sampler_from_resonance, shots=20000)

    qaoa.angles = [0.1, 0.1]  # Reset the QAOA angles (to make comparison of training methods fair).
    qaoa.train(estimator=estimator_from_resonance)  # Here the QAOA is trained.
    results["res"][1] = estimator_from_resonance.estimate(qaoa)
    print("Expected value using ``EstimatorFromSampler`` with ``SamplerResonance``:", results["res"][1])
```

Now we “train” the angles by setting them to the *Tree QAOA* angles. The Tree QAOA angles are the optimal angles for problems on regular infinite random graphs, where the neighborhood of each node is a tree graph. These angles are pre-calculated for various values of graph regularity and parameters of the Hamiltonian. The method `set_tree_angles` looks at the parameters of our problem and sets the QAOA angles to the corresponding Tree QAOA angles.

While these angles aren’t likely the most optimal angles for our problem, they are likely to produce good results and it allows us to skip conventional QAOA training completely.

[More reading on Tree QAOA](https://arxiv.org/abs/2406.14618)

```
qaoa.angles = [0.1, 0.1]  # Reset the QAOA angles (to make comparison of training methods fair).
qaoa.set_tree_angles()  # The method gets all the necessary info from the ``qaoa`` object.
results["tree"][1] = estimator_single_layer.estimate(qaoa)
print(
    "Expected value using ``EstimatorSingleLayer`` after setting the angles with ``set_tree_angles``:",
    results["tree"][1],
)
```

For comparison we now repeat all of the above (except for `EstimatorSingleLayer`) for QAOA with 2 layers and summarize the data in a table.

```
qaoa.num_layers = 2  # The extra QAOA parameters will be padded with zeros.

# After increasing the number of layers, the QAOA angles are [gamma1, beta1, bamma2, beta2].
# The same pattern holds for more layers. They can also be set separately using ``qaoa.betas = [beta1, beta2]``

qaoa.angles = [0.1, 0.1, 0.1, 0.1]  # Reset the QAOA angles (to make comparison of training methods fair).
qaoa.train(estimator=estimator_statevector)  # Here the QAOA is trained.
results["sv"][2] = estimator_statevector.estimate(qaoa)

qaoa.angles = [0.1, 0.1, 0.1, 0.1]  # Reset the QAOA angles (to make comparison of training methods fair).
qaoa.train(estimator=estimator_from_simulation)  # Here the QAOA is trained.
results["sim"][2] = estimator_from_simulation.estimate(qaoa)

qaoa.angles = [0.1, 0.1, 0.1, 0.1]  # Reset the QAOA angles (to make comparison of training methods fair).
qaoa.train(estimator=estimator_from_simulation_cvar)  # Here the QAOA is trained.
results["sim_cvar"][2] = estimator_from_simulation_cvar.estimate(qaoa)

if "END_TO_END_TESTING" not in os.environ:  # Again, skip this if we're testing.
    qaoa.angles = [0.1, 0.1, 0.1, 0.1]  # Reset the QAOA angles (to make comparison of training methods fair).
    qaoa.train(estimator=estimator_from_resonance)  # Here the QAOA is trained.
    results["res"][2] = estimator_from_resonance.estimate(qaoa)

qaoa.angles = [0.1, 0.1, 0.1, 0.1]  # Reset the QAOA angles (to make comparison of training methods fair).
qaoa.set_tree_angles()
results["tree"][2] = estimator_statevector.estimate(
    qaoa
)  # The statevector estimator is the most accurate one, so it's used here.
```

```
from IPython.display import HTML, display

# Row labels and column labels
methods = sorted(results.keys())
# For each method, there is an inner dict of the format p:exp_val
ps = sorted({p for inner_dict in results.values() for p in inner_dict})

# Build the table
html = "<table border='1' style='border-collapse: collapse;'>"
html += "<tr><th>Training Method</th>" + "".join(f"<th>p = {p}</th>" for p in ps) + "</tr>"

method_names = {
    "sv": "Statevector",
    "sl": "Single Layer",
    "sim": "Simulated Samples",
    "sim_cvar": "Simulated Samples, CVaR",
    "res": "Resonance Samples",
    "tree": "Tree Schedule",
}  # Just longer names for the methods, for a nicer table.

for method in methods:
    html += f"<tr><th>{method_names[method]}</th>"
    for p in ps:
        exp_val = results[method].get(p)
        exp_val_str = f"{exp_val:.4f}" if exp_val is not None else "N/A"
        html += f"<td>{exp_val_str}</td>"
    html += "</tr>"

html += "</table>"

display(HTML(html))
```

We expect the `Statevector`, `Simulated Samples` and the `Single Layer` methods to perform the best (although none of them is scalable).

Using `CVaR` instead of the mean gives better results, but this is expected, given that we’re looking at a tail of a distribution. Whether it actually helps in training the QAOA is not clear.

We expect all methods to improve with increasing `p`.
