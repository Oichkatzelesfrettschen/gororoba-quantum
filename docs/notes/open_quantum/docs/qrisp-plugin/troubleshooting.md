> Full piece: [https://docs.openquantum.com/qrisp-plugin/troubleshooting/](https://docs.openquantum.com/qrisp-plugin/troubleshooting/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7b7f584877ea69fdac143e2a33d852fde1e545cb615a1177132828fac1af6333.

# Troubleshooting

## Authentication required

```
AuthenticationError: Authentication required. Provide a token or
client_id+client_secret (or OPENQUANTUM_TOKEN / OPENQUANTUM_CLIENT_ID +
OPENQUANTUM_CLIENT_SECRET / OPENQUANTUM_SDK_KEY).
```

No credentials were found. `OpenQuantumBackend` calls `OpenQuantumService.from_env()`. Set `OPENQUANTUM_CLIENT_ID` and `OPENQUANTUM_CLIENT_SECRET`, set `OPENQUANTUM_TOKEN` or `OPENQUANTUM_SDK_KEY`, or pass `token=`, `client_id=` + `client_secret=`, or a pre-built `service=`. See [Authentication](https://docs.openquantum.com/core-sdk/authentication/).

## `configuration_data validation failed: ... required property 'engine'`

The target backend requires extra configuration that was not supplied. The Quantum Rings simulator, for example, requires an `engine`:

``` python
oq = OpenQuantumBackend(
    backend="qr:gpu-gb10",
    shots=1024,
    configuration_data={"engine": "amber_quantum_rings"},
)
```

## `configuration_data validation failed: ... must match "else" schema`

A backend's configuration schema can be conditional. The Quantum Rings simulator only permits `threshold` when `performance="CUSTOM"`. Send such fields only when they apply:

``` python
# Valid: no threshold unless performance is CUSTOM
configuration_data={"engine": "amber_quantum_rings"}

# Valid: threshold allowed because performance is CUSTOM
configuration_data={"engine": "amber_quantum_rings", "performance": "CUSTOM", "threshold": 128}
```

## `QASM precompilation failed: At most one qubit register allowed`

This should not occur: the plugin flattens Qrisp's per-qubit registers onto a single register automatically. If you see it, make sure you are on a current version of `openquantum-sdk[qrisp]` and are submitting through `get_measurement` / `run` (not a hand-built payload).

## Results look bit-reversed

The platform returns bitstrings in Qiskit's little-endian convention (the first classical bit is the rightmost character). Qrisp reconciles bit order during measurement decoding, so the default (`reverse_bits=False`) is correct. If a particular backend instead returns counts big-endian, construct the backend with `reverse_bits=True`. Confirm with an asymmetric state such as `|01>`.

## Shots are required

Open Quantum is shot-based; analytic execution is not supported. Set `shots` on the backend or pass `shots=` to `get_measurement` / `run`.

## Backend is offline or not accepting jobs

Pick another backend. List what is online with the [Core SDK](https://docs.openquantum.com/core-sdk/backend-discovery/) (`client.backends(online=True)`), the [Qiskit plugin](https://docs.openquantum.com/qiskit-plugin/backends-targets/), or the [Open Quantum Portal](https://www.openquantum.com).

## Organization could not be resolved

If your account belongs to more than one organization, pass an explicit `organization_id` to the backend (discover it via `client.organizations()`).
