> Full piece: [https://perceval.quandela.net/docs/v1.3/reference/runtime/execution_group.html](https://perceval.quandela.net/docs/v1.3/reference/runtime/execution_group.html)
> Retrieved 2026-10-25T09:12Z by scripts/capture_qd_docs.py --perceval (urllib, pandoc); fetched HTML sha256 b84535b7cf4c3e82ed0fb07f2124f476f9b36325b3d3ee7abde895209ca0d73b.

# ExecutionGroup

The `ExecutionGroup` class manages a named collection of [Execution](https://perceval.quandela.net/docs/v1.3/reference/runtime/execution.html#execution) objects. Groups are stored locally, so large experiments can be split into several executions, launched over multiple Python sessions, and retrieved from a single place. Creating an `ExecutionGroup` with an existing name loads the previously stored group.

An execution group can contain both local and remote executions. It can launch unsent executions sequentially or in parallel, rerun unsuccessful executions, monitor their progress, cancel active executions, and retrieve all available results at once.

Warning

Execution groups store their data in a “execution_groups” directory under the current directory by default. These files can grow quite large and are not removed automatically. They can be removed by hand if they are no longer needed.

Note

The storage directory can be changed at instantiation of an `ExecutionGroup`. An existing group can be retrieved if and only if both the directory and the name match the original values.

## Usage example

The following example prepares a group containing two executions of the same acquisition, one using a post-processed CNOT gate and the other a heralded CNOT gate:

``` default
>>> import perceval as pcvl
>>>
>>> computer = pcvl.RemoteComputer(pcvl.QuandelaCommunicationLayer("sim:belenos"))
>>>
>>> ralph_experiment = pcvl.catalog["postprocessed cnot"].build_experiment()
>>> ralph_experiment.min_detected_photons_filter(2)
>>> ralph_experiment.with_input(pcvl.BasicState([0, 1, 0, 1]))
>>> ralph_factory = pcvl.ExecutionFactory(computer, ralph_experiment, max_shots_per_call=1_000_000)
>>>
>>> knill_experiment = pcvl.catalog["heralded cnot"].build_experiment()
>>> knill_experiment.min_detected_photons_filter(2)
>>> knill_experiment.with_input(pcvl.BasicState([0, 1, 0, 1]))
>>> knill_factory = pcvl.ExecutionFactory(computer, knill_experiment, max_shots_per_call=1_000_000)
>>>
>>> group = pcvl.ExecutionGroup("compare_knill_and_ralph_cnot")
>>> group.add(ralph_factory.sample_count, max_samples=10_000)
>>> group.add(knill_factory.sample_count, max_samples=10_000)
```

At this point the executions have only been prepared and saved locally. No computation has been launched. A later script can load the group by name and run its unsent executions sequentially:

``` default
>>> import perceval as pcvl
>>>
>>> group = pcvl.ExecutionGroup("compare_knill_and_ralph_cnot")
>>> # Starts the computer of the first execution - Assume the same computer is used for all executions
>>> with pcvl.acquire(*group.list_unsent_computers()):
...     group.run_sequential(0)  # Launch the second execution after the first one finishes
```

Use `group.run_parallel()` to run as many executions concurrently as their computers allow. The corresponding `group.rerun_failed_sequential(delay)` and `group.rerun_failed_parallel()` methods rerun unsuccessful executions.

Note

The computers are not started and stopped automatically within the run. They should be started and stopped outside the run or rerun methods.

The `encapsulate_manager_list()` utility function and the computer listing methods (`list_unsent_computers()`, `list_active_computers()` and `list_unsuccessful_computers()`) can be used for this purpose.

Note

Like [RemoteComputer](https://perceval.quandela.net/docs/v1.3/reference/runtime/computer.html#remotecomputer), an `ExecutionGroup` is not stored with your credentials. For automatic retrieval of an existing group, they must be inserted back using the correct [RemoteConfig](https://perceval.quandela.net/docs/v1.3/reference/providers/quandela.html#remoteconfig).

Executions can also be launched without waiting for them to finish:

``` default
>>> group.launch_async_executions(concurrent_execution_count=2)
>>> group.track_progress()  # Block and display progress until no execution remains active
```

Note

`launch_async_executions()` launches as many executions as the computers’ available capacity permits, up to `concurrent_execution_count` when it is provided. Local asynchronous executions that are still running when the Python process exits must be started again.

Warning

A computer should not be stopped until all async executions associated to it have finished. Splitting the execution launch and the result retrieval into two scripts requires calling `start()` and `stop()` manually.

Finally, another script can load the group and retrieve its results in insertion order. An entry is `None` when the corresponding execution has not completed or its result is unavailable.

``` default
>>> import perceval as pcvl
>>>
>>> group = pcvl.ExecutionGroup("compare_knill_and_ralph_cnot")
>>> results = group.get_results()
>>> ralph_result = results[0]
>>> knill_result = results[1]
```

## Class reference

*class* perceval.runtime.execution_group.ExecutionGroup(*name*, *folder_path='./execution_groups'*)  
A named, persistent collection of `Execution` objects.

An existing group is loaded when its name is reused. Every mutation is automatically stored with the archive serialization system.

The ExecutionGroup class can perform various tasks such as: - Saving information for a collection of executions, whether they have been sent to the cloud or not. - Running executions within the group either in parallel or sequentially. - Rerunning failed executions within the group. - Retrieving all results at once.

Parameters:  
**name** (`str`) – Name uniquely identifying the group on disk.

add(*execution*, *\*\*kwargs*)  
Add an execution then saves the group.

Parameters:  
- **execution** ([`Execution`](https://perceval.quandela.net/docs/v1.3/reference/runtime/execution.html#perceval.runtime.execution.Execution "perceval.runtime.execution.Execution")) – an execution to add to the list of current execution group

- **kwargs** – parameters to pass to the execution, that will be used when it is launched.

Return type:  
`None`

cancel_all()  
Cancels all started and not completed executions in the group.

Return type:  
`None`

*property* executions*: list\[[perceval.runtime.execution.Execution](https://perceval.quandela.net/docs/v1.3/reference/runtime/execution.html#perceval.runtime.execution.Execution "perceval.runtime.execution.Execution")\]*  
Return the executions in insertion order.

get_results()  
Retrieve results for all completed executions in the group. Non-completed executions will add None to the resulting list.

Return type:  
`list`\[`Optional`\[`dict`\]\]

launch_async_executions(*concurrent_execution_count=None*)  
Launches up to concurrent_execution_count executions and returns without waiting for execution completion.

Beware that local executions that are not finished will have to be started from scratch again if the scripts stops. In that case, use `track_progress()` to block, or launch your executions using `run_sequential()` or `run_parallel()`.

Parameters:  
**concurrent_execution_count** (`Optional`\[`int`\]) – maximum number of concurrent executions. If not specified, the maximum number allowed by the computers is launched.

Return type:  
`None`

list_active_computers()  
Returns the list of computers having at least one active execution

Return type:  
`list`\[`AComputer`\]

list_active_executions()  
Returns a list of all Executions in the group that are currently active - those with a Running or Waiting status.

Return type:  
`list`\[[`Execution`](https://perceval.quandela.net/docs/v1.3/reference/runtime/execution.html#perceval.runtime.execution.Execution "perceval.runtime.execution.Execution")\]

list_successful_executions()  
Returns a list of all Executions in the group that have run successfully.

Return type:  
`list`\[[`Execution`](https://perceval.quandela.net/docs/v1.3/reference/runtime/execution.html#perceval.runtime.execution.Execution "perceval.runtime.execution.Execution")\]

list_unsent_computers()  
Returns the list of computers having at least one unsent execution

Return type:  
`list`\[`AComputer`\]

list_unsent_executions()  
Returns a list of all Executions in the group that have not been launched

Return type:  
`list`\[[`Execution`](https://perceval.quandela.net/docs/v1.3/reference/runtime/execution.html#perceval.runtime.execution.Execution "perceval.runtime.execution.Execution")\]

list_unsuccessful_computers()  
Returns the list of computers having at least one unsuccessful execution

Return type:  
`list`\[`AComputer`\]

list_unsuccessful_executions()  
Returns a list of all Executions in the group that have run unsuccessfully - errored or canceled

Return type:  
`list`\[[`Execution`](https://perceval.quandela.net/docs/v1.3/reference/runtime/execution.html#perceval.runtime.execution.Execution "perceval.runtime.execution.Execution")\]

progress()  
Summarize finished and unfinished executions.

return format: {“Total”: int, “Finished”: \[int, {“successful”: int, “unsuccessful”: int}\], “Unfinished”: \[int, {“sent”: int, “not sent”: int}\]}

Return type:  
`dict`

relaunch_async_failed_executions(*replace_failed_executions=True*, *concurrent_execution_count=None*)  
Relaunches up to concurrent_execution_count failed executions and returns without waiting for execution completion.

Beware that local executions that are not finished will have to be started from scratch again if the scripts stops. In that case, use `track_progress()` to block, or launch your executions using `rerun_failed_sequential()` or `rerun_failed_parallel()`.

Parameters:  
- **concurrent_execution_count** (`Optional`\[`int`\]) – maximum number of concurrent executions. If not specified, the maximum number allowed by the computers is used.

- **replace_failed_executions** (`bool`) – replace the rerun executions in the execution group, else keep the failed ones in addition of the rerun ones

Return type:  
`None`

rerun_failed_parallel(*replace_failed_executions=True*, *\*\*kwargs*)  
Restart all failed executions in the group, running them in parallel. The number of concurrent executions is determined by the capabilities of the computers.

Parameters:  
**replace_failed_executions** (`bool`) – Indicates whether a new execution created from a rerun should replace the previously failed execution (defaults to True).

Return type:  
`None`

rerun_failed_sequential(*delay*, *replace_failed_executions=True*, *\*\*kwargs*)  
Reruns Failed executions in the group in a sequential manner with a user-specified delay between the completion of one execution and the start of the next.

Parameters:  
- **delay** (`float`) – number of seconds to wait between re-launching executions on cloud

- **replace_failed_executions** (`bool`) – Indicates whether a new execution created from a rerun should replace the previously failed execution (defaults to True).

Return type:  
`None`

run_parallel()  
Launches all the unsent executions in the group, running them in parallel. The number of concurrent executions is determined by the capabilities of the computers.

Return type:  
`None`

run_sequential(*delay*)  
Launches the unsent executions in the group in a sequential manner with a user-specified delay between the completion of one execution and the start of the next.

Parameters:  
**delay** (`float`) – number of seconds to wait between launching executions on cloud

Return type:  
`None`

track_progress()  
Display progress bars until no execution is active using ‘tqdm’. The bars represent the number of Successful, Active (i.e. launched and not finished), and Unsuccessful executions

Return type:  
`None`
