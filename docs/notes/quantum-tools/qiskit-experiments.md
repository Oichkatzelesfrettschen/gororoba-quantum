# qiskit-experiments

## NAME

qiskit-experiments 0.14.2 -- calibration, characterization and benchmarking
experiments with curve-fit analysis (T1, T2, RB, readout, tomography).

## SYNOPSIS

```python
from qiskit_experiments.library import LocalReadoutError, StandardRB, T1
exp = T1([0], delays=[1e-6, 1e-4, 3e-4])          # delays in seconds
data = exp.run(backend, shots=1000, seed_simulator=1).block_for_results()
data.analysis_results(dataframe=True)            # name / value / quality table
```

Run every script that calls `.run(...)` under `if __name__ == "__main__":`.

| Substrate | Status |
| --- | --- |
| Build host | python-qiskit-experiments 0.14.2 (Arch) |
| Kaggle | `qiskit-experiments==0.14.2` in the `quantum-tools` group; unmeasured on a kernel |

## CAPABILITIES IN THIS REPOSITORY

- Readout error: `LocalReadoutError(qubits)` measures the per-qubit assignment
  matrices (2 x 2 each) and `CorrelatedReadoutError` the full 2^n matrix; the
  analysis result `Local Readout Mitigator` exposes `assignment_matrix([q])`
  and `quasi_probabilities(counts)`. That is the readout-factor measurement
  `1 - P(1|0) - P(0|1)` per qubit as an experiment object; compare
  [mthree.md](mthree.md), which applies the same matrices matrix-free.
- Relaxation and dephasing against the retained calibration: `T1`,
  `T2Ramsey`, `T2Hahn`, `Tphi` fit exponential and damped-oscillation models
  (`curve_analysis`); on the density-matrix replay `T1` recovers the Target
  T1 (example). The replay noise model relaxes idle `delay` instructions, so
  delay experiments are meaningful offline.
- Gate quality: `StandardRB`, `InterleavedRB`, `PurityRB`, `LayerFidelity`
  fit EPC and EPG from Clifford sequences; the example recovers the order of
  the Target's sx error. They sample Clifford sequences and so exercise the
  Qiskit `Clifford` path ([stim.md](stim.md) simulates Clifford circuits in
  the stabilizer formalism).
- State and process tomography: `StateTomography`, `ProcessTomography` and the
  `MitigatedStateTomography` and `MitigatedProcessTomography` variants (listed
  in the library; not run here), for small registers (3^n measurement bases),
  the density-matrix reconstruction behind the coherence settings listed in the
  root AGENTS.md.
- Not covered: pulse-level calibration experiments (IBM removed pulse-level
  control on 3 February 2025; `FineDrag` and `FineSXDrag` appear in the
  library and were not run) and device queries. Running an
  experiment on an IBM backend submits jobs and needs the approved-case flow of
  the root AGENTS.md; this manual runs only against Aer.

## API ENTRY POINTS

`qiskit_experiments.library` public names (33), by introspection:

classes:

```text
  CorrelatedReadoutError, FineAmplitude, FineDrag, FineFrequency,
  FineSXAmplitude, FineSXDrag, FineXAmplitude, FineXDrag, HalfAngle,
  InterleavedRB, LayerFidelity, LayerFidelityUnitary, LocalReadoutError,
  MitigatedProcessTomography, MitigatedStateTomography,
  MultiStateDiscrimination, ProcessTomography, PurityRB, QuantumVolume,
  RamseyXY, ReadoutAngle, StandardRB, StateTomography, T1, T2Hahn, T2Ramsey,
  TomographyExperiment, Tphi, ZZRamsey
```

modules:

```text
  characterization, quantum_volume, randomized_benchmarking, tomography
```

Framework classes:

`qiskit_experiments.framework` public names (59), by introspection:

classes:

```text
  AnalysisCallback, AnalysisConfig, AnalysisResult, AnalysisResultData,
  AnalysisResultTable, AnalysisStatus, ArtifactData, BackendData,
  BackendTiming, BaseAnalysis, BaseExperiment, BaseJob, BaseProvider,
  BasicExperiment, BatchExperiment, CompositeAnalysis, CompositeExperiment,
  ExperimentConfig, ExperimentData, ExperimentDecoder, ExperimentEncoder,
  ExperimentService, ExperimentStatus, ExtendedJob, FigureData, MeasLevel,
  MeasReturnType, Options, ParallelExperiment, TiledExperiment
```

Curve analysis:

`qiskit_experiments.curve_analysis` public names (22), by introspection:

classes:

```text
  BaseCurveAnalysis, BlochTrajectoryAnalysis, CompositeCurveAnalysis,
  CurveAnalysis, CurveFitResult, DampedOscillationAnalysis, DecayAnalysis,
  ErrorAmplificationAnalysis, FitOptions, GaussianAnalysis,
  OscillationAnalysis, ParameterRepr, ScatterTable
```

modules:

```text
  base_curve_analysis, composite_curve_analysis, curve_analysis, curve_data,
  fit_function, guess, scatter_table, standard_analysis, utils
```

## EXAMPLES

### Readout assignment matrices against the snapshot

```python
import json, sys
sys.path.insert(0, "gororoba_quantum")
import calibration_snapshot as cs
from qiskit_experiments.library import LocalReadoutError


def main():
    snap = json.load(open("docs/evidence/calibration/ibm_kingston.json"))
    sim = cs.noise_simulator(snap)
    data = LocalReadoutError([0, 1]).run(sim, shots=20000, seed_simulator=3).block_for_results()
    mit = data.analysis_results("Local Readout Mitigator", dataframe=True).iloc[0].value
    for k in (0, 1):
        a = mit.assignment_matrix([k])
        q = snap["qubits"][k]
        print(f"qubit {k}: measured P(1|0)={a[1, 0]:.4f} P(0|1)={a[0, 1]:.4f} factor={a[0, 0] + a[1, 1] - 1:.4f}"
              f"   snapshot e10={q['e10']:.4f} e01={q['e01']:.4f} factor={1 - q['e10'] - q['e01']:.4f}")
    quasi = mit.quasi_probabilities({"00": 9000, "01": 600, "10": 200, "11": 200})
    print("mitigated quasi-probabilities of 9000/600/200/200:", {k: round(float(v), 5) for k, v in quasi.items()})


if __name__ == "__main__":  # qiskit-experiments analysis starts spawn workers that re-import this file
    main()
```

Output:

```text
qubit 0: measured P(1|0)=0.0036 P(0|1)=0.0149 factor=0.9814   snapshot e10=0.0037 e01=0.0146 factor=0.9817
qubit 1: measured P(1|0)=0.0029 P(0|1)=0.0057 factor=0.9913   snapshot e10=0.0039 e01=0.0061 factor=0.9900
mitigated quasi-probabilities of 9000/600/200/200: {0: 0.90496, 1: 0.05767, 2: 0.0172, 3: 0.02018}
```

### Randomized benchmarking and T1 on the replay noise

```python
import json, sys, warnings
sys.path.insert(0, "gororoba_quantum")
import calibration_snapshot as cs
from qiskit_experiments.library import StandardRB, T1


def main():
    warnings.filterwarnings("ignore")
    snap = json.load(open("docs/evidence/calibration/ibm_kingston.json"))
    sim = cs.noise_simulator(snap)
    rb = StandardRB([0], lengths=[1, 300, 900, 1800], num_samples=5, seed=11)
    res = rb.run(sim, shots=500, seed_simulator=11).block_for_results()
    df = res.analysis_results(dataframe=True)
    print(df[["name", "value", "quality"]].to_string(index=False))
    sx = [r for r in snap["instructions"]["sx"] if r["qargs"] == [0]][0]
    print("snapshot sx error on q0:", sx["error"])

    t1 = snap["qubits"][0]["t1"]
    delays = [d * 1e-6 for d in (1, 100, 300, 600, 1000)]
    res = T1([0], delays=delays).run(sim, shots=1000, seed_simulator=11).block_for_results()
    df = res.analysis_results(dataframe=True)
    print(df[["name", "value", "quality"]].to_string(index=False))
    print("snapshot T1 on q0 (us):", round(t1 * 1e6, 1))


if __name__ == "__main__":
    main()
```

Output:

```text
  name             value quality
 alpha 0.99930+/-0.00010    good
   EPC 0.00035+/-0.00005    good
EPG_sx 0.00042+/-0.00006    good
EPG_rz           0.0+/-0    good
 EPG_x 0.00042+/-0.00006    good
snapshot sx error on q0: 0.0004725667427331994
name               value quality
  T1 0.000298+/-0.000013    good
snapshot T1 on q0 (us): 313.2
```

## INTEROP WITH QISKIT

Verified with qiskit 2.5.2 and qiskit-aer 0.17.2: every experiment above ran
on `calibration_snapshot.noise_simulator(snapshot)` (a density-matrix
`AerSimulator` built `from_backend` on a 156-qubit Target), which is a
`BackendV2`. Experiments transpile to the Target, so each run spends seconds
to tens of seconds before simulation. IBM backends accept the same objects;
that path was not run.

## CPU AND GPU

Analysis runs on the CPU (`curve_analysis`, SciPy-based fitting); the
simulation is whatever the backend does. `noise_simulator(snapshot,
device="GPU")` moves the density-matrix step to the GPU; 1- and 2-qubit
experiments gain nothing from it.

## TRAPS

- Analysis starts worker processes with the spawn start method. A script
  without the `__main__` guard re-executes at import in each worker and
  prints its output twice (observed during this work).
- `ExperimentData.analysis_results()` without `dataframe=True` raises a
  `DeprecationWarning` and returns the legacy list; use `dataframe=True`.
- `T1(physical_qubits, delays)` takes seconds and has no `unit=` argument
  (`TypeError: T1.__init__() got an unexpected keyword argument 'unit'`).
- The retained snapshot Target reports `granularity` 1 and `min_length` 1, so
  delay rounding is fine; the live Target's timing constraints (root AGENTS.md)
  are the authority for hardware.
- Quality labels (`good`) judge the fit, not agreement with the calibration.
  The example's `EPG_sx` (0.00042 +/- 0.00006) is the quantity to compare with
  the Target's sx error (0.00047); `EPC` is per Clifford and is not.
- The `rz` virtual gate carries zero error, so RB on qubits with only rz
  structure reports `EPG_rz = 0.0+/-0`.

## LICENSE

Apache-2.0.
