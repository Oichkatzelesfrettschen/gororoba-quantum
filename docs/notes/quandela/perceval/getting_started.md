> Full piece: [https://perceval.quandela.net/docs/v1.3/getting_started.html](https://perceval.quandela.net/docs/v1.3/getting_started.html)
> Retrieved 2026-10-17T17:29Z by scripts/capture_qd_docs.py --perceval (urllib, pandoc); fetched HTML sha256 e29377aa1cd2eec8906dc4fcef5886e0a9b282ca89503518e3f51610fda495f1.

# Getting started

## What is Perceval?

Perceval is a toolbox containing generic functions and classes, built around an optimised native core (see [exqalibur](https://perceval.quandela.net/docs/v1.3/reference/exqalibur/index.html#exqalibur) code reference).

It offers tools to:

- Manipulate quantum states in the Fock space

  - Pure states ([FockState](https://perceval.quandela.net/docs/v1.3/reference/exqalibur/fockstate.html#fockstate), [StateVector](https://perceval.quandela.net/docs/v1.3/reference/exqalibur/statevector.html#statevector))

  - Mixed states ([SVDistribution](https://perceval.quandela.net/docs/v1.3/reference/exqalibur/statevector.html#svdistribution), [DensityMatrix](https://perceval.quandela.net/docs/v1.3/reference/utils/density_matrix.html#densitymatrix))

- Build a linear optics [Experiment](https://perceval.quandela.net/docs/v1.3/reference/components/experiment.html#experiment) containing

  - A unitary [Circuit](https://perceval.quandela.net/docs/v1.3/reference/components/circuit.html#circuit) composed of [Unitary Components](https://perceval.quandela.net/docs/v1.3/reference/components/unitary_components.html#unitary-components)

  - Some [Non-unitary Components](https://perceval.quandela.net/docs/v1.3/reference/components/non_unitary_components.html#non-unitary-components)

  - Feed-forward through [Feed-forward Configurators](https://perceval.quandela.net/docs/v1.3/reference/components/feed_forward_configurator.html#feed-forward-configurators)

  - Variable [parameters](https://perceval.quandela.net/docs/v1.3/reference/utils/parameter.html#parameter) and [expressions](https://perceval.quandela.net/docs/v1.3/reference/utils/expression.html#expression) to parametrise components

- Display circuits and data ([pdisplay](https://perceval.quandela.net/docs/v1.3/reference/rendering/pdisplay.html#pdisplay)), serialise them ([serialization](https://perceval.quandela.net/docs/v1.3/reference/serialization/index.html#serialization))

- Define real-world noise parameters applied in the input, the linear-optics circuit and the photon detectors ([Noise Model](https://perceval.quandela.net/docs/v1.3/reference/utils/noise_model.html#noise-model))

- Simulate these experiments through [different layers of simulations](https://perceval.quandela.net/docs/v1.3/notebooks/Computation_Tutorial.html#I.-Different-layers-of-simulation)

  - Perfect simulations with [Simulation Back-ends](https://perceval.quandela.net/docs/v1.3/backends.html#simulation-back-ends)

  - Noisy and non-unitary simulations with the [Simulator](https://perceval.quandela.net/docs/v1.3/reference/simulators/simulator.html#simulator) layer

- Control the flow of quantum computations and choose where they are run:

  - Locally with the [SimulatedComputer](https://perceval.quandela.net/docs/v1.3/reference/runtime/computer.html#simulatedcomputer), remotely with the [RemoteComputer](https://perceval.quandela.net/docs/v1.3/reference/runtime/computer.html#remotecomputer)

  - Manage your [jobs](https://perceval.quandela.net/docs/v1.3/reference/runtime/execution.html#execution) with the [ExecutionGroup](https://perceval.quandela.net/docs/v1.3/reference/runtime/execution_group.html#executiongroup)

## Installing Perceval

*Perceval* supports several *Python* versions (typically, [those that are not in “end-of-life”](https://devguide.python.org/versions/)). In a virtual environment of any *Python* supported version, a single `pip` command installs Perceval and all of its dependencies.

``` bash
$ pip install perceval-quandela
```

Warning

Pay attention that the *Python* package name is “perceval-quandela” and not “perceval”

Once the above command succeeds, you can start typing code in your favorite IDE!

## Hello world

The following example is a minimal code to simulate the [Hong–Ou–Mandel effect](https://en.wikipedia.org/wiki/Hong%E2%80%93Ou%E2%80%93Mandel_effect) on the user’s computer in a noisy situation, and retrieve both a sample count and exact probabilities computed by a strong simulation back-end.

``` default
>>> import perceval as pcvl
>>>
>>> experiment = pcvl.Experiment(pcvl.BS())          # In a perfect beam splitter experiment...
>>> experiment.with_input(pcvl.BasicState("|1,1>"))  # ... we inject one photon into each mode
>>> experiment.min_detected_photons_filter(1)  # Accept all output states containing at least 1 photon
>>>
>>> computer = pcvl.SimulatedComputer("SLOS")  # Use SLOS, a strong simulation back-end
>>> computer.noise = pcvl.NoiseModel(transmittance=0.05, indistinguishability=0.85)  # Define some noise level
>>>
>>> factory = pcvl.ExecutionFactory(computer, experiment)
>>> with computer.acquire():  # Good practice - may be used to warm the computer up
...     samples = factory.sample_count(10_000)['results']  # Ask to generate 10k samples, and get back only the raw results
...     probs = factory.probs()['results']  # Ask for the exact probabilities
>>> print(f"Samples: {samples}")
>>> print(f"Probabilities: {probs}")
Samples: {
  |2,0>: 117
  |0,2>: 147
  |1,0>: 4822
  |1,1>: 22
  |0,1>: 4892
}
Probabilities: {
  |2,0>: 0.011858974358974369
  |0,2>: 0.011858974358974369
  |1,1>: 0.0019230769230769245
  |1,0>: 0.48717948717948717
  |0,1>: 0.48717948717948717
}
```

Now that you can run some code, let’s continue with a tutorial to learn Perceval syntax.
