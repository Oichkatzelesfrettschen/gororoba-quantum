> Full piece: [https://perceval.quandela.net/docs/v1.3/reference/runtime/execution_factory.html](https://perceval.quandela.net/docs/v1.3/reference/runtime/execution_factory.html)
> Retrieved 2026-10-25T09:12Z by scripts/capture_qd_docs.py --perceval (urllib, pandoc); fetched HTML sha256 5301607c5fb949585def3d8d04a7237ad81edeeb36c076864fc9af2271e3b114.

# ExecutionFactory

An `ExecutionFactory` creates [Computations](https://perceval.quandela.net/docs/v1.3/reference/runtime/legacy/remote_processor.html#computation), [ComputationIterators](https://perceval.quandela.net/docs/v1.3/reference/runtime/computation.html#computationiterator), and [Executions](https://perceval.quandela.net/docs/v1.3/reference/runtime/execution.html#execution) for a fixed [Computer](https://perceval.quandela.net/docs/v1.3/reference/runtime/computer.html#computer) and [Experiment](https://perceval.quandela.net/docs/v1.3/reference/components/experiment.html#experiment). It is the usual entry point for requesting probabilities or samples without constructing these runtime objects manually.

## Creating a factory

Pass the computer that will perform the work and the experiment to compute:

``` default
>>> import perceval as pcvl
>>>
>>> experiment = pcvl.Experiment(pcvl.BS())
>>> experiment.with_input(pcvl.BasicState("|1,1>"))
>>> computer = pcvl.SimulatedComputer("SLOS")
>>> factory = pcvl.ExecutionFactory(computer, experiment)
```

For a [RemoteComputer](https://perceval.quandela.net/docs/v1.3/reference/runtime/computer.html#remotecomputer), `max_shots_per_call` is mandatory. It provides a positive default upper bound on the shots used by every computation built by the factory:

``` default
>>> communication_layer = pcvl.QuandelaCommunicationLayer("sim:belenos")
>>> remote_computer = pcvl.RemoteComputer(communication_layer)
>>> remote_factory = pcvl.ExecutionFactory(
...     remote_computer,
...     experiment,
...     max_shots_per_call=100_000,
... )
```

## Standard commands

The factory exposes the three standard [Commands](https://perceval.quandela.net/docs/v1.3/reference/runtime/command.html#command) as properties:

- `probs` creates an execution that computes output probabilities.

- `samples` creates an execution that returns individual output samples.

- `sample_count` creates an execution that groups samples by state and occurrence count.

Accessing a property creates a fresh, unsent execution. Execution parameters can then be supplied when it is run:

``` default
>>> sample_count = factory.sample_count
>>> with computer.acquire():
...     results = sample_count(max_samples=10_000)
```

Because every property access produces a new object, executions with different parameters can be prepared independently:

``` default
>>> short_run = factory.sample_count
>>> long_run = factory.sample_count
>>> short_run is long_run
False
```

## Custom commands

Commands registered by the computer are exposed dynamically using their command name. For example, if a provider’s computer advertises a `custom_command`, it can be accessed as follows:

``` default
>>> custom_execution = factory.custom_command
```

Use `Computer.available_commands` to discover the names supported by a computer.

## Building computations and executions

`build_computation()` creates a [Computation](https://perceval.quandela.net/docs/v1.3/reference/runtime/legacy/remote_processor.html#computation) for a named command without wrapping it in an execution. `build_execution()` then associates a computation with the factory’s computer:

``` default
>>> computation = factory.build_computation("sample_count")
>>> computation.add_params(max_samples=10_000)
>>> execution = factory.build_execution(computation)
```

The factory’s `default_job_name` is copied to every execution created afterward when it is not `None`:

``` default
>>> factory.default_job_name = "my sampling run"
>>> execution = factory.sample_count
>>> execution.name
'my sampling run'
```

## Iterations

Iterations describe several variants of the base computation. Add them individually with `add_iteration()` or in a list with `add_iteration_list()`:

``` default
>>> factory.add_iteration(
...     input_state=pcvl.BasicState("|1,1>"),
...     min_detected_photons=1,
... )
>>> factory.add_iteration_list([
...     {
...         "input_state": pcvl.BasicState("|2,0>"),
...         "min_detected_photons": 1,
...         "max_samples": 2_000,
...     },
... ])
```

When at least one iteration is stored, `build_computation()` and the command properties build a [ComputationIterator](https://perceval.quandela.net/docs/v1.3/reference/runtime/computation.html#computationiterator) instead of a single computation:

``` default
>>> execution = factory.sample_count
>>> isinstance(execution.computation, pcvl.ComputationIterator)
True
>>> factory.n_iterations
2
```

The supported iteration keys are `circuit_params`, `input_state`, `min_detected_photons`, `max_samples`, `max_shots`, and `postselect`. They are validated when a computation is built.

Iterations remain in the factory and affect every later computation until `clear_iterations()` is called:

``` default
>>> factory.clear_iterations()
>>> factory.n_iterations
0
>>> isinstance(factory.build_computation("sample_count"), pcvl.Computation)
True
```

An execution backed by a computation iterator returns its individual results in the `"results_list"` field, in the same order as the iterations.

## Class reference

*class* perceval.runtime.execution_factory.ExecutionFactory(*computer*, *experiment*, *max_shots_per_call=None*)  
Build computations and executions for a computer and an experiment.

The factory exposes the standard `probs`, `samples`, and `sample_count` commands as properties. Accessing one of these properties creates a new `Execution`. Commands registered by a custom computer are exposed dynamically in the same way (but will not get autocompletion from your IDE).

Iterations added to the factory are included in every subsequently built computation until [`clear_iterations()`](#perceval.runtime.execution_factory.ExecutionFactory.clear_iterations "perceval.runtime.execution_factory.ExecutionFactory.clear_iterations") is called.

Parameters:  
- **computer** (`AComputer`) – Computer that will perform the executions.

- **experiment** ([`Experiment`](https://perceval.quandela.net/docs/v1.3/reference/components/experiment.html#perceval.components.experiment.Experiment "perceval.components.experiment.Experiment")) – Experiment used by the computations.

- **max_shots_per_call** (`Optional`\[`int`\]) – Default maximum number of shots for each built computation. A positive value is mandatory for remote computers.

add_iteration(*\*\*kwargs*)  
Add an iteration to subsequently built computations.

Iteration parameters are validated when [`build_computation()`](#perceval.runtime.execution_factory.ExecutionFactory.build_computation "perceval.runtime.execution_factory.ExecutionFactory.build_computation") creates the `ComputationIterator`, or an `Execution` is created through a property.

Parameters:  
**kwargs** –

List of accepted keywords:

- `circuit_params`: numerical values keyed by circuit parameter name

- `input_state`: `BasicState`

- `min_detected_photons`: minimum accepted photon count

- `max_samples`: maximum number of samples to collect

- `max_shots`: maximum number of shots to perform

- `postselect`: `PostSelect` condition

add_iteration_list(*iterations*)  
Add several iterations to subsequently built computations.

The dictionaries are appended in order and follow the same format as [`add_iteration()`](#perceval.runtime.execution_factory.ExecutionFactory.add_iteration "perceval.runtime.execution_factory.ExecutionFactory.add_iteration").

Parameters:  
**iterations** (`list`\[`dict`\]) – Ordered iteration parameter dictionaries.

build_computation(*name*)  
Build a computation for a command supported by the computer.

If the factory contains iterations, the result is a `ComputationIterator` wrapping the base computation. Otherwise, a `Computation` is returned. The factory’s `max_shots_per_call` value is added as the base `max_shots` parameter when configured.

Parameters:  
**name** (`str`) – Name of a command registered by the computer.

Return type:  
[`Computation`](https://perceval.quandela.net/docs/v1.3/reference/runtime/computation.html#perceval.runtime.computation.Computation "perceval.runtime.computation.Computation") \| [`ComputationIterator`](https://perceval.quandela.net/docs/v1.3/reference/runtime/computation.html#perceval.runtime.computation_iterator.ComputationIterator "perceval.runtime.computation_iterator.ComputationIterator")

Returns:  
A computation, or a computation iterator when iterations have been added.

Raises:  
**ValueError** – If the computer does not support `name`.

build_execution(*computation*)  
Build a new execution for this factory’s computer.

If `default_job_name` is set, that name is assigned to the new execution.

Parameters:  
**computation** ([`Computation`](https://perceval.quandela.net/docs/v1.3/reference/runtime/computation.html#perceval.runtime.computation.Computation "perceval.runtime.computation.Computation") \| [`ComputationIterator`](https://perceval.quandela.net/docs/v1.3/reference/runtime/computation.html#perceval.runtime.computation_iterator.ComputationIterator "perceval.runtime.computation_iterator.ComputationIterator")) – Computation or iterator to execute.

Return type:  
[`Execution`](https://perceval.quandela.net/docs/v1.3/reference/runtime/execution.html#perceval.runtime.execution.Execution "perceval.runtime.execution.Execution")

Returns:  
A new, unsent execution.

clear_iterations()  
Remove all iterations currently stored by the factory.

*property* n_iterations  
Return the number of iterations currently stored by the factory.

*property* probs  
Build a new execution for the standard `probs` command.

*property* sample_count  
Build a new execution for the standard `sample_count` command.

*property* samples  
Build a new execution for the standard `samples` command.
