# Mixed-PUB Runtime compatibility audit

The `migrate-qiskit-ibm-runtime` skill was applied to `probe.py`. The retained
source already targets Runtime 0.50.0 through
`qiskit_ibm_runtime.executor_sampler.Sampler`; the installed workload uses
Qiskit 2.5.2, Aer 0.17.2, and Runtime 0.50.0. The registry's minimum version for
client-side primitives is 0.50.0. `registry_detection.json` records every
registry change's primary, secondary, and already-migrated matches against the
final source, along with skill, registry, source, and installed-source hashes.

The primitives-domain `v1-to-v2` and `server-to-client` entries take the skill's
already-migrated exit. The `import Sampler` secondary match names the explicit
client module. The execution-domain `.run(` and `mode=backend` matches refer to
`sampler.run(...)` and the local Aer backend; the probe contains neither
`backend.run(...)` nor a Session/Batch context. Cloud-simulator retirement
already resolves to local `AerSimulator`. The installed source-version window
for NoiseLearner post-selection has no corresponding usage in this probe.
The remaining registry entries produce empty executable migration queues.

The audit preserves the primitive import and all runtime option values. The
only automatic code repair replaces assertion-only result validation with an
explicit `RuntimeError`, then tests malformed counts, PUB order, and cardinality
under normal and optimized Python. The repair follows the requested evidence
validation boundary; it requires no Runtime API migration or result-changing
decision. Published migration guides were not fetched because the applicable
primitive entries already match their destination and the audit changes zero
Runtime API paths.

Installed Runtime source grounds the exercised surfaces:

- `executor_sampler/__init__.py` exports `Sampler` and its `SamplerV2` alias.
  `executor_estimator/__init__.py` likewise exports both Estimator spellings;
  the import-only regression confirms those aliases without constructing an
  Estimator.
- `executor_sampler/prepare.py` validates each PUB, rejects DD with control
  flow, and builds one `CircuitItem` per PUB when both twirling options are
  false. `executor_sampler/utils.py` requires uniform shot counts.
- `options_models/twirling.py` declares the gate and measurement enable paths;
  `options_models/dynamical_decoupling.py` declares `enable`; and
  `options_models/simulator.py` declares `seed_simulator`. The probe sets false,
  false, false, and 7 respectively, then exercises those paths locally.
- `base_primitive.py` routes an Aer `BackendV2` to `QiskitRuntimeLocalService`.
  `executor/executor.py` uses that local branch. The local executor iterates
  program items through Aer, so one local job establishes neither one hardware
  subjob nor one billed overhead.

The skill's general verification recipe calls `ConvertISAToClifford`. Its
installed instruction vocabulary rejects `if_else` and reset, which are the
dynamic mechanisms this probe must retain. The probe already contains only
Pauli-X gates, computational-basis measurements, conditional X, and reset; it
has zero rotation or parameter expressions to round. The audit therefore keeps
those circuits intact and requires successful CPU stabilizer execution. The
whole-circuit conversion-pass check remains inapplicable to that dynamic input.

Normal and optimized executions each process two 64-shot PUBs, return the same
ordered distributions, and exit zero with warnings treated as errors. Four
regression tests pass in both interpreter modes. Ruff checks and formatting use
the repository configuration; mypy checks both files. Byte compilation targets
temporary storage so the retained directory contains source and evidence only.

The audit establishes installed-client preparation, local execution, option
access, and result decoding. Hardware acceptance, scheduling, calibration
continuity, subjob partitioning, and charged time require separate hardware
evidence. The audit constructs zero live services and performs zero QPU calls.
