> Full piece: [https://docs.openquantum.com/qiskit-plugin/getting-started/](https://docs.openquantum.com/qiskit-plugin/getting-started/)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 15223985350e8abc0ebc3f35105ed3f2ba89309a5061d0afedfb63b354f34988.

# Qiskit Plugin Getting Started

## Install

[](#__codelineno-0-1)`pip`` ``install`` ``"openquantum-sdk[qiskit]"`\

This installs the Qiskit plugin along with `openquantum-sdk` (Core SDK) and `qiskit>=2.0.0`.

## Create a Service

### With Credentials

[](#__codelineno-1-1)`from`` ``openquantum_sdk.auth`` ``import`` ``ClientCredentials`\
[](#__codelineno-1-2)`from`` ``openquantum_sdk_qiskit`` ``import`` ``OpenQuantumService`\
[](#__codelineno-1-3)\
[](#__codelineno-1-4)`service`` ``=`` ``OpenQuantumService``(`\
[](#__codelineno-1-5)`    ``creds``=``ClientCredentials``(`\
[](#__codelineno-1-6)`        ``client_id``=``"s_your_client_id"``,`\
[](#__codelineno-1-7)`        ``client_secret``=``"your_client_secret"``,`\
[](#__codelineno-1-8)`    ``),`\
[](#__codelineno-1-9)`)`\

### With a Saved Account

If you have previously saved credentials (see [Authentication](https://docs.openquantum.com/core-sdk/authentication/)):

[](#__codelineno-2-1)`from`` ``openquantum_sdk_qiskit`` ``import`` ``OpenQuantumService`\
[](#__codelineno-2-2)\
[](#__codelineno-2-3)`service`` ``=`` ``OpenQuantumService``.``from_saved_account``(``name``=``"default"``)`\

### With a JWT Token

[](#__codelineno-3-1)`from`` ``openquantum_sdk_qiskit`` ``import`` ``OpenQuantumService`\
[](#__codelineno-3-2)\
[](#__codelineno-3-3)`service`` ``=`` ``OpenQuantumService``(``token``=``"your_jwt_token"``)`\

### Auto-Load

If you have a saved account named `"default"`, the service loads it automatically:

[](#__codelineno-4-1)`service`` ``=`` ``OpenQuantumService``()`\

When that account is missing or cannot be loaded, the same constructor falls back to environment credentials: `OPENQUANTUM_TOKEN`, an SDK-key file at `OPENQUANTUM_SDK_KEY`, or `OPENQUANTUM_CLIENT_ID` + `OPENQUANTUM_CLIENT_SECRET`. An explicit `token` or `creds` argument still wins, and a saved account still wins over the environment.

Tip

Set `OPENQUANTUM_NO_AUTOLOAD=1` to skip the saved account and use only the environment credentials.

### Service URLs from the environment

`OpenQuantumService()` does not read the playbook URL variables. Use `from_env()` when you want `OPENQUANTUM_SCHEDULER_URL`, `OPENQUANTUM_MANAGEMENT_URL`, `OPENQUANTUM_KEYCLOAK_BASE`, and `OPENQUANTUM_KEYCLOAK_REALM`. That call does not autoload a saved account, and it raises `AuthenticationError` when no credential resolves:

[](#__codelineno-5-1)`service`` ``=`` ``OpenQuantumService``.``from_env``()`\

## Run a Simple Circuit

[](#__codelineno-6-1)`from`` ``qiskit.circuit`` ``import`` ``QuantumCircuit`\
[](#__codelineno-6-2)\
[](#__codelineno-6-3)`# Get a backend`\
[](#__codelineno-6-4)`backend`` ``=`` ``service``.``return_backend``(``"rigetti:cepheus-1-108q"``)`\
[](#__codelineno-6-5)\
[](#__codelineno-6-6)`# Build a Bell state circuit`\
[](#__codelineno-6-7)`qc`` ``=`` ``QuantumCircuit``(``2``,`` ``2``)`\
[](#__codelineno-6-8)`qc``.``h``(``0``)`\
[](#__codelineno-6-9)`qc``.``cx``(``0``,`` ``1``)`\
[](#__codelineno-6-10)`qc``.``measure``([``0``,`` ``1``],`` ``[``0``,`` ``1``])`\
[](#__codelineno-6-11)\
[](#__codelineno-6-12)`# Run on Open Quantum`\
[](#__codelineno-6-13)`job`` ``=`` ``backend``.``run``(``qc``,`` ``shots``=``128``)`\
[](#__codelineno-6-14)`result`` ``=`` ``job``.``result``()`\
[](#__codelineno-6-15)`counts`` ``=`` ``result``.``get_counts``()`\
[](#__codelineno-6-16)`print``(``counts``)`\

Expected output:

[](#__codelineno-7-1)`{``'00'``:`` ``512``,`` ``'11'``:`` ``512``}`\

Note

Counts use bitstring keys, zero-padded to the circuit's classical register width and ordered most-significant-bit first (matching Qiskit's convention).

## Get Results

The `backend.run()` method returns an immediate result job. Call `.result()` to access the Qiskit `Result` object:

[](#__codelineno-8-1)`job`` ``=`` ``backend``.``run``(``qc``,`` ``shots``=``128``)`\
[](#__codelineno-8-2)`result`` ``=`` ``job``.``result``()`\
[](#__codelineno-8-3)\
[](#__codelineno-8-4)`# Get counts`\
[](#__codelineno-8-5)`counts`` ``=`` ``result``.``get_counts``()`\
[](#__codelineno-8-6)\
[](#__codelineno-8-7)`# Get memory (individual shot results)`\
[](#__codelineno-8-8)`memory`` ``=`` ``result``.``get_memory``()`\

## Clean Up

Close the service when done to release HTTP connections:

[](#__codelineno-9-1)`service``.``close``()`\

Or use the context manager:

[](#__codelineno-10-1)`with`` ``OpenQuantumService``(``creds``=``creds``)`` ``as`` ``service``:`\
[](#__codelineno-10-2)`    ``backend`` ``=`` ``service``.``return_backend``(``"rigetti:cepheus-1-108q"``)`\
[](#__codelineno-10-3)`    ``job`` ``=`` ``backend``.``run``(``qc``,`` ``shots``=``128``)`\
[](#__codelineno-10-4)`    ``result`` ``=`` ``job``.``result``()`\

## Next Steps

- [Backends & Targets](https://docs.openquantum.com/qiskit-plugin/backends-targets/) -- Backend capabilities and filtering.
- [Sampler & Estimator](https://docs.openquantum.com/qiskit-plugin/sampler-estimator/) -- Use SamplerV2 and EstimatorV2.
- [Examples](https://docs.openquantum.com/qiskit-plugin/examples/) -- More Qiskit workflows.
