> Full piece: [https://docs.openquantum.com/cirq-plugin/troubleshooting/](https://docs.openquantum.com/cirq-plugin/troubleshooting/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 aaf5ad0fd56e563b647302b302299a6d1c5dacea600a34433ec39c597f5a6dfc.

# Troubleshooting

## Authentication required

```
AuthenticationError: Authentication required. Provide a token or
client_id+client_secret (or OPENQUANTUM_TOKEN / OPENQUANTUM_CLIENT_ID +
OPENQUANTUM_CLIENT_SECRET / OPENQUANTUM_SDK_KEY).
```

No credentials were found. `OpenQuantumSampler` calls `OpenQuantumClient.from_env()`. Set `OPENQUANTUM_CLIENT_ID` and `OPENQUANTUM_CLIENT_SECRET`, set `OPENQUANTUM_TOKEN` or `OPENQUANTUM_SDK_KEY`, or pass `token=`, `client_id=` + `client_secret=`, or a pre-built `client=`. See [Authentication](https://docs.openquantum.com/core-sdk/authentication/).

## `Circuit has no measurement gates`

```
CircuitValidationError: Circuit has no measurement gates; add cirq.measure(...)
before sampling on the Open Quantum platform.
```

The platform is shot-based and Cirq's QASM exporter does not add measurements. Append a measurement to your circuit:

``` python
circuit.append(cirq.measure(*cirq.LineQubit.range(2), key="m"))
```

## `configuration_data validation failed: ... required property 'engine'`

The target backend requires extra configuration that was not supplied. The Quantum Rings simulator, for example, requires an `engine`:

``` python
sampler = OpenQuantumSampler(
    backend="qr:gpu-gb10",
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

## Results look bit-reversed

The platform returns counts little-endian (first classical bit rightmost), while Cirq is big-endian. The sampler reverses bitstrings by default (`reverse_bits=True`) so the mapping is correct. If a particular backend returns counts big-endian and your results look reversed, construct the sampler with `reverse_bits=False`. Confirm with an asymmetric state: apply `X` to one qubit and check which bit flips.

## `to_qasm` raised on an unsupported gate

Cirq could not express an operation in OpenQASM. Decompose it before sampling:

``` python
circuit = cirq.Circuit(cirq.decompose(circuit))
```

## Shots are required

Open Quantum is shot-based; analytic execution is not supported. Pass `repetitions=` to `run` / `sample` / `run_sweep`. For local state-vector simulation use `cirq.Simulator` instead.

## Backend is offline or not accepting jobs

Pick another backend. List what is online with the [Core SDK](https://docs.openquantum.com/core-sdk/backend-discovery/) (`client.backends(online=True)`) or the [Open Quantum Portal](https://www.openquantum.com).

## Organization could not be resolved

If your account belongs to more than one organization, pass an explicit `organization_id` to the sampler (discover it via `client.organizations()`).
