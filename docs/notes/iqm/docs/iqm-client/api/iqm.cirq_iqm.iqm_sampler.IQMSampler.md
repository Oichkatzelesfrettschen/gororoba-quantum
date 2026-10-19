> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.iqm_sampler.IQMSampler.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.iqm_sampler.IQMSampler.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 fdf0943b55556d4ed77e668a2dea1a2878d5e3d04599e98ce2e63396f03af1a2.

# IQMSampler

Module: [`iqm.cirq_iqm.iqm_sampler`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.iqm_sampler.html#module-iqm.cirq_iqm.iqm_sampler "iqm.cirq_iqm.iqm_sampler")

*class* iqm.cirq_iqm.iqm_sampler.IQMSampler(*url: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *\**, *quantum_computer: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *device: [IQMDevice](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.devices.iqm_device.IQMDevice.html#iqm.cirq_iqm.devices.iqm_device.IQMDevice "iqm.cirq_iqm.devices.iqm_device.IQMDevice") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *calibration_set_id: [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *run_sweep_timeout: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *compiler_options: [CircuitCompilationOptions](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.CircuitCompilationOptions.html#iqm.iqm_client.models.CircuitCompilationOptions "iqm.iqm_client.models.CircuitCompilationOptions") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *use_timeslot: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*, *\*\*user_auth_args*)  
Bases: `Sampler`

Circuit sampler for executing quantum circuits on IQM quantum computers.

IQMSampler connects to a quantum computer through an IQM Server. The IQM Server URL and quantum computer can alternatively be provided as environment variables IQM_SERVER_URL and IQM_QUANTUM_COMPUTER (init arguments have priority if provided). If the server requires user authentication, you can provide it either using environment variables, or as keyword arguments to IQMSampler. The user authentication kwargs are passed through to [`IQMClient`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.iqm_client.IQMClient.html#iqm.iqm_client.iqm_client.IQMClient "iqm.iqm_client.iqm_client.IQMClient") as is, and are documented there.

Parameters:  
- **url** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – URL of the IQM Server (e.g. “[https://resonance.iqm.tech/](https://resonance.iqm.tech/)”). If `None`, must be provided as an environment variable IQM_SERVER_URL.

- **quantum_computer** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – ID or alias of the quantum computer to connect to, if the IQM Server instance controls more than one (e.g. “garnet”). `None` means connect to the default one.

- **use_timeslot** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Submits the job to the timeslot queue if set to `True`. If set to `False`, the job is submitted to the normal on-demand queue.

- **device** ([*IQMDevice*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.devices.iqm_device.IQMDevice.html#iqm.cirq_iqm.devices.iqm_device.IQMDevice "iqm.cirq_iqm.devices.iqm_device.IQMDevice") *\|* *None*) – Device to execute the circuits on. If `None`, the device will be created based on the calibration-specific dynamic quantum architecture obtained from [`IQMClient`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.iqm_client.IQMClient.html#iqm.iqm_client.iqm_client.IQMClient "iqm.iqm_client.iqm_client.IQMClient").

- **calibration_set_id** (*UUID* *\|* *None*) – ID of the calibration set to use. If `None`, use the default one.

- **run_sweep_timeout** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* *None*) – Timeout for polling sweep results, in seconds. If `None`, use the client default value.

- **compiler_options** ([*CircuitCompilationOptions*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.CircuitCompilationOptions.html#iqm.iqm_client.models.CircuitCompilationOptions "iqm.iqm_client.models.CircuitCompilationOptions") *\|* *None*) – The compilation options to use for the circuits, as defined by IQM Client.

Attributes

|  |  |
|----|----|
| [`device`](#iqm.cirq_iqm.iqm_sampler.IQMSampler.device "iqm.cirq_iqm.iqm_sampler.IQMSampler.device") | Returns the device used by the sampler. |

Methods

|  |  |
|----|----|
| [`create_circuit_job_definition`](#iqm.cirq_iqm.iqm_sampler.IQMSampler.create_circuit_job_definition "iqm.cirq_iqm.iqm_sampler.IQMSampler.create_circuit_job_definition") | Create a circuit job definition without submitting it for execution. |
| [`run_iqm_batch`](#iqm.cirq_iqm.iqm_sampler.IQMSampler.run_iqm_batch "iqm.cirq_iqm.iqm_sampler.IQMSampler.run_iqm_batch") | Sends a batch of circuits to be executed. |
| [`run_sweep`](#iqm.cirq_iqm.iqm_sampler.IQMSampler.run_sweep "iqm.cirq_iqm.iqm_sampler.IQMSampler.run_sweep") | Execute the given quantum circuit for various values of the given parameters. |
| [`run_sweep_async`](#iqm.cirq_iqm.iqm_sampler.IQMSampler.run_sweep_async "iqm.cirq_iqm.iqm_sampler.IQMSampler.run_sweep_async") | Asynchronously samples from the given Circuit. |

*property* device*: [IQMDevice](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.devices.iqm_device.IQMDevice.html#iqm.cirq_iqm.devices.iqm_device.IQMDevice "iqm.cirq_iqm.devices.iqm_device.IQMDevice")*  
Returns the device used by the sampler.

run_sweep(*program: Circuit*, *params: ParamResolver \| [Mapping](https://docs.python.org/3.11/library/typing.html#typing.Mapping "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| Expr, [complex](https://docs.python.org/3.11/library/functions.html#complex "(in Python v3.11)") \| [number](https://numpy.org/doc/stable/reference/arrays.scalars.html#numpy.number "(in NumPy v2.5)") \| Expr\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") \| Sweep \| \_Sweepable*, *repetitions: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 1*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[IQMResult](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.iqm_sampler.IQMResult.html#iqm.cirq_iqm.iqm_sampler.IQMResult "iqm.cirq_iqm.iqm_sampler.IQMResult")\]  
Execute the given quantum circuit for various values of the given parameters.

Parameters:  
- **program** (*Circuit*)

- **params** (*ParamResolver* *\|* [*Mapping*](https://docs.python.org/3.11/library/typing.html#typing.Mapping "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *Expr,* [*complex*](https://docs.python.org/3.11/library/functions.html#complex "(in Python v3.11)") *\|* [*number*](https://numpy.org/doc/stable/reference/arrays.scalars.html#numpy.number "(in NumPy v2.5)") *\|* *Expr\]* *\|* *None* *\|* *Sweep* *\|* *\_Sweepable*)

- **repetitions** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*IQMResult*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.iqm_sampler.IQMResult.html#iqm.cirq_iqm.iqm_sampler.IQMResult "iqm.cirq_iqm.iqm_sampler.IQMResult")\]

run_iqm_batch(*programs: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[Circuit\]*, *repetitions: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 1*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[IQMResult](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.iqm_sampler.IQMResult.html#iqm.cirq_iqm.iqm_sampler.IQMResult "iqm.cirq_iqm.iqm_sampler.IQMResult")\]  
Sends a batch of circuits to be executed.

Running circuits in a batch is more efficient and hence completes quicker than running the circuits individually. Circuits run in a batch must all measure the same qubits.

Parameters:  
- **programs** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[Circuit\]*) – quantum circuits to execute

- **repetitions** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – number of times the circuits are sampled

Returns:  
results of the execution

Raises:  
- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – circuits are not valid for execution

- **CircuitExecutionError** – something went wrong on the server

- **RequestTimeoutError** – server did not return the results in the allocated time

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*IQMResult*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.iqm_sampler.IQMResult.html#iqm.cirq_iqm.iqm_sampler.IQMResult "iqm.cirq_iqm.iqm_sampler.IQMResult")\]

create_circuit_job_definition(*programs: Circuit \| [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[Circuit\]*, *\**, *params: ParamResolver \| [Mapping](https://docs.python.org/3.11/library/typing.html#typing.Mapping "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| Expr, [complex](https://docs.python.org/3.11/library/functions.html#complex "(in Python v3.11)") \| [number](https://numpy.org/doc/stable/reference/arrays.scalars.html#numpy.number "(in NumPy v2.5)") \| Expr\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") \| Sweep \| \_Sweepable = None*, *repetitions: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 1*) → PostJobsRequest  
Create a circuit job definition without submitting it for execution.

This takes the same parameters as `run()` and [`run_iqm_batch()`](#iqm.cirq_iqm.iqm_sampler.IQMSampler.run_iqm_batch "iqm.cirq_iqm.iqm_sampler.IQMSampler.run_iqm_batch"), and can be used to check the circuit job definition that would be sent when calling those functions.

Parameters:  
- **programs** (*Circuit* *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[Circuit\]*) – quantum circuit(s) that would be executed when submitting the circuit job definition

- **params** (*ParamResolver* *\|* [*Mapping*](https://docs.python.org/3.11/library/typing.html#typing.Mapping "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *Expr,* [*complex*](https://docs.python.org/3.11/library/functions.html#complex "(in Python v3.11)") *\|* [*number*](https://numpy.org/doc/stable/reference/arrays.scalars.html#numpy.number "(in NumPy v2.5)") *\|* *Expr\]* *\|* *None* *\|* *Sweep* *\|* *\_Sweepable*) – same as `params` for `run()`, used only if `programs` is not a list

- **repetitions** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – number of times the circuits are sampled

Returns:  
the created circuit job definition

Return type:  
*PostJobsRequest*

run_sweep_async(*program: cirq.AbstractCircuit*, *params: cirq.Sweepable*, *repetitions: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 1*) → [Sequence](https://docs.python.org/3.11/library/typing.html#typing.Sequence "(in Python v3.11)")\[cirq.Result\]  
Asynchronously samples from the given Circuit.

By default, this method invokes run_sweep synchronously and simply exposes its result is an awaitable. Child classes that are capable of true asynchronous sampling should override it to use other strategies.

Parameters:  
- **program** (*cirq.AbstractCircuit*) – The circuit to sample from.

- **params** (*cirq.Sweepable*) – Parameters to run with the program.

- **repetitions** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of times to sample.

Returns:  
Result list for this run; one for each possible parameter resolver.

Return type:  
[*Sequence*](https://docs.python.org/3.11/library/typing.html#typing.Sequence "(in Python v3.11)")\[cirq.Result\]

Inheritance

![Inheritance diagram of iqm.cirq_iqm.iqm_sampler.IQMSampler](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-8a2ae259e2f9dc0e24d5b3a106ba401a4d8dfab8.png)
