> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMProvider.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMProvider.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 afaab7412a01cf7ca6d1a7e7fcb982636fe32728fdd97f76631978f185003ac5.

# IQMProvider

Module: [`iqm.qiskit_iqm.iqm_provider`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.html#module-iqm.qiskit_iqm.iqm_provider "iqm.qiskit_iqm.iqm_provider")

*class* iqm.qiskit_iqm.iqm_provider.IQMProvider(*url: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *\**, *quantum_computer: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *\*\*user_auth_args*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Provider for IQM backends.

IQMProvider connects to a quantum computer through an IQM Server. The IQM Server URL and quantum computer can alternatively be provided as environment variables IQM_SERVER_URL and IQM_QUANTUM_COMPUTER (init arguments have priority if provided). If the server requires user authentication, you can provide it either using environment variables, or as keyword arguments to IQMProvider. The user authentication kwargs are passed through to [`IQMClient`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.iqm_client.IQMClient.html#iqm.iqm_client.iqm_client.IQMClient "iqm.iqm_client.iqm_client.IQMClient") as is, and are documented there.

Parameters:  
- **url** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – URL of the IQM Server (e.g. “[https://resonance.iqm.tech/](https://resonance.iqm.tech/)”). If `None`, must be provided in the environment variable `IQM_SERVER_URL`.

- **quantum_computer** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – ID or alias of the quantum computer to connect to, if the IQM Server instance controls more than one (e.g. “garnet”). `None` means connect to the default one.

Methods

|  |  |
|----|----|
| [`get_backend`](#iqm.qiskit_iqm.iqm_provider.IQMProvider.get_backend "iqm.qiskit_iqm.iqm_provider.IQMProvider.get_backend") | IQMBackend instance associated with this provider. |

get_backend(*name: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *calibration_set_id: [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *\**, *use_metrics: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*) → [IQMBackend](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend "iqm.qiskit_iqm.iqm_provider.IQMBackend")  
IQMBackend instance associated with this provider.

Parameters:  
- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – Optional name of a facade backend to request, see [`IQMFacadeBackend`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend.html#iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend "iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend").

- **calibration_set_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") *\|* *None*) – ID of the calibration set to be used with the backend. Affects both the transpilation target and the circuit execution. If None, the server default calibration set will be used.

- **use_metrics** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If True, the backend will provide calibration data and related quality metrics to the transpilation target to improve the transpilation. The default value is set to False until quality metrics become available on the Resonance API.

Returns:  
Backend instance for connecting to a quantum computer.

Return type:  
[*IQMBackend*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend "iqm.qiskit_iqm.iqm_provider.IQMBackend")

Inheritance

![Inheritance diagram of iqm.qiskit_iqm.iqm_provider.IQMProvider](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-a32567bdd1f8fa8ac6169e7fbe2f4cedf1ca7a2a.png)
