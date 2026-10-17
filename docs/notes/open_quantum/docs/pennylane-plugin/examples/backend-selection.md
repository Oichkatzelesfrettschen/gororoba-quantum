> Full piece: [https://docs.openquantum.com/pennylane-plugin/examples/backend-selection/](https://docs.openquantum.com/pennylane-plugin/examples/backend-selection/)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1223c00ee9f15adcedf175d0d439d5fdc86fd76399e2b0fb44d1ec7d79a5c401.

# Backend Selection

This guide explains how to choose and configure backends on Open Quantum.

## Listing Available Backends

Available backends can be queried from the Management API (no authentication required):

[](#__codelineno-0-1)`curl`` ``https://management.openquantum.com/v1/backends/classes?limit``=``20`\

Response:

[](#__codelineno-1-1)`{`\
[](#__codelineno-1-2)`  ``"backend_classes"``:`` ``[`\
[](#__codelineno-1-3)`    ``{`\
[](#__codelineno-1-4)`      ``"id"``:`` ``"..."``,`\
[](#__codelineno-1-5)`      ``"short_code"``:`` ``"ionq:forte-1"``,`\
[](#__codelineno-1-6)`      ``"name"``:`` ``"IonQ Forte-1"``,`\
[](#__codelineno-1-7)`      ``"type"``:`` ``"QPU"``,`\
[](#__codelineno-1-8)`      ``"status"``:`` ``"Online"``,`\
[](#__codelineno-1-9)`      ``"accepting_jobs"``:`` ``true``,`\
[](#__codelineno-1-10)`      ``"queue_depth"``:`` ``3`\
[](#__codelineno-1-11)`    ``}`\
[](#__codelineno-1-12)`  ``]`\
[](#__codelineno-1-13)`}`\

You can also browse available backends in the [Open Quantum Portal](https://www.openquantum.com).

## Backend Short Codes

Each backend has a unique `short_code` in the format `provider:device`. This is the value you pass to the `backend` parameter:

[](#__codelineno-2-1)`# QPU backend`\
[](#__codelineno-2-2)`dev_qpu`` ``=`` ``qml``.``device``(``"openquantum.device"``,`` ``wires``=``4``,`` ``shots``=``128``,`` ``backend``=``"ionq:forte-1"``)`\

## Backend Properties

Each backend has properties you should be aware of:

| Property | Description |
|----|----|
| **type** | `QPU` (real quantum hardware) |
| **status** | `Online` (accepting jobs), `Offline` (unavailable), or `Maintenance` (scheduled maintenance) |
| **accepting_jobs** | Whether the backend is currently accepting new job submissions |
| **queue_depth** | Number of jobs currently waiting in the queue |
| **max_qubits** | Maximum number of qubits supported (from backend constraints) |

Warning

Check that the backend is `Online` and `accepting_jobs` is `true` before submitting jobs. Submitting to an offline backend will result in a job failure.

## Related Pages

- [Device Options](https://docs.openquantum.com/pennylane-plugin/device-options/) -- Full list of device parameters including `execution_plan` and `queue_priority`.
- [Credits](https://docs.openquantum.com/concepts/credits/) -- How backend choice affects pricing.
- [Backends](https://docs.openquantum.com/concepts/backends/) -- Platform-level backend documentation.
