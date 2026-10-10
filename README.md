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
- `gororoba_quantum/order_finding.py` -- semiclassical phase estimation of x -> 2x
  mod 15 on its eigenstates: mid-circuit measurement, reset, and feed-forward.
- `gororoba_quantum/FACTORING_NOTES.md` -- what Cayley-Dickson structure can and
  cannot contribute to Shor's algorithm, against the RSA-2048 resource floor.
- `gororoba_quantum/select_lcu.py` -- the ancilla-selected left multiplication
  (one joint sign diagonal, X, CX) and sparse pair-state preparation.
- `gororoba_quantum/predict.py` -- every algebraic prediction, from cd_sign and
  cd_multiply; no circuit builder imports it.
- `gororoba_quantum/designs.py` -- the four designs, checked by statevector and
  operator equality over every instance.
- `gororoba_quantum/experiments.py` -- experiment groups: a primary circuit, its
  controls, their ideals, and the summary of each design's observable.
- `gororoba_quantum/live_run.py` -- live calibration across every accessible
  backend: exclusion policy, ESP-ranked backend and layout selection, noise
  simulation from the same Target, gated submission through the client-side
  Sampler, and replay at the execution-time calibration.
- `gororoba_quantum/DESIGN_NOTES.md` -- mechanism, prediction, observable, and
  falsifier for each design, and the live-calibration policy.
- `results/live/<UTC start>/` -- one audit record per run: the chosen ISA
  circuits (QPY) and the JSON of backend states, exclusions, selection trace,
  and noisy outcomes.
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
PYTHON=${PYTHON:-python3}
cd gororoba_quantum
$PYTHON verify.py        # ground-truth checks against the kernel; nonzero exit on failure
$PYTHON designs.py       # statevector checks over every instance
$PYTHON order_finding.py # exact checks of the folded order-finding circuits
$PYTHON live_run.py --out ../results/live   # live calibration, selection, noise model (IBM Quantum account)
$PYTHON live_run.py --out ../results/live --submit             # the same, then submit (spends QPU time)
$PYTHON live_run.py --collect ../results/live/<UTC start>      # measured vs execution-time calibration
```

requirements.txt pins the tested numpy, qiskit, qiskit-aer, and
qiskit-ibm-runtime versions. The modules run as scripts from gororoba_quantum/,
which puts their sibling imports on sys.path; they form no installable package,
and pyproject.toml carries only lint and type-check configuration. The IBM Quantum credential
is read from the qiskit account store (`~/.qiskit/qiskit-ibm.json`), not from
this repository. The kernel ground-truth CSV is located through `GOROROBA_ROOT`
(default `~/Github/open_gororoba`); `verify.py` needs that checkout, the circuit
modules do not.
