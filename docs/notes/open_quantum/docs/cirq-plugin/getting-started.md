> Full piece: [https://docs.openquantum.com/cirq-plugin/getting-started/](https://docs.openquantum.com/cirq-plugin/getting-started/)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3570a14b4ba2c8bc87f73f4b45662efac0eac585cd1bc31ac6bbd4e2f36bc694.

# Cirq Plugin Getting Started

## Install

[](#__codelineno-0-1)`pip`` ``install`` ``"openquantum-sdk[cirq]"`\

This installs the Cirq sampler along with `cirq-core` and `openquantum-sdk` (Core SDK).

## Create a Sampler

The `OpenQuantumSampler` builds an `OpenQuantumClient` with `from_env()`. Authentication is resolved in this order: a pre-built `client`, then a `token`, then `client_id` + `client_secret` (or an SDK-key file at `OPENQUANTUM_SDK_KEY`). Each explicit value falls back to the matching environment variable. Omitted service URLs also read `OPENQUANTUM_SCHEDULER_URL`, `OPENQUANTUM_MANAGEMENT_URL`, `OPENQUANTUM_KEYCLOAK_BASE`, and `OPENQUANTUM_KEYCLOAK_REALM`. If nothing resolves, construction raises `AuthenticationError`.

### With Environment Variables (recommended)

[](#__codelineno-1-1)`export`` ``OPENQUANTUM_CLIENT_ID``=``"s_your_client_id"`\
[](#__codelineno-1-2)`export`` ``OPENQUANTUM_CLIENT_SECRET``=``"your_client_secret"`\

[](#__codelineno-2-1)`from`` ``cirq_openquantum`` ``import`` ``OpenQuantumSampler`\
[](#__codelineno-2-2)\
[](#__codelineno-2-3)`sampler`` ``=`` ``OpenQuantumSampler``(``backend``=``"rigetti:cepheus-1-108q"``)`\

### With Explicit Credentials

[](#__codelineno-3-1)`sampler`` ``=`` ``OpenQuantumSampler``(`\
[](#__codelineno-3-2)`    ``backend``=``"rigetti:cepheus-1-108q"``,`\
[](#__codelineno-3-3)`    ``client_id``=``"s_your_client_id"``,`\
[](#__codelineno-3-4)`    ``client_secret``=``"your_client_secret"``,`\
[](#__codelineno-3-5)`)`\

### With a Pre-built Client

Reuse an existing `OpenQuantumClient` (for saved accounts, custom URLs, or keyring-backed credentials):

[](#__codelineno-4-1)`from`` ``openquantum_sdk`` ``import`` ``OpenQuantumClient`\
[](#__codelineno-4-2)`from`` ``cirq_openquantum`` ``import`` ``OpenQuantumSampler`\
[](#__codelineno-4-3)\
[](#__codelineno-4-4)`client`` ``=`` ``OpenQuantumClient``.``from_saved_account``(``name``=``"default"``)`\
[](#__codelineno-4-5)`sampler`` ``=`` ``OpenQuantumSampler``(``backend``=``"rigetti:cepheus-1-108q"``,`` ``client``=``client``)`\

## Run a Circuit

Build a circuit with a measurement and call `run`:

[](#__codelineno-5-1)`import`` ``cirq`\
[](#__codelineno-5-2)\
[](#__codelineno-5-3)`q`` ``=`` ``cirq``.``LineQubit``.``range``(``2``)`\
[](#__codelineno-5-4)`circuit`` ``=`` ``cirq``.``Circuit``([`\
[](#__codelineno-5-5)`    ``cirq``.``H``(``q``[``0``]),`\
[](#__codelineno-5-6)`    ``cirq``.``CNOT``(``q``[``0``],`` ``q``[``1``]),`\
[](#__codelineno-5-7)`    ``cirq``.``measure``(``*``q``,`` ``key``=``"m"``),`\
[](#__codelineno-5-8)`])`\
[](#__codelineno-5-9)\
[](#__codelineno-5-10)`result`` ``=`` ``sampler``.``run``(``circuit``,`` ``repetitions``=``1024``)`\
[](#__codelineno-5-11)`print``(``result``.``histogram``(``key``=``"m"``))`\
[](#__codelineno-5-12)`# Counter({0: ~512, 3: ~512})   # 00 and 11`\

`result` is a standard `cirq.Result`, so `result.measurements["m"]`, `result.histogram(key="m")`, and `cirq.plot_state_histogram(result)` all work.

## Backend-Specific Configuration

Some backends require extra parameters. Simulators in the Quantum Rings family, for example, require an `engine`. Pass these through `configuration_data`:

[](#__codelineno-6-1)`sampler`` ``=`` ``OpenQuantumSampler``(`\
[](#__codelineno-6-2)`    ``backend``=``"qr:gpu-gb10"``,`\
[](#__codelineno-6-3)`    ``configuration_data``=``{``"engine"``:`` ``"amber_quantum_rings"``},`\
[](#__codelineno-6-4)`)`\

Note

Only send the fields a backend actually needs. Conditional schema fields (for example a `threshold` that only applies when `performance="CUSTOM"`) should be set explicitly and only when they apply.

## Cost and Scheduling Controls

[](#__codelineno-7-1)`sampler`` ``=`` ``OpenQuantumSampler``(`\
[](#__codelineno-7-2)`    ``backend``=``"ionq:forte-1"``,`\
[](#__codelineno-7-3)`    ``job_subcategory_id``=``"ml:qcl"``,``   ``# classify your workload`\
[](#__codelineno-7-4)`    ``execution_plan``=``"private"``,``       ``# "auto" | "public" | "private"`\
[](#__codelineno-7-5)`    ``queue_priority``=``"priority"``,``      ``# "auto" | "standard" | "priority" | "instant"`\
[](#__codelineno-7-6)`    ``organization_id``=``"your-org-uuid"``,`\
[](#__codelineno-7-7)`    ``job_timeout_seconds``=``3600``,``       ``# max wait (default 86400 / 1 day)`\
[](#__codelineno-7-8)`)`\

## Next Steps

- [Supported Operations](https://docs.openquantum.com/cirq-plugin/supported-operations/) — gates, measurements, and bit ordering.
- [Examples](https://docs.openquantum.com/cirq-plugin/examples/) — more Cirq workflows.
- [Troubleshooting](https://docs.openquantum.com/cirq-plugin/troubleshooting/) — auth, backend config, and common errors.
