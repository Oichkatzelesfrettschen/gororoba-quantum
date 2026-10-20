# Python stack for photonic (Belenos) design and analysis

This note inventories the Python distributions of the system interpreter
(`/usr/bin/python3`, Python 3.14, Arch packages) that bear on Quandela
Belenos experiment design and analysis, and maps what Perceval 1.3.1 and
exqalibur 1.4.2 compute. Versions come from `importlib.metadata`; the complete
list of 1305 installed distributions is
[python-stack-versions.json](python-stack-versions.json). Installation
recipes and the pinned dependency table are in [README.md](README.md#installation);
service behavior, the measured cost model and the open form-versus-dwell
design are in [strategy.md](strategy.md); the captured Perceval 1.3 pages are
under [perceval/](perceval/reference/runtime/computer.md). Hypercomplex,
quaternion and Clifford packages have one note each under
[../packages/](../packages/README.md).

Evidence labels: "verified" means read in the installed source or executed
locally; "docs" means stated in a docstring or captured page only;
"unverified" means neither. "Repo use" names the scripts that import or call
the item; "none" means no file under `scripts/` or `gororoba_quantum/`
references it.

## 1. Installed distributions

### 1.1 Photonic stack

| Distribution | Import | Version | Role |
|---|---|---|---|
| perceval-quandela | `perceval` | 1.3.1 | circuits, Experiment, noise model, local backends, cloud client |
| exqalibur | `exqalibur` | 1.4.2 | compiled core: SLOS, Clifford and Clifford, CircuitOptimizer, Fock-state containers, protobuf schema |
| scmver | `scmver` | 1.10 | build-time version reader for Perceval |
| multipledispatch | `multipledispatch` | 1.0.0 | dispatch behind `Experiment.with_input` and friends |
| latexcodec | `latexcodec` | 3.0.1 | LaTeX text codec for circuit rendering |
| drawsvg | `drawsvg` | 2.4.2 | SVG circuit drawing |
| CairoSVG, cairocffi | `cairosvg`, `cairocffi` | 2.9.1, 1.7.1 | SVG rasterization for drawings |
| tabulate | `tabulate` | 0.10.0 | table display |
| platformdirs | `platformdirs` | 4.13.0 | Perceval persistent-data directory |
| protobuf | `google.protobuf` | 7.36.1 | runtime for exqalibur's `circuit_pb2` |
| mcp | `mcp` | 1.29.0 | MCP server SDK for `scripts/qd_mcp_server.py` |
| pydantic, anyio | `pydantic`, `anyio` | 2.13.5, 4.15.1 | MCP server dependencies |

`perceval-interop` and `qhub-api` (the `kipu` extra) are not installed.

### 1.2 Numerical, symbolic and statistics

| Distribution | Import | Version | Role |
|---|---|---|---|
| numpy | `numpy` | 2.5.4 | array core; Perceval Matrix backend |
| scipy | `scipy` | 1.18.1 | linear algebra, optimization, stats (binomial and hypergeometric tests, `scipy.stats.binomtest`) |
| sympy | `sympy` | 1.14.0 | symbolic parameters in Perceval circuits |
| python-flint | `flint` | 0.9.0 | exact rank and nullspace (`scripts/exact_rank.py`) |
| mpmath | `mpmath` | 1.4.1 | arbitrary-precision floats |
| gmpy2 | `gmpy2` | 2.3.2 | multiprecision integers |
| networkx | `networkx` | 3.7 | graph algorithms (Perceval dependency) |
| rustworkx | `rustworkx` | 0.18.1 | graph core for Qiskit |
| matplotlib | `matplotlib` | 3.11.2 | plotting |
| seaborn, plotly | `seaborn`, `plotly` | 0.13.2, 7.1.0 | statistical and interactive plots |
| pandas | `pandas` | 2.3.3 | tables |
| scikit-learn, scikit-image | `sklearn`, `skimage` | 1.9.1, 0.26.0 | regression, clustering, image tools |
| lmfit | `lmfit` | 1.3.4 | nonlinear least squares with bounds |
| emcee | `emcee` | 3.1.6 | MCMC ensemble sampler |
| uncertainties | `uncertainties` | 3.2.4 | first-order error propagation |
| numdifftools | `numdifftools` | 0.11.1 | numerical derivatives |
| cvxpy | `cvxpy` | 1.9.3 | convex optimization |
| PySCIPOpt | `pyscipopt` | 6.3.0 | mixed-integer programming |
| opt_einsum | `opt_einsum` | 3.4.0 | contraction path search |
| sparse | `sparse` | 0.17.0 | sparse n-dimensional arrays |
| numba | `numba` | 0.68.0 | JIT compilation |
| torch | `torch` | 2.14.1 | tensors, autodiff, GPU |
| jax, jaxlib | `jax` | 0.9.0, 0.9.0.dev0+selfbuilt | autodiff, XLA |
| tensorflow | `tensorflow` | 2.21.0 | tensors, autodiff |
| cupy | `cupy` | 14.2.0 | GPU arrays |

statsmodels, pymc, arviz, qutip, pennylane, cirq and symengine are not
installed.

### 1.3 Gate-model quantum stack

| Distribution | Import | Version | Role |
|---|---|---|---|
| qiskit | `qiskit` | 2.5.2 | circuits, transpiler (CI replay pin; Kaggle runs 2.6.0) |
| qiskit-aer | `qiskit_aer` | 0.17.2 | CUDA build, CPU and GPU simulators |
| qiskit-ibm-runtime | `qiskit_ibm_runtime` | 0.50.0 | IBM primitives |
| qiskit-experiments | `qiskit_experiments` | 0.14.2 | calibration and characterization experiments |
| qiskit-mitigation | `qiskit_mitigation` | 0.1.1 | error mitigation add-on |
| qiskit-addon-utils | `qiskit_addon_utils` | 0.4.0 | Qiskit addon helpers |
| qiskit-qasm3-import | `qiskit_qasm3_import` | 0.6.0 | OpenQASM 3 import |
| samplomatic | `samplomatic` | 0.21.0 | runtime 0.50 boxing and twirling |
| ibm-quantum-schemas | `ibm_quantum_schemas` | 0.12.20260921 | runtime 0.50 schemas |
| stim | `stim` | 1.16.0 | Clifford and stabilizer simulation |
| mthree | `mthree` | 3.0.0 | matrix-free readout mitigation |
| runningman | `runningman` | 2.3.0 | mthree dependency |
| quimb | `quimb` | 1.15.0 | tensor-network states and circuits |
| cotengra | `cotengra` | 0.8.2 | contraction ordering |
| pyzx | `pyzx` | 0.10.7 | ZX-calculus circuit rewriting |
| galois | `galois` | 0.4.11 | finite-field arrays |

### 1.4 Hypercomplex, quaternion and Clifford packages

Relation to `cd_core` is in [docs/notes/algebra_circuit_rules.md](../algebra_circuit_rules.md) and one note per
package under [../packages/](../packages/README.md).

| Distribution | Import | Version | Role |
|---|---|---|---|
| sagemath | `sage` | 10.10 | exact octonion reference, quadratic forms |
| hypercomplex | `hypercomplex` | 0.3.4 | exact Cayley-Dickson algebras over `Fraction` |
| hypercomplex-engine | `hypercomplex_engine` | 0.5.0 | fast basis-sign oracle |
| hypercomplex-algebra | `hypercomplex_algebra` | 0.2.0.2 | expression parsing over the engine |
| Cayley_Calculator | `Cayley_Calculator` | 1.3.1 | elementary functions through D = 128 |
| cayley-dickson | `cayley_dickson` | 0.1.0 | reading and cross-checking |
| octonion | `octonion` | 0.1.0 | batched octonion tensors (PyTorch) |
| SplitOct | `SplitOct` | 0.16 | split-octonion negative control |
| mathdunders | `mathdunders` | 0.4.2 | operator plumbing |
| pyoctonion | `pyoctonion` | 3.12 | octonion check |
| Octonion_Sedenion | `Octonion_Sedenion` | 1.0.0 | sedenion table |
| numpy-quaternion | `quaternion` | 2024.0.13 | compiled quaternion dtype |
| quaternionic | `quaternionic` | 1.0.18 | numba quaternion arrays |
| pyquaternion | `pyquaternion` | 0.9.9 | rotation quaternions |
| clifford | `clifford` | 1.5.1 | numerical geometric algebra |
| kingdon | `kingdon` | 3.0.0 | geometric algebra on numpy, sympy, torch |
| galgebra | `galgebra` | 0.6.0 | symbolic geometric algebra |
| hyprat | `hyprat` | 0.2.0 | rational Cayley-Dickson with doubling parameter |
| pyadic | `pyadic` | 0.3.0 | p-adic and exact number types |

## 2. Perceval 1.3.1 capability map

All entries verified by `inspect` against
`/usr/lib/python3.14/site-packages/perceval` unless marked otherwise. The
Perceval namespace exports 293 public names; this section lists those that bear on
Belenos work.

### 2.1 Circuits and components

| Item | Key parameters | Computes | Repo use |
|---|---|---|---|
| `Circuit(m, name)` | `add(port, component, merge)`, `//`, `compute_unitary()`, `decomposition`, `isolate`, `replace`, `barrier` | container of m modes; `compute_unitary` returns the m x m `Matrix` | `qd_platform.py` (`pcvl.Circuit`), `qd_belenos_mesh.py` |
| `BS(theta, phi_tl, phi_bl, phi_tr, phi_br, convention)` | `convention` in `BSConvention.Rx|Ry|H`; classmethods `BS.Rx/Ry/H` | 2-mode beam splitter, default `theta = pi/2` (50:50) | `qd_platform.py` (`BS.H`, `BS(theta=...)`) |
| `PS(phi, max_error)` | `max_error` is a per-component random phase bound | phase shifter on one mode | `qd_platform.py`, `qd_belenos_mesh.py` |
| `PERM(perm)` | `perm`: list of target modes; `break_in_2_mode_perms`, `fourier`, `random` | mode permutation | `qd_platform.py` |
| `Unitary(U, name, use_polarization)` | `U`: `Matrix` or ndarray | arbitrary linear-optical unitary | `qd_platform.py`, `qd_mcp_server.py` |
| `GenericInterferometer(m, fun_gen, shape, depth, phase_shifter_fun_gen, phase_at_output, ...)` | `shape` is `InterferometerShape.RECTANGLE|TRIANGLE`; `set_param_list`, `set_identity_mode` | rectangular MZI mesh of free parameters | none (the 552-coupler mesh is decoded from the service record by `qd_belenos_mesh.py`) |
| `LC(loss)`, `TD(dt)`, `PR`, `HWP`, `QWP`, `WP`, `PBS`, `Barrier` | | loss channel, time delay, polarization elements | none |
| `Matrix(source)` | `random_unitary(n)`, `is_unitary`, `get_unitary_extension`, `tonp`, `tosp`, `parametrized_unitary` | numeric or symbolic matrix | `qd_platform.py`, `qd_belenos_mesh.py` (cross-check) |
| `P(name)` / `Parameter` | named free parameter | binds by `Experiment.get_circuit_parameters`; remote iterations rebind them via `circuit_params` | `qd_platform.py` |
| `ConstraintChecker`, `decompose_perms` | | circuit checks against platform constraints; PERM decomposition | none |

### 2.2 Experiment, states and post-selection

| Item | Signature or key parameters | Computes | Repo use |
|---|---|---|---|
| `Experiment(m_circuit, noise, name)` | `add`, `set_circuit`, `with_input(state)`, `min_detected_photons_filter(n)`, `set_postselection(PostSelect)`, `add_herald`, `add_port`, `copy`, `get_circuit_parameters`, `unitary_circuit(flatten, use_phase_noise)`, `non_unitary_circuit`, `use_phase_noise(noise, seed)` | description of a run: circuit, input, detectors, heralds, selection, noise | `qd_platform.py` (`pcvl.Experiment`) |
| `BasicState` / `FockState` | `BasicState([1,0,1])` or `"|1,0,1>"`; `.n`, `.m`, `.threshold_detection()` | one Fock configuration; exqalibur `FockState` underneath | `qd_platform.py` |
| `StateVector`, `AnnotatedFockState`, `NoisyFockState` | superpositions, photon annotations (distinguishability), noisy inputs | coherent and partially distinguishable inputs | none |
| `SVDistribution`, `BSDistribution`, `BSCount`, `BSSamples` | dict-like (`BSCount` has `total`; `BSSamples` is a list) | mixed-state input, output probabilities, counts, ordered sample stream | none (service results are parsed without Perceval's deserializer) |
| `PostSelect("[0,1] == 1 & [2] > 0")` | condition syntax in the exqalibur docstring | predicate on output states | none |
| `StateGenerator(Encoding)` | `bell_state`, `ghz_state`, `dicke_state`, `graph_state`, `logical_state` | encoded states | none |
| `Processor(backend, m_circuit, noise)` | local container with `.probs()`, `.samples()` | local simulation with an Experiment inside | `qd_mcp_server.py` (`pcvl.Processor`) |
| `Source(emission_probability, multiphoton_component, indistinguishability, losses, multiphoton_model)` | `from_noise_model`, `generate_distribution`, `create_sampler`, `is_perfect` | quantum-dot source mixture of Fock states | none directly |

### 2.3 NoiseModel

`NoiseModel(brightness, indistinguishability, g2, g2_distinguishable,
transmittance, phase_imprecision, phase_error)`; verified in
`perceval/utils/noise_model.py`. Defaults mean no noise.

| Field | Range, default | Effect |
|---|---|---|
| `brightness` | 0..1, 1 | source `emission_probability` |
| `indistinguishability` | 0..1, 1 | two-photon mean wavepacket overlap |
| `g2` | 0..1, 0 | multiphoton component g2(0) |
| `g2_distinguishable` | bool, True | extra photons distinguishable or not |
| `transmittance` | 0..1, 1 | system-wide `Source.losses = 1 - transmittance` |
| `phase_error` | 0..pi, 0 | uniform random error in [-phase_error, +phase_error] added to every PS |
| `phase_imprecision` | >= 0, 0 | phase quantization step |

`perf_dict_to_noise` and `noise_to_perf_dict` convert to the platform's
performance dictionary (percent units for `transmittance`,
`indistinguishability`, `g2`). Repo use: none for local noise; the service's
own figures are recorded by `qd_platform.py plan`.

### 2.4 Detectors

`Detector.threshold()`, `Detector.pnr()`, `Detector.ppnr(n_wires,
max_detections, wire_efficiency)`; `Detector(n_wires, max_detections,
wire_efficiency)`, `BSLayeredPPNR` for the layered pseudo-PNR model.
`wire_efficiency` in (0, 1] is the only loss parameter. No detector model
carries a dark-count rate: the `DetectorBalancing` source states the
hypothesis "the detectors only model photon losses (no dark count)", and a
search of the package for dark-count fields finds none. Repo use: none.

### 2.5 Local backends

`BACKEND_LIST` (verified): `CliffordClifford2017`, `SamplingStepper`, `MPS`,
`Naive`, `NaiveApprox`, `SLAP`, `SLOS_LEGACY`, `SLOS`. Classes:
`SLOSBackend`, `SLOSExqaliburBackend`, `NaiveBackend`, `NaiveApproxBackend`
(`gurvits_iterations`), `MPSBackend(cutoff)`, `SLAPBackend`,
`Clifford2017Backend`, `StepperBackend`; `BackendFactory.get_backend(name)`.
Strong backends compute all output probabilities; `Clifford2017Backend`
(sampling) draws samples with `samples(count)`, parallel in exqalibur.
`SimulatedComputer(backend)` exposes `probs`, `samples`, `sample_count`
with the same `compilation_seed` argument as the remote command signature.
`Simulator`, `SimulatorFactory.build`, `NoisySamplingSimulator`, `FFSimulator`
(feed-forward) and `LossSimulator`, `DelaySimulator`, `PolarizationSimulator`
sit underneath. Repo use: `qd_mcp_server.py` runs `pcvl.Processor("SLOS", ...)`
for `qd_simulate_local`; no script uses `SimulatedComputer` or the noise path.

### 2.6 Runtime: computers, executions, commands

| Item | Signature or key parameters | Computes | Repo use |
|---|---|---|---|
| `CommandFactory` | `probs(max_samples?, max_shots?)`, `samples(max_samples, max_shots?)`, `sample_count(max_samples, max_shots?)` | the three commands; `compilation_seed` is a computation parameter that `samples`, `sample_count` and the computers accept | `qd_platform.py` builds `sample_count` bodies; `qd_belenos_mesh.py` records `"command": "sample_count"` |
| `QuandelaCommunicationLayer(platform, token, url)` | RPC layer to the cloud | prepares and sends job bodies | `qd_platform.py` (recorder replaces `create_job`) |
| `RemoteComputer(layer)` | `execute_async`, `estimate_required_shots(computation, nsamples, param_values)`, `estimate_expected_samples`, `prepare_payload`, `check_experiment` | remote execution | `qd_platform.py` |
| `RemoteProcessor`, `QuandelaSession` | legacy single-object interface | | none |
| `ExecutionFactory(computer, experiment, max_shots_per_call)` | `build_computation(name)`, `add_iteration(**kw)`, `add_iteration_list`, `clear_iterations`, `build_execution(computation)` | builds a `Computation` or `ComputationIterator` | `qd_platform.py` |
| `Computation(command, experiment)` | `add_params(**kw)` | one job | `qd_platform.py` |
| `ComputationIterator` | `add_iteration`, `make_inserter` | many parameter sets in one job | `qd_platform.py` |
| `Execution` | `execute_sync`, `execute_async`, `cancel`, `get_results`, `rerun` | job handle | none (the runner POSTs through its own checkpointed path) |
| `ExecutionGroup` | `run_parallel`, `run_sequential`, `relaunch_*` | job batches | none |

Iteration keys (verified, `ComputationIterator._ITERATOR_TYPE_CHECK`):
`circuit_params` (dict of name to Number, names must exist in the
experiment), `input_state` (BasicState with matching m), `min_detected_photons`
(int), `max_samples` (int), `max_shots` (int), `postselect` (PostSelect),
`compilation_seed` (int). Any other key raises `NotImplementedError`. The
repo's mesh iterations use `circuit_params`, `input_state`, `max_samples`,
`max_shots`, `compilation_seed`; seeded iterations use the last three.

### 2.7 Error mitigation

`MitigationFactory(level)` with `MitigationLevel.none|low|medium|high`,
`set_compilation_averaging(repetitions, starting_seed)`,
`set_distinguishable_photon_mitigation(order)`, `set_photon_recycling`,
`set_detector_balancing`.

| Class | Behavior (verified) | Repo use |
|---|---|---|
| `CompilationAveraging(repetitions, starting_seed)` | splits `max_samples` and `max_shots` evenly over `repetitions` sub-computations, forces command `probs`, sets `compilation_seed = starting_seed + i` (random start in 0..1,000,000 if none), averages the resulting distributions | none; the repo names the seed per iteration instead |
| `PhotonRecycling` | recycles unused photons into extra samples (docs) | none |
| `DetectorBalancing` | divides out detector loss per state; assumes no dark counts | none |
| `DistinguishablePhotonMitigation(order)` | corrects distinguishable-photon contributions up to `order` | none |

### 2.8 Serialization

`perceval.serialization.serialize/deserialize` and `serialize_binary` cover
circuits, experiments, states, `BSSamples`, `BSCount`, `BSDistribution`,
`NoiseModel`, detectors. `serialize_bssamples` writes the distinct states and
an index list in sample order, and `deserialize_bssamples` rebuilds the list
in that order (verified), so an order-bearing stream survives a round trip.
The repository never calls `deserialize` on service strings because it
evaluates parameter expressions through sympy ([README.md](README.md),
`scripts/qd_platform.py`); `qd_belenos_mesh.py` decodes the protobuf wire
format with a standard-library reader instead.

### 2.9 Providers and utilities

`PROVIDER_LIST`: `Quandela`, `Scaleway`, `Kipu`. `RemoteConfig` stores
token and URL (`save()` writes plain text and is never called here).
`PlatformSpecs` is a dict of platform constraints. `Catalog`/`catalog` hold
named components. `CircuitOptimizer` (Perceval wrapper) is in section 2.10.
Metrics: `tvd_dist`, `kl_divergence`, `dist_metrics` in `perceval.utils`;
`Analyzer` and `Sampler` algorithm classes under `perceval.algorithm`;
tomography helpers `tomography_exp_configurer`, `get_pauli_*`. Repo use of
these metrics: none (the repo carries its own Wilson and likelihood code).

### 2.10 CircuitOptimizer (Perceval wrapper)

`perceval.utils.algorithms.circuit_optimizer.CircuitOptimizer(threshold=1e-6,
ntrials=4, max_eval_per_trial=200000)` with
`optimize(target, template, empty_mode_list=None, first_guess=None,
seed=None) -> (circuit, fidelity)`. It forwards `seed` as the fourth
positional argument of `exqalibur.CircuitOptimizer` (verified in source).
`optimize_rectangle` runs a rectangular decomposition. Repo use: none in
code; strategy.md section 7 records a local run of this class against the
Belenos architecture.

## 3. exqalibur 1.4.2 capability map

Module attributes (verified by `dir`): `CircuitOptimizer`,
`RectangularDecomposer`, `SLOS`, `SLOS_V2`, `SLOS_V3`, `SLAP`, `SLAPSampler`,
`Clifford2017`, `SamplingSimulator`, `StrongSimulator`, `Source`,
`SourceSampler`, `SimpleSourceIterator`, `FSArray`, `FSDistribution`,
`FSFunction`, `FSMap`, `FSMask`, `FockState`, `NoisyFockState`,
`AnnotatedFockState`, `StateVector`, `SVDistribution`, `BSCount`,
`BSSamples`, `PostSelect`, `ModeIterator`, `Config`, `set_seed`,
`permanent_cx`, `permanent_fl`, `permanent_in`, `estimate_permanent_cx`,
`estimate_permanent_fl`, `sub_permanents_cx`, `sub_permanents_fl`,
`all_prob_normalize_output`, `serialization`.

| Item | Signature | Computes | Repo use |
|---|---|---|---|
| `CircuitOptimizer(target_matrix, serial_circuit, empty_modes=[], random_seed=None)` | `optimize(max_trials=4)` or `optimize(first_guess)` -> serialized circuit bytes; `set_threshold`, `set_max_eval_per_trial`, `set_max_time_per_trial`, `fidelity` | gradient-descent fit of the template's free phases to the target unitary; ignores columns listed in `empty_modes`; trials run in parallel | none in code (reached through Perceval's wrapper) |
| `RectangularDecomposer` | `decompose`, `get_interferometer`, `set_precision` | Clements-style rectangular decomposition of a unitary | none |
| `SLOS`, `SLOS_V2`, `SLOS_V3`, `SLAP` | `set_unitary`, `set_input_state`, `all_amplitudes`, `all_probabilities`, `distribution`, `set_mask`; V2/V3 add `set_post_select`, `set_backward` | strong simulation of all output amplitudes | none |
| `Clifford2017` | `set_unitary`, `set_input_state`, `sample()`, `samples(n)` | exact boson sampling, parallel | none |
| `SamplingSimulator`, `StrongSimulator` | `set_detectors`, `postselect`, `heralds`, `min_photons_filter`, `samples`, `probs_svd`, `rel_precision` | noisy simulation with detectors and post-processing | none |
| `Source(emission_probability, multiphoton_component, indistinguishability, losses, ...)` | `generate_distribution`, `create_sampler`, `is_perfect` | source mixture model (Pont et al. PRX 12, 031033 and arXiv:2211.15626, per its docstring) | none |
| `SourceSampler` | `generate_samples(n)`, `generate_separated_samples`, `physical_perf`, `zpp` | i.i.d. draws from the source model | none |
| `BSSamples` | list-like: `append`, `extend`, `insert`, `pop`, `remove`, `count`, `clear` | "ordered container, suited to save a sample stream data acquisition" (docstring) | none |
| `BSCount` | `add`, `items`, `keys`, `values`, `total` | state counts | none |
| `Config` | static `compute_max_thread_count`, `use_single_precision`, `unitary_check_precision` | thread cap (CircuitOptimizer, Clifford, permanents, noisy sampling), precision | none |
| `set_seed(seed)` | | seeds the library RNG; docstring: parallel computations are deterministic once set | none |
| `permanent_cx(M, ptype)`, `estimate_permanent_cx(M, n_iter)` | `ptype` in `glynn`, `ryser`; estimate by Gurvits with 99 percent interval | matrix permanents | none |
| `FSArray(m, n, mask)`, `FSDistribution`, `FSMask`, `FSMap`, `FSFunction` | Fock-space iteration and distributions | enumeration and masking of Fock states | none |
| `exqalibur.serialization.circuit_pb2` | protobuf messages `Experiment`, `Circuit`, `BeamSplitter`, `PhaseShifter`, `Permutation`, `Unitary`, `Detector`, `Port`, `Herald`, `CompiledCircuit`, `VariableValues`, `Parameter`, `LossChannel`, `TimeDelay` | wire format of the service's architecture and compiled circuits | `qd_belenos_mesh.py` cross-checks its own wire decoder against it |

## 4. Capabilities that bear on the form-versus-dwell jobs D1 to D4

Context: [strategy.md](strategy.md) section 7 item 10 defines D1 (S form at
dwell 1500 on mesh 29dc6ef8), D2 (I form over a dwell ladder), D3 (S form at
dwell 10000 on a fresh mesh drawn by seed) and D4 (I dwell ladder on that
mesh).

### 4.1 (a) Predicting a served mesh locally from a compilation seed

- Verified: `exqalibur.CircuitOptimizer` takes `random_seed` as its fourth
  constructor argument, and Perceval's `CircuitOptimizer.optimize(...,
  seed=...)` forwards it. A 4-mode `GenericInterferometer` fit of a fixed
  random unitary with `empty_mode_list=[1,2,3]` returned identical parameters
  and fidelity for seed 3 on two runs and different parameters for seed 4
  (fidelity 0.99999999 for seed 3). Local fits are deterministic per seed.
- Verified: Perceval does not pass `compilation_seed` to any optimizer.
  `compilation_seed` appears in `SimulatedComputer` only as the seed of
  `Experiment.use_phase_noise(noise, seed)`, which draws a
  `random.Random(seed)` phase error; the string occurs elsewhere only in the
  iteration schema, the `CompilationAveraging` mitigation and the command
  signature. The client contains no compilation step. Server-side compilation
  is outside the installed code.
- Not established: that the service seeds `exqalibur.CircuitOptimizer` with
  `compilation_seed` directly, which options (trials, threshold, evaluation
  cap, `empty_modes`) it uses, or how it maps the integer to `random_seed`.
  strategy.md section 7 records that no local seed from 0 to 63 reproduced a
  served phase, so a local seed does not predict the served mesh bitwise.
  The docs capture (`perceval/reference/runtime/computer.md`) describes the
  argument only as "a seed to use for the compilation starting point or the
  random phases".
- Consequence: a local run predicts the distribution of served meshes, not
  the mesh of a given seed. The mesh identity of D1 to D4 comes from the
  returned architecture's sha256 (`qd_belenos_mesh.py`), never from a local
  fit.

### 4.2 (b) Simulating a mesh under noise

Verified in source:

| Effect | Mechanism | Limit |
|---|---|---|
| heater phase noise | `NoiseModel.phase_error` (uniform in +-phase_error per PS, drawn once per computation from `random.Random(compilation_seed)`), `phase_imprecision` (quantization), `PS.max_error` | static per computation: no time-varying drift inside one run; a drift study needs one `SimulatedComputer` call per time slice |
| source brightness | `NoiseModel.brightness` -> `Source.emission_probability` | |
| g2(0) | `NoiseModel.g2` and `g2_distinguishable` -> multiphoton component | |
| indistinguishability | `NoiseModel.indistinguishability` | |
| transmittance | `NoiseModel.transmittance` -> `Source.losses` | one system-wide number; no per-mode efficiency |
| detector efficiency | `Detector.ppnr(..., wire_efficiency)`, `Experiment.detectors` | threshold and PNR detectors carry efficiency 1 by default; per-mode efficiency by assigning a `Detector` to each output mode |
| dark counts | none in Perceval 1.3.1 | add by post-processing counts |

The repository fits per-mode relative efficiencies and heater offsets itself
(`scripts/qd_box_kite_analysis.py`, `--static`, `--efficiency`); no script
runs Perceval's noisy simulators. Beyond Perceval's model the repository's
own noise classes (gain, thermal crosstalk, demultiplexer misroute) have no
Perceval counterpart. Executed locally: `SimulatedComputer` with
`CliffordClifford2017` and `SLOS` returns `BSSamples` for a one-beam-splitter
experiment (both outputs in a Hong-Ou-Mandel input appear as |2,0> and |0,2>,
as expected). A full 24-mode, 574-phase mesh simulation under the noise model
is not run here: unverified.

### 4.3 (c) Time-ordered samples

- Verified: the `samples` command returns `BSSamples`; its docstring in
  exqalibur calls it an "ordered container, suited to save a sample stream
  data acquisition", and Perceval's conversion helpers call it a
  "chronological list of samples".
- Verified: `serialize_bssamples` keeps sample order through an index list,
  and `deserialize_bssamples` appends states in that order, so the client
  parser preserves the order the server sends.
- Verified: locally, order is generation order. The noisy sampler appends
  each accepted sample to `output` in the loop of `_noisy_sampling`, and the
  perfect path concatenates batches of 1000 from `Clifford2017Backend.samples`.
  Strong backends do not sample in time: `SimulatedComputer.samples` on a
  strong backend computes `probs` and then draws with `probs_to_samples`,
  i.i.d. draws; `sample_count_to_samples` shuffles.
- Unverified: whether the cloud returns the events of `samples` in acquisition
  order. Nothing in the installed client reorders the list, but the server's
  assembly (sub-job splitting, parallel workers) is not visible; no retained
  run uses the `samples` command (`results/quandela` contains only
  `sample_count`). strategy.md section 7 item 10 already holds `samples`
  unused until a job proves the order. A proof needs a job whose input state
  or phase changes in a known pattern within the sample stream, which a
  single-circuit job cannot provide, so an I-form iteration ladder with a
  `samples` command is the only retained-API route to test it: unverified.
- Not retained by `sample_count`: iterations return counts per iteration, so
  within-iteration time structure is lost; iterations (separate computations
  in one job) are the only time resolution the current runner has.

### 4.4 (d) Analyzing counts

- Perceval: `BSCount`, `BSDistribution`, `samples_to_sample_count`,
  `sample_count_to_probs`, `tvd_dist`, `kl_divergence`. These do not return
  intervals.
- Repository: `wilson(successes, trials)` in `scripts/qd_box_kite_analysis.py`
  and `scripts/qd_belenos_mesh.py` (95 percent Wilson interval, z =
  1.959963984540054) is the binomial interval used for `in_block` and `a`
  shares; `docs/notes/quandela/strategy.md` section 5 holds the analysis
  rules.
- Installed and unused here for this purpose: `scipy.stats` (`binomtest`,
  `fisher_exact`, `chi2_contingency`, `beta` for Clopper-Pearson), `lmfit`
  and `emcee` for likelihood fits, `uncertainties` for propagation,
  `numdifftools` for derivatives. Whether each is the right test for the
  D1 to D4 readings is a design decision outside this inventory.
- Statistical tests that compare two iterations of one job (drift) or two
  jobs (cross-job drift near 0.034 per strategy.md) have no Perceval
  implementation; they are plain binomial or contingency tests.

### 4.5 Summary of status

| Question | Status |
|---|---|
| local `CircuitOptimizer` deterministic per seed | verified (4-mode run) |
| Perceval passes `compilation_seed` to the optimizer | verified false; it seeds only the phase-noise RNG |
| service maps `compilation_seed` to `random_seed` | unverified; 64 local seeds matched no served phase |
| noise model covers heater phase, indistinguishability, g2, transmittance, detector efficiency | verified |
| noise model covers dark counts | verified absent |
| time-varying phase drift within one simulated run | verified absent |
| client preserves `BSSamples` order | verified |
| cloud returns events in acquisition order | unverified |
| Wilson intervals in Perceval | verified absent; repository code supplies them |
