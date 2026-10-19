> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.CircuitExecutionError.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.CircuitExecutionError.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 dc85a59e3ec140ea5524f091b7689d9f4be4a4946fb57d1408fb6ed23cacfcf4.

# exa.common.errors.iqm_error.CircuitExecutionError

*exception* CircuitExecutionError(*message*, *\**, *error_code=None*, *log_level=40*)  
Raised when a failure occurs during the physical execution of a circuit.

In synchronous flows, this error is raised directly to the caller. In asynchronous flows, this error is only raised if the execution fails before a job can be successfully created; otherwise, the failure is recorded within the job’s terminal status.

Parameters:  
- **message** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **error_code** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*)

- **log_level** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))
