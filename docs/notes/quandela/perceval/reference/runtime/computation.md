> Full piece: [https://perceval.quandela.net/docs/v1.3/reference/runtime/computation.html](https://perceval.quandela.net/docs/v1.3/reference/runtime/computation.html)
> Retrieved 2026-10-17T17:29Z by scripts/capture_qd_docs.py --perceval (urllib, pandoc); fetched HTML sha256 360db1ef0857052fdfb0302966be626ed5d19e5db0df3c301f62a45b277b2433.

# Computation

A `Computation` describes what should be computed, independently of the [Computer](https://perceval.quandela.net/docs/v1.3/reference/runtime/computer.html#computer) that will perform the work. It combines a [Command](https://perceval.quandela.net/docs/v1.3/reference/runtime/command.html#command), which defines the requested result and its accepted parameters, with the [Experiment](https://perceval.quandela.net/docs/v1.3/reference/components/experiment.html#experiment) with which that command will run.

Computations are normally created by an `ExecutionFactory`:

``` default
>>> import perceval as pcvl
>>>
>>> experiment = pcvl.Experiment(pcvl.BS())
>>> experiment.with_input(pcvl.BasicState("|1,1>"))
>>> computer = pcvl.SimulatedComputer("SLOS")
>>> factory = pcvl.ExecutionFactory(computer, experiment)
>>> computation = factory.build_computation("sample_count")
```

They can also be created directly from a command and an experiment:

``` default
>>> computation = pcvl.Computation(computer.get_command("sample_count"), experiment)
```

## Parameters

The parameters accepted by a computation are defined by its command. `add_params()` accepts positional or keyword arguments, validates their names and types against the command signature, and adds them to the `parameters` dictionary:

``` default
>>> computation.add_params(max_samples=10_000, max_shots=100_000)
>>> computation.parameters
{'max_samples': 10000, 'max_shots': 100000}
```

Calling `validate()` checks that every mandatory command parameter has been provided. It is also called automatically before a computer executes the computation.

## Standard Commands

The `"probs"`, `"sample_count"` and `"samples"` [Commands](https://perceval.quandela.net/docs/v1.3/reference/runtime/command.html#command) are standardized for all [Computers](https://perceval.quandela.net/docs/v1.3/reference/runtime/computer.html#computer). Most of their parameters are shared, so it should be possible to use the same `Computation` on any [Computer](https://perceval.quandela.net/docs/v1.3/reference/runtime/computer.html#computer) for these commands.

## Class reference

*class* perceval.runtime.computation.Computation(*command*, *experiment*)  
Descriptor of what we want to compute. This is meant to be fully independent of how we will get the results for it

Parameters:  
- **command** ([`Command`](https://perceval.quandela.net/docs/v1.3/reference/runtime/command.html#perceval.runtime.command.Command "perceval.runtime.command.Command")) – A command to do, describing what kind of results we want and the allowed parameters

- **experiment** ([`Experiment`](https://perceval.quandela.net/docs/v1.3/reference/components/experiment.html#perceval.components.experiment.Experiment "perceval.components.experiment.Experiment")) – The Experiment we want to compute results for

add_params(*\*args*, *\*\*kwargs*)  
Adds or replace parameters with the given values, following the signature given by the command

Parameters:  
- **args** – The user given positional arguments

- **kwargs** – The user given keyword arguments

Return type:  
`None`

validate()  
Checks that all non-optional parameters are filled

Raises:  
**ValueError** – if parameters are not correct

# ComputationIterator

A `ComputationIterator` describes several independent variants of one base `Computation`. Each iteration can change a supported subset of the experiment or computation parameters. This is useful for parameter sweeps because the variants keep the same [Execution](https://perceval.quandela.net/docs/v1.3/reference/runtime/execution.html#execution).

An iterator can be created using the factory (in which case creating an [Execution](https://perceval.quandela.net/docs/v1.3/reference/runtime/execution.html#execution) directly creates it with a `ComputationIterator`):

``` default
>>> factory = pcvl.ExecutionFactory(computer, experiment)
>>> factory.add_iteration(input_state=pcvl.BasicState("|1,1>"))
>>> factory.add_iteration(input_state=pcvl.BasicState("|2,0>"), max_samples=2_000)
>>> computation = factory.build_computation("sample_count")
>>> computation.add_params(max_samples = 1_000)
```

An iterator can also be created directly:

``` default
>>> base_computation = pcvl.Computation(computer.get_command("sample_count"), experiment)
>>> base_computation.add_params(max_samples=1_000)
>>> computation_iterator = pcvl.ComputationIterator(base_computation)
>>> computation_iterator.add_iteration(input_state=pcvl.BasicState("|1,1>"))
>>> computation_iterator.add_iteration(input_state=pcvl.BasicState("|2,0>"), max_samples=2_000)
```

The supported iteration parameters are:

- `circuit_params`: numerical values for named circuit parameters

- `input_state`: the input `BasicState`

- `min_detected_photons`: minimum accepted photon count

- `max_samples`: maximum number of samples to collect

- `max_shots`: maximum number of shots to perform

- `postselect`: a [`PostSelect`](https://perceval.quandela.net/docs/v1.3/reference/exqalibur/postselect.html#perceval.utils.postselect.PostSelect "perceval.utils.postselect.PostSelect") condition

Iteration parameters are checked when `add_iteration()` is called. Iterating over the object yields a new, independent `Computation` for each set of parameters, leaving the base computation unchanged:

``` default
>>> for computation in computation_iterator:
...     print(computation)
```

When an iterator is executed, its output dictionary contains a `"results_list"` entry. Results appear in iteration order, and each result includes the iteration parameters that produced it.

The recommended way to prepare an iterator is through [`ExecutionFactory`](https://perceval.quandela.net/docs/v1.3/reference/runtime/execution_factory.html#perceval.runtime.execution_factory.ExecutionFactory "perceval.runtime.execution_factory.ExecutionFactory"), which builds the iterator automatically when iterations have been added:

``` default
>>> factory.add_iteration(input_state=pcvl.BasicState("|1,1>"))
>>> factory.add_iteration(input_state=pcvl.BasicState("|2,0>"))
>>> execution = factory.sample_count
>>> isinstance(execution.computation, pcvl.ComputationIterator)
True
```

## Class reference

*class* perceval.runtime.computation_iterator.ComputationIterator(*base_computation*)  
A computation consisting of several independent computations, where only a few parameters can change.

This class modifies the results dict so that each individual result is inserted to a “results_list” field.

add_iteration(*\*\*kwargs*)  
Add a single iteration to future executions.

Parameters:  
**kwargs** –

List of accepted keywords:

- circuit_params: dict containing pairs (parameter_name: str - value : number)

- input_state: BasicState

- min_detected_photons: int

- max_samples: int

- max_shots: int

- postselect: PostSelect

- compilation_seed: int

add_params(*\*args*, *\*\*kwargs*)  
Adds or replace parameters of the common computation with the given values, following the signature given by the command

Parameters:  
- **args** – The user given positional arguments

- **kwargs** – The user given keyword arguments

Return type:  
`None`

clear_iterations()  
Clear all prepared iterations.

make_inserter(*out*)  
Parameters:  
**out** (`dict`) – The place where to store the results of the computation

Return type:  
`Callable`\[\[`dict`\], `None`\]

Returns:  
A callable that can be used to add results to `out`
