# gororoba-quantum

Quantum circuits whose structure comes from the open_gororoba Cayley-Dickson
algebra kernel, targeting IBM Quantum Heron backends. Left multiplication by a
basis unit is a signed permutation of the 2^k basis states, so it is unitary on
k qubits; two algebraic defects the kernel measures classically become hardware
observables.

## Contents

- `gororoba_quantum/cd_core.py` -- Cayley-Dickson sign table ported from
  cd_kernel, plus associator and zero-divisor enumeration.
- `gororoba_quantum/verify.py` -- non-circular checks against the kernel's own
  ground-truth CSV and norm multiplicativity.
- `gororoba_quantum/designs.py` -- the two circuits with ideal statevector
  outcomes.
- `gororoba_quantum/hw_estimate.py` -- routed cost and noisy prediction on a
  real backend.
- `gororoba_quantum/DESIGN_NOTES.md` -- mechanism, prediction, observable, and
  falsifier for each design.

## Designs

- Design A turns the octonion associator into a Fano Z-string read out as a
  deterministic measurement bit (3 qubits, ancilla-free).
- Design B turns a sedenion zero divisor into perfect destructive interference
  through a one-ancilla linear combination of unitaries (4 data qubits + 1
  ancilla).

## Setup

```sh
PYTHON=${PYTHON:-python3}
$PYTHON verify.py        # ground-truth checks against the kernel
$PYTHON designs.py       # ideal statevector outcomes
$PYTHON hw_estimate.py   # routed cost and noise model (needs an IBM Quantum account)
```

Dependencies: qiskit, qiskit-aer, qiskit-ibm-runtime. The IBM Quantum credential
is read from the qiskit account store (`~/.qiskit/qiskit-ibm.json`), not from
this repository. The kernel ground-truth CSV is located through `GOROROBA_ROOT`
(default `~/Github/open_gororoba`); `verify.py` needs that checkout, the circuit
modules do not.
