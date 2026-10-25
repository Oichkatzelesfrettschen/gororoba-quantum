> Full piece: [https://perceval.quandela.net/docs/v1.3/reference/runtime/computer.html](https://perceval.quandela.net/docs/v1.3/reference/runtime/computer.html)
> Retrieved 2026-10-17T17:29Z by scripts/capture_qd_docs.py --perceval (urllib, pandoc); fetched HTML sha256 47cf561b54733d69ad27553354018e9b0496f7f9fe26ff99753e0986ccdd9017.

# Computer

A `Computer` is a class dedicated at executing [Computation](https://perceval.quandela.net/docs/v1.3/reference/runtime/legacy/remote_processor.html#computation) or [ComputationIterator](https://perceval.quandela.net/docs/v1.3/reference/runtime/computation.html#computationiterator). It represents a physical or simulated way of performing some data acquisition.

`Computers` can be local, in which case they do everything on the user machine, or remote, in which case they send HTTP requests to some distant platform that will perform the acquisition. A `Computer` can be a simulator or real QPU. In any case, its intent is to represent a QPU.

As such, it has some noise, or can be given some if it’s a simulator.

``` default
>>> remote_computer = RemoteComputer(QuandelaCommunicationLayer("qpu:belenos"))
>>> print(computer.noise)  # Will print the current qpu noise
>>> local_computer = SimulatedComputer("SLOS")
>>> local_computer.noise = NoiseModel(brightness = 0.8)  # Set the noise for this simulation computer
```

Any `Computer` can apply some [Error mitigation](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/index.html#error-mitigation) techniques automatically when given a [Computation](https://perceval.quandela.net/docs/v1.3/reference/runtime/legacy/remote_processor.html#computation).

``` default
>>> local_computer.mitigations = MitigationFactory(MitigationLevel.medium).build()
```

Also, some `Computers` may have particular possible parameters that will act on the computation process.

``` default
>>> print(remote_computer.available_parameters)
>>> remote_computer.reset_parameters()  # Reset to default parameters
>>> remote_computer.parameters |= {"compute_physical_logical_perf": True}
```

`Computers` are made to be interchangeable as much as possible. As such, their public interface is essentially the same. In particular, they can all do computations synchronously and asynchronously. The details on how they do it depends on their particular implementation.

Since they share the same interface, it is a good idea to always use the common public methods. For instance, you should always start and stop them before and after doing all your computations, even for computers where this does nothing. This automatic start and stop process can be done using the `acquire()` context manager.

``` default
>>> with acquire(remote_computer):
...     # All computations here
```

Note

A computer should not be stopped until all computations are executed. Hence, the acquisition should be done at the topmost level. For instance, methods that take a computer as argument should not acquire it.

abstract_computer.acquire()  
Acquires any number of computers.

Note

Duplicated computers are acquired only once. The acquisition may happen in any order.

Parameters:  
**computers** (`AComputer`) – The computers to acquire

Return type:  
`ContextManager`

Returns:  
A context manager that starts the computers at enter and stops them at exit.

# SimulatedComputer

Unless you have a real QPU on your machine, the only local computer you’re going to use is the `SimulatedComputer`. This computer can be used to simulate experiments, by giving it a backend or a backend name. It will automatically choose which method to use to do the simulation based on the backend and the request (sampling, feed-forward…).

Its main way to compute is synchronous, but it can create threads to allow for asynchronous calls.

*class* perceval.runtime.simulated_computer.SimulatedComputer(*backend*)  
A computer able to perform local simulations

Parameters:  
**backend** – The backend to use to perform the simulations. Can be a backend name or a backend instance

acquire()  
Return type:  
`ContextManager`

Returns:  
A context manager that starts the computer at enter and stops it at exit

apply_configuration(*mitigations=None*, *noise=None*, *parameters=None*)  
Warning

Using this method is generally not safe in an asynchronous context. In that case, make a persistent copy of the computer inside the with block, then use the copy. Async usage with `Execution` should be safe with the Computers directly provided by Perceval.

Parameters:  
- **mitigations** (`Optional`\[`list`\[`AMitigation`\]\]) – The mitigations to apply within the ContextManager. If None, nothing is changed

- **noise** (`Optional`\[[`NoiseModel`](https://perceval.quandela.net/docs/v1.3/reference/utils/noise_model.html#perceval.utils.noise_model.NoiseModel "perceval.utils.noise_model.NoiseModel")\]) – The noise model to apply within the ContextManager. If None, nothing is changed

- **parameters** (`Optional`\[`dict`\[`str`, `Any`\]\]) – The parameters to apply within the ContextManager. If None, nothing is changed

Return type:  
`ContextManager`

Returns:  
A ContextManager that applies the given arguments to the computer (noise, mitigations, parameters) at enter and reset the parameters to the previous values at exit

*property* available_commands*: list\[str\]*  
Returns a list of all available command names available in the computer.

*property* available_jobs*: int*  
Returns the number of jobs that can currently be added to the asynchronous queue

*property* available_parameters*: dict\[str, str\]*  
Returns:  
A dictionary describing all the available parameters keys and their meaning.

compute_physical_logical_perf(*value*)  
Tells the simulator to compute or not the physical and logical performances when possible

Parameters:  
**value** (`bool`) – True to compute the physical and logical performances, False otherwise.

delete()  
Deletes the computer session. May do nothing for stateless computers

Return type:  
`None`

*property* details*: dict\[str, Any\]*  
Return details about the computer. Any kind of details can be given here, but there is no guarantee that a particular detail will appear, so computer-agnostic code should never assume that a field is present here.

execute(*computation*, *out=None*, *progress_callback=None*)  
Synchronous execution of computation

Parameters:  
- **computation** ([`Computation`](https://perceval.quandela.net/docs/v1.3/reference/runtime/computation.html#perceval.runtime.computation.Computation "perceval.runtime.computation.Computation") \| [`ComputationIterator`](https://perceval.quandela.net/docs/v1.3/reference/runtime/computation.html#perceval.runtime.computation_iterator.ComputationIterator "perceval.runtime.computation_iterator.ComputationIterator")) – A Computation or an iterator to execute.

- **out** (`Optional`\[`dict`\]) – A potentially externally given dict where to place the results. If the computation is an iterator, it can receive be used to retrieve partial results.

- **progress_callback** (`Optional`\[`Callable`\[\[`float`, `str`\], `UnionType`\[`None`, `dict`, `bool`\]\]\]) – A ProgressCallback to monitor the progress and potentially cancel the execution.

Return type:  
`dict`

Returns:  
the filled out dict if it was given, or a new dict containing the results.

execute_async(*computation*)  
Asynchronous execution of computation.

Parameters:  
**computation** ([`Computation`](https://perceval.quandela.net/docs/v1.3/reference/runtime/computation.html#perceval.runtime.computation.Computation "perceval.runtime.computation.Computation") \| [`ComputationIterator`](https://perceval.quandela.net/docs/v1.3/reference/runtime/computation.html#perceval.runtime.computation_iterator.ComputationIterator "perceval.runtime.computation_iterator.ComputationIterator")) – The computation to execute

Return type:  
`tuple`\[`list`\[`AMitigation`\], `Imperfections`, `list`\[`list`\[`AsyncGetter`\]\]\]

Returns:  
The imperfections of the computer when the execution was launched, and the list of objects that can be used to get the results. Beware that the given imperfections that can be used to get the results are those from when the job was launched, not the ones from when it is executed.

get_results(*computation*, *imperfections*, *async_getters*, *out=None*)  
Get the results for an asynchronous computation.

Parameters:  
- **computation** ([`Computation`](https://perceval.quandela.net/docs/v1.3/reference/runtime/computation.html#perceval.runtime.computation.Computation "perceval.runtime.computation.Computation") \| [`ComputationIterator`](https://perceval.quandela.net/docs/v1.3/reference/runtime/computation.html#perceval.runtime.computation_iterator.ComputationIterator "perceval.runtime.computation_iterator.ComputationIterator")) – The original computation that was executed

- **imperfections** (`Imperfections`) – The imperfections with which the computations were executed

- **async_getters** (`list`\[`list`\[`AsyncGetter`\]\]) – The list of async_getters that point to the executions of the computation (as returned by execute_async)

- **out** (`Optional`\[`dict`\]) – An in-out dictionary where to place the results.

Return type:  
`dict`\[`str`, `Any`\]

*property* is_remote*: bool*  
Returns true if the computer is remote

log_resources(*method*, *experiment*, *extra_parameters*)  
Log resources of the AComputer

Parameters:  
- **method** (`str`) – name of the method used

- **extra_parameters** (`dict`) –

  extra parameters to log.

  Extra parameter can be:

  > - max_samples
  >
  > - max_shots
  >
  > - precision

*property* mitigations*: list\[perceval.runtime.error_mitigation.abstract_mitigation.AMitigation\] \| None*  
The list of error mitigations that the computer will apply, or None if unspecified (use default mitigations).

*property* noise*: [NoiseModel](https://perceval.quandela.net/docs/v1.3/reference/utils/noise_model.html#perceval.utils.noise_model.NoiseModel "perceval.utils.noise_model.NoiseModel")*  
The noise model representing the computer. Will be used only for simulators

*property* parameters*: dict\[str, Any\]*  
The computer-specific parameters. The possible items are detailed in ‘self.available_parameters’.

*property* performance  
A more detailed characterization of the noise than the noise model, possibly evaluating things that a noise model doesn’t know

probs(*experiment*, *progress_callback=None*, *precision=None*, *max_samples=None*, *max_shots=None*, *compilation_seed=None*, *\*\*kwargs*)  
Computes the probabilities for a given experiment. Does not apply error mitigations

Parameters:  
- **experiment** ([`Experiment`](https://perceval.quandela.net/docs/v1.3/reference/components/experiment.html#perceval.components.experiment.Experiment "perceval.components.experiment.Experiment")) – The Experiment to simulate.

- **progress_callback** (`Optional`\[`Callable`\[\[`float`, `str`\], `UnionType`\[`None`, `dict`, `bool`\]\]\]) – An optional progress callback that will be used to report the progress of the simulation, and possibly cancel the computation.

- **precision** (`Optional`\[`float`\]) – The precision of the computation. Probabilities lower than the biggest input probability times this are ignored. Used only with Probability backends

- **max_shots** (`Optional`\[`int`\]) – The maximum number of shots to consider. A shot is any event with at least 1 photon Used only is the computer has a Sampling backend or if the precision is not given

- **max_samples** (`Optional`\[`int`\]) – The maximum number of samples to consider. A sample is any event with at least min_photons photon (defined in the Experiment). Used only is the computer has a Sampling backend or if the precision and the max_shots are not given

- **compilation_seed** (`Optional`\[`int`\]) – A seed to use for the compilation starting point or the random phases

Return type:  
`dict`

Returns:  
A dict with the following fields:

- ”result”: BSDistribution,

- ”global_perf”: float,

- If compute_physical_logical_perf is True:  
  - ”physical_perf”: float,

  - ”logical_perf”: float,

reset_parameters()  
Reset the parameters to their default values.

sample_count(*experiment*, *max_samples*, *max_shots=None*, *progress_callback=None*, *compilation_seed=None*, *\*\*kwargs*)  
Computes the probabilities for a given experiment. Does not apply error mitigations

Parameters:  
- **experiment** ([`Experiment`](https://perceval.quandela.net/docs/v1.3/reference/components/experiment.html#perceval.components.experiment.Experiment "perceval.components.experiment.Experiment")) – The Experiment to simulate.

- **progress_callback** (`Optional`\[`Callable`\[\[`float`, `str`\], `UnionType`\[`None`, `dict`, `bool`\]\]\]) – An optional progress callback that will be used to report the progress of the simulation, and possibly cancel the computation.

- **max_shots** (`Optional`\[`int`\]) – The maximum number of shots to consider. A shot is any event with at least 1 photon Used only is the computer has a Sampling backend or if the precision is not given

- **max_samples** (`int`) – The maximum number of samples to consider. A sample is any event with at least min_photons photon (defined in the Experiment). Used only is the computer has a Sampling backend or if the precision and the max_shots are not given

- **compilation_seed** (`Optional`\[`int`\]) – A seed to use for the compilation starting point or the random phases

Return type:  
`dict`

Returns:  
A dict with the following fields:

- ”result”: BSCount,

- ”global_perf”: float,

- If compute_physical_logical_perf is True:  
  - ”physical_perf”: float,

  - ”logical_perf”: float,

samples(*experiment*, *max_samples*, *max_shots=None*, *progress_callback=None*, *compilation_seed=None*, *\*\*kwargs*)  
Computes the probabilities for a given experiment. Does not apply error mitigations

Parameters:  
- **experiment** ([`Experiment`](https://perceval.quandela.net/docs/v1.3/reference/components/experiment.html#perceval.components.experiment.Experiment "perceval.components.experiment.Experiment")) – The Experiment to simulate.

- **progress_callback** (`Optional`\[`Callable`\[\[`float`, `str`\], `UnionType`\[`None`, `dict`, `bool`\]\]\]) – An optional progress callback that will be used to report the progress of the simulation, and possibly cancel the computation.

- **max_shots** (`Optional`\[`int`\]) – The maximum number of shots to consider. A shot is any event with at least 1 photon Used only is the computer has a Sampling backend or if the precision is not given

- **max_samples** (`int`) – The maximum number of samples to consider. A sample is any event with at least min_photons photon (defined in the Experiment). Used only is the computer has a Sampling backend or if the precision and the max_shots are not given

- **compilation_seed** (`Optional`\[`int`\]) – A seed to use for the compilation starting point or the random phases

Return type:  
`dict`

Returns:  
A dict with the following fields:

- ”result”: BSSamples,

- ”global_perf”: float,

- If compute_physical_logical_perf is True:  
  - ”physical_perf”: float,

  - ”logical_perf”: float,

*property* specs*: [PlatformSpecs](https://perceval.quandela.net/docs/v1.3/reference/runtime/platform_specs.html#perceval.runtime.platform_specs.PlatformSpecs "perceval.runtime.platform_specs.PlatformSpecs")*  
Returns:  
the specs of the computer.

start()  
Starts the computer. May do nothing for stateless computers

Return type:  
`None`

*property* status*: str*  
Returns the status of the computer as a string

stop()  
Stops the computer. May do nothing for stateless computers

Return type:  
`None`

*property* type  
The type of the computer (qpu or simulator)

validate_single(*computation*)  
Parameters:  
**computation** ([`Computation`](https://perceval.quandela.net/docs/v1.3/reference/runtime/computation.html#perceval.runtime.computation.Computation "perceval.runtime.computation.Computation")) – The computation to validate. This is a computation that is the result of mitigation decomposition.

Return type:  
`None`

# RemoteComputer

The `RemoteComputer` lets you have access to a distant QPU or simulator. It requires a `CommunicationLayer`, that can be one given by any of the [providers](https://perceval.quandela.net/docs/v1.3/reference/providers/index.html#providers) (Quandela, Scaleway, Kipu…).

Its main way of compute is asynchronous, but it can wait internally for job completion to allow for synchronous calls.

A `RemoteComputer` can have default mitigations if its `mitigation` member is `None`. The mitigations can be completely disabled by explicitly setting them to an empty list.

``` default
>>> remote_computer.mitigations = []  # Disable default mitigations
```

Also, the mitigations are usually sent through the `CommunicationLayer` and applied directly on the distant platform. This can be changed so that the mitigations happen on your machine. Note however that default mitigations are still applied remotely if the `mitigations` member is None.

``` default
>>> remote_computer.use_mitigations_remotely = False
```

Warning

When applying the mitigations locally, the mitigated imperfections are taken from when the execution was sent, not when it was executed on the platform, so this parameter should not be modified unless necessary.

*class* perceval.runtime.remote_computer.RemoteComputer(*communication_layer*)  
A computer that sends Computations to a remote platform.

Parameters:  
**communication_layer** ([`CommunicationLayer`](https://perceval.quandela.net/docs/v1.3/reference/runtime/communication_layer.html#perceval.runtime.communication_layer.CommunicationLayer "perceval.runtime.communication_layer.CommunicationLayer")) – A CommunicationLayer used to communicate with the remote computer.

acquire()  
Return type:  
`ContextManager`

Returns:  
A context manager that starts the computer at enter and stops it at exit

apply_configuration(*mitigations=None*, *noise=None*, *parameters=None*)  
Warning

Using this method is generally not safe in an asynchronous context. In that case, make a persistent copy of the computer inside the with block, then use the copy. Async usage with `Execution` should be safe with the Computers directly provided by Perceval.

Parameters:  
- **mitigations** (`Optional`\[`list`\[`AMitigation`\]\]) – The mitigations to apply within the ContextManager. If None, nothing is changed

- **noise** (`Optional`\[[`NoiseModel`](https://perceval.quandela.net/docs/v1.3/reference/utils/noise_model.html#perceval.utils.noise_model.NoiseModel "perceval.utils.noise_model.NoiseModel")\]) – The noise model to apply within the ContextManager. If None, nothing is changed

- **parameters** (`Optional`\[`dict`\[`str`, `Any`\]\]) – The parameters to apply within the ContextManager. If None, nothing is changed

Return type:  
`ContextManager`

Returns:  
A ContextManager that applies the given arguments to the computer (noise, mitigations, parameters) at enter and reset the parameters to the previous values at exit

*property* available_commands*: list\[str\]*  
Returns a list of all available command names available in the computer.

*property* available_jobs*: int*  
Returns the number of jobs that can currently be added to the asynchronous queue

*property* available_parameters*: dict\[str, str\]*  
Returns:  
A dictionary describing all the available parameters keys and their meaning.

delete()  
May be used to delete a non-interrupted session. May do nothing for stateless providers

Return type:  
`None`

*property* details*: dict\[str, Any\]*  
Return details about the computer. Any kind of details can be given here, but there is no guarantee that a particular detail will appear, so computer-agnostic code should never assume that a field is present here.

estimate_expected_samples(*computation*, *nshots*, *param_values=None*)  
Compute an estimate number of samples the user can expect given the platform and the user request. The circuit, input state, minimum photon filter, and error mitigations are taken into account.

Parameters:  
- **computation** ([`Computation`](https://perceval.quandela.net/docs/v1.3/reference/runtime/computation.html#perceval.runtime.computation.Computation "perceval.runtime.computation.Computation") \| [`ComputationIterator`](https://perceval.quandela.net/docs/v1.3/reference/runtime/computation.html#perceval.runtime.computation_iterator.ComputationIterator "perceval.runtime.computation_iterator.ComputationIterator")) – The computation that will be sent with unknown number of shots. It needs to be valid.

- **nshots** (`int`) – Number of shots the user is willing to consume

- **param_values** (`Optional`\[`dict`\]) – Key/value pairs for variable parameters inside the circuit. All parameters need to be fixed for this computation to run.

Return type:  
`int`

Returns:  
Estimate of the number of samples of interest the user can expect back

estimate_required_shots(*computation*, *nsamples*, *param_values=None*)  
Compute an estimate number of required shots given the platform and the user request. The circuit, input state, minimum photon filter, and error mitigations are taken into account.

Parameters:  
- **computation** ([`Computation`](https://perceval.quandela.net/docs/v1.3/reference/runtime/computation.html#perceval.runtime.computation.Computation "perceval.runtime.computation.Computation") \| [`ComputationIterator`](https://perceval.quandela.net/docs/v1.3/reference/runtime/computation.html#perceval.runtime.computation_iterator.ComputationIterator "perceval.runtime.computation_iterator.ComputationIterator")) – The computation that will be sent with unknown number of samples. It needs to be valid.

- **nsamples** (`int`) – Number of expected samples of interest

- **param_values** (`Optional`\[`dict`\]) – Key/value pairs for variable parameters inside the circuit. All parameters need to be fixed for this computation to run.

Return type:  
`Optional`\[`int`\]

Returns:  
Estimate of the number of shots the user needs to acquire enough samples of interest, or None if no sample of interest can be acquired

execute(*computation*, *out=None*, *progress_callback=None*)  
Synchronous execution of computation

Parameters:  
- **computation** ([`Computation`](https://perceval.quandela.net/docs/v1.3/reference/runtime/computation.html#perceval.runtime.computation.Computation "perceval.runtime.computation.Computation") \| [`ComputationIterator`](https://perceval.quandela.net/docs/v1.3/reference/runtime/computation.html#perceval.runtime.computation_iterator.ComputationIterator "perceval.runtime.computation_iterator.ComputationIterator")) – A Computation or an iterator to execute.

- **out** (`Optional`\[`dict`\]) – A potentially externally given dict where to place the results. If the computation is an iterator, it can receive be used to retrieve partial results.

- **progress_callback** (`Optional`\[`Callable`\[\[`float`, `str`\], `UnionType`\[`None`, `dict`, `bool`\]\]\]) – A ProgressCallback to monitor the progress and potentially cancel the execution.

Return type:  
`dict`

Returns:  
the filled out dict if it was given, or a new dict containing the results.

execute_async(*computation*)  
Asynchronous execution of computation.

Parameters:  
**computation** ([`Computation`](https://perceval.quandela.net/docs/v1.3/reference/runtime/computation.html#perceval.runtime.computation.Computation "perceval.runtime.computation.Computation") \| [`ComputationIterator`](https://perceval.quandela.net/docs/v1.3/reference/runtime/computation.html#perceval.runtime.computation_iterator.ComputationIterator "perceval.runtime.computation_iterator.ComputationIterator")) – The computation to execute

Return type:  
`tuple`\[`list`\[`AMitigation`\], `Imperfections`, `list`\[`list`\[`AsyncGetter`\]\]\]

Returns:  
The imperfections of the computer when the execution was launched, and the list of objects that can be used to get the results. Beware that the given imperfections that can be used to get the results are those from when the job was launched, not the ones from when it is executed.

get_results(*computation*, *imperfections*, *async_getters*, *out=None*)  
Get the results for an asynchronous computation.

Parameters:  
- **computation** ([`Computation`](https://perceval.quandela.net/docs/v1.3/reference/runtime/computation.html#perceval.runtime.computation.Computation "perceval.runtime.computation.Computation") \| [`ComputationIterator`](https://perceval.quandela.net/docs/v1.3/reference/runtime/computation.html#perceval.runtime.computation_iterator.ComputationIterator "perceval.runtime.computation_iterator.ComputationIterator")) – The original computation that was executed

- **imperfections** (`Imperfections`) – The imperfections with which the computations were executed

- **async_getters** (`list`\[`list`\[`AsyncGetter`\]\]) – The list of async_getters that point to the executions of the computation (as returned by execute_async)

- **out** (`Optional`\[`dict`\]) – An in-out dictionary where to place the results.

Return type:  
`dict`\[`str`, `Any`\]

*property* is_remote*: bool*  
Returns true if the computer is remote

*property* mitigations*: list\[perceval.runtime.error_mitigation.abstract_mitigation.AMitigation\] \| None*  
The list of error mitigations that the computer will apply, or None if unspecified (use default mitigations).

*property* noise  
The noise model representing the computer. Will be used only for simulators

*property* parameters*: dict\[str, Any\]*  
The computer-specific parameters. The possible items are detailed in ‘self.available_parameters’.

*property* performance  
A more detailed characterization of the noise than the noise model, possibly evaluating things that a noise model doesn’t know

reset_parameters()  
Reset the parameters to their default values.

*property* specs*: [PlatformSpecs](https://perceval.quandela.net/docs/v1.3/reference/runtime/platform_specs.html#perceval.runtime.platform_specs.PlatformSpecs "perceval.runtime.platform_specs.PlatformSpecs")*  
Returns:  
the specs of the computer.

start()  
May be used to start a non-interrupted session. May do nothing for stateless providers

Return type:  
`None`

*property* status*: str*  
Returns the status of the computer as a string

stop()  
May be used to stop a non-interrupted session. May do nothing for stateless providers

Return type:  
`None`

*property* type  
The type of the computer (qpu or simulator)

validate_single(*computation*)  
Parameters:  
**computation** ([`Computation`](https://perceval.quandela.net/docs/v1.3/reference/runtime/computation.html#perceval.runtime.computation.Computation "perceval.runtime.computation.Computation")) – The computation to validate. This is a computation that is the result of mitigation decomposition.

Return type:  
`None`
