# Installed Qiskit-adjacent packages: surfaces, roles and interconnections

This directory documents the Qiskit-adjacent distributions installed on the
build host beyond the pinned core of [requirements.txt](../../../requirements.txt).
Each package has one note here giving its use case, install surface, its
connections to the other installed packages, and its caveats.
[qiskit-ecosystem.md](../qiskit-ecosystem.md) remains the survey and
recommendation authority for the wider ecosystem, and
[python-stack.md](../build_host/python-stack.md) lists the Arch packages and
the pins they carry. Every package below is installed from a PKGBUILD in
`~/Github/PKGBUILDs`. Installation creates no credential, contacts no
provider and submits no job. A provider call made through any of these
packages follows the approval rules of [AGENTS.md](../../../AGENTS.md).

## Install surfaces

Python 3.14 and the core qiskit 2.6.1, qiskit-ibm-runtime 0.51.0 and
qiskit-aer 0.18.2 live on the system interpreter. A package whose
requirements cannot coexist with that core lives in a hash-locked
environment under `/opt`, reached through its launcher.

| Surface | Interpreter | Core it carries | Packages |
|---|---|---|---|
| system, `$PYTHON` | Python 3.14 | qiskit 2.6.1, runtime 0.51.0, Aer 0.18.2 (CUDA build) | [qiskit-aer](qiskit-aer.md), [ibm-quantum-schemas](ibm-quantum-schemas.md), [qiskit-noise-learning](qiskit-noise-learning.md), [pauli-prop and qiskit-addon-slc](qiskit-addon-slc.md), [qiskit-serverless and qiskit-ibm-catalog](qiskit-functions.md), [qiskit-connector](qiskit-connector.md), [qiskit-resume](qiskit-resume.md), [qiskit-waveform-sim](qiskit-waveform-sim.md), [qcog](qcog.md), [qubasic](qubasic.md), [eigenkit](eigenkit.md), [quantum-al](quantum-al.md), [perceval-quandela and perceval-interop](perceval-interop.md) |
| `quantuminspire-qiskit-stack`, `qi-stack-python` | Python 3.13 | qiskit 2.3.0, Aer 0.17.2 | [quantuminspire, qiskit-quantuminspire, pennylane-quantuminspire](quantum-inspire-family.md) |
| `qiskit-debugger-stack`, `qiskit-debugger-python` | Python 3.11 | qiskit 0.43.2 (terra 0.24.1), Aer 0.12.1 | [qiskit-debugger](qiskit-debugger.md) |
| `quantum-pipeline-stack`, `quantum-pipeline-python` | Python 3.13 | qiskit 2.6.1, runtime 0.51.0, Aer 0.17.2 | [quantum-pipeline](quantum-pipeline.md) |

Each package's placement follows from one requirement:

- The Quantum Inspire family requires Python below 3.14. pennylane-qiskit,
  which pennylane-quantuminspire requires, caps qiskit at 2.3.0.
- qiskit-debugger pins `qiskit==0.43.2`. It imports `qiskit.Aer` and
  `qiskit.execute`, both of which Qiskit 1.0 removed.
- quantum-pipeline caps qiskit-aer below 0.18.
- qiskit-serverless 0.37.0 caps qiskit-ibm-runtime below 0.51 and pins
  cloudpickle, zipp, certifi and ipython to its Ray image. Its system
  package relaxes those pins (Open item 1).

## How the packages connect

The diagram below links each package to the installed packages it depends
on, as recorded in each distribution's `requires_dist` and in its imports.
An arrow `A -> B` means that A imports B at run time.

```text
                        qiskit 2.6.1  (circuits, transpiler, quantum_info, qpy, qasm3)
      ┌──────────────┬────────┼───────────────┬──────────────────┬──────────────┐
  qiskit-aer 0.18.2  samplomatic 0.21  qiskit-qasm3-import   rustworkx      numpy/scipy
      │   ▲               │  ▲  ▲            │
      │   │               │  │  └── ibm-quantum-schemas ── pydantic
      │   │               │  └───── qiskit-noise-learning ── xarray
      │   │               └──────── qiskit-addon-slc ── pauli-prop ── qiskit-aer
      │   │
      │   ├── qcog, qubasic, eigenkit (optional), quantum-al (optional)
      │
  qiskit-ibm-runtime 0.51.0 ── ibm-quantum-schemas, samplomatic, qiskit-mitigation
      ├── qiskit-serverless 0.37.0 ── qiskit-ibm-catalog 0.21.0
      ├── qiskit-connector 2.4.6
      └── eigenkit (optional IBM backend)

  qiskit-resume 0.2.1 ── qiskit primitives base classes (wraps any SamplerV2/EstimatorV2:
                          Aer, runtime executor_sampler, StatevectorSampler)
  qiskit-waveform-sim 0.3.0 ── qiskit Target timings, qasm3, BoxOp annotations
  perceval-interop 1.3.1 ── perceval-quandela 1.3.1 ── exqalibur; optional qiskit, qutip, myqlm, libqasm
```

The packages fall into five roles:

1. **Execution and simulation.** qiskit-aer runs every simulator primitive:
   `AerSimulator`, the Aer `SamplerV2` and `EstimatorV2`, and noise models.
   qcog, qubasic, quantum-pipeline and pauli-prop all execute through it.
   qiskit-resume wraps the primitive layer, whichever backend sits under it.
2. **IBM platform payloads and clients.** ibm-quantum-schemas holds the
   pydantic wire models that qiskit-ibm-runtime 0.51 serializes.
   qiskit-serverless and qiskit-ibm-catalog reach IBM Qiskit Functions.
   qiskit-connector selects the least-busy backend through
   `QiskitRuntimeService`.
3. **Noise characterization and mitigation.** samplomatic builds the boxed,
   twirled templates. qiskit-noise-learning fits Pauli-Lindblad noise models
   to experiments built on them. qiskit-addon-slc uses pauli-prop's Pauli
   propagation to restrict PEC sampling to a shaded lightcone. These
   packages complement qiskit-mitigation and mthree, which correct readout
   and expectation values after the run.
4. **Timing and inspection.** qiskit-waveform-sim draws control waveforms
   from a `Target`'s instruction durations, a view that replaces the pulse
   schedules IBM removed on 3 February 2025. qiskit-debugger steps through
   a circuit under the legacy Qiskit 0.43 API.
5. **Cross-framework and cross-provider bridges.**
   - perceval-interop converts between Perceval and Qiskit circuits for the
     Quandela photonic route.
   - The Quantum Inspire family takes a Qiskit or PennyLane circuit to cQASM 3
     for Tuna-17.
   - eigenkit and quantum-al build algorithms on Qiskit's primitives.

## Verification

[probe_packages.py](probe_packages.py) imports every system package, checks
one exact local result where a package computes offline, and with
`--stacks` reads the versions through the three `/opt` launchers
(`"$PYTHON" docs/notes/qiskit-packages/probe_packages.py --stacks`). It
constructs no service and reads no credential. It reads qiskit-connector
from metadata only, because importing that package loads `.env` files. The
run that preceded the core upgrade imported all seventeen system packages
and recorded these results:

| Probe | Result |
|---|---|
| pauli-prop, Heisenberg propagation of Z through H | X, discarded weight 0.0 |
| qiskit-waveform-sim, ALAP-scheduled X on FakeFez qubit 0 | 6 samples at dt 4 ns, equal to the Target's 24 ns X; envelope DRAG with placeholder amplitude 0.9 |
| perceval-interop, Qiskit H-CX circuit | 4-mode Perceval processor |
| qiskit-aer, `AerSimulator().available_devices()` | `('CPU', 'GPU')` |
| `qi-stack-python` | qiskit 2.3.0, qiskit-quantuminspire 0.18.6, pennylane-quantuminspire 0.15.6, quantuminspire 4.2.0 |
| `qiskit-debugger-python` | qiskit 0.43.2, qiskit-terra 0.24.1, qiskit-aer 0.12.1, qiskit-debugger 0.1.2 |
| `quantum-pipeline-python` | qiskit 2.6.1, qiskit-aer 0.17.2, qiskit-ibm-runtime 0.51.0, quantum-pipeline 2.5.1 |

Each stack package also runs its own offline tests in `check()`.
`uv pip check` reports every dependency compatible in the three user
environments: `QI_ENV`, the Open Quantum venv, and the Qiskit skills
validation venv.

Packaging fixes that the probes forced:
- **perceval-interop (pkgrel 3).** It defines its myQLM fallback name, so
  the package imports without myQLM. It also takes its version from the
  release, because scmver reports 0.0.0 from an sdist without git metadata.
- **Quantum Inspire stack.** qiskit drops from 2.3.1 to 2.3.0, which
  pennylane-qiskit requires.

## Open items

The plan record [qiskit-package-graph](../../state/plans/qiskit-package-graph.json)
tracks each open item as a step with its acceptance condition:

1. `catalog-call-runtime-051`: one `QiskitFunctionsCatalog.list()` call
   under the relaxed qiskit-serverless pins and runtime 0.51.0, inside an
   approved case. A serverless release that admits runtime 0.51 retires
   the relaxation.
2. `interop-qiskit-261`: rerun the perceval-interop converter probe on
   qiskit 2.6.1. The upstream extra pins `qiskit~=2.1.2`.
3. `debugger-stack-retire`: the qiskit-debugger stack retires when an
   upstream release supports Qiskit 2.x or the package is dropped.
4. `qi-qiskit-ceiling`: the Quantum Inspire stack's qiskit 2.3.0 ceiling
   lifts when pennylane-qiskit and qiskit-quantuminspire admit a newer
   qiskit.
5. `pipeline-aer-018`: quantum-pipeline moves to Aer 0.18 when a release
   lifts its `qiskit-aer<0.18` cap. It depends on the archived qiskit-nature.
6. `missing-package-block`: the request that produced this directory named
   a further block of packages that did not reach the session. This step
   closes when that block is installed and documented here.
