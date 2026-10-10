# gororoba-quantum

Quantum circuits whose structure comes from the open_gororoba Cayley-Dickson
algebra kernel, targeting IBM Quantum Heron backends. Left multiplication by a
basis unit is a signed permutation of the 2^k basis states, so it is unitary on
k qubits; two algebraic defects the kernel measures classically become hardware
observables.

## Contents

- `gororoba_quantum/cd_core.py` -- Cayley-Dickson sign table ported from
  cd_kernel, plus associator and zero-divisor enumeration.
- `gororoba_quantum/verify.py` -- fail-closed checks: the sign tensor against the
  kernel's hash-pinned multiplication tables, the zero-divisor corpus against
  the kernel CSV, norm multiplicativity, and the phase-degree rules along the
  ladder.
- `gororoba_quantum/boolean_anf.py` and `modular_arithmetic.py` -- exact Boolean
  coefficient extraction and controlled modular-permutation synthesis through
  Mersenne rotations, ANF networks, or scratch-free cycle transpositions.
- `gororoba_quantum/factoring.py`, `order_finding.py`, and `hybrid_shor.py` --
  classical admission and decoding around faithful `|1>` semiclassical order
  finding, plus a credential-free plan, simulation, and decode CLI.
- `gororoba_quantum/FACTORING_NOTES.md` -- what Cayley-Dickson structure can and
  cannot contribute to Shor's algorithm, against the RSA-2048 resource floor.
- `gororoba_quantum/HYBRID_SHOR.md` -- host/QPU boundary, coefficient
  derivations, bounded hardware frontier, evidence levels, falsifiers, and the
  roadmap beyond `N = 15`.
- `gororoba_quantum/HARDWARE_PLAN.md` -- the joint submission plan for every
  experiment group: claims and falsifiers, calibration-to-circuit pipeline,
  deciding statistics, QPU cost, and the path to the first submission.
- `gororoba_quantum/packing.py` and `variance.py` -- disjoint replica placement
  and packing of compiled circuits, and the shot, layout, and instance
  variance decomposition with replicate intervals.
- `gororoba_quantum/select_lcu.py` -- the ancilla-selected left multiplication
  (one joint sign diagonal, X, CX) and sparse pair-state preparation.
- `gororoba_quantum/predict.py` -- every algebraic prediction, from cd_sign and
  cd_multiply; no circuit builder imports it.
- `gororoba_quantum/designs.py` -- the four designs, checked by statevector and
  operator equality over every instance.
- `gororoba_quantum/experiments.py` -- experiment groups: a primary circuit, its
  controls, their ideals, and the summary of each design's observable.
- `gororoba_quantum/live_run.py` -- live system discovery, circuit-derived
  capability admission, degraded-hardware-filtered routing, recursive Target
  validation, ESP-and-coherence-ranked selection, disjoint replica placement,
  stable-pass cross-system reselection, local noise simulation, gated
  client-side Sampler submission, and execution-time replay.
- `gororoba_quantum/runtime_contracts.py` -- credential-free checks for packed
  static and dynamic circuits, capability and routing admission, recursive
  Target support, coherent calibration snapshots, final execution-set job-batch
  partitioning, every-batch revalidation, submission recovery, archive
  integrity, per-replica result order, twirling shots, and source-manifest
  stability.
- `gororoba_quantum/DESIGN_NOTES.md` -- mechanism, prediction, observable, and
  falsifier for each design, and the live-calibration policy.
- `results/live/<UTC start>/` -- retained JSON and QPY evidence. Schema 4
  combines live capability admission and submission recovery with packed
  replicas, variance, crosstalk, and statistical admission. Earlier schemas
  remain historical evidence under `results/live/README.md`.
- `results/hw_estimate/` -- the fixed ibm_fez compile behind the design
  sections' "Measured" figures.

## Designs

- Design A turns the octonion associator into a Fano Z-string read out as a
  deterministic measurement bit (3 qubits, ancilla-free).
- Design B turns a sedenion zero divisor into perfect destructive interference
  through a one-ancilla linear combination of unitaries (4 data qubits + 1
  ancilla), compiled to 46 CZ on ibm_fez.
- Design C measures the Walsh spectrum of the associator phase at dims 8, 16,
  and 32, with sign-flip and omitted-block controls.
- Design D sweeps the relative phase of design B's input and fits offset,
  visibility, and phase of the (1 - s cos phi)/2 fringe.

## Setup

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
cd gororoba_quantum
"$PYTHON" verify.py
"$PYTHON" designs.py
"$PYTHON" factoring.py
"$PYTHON" modular_arithmetic.py
"$PYTHON" order_finding.py
"$PYTHON" runtime_contracts.py
"$PYTHON" hybrid_shor.py plan 15
"$PYTHON" hybrid_shor.py simulate 15 --shots 256 --seed 7
"$PYTHON" live_run.py --out ../results/live
```

The final command reads live calibration and performs local compilation and
noise simulation. It omits `--submit` and sends zero quantum jobs. Every
`live_run.py --submit` invocation requires the written case and immediate user
approval specified in `AGENTS.md`.

requirements.txt pins the tested numpy, qiskit, qiskit-aer, and
qiskit-ibm-runtime versions. The modules run as scripts from gororoba_quantum/,
which puts their sibling imports on sys.path; they form no installable package,
and pyproject.toml carries only lint and type-check configuration. The IBM Quantum credential
is read from the qiskit account store (`~/.qiskit/qiskit-ibm.json`), not from
this repository. The kernel ground-truth CSV is located through `GOROROBA_ROOT`
(default `~/Github/open_gororoba`); `verify.py` needs that checkout, the circuit
modules do not.
