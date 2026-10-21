# Numerical environment validation

`requirements.txt` pins NumPy 2.5.4 to match the tested workstation runtime.
The reconciliation preserves the Qiskit and IBM Runtime versions and the
experiment approval boundary. Dependency-version matching requires a fresh
approval record when a saved run names NumPy 2.5.3.

The numerical baseline uses Python 3.14.7 and these installed versions:

| Dependency | Version |
|---|---|
| NumPy | 2.5.4 |
| Qiskit | 2.5.2 |
| Qiskit Aer | 0.17.2 |
| Qiskit IBM Runtime | 0.50.0 |
| rustworkx | 0.18.1 |
| SciPy | 1.18.1 |
| SymPy | 1.14.0 |

Run the repository's [complete gates](../../ci/AGENTS.md#layout-and-gates) with
`PYTHONDONTWRITEBYTECODE=1`, `PYTHONWARNINGS=error`, and
`GOROROBA_WORKERS=2`. The complete gate list passes on baseline source commit
`fbf683d1141b1b2efd8b32f4a06cba6cb5881b22` under NumPy 2.5.4.
The gates cover exact algebraic certificates,
statevector/operator checks, Aer sampling, numerical inference, and the
credential-free Runtime contract suite. A source snapshot needs Git metadata:
`compile_evidence.py` records the source commit and checks its tracked diff.

The local client-side primitive smoke check exercises `configure_sampler`
against `FakeManilaV2` with the backend simulator seed and transpiler seed
20261011. A two-qubit Bell circuit returns 2048 shots with gate twirling,
measurement twirling, and XX dynamical decoupling. A two-qubit circuit with
measurement and conditional X returns 256 shots; the dynamic policy disables
both twirling flags and dynamical decoupling. Warnings raise exceptions.
These tests check option paths and local execution, and consume zero QPU jobs.

The verification transforms ISA gate instructions through
`ConvertISAToClifford`. Runtime 0.50.0 rejects an `if_else` instruction in that
pass, so the verification recursively transforms its blocks and preserves the
control-flow operation. Production experiment circuits retain their original
angles and control flow.

The migration registry scan identifies the existing
`qiskit_ibm_runtime.executor_sampler.Sampler` imports as migrated. The
client-side Estimator import also resolves. The scan finds zero deprecated
primary-trigger usages in the Python modules. Broad secondary matches denote
transpiler options, simulator calls, backend properties, and ordinary Python
collections; they require no API migration.

## Execution-time units

The [client-side ExecutionOptions reference](https://quantum.cloud.ibm.com/docs/api/qiskit-ibm-runtime/options-models-execution-options)
defines `execution.rep_delay` as the delay between a measurement and the next
quantum circuit. The value must fall within the backend's `rep_delay_range`
and requires `dynamic_reprate_enabled=True`.

Read `backend.configuration().default_rep_delay` as seconds. Runtime 0.50.0
[converts the configuration wire value from microseconds](https://github.com/Qiskit/qiskit-ibm-runtime/blob/stable/0.50/qiskit_ibm_runtime/models/backend_configuration.py#L313-L317)
and [converts it back in `to_dict()`](https://github.com/Qiskit/qiskit-ibm-runtime/blob/stable/0.50/qiskit_ibm_runtime/models/backend_configuration.py#L422-L425).
The observed FakeFez and FakeManila attributes equal 0.00025 seconds; their
serialized configuration dictionaries contain 250.0 microseconds. Assigning
the attribute to `sampler.options.execution.rep_delay` succeeds locally.

Use the top-level `sampler.options.max_execution_time`. The
[SamplerOptions reference](https://quantum.cloud.ibm.com/docs/api/qiskit-ibm-runtime/options-models-sampler-options)
calls the bound system execution time. The [service timeout guide](https://quantum.cloud.ibm.com/docs/guides/max-execution-time)
specifies QPU usage in seconds and the lesser of the user ceiling and the
three-hour service limit. Batch or session time-to-live has different
semantics: running jobs can continue after the enclosing lifetime expires.
Per-job ceilings therefore remain necessary for the aggregate budget ledger.
