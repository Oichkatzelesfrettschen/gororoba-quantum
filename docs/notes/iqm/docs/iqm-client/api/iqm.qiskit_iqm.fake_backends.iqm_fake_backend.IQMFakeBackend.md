> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMFakeBackend.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMFakeBackend.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d608ed896631f7aebe61316c0bd8bd7385496633893b32b6c0ec6733ea3cf43d.

# IQMFakeBackend

Module: [`iqm.qiskit_iqm.fake_backends.iqm_fake_backend`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.fake_backends.iqm_fake_backend.html#module-iqm.qiskit_iqm.fake_backends.iqm_fake_backend "iqm.qiskit_iqm.fake_backends.iqm_fake_backend")

*class* iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMFakeBackend(*architecture: StaticQuantumArchitecture*, *error_profile: [IQMErrorProfile](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMErrorProfile.html#iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMErrorProfile "iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMErrorProfile")*, *name: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") = 'IQMFakeBackend'*, *\*\*kwargs*)  
Bases: [`IQMBackendBase`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "iqm.qiskit_iqm.iqm_backend.IQMBackendBase")

Simulated backend that mimics the behaviour of IQM quantum computers.

Can be used to perform noisy gate-level simulations of quantum circuit execution on IQM hardware.

A fake backend contains information about a specific IQM system, such as the static quantum architecture (number of qubits, connectivity), and a noise model based on system parameters such as relaxation (\\T_1\\) and dephasing (\\T_2\\) times, gate infidelities, and readout errors.

Parameters:  
- **architecture** (*StaticQuantumArchitecture*) – Static quantum architecture associated with the backend instance.

- **error_profile** ([*IQMErrorProfile*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMErrorProfile.html#iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMErrorProfile "iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMErrorProfile")) – Characteristics of a particular QPU specimen.

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

Attributes

|  |  |
|----|----|
| [`error_profile`](#iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMFakeBackend.error_profile "iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMFakeBackend.error_profile") | Error profile of this IQM fake backend instance. |
| `name` | Name of the backend. |
| `description` | Optional human-readable description. |
| `online_date` | Date that the backend came online. |
| `backend_version` | Version of the backend being provided. |

Methods

|  |  |
|----|----|
| [`copy_with_error_profile`](#iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMFakeBackend.copy_with_error_profile "iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMFakeBackend.copy_with_error_profile") | New instance of IQMFakeBackend which has the same quantum architecture but a different error profile. |
| [`run`](#iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMFakeBackend.run "iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMFakeBackend.run") | Run quantum circuits on the fake backend (by simulating them). |
| [`validate_compatible_architecture`](#iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMFakeBackend.validate_compatible_architecture "iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMFakeBackend.validate_compatible_architecture") | Compare a static quantum architecture to the static architecture of the fake backend. |

*property* error_profile*: [IQMErrorProfile](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMErrorProfile.html#iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMErrorProfile "iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMErrorProfile")*  
Error profile of this IQM fake backend instance.

copy_with_error_profile(*new_error_profile: [IQMErrorProfile](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMErrorProfile.html#iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMErrorProfile "iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMErrorProfile")*) → [IQMFakeBackend](#iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMFakeBackend "iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMFakeBackend")  
New instance of IQMFakeBackend which has the same quantum architecture but a different error profile.

Parameters:  
**new_error_profile** ([*IQMErrorProfile*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMErrorProfile.html#iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMErrorProfile "iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMErrorProfile"))

Return type:  
[*IQMFakeBackend*](#iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMFakeBackend "iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMFakeBackend")

run(*run_input: [QuantumCircuit](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)") \| [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[QuantumCircuit](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")\]*, *\*\*options*) → [JobV1](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.providers.JobV1 "(in Qiskit v2.5)")  
Run quantum circuits on the fake backend (by simulating them).

This method will run the simulation with the noise model of the fake backend. Validity of the circuits is also checked.

Parameters:  
- **run_input** ([*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)") *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")*\]*) – One or more quantum circuits to simulate on the backend.

- **options** – Any kwarg options to pass to the backend.

Returns:  
The job object representing the run.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – Empty list of circuits was provided.

Return type:  
[*JobV1*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.providers.JobV1 "(in Qiskit v2.5)")

validate_compatible_architecture(*architecture: StaticQuantumArchitecture*) → [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")  
Compare a static quantum architecture to the static architecture of the fake backend.

Parameters:  
**architecture** (*StaticQuantumArchitecture*) – static quantum architecture to compare to

Returns:  
True iff the locus components and the component connectivity in the IQMFakeBackend SQA match `architecture`.

Return type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

Inheritance

![Inheritance diagram of iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMFakeBackend](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-705ca5232890bd5e99feef57661c9976322004da.png)
