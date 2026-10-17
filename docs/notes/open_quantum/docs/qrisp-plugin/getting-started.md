> Full piece: [https://docs.openquantum.com/qrisp-plugin/getting-started/](https://docs.openquantum.com/qrisp-plugin/getting-started/)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 9c2a62620a249c80bd7cc5ead8a00644c78000d80d9899c9fe3859b096f029f5.

# Qrisp Plugin Getting Started

## Install

[](#__codelineno-0-1)`pip`` ``install`` ``"openquantum-sdk[qrisp]"`\

This installs the Qrisp backend along with `qrisp`, `openquantum-sdk` (Core SDK), and `openquantum-sdk-qiskit`.

## Create a Backend

The `OpenQuantumBackend` builds an `OpenQuantumService` with `from_env()`. Authentication is resolved in this order: a pre-built `service`, then a `token`, then `client_id` + `client_secret` (or an SDK-key file at `OPENQUANTUM_SDK_KEY`). Each explicit value falls back to the matching environment variable. Omitted service URLs also read `OPENQUANTUM_SCHEDULER_URL`, `OPENQUANTUM_MANAGEMENT_URL`, `OPENQUANTUM_KEYCLOAK_BASE`, and `OPENQUANTUM_KEYCLOAK_REALM`. If nothing resolves, construction raises `AuthenticationError`.

### With Environment Variables (recommended)

[](#__codelineno-1-1)`export`` ``OPENQUANTUM_CLIENT_ID``=``"s_your_client_id"`\
[](#__codelineno-1-2)`export`` ``OPENQUANTUM_CLIENT_SECRET``=``"your_client_secret"`\

[](#__codelineno-2-1)`from`` ``qrisp_openquantum`` ``import`` ``OpenQuantumBackend`\
[](#__codelineno-2-2)\
[](#__codelineno-2-3)`oq`` ``=`` ``OpenQuantumBackend``(``backend``=``"rigetti:cepheus-1-108q"``,`` ``shots``=``1024``)`\

### With Explicit Credentials

[](#__codelineno-3-1)`oq`` ``=`` ``OpenQuantumBackend``(`\
[](#__codelineno-3-2)`    ``backend``=``"rigetti:cepheus-1-108q"``,`\
[](#__codelineno-3-3)`    ``shots``=``1024``,`\
[](#__codelineno-3-4)`    ``client_id``=``"s_your_client_id"``,`\
[](#__codelineno-3-5)`    ``client_secret``=``"your_client_secret"``,`\
[](#__codelineno-3-6)`)`\

### With a Pre-built Service

Reuse an existing `OpenQuantumService` (for saved accounts, custom URLs, or keyring-backed credentials):

[](#__codelineno-4-1)`from`` ``openquantum_sdk_qiskit`` ``import`` ``OpenQuantumService`\
[](#__codelineno-4-2)`from`` ``qrisp_openquantum`` ``import`` ``OpenQuantumBackend`\
[](#__codelineno-4-3)\
[](#__codelineno-4-4)`service`` ``=`` ``OpenQuantumService``.``from_saved_account``(``name``=``"default"``)`\
[](#__codelineno-4-5)`oq`` ``=`` ``OpenQuantumBackend``(``backend``=``"rigetti:cepheus-1-108q"``,`` ``shots``=``1024``,`` ``service``=``service``)`\

## Run a Program

Pass the backend to `get_measurement` on a `QuantumVariable`:

[](#__codelineno-5-1)`from`` ``qrisp`` ``import`` ``QuantumVariable``,`` ``h``,`` ``cx`\
[](#__codelineno-5-2)\
[](#__codelineno-5-3)`qv`` ``=`` ``QuantumVariable``(``2``)`\
[](#__codelineno-5-4)`h``(``qv``[``0``])`\
[](#__codelineno-5-5)`cx``(``qv``[``0``],`` ``qv``[``1``])`\
[](#__codelineno-5-6)\
[](#__codelineno-5-7)`print``(``qv``.``get_measurement``(``backend``=``oq``,`` ``shots``=``1024``))`\
[](#__codelineno-5-8)`# {'00': 0.51, '11': 0.49}`\

Note

`get_measurement` returns Qrisp's decoded outcomes as **probabilities**, not shot counts. This is Qrisp's own normalization and applies to every backend. To get integer counts, run a low-level `QuantumCircuit` with `QuantumCircuit.run(backend=oq, shots=...)`, shown next.

Or run a raw `QuantumCircuit` directly, which returns integer counts:

[](#__codelineno-6-1)`from`` ``qrisp`` ``import`` ``QuantumCircuit`\
[](#__codelineno-6-2)\
[](#__codelineno-6-3)`qc`` ``=`` ``QuantumCircuit``(``2``)`\
[](#__codelineno-6-4)`qc``.``h``(``0``)`\
[](#__codelineno-6-5)`qc``.``cx``(``0``,`` ``1``)`\
[](#__codelineno-6-6)`qc``.``measure``([``0``,`` ``1``])`\
[](#__codelineno-6-7)\
[](#__codelineno-6-8)`counts`` ``=`` ``qc``.``run``(``backend``=``oq``,`` ``shots``=``1024``)`\
[](#__codelineno-6-9)`# e.g. {'00': 518, '11': 506}`\

## Backend-Specific Configuration

Some backends require extra parameters. Simulators in the Quantum Rings family, for example, require an `engine`. Pass these through `configuration_data`:

[](#__codelineno-7-1)`oq`` ``=`` ``OpenQuantumBackend``(`\
[](#__codelineno-7-2)`    ``backend``=``"qr:gpu-gb10"``,`\
[](#__codelineno-7-3)`    ``shots``=``1024``,`\
[](#__codelineno-7-4)`    ``configuration_data``=``{``"engine"``:`` ``"amber_quantum_rings"``},`\
[](#__codelineno-7-5)`)`\

Note

Only send the fields a backend actually needs. Conditional schema fields (for example a `threshold` that only applies when `performance="CUSTOM"`) should be set explicitly and only when they apply.

## Cost and Scheduling Controls

[](#__codelineno-8-1)`oq`` ``=`` ``OpenQuantumBackend``(`\
[](#__codelineno-8-2)`    ``backend``=``"ionq:forte-1"``,`\
[](#__codelineno-8-3)`    ``shots``=``1024``,`\
[](#__codelineno-8-4)`    ``job_subcategory_id``=``"ml:qcl"``,``   ``# classify your workload`\
[](#__codelineno-8-5)`    ``execution_plan``=``"private"``,``       ``# "auto" | "public" | "private"`\
[](#__codelineno-8-6)`    ``queue_priority``=``"priority"``,``      ``# "auto" | "standard" | "priority" | "instant"`\
[](#__codelineno-8-7)`    ``organization_id``=``"your-org-uuid"``,`\
[](#__codelineno-8-8)`    ``job_timeout_seconds``=``3600``,``       ``# max wait (default 86400 / 1 day)`\
[](#__codelineno-8-9)`)`\

## Next Steps

- [Supported Operations](https://docs.openquantum.com/qrisp-plugin/supported-operations/) — gates, measurements, and bit ordering.
- [Examples](https://docs.openquantum.com/qrisp-plugin/examples/) — more Qrisp workflows.
- [Troubleshooting](https://docs.openquantum.com/qrisp-plugin/troubleshooting/) — auth, backend config, and common errors.
