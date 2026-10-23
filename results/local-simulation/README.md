# Local photonic and compiler cross-check

The user authorized additive background simulation on the build host while
the Ascella acquisition waited. The authorization explicitly selected local
Perceval and OpenSquirrel execution. The records contain noiseless local
simulation and simulated samples; hardware loss, drift, calibration and
device conformance remain unmeasured.

The bounded run used one ordered-map worker, one OpenBLAS thread, one OpenMP
thread and process niceness 10. The background launches had a 1800-second
timeout; the final verification launch had a 120-second timeout. The initial
launch, physical rerun and two terminal-unitary runs record 144.89 seconds
of cumulative elapsed execution (nested QI subprocess time is included in
its parent launch). The four launches remained within the total
30-minute task budget selected by the coordinating agent. A fifth local
execution of the full-precision exporter adds 20.35 seconds, bringing the
cumulative execution to 165.24 seconds.

## Retained results

- [Serialized Ascella order replay](ascella-serialized-order-replay/replay.json)
  executes the failed acquisition's actual serialized computation on SLOS and
  Naive. Both local backends complete eight settings with 65,536 simulated
  samples, and sixteen probability comparisons agree with the manifest
  within 4.45e-16. Its adjacent `producer.py` supports `--check` and retains
  source hashes. The hardware instrument layer is outside this replay.

- `physical-photonic-compiler-crosscheck/photonic.json` retains 128 passing
  settings: 120 Belenos settings (three repeats of 40 order, wave, Fourier
  and control settings) on 24 physical modes and eight Ascella order
  settings on 12 physical modes. Each row retains every output probability,
  including physical outputs outside the logical support. SLOS and Naive
  agree with the frozen ideal probabilities within 6.67e-16; full optical
  operators agree within 4.06e-15. The acceptance threshold was 1e-9.
- `physical-photonic-compiler-crosscheck/producer.py` preserves the exact
  physical-run producer identified by that record's SHA-256.
- `validated-terminal-unitary-compiler-crosscheck/qi.json` retains 24 cQASM 3.0
  circuits from eight frozen Tuna-17 quaternion-order batches. libqasm
  accepts all source and compiled circuits. Each circuit retains 1024
  seeded simulated measurement samples and a separately hashed unitary
  probe derived by removing terminal measurements. The probe rejects any
  operation after the first measurement. QX output strings use qubit zero
  at the rightmost position, matching the frozen native probabilities.
  The adjacent `producer.py` matches the record's producer SHA-256.
- All 24 source unitary probes agree with native predictions within
  2.23e-16. Twenty compiled probes satisfy 1e-9; four compiled probes differ
  by 1.18e-8 to 1.34e-8. The records retain the failed comparison criterion.
  OpenSquirrel 0.9.1's `writer/writer.py` sets `FLOAT_PRECISION = 8` and
  formats floats with that precision. The retained compiled cQASM rounds
  `Ry(-1.5707963267948966)` to `Ry(-1.5707963)`. Source and compiled seeded
  samples remain available independently of the exact-probability check.
  `Circuit.__repr__` calls `writer.circuit_to_string(circuit)`, whose public
  signature accepts the circuit alone and whose implementation instantiates
  the private `_WriterImpl`. A supported public precision control is absent
  from that installed path. A separately tested repository adapter can
  address serialization precision through the separately retained export
  below; the installed package and frozen circuits retain their bytes.
- `fullprecision-compiler-crosscheck/qi.json` retains the repository-owned
  public `IRVisitor` export of the same default Tuna compiler passes. All
  24 source and full-precision compiled probes satisfy 1e-9, with maximum
  probability error 2.23e-16. Every paired source/compiled 1024-shot seeded
  histogram agrees exactly. The adapter pins OpenSquirrel 0.9.1 and accepts
  exact `Rx`, `Ry`, `Rz`, `X`, `CZ`, `Barrier` and Z-axis `Measure` statement
  classes. Unsupported IR and nonfinite angles raise explicit exceptions.
  The adapter serializes finite binary64 angles with 17 significant digits
  and preserves each measurement's bit/qubit mapping. Producer and exporter
  snapshots beside the record bind the executing sources. The default
  writer's four numerical failures remain retained independently.
- OpenQASM circuits are absent from the selected frozen cases. The run
  establishes the listed cQASM path and the Perceval optical template path.

## Diagnostic attempts

`photonic-compiler-crosscheck/` retains an initial runner API failure:
`Experiment.circuit` raised `AttributeError` for 40 logical settings. The
installed Perceval API exposes `Experiment.unitary_circuit()`. The initial
QI comparison also compared a collapsed post-measurement state with native
pre-measurement probabilities. The physical rerun corrected the Experiment
API and retains its own QI comparison using the earlier collapsed-state
method. Both collapsed-state comparisons are diagnostic harness output;
the terminal-unitary record supplies the meaningful probability comparison.
`terminal-unitary-compiler-crosscheck/qi.json` retains the first successful
terminal-unitary diagnostic; the validated record repeats its numerical
outcome after runner formatting, type checks and regression tests.
The initial runner changed on disk during its first process, so the initial
record's runner hash names the on-disk file at completion rather than the
executing initial producer. The physical producer snapshot supplies an exact
producer identity for the physical results.

## Replay

Export `PYTHON` to the repository interpreter and `QI_PYTHON` to the pinned
Quantum Inspire interpreter, then run from the checkout root:

```sh
export PYTHON QI_PYTHON
bash scripts/local_photonic_compiler_crosscheck.sh results/local-simulation/fresh-replay
```

The launcher sets the required TLS tunable, CPU thread limits and import
paths. The runner rejects an existing destination record. Exact output
probabilities are deterministic; elapsed time and resource scheduling vary.
The measured sample seed is 20261022. Photonic simulated counts use NumPy
multinomial sampling of frozen ideal probabilities; Perceval contributes
the two independently evaluated probability distributions.

Replay the full-precision QI comparison separately in a fresh directory:

```sh
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export GOROROBA_WORKERS=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
PYTHONPATH=gororoba_quantum:scripts nice -n 14 timeout 120 "$PYTHON" -c '
from qi_stack import run
print(run(["scripts/local_photonic_compiler_crosscheck.py", "--qi-worker",
           "--full-precision", "--out", "results/local-simulation/fresh-fullprecision-replay"]))
'
```
