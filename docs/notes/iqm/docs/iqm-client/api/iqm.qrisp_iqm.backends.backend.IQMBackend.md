> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.backend.IQMBackend.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.backend.IQMBackend.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 cca9d021aa3691d91aab7c7c8a5b0552f51172832b13f1846d3a0c62b9962f21.

# IQMBackend

Module: [`iqm.qrisp_iqm.backends.backend`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.backend.html#module-iqm.qrisp_iqm.backends.backend "iqm.qrisp_iqm.backends.backend")

*class* iqm.qrisp_iqm.backends.backend.IQMBackend(*server_url: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *\**, *device_instance: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *iqm_client: [IQMClient](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.iqm_client.IQMClient.html#iqm.iqm_client.iqm_client.IQMClient "iqm.iqm_client.iqm_client.IQMClient") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *transpiler: Callable\[\[QuantumCircuit\], QuantumCircuit\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *calibration_set_id: UUID \| [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *use_metrics: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*, *pass_manager: PassManager \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *use_timeslot: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*, *compilation_options: [CircuitCompilationOptions](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.CircuitCompilationOptions.html#iqm.iqm_client.models.CircuitCompilationOptions "iqm.iqm_client.models.CircuitCompilationOptions") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *compiler: Compiler \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *\*\*user_auth_args*)  
Bases: `Backend`

Qrisp backend for executing circuits on IQM quantum hardware.

After transpilation, [`run_async()`](#iqm.qrisp_iqm.backends.backend.IQMBackend.run_async "iqm.qrisp_iqm.backends.backend.IQMBackend.run_async") automatically detects whether any of the circuits contains [`IQMPulseOperation`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.pulse_operation.IQMPulseOperation.html#iqm.qrisp_iqm.pulse_operation.IQMPulseOperation "iqm.qrisp_iqm.pulse_operation.IQMPulseOperation") instructions, and routes the job to the appropriate submission path:

- **No pulse ops** → submitted as a gate-level [`IQMCircuitJob`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.iqm_circuit_job.IQMCircuitJob.html#iqm.qrisp_iqm.backends.iqm_circuit_job.IQMCircuitJob "iqm.qrisp_iqm.backends.iqm_circuit_job.IQMCircuitJob").

- **Has pulse ops** → compiled locally down to pulse level, and submitted as a [`IQMPulseJob`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.iqm_pulse_job.IQMPulseJob.html#iqm.qrisp_iqm.backends.iqm_pulse_job.IQMPulseJob "iqm.qrisp_iqm.backends.iqm_pulse_job.IQMPulseJob").

The `server_url` and `device_instance` parameters can alternatively be provided as the environment variables `IQM_SERVER_URL` and `IQM_QUANTUM_COMPUTER`. If the server requires user authentication, you can provide it either using environment variables or as keyword arguments. The user authentication kwargs are passed through to [`IQMClient`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.iqm_client.IQMClient.html#iqm.iqm_client.iqm_client.IQMClient "iqm.iqm_client.iqm_client.IQMClient") as is, and are documented there.

Parameters:  
- **server_url** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – URL for connecting to a quantum computer. If None, use environment variable `IQM_SERVER_URL`.

- **device_instance** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – IQM quantum computer identifier (e.g., `"garnet"`). If None, use environment variable `IQM_QUANTUM_COMPUTER`. If it is not defined, use the default quantum computer on the server.

- **user_auth_args** – User authentication information, e.g. an API token.

- **iqm_client** ([*IQMClient*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.iqm_client.IQMClient.html#iqm.iqm_client.iqm_client.IQMClient "iqm.iqm_client.iqm_client.IQMClient") *\|* *None*) – If not None, use this client instance and ignore `server_url`, `device_instance` and `user_auth_args`.

- **transpiler** (*Callable\[\[QuantumCircuit\],* *QuantumCircuit\]* *\|* *None*) –

  Deprecated since version 36.0.0: Use `pass_manager` instead.

  Transforms quantum circuits for hardware compatibility. If provided, a `DeprecationWarning` is raised and the callable is wrapped in a `CircuitPass` and installed as the sole pass in the `PassManager`. Must not be used together with `pass_manager`.

- **calibration_set_id** (*UUID* *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – ID of the calibration set to use. `None` means the server’s current default calibration set is used.

- **use_metrics** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Iff `True`, the backend will query the server for calibration data and related quality metrics, and pass these to the default pass manager. **Currently a no-op** — the flag is stored and will be wired into both submission paths in a future release.

- **pass_manager** (*PassManager* *\|* *None*) –

  PassManager for circuit transpilation. Accepted values:

  - `None`: Builds a pre-configured PassManager that performs routing, layout and other optimization to bring good performance without configuration overhead.

  - A `PassManager` instance: Used directly for transpilation, bypassing the default pipeline entirely.

- **use_timeslot** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If True, submits the job to the timeslot queue. If False, the job is submitted to the normal on-demand queue.

- **compilation_options** ([*CircuitCompilationOptions*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.CircuitCompilationOptions.html#iqm.iqm_client.models.CircuitCompilationOptions "iqm.iqm_client.models.CircuitCompilationOptions") *\|* *None*) – Options for compiling circuits to pulse schedules. On the pulse-level execution path, the `CircuitCompilationOptions.max_circuit_duration_over_t2` attribute has no effect. `None` means use the default options.

- **compiler** (*Compiler* *\|* *None*) – IQM circuit-to-pulse compiler to use for pulse-level submissions. `None` uses the standard compiler.

Examples: **Automatic transpilation** (default PassManager):

```
>>> from iqm.qrisp_iqm import IQMBackend
>>> backend = IQMBackend(
...     token="YOUR_API_TOKEN",
...     device_instance="garnet"
... )
>>> from qrisp import QuantumCircuit
>>> qc = QuantumCircuit(2)
>>> qc.h(0)
>>> qc.cx(0, 1)
>>> qc.measure(qc.qubits)
>>> result = backend.run(qc, shots=1000)
```

**Custom pass pipeline via :attr:\`pm\`**:

```
>>> from qrisp import PassManager, convert_to_cz, convert_to_prx
>>> from iqm.qrisp_iqm import vf2pp_layout
>>> backend = IQMBackend(
...     token="YOUR_API_TOKEN",
...     device_instance="garnet",
...     pass_manager=PassManager()  # start with an empty manager
... )
>>> coupling_map = [(0, 1), (1, 2), (2, 3)]
>>> backend.pm += vf2pp_layout(coupling_map)
>>> backend.pm += convert_to_cz()
>>> backend.pm += convert_to_prx
>>> result = backend.run(my_circuit, shots=1000)
```

The `pass_manager=PassManager()` constructor argument gives you full control. You can also start from `None` and extend the pipeline (or even insert passes at arbitrary positions via `insert_before()`).

**Pulse-level execution** (automatic routing):

```
>>> from iqm.qrisp_iqm import IQMBackend
>>> from iqm.qrisp_iqm.pulse_operation  import IQMPulseOperation
>>> backend = IQMBackend(
...     token="YOUR_API_TOKEN",
...     device_instance="garnet"
... )
>>> # Circuit with IQMPulseOperation is compiled locally to a pulse-level job.
>>> job = backend.run_async(my_pulse_circuit, shots=1000)
>>> result = job.result()
```

Attributes

|  |  |
|----|----|
| [`connectivity`](#iqm.qrisp_iqm.backends.backend.IQMBackend.connectivity "iqm.qrisp_iqm.backends.backend.IQMBackend.connectivity") | Currently executable qubit connectivity for this IQM backend. |
| [`pm`](#iqm.qrisp_iqm.backends.backend.IQMBackend.pm "iqm.qrisp_iqm.backends.backend.IQMBackend.pm") | The public pass manager for circuit transpilation. |

Methods

|  |  |
|----|----|
| [`retrieve_job`](#iqm.qrisp_iqm.backends.backend.IQMBackend.retrieve_job "iqm.qrisp_iqm.backends.backend.IQMBackend.retrieve_job") | Retrieve a previously submitted job. |
| [`run`](#iqm.qrisp_iqm.backends.backend.IQMBackend.run "iqm.qrisp_iqm.backends.backend.IQMBackend.run") | Transpile and submit circuits for execution, return measurement result(s). |
| [`run_async`](#iqm.qrisp_iqm.backends.backend.IQMBackend.run_async "iqm.qrisp_iqm.backends.backend.IQMBackend.run_async") | Transpile and submit circuits for execution on the IQM device, return immediately. |

pm*: PassManager*  
The public pass manager for circuit transpilation. Set via the `pass_manager` `__init__()` parameter. Can be a pre-built `PassManager` instance or `None` (the default pipeline). After construction, passes can be added incrementally via `+=`.

run(*circuits: QuantumCircuit \| [Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[QuantumCircuit\]*, *shots: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *\**, *use_timeslot: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *compilation_options: [CircuitCompilationOptions](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.CircuitCompilationOptions.html#iqm.iqm_client.models.CircuitCompilationOptions "iqm.iqm_client.models.CircuitCompilationOptions") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → MeasurementResult \| [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[MeasurementResult\]  
Transpile and submit circuits for execution, return measurement result(s).

Blocks until the execution is finished, which may take awhile if there are other jobs in the queue. Consider using [`run_async()`](#iqm.qrisp_iqm.backends.backend.IQMBackend.run_async "iqm.qrisp_iqm.backends.backend.IQMBackend.run_async") instead.

Takes the same args as [`run_async()`](#iqm.qrisp_iqm.backends.backend.IQMBackend.run_async "iqm.qrisp_iqm.backends.backend.IQMBackend.run_async").

Returns:  
A pre-populated `MeasurementResult` when one circuit is submitted, or a list of them for multiple circuits.

Parameters:  
- **circuits** (*QuantumCircuit* *\|* [*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[QuantumCircuit\]*)

- **shots** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*)

- **use_timeslot** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") *\|* *None*)

- **compilation_options** ([*CircuitCompilationOptions*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.CircuitCompilationOptions.html#iqm.iqm_client.models.CircuitCompilationOptions "iqm.iqm_client.models.CircuitCompilationOptions") *\|* *None*)

Return type:  
*MeasurementResult* \| [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[*MeasurementResult*\]

run_async(*circuits: QuantumCircuit \| [Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[QuantumCircuit\]*, *shots: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *\**, *use_timeslot: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *compilation_options: [CircuitCompilationOptions](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.CircuitCompilationOptions.html#iqm.iqm_client.models.CircuitCompilationOptions "iqm.iqm_client.models.CircuitCompilationOptions") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [IQMJob](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.iqm_job.IQMJob.html#iqm.qrisp_iqm.backends.iqm_job.IQMJob "iqm.qrisp_iqm.backends.iqm_job.IQMJob")  
Transpile and submit circuits for execution on the IQM device, return immediately.

Automatically detects whether any of `circuits` contain [`IQMPulseOperation`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.pulse_operation.IQMPulseOperation.html#iqm.qrisp_iqm.pulse_operation.IQMPulseOperation "iqm.qrisp_iqm.pulse_operation.IQMPulseOperation") instances:

- **No pulse ops** → submitted as a gate-level [`IQMCircuitJob`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.iqm_circuit_job.IQMCircuitJob.html#iqm.qrisp_iqm.backends.iqm_circuit_job.IQMCircuitJob "iqm.qrisp_iqm.backends.iqm_circuit_job.IQMCircuitJob").

- **Has pulse ops** → compiled locally down to pulse level, and submitted as a [`IQMPulseJob`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.iqm_pulse_job.IQMPulseJob.html#iqm.qrisp_iqm.backends.iqm_pulse_job.IQMPulseJob "iqm.qrisp_iqm.backends.iqm_pulse_job.IQMPulseJob").

Parameters:  
- **circuits** (*QuantumCircuit* *\|* [*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[QuantumCircuit\]*) – The circuit(s) to execute.

- **shots** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – Number of shots per circuit. If `None`, use the backend default.

- **use_timeslot** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") *\|* *None*) – If True, submits the job to the timeslot queue. If False, the job is submitted to the normal on-demand queue. `None` means use the default set in `__init__()`.

- **compilation_options** ([*CircuitCompilationOptions*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.CircuitCompilationOptions.html#iqm.iqm_client.models.CircuitCompilationOptions "iqm.iqm_client.models.CircuitCompilationOptions") *\|* *None*) – Options for compiling circuits to pulse schedules. On the pulse-level execution path, the `CircuitCompilationOptions.max_circuit_duration_over_t2` attribute has no effect. `None` means use the default set in `__init__()`.

Returns:  
A job handle for the submitted execution.

Return type:  
[*IQMJob*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.iqm_job.IQMJob.html#iqm.qrisp_iqm.backends.iqm_job.IQMJob "iqm.qrisp_iqm.backends.iqm_job.IQMJob")

*property* connectivity*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]*  
Currently executable qubit connectivity for this IQM backend.

Cached once at construction time from the DynamicQuantumArchitecture.

Returns:  
The two-qubit gate coupling map as a list of qubit-index pairs.

retrieve_job(*job_id: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*) → [IQMJob](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.iqm_job.IQMJob.html#iqm.qrisp_iqm.backends.iqm_job.IQMJob "iqm.qrisp_iqm.backends.iqm_job.IQMJob")  
Retrieve a previously submitted job.

Parameters:  
**job_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The IQM job ID (UUID as string) of the job to retrieve.

Returns:  
Handle for the previously submitted job.

Return type:  
[*IQMJob*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.iqm_job.IQMJob.html#iqm.qrisp_iqm.backends.iqm_job.IQMJob "iqm.qrisp_iqm.backends.iqm_job.IQMJob")

Inheritance

![Inheritance diagram of iqm.qrisp_iqm.backends.backend.IQMBackend](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-222641df40778b1a28f1f6a4ae45c3d72fc4046b.png)
