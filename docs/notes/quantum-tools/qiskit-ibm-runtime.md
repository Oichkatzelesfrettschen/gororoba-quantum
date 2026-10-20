# qiskit-ibm-runtime

## NAME

qiskit-ibm-runtime 0.50.0 -- IBM Quantum Runtime client: services, backends,
sessions and batches, the client-side `executor_sampler.Sampler`, options,
fake backends. This guide covers the local-only aspects.

## SYNOPSIS

```python
from qiskit_ibm_runtime.executor_sampler import Sampler
sampler = Sampler(mode=backend)              # BackendV2: local; IBMBackend / Session / Batch: service
sampler.options.default_shots = 2000
sampler.run([isa_circuit]).result()[0].data.c.get_counts()
```

No example in this manual contacts IBM. The runtime examples run inside
`unshare -rn` (a network namespace with no route), so a stray service call
fails instead of reaching the service.

| Substrate | Status |
| --- | --- |
| Build host | python-qiskit-ibm-runtime 0.50.0, python-samplomatic 0.21.0, python-ibm-quantum-schemas 0.12.20260921 (Arch) |
| Kaggle | `qiskit-ibm-runtime==0.50.0` in the `quantum-tools` group (not installed otherwise), installed at 0.50.0 on the CPU kernel run `results/kaggle/2026-10-16T163552Z-gororoba-substrate-crossover-cpu` (`pin_groups.json`); a kernel holds no IBM credential, so it uses only the local aspects below |

## CAPABILITIES IN THIS REPOSITORY

- Local `Sampler`. Passing a `BackendV2` that is not an `IBMBackend` (the
  snapshot `AerSimulator`) makes the primitive use `QiskitRuntimeLocalService`;
  `run` executes on Aer and returns the same `PubResult` shape as a hardware
  job. The example runs a static Bell circuit and a feed-forward circuit.
- Option objects. `sampler.options` carries `default_shots`, `execution`
  (`rep_delay`, `scheduler_timing`), `twirling`, `dynamical_decoupling`,
  `max_execution_time`, `environment` (`job_tags`), `experimental`,
  `simulator`; `live_run.py` sets these (`gororoba_quantum/live_run.py`,
  `sampler = Sampler(mode=backend)` and the lines after it). Options set
  locally are accepted; their effect is partial (see Traps).
- Fake backends. `qiskit_ibm_runtime.fake_provider.FakeKingston`, `FakeFez`
  and `FakeMarrakesh` are bundled `BackendV2` objects; `FakeKingston` (the one
  checked) has 156 qubits and a Target that lists `measure_2` and `if_else`,
  which the retained snapshot omits. Their data is bundled with the package, not
  the retained `docs/evidence/calibration/` export.
- `dry_run=True` on `Sampler.run`. Read from the source (`executor_sampler/sampler.py`):
  the docstring states the dry run is processed server-side and returns
  randomized mock data. It contacts IBM, so it was not run, and it belongs to the
  `--native-dry-run` path that ci/AGENTS.md describes.
- Not run: `QiskitRuntimeService`, `Session`, `Batch`, `Executor`,
  `NoiseLearner*`, `usage()`, job retrieval.

## API ENTRY POINTS

`qiskit_ibm_runtime` public names (76), by introspection:

classes:

```text
  Batch, Estimator, EstimatorOptions, EstimatorV2, Executor,
  ExecutorOptions, IBMAccountError, IBMApiError, IBMBackend,
  IBMBackendApiError, IBMBackendApiProtocolError, IBMBackendError,
  IBMBackendValueError, IBMError, IBMInputValueError, IBMNotAuthorizedError,
  IBMQuantumComputeService, IBMRuntimeError, JobError, JobTimeoutError,
  NoiseLearner, NoiseLearnerOptions, NoiseLearnerV2, NoiseLearnerV3,
  NoiseLearnerV3Options, Options, OptionsV2, QiskitError,
  QiskitRuntimeService, QuantumProgram, RuntimeDecoder, RuntimeEncoder,
  RuntimeInvalidStateError, RuntimeJobFailureError,
  RuntimeJobMaxTimeoutError, RuntimeJobNotFound, RuntimeJobTimeoutError,
  RuntimeJobV2, RuntimeOptions, RuntimeProgramNotFound, Sampler,
  SamplerOptions, SamplerV2, Session
```

`qiskit_ibm_runtime.executor_sampler` public names (6), by introspection:

classes:

```text
  Sampler, SamplerV2
```

modules:

```text
  finalize_options, prepare, sampler, utils
```

`qiskit_ibm_runtime.options_models` public names (35), by introspection:

classes:

```text
  BitFlipChecksOptions, DynamicalDecouplingOptions, EnvironmentOptions,
  EstimatorOptions, ExecutionOptions, ExecutorOptions,
  MeasureNoiseLearningOptions, NoiseLearnerV3Options, PecOptions,
  PostCircuitBitFlipChecksOptions, PostSelectionOptions,
  PreCircuitBitFlipChecksOptions, ResilienceOptions,
  SamplerExecutionOptions, SamplerOptions, SimulatorOptions,
  TwirlingOptions, ZneOptions
```

## EXAMPLES

```python
# nonet: runs inside `unshare -rn`, so a stray IBM call fails instead of reaching the service
import json, sys
sys.path.insert(0, "gororoba_quantum")
import qiskit_ibm_runtime
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime.executor_sampler import Sampler
from qiskit_ibm_runtime.fake_provider import FakeKingston
import calibration_snapshot as cs

snap = json.load(open("docs/evidence/calibration/ibm_kingston.json"))
sim = cs.noise_simulator(snap)
print("qiskit-ibm-runtime", qiskit_ibm_runtime.__version__)

s = Sampler(mode=sim)                       # a BackendV2 selects QiskitRuntimeLocalService
print("service:", type(s._service).__name__, "| default_shots:", s.options.default_shots)
print("option groups:", sorted(n for n in dir(s.options) if not n.startswith("_")))

bell = QuantumCircuit(2, 2); bell.h(0); bell.cx(0, 1); bell.measure([0, 1], [0, 1])
tc = transpile(bell, sim, initial_layout=[0, 1], optimization_level=1, seed_transpiler=1)
s.options.default_shots = 2000
print("static Bell counts:", dict(sorted(s.run([tc]).result()[0].data.c.get_counts().items())))

# feed-forward: the circuit carries rz/sx only, the basis of the Aer noise model
dc = QuantumCircuit(2, 2)
dc.rz(1.5707963267948966, 0); dc.sx(0); dc.rz(1.5707963267948966, 0); dc.measure(0, 0)
with dc.if_test((dc.clbits[0], 1)):
    dc.x(1)
dc.measure(1, 1)
print("dynamic circuit counts:", dict(sorted(s.run([dc]).result()[0].data.c.get_counts().items())))
try:
    transpile(dc, sim, initial_layout=[0, 1])
except Exception as e:
    print("transpile against the snapshot Target:", type(e).__name__, e)

s2 = Sampler(mode=sim)
s2.options.default_shots = 50
s2.options.twirling.enable_gates = True
print("shots returned with gate twirling enabled and 50 requested:", s2.run([tc]).result()[0].data.c.num_shots)

fk = FakeKingston()
print("FakeKingston:", fk.num_qubits, "qubits,", sorted(fk.target.operation_names)[:6], "...")
```

Output:

```text
qiskit-ibm-runtime 0.50.0
service: QiskitRuntimeLocalService | default_shots: 4096
option groups: ['default_shots', 'dynamical_decoupling', 'environment', 'execution', 'experimental', 'max_execution_time', 'simulator', 'twirling']
static Bell counts: {'00': 1013, '01': 9, '10': 19, '11': 959}
dynamic circuit counts: {'00': 1040, '01': 8, '10': 5, '11': 947}
transpile against the snapshot Target: TranspilerError "The control-flow construct 'if_else' is not supported by the backend."
shots returned with gate twirling enabled and 50 requested: 64
FakeKingston: 156 qubits, ['cz', 'delay', 'id', 'if_else', 'measure', 'measure_2'] ...
```

## INTEROP WITH QISKIT

The local `Sampler` accepts ISA circuits (and, as the dynamic example shows,
circuits built from the Target's basis with `if_test`), returns
results whose `data.<creg>.get_counts()` gives counts, and takes
`default_shots` from `options`. `transpile` against the snapshot Target rejects
`if_else` (`TranspilerError "The control-flow construct 'if_else' is not
supported by the backend."`), so a dynamic circuit is built directly in the basis.

## CPU AND GPU

Local runs use the backend's simulator device (`noise_simulator(snapshot,
device=...)`). The client code is CPU only.

## TRAPS

- With `twirling.enable_gates = True` and 50 shots requested the local run
  returned 64 shots: the randomization grid sets the shot count. Hardware
  jobs in `live_run.py` guard this with `TWIRLING_RANDOMIZATIONS` and
  `TWIRLING_MIN_SHOTS_PER_RANDOMIZATION`.
- `default_shots` is 4096 until set.
- An untranspiled circuit (`h`) on the snapshot simulator fails with
  `AerError: unknown instruction: h`.
- Per the root AGENTS.md, gate twirling boxes circuits through samplomatic,
  which rejects `if_else`, and the service rejects dynamical decoupling on
  dynamic circuits, so `live_run.py` sends dynamic circuits in their own job
  with both off. This statement is from AGENTS.md and was not rerun here.
- `Sampler(mode=IBMBackend)` and a bare `QiskitRuntimeService()` need the
  credential in `~/.qiskit/qiskit-ibm.json`; neither is needed or used by the
  examples.
- Use `/migrate-qiskit-ibm-runtime` for any change that touches this package
  (root AGENTS.md, "Qiskit skills").

## LICENSE

Apache-2.0.
