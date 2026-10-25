> Full piece: [https://perceval.quandela.net/docs/v1.3/reference/runtime/legacy/job.html](https://perceval.quandela.net/docs/v1.3/reference/runtime/legacy/job.html)
> Retrieved 2026-10-25T09:12Z by scripts/capture_qd_docs.py --perceval (urllib, pandoc); fetched HTML sha256 3f09aaeaa2eea8e6d0c3502a4aa6b7c99267ccab8048b494337c9f71a75f4921.

# Job

Job is class responsible for the computation and retrieval of a task’s results. It hides the local vs remote, and synchronous vs asynchronous executions, which are orthogonal concepts, even if it’s more natural for a local job to be run synchronously, and a remote job asynchronously.

The local vs remote question is handled by two different classes, `LocalJob` and `RemoteJob`, sharing the same interface.

- Execute a job synchronously

``` default
>>> args = [10_000]  # for instance, the expected sample count
>>> results = job.execute_sync(*args)  # Executes the job synchronously (blocks the execution until results are ready)
>>> results = job(*args)  # Same as above
```

- Execute a job asynchronously

``` default
>>> job.execute_async(*args)
```

This call is non-blocking, however results are not available when this line has finished executing. The job object provides information on the progress.

``` default
>>> while not job.is_complete:  # Check if the job has finished running
...     print(job.status.progress)  # Progress is a float value between 0. and 1. representing a progress from 0 to 100%
...     time.sleep(1)
>>> if job.is_failed:  # Check if the job has failed
...     print(job.status.stop_message)  # If so, print the reason
>>> results = job.get_results()  # Retrieve the results if any
```

Typically, the results returned by an algorithm is a Python dictionary containing a `'results'` key, plus additional data (performance scores, etc.).

- A job cancellation can be requested programmatically by the user

``` default
>>> job.cancel()  # Ask for job cancelation. The actual end of the execution may take some time
```

When a job is canceled, it may contain partial results. To retrieve them, call `get_results()`.

- A remote job can be resumed as following:

``` default
>>> remote_processor = pcvl.RemoteProcessor("any:platform")
>>> job = remote_processor.resume_job("job_id")  # You can find job IDs on Quandela Cloud's website
>>> print(job.id)  # The ID field is also available in every remote job object
```

- At any time, the user can retrieve a [ExecutionStatus](https://perceval.quandela.net/docs/v1.3/reference/runtime/execution_status.html#executionstatus) to retrieve several job metadata:

``` default
>>> job_status = job.status
```

## LocalJob

*class* perceval.runtime.legacy.local_job.LocalJob(*fn*, *result_mapping_function=None*, *delta_parameters=None*, *command_param_names=None*)  
Handle a computation task locally (i.e. on the computer running Perceval)

Parameters:  
- **fn** (`callable`) – Function to be called by the job when run, aka “the task”

- **result_mapping_function** (`Optional`\[`callable`\]) – Optional results post-processing function (e.g. can be used to convert results)

- **delta_parameters** (`Optional`\[`dict`\]) – mapping of {‘param_name’: param_value} redirected to either the function or the mapping function

- **command_param_names** (`Optional`\[`list`\]) – names of fn parameters which can be mapped from the \*args of \_\_call\_\_

cancel()  
Request the cancellation of the job.

execute_async(*\*args*, *\*\*kwargs*)  
Execute the task asynchronously. This call is non-blocking allowing for concurrency. Results cannot be expected to be ready as soon as this call ends. The results have to be retrieved only when the job status says it’s completed.

Parameters:  
- **args** – arguments to pass to the task function

- **kwargs** – keyword arguments to pass to the task function

Return type:  
[`LocalJob`](#perceval.runtime.legacy.local_job.LocalJob "perceval.runtime.legacy.local_job.LocalJob")

Returns:  
self

execute_sync(*\*args*, *\*\*kwargs*)  
Execute the task synchronously. This call is blocking and immediately returns a results dictionary.

Note

This method has exactly the same effect as \_\_call\_\_.

Parameters:  
- **args** – arguments to pass to the task function

- **kwargs** – keyword arguments to pass to the task function

Return type:  
`dict`

Returns:  
the results

get_results()  
Retrieve the results of the job.

Return type:  
`dict`

Returns:  
results dictionary. You can expect a “results” or a “results_list” field, performance scores and other data corresponding to the job nature.

Raises:  
RuntimeError if the job hasn’t finished running, or if the results data are empty or malformed.

*property* name*: str*  
The job name

set_progress_callback(*callback*)  
Set a progress callback function with the following signature:

def progress_callback(progress: float, message: str) -\> dict \| None

Parameters:  
**callback** (`Callable`\[\[`float`, `str`\], `UnionType`\[`None`, `dict`, `bool`\]\]) – callback function

*property* status*: [ExecutionStatus](https://perceval.quandela.net/docs/v1.3/reference/runtime/execution_status.html#perceval.runtime.execution_status.ExecutionStatus "perceval.runtime.execution_status.ExecutionStatus")*  
The job status metadata structure

## RemoteJob

*class* perceval.runtime.legacy.remote_job.RemoteJob(*request_data*, *rpc_handler*, *job_name*, *delta_parameters=None*, *job_context=None*, *command_param_names=None*, *refresh_progress_delay=3*)  
Handle a computation task remotely (i.e. through a Cloud provider) by sending a request body of the form:

``` default
{
    'platform_name': '...',
    'pcvl_version': 'M.m.p',
    'payload': {
        'command': '...',
        'experiment': <serialized Experiment>,
        ...
        other parameters
    }
}
```

Parameters:  
- **request_data** (`dict`) – prepared data for the job. It is extended by an execute_async() call before being sent. It is expected to be prepared by a RemoteProcessor.

- **rpc_handler** – a valid RPC handler to connect to a Cloud provider

- **job_name** (`str`) – the job name (visible cloud-side)

- **delta_parameters** (`Optional`\[`dict`\]) – parameters to add/remove dynamically

- **job_context** (`Optional`\[`dict`\]) – Data on the job execution context (conversion required on results, etc.)

- **command_param_names** (`Optional`\[`list`\]) – List of parameter names for the command call (in order to resolve \*args in execute_async() call). This parameter is optional (default = empty list). However, without it, only \*\*kwargs are available in the execute_async() call

- **refresh_progress_delay** (`int`) – wait time when running in sync mode between each refresh (in seconds)

cancel()  
Request the cancellation of the job.

execute_async(*\*args*, *\*\*kwargs*)  
Execute the task asynchronously. This call is non-blocking allowing for concurrency. Results cannot be expected to be ready as soon as this call ends. The results have to be retrieved only when the job status says it’s completed.

Parameters:  
- **args** – arguments to pass to the task function

- **kwargs** – keyword arguments to pass to the task function

Return type:  
[`RemoteJob`](#perceval.runtime.legacy.remote_job.RemoteJob "perceval.runtime.legacy.remote_job.RemoteJob")

Returns:  
self

execute_sync(*\*args*, *\*\*kwargs*)  
Execute the task synchronously. This call is blocking and immediately returns a results dictionary.

Note

This method has exactly the same effect as \_\_call\_\_.

Warning

A remote job natural way of running is asynchronous. This call will actually run the task asynchronously with a waiting loop to reproduce the behaviour of the synchronous call.

Parameters:  
- **args** – arguments to pass to the task function

- **kwargs** – keyword arguments to pass to the task function

Return type:  
`dict`

Returns:  
the results

*static* from_id(*job_id*, *rpc_handler*)  
Recreate an existing RemoteJob from its unique identifier, and a RPCHandler.

Parameters:  
- **job_id** (`str`) – existing unique identifier

- **rpc_handler** – a RPCHandler with valid credentials to connect to the Cloud provider where the job was sent

Return type:  
[`RemoteJob`](#perceval.runtime.legacy.remote_job.RemoteJob "perceval.runtime.legacy.remote_job.RemoteJob")

get_results()  
Retrieve the results of the job.

Return type:  
`dict`

Returns:  
results dictionary. You can expect a “results” or a “results_list” field, performance scores and other data corresponding to the job nature.

Raises:  
RuntimeError if the job hasn’t finished running, or if the results data are empty or malformed.

*property* id*: str \| None*  
Job unique identifier

Returns:  
a UUID, or None if the job was never sent to a Cloud provider

*property* name*: str*  
The job name

rerun()  
Rerun a job. Same job will be executed again as a new one. Job must have failed, meaning job status is either CANCELED or ERROR.

Raises:  
**RuntimeError** – Job have not failed, therefore it cannot be rerun.

Return type:  
[`RemoteJob`](#perceval.runtime.legacy.remote_job.RemoteJob "perceval.runtime.legacy.remote_job.RemoteJob")

Returns:  
The new remote job.

*property* status*: [ExecutionStatus](https://perceval.quandela.net/docs/v1.3/reference/runtime/execution_status.html#perceval.runtime.execution_status.ExecutionStatus "perceval.runtime.execution_status.ExecutionStatus")*  
The job status metadata structure

*property* was_sent*: bool*  
Returns:  
True if the job was sent to a Cloud provider, False otherwise
