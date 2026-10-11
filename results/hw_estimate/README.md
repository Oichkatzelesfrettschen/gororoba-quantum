# Static compiler evidence

The directory contains compiler and local-simulation records. Every record sets
`qpu_executed` to `false`; none supplies live calibration or hardware evidence.

- `ibm_fez_record.json` and `ibm_fez_isa.qpy` retain the fixed calibrated
  compile used by the design documents.
- `hybrid_shor_fake_fez.json` retains the original single-seed ANF-versus-cycle
  comparison. Its recorded source commits preserve the historical circuit
  definitions, so later captures never overwrite it.
- `n21_heavy_hex_mcx_workspace.json` uses schema 2 and records the reproducible
  eight-seed scratch-free, one-clean, two-clean, and ANF comparison. The record
  includes the complete FakeFez coupling graph, source hashes, logical and physical
  layouts, aggregate-resource pass transitions, named stage snapshots, and
  summary ranges. Each transition marks a change in qubit count, recursive
  depth, or recursive operation census; the transition list is not a full
  structural digest.

- `n21_target_flip_compilation.json` captures eight seeds of the exact
  Boolean target-flip circuit at ten-bit phase precision.
- `n21_target_flip_precision5.json` captures the same exact arithmetic
  at five-bit precision; the shorter circuit has a distinct decoder law.

- `n21_target_flip_proof_verification.json` and `n21_target_flip_proof/`
  retain fresh kernel checks, assumption output, and failed mutations.
- `n21_target_flip_ideal_simulation.json` retains credential-free five-bit
  Aer sampling and exact decoder output.
- `n21_cross_project_proof_audit.json` binds the selected fresh
  open_gororoba source proof audit.
- `mod15_signed_multiplier_census.json` retains the unitary checks, ideal
  order-finding yield, and eight-seed FakeFez compile of one controlled
  multiplier for each nonidentity unit modulo 15.

Both target-flip captures bind the source generator and finite Rocq
certificate. `gororoba_quantum/MODULAR_SYNTHESIS.md` gives replay commands
and keeps compiler evidence separate from physical admission.

The full crossover capture runs from the repository root:

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
"$PYTHON" gororoba_quantum/compile_evidence.py \
  --out results/hw_estimate/n21_heavy_hex_mcx_workspace.json
```

The capture uses the static `FakeFez` target, performs local compilation, and
submits zero Runtime jobs.
