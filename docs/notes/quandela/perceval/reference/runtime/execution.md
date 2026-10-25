> Full piece: [https://perceval.quandela.net/docs/v1.3/reference/runtime/execution.html](https://perceval.quandela.net/docs/v1.3/reference/runtime/execution.html)
> Retrieved 2026-10-25T09:12Z by scripts/capture_qd_docs.py --perceval (urllib, pandoc); fetched HTML sha256 7c96efe386644f80e14dee458a82d0e1a8e1ab162ad9910c6224b9783cacbed3.

# Execution

An `Execution` is responsible for running a `Computation` on a [Computer](https://perceval.quandela.net/docs/v1.3/reference/runtime/computer.html#computer) and retrieving its results. Internally, it hides the complexity of the execution, stores intermediate variables, and offers monitoring convenience. It provides the same interface for local and remote computers, and supports both synchronous and asynchronous runs. The computer within the execution determines where and how the computation is performed.

Executions are normally created by an `ExecutionFactory`:

``` default
>>> import perceval as pcvl
>>>
>>> experiment = pcvl.Experiment(pcvl.BS())
>>> experiment.with_input(pcvl.BasicState("|1,1>"))
>>> computer = pcvl.SimulatedComputer("SLOS")
>>> factory = pcvl.ExecutionFactory(computer, experiment)
>>> execution = factory.sample_count
```

They can also be created directly using a [Computation](https://perceval.quandela.net/docs/v1.3/reference/runtime/legacy/remote_processor.html#computation) or a [ComputationIterator](https://perceval.quandela.net/docs/v1.3/reference/runtime/computation.html#computationiterator):

``` default
>>> computation = factory.build_computation("sample_count")
>>> computation.add_params(max_samples = 10000)
>>> execution = pcvl.Execution(computation, computer)
```

## Synchronous execution

Call `execute_sync()` to run an execution synchronously. The call blocks until the results are ready. Calling the execution directly is equivalent:

``` default
>>> with computer.acquire():
...     results = execution.execute_sync(max_samples=10_000)  # Giving parameters here override the ones given in the Computation
...     # Equivalently: results = execution(max_samples=10_000)
```

The returned dictionary contains a `"results"` if it has a [Computation](https://perceval.quandela.net/docs/v1.3/reference/runtime/legacy/remote_processor.html#computation), or `"results_list"` entry if it has a [ComputationIterator](https://perceval.quandela.net/docs/v1.3/reference/runtime/computation.html#computationiterator), and may contain additional data such as performance values.

A progress callback can be installed before a synchronous run. Returning `True` from the callback requests cancellation:

``` default
>>> def progress_callback(progress: float, message: str):
...     print(f"{progress:.0%}: {message}")
...     return False
>>>
>>> execution = factory.sample_count
>>> execution.set_progress_callback(progress_callback)
```

## Asynchronous execution

Call `execute_async()` to launch an execution without waiting for completion. The method returns the same execution object, whose status can then be monitored:

``` default
>>> import time
>>>
>>> execution = factory.sample_count
>>> with execution.computer.acquire():
...     execution.execute_async(max_samples=10_000)
...     while not execution.is_complete:
...         print(execution.status.progress)
...         time.sleep(1)
...     if execution.is_failed:
...         print(execution.status.stop_message)
...     else:
...         results = execution.get_results()
```

Warning

A computer must remain started until all asynchronous executions associated with it have finished. Use `Computer.start` and `Computer.stop` when launching an execution and waiting for its completion in different scopes.

## Cancellation and rerunning

Cancellation can be requested for an execution that has already been launched and has not completed:

``` default
>>> execution.cancel()
```

Cancellation may take some time. Partial results, when available, can be retrieved with:

``` default
>>> partial_results = execution.get_results(allow_partial_results=True)
```

An execution cannot be launched more than once. Use `clone()` to create an equivalent unsent execution, or `rerun()` to create and asynchronously launch a replacement for a failed execution:

``` default
>>> another_execution = execution.clone()
```

## Storage

Launched remote `Executions` can’t be directly created using their cloud id, as they could be linked to several cloud jobs due to [Error mitigation](https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/index.html#error-mitigation). To be able to access the results of an `Execution` in another script, it must be serialized after launch and stored somewhere, then deserialized in the other script.

Use an [ExecutionGroup](https://perceval.quandela.net/docs/v1.3/reference/runtime/execution_group.html#executiongroup) to do that automatically for you, or use the [serialization](https://perceval.quandela.net/docs/v1.3/reference/serialization/index.html#serialization) system.

## Execution status

The `status` property returns an [ExecutionStatus](https://perceval.quandela.net/docs/v1.3/reference/runtime/execution_status.html#executionstatus). Convenience properties are available for common state checks:

``` default
>>> status = execution.status
>>> execution.was_sent
>>> execution.is_waiting
>>> execution.is_running
>>> execution.is_complete
>>> execution.is_success
>>> execution.is_failed
```

## Class reference

*class* perceval.runtime.execution.Execution(*computation*, *computer*)  
A class aimed at controlling the execution flow of a computation on a given computer. It provides means to compute synchronously or asynchronously, hiding the complexity of handling intermediate objects.

Depending on the mitigations that are set into the computer, one or several jobs (i.e. a unit computation on the cloud, or a single simulation call) may be created. This complexity is hidden by this object, but may appear on a provider’s cloud interface.

``` default
>>> execution = Execution(computation, computer)
>>> res = execution(max_shots = 10000)  # Synchronous call - Computation parameters can be given here
```

Parameters:  
- **computation** ([`Computation`](https://perceval.quandela.net/docs/v1.3/reference/runtime/computation.html#perceval.runtime.computation.Computation "perceval.runtime.computation.Computation") \| [`ComputationIterator`](https://perceval.quandela.net/docs/v1.3/reference/runtime/computation.html#perceval.runtime.computation_iterator.ComputationIterator "perceval.runtime.computation_iterator.ComputationIterator")) – The computation to be executed

- **computer** (`AComputer`) – The computer that will execute the computation

cancel()  
Request the cancellation of the execution.

clone()  
Return type:  
[`Execution`](#perceval.runtime.execution.Execution "perceval.runtime.execution.Execution")

Returns:  
A new execution, identical to this one, except that it is not associated to any run or results, and can thus be used with other parameters, or to rerun an execution.

execute_async(*\*args*, *\*\*kwargs*)  
Execute the task asynchronously. This call is non-blocking allowing for concurrency. Results cannot be expected to be ready as soon as this call ends. The results have to be retrieved only when the execution status says it’s completed.

Parameters:  
- **args** – arguments to pass to the task function

- **kwargs** – keyword arguments to pass to the task function

Return type:  
[`Execution`](#perceval.runtime.execution.Execution "perceval.runtime.execution.Execution")

Returns:  
self

execute_sync(*\*args*, *allow_partial_results=False*, *\*\*kwargs*)  
Execute the task synchronously.

Parameters:  
- **args** – arguments to pass to the task function

- **allow_partial_results** (`bool`) – If True, results will be returned even if there is an error somewhere. Else, the error will be raised

- **kwargs** – keyword arguments to pass to the task function

Return type:  
`dict`

Returns:  
results dictionary. You can expect a “results” or a “results_list” field, performance scores and other data corresponding to the computation and computer nature.

Raises:  
RuntimeError if the execution hasn’t been launched, or if there is an error and allow_partial_results is False.

get_details()  
Return type:  
`str`

Returns:  
A str representing the details of the execution.

get_results(*allow_partial_results=False*)  
Retrieve the results of the execution.

Parameters:  
**allow_partial_results** (`bool`) – If True, results will be returned even if there is an error somewhere. Else, the error will be raised

Return type:  
`dict`

Returns:  
results dictionary. You can expect a “results” or a “results_list” field, performance scores and other data corresponding to the computation and computer nature.

Raises:  
RuntimeError if the execution hasn’t been launched, or if there is an error and allow_partial_results is False.

*property* job_group_name*: str \| None*  
The execution group name, that will be used to give a job group name to the generated jobs

*property* name*: str*  
The execution name, that will be used to name generated jobs

rerun()  
Return type:  
[`Execution`](#perceval.runtime.execution.Execution "perceval.runtime.execution.Execution")

Returns:  
A new execution, identical to this one, and run it asynchronously

reset_results_cache()  
Reset the results cache. May be useful in case of a communication error during `get_results()` with `allow_partial_results=True`

Return type:  
`None`

set_progress_callback(*callback*)  
Set a progress callback function with the following signature:

def progress_callback(progress: float, message: str) -\> dict \| bool \| None

If the progress callback returns True, a cancellation is requested. This custom callback is only used for synchronous execution. For asynchronous execution, call self.cancel() to cancel, or self.status, self.is_complete… to monitor the progress.

Note

This callback is never serialized.

Parameters:  
**callback** (`Callable`\[\[`float`, `str`\], `UnionType`\[`None`, `dict`, `bool`\]\]) – callback function

*property* status*: [ExecutionStatus](https://perceval.quandela.net/docs/v1.3/reference/runtime/execution_status.html#perceval.runtime.execution_status.ExecutionStatus "perceval.runtime.execution_status.ExecutionStatus")*  
The execution status metadata structure
