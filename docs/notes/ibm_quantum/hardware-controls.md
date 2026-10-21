# IBM Quantum hardware controls: audit and configuration per workload

This note audits every control the repository reaches on IBM Quantum hardware
through qiskit-ibm-runtime 0.50.0 and IBM's REST API, and states the
configuration each workload type should use. Every row names its authority.

Tags: [P] an IBM documentation statement (a transcribed guide in this
directory, or a page the repository records by SHA-256); [M] a measured value
from a live read or a retained record; [S] the installed package source or an
offline probe of it; [I] a repository inference from tagged facts. A claim no
source supports reads **unverified**.

**Verified on.**

| Read | Time (UTC) | Calls | Retained in |
| --- | --- | --- | --- |
| Live read A, exploratory | 2026-10-17T21:33:40Z to 21:33:45Z | `QiskitRuntimeService()`, `service.backends()`, `ibm_kingston` `configuration()` and `status()`, `service.usage()` | superseded by read B; values agree |
| Live read B | 2026-10-17T21:46:09Z to 21:46:19Z | `service.backends()` (plain, `dynamic_circuits=True`, `use_fractional_gates=True`), `service.usage()`, and per backend `configuration()`, `status()`, `properties()`, `target`, fractional `target`; each call stamped | [backends.json](../../evidence/ibm_runtime_options/backends.json) |
| Calibration at read B | ibm_fez 2026-10-17T14:32:07-07:00, ibm_kingston 13:50:45-07:00, ibm_marrakesh 14:18:18-07:00 | `properties().last_update_date` | backends.json |
| Installed source and offline probes | 2026-10-17 | qiskit-ibm-runtime 0.50.0, qiskit 2.6.0, samplomatic 0.21.0, qiskit-mitigation 0.1.1, pydantic 2.14.1, ibm-quantum-schemas 0.13.20261016, Python 3.14.7 | [inventory.json](../../evidence/ibm_runtime_options/inventory.json) |
| Target snapshot | 2026-10-14T21:00:38Z | `scripts/heron_target_snapshot.py --out` | [targets.json](../../evidence/heron_platform/targets.json) |

`scripts/ibm_runtime_options_inventory.py` writes both evidence files: `--out`
introspects the installed package offline, `--backends` makes read B, and
`--check` (gate core-533) regenerates the inventory, holds the five generated
blocks below to `--render`, and validates the schema of backends.json. The
inventory binds the installed probe dependencies exactly. Read B retains its
original producer versions; its schema accepts stable Qiskit releases in Runtime
0.50's declared range `>=2.3.0,<3` and requires Runtime 0.50.0. Read B
submitted nothing and records the instance only as the 12-hex sha256 of its
CRN; `instance_id` and `plan_id` of `usage()` are dropped.

## 1. Authority order

1. The live Target and configuration of the backend that runs the job (section 4).
2. The installed client source and offline probes (sections 2 and 3).
3. IBM's guides as transcribed in this directory and recorded in
   [ibm_heron_platform.md](../ibm_heron_platform.md),
   [ibm-runtime-execution-guides.md](../ibm-runtime-execution-guides.md) and
   [ibm_fractional_execution_sources.md](../papers/ibm_fractional_execution_sources.md).
4. Repository records: [N21_USAGE_BUDGET.md](../../../gororoba_quantum/N21_USAGE_BUDGET.md),
   [QPU_OPTIMIZATION.md](../../../gororoba_quantum/QPU_OPTIMIZATION.md) and the
   retained runs under `results/live/`.

Where two disagree, the higher one holds and the disagreement is listed in
section 10.

## 2. Access surfaces

### 2.1 Python client

| Surface | Installed object | Status in 0.50.0 | Source |
| --- | --- | --- | --- |
| Service | `QiskitRuntimeService` | saved account in the qiskit account store; `backends()`, `backend()`, `usage()`, `least_busy()` read only | [S] signatures in 2.3 |
| Client-side Sampler | `qiskit_ibm_runtime.executor_sampler.Sampler` | builds a `QuantumProgram` locally (`prepare`), boxes and twirls through samplomatic, applies DD locally with `PadDynamicalDecoupling` on the backend Target, and submits through `Executor` | [S] `executor_sampler/prepare.py`, `executor/dynamical_decoupling.py` |
| Client-side Estimator | `qiskit_ibm_runtime.executor_estimator.Estimator` | resilience through qiskit-mitigation tasks (TREX, gate folding, PEA, PEC) on the client | [S] `executor_estimator/prepare.py` |
| Server-side primitives | `SamplerV2`, `EstimatorV2` | deprecated in 0.50.0 | [S] deprecation sites in 3.2 |
| Executor | `qiskit_ibm_runtime.Executor` | runs a `QuantumProgram`; the client-side primitives map their options onto `ExecutorOptions` (`sampler_option_to_executor_options` drops `meas_type`, which travels as the program's `meas_level`) | [S] `options_models/converters.py` |
| Noise learning | `NoiseLearnerV3` | produces the `layer_noise_model` that client-side PEC and PEA require | [S] probe "PEC without layer_noise_model" |
| Execution modes | `Session(backend, max_time, create_new)`, `Batch(...)`; a primitive given a backend runs in job mode | REST `POST /sessions` with `mode` and `max_ttl` | [S] |
| Dry run | `Sampler.run(..., dry_run=True)` | the service validates the job and returns randomized mock data; it is a service request, so this audit ran none | [S] `executor_sampler/sampler.py` docstring |

Hardware calls in the repository go through `QiskitRuntimeService` and the
client-side Sampler (live_run.py); the other runtime imports are fake
backends for offline contracts, result containers, and `MidCircuitMeasure`
in the syndrome readout of `heron_multiprogramming.py` [S].

### 2.2 Execution modes and their billing

| Mode | What it holds | Billing | Calibration | Source |
| --- | --- | --- | --- | --- |
| Job | one primitive call | QPU lock time of the job; a system error bills zero, a user error or cancel bills consumption including preparation | calibration jobs can run before or after | [P] estimate-job-run-time.md "Workload usage", "Usage for failed and canceled jobs" |
| Batch | independent jobs grouped for scheduling | cumulative lock time of its jobs; same failure rule as jobs | calibration can run between batched jobs; order not guaranteed | [P] same; execution-modes row in ibm-runtime-execution-guides.md |
| Session | reserved QPU window | wall-clock time while active, idle time and failed jobs included | calibration excluded during the window, so drift accumulates | [P] same; calibration-jobs.md "How calibrations are scheduled" |

Whether this account's plan admits session mode is **unverified**: no
repository source states it, and testing it would create a session.

### 2.3 REST API

The client resolves the API at `https://quantum.cloud.ibm.com/api/v1` for
us-east and `https://<region>.quantum.cloud.ibm.com/api/v1` elsewhere
(`qiskit_ibm_runtime/api/utils.py`) [S]. The table lists every endpoint the
installed REST adaptors call; the guides add `GET /sessions/{id}` and
`GET /jobs/{id}` as the usage sources (estimate-job-run-time.md "Query a
workload's actual usage") [P]. `max_execution_time` travels as the payload key
`cost`, `Session(max_time)` as `max_ttl`, and both `service.backend()` and the
run payload accept a `calibration_id`.

<!-- ibm-runtime-options:rest:begin -->
Generated by `scripts/ibm_runtime_options_inventory.py --render` from the installed REST adaptors; every request carries `IBM-API-Version: 2026-04-15`.

| Adaptor | Path prefix | Method | Verb | Path suffix | Argument -> payload or query key |
| --- | --- | --- | --- | --- | --- |
| `api.rest.runtime.Runtime` | `""` | `program_run` | POST | `/jobs` | backend_name -> backend, calibration_id -> calibration_id, image -> runtime, job_tags -> tags, log_level -> log_level, max_execution_time -> cost, session_id -> session_id, session_time -> session_time, start_session -> start_session |
| `api.rest.runtime.Runtime` | `""` | `jobs_get` | GET | `/jobs` | backend_name -> backend, job_tags -> tags, limit -> limit, program_id -> program, session_id -> session_id, skip -> offset |
| `api.rest.runtime.Runtime` | `""` | `backends` | GET | `/backends` |  |
| `api.rest.runtime.Runtime` | `""` | `cloud_usage` | GET | `/instances/usage` |  |
| `api.rest.runtime.Runtime` | `""` | `workloads_get` | GET | `/workloads` |  |
| `api.rest.cloud_backend.CloudBackend` | `f'{url_prefix}/backends/{backend_name}'` | `configuration` | GET | `/configuration` | calibration_id -> calibration_id |
| `api.rest.cloud_backend.CloudBackend` | `f'{url_prefix}/backends/{backend_name}'` | `properties` | GET | `/properties` | calibration_id -> calibration_id |
| `api.rest.cloud_backend.CloudBackend` | `f'{url_prefix}/backends/{backend_name}'` | `status` | GET | `/status` |  |
| `api.rest.program_job.ProgramJob` | `f'{url_prefix}/jobs/{job_id}'` | `get` | GET | (prefix) |  |
| `api.rest.program_job.ProgramJob` | `f'{url_prefix}/jobs/{job_id}'` | `delete` | DELETE | (prefix) |  |
| `api.rest.program_job.ProgramJob` | `f'{url_prefix}/jobs/{job_id}'` | `results` | GET | `/results` |  |
| `api.rest.program_job.ProgramJob` | `f'{url_prefix}/jobs/{job_id}'` | `cancel` | POST | `/cancel` |  |
| `api.rest.program_job.ProgramJob` | `f'{url_prefix}/jobs/{job_id}'` | `logs` | GET | `/logs` |  |
| `api.rest.program_job.ProgramJob` | `f'{url_prefix}/jobs/{job_id}'` | `metadata` | GET | `/metrics` |  |
| `api.rest.program_job.ProgramJob` | `f'{url_prefix}/jobs/{job_id}'` | `update_tags` | PUT | `/tags` |  |
| `api.rest.runtime_session.RuntimeSession` | `f'{url_prefix}/sessions'` or `f'{url_prefix}/sessions/{session_id}'` | `create` | POST | (prefix) | backend -> backend, instance -> instance, max_time -> max_ttl, mode -> mode |
| `api.rest.runtime_session.RuntimeSession` | `f'{url_prefix}/sessions'` or `f'{url_prefix}/sessions/{session_id}'` | `cancel` | DELETE | `/close` |  |
| `api.rest.runtime_session.RuntimeSession` | `f'{url_prefix}/sessions'` or `f'{url_prefix}/sessions/{session_id}'` | `close` | PATCH | (prefix) |  |
| `api.rest.runtime_session.RuntimeSession` | `f'{url_prefix}/sessions'` or `f'{url_prefix}/sessions/{session_id}'` | `details` | GET | (prefix) |  |

**Entry points** (installed signatures).

| Name | Signature |
| --- | --- |
| `Session` | `(self, backend: 'BackendV2', max_time: 'int \| str \| None' = None, *, create_new: 'bool \| None' = True)` |
| `Batch` | `(self, backend: 'BackendV2', max_time: 'int \| str \| None' = None, *, create_new: 'bool \| None' = True)` |
| `QiskitRuntimeService` | `(self, channel: 'ChannelType \| None' = None, token: 'str \| None' = None, url: 'str \| None' = None, filename: 'str \| None' = None, name: 'str \| None' = None, instance: 'str \| None' = None, proxies: 'dict \| None' = None, verify: 'bool \| None' = None, private_endpoint: 'bool \| None' = None, url_resolver: 'Callable[[str, str, bool \| None, str], str] \| None' = None, region: 'str \| None' = None, plans_preference: 'list[str] \| None' = None, tags: 'list[str] \| None' = None) -> 'None'` |
| `QiskitRuntimeService.backends` | `(self, name: 'str \| None' = None, min_num_qubits: 'int \| None' = None, instance: 'str \| None' = None, dynamic_circuits: 'bool \| None' = None, filters: 'Callable[[IBMBackend], bool] \| None' = None, *, use_fractional_gates: 'bool \| None' = False, calibration_id: 'str \| None' = None, **kwargs: 'Any') -> 'list[IBMBackend]'` |
| `QiskitRuntimeService.backend` | `(self, name: 'str', instance: 'str \| None' = None, use_fractional_gates: 'bool \| None' = False, calibration_id: 'str \| None' = None) -> 'Backend'` |
| `QiskitRuntimeService.usage` | `(self) -> 'dict[str, Any]'` |
| `QiskitRuntimeService.least_busy` | `(self, min_num_qubits: 'int \| None' = None, instance: 'str \| None' = None, filters: 'Callable[[IBMBackend], bool] \| None' = None, use_fractional_gates: 'bool \| None' = False, **kwargs: 'Any') -> 'IBMBackend'` |
| `executor_sampler.Sampler.run` | `(self, pubs: 'Iterable[SamplerPubLike]', *, shots: 'int \| None' = None, dry_run: 'bool' = False) -> 'RuntimeJobV2 \| LocalRuntimeJob'` |
| `executor_estimator.Estimator.run` | `(self, pubs: 'Iterable[EstimatorPubLike]', *, precision: 'float \| None' = None, dry_run: 'bool' = False) -> 'RuntimeJobV2 \| LocalRuntimeJob'` |
<!-- ibm-runtime-options:rest:end -->

### 2.4 MCP

No IBM Quantum MCP server is registered for this repository. The Claude Code
user scope (`~/.claude.json`) registers kaggle, openquantum, quandela and
quantum-inspire among the hardware and compute servers, and no project-scope
server for this checkout; `~/.codex/config.toml` registers quantum_inspire,
openquantum and quandela (read 2026-10-17). This audit therefore covers the
Python client and its REST layer.

## 3. Primitive options

### 3.1 Option inventory

Two option families exist in 0.50.0. `qiskit_ibm_runtime.options_models`
(pydantic models, concrete defaults) serves the client-side primitives that
live_run.py uses. `qiskit_ibm_runtime.options` (primitive dataclasses whose
defaults are `Unset` and whose effective defaults live in the docstrings)
serves the deprecated `SamplerV2` and `EstimatorV2`. `layer_noise_learning`
exists only in the server family; the client family takes a
`layer_noise_model` instead.

<!-- ibm-runtime-options:options:begin -->
Generated by `scripts/ibm_runtime_options_inventory.py --render` from the installed qiskit-ibm-runtime 0.50.0; `--check` (gate core-533) holds this block to the package.

**Option roots.** Leaf fields count every nested path.

| Root | Options class | Accepted by | Leaf fields |
| --- | --- | --- | --- |
| client Sampler | `options_models.sampler.SamplerOptions` | `executor_sampler.Sampler` | 28 |
| client Estimator | `options_models.estimator.EstimatorOptions` | `executor_estimator.Estimator` | 40 |
| Executor | `options_models.executor.ExecutorOptions` | `Executor` | 15 |
| NoiseLearnerV3 | `options_models.noise_learner_v3.NoiseLearnerV3Options` | `NoiseLearnerV3` | 23 |
| Calibrator | `options_models.calibrator.CalibratorOptions` | `calibrator.Calibrator` | 6 |
| server SamplerV2 | `options.sampler_options.SamplerOptions` | `SamplerV2` | 23 |
| server EstimatorV2 | `options.estimator_options.EstimatorOptions` | `EstimatorV2` | 41 |

**Leaf option paths by root** (x: the root accepts the path).

| Path | client Sampler | client Estimator | Executor | NoiseLearnerV3 | Calibrator | server SamplerV2 | server EstimatorV2 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `bit_flip_checks.post_circuit.enable` |  |  |  | x |  |  |  |
| `bit_flip_checks.post_circuit.strategy` |  |  |  | x |  |  |  |
| `bit_flip_checks.post_circuit.x_pulse_type` |  |  |  | x |  |  |  |
| `bit_flip_checks.pre_circuit.enable` |  |  |  | x |  |  |  |
| `bit_flip_checks.pre_circuit.strategy` |  |  |  | x |  |  |  |
| `bit_flip_checks.pre_circuit.x_pulse_type` |  |  |  | x |  |  |  |
| `default_precision` |  | x |  |  |  |  | x |
| `default_shots` | x | x |  |  |  | x | x |
| `dynamical_decoupling.enable` | x | x |  |  |  | x | x |
| `dynamical_decoupling.extra_slack_distribution` | x | x |  |  |  | x | x |
| `dynamical_decoupling.scheduling_method` | x | x |  |  |  | x | x |
| `dynamical_decoupling.sequence_type` | x | x |  |  |  | x | x |
| `dynamical_decoupling.skip_reset_qubits` | x | x |  |  |  | x | x |
| `environment.image` | x | x | x | x | x |  |  |
| `environment.job_tags` | x | x | x | x | x | x | x |
| `environment.log_level` | x | x | x | x | x | x | x |
| `environment.max_execution_time` | x | x | x | x | x |  |  |
| `environment.private` | x | x | x | x | x | x | x |
| `execution.init_qubits` | x | x | x | x |  | x | x |
| `execution.meas_type` | x |  |  |  |  | x |  |
| `execution.rep_delay` | x | x | x | x |  | x | x |
| `execution.scheduler_timing` | x | x | x | x |  |  |  |
| `execution.stretch_values` | x | x | x | x |  |  |  |
| `experimental` | x | x | x | x | x | x | x |
| `layer_pair_depths` |  |  |  | x |  |  |  |
| `max_execution_time` | x | x | x | x |  | x | x |
| `num_randomizations` |  |  |  | x |  |  |  |
| `post_selection.enable` |  |  |  | x |  |  |  |
| `post_selection.strategy` |  |  |  | x |  |  |  |
| `post_selection.x_pulse_type` |  |  |  | x |  |  |  |
| `resilience.layer_noise_learning.layer_pair_depths` |  |  |  |  |  |  | x |
| `resilience.layer_noise_learning.max_layers_to_learn` |  |  |  |  |  |  | x |
| `resilience.layer_noise_learning.num_randomizations` |  |  |  |  |  |  | x |
| `resilience.layer_noise_learning.shots_per_randomization` |  |  |  |  |  |  | x |
| `resilience.layer_noise_model` |  | x |  |  |  |  | x |
| `resilience.measure_mitigation` |  | x |  |  |  |  | x |
| `resilience.measure_noise_learning.num_randomizations` |  | x |  |  |  |  | x |
| `resilience.measure_noise_learning.shots_per_randomization` |  |  |  |  |  |  | x |
| `resilience.pec.max_overhead` |  | x |  |  |  |  | x |
| `resilience.pec.noise_gain` |  | x |  |  |  |  | x |
| `resilience.pec_mitigation` |  | x |  |  |  |  | x |
| `resilience.zne.amplifier` |  | x |  |  |  |  | x |
| `resilience.zne.extrapolated_noise_factors` |  | x |  |  |  |  | x |
| `resilience.zne.extrapolator` |  | x |  |  |  |  | x |
| `resilience.zne.noise_factors` |  | x |  |  |  |  | x |
| `resilience.zne_mitigation` |  | x |  |  |  |  | x |
| `resilience_level` |  | x |  |  |  |  | x |
| `seed_estimator` |  |  |  |  |  |  | x |
| `shots_per_randomization` |  |  |  | x |  |  |  |
| `simulator.angle_decimals` | x | x | x |  |  |  |  |
| `simulator.basis_gates` |  |  |  |  |  | x | x |
| `simulator.coupling_map` |  |  |  |  |  | x | x |
| `simulator.layer_noise_model` | x | x | x |  |  |  |  |
| `simulator.noise_model` |  |  |  |  |  | x | x |
| `simulator.seed_simulator` | x | x | x |  |  | x | x |
| `simulator.warn_absent` | x | x | x |  |  |  |  |
| `twirling.enable_gates` | x | x |  |  |  | x | x |
| `twirling.enable_measure` | x | x |  |  |  | x | x |
| `twirling.group` | x | x |  |  |  |  |  |
| `twirling.num_randomizations` | x | x |  |  |  | x | x |
| `twirling.shots_per_randomization` | x | x |  |  |  | x | x |
| `twirling.strategy` | x | x |  |  |  | x | x |

**client `options_models.bit_flip_checks.BitFlipChecksOptions`**: Options to apply bit-flip checks to the results of noise learning circuits.

| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds | Deprecated | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `pre_circuit` | `PreCircuitBitFlipChecksOptions` | `PreCircuitBitFlipChecksOptions()` |  | nested options_models.bit_flip_checks.PreCircuitBitFlipChecksOptions |  | Options to apply pre-circuit bit-flip checks to the results of noise learning circuits. |
| `post_circuit` | `PostCircuitBitFlipChecksOptions` | `PostCircuitBitFlipChecksOptions()` |  | nested options_models.bit_flip_checks.PostCircuitBitFlipChecksOptions |  | Options to apply post-circuit bit-flip checks to the results of noise learning circuits. |

**client `options_models.bit_flip_checks.PostCircuitBitFlipChecksOptions`**: Options to apply post-circuit bit-flip checks to the results of noise learning circuits.

| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds | Deprecated | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `enable` | `bool` | `False` |  |  |  | Whether to apply post-circuit bit-flip checks. |
| `x_pulse_type` | `Literal['xslow', 'rx']` | `'xslow'` |  | "xslow", "rx" |  | The type of the X-pulse used for the post-circuit bit-flip checks. |
| `strategy` | `Literal['node', 'edge']` | `'node'` |  | "node", "edge" |  | The strategy used to decide if a shot should be kept or discarded. |

**client `options_models.bit_flip_checks.PreCircuitBitFlipChecksOptions`**: Options to apply pre-circuit bit-flip checks to the results of noise learning circuits.

| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds | Deprecated | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `enable` | `bool` | `False` |  |  |  | Whether to apply pre-circuit bit-flip checks. |
| `x_pulse_type` | `Literal['xslow', 'rx']` | `'xslow'` |  | "xslow", "rx" |  | The type of the X-pulse used for the pre-circuit bit-flip checks. |
| `strategy` | `Literal['node', 'edge']` | `'node'` |  | "node", "edge" |  | The strategy used to decide if a shot should be kept or discarded. |

**client `options_models.calibrator.CalibratorOptions`**: Options for the Calibrator.

| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds | Deprecated | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `environment` | `EnvironmentOptions` | `EnvironmentOptions()` |  | nested options_models.environment.EnvironmentOptions |  | Options related to the execution environment. |
| `experimental` | `dict` | `{}` |  |  |  | Experimental options that are passed to the executor. |

**client `options_models.dynamical_decoupling.DynamicalDecouplingOptions`**: Options for dynamical decoupling (DD).

| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds | Deprecated | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `enable` | `bool` | `False` |  |  |  | Whether to enable DD as specified by the other options in this class. |
| `sequence_type` | `Literal['XX', 'XpXm', 'XY4']` | `'XX'` |  | "XX", "XpXm", "XY4" |  | Which dynamical decoupling sequence to use. |
| `extra_slack_distribution` | `Literal['middle', 'edges']` | `'middle'` |  | "middle", "edges" |  | Where to put extra timing delays due to rounding issues. |
| `scheduling_method` | `Literal['alap', 'asap']` | `'alap'` |  | "alap", "asap" |  | Whether to schedule gates as soon as ("asap") or as late as ("alap") possible. |
| `skip_reset_qubits` | `bool` | `False` |  |  |  | Whether to insert DD on idle periods that immediately follow initialized/reset qubits. |

**client `options_models.environment.EnvironmentOptions`**: Options related to the execution environment.

| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds | Deprecated | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `log_level` | `LogLevelType` | `'WARNING'` |  | "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL" |  | Logging level to set in the execution environment. |
| `job_tags` | `list[str]` | `[]` |  |  |  | Tags to be assigned to the job. |
| `private` | `bool` | `False` |  |  |  | Boolean that indicates whether the job is marked as private. |
| `max_execution_time` | `Annotated[int \| None, AfterValidator(warn_max_execution_time)]` | `None` |  |  | 0.50.0: Setting `max_execution_time` via `EnvironmentOptions` is deprecated | Maximum execution time in seconds. |
| `image` | `Annotated[str, Field(pattern='[a-zA-Z0-9]+([/.\\-_][a-zA-Z0-9]+)*:[a-zA-Z0-9]+([.\\-_][a-zA-Z0-9]+)*$')] \| None` | `None` |  |  |  | IBM Quantum Compute (formerly Qiskit Runtime) image used for this job. |

**client `options_models.estimator.EstimatorOptions`**: Options for the client-side Estimator.

| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds | Deprecated | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `default_precision` | `Annotated[float, Field(gt=0)]` | `0.015625` |  | gt 0 |  | The default precision to use for any PUB or `run()` call that does not specify one. |
| `default_shots` | `Annotated[int, Field(ge=0)] \| None` | `None` |  | ge 0 |  | The total number of shots to use per circuit per configuration. |
| `execution` | `ExecutionOptions` | `ExecutionOptions()` |  | nested options_models.execution.ExecutionOptions |  | Execution options. |
| `twirling` | `TwirlingOptions` | `TwirlingOptions()` |  | nested options_models.twirling.TwirlingOptions |  | Twirling options. |
| `dynamical_decoupling` | `DynamicalDecouplingOptions` | `DynamicalDecouplingOptions()` |  | nested options_models.dynamical_decoupling.DynamicalDecouplingOptions |  | Dynamical decoupling options. |
| `simulator` | `SimulatorOptions` | `SimulatorOptions()` |  | nested options_models.simulator.SimulatorOptions |  | Options related to local mode simulations. |
| `experimental` | `dict` | `{}` |  |  |  | Experimental options. |
| `environment` | `EnvironmentOptions` | `EnvironmentOptions()` |  | nested options_models.environment.EnvironmentOptions |  | Options related to the execution environment. |
| `resilience` | `ResilienceOptions` | `ResilienceOptions()` |  | nested options_models.resilience.ResilienceOptions |  | Advanced resilience options to fine-tune the resilience strategy. |
| `resilience_level` | `Literal[0, 1, 2]` | `1` |  | 0, 1, 2 |  | How much resilience to build against errors. |
| `max_execution_time` | `int \| None` | `None` |  |  |  | Maximum execution time in seconds. |

**client `options_models.execution.ExecutionOptions`**: Low-level execution options.

| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds | Deprecated | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `init_qubits` | `bool` | `True` |  |  |  | Whether to reset the qubits to the ground state for each shot. |
| `rep_delay` | `float \| None` | `None` | given by `backend.default_rep_delay`. |  |  | The repetition delay. |
| `scheduler_timing` | `bool` | `False` |  |  |  | Whether to return circuit schedule timing of each provided quantum circuit. |
| `stretch_values` | `bool` | `False` |  |  |  | Whether to return numeric resolutions of stretches for each provided quantum circuit. |

**client `options_models.execution.SamplerExecutionOptions`**: Execution options for the sampler primitive.

| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds | Deprecated | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `init_qubits` | `bool` | `True` |  |  |  | Whether to reset the qubits to the ground state for each shot. |
| `rep_delay` | `float \| None` | `None` | given by `backend.default_rep_delay`. |  |  | The repetition delay. |
| `scheduler_timing` | `bool` | `False` |  |  |  | Whether to return circuit schedule timing of each provided quantum circuit. |
| `stretch_values` | `bool` | `False` |  |  |  | Whether to return numeric resolutions of stretches for each provided quantum circuit. |
| `meas_type` | `Literal['classified', 'kerneled', 'avg_kerneled']` | `'classified'` |  | "classified", "kerneled", "avg_kerneled" |  | How to process and return measurement results. |

**client `options_models.executor.ExecutorOptions`**: Options for the executor.

| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds | Deprecated | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `environment` | `EnvironmentOptions` | `EnvironmentOptions()` |  | nested options_models.environment.EnvironmentOptions |  | Options related to the execution environment. |
| `execution` | `ExecutionOptions` | `ExecutionOptions()` |  | nested options_models.execution.ExecutionOptions |  | Low-level execution options. |
| `experimental` | `dict` | `{}` |  |  |  | Experimental options that are passed to the executor. |
| `simulator` | `SimulatorOptions` | `SimulatorOptions()` |  | nested options_models.simulator.SimulatorOptions |  | Options related to local mode simulations. |
| `max_execution_time` | `int \| None` | `None` |  |  |  | Maximum execution time in seconds. |

**client `options_models.measure_noise_learning.MeasureNoiseLearningOptions`**: Options for measurement noise learning.

| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds | Deprecated | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `num_randomizations` | `Annotated[int, Field(ge=1)] \| Literal['auto']` | `'auto'` |  | "auto"; ge 1 |  | The number of random circuits to draw for the measurement learning experiment. |

**client `options_models.noise_learner_v3.NoiseLearnerV3Options`**: Options for :class:`.NoiseLearnerV3`.

| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds | Deprecated | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `shots_per_randomization` | `Annotated[int, Field(ge=1)]` | `128` |  | ge 1 |  | The total number of shots to use per randomized learning circuit. |
| `num_randomizations` | `Annotated[int, Field(ge=1)]` | `32` |  | ge 1 |  | The number of random circuits to use per learning circuit configuration. |
| `layer_pair_depths` | `list[Annotated[int, Field(ge=0)]]` | `[0, 1, 2, 4, 16, 32]` |  | ge 0 |  | The circuit depths (measured in number of pairs) to use in Pauli Lindblad experiments. |
| `bit_flip_checks` | `BitFlipChecksOptions` | `BitFlipChecksOptions()` |  | nested options_models.bit_flip_checks.BitFlipChecksOptions |  | Options to apply bit-flip checks to the results of noise learning circuits. |
| `post_selection` | `PostSelectionOptions` | `PostSelectionOptions()` |  | nested options_models.post_selection.PostSelectionOptions |  | Options for post selecting the results of noise learning circuits. |
| `experimental` | `dict` | `{}` |  |  |  | Experimental options. |
| `execution` | `ExecutionOptions` | `ExecutionOptions()` |  | nested options_models.execution.ExecutionOptions |  | Low-level execution options. |
| `environment` | `EnvironmentOptions` | `EnvironmentOptions()` |  | nested options_models.environment.EnvironmentOptions |  | Options related to the execution environment. |
| `max_execution_time` | `int \| None` | `None` |  |  |  | Maximum execution time in seconds. |

**client `options_models.pec.PecOptions`**: Probabalistic error cancellation mitigation options.

| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds | Deprecated | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `max_overhead` | `Annotated[float, Field(gt=0)] \| None` | `100` |  | gt 0 |  | The maximum circuit sampling overhead allowed, or `None` for no maximum. |
| `noise_gain` | `Annotated[float, Field(ge=0)] \| Literal['auto']` | `'auto'` |  | "auto"; ge 0 |  | The amount by which to scale the noise. |

**client `options_models.post_selection.PostSelectionOptions`**: Options for post selecting results.

| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds | Deprecated | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `enable` | `Annotated[bool, AfterValidator(warn_post_selection)]` | `False` |  |  | 0.49.0: The 'post_selection' field of NoiseLearnerV3 is deprecated | Whether to enable Post Selection when performing learning experiments. |
| `x_pulse_type` | `Literal['xslow', 'rx']` | `'xslow'` |  | "xslow", "rx" |  | The type of the X-pulse used for the post selection measurements. |
| `strategy` | `Literal['node', 'edge']` | `'node'` |  | "node", "edge" |  | The strategy used to decide if a shot should be kept or discarded. |

**client `options_models.resilience.ResilienceOptions`**: Resilience options for V2 Estimator.

| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds | Deprecated | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `measure_mitigation` | `bool \| None` | `None` |  |  |  | Whether to enable measurement error mitigation method. |
| `measure_noise_learning` | `MeasureNoiseLearningOptions` | `MeasureNoiseLearningOptions()` |  | nested options_models.measure_noise_learning.MeasureNoiseLearningOptions |  | Additional measurement noise learning options. |
| `pec_mitigation` | `bool` | `False` |  |  |  | Whether to turn on Probabilistic Error Cancellation error mitigation method. |
| `pec` | `PecOptions` | `PecOptions()` |  | nested options_models.pec.PecOptions |  | Additional probabalistic error cancellation mitigation options. |
| `zne_mitigation` | `bool \| None` | `None` |  |  |  | Whether to turn on Zero-Noise Extrapolation error mitigation method. |
| `zne` | `ZneOptions` | `ZneOptions()` |  | nested options_models.zne.ZneOptions |  | Additional zero noise extrapolation mitigation options. |
| `layer_noise_model` | `list[LayerNoiseModel] \| None` | `None` |  |  |  | Noise model specified by a collection of instructions and the noise that affects them. |

**client `options_models.sampler.SamplerOptions`**: Options for the client-side Sampler.

| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds | Deprecated | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `default_shots` | `int \| None` | `4096` |  |  |  | The default number of shots to use if none are specified in the PUBs or in the run method. |
| `dynamical_decoupling` | `DynamicalDecouplingOptions` | `DynamicalDecouplingOptions()` |  | nested options_models.dynamical_decoupling.DynamicalDecouplingOptions |  | Suboptions for dynamical decoupling. |
| `execution` | `SamplerExecutionOptions` | `SamplerExecutionOptions()` |  | nested options_models.execution.SamplerExecutionOptions |  | Execution options. |
| `twirling` | `TwirlingOptions` | `TwirlingOptions()` |  | nested options_models.twirling.TwirlingOptions |  | Pauli twirling options. |
| `max_execution_time` | `int \| None` | `None` |  |  |  | Maximum execution time in seconds. |
| `simulator` | `SimulatorOptions` | `SimulatorOptions()` |  | nested options_models.simulator.SimulatorOptions |  | Options related to local mode simulations. |
| `experimental` | `dict` | `{}` |  |  |  | Experimental options. |
| `environment` | `EnvironmentOptions` | `EnvironmentOptions()` |  | nested options_models.environment.EnvironmentOptions |  | Options related to the execution environment. |

**client `options_models.simulator.SimulatorOptions`**: Simulator options.

| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds | Deprecated | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `angle_decimals` | `int` | `5` |  |  |  | Gate angle decimal precision. |
| `layer_noise_model` | `list[LayerNoiseModel] \| None` | `None` |  |  |  | Noise model specified by a collection of instructions and the noise that affects them. |
| `seed_simulator` | `int \| None` | `None` |  |  |  | Random seed to control sampling. |
| `warn_absent` | `bool` | `True` |  |  |  | Whether to emit a warning when an entry is missing in :attr:`layer_noise_dict`. |

**client `options_models.twirling.TwirlingOptions`**: Twirling options.

| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds | Deprecated | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `enable_gates` | `bool \| None` | `None` |  |  |  | Whether to apply 2-qubit Clifford gate twirling. |
| `enable_measure` | `bool \| None` | `None` |  |  |  | Whether to enable twirling of measurement instructions. |
| `group` | `Literal['pauli', 'balanced_pauli', 'local_c1', 'local_pauli']` | `'pauli'` |  | "pauli", "balanced_pauli", "local_c1", "local_pauli" |  | The group used to twirl the content of the identified layers. |
| `num_randomizations` | `Annotated[int, Field(ge=1)] \| Literal['auto']` | `'auto'` |  | "auto"; ge 1 |  | The number of random samples to use when twirling or performing sampled mitigation. |
| `shots_per_randomization` | `Annotated[int, Field(ge=1)] \| Literal['auto']` | `'auto'` |  | "auto"; ge 1 |  | The number of shots to run for each random sample. |
| `strategy` | `Literal['active', 'active-accum', 'active-circuit', 'all']` | `'active-accum'` |  | "active", "active-accum", "active-circuit", "all" |  | Specify the strategy of twirling qubits in identified layers of 2-qubit twirled gates. |

**client `options_models.zne.ZneOptions`**: Zero noise extrapolation mitigation options.

| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds | Deprecated | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `amplifier` | `Literal['gate_folding', 'gate_folding_front', 'gate_folding_back', 'pea']` | `'gate_folding'` |  | "gate_folding", "gate_folding_front", "gate_folding_back", "pea" |  | Which technique to use for amplifying noise. |
| `noise_factors` | `Annotated[Sequence[Annotated[float, Field(ge=1)]], AfterValidator(at_least_two_noise_factors)] \| Literal['auto']` | `'auto'` |  | "auto"; ge 1 |  | Noise factors to use for noise amplification. |
| `extrapolator` | `ExtrapolatorType \| Sequence[ExtrapolatorType]` | `('exponential', 'linear')` |  | "linear", "exponential", "double_exponential", "polynomial_degree_1", "polynomial_degree_2", "polynomial_degree_3", "polynomial_degree_4", "polynomial_degree_5", "polynomial_degree_6", "polynomial_degree_7", "fallback" |  | Extrapolator(s) to try (in order) for extrapolating to zero noise. |
| `extrapolated_noise_factors` | `Sequence[Annotated[float, Field(ge=0)]] \| Literal['auto']` | `'auto'` |  | "auto"; ge 0 |  | Noise factors to evaluate the fit extrapolation models at. |

**server `options.dynamical_decoupling_options.DynamicalDecouplingOptions`**: Options for dynamical decoupling (DD).

| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds | Deprecated | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `enable` | `UnsetType \| bool` | `Unset` | `False`. |  |  | Whether to enable DD as specified by the other options in this class. |
| `sequence_type` | `UnsetType \| Literal['XX', 'XpXm', 'XY4']` | `Unset` | `"XX"`. | "XX", "XpXm", "XY4" |  | Which dynamical decoupling sequence to use. |
| `extra_slack_distribution` | `UnsetType \| Literal['middle', 'edges']` | `Unset` | `"middle"`. | "middle", "edges" |  | Where to put extra timing delays due to rounding issues. |
| `scheduling_method` | `UnsetType \| Literal['alap', 'asap']` | `Unset` | `"alap"`. | "alap", "asap" |  | Whether to schedule gates as soon as ("asap") or as late as ("alap") possible. |
| `skip_reset_qubits` | `UnsetType \| bool` | `Unset` | `False`. |  |  | Whether to insert DD on idle periods that immediately follow initialized/reset qubits. |

**server `options.environment_options.EnvironmentOptions`**: Options related to the execution environment.

| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds | Deprecated | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `log_level` | `LogLevelType` | `'WARNING'` | `WARNING`. | "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL" |  | logging level to set in the execution environment. |
| `job_tags` | `list \| None` | `None` | `None`. |  |  | Tags to be assigned to the job. |
| `private` | `bool \| None` | `False` | False. |  |  | Boolean that indicates whether the job is marked as private. |

**server `options.estimator_options.EstimatorOptions`**: Options for V2 Estimator.

| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds | Deprecated | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `max_execution_time` | `UnsetType \| int` | `Unset` |  |  |  | Maximum execution time in seconds, which is based on system execution time (not wall clock time). |
| `environment` | `EnvironmentOptions \| Dict` | `Field(default_factory=EnvironmentOptions)` |  | nested options.environment_options.EnvironmentOptions |  | Options related to the execution environment. |
| `simulator` | `SimulatorOptions \| Dict` | `Field(default_factory=SimulatorOptions)` |  | nested options.simulator_options.SimulatorOptions |  | Simulator options. |
| `default_precision` | `UnsetType \| float` | `Unset` | 0.015625 (1 / sqrt(4096)). | gt 0 |  | The default precision to use for any PUB or `run()` call that does not specify one. |
| `default_shots` | `UnsetType \| int \| None` | `Unset` | `None`. | ge 0 |  | The total number of shots to use per circuit per configuration. |
| `resilience_level` | `UnsetType \| int` | `Unset` | 1. | ge 0, le 2 |  | How much resilience to build against errors. |
| `seed_estimator` | `UnsetType \| int` | `Unset` | `None`. |  |  | Seed used to control sampling. |
| `dynamical_decoupling` | `DynamicalDecouplingOptions \| Dict` | `Field(default_factory=DynamicalDecouplingOptions)` |  | nested options.dynamical_decoupling_options.DynamicalDecouplingOptions |  | Suboptions for dynamical decoupling. |
| `resilience` | `ResilienceOptionsV2 \| Dict` | `Field(default_factory=ResilienceOptionsV2)` |  | nested options.resilience_options.ResilienceOptionsV2 |  | Advanced resilience options to fine-tune the resilience strategy. |
| `execution` | `ExecutionOptionsV2 \| Dict` | `Field(default_factory=ExecutionOptionsV2)` |  | nested options.execution_options.ExecutionOptionsV2 |  | Execution time options. |
| `twirling` | `TwirlingOptions \| Dict` | `Field(default_factory=TwirlingOptions)` |  | nested options.twirling_options.TwirlingOptions |  | Pauli twirling options. |
| `experimental` | `UnsetType \| dict` | `Unset` |  |  |  | Experimental options. |

**server `options.execution_options.ExecutionOptionsV2`**: Execution options for V2 primitives.

| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds | Deprecated | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `init_qubits` | `UnsetType \| bool` | `Unset` | `True`. |  |  | Whether to reset the qubits to the ground state for each shot. |
| `rep_delay` | `UnsetType \| float` | `Unset` | given by `backend.default_rep_delay`. |  |  | The repetition delay. |

**server `options.layer_noise_learning_options.LayerNoiseLearningOptions`**: Options for learning layer noise.

| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds | Deprecated | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `max_layers_to_learn` | `UnsetType \| int \| None` | `Unset` | 4. | ge 0 |  | The max number of unique layers to learn. |
| `shots_per_randomization` | `UnsetType \| int` | `Unset` | 128. | ge 1 |  | The total number of shots to use per random learning circuit. |
| `num_randomizations` | `UnsetType \| int` | `Unset` | 32. | ge 1 |  | The number of random circuits to use per learning circuit configuration. |
| `layer_pair_depths` | `UnsetType \| list[int]` | `Unset` | (0, 1, 2, 4, 16, 32). | validator _nonnegative_list |  | The circuit depths (measured in number of pairs) to use in learning experiments. |

**server `options.measure_noise_learning_options.MeasureNoiseLearningOptions`**: Options for measurement noise learning.

| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds | Deprecated | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `num_randomizations` | `UnsetType \| int` | `Unset` | 32. | ge 1 |  | The number of random circuits to draw for the measurement learning experiment. |
| `shots_per_randomization` | `UnsetType \| int \| Literal['auto']` | `Unset` | "auto". | "auto"; ge 1; validator _warn_shots_per_randomization_int | 0.48.0: Specifying 'measure_noise_learning.shots_per_randomization' as an integer is deprecated | The number of shots to use for the learning experiment per random circuit. |

**server `options.pec_options.PecOptions`**: Probabalistic error cancellation mitigation options.

| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds | Deprecated | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `max_overhead` | `UnsetType \| float \| None` | `Unset` | 100. | gt 0 |  | The maximum circuit sampling overhead allowed, or `None` for no maximum. |
| `noise_gain` | `UnsetType \| float \| Literal['auto']` | `Unset` | "auto". | "auto"; ge 0 |  | The amount by which to scale the noise, where: |

**server `options.resilience_options.ResilienceOptionsV2`**: Resilience options for V2 Estimator.

| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds | Deprecated | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `measure_mitigation` | `UnsetType \| bool` | `Unset` |  |  |  | Whether to enable measurement error mitigation method. |
| `measure_noise_learning` | `MeasureNoiseLearningOptions \| Dict` | `Field(default_factory=MeasureNoiseLearningOptions)` |  | nested options.measure_noise_learning_options.MeasureNoiseLearningOptions |  | Additional measurement noise learning options. |
| `zne_mitigation` | `UnsetType \| bool` | `Unset` |  |  |  | Whether to turn on Zero-Noise Extrapolation error mitigation method. |
| `zne` | `ZneOptions \| Dict` | `Field(default_factory=ZneOptions)` |  | nested options.zne_options.ZneOptions |  | Additional zero-noise extrapolation mitigation options. |
| `pec_mitigation` | `UnsetType \| bool` | `Unset` | False. |  |  | Whether to turn on Probabilistic Error Cancellation error mitigation method. |
| `pec` | `PecOptions \| Dict` | `Field(default_factory=PecOptions)` |  | nested options.pec_options.PecOptions |  | Additional probabalistic error cancellation mitigation options. |
| `layer_noise_learning` | `LayerNoiseLearningOptions \| Dict` | `Field(default_factory=LayerNoiseLearningOptions)` |  | nested options.layer_noise_learning_options.LayerNoiseLearningOptions |  | Layer noise learning options. |
| `layer_noise_model` | `UnsetType \| NoiseLearnerResult \| Sequence[LayerError] \| None` | `Unset` | `None`. |  |  | A :class:`NoiseLearnerResult` or a sequence of :class:`LayerError` objects. |

**server `options.sampler_execution_options.SamplerExecutionOptionsV2`**: Extends :class:`~qiskit_ibm_runtime.options.ExecutionOptionsV2` for the sampler primitive.

| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds | Deprecated | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `init_qubits` | `UnsetType \| bool` | `Unset` | `True`. |  |  | Whether to reset the qubits to the ground state for each shot. |
| `rep_delay` | `UnsetType \| float` | `Unset` | given by `backend.default_rep_delay`. |  |  | The repetition delay. |
| `meas_type` | `UnsetType \| Literal['classified', 'kerneled', 'avg_kerneled']` | `Unset` | "classified". | "classified", "kerneled", "avg_kerneled" |  | How to process and return measurement results. |

**server `options.sampler_options.SamplerOptions`**: Options for V2 Sampler.

| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds | Deprecated | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `max_execution_time` | `UnsetType \| int` | `Unset` |  |  |  | Maximum execution time in seconds, which is based on system execution time (not wall clock time). |
| `environment` | `EnvironmentOptions \| Dict` | `Field(default_factory=EnvironmentOptions)` |  | nested options.environment_options.EnvironmentOptions |  | Options related to the execution environment. |
| `simulator` | `SimulatorOptions \| Dict` | `Field(default_factory=SimulatorOptions)` |  | nested options.simulator_options.SimulatorOptions |  | Simulator options. |
| `default_shots` | `UnsetType \| int` | `Unset` | 4096. |  |  | The default number of shots to use if none are specified in the PUBs or in the run method. |
| `dynamical_decoupling` | `DynamicalDecouplingOptions \| Dict` | `Field(default_factory=DynamicalDecouplingOptions)` |  | nested options.dynamical_decoupling_options.DynamicalDecouplingOptions |  | Suboptions for dynamical decoupling. |
| `execution` | `SamplerExecutionOptionsV2 \| Dict` | `Field(default_factory=SamplerExecutionOptionsV2)` |  | nested options.sampler_execution_options.SamplerExecutionOptionsV2 |  | Execution time options. |
| `twirling` | `TwirlingOptions \| Dict` | `Field(default_factory=TwirlingOptions)` |  | nested options.twirling_options.TwirlingOptions |  | Pauli twirling options. |
| `experimental` | `UnsetType \| dict` | `Unset` |  |  |  | Experimental options. |

**server `options.simulator_options.SimulatorOptions`**: Simulator options.

| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds | Deprecated | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `noise_model` | `UnsetType \| dict \| NoiseModel \| None` | `Unset` | `None`. | validator _validate_noise_model |  | Noise model for the simulator. |
| `seed_simulator` | `UnsetType \| int` | `Unset` | `None`. |  |  | Random seed to control sampling. |
| `coupling_map` | `UnsetType \| list[list[int]] \| CouplingMap` | `Unset` | `None`, which implies no connectivity constraints. |  |  | Directed coupling map to target in mapping. |
| `basis_gates` | `UnsetType \| list[str]` | `Unset` | all basis gates supported by the simulator. |  |  | List of basis gate names to unroll to. |

**server `options.twirling_options.TwirlingOptions`**: Twirling options.

| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds | Deprecated | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `enable_gates` | `UnsetType \| bool` | `Unset` | - For the Sampler: `False`. - For the Estimator: If `enables_gates` is `Unset`, it is determined by the server according to the resilience level: it is `False` for resilience levels 0 and 1, and `True` for resilience level 2. |  |  | Whether to apply 2-qubit Clifford gate twirling. |
| `enable_measure` | `UnsetType \| bool` | `Unset` | - For the Sampler: `False`. - For the Estimator: If `enable_measure` is `Unset`, it is determined by the server according to the resilience level: it is `False` for resilience level 0, and `True` for resilience levels 1 and 2. |  |  | Whether to enable twirling to measurement instructions, as long as the measurement is not involved within a conditional block. |
| `num_randomizations` | `UnsetType \| int \| Literal['auto']` | `Unset` | `"auto"`. | "auto"; ge 1 |  | The number of random samples to use when twirling or peforming sampled mitigation. |
| `shots_per_randomization` | `UnsetType \| int \| Literal['auto']` | `Unset` | `"auto"`. | "auto"; ge 1 |  | The number of shots to run for each random sample. |
| `strategy` | `UnsetType \| TwirlingStrategyType` | `Unset` | `"active-accum"`. | "active", "active-accum", "active-circuit", "all" |  | Specify the strategy of twirling qubits in identified layers of 2-qubit twirled gates. |

**server `options.zne_options.ZneOptions`**: Zero noise extrapolation mitigation options.

| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds | Deprecated | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `amplifier` | `UnsetType \| Literal['gate_folding', 'gate_folding_front', 'gate_folding_back', 'pea']` | `Unset` |  | "gate_folding", "gate_folding_front", "gate_folding_back", "pea" |  | Which technique to use for amplifying noise. |
| `noise_factors` | `UnsetType \| Sequence[float]` | `Unset` | `(1, 3, 5)`. | validator _validate_zne_noise_factors |  | noise_factors: |
| `extrapolator` | `UnsetType \| ExtrapolatorType \| Sequence[ExtrapolatorType]` | `Unset` | `("exponential", "linear")`. | "linear", "exponential", "double_exponential", "polynomial_degree_1", "polynomial_degree_2", "polynomial_degree_3", "polynomial_degree_4", "polynomial_degree_5", "polynomial_degree_6", "polynomial_degree_7", "fallback" |  | Extrapolator(s) to try (in order) for extrapolating to zero noise. |
| `extrapolated_noise_factors` | `UnsetType \| Sequence[float]` | `Unset` |  |  |  | Noise factors to evaluate the fit extrapolation models at. |
<!-- ibm-runtime-options:options:end -->

### 3.2 Resolution rules, deprecations and probes

<!-- ibm-runtime-options:behavior:begin -->
Generated by `scripts/ibm_runtime_options_inventory.py --render`; probes call `prepare()` of the client-side primitives on FakeFez and submit nothing.

**Client-side Sampler, resolved twirling defaults** (`finalize_sampler_options`): `twirling.enable_gates` = false, `twirling.enable_measure` = false.

**Client-side Estimator, resolved defaults by resilience level** (`finalize_estimator_options`).

| resilience_level | `resilience.measure_mitigation` | `resilience.pec_mitigation` | `resilience.zne_mitigation` | `twirling.enable_gates` | `twirling.enable_measure` |
| --- | --- | --- | --- | --- | --- |
| 0 | false | false | false | false | false |
| 1 | true | false | false | false | true |
| 2 | true | false | true | true | true |

**Twirling shot split** (`calculate_twirling_shots` with `shots_per_randomization` "auto").

| PUB shots | num_randomizations | resolved randomizations | shots per randomization | executed shots |
| --- | --- | --- | --- | --- |
| 1024 | "auto" | 16 | 64 | 1024 |
| 1024 | 32 | 32 | 32 | 1024 |
| 4096 | "auto" | 32 | 128 | 4096 |
| 4096 | 32 | 32 | 128 | 4096 |
| 8192 | "auto" | 32 | 256 | 8192 |
| 8192 | 32 | 32 | 256 | 8192 |
| 65536 | "auto" | 32 | 2048 | 65536 |
| 65536 | 32 | 32 | 2048 | 65536 |
| 100000 | "auto" | 32 | 3125 | 100000 |
| 100000 | 32 | 32 | 3125 | 100000 |
| 122880 | "auto" | 32 | 3840 | 122880 |
| 122880 | 32 | 32 | 3840 | 122880 |

**Deprecation sites** (`issue_deprecation_msg` calls).

| Module | Site | Since | Message |
| --- | --- | --- | --- |
| `estimator` | `EstimatorV2.__init__` | 0.50.0 | The EstimatorV2 class is deprecated |
| `estimator` | `EstimatorV2.run` | 0.48.0 | Specifying different 'precision' across pubs is deprecated |
| `options.measure_noise_learning_options` | `MeasureNoiseLearningOptions._warn_shots_per_randomization_int` | 0.48.0 | Specifying 'measure_noise_learning.shots_per_randomization' as an integer is deprecated |
| `options_models.environment` | `warn_max_execution_time` | 0.50.0 | Setting `max_execution_time` via `EnvironmentOptions` is deprecated |
| `options_models.post_selection` | `warn_post_selection` | 0.49.0 | The 'post_selection' field of NoiseLearnerV3 is deprecated |
| `sampler` | `SamplerV2.__init__` | 0.50.0 | The SamplerV2 class is deprecated |
| `sampler` | `SamplerV2.run` | 0.48.0 | Specifying different 'shots' across pubs is deprecated |

**Offline prepare() probes.** A rejection names its exception; the message is kept when qiskit-ibm-runtime raises it.

| Primitive | Case | Options | Accepted | Program shots | Error |
| --- | --- | --- | --- | --- | --- |
| client Sampler | static, defaults | `{}` | yes | 4096 |  |
| client Sampler | if_else, defaults | `{}` | yes | 4096 |  |
| client Sampler | static, DD | `{"dynamical_decoupling": {"enable": true}}` | yes | 4096 |  |
| client Sampler | if_else, DD | `{"dynamical_decoupling": {"enable": true}}` | no |  | IBMInputValueError: 'Dynamical decoupling is not compatible with dynamic circuits (circuits with control flow operations).' |
| client Sampler | mid-circuit measure, DD | `{"dynamical_decoupling": {"enable": true}}` | yes | 4096 |  |
| client Sampler | reset, DD | `{"dynamical_decoupling": {"enable": true}}` | yes | 4096 |  |
| client Sampler | static, gate and measure twirling | `{"twirling": {"enable_gates": true, "enable_measure": true}}` | yes | 128 |  |
| client Sampler | if_else, gate twirling | `{"twirling": {"enable_gates": true}}` | no |  | TranspilerError |
| client Sampler | if_else, measure twirling | `{"twirling": {"enable_measure": true}}` | no |  | TranspilerError |
| client Sampler | mid-circuit measure, gate and measure twirling | `{"twirling": {"enable_gates": true, "enable_measure": true}}` | yes | 128 |  |
| client Sampler | MidCircuitMeasure, gate and measure twirling | `{"twirling": {"enable_gates": true, "enable_measure": true}}` | yes | 128 |  |
| client Sampler | reset, gate and measure twirling | `{"twirling": {"enable_gates": true, "enable_measure": true}}` | no |  | SamplexBuildError |
| client Sampler | measure twice into one bit, gate and measure twirling | `{"twirling": {"enable_gates": true, "enable_measure": true}}` | no |  | SamplexBuildError |
| client Sampler | static, meas_type kerneled | `{"execution": {"meas_type": "kerneled"}}` | yes | 4096 |  |
| client Sampler | static, meas_type kerneled, measure twirling | `{"execution": {"meas_type": "kerneled"}, "twirling": {"enable_measure": true}}` | no |  | IBMInputValueError: "'meas_type=kerneled' and measurement twirling are not compatible. Set `twirling.enable_measure=False` or `execution.meas_type='classified'`" |
| client Sampler | BoxOp, twirling off | `{}` | no |  | IBMInputValueError: "Circuit contains a BoxOp instruction 'box' which is not supported in this minimal implementation. BoxOp support (for twirling) will be added in a future phase." |
| client Sampler | two PUBs, 1000 and 2000 shots | `{}` | no |  | IBMInputValueError: 'All pubs must have the same number of shots. Found: {1000, 2000}' |
| client Sampler | static, 32 randomizations x 64 shots | `{"twirling": {"enable_gates": true, "num_randomizations": 32, "shots_per_randomization": 64}}` | yes | 64 |  |
| client Estimator | level 0 | `{"resilience_level": 0}` | yes |  |  |
| client Estimator | level 1 | `{"resilience_level": 1}` | yes |  |  |
| client Estimator | level 2 | `{"resilience_level": 2}` | yes |  |  |
| client Estimator | PEC without layer_noise_model | `{"resilience": {"pec_mitigation": true}}` | no |  | IBMInputValueError: "PEA/PEC mitigation requires a noise model. Set 'resilience.layer_noise_model' before running." |
| client Estimator | ZNE with PEA without layer_noise_model | `{"resilience": {"zne": {"amplifier": "pea"}, "zne_mitigation": true}}` | no |  | IBMInputValueError: "PEA/PEC mitigation requires a noise model. Set 'resilience.layer_noise_model' before running." |
| client Estimator | ZNE with gate folding | `{"resilience": {"zne_mitigation": true}}` | yes |  |  |
| client Estimator | PEC and ZNE | `{"resilience": {"pec_mitigation": true, "zne_mitigation": true}}` | no |  | IBMInputValueError: 'PEC mitigation and ZNE mitigation are incompatible with one another.' |
| client Estimator | DD | `{"dynamical_decoupling": {"enable": true}}` | yes |  |  |
<!-- ibm-runtime-options:behavior:end -->

### 3.3 Runtime 0.48 to 0.50 release facts

| Release | Change | Effect on this repository | Source |
| --- | --- | --- | --- |
| 0.48 | differing `pub.shots` across the PUBs of one job deprecated on `SamplerV2` | the client-side Sampler already rejects it (probe "two PUBs, 1000 and 2000 shots"), so live_run.py splits jobs by shot tier | [P] release notes row in ibm_heron_platform.md; [S] 3.2 |
| 0.48 | `least_busy(fractional_gates=True)` | none used | [P] fractional-gates.md |
| 0.49 | `MidCircuitReset`, `ConvertToMidCircuitResetAndMeasure`; `post_selection` of NoiseLearnerV3 deprecated; `dataclasses.asdict()` on option models deprecated (`options_models/base.py`) | live_run.py serializes options with `model_dump` | [P] docs/notes/ibm_heron_platform.md "Execution facts"; [S] |
| 0.50 | client-side `executor_sampler.Sampler` and `executor_estimator.Estimator`; `SamplerV2` and `EstimatorV2` deprecated; `max_execution_time` at the options top level (`environment.max_execution_time` deprecated); `XSlowGate`; samplomatic and ibm-quantum-schemas floors | live_run.py uses the client-side Sampler and the top-level ceiling | [P] release notes row; [S] 3.2 |

## 4. Backend controls and limits

All values are read B unless the source column names another.

<!-- ibm-runtime-options:backends:begin -->
Generated by `scripts/ibm_runtime_options_inventory.py --render` from `docs/evidence/ibm_runtime_options/backends.json`, read 2026-10-17T21:46:09+00:00 under qiskit 2.5.2 and qiskit-ibm-runtime 0.50.0.

| Control | ibm_fez | ibm_kingston | ibm_marrakesh | Source |
| --- | --- | --- | --- | --- |
| processor_type, backend_version | Heron r2, 1.3.37 | Heron r2, 1.0.0 | Heron r2, 1.0.21 | [M] `configuration()` |
| qubits | 156 | 156 | 156 | [M]; [P] processor-types.md for the heavy-hex coupling |
| basis_gates | cz, id, rz, sx, x, xslow | cz, id, rz, sx, x, xslow | cz, id, rz, sx, x, xslow | [M] |
| supported_instructions | cz, id, delay, measure, measure_reset, measure_2, measure_reset_2, reset, reset_2, rz, sx, x, if_else, store, xslow | cz, id, delay, measure, measure_reset, measure_2, measure_reset_2, reset, reset_2, rz, sx, x, if_else, store, xslow | cz, id, delay, measure, measure_reset, measure_2, measure_reset_2, reset, reset_2, rz, sx, x, if_else, store, xslow | [M] |
| supported_features | qobj, qasm3, dynamic_circuits, parameters | qobj, qasm3, dynamic_circuits, parameters | qobj, qasm3, dynamic_circuits, parameters | [M] |
| `conditional` (legacy flag) | false | false | false | [M]; `if_else` support comes from `supported_instructions` and `dynamic_circuits`, and every backend listed in `dynamic_circuit_backends` accepts it |
| measure duration / median error | 1660 ns / 0.01239 | 2180 ns / 0.00970 | 2684 ns / 0.01678 | [M] Target |
| measure_2 duration / median error | 1340 ns / 0.01404 | 1380 ns / 0.00940 | 1884 ns / 0.02075 | [M] Target |
| reset duration | 1684 ns | 2212 ns | 2720 ns | [M] Target |
| measure_reset duration | 1684 ns | 2212 ns | 2720 ns | [M] Target |
| reset_2 duration | 1364 ns | 1412 ns | 1920 ns | [M] Target |
| measure_reset_2 duration | 1364 ns | 1412 ns | 1920 ns | [M] Target |
| x, sx, id, xslow duration | x 24 ns, sx 24 ns, id 24 ns, xslow 1000 ns | x 32 ns, sx 32 ns, id 32 ns, xslow 1000 ns | x 36 ns, sx 36 ns, id 36 ns, xslow 1000 ns | [M] Target |
| cz duration median (max) / median error | 68 (88) ns / 0.00256 | 68 (108) ns / 0.00199 | 68 (96) ns / 0.00287 | [M] Target |
| dt, dtm (s) | 4e-09, 4e-09 | 4e-09, 4e-09 | 4e-09, 4e-09 | [M] |
| timing_constraints | acquire_alignment 1, granularity 1, min_length 2, pulse_alignment 1 | acquire_alignment 1, granularity 1, min_length 2, pulse_alignment 1 | acquire_alignment 1, granularity 1, min_length 2, pulse_alignment 1 | [M] |
| rep_delay_range, default_rep_delay (SDK seconds) | [0, 0.002], 0.00025 (wire 0 to 2000, 250) | [0, 0.002], 0.00025 (wire 0 to 2000, 250) | [0, 0.002], 0.00025 (wire 0 to 2000, 250) | [M]; `to_dict()` reports microseconds |
| dynamic_reprate_enabled | true | true | true | [M] |
| max_shots | 100000 | 100000 | 100000 | [M] |
| max_experiments; `backend.max_circuits` | 300; null | 300; null | 300; null | [M]; [S] `IBMBackend.max_circuits` returns None because `max_experiments` "is no longer an accurate representation of backend circuit limits" |
| meas_map | 1 group(s), largest 156 | 1 group(s), largest 156 | 1 group(s), largest 156 | [M] |
| meas_levels, meas_kernels, discriminators | null, null, null | null, null, null | null, null, null | [M] |
| multi_meas_enabled, measure_esp_enabled | true, false | true, false | true, false | [M] |
| mcps, clops_h | 3864, 320000 | 3829, 340000 | 3732, 300000 | [M] |
| fractional `rzz` duration / median error | 68 ns / 0.00282 | 68 ns / 0.00199 | 68 ns / 0.00418 | [M] fractional Target |
| fractional `rx` median error | 24 ns / 0.00029 | 32 ns / 0.00030 | 36 ns / 0.00040 | [M]; [P] qpu-information.md "RX error" |
| `rzz` angle bounds in the Target | admitted 0.3, 1.571; refused -0.3, 2 | admitted 0.3, 1.571; refused -0.3, 2 | admitted 0.3, 1.571; refused -0.3, 2 | [M] `supported_angle_bound` |
| `rx` angle bounds | none | none | none | [M] `gate_has_angle_bounds`; [P] "any theta" |
| status at read | active, 1 pending | active, 1 pending | active, 0 pending | [M] `status()` |
<!-- ibm-runtime-options:backends:end -->

Dynamic-circuit limits per job: one level of `if` and no nesting; operands of
at most 32 bits; no `reset` or measurement inside a conditional; no `for`,
`while`, `switch` or arithmetic; about 300 broadcasts of 60 bits or 2400
broadcasts of 1 bit, where a broadcast is a transfer of unchanged classical
data and the budget belongs to the job, not the circuit
(execute-dynamic-circuits.md "Quantum Compute limitations") [P]. `store`
needs runtime 0.47 and its values never reach the result [P]. The Estimator
takes no dynamic circuits (same guide, "Use dynamic circuits with Estimator")
[P].

Implicit initialization (`init_qubits=True`) appears in every retained
scheduler timing as an `INIT_<qubit>` block of two capture rounds per qubit
that ends 877 dt (3.51 us) after circuit start on ibm_fez (9 retained jobs,
for example `results/live/2026-10-13T025444.603480Z`) and 1139 dt (4.56 us)
on ibm_kingston (14 jobs, for example `results/live/2026-10-11T152922.787095Z`)
[M].

## 5. Transpiler controls

| Control | Values in qiskit 2.5.2 with qiskit-ibm-runtime 0.50.0 | Rule | Source |
| --- | --- | --- | --- |
| `optimization_level` | 0 to 3 | level 3 consolidates 2-qubit blocks and resynthesizes them | [P] transpiler-stages.md "Optimization stage" |
| layout plugins | default, dense, sabre, trivial | VF2Layout first, then Sabre; `initial_layout` fixes placement | [S] `list_stage_plugins("layout")`; [P] transpiler-stages.md |
| routing plugins | basic, default, lookahead, none, sabre | SabreSwap is stochastic, so `seed_transpiler` fixes the output | [S]; [P] transpiler-stages.md "Routing stage" |
| translation plugins | ibm_backend, ibm_dynamic_circuits, ibm_dynamic_and_fractional, default, synthesis, translator | `IBMBackend.get_translation_stage_plugin()` returns `ibm_dynamic_circuits` whatever the backend's flags; only `ibm_dynamic_and_fractional` appends `FoldRzzAngle`; `ibm_dynamic_circuits` passes no `qubits_initially_zero` | [S] `qiskit_ibm_runtime/transpiler/plugin.py`, `ibm_backend.py` |
| constant `rzz` outside (0, pi/2] | both the default plugin and `ibm_dynamic_and_fractional` emit rzz(2.0) as rzz(pi - 2.0 = 1.141593) with two X and two RZ on all three backends | the Target's angle bounds drive the wrap; parameterized `rzz` is assumed in range and an out-of-range binding fails the job | [M] rzz_transpile_probe in backends.json; [P] fractional-gates.md |
| scheduling plugins | alap, asap, default | scheduling runs only when `scheduling_method` is set; the service schedules a submitted ISA circuit itself and reports it through `scheduler_timing` | [S]; [P] transpiler-stages.md "Scheduling", qiskit-runtime-circuit-timing.md |
| `stretch` | relative delays resolved at compile time; one stretch per qubit set between barriers, form `X*stretch + Y`, nonnegative; remainder on the first delay | explicit echoes on idle qubits during an `if_else` block | [P] stretch.md |
| DD by pass manager versus primitive | the client-side primitive inserts DD with `PadDynamicalDecoupling` and the Target (XX, XpXm, XY4; alap or asap; `skip_reset_qubits`), and refuses it on control flow; a circuit can carry its own DD or stretch echoes instead | [S] `executor/dynamical_decoupling.py`, probe "if_else, DD"; [P] stretch.md |
| ISA requirement | every gate in the Target's instruction set, every 2-qubit gate on a coupled pair | the service runs ISA circuits only | [P] transpile.md |
| `use_fractional_gates` | `service.backend(name, use_fractional_gates=True)` adds `rx` and `rzz` to the Target | experimental; the flag can change | [P] fractional-gates.md |

## 6. Billing and quota

<!-- ibm-runtime-options:usage:begin -->
Generated by `scripts/ibm_runtime_options_inventory.py --render` from the `usage` block of `docs/evidence/ibm_runtime_options/backends.json`

| Item | Value | Source |
| --- | --- | --- |
| Plan window | 600 s on a rolling 28-day window; `usage()` returned a period ending at the call (2026-09-19T21:46:10Z to 2026-10-17T21:46:10Z), 334 s consumed, 266 s remaining, `usage_limit_reached` false | [M] read B; AGENTS.md "QPU time and calibration" |
| Resource units | `usage()` also reports `usage_limit_ru` 10 and `usage_consumed_ru` 5.376124; job metrics carry `resource_units` | [M]; their conversion to seconds is **unverified** |
<!-- ibm-runtime-options:usage:end -->

| Item | Value | Source |
| --- | --- | --- |
| Usage model | about 2 s per sub-job plus (rep_delay + circuit length) x executions; executions = circuits after broadcasting x shots | [P] estimate-job-run-time.md "Estimate usage before submitting a job" |
| Fitted model | metered `circuits_execution_time_ns` = sum over PUBs of shots x (rep_delay + scheduler circuit duration), less one rep_delay and 8.6 to 22.1 us per job; integer `qpu_charge_time_seconds` = ceil(execution + c), c in (1.672, 1.725] s, over 23 pinned jobs of 1,024 to 122,880 executions, one executor chunk each | [M] N21_USAGE_BUDGET.md generated block |
| Planner constants | 2.3 s per job and 20 us per feed-forward stage | [M] QPU_OPTIMIZATION.md "Charged-time model and ceilings" |
| Scheduler surplus | ibm_kingston scheduler duration minus the Target gate-time bound: 2246 dt median without feed-forward, 2379 dt with one stage | [M] N21_USAGE_BUDGET.md |
| rep_delay term | at 250 us the delay is 78 percent of each n21 execution; one pair of shots costs 657.8, 357.8, 257.8 and 157.8 us at 250, 100, 50 and 0 us | [M] N21_USAGE_BUDGET.md |
| `max_execution_time` | bounds system execution time per job; the service cancels a job past it; REST key `cost` | [S] `options_models/sampler.py`, `api/rest/runtime.py` |
| Session versus batch versus job | section 2.2 | [P] |
| Instance usage pages | Instances page real-time over the last 28 days; Analytics page hourly over the last 28 full days | [P] estimate-job-run-time.md "View instance usage" |

## 7. Configuration per workload

Each table gives the recommended setting, the reason, the source and the
basis: **measured** means a repository record or live read supports it;
**inferred** means it follows from tagged facts without a repository
measurement of the outcome.

### 7.1 Static circuits, Clifford-heavy

| Control | Setting | Reason | Source | Basis |
| --- | --- | --- | --- | --- |
| twirling | `enable_gates` and `enable_measure` on, strategy `active-accum`, `num_randomizations` 32 with shots divisible by 32 and at least 64 per randomization | gate twirling turns coherent CZ error into Pauli error and measure twirling symmetrizes readout, which the symmetric correction in `live_run.corrected_summary` assumes; executions stay shots (32 x 128 = 4096) | [S] probes, 3.2 split table; live_run.py `configure_sampler` | inferred: no retained run used twirling |
| DD | XY4 or XX with `skip_reset_qubits` true, after a matched comparison at equal charge | idle CZ-layer windows dephase; DD can hurt densely packed circuits | [S] probe "static, DD"; [P] QPU_EXECUTION_ROADMAP.md item 4 | inferred |
| resilience, TREX, ZNE, PEC | Sampler has none; measure twirling plus the symmetric correction plays the role of TREX | the Sampler options carry no resilience field (3.1) | [S] | inferred |
| rep_delay | 250 us default until the state-prep control family measures the excess at a shorter delay | lowering the delay raises state-preparation error | [P] repetition-rate-execution.md; PR #229 plan | inferred |
| init_qubits | true | the INIT block costs 3.5 to 4.6 us per shot, 1.4 to 1.8 percent of a 250 us delay | [M] section 4 | measured |
| measure versus measure_2 | `measure` for terminal readout | measure_2 targets mid-circuit use; read the Target's errors at submission, since the ordering moved on ibm_kingston between 2026-10-14 and 2026-10-17 | [P] execute-dynamic-circuits.md; [M] section 4 | measured |
| fractional gates | off | Clifford circuits need no arbitrary rotations; fractional gates exclude gate twirling | [P] fractional-gates.md | inferred |
| shots versus replicas | replicas on disjoint buffered placements in one wide circuit before more shots | replicas share each execution's rep_delay and INIT; their benefit needs the independence and variance bound that collection checks | [M] N21_USAGE_BUDGET.md lever 4 | measured for cost, inferred for power |
| job splitting | one job per kind and shot tier; fewest jobs | each job adds 1.7 to 2.3 s; the client-side Sampler refuses mixed PUB shots | [M] billing fit; [S] probe | measured |
| mode | job | lock-time billing; sessions bill idle time | [P] 2.2 | inferred |

### 7.2 Static circuits with arbitrary rotations

| Control | Setting | Reason | Source | Basis |
| --- | --- | --- | --- | --- |
| twirling | as 7.1 with CZ entanglers; off for any circuit carrying fractional `rzz` | gate twirling excludes fractional gates and non-Clifford entanglers; `local_c1` and `local_pauli` groups exist for non-Clifford entanglers | [P] ibm_fractional_execution_sources.md; [S] TwirlingOptions.group | inferred |
| DD | as 7.1 | | | inferred |
| resilience | Sampler: as 7.1; TREX stays available with fractional gates | | [P] fractional-gates.md | inferred |
| rep_delay, init_qubits, measure | as 7.1 | | | |
| fractional gates | candidate where rotation count dominates: one `rzz` replaces the two CZ of an RZZ decomposition, and median `rzz` error sits below twice the median CZ error on all three backends (0.00282 against 0.00511, 0.00199 against 0.00398, 0.00418 against 0.00574); `rx` halves the duration of an arbitrary single-qubit rotation | reported `rzz` error averages over angles; parameters must bind inside (0, pi/2]; it is an intervention with its own controls | [M] section 4; [P] fractional-gates.md, qpu-information.md "RZZ error" | inferred |
| shots, jobs, mode | as 7.1 | | | |

### 7.3 Dynamic circuits (mid-circuit measure, reset, if_else)

| Control | Setting | Reason | Source | Basis |
| --- | --- | --- | --- | --- |
| twirling | off for any circuit with `if_else` or `reset` | samplomatic boxing rejects `if_else` (TranspilerError) and reset propagation (SamplexBuildError); a mid-circuit measurement without control flow is accepted client-side, while the Sampler guide twirls terminal measurements only | [S] probes; [P] ibm_fractional_execution_sources.md | measured (probe) |
| DD | off with `if_else`; explicit `stretch` echoes on idle qubits during conditional blocks | the client refuses DD on control flow; it accepts DD on mid-circuit measure and reset circuits without control flow, and server acceptance of those is unverified | [S] probes; [P] stretch.md | measured (probe) |
| resilience | none; Estimator takes no dynamic circuits | | [P] execute-dynamic-circuits.md | inferred |
| rep_delay | as 7.1 | | | |
| init_qubits | true | | | |
| measure versus measure_2 | `measure` and `reset` by default; `measure_2` and `reset_2` only where waiting qubits decohere during the readout, with a matched control | measure_2 is 320, 800 and 800 ns shorter on fez, kingston and marrakesh; its error is higher on fez and marrakesh and lower on kingston at read B; Aer lacks measure_2 | [M] section 4; [P] execute-dynamic-circuits.md; AGENTS.md | measured |
| fractional gates | allowed with dynamic circuits from runtime 0.42; transpile with `ibm_dynamic_and_fractional` | the default plugin omits `FoldRzzAngle` | [P] ibm_fractional_execution_sources.md; [S] plugin.py | inferred |
| limits | one-level `if`, at most 32-bit operands, broadcast budget per job | | [P] section 4 | |
| shots versus replicas, jobs | own job, twirling and DD off; fewest jobs | | live_run.py; [S] | measured |
| mode | job | | [P] | inferred |

### 7.4 Readout and state-preparation characterization

| Control | Setting | Reason | Source | Basis |
| --- | --- | --- | --- | --- |
| twirling | measure twirling off | twirling symmetrizes the assignment channel and hides the asymmetry between P(0 given 1) and P(1 given 0) that the run measures | [S] live_run.py docstring of the symmetric readout correction | inferred |
| DD | off | | | inferred |
| resilience | none | the run measures the error mitigation would remove | | inferred |
| rep_delay | the swept variable, one value per job, each delay with its own 250 us reference | `rep_delay` is a job option; PR #229's `state-prep-control` family runs prep0, reset and x arms per qubit at 8192 shots, 10.82 s at 250 us and 5.90 s at 50 us | [P] repetition-rate-execution.md; [M] PR #229 dry runs | measured (dry run) |
| init_qubits | true for the standard arms; false with `rep_delay` 0 only to study carry-over, since the shots then merge | | [P] repetition-rate-execution.md | inferred |
| measure versus measure_2 | both, as matched arms | they are different physical measurements | docs/notes/ibm_heron_platform.md | inferred |
| meas_type | `classified`; `kerneled` or `avg_kerneled` for IQ data only after a dry check, since the backends report `meas_levels` None | kerneled output is incompatible with measure twirling | [S] probe; [M] section 4 | **unverified** on hardware |
| shots, jobs | one job per delay | | | |
| mode | job | | | |

### 7.5 Coherence and Ramsey

| Control | Setting | Reason | Source | Basis |
| --- | --- | --- | --- | --- |
| twirling | gates off (single-qubit circuits have no 2-qubit layers); measure twirling on if the analysis reads populations with the symmetric correction | `enable_gates` twirls 2-qubit Clifford layers only | [S] TwirlingOptions docstring | inferred |
| DD | off | DD turns a Ramsey (T2*) measurement into an echo measurement | | inferred |
| resilience | none | | | |
| delays | explicit `delay` in dt multiples (granularity 1, min_length 2 at dt 4 ns); `xslow` (1 us X) where a slow native pulse is the object | | [M] section 4 | measured |
| rep_delay | default; long delays make circuit length, not rep_delay, the per-shot cost | | [P] estimate-job-run-time.md | inferred |
| init_qubits | true | | | |
| timing check | `scheduler_timing` true, as live_run.py sets for every job | the returned schedule confirms delay placement; it is not billing | [P] qiskit-runtime-circuit-timing.md | measured |
| fractional gates | `rx` only if the phase sweep needs arbitrary-angle pulses | | [P] | inferred |
| routing | IBM hardware only for a device question (a named qubit's detuning or drift); otherwise Kaggle | | AGENTS.md "QPU time and calibration" | |

### 7.6 n21-feedback-encoded run

The reference dry run `results/live/2026-10-17T130242.718497Z/record.json`
selected two replicas at 122,880 shots per arm, one dynamic job of two PUBs,
250 us delay, twirling off, DD off: 83.1 s planner charge under a 95 s
ceiling [M].

| Control | Setting | Reason | Source | Basis |
| --- | --- | --- | --- | --- |
| twirling | off | `if_else` | [S] probe | measured (probe) |
| DD | off | control flow | [S] probe | measured (probe) |
| rep_delay | 50 to 100 us once the state-prep control measures the excess and the exact model carries it | at one calibration and design the 50 us plan charges 27.73 s against 67.05 s at 250 us, 39.3 s from the delay alone; the 50 us plan clears power by 0.00026 at prep excitation 0.01 | [M] PR #229 dry runs 2026-10-17T203941.331080Z and 2026-10-17T204710.144206Z | measured (dry run) |
| init_qubits | true | its INIT block is part of the 2246 dt scheduler surplus the billing fit absorbs | [M] | measured |
| measure versus measure_2 | `measure`, `reset` | measure_2 and reset_2 save 3.2 us per pair of shots on kingston, 0.4 s at 120,000 shots, at a readout Aer cannot represent | [M] N21_USAGE_BUDGET.md lever 7 | measured |
| fractional gates | off | no fractional plan or control exists for this family, and a fractional decomposition is an intervention with its own controls | docs/notes/ibm_heron_platform.md "Execution facts" | inferred |
| shots versus replicas | two replicas; per-PUB shots at most `max_shots` 100,000 | the selected tier of 122,880 shots per PUB exceeds `max_shots`; job db6q2p2mb58s738c75gg (`results/live/2026-10-13T025444.603480Z`) ran 120 PUBs of 1,024 shots, 122,880 executions, so the limit does not bind the job total, while no retained PUB exceeds 8,192 shots and a per-PUB reading stays **unverified**; two identical PUBs of 61,440 shots per arm keep one job and uniform shots | [M] section 4, retained raw files | measured limit, inferred remedy |
| job splitting | one dynamic job | each added job costs 1.7 to 2.3 s | [M] | measured |
| mode | job | | [P] | inferred |

### 7.7 Estimator-style expectation values

| Control | Setting | Reason | Source | Basis |
| --- | --- | --- | --- | --- |
| primitive | client-side `executor_estimator.Estimator`; dynamic circuits go through the Sampler with basis rotations | `EstimatorV2` is deprecated; the Estimator takes no dynamic circuits | [S]; [P] execute-dynamic-circuits.md | |
| resilience_level | 1 (the default): measure twirling and measurement mitigation (TREX) | level 2 adds gate twirling and ZNE gate folding, and the default noise factors (1, 3, 5) multiply executions | [S] 3.2 level table, ZneOptions | inferred cost |
| PEC, PEA | off on this plan | client-side PEC and PEA refuse to run without `layer_noise_model`; one NoiseLearnerV3 layer at the defaults (6 depths x 9 circuits x 32 randomizations x 128 shots) is 221,184 executions, about 58 s at 250 us per layer; PEC and ZNE are mutually exclusive; fractional gates exclude both | [S] probes, NoiseLearnerV3Options defaults; [P] fractional-gates.md | inferred cost |
| twirling | as the level resolves it | | [S] | |
| DD | as 7.1 | | | |
| precision, shots | `default_precision` 0.015625 is 4096 shots; `default_shots` overrides it | | [S] | |
| rep_delay, init_qubits, measure | as 7.1 | | | |
| fractional gates | TREX only | | [P] | |
| mode | job | | [P] | |

## 8. Restrictions the repository hit

| Restriction | Evidence | Source |
| --- | --- | --- |
| twirling boxing rejects `if_else` | probes "if_else, gate twirling" and "if_else, measure twirling": TranspilerError | [S] 3.2; QPU_EXECUTION_ROADMAP.md item 4 |
| twirling rejects reset and a classical bit measured twice | probes "reset, ..." and "measure twice into one bit, ...": SamplexBuildError | [S] 3.2 |
| DD rejected on control flow | probe "if_else, DD": IBMInputValueError | [S] 3.2; ibm-runtime-execution-guides.md |
| one shot count per client-side job | probe "two PUBs, 1000 and 2000 shots" | [S] 3.2 |
| fractional gates exclude gate twirling, PEC and PEA | | [P] fractional-gates.md |
| PUB order and single-batch execution not guaranteed | column-wise iteration over circuits and shots | [P] repetition-rate-execution.md |
| `rzz` error is its own on most pairs and can exceed `cz` | median `rzz` above `cz` on fez and marrakesh | [M] section 4; ibm_heron_platform.md |
| measure_2 absent from Aer | local simulation needs an explicit representation | docs/notes/ibm_heron_platform.md |
| pulse-level control removed on 3 February 2025 | | docs/notes/algebra_circuit_rules.md |

## 9. live_run.py against the optimum

What `live_run.configure_sampler` and `live_run._compile` set today [S]:
the client-side Sampler in job mode; `default_shots` per job; `rep_delay` set
to `--rep-delay` when given and to `backend.default_rep_delay` when the option
is omitted, on a backend with `dynamic_reprate_enabled`; top-level
`max_execution_time` from the approved ceiling; `scheduler_timing` true;
`job_tags`; on static jobs only, with `--twirl`, gate and measure twirling at
32 randomizations of at least 64 shots, and with `--dd` the named sequence
with `skip_reset_qubits`; transpilation at optimization level 3 with a seed
and an admission Target through `transpile(backend=...)`, so the translation
plugin is `ibm_dynamic_circuits`; no fractional gates, no `MidCircuitMeasure`,
`init_qubits` and `meas_type` at their defaults; jobs split by kind and shot
tier.

| # | Gap | Candidate change | Impact | Source |
| --- | --- | --- | --- | --- |
| G1 | No `max_shots` check; the n21 reference plan selects 122,880 shots per PUB against 100,000, and the retained jobs show only that the limit does not bind a job's summed executions (120 x 1,024 completed) | refuse a plan above `configuration().max_shots`, or split each PUB into equal copies within it | a refused or truncated n21 job | [M] section 4, 7.6 |
| G2 | Closed: `--rep-delay SECONDS` reaches `sampler_rep_delay()` and `execution.rep_delay` in `configure_sampler`, validated against `rep_delay_range` and bound in the approved record; the backend `default_rep_delay` applies only when the option is omitted | run the n21 plan at 50 us with the state-prep control | 39.3 s on the n21 run at 50 us | [S] `live_run.py`; [M] PR #229 dry runs |
| G3 | The planner's per-shot cost uses the Target gate-time bound; the scheduler adds the INIT block and a constant surplus (2246 dt on kingston without feed-forward) that the declared 20 us per stage absorbs only for feed-forward PUBs | add the measured per-backend surplus to static PUBs | 9.0 us per static shot on kingston, 3.6 percent of a 250 us delay and 18 percent of a 50 us one; the 0.6 s between the 2.3 s planner overhead and the fitted 1.7 s constant covers it up to about 66,000 static shots per job | [M] N21_USAGE_BUDGET.md, section 4 |
| G4 | `local_compute.is_dynamic` marks mid-circuit measurement and reset as dynamic, so those jobs never get DD, though the client accepts DD without control flow | key DD eligibility on control flow after a hardware check of server acceptance | data quality of idle-heavy mid-circuit circuits | [S] probes |
| G5 | Twirling and DD have no retained hardware run | a matched A/B at equal charge on a static case before either becomes a default | unknown sign of the effect | QPU_EXECUTION_ROADMAP.md item 4 |
| G6 | Fractional gates unused | `use_fractional_gates=True` with `ibm_dynamic_and_fractional` for rotation-heavy static families, with its own controls and twirling off | CZ count of RZZ-heavy circuits | [M] section 4; [P] |
| G7 | `measure_2` and `reset_2` unused | use only where readout duration limits a feed-forward circuit, with a matched control; re-read the Target errors per run | 0.8 us per mid-circuit readout on kingston | [M]; N21_USAGE_BUDGET.md |
| G8 | Calibration drift between planning and execution is detected per batch but not pinned | evaluate `calibration_id` on `service.backend()` and the run payload | drift risk of the n21 contrast (0.0229 to 0.0308 within a day) | [S] 2.3; [M] N21_USAGE_BUDGET.md "Calibration drift" |
| G9 | `meas_type` fixed at `classified` | kerneled readout for readout studies after a check, since `meas_levels` reads None | new readout observable | [S]; [M] |

No gap: job mode over session mode; one dynamic job per kind; the top-level
`max_execution_time`; `scheduler_timing` on every job; seeded level-3
transpilation.

## 10. Disagreements, unverified claims and checks not run

- ibm_kingston's median `measure_2` error (0.00940) sits below its `measure`
  error (0.00970) at read B, while docs/notes/ibm_heron_platform.md "Execution facts" and the
  2026-10-14 targets.json (0.01074 against 0.00958) state the reverse. The
  live Target holds; core-254 checks the retained snapshot only.
- The fractional-gates guide says `FoldRzzAngle` handles out-of-range
  constant angles; the default `ibm_dynamic_circuits` plugin lacks it, and the
  wrap comes from the Target's angle bounds (section 5).
- The Sampler guide twirls terminal measurements only; the client accepts
  measure twirling on a circuit with a mid-circuit measurement, and which
  measurements it twirls there is unverified.
- Unverified: session availability on this plan; the conversion of
  resource units to seconds; whether `max_shots` binds a PUB or a
  circuit (a job total of 122,880 executions completed); the server's handling of `calibration_id` at execution;
  kerneled readout on these backends; billing overhead per twirling
  randomization.
- Not run: any submission, `dry_run=True`, session or batch creation, each
  a service request that waits for an approved written case (AGENTS.md "QPU
  time and calibration"); a fresh read of the IBM web guides (the transcribed
  copies and recorded hashes are the documentation authority here).
