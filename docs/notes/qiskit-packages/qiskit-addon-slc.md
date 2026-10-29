# qiskit-addon-slc and pauli-prop

qiskit-addon-slc 0.2.0 (`python-qiskit-addon-slc`) lowers the sampling
overhead of probabilistic error cancellation with shaded lightcones. Errors
that fall outside an observable's backward lightcone, or whose propagated
weight on the observable is bounded small, drop out of the cancellation.
Its Rust core builds with maturin.

pauli-prop 0.2.1 (`python-pauli-prop`) supplies the Pauli propagation.
`propagate_through_circuit(operator, circuit, max_terms, atol, frame)`
evolves a `SparsePauliOp` through Pauli rotations, Clifford gates and
`PauliLindbladError` channels. With `frame="s"` it applies the Schrodinger
map U O U^dagger; with `frame="h"` it applies the Heisenberg map
U^dagger O U. It returns the truncated operator and the weight it
discarded. The host probe propagates Z through a Hadamard and returns
exactly X with discarded weight 0.0.

## Connections

- The model input comes from noise-learning fits
  ([qiskit-noise-learning](qiskit-noise-learning.md)) or Aer
  `PauliLindbladError` channels ([qiskit-aer](qiskit-aer.md)).
- samplomatic boxes define the layers that the lightcone is computed over.
- The result feeds a PEC run through qiskit-ibm-runtime. Truncation by
  `max_terms` and `atol` is an approximation that the returned discarded
  weight bounds; it is reported and never hidden.
