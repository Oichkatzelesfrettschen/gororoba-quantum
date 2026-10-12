# N21 native Qiskit shared-predicate evidence

The probe reduces repeated scratch computation in the controlled multipliers
for the N21 two-bit feed-forward diagnostic. The candidate uses installed
Qiskit gates and `synth_mcx_1_clean_kg24`. Dynamic programming selects signed
common data-control pivots across adjacent target-flip cubes. A shared outer
RCCX computes the scratch predicate once per compatible group; a matching
RCCX restores scratch at the end. The target-flip word remains unchanged.

`result.json` records relative source hashes, checkout HEAD and status before
and after computation, before the report write, Python and Qiskit versions, source operation counts, and
phase-sensitive complex operator comparisons. Each comparison covers all
32 data values and both phase-control values with scratch initialized to zero.
The expected permutation comes independently from integer modular
multiplication, with data values 21 through 31 fixed. The comparison therefore
covers the full data register, beyond the three-state orbit of the diagnostic.

| Multiplier | Shared boundaries | RCCX before / after | Unrouted CX before / after | Depth before / after |
|---|---|---|---|---|
| 4 | 8 | 50 / 34 | 243 / 204 | 528 / 425 |
| 16 | 8 | 50 / 34 | 243 / 204 | 531 / 412 |

Both source circuits reduce X gates from 68 to 52 and retain 17 CCX gates.
The maximum controlled-permutation error, baseline operator difference, and
scratch leakage each equal 0.0 in the recorded floating-point computation.
The unrouted counts use native Qiskit optimization level 3, the
`cx/rz/sx/x` basis, and transpiler seed 20261010.

## Replay

Run from the repository root and select a new output filename. The probe opens
its output exclusively, so an existing result remains intact. Preserve the
historical `result.json`; differing source or library versions supply a new
measurement whose hashes and versions require comparison.

```sh
set -eu
PYTHON="${PYTHON:-$(command -v python3)}"
probe_output="n21-shared-predicate-replayed.json"
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" \
  results/local_compute/n21_shared_predicate/probe.py \
  --source-root . --output "$probe_output"
```

The script records eight dependency/source hashes and rejects a change in
those hashes, HEAD, or checkout status during computation. The executing
probe has a separate digest captured before external imports and computation;
the script compares that digest immediately before opening the new report
and records the captured value. The observations establish equal source bytes
at the two checks; an intervening edit followed by restoration lies outside
that boundary.

`result.json` remains the historical report. `historical_probe.py.gz` preserves
the source bytes whose decompressed SHA-256 matches the report's
`probe_sha256`, `84d4b4839e62f4310cfc574254d04e2f96a4e87706bbe4dbe9411ac93ef3e5e9`.
The historical probe computed that digest after the experiment; its record
does not establish equality with probe bytes at startup. The archive preserves
the bytes matching that post-run observation. The archive uses gzip timestamp
zero. The repaired `probe.py` adds the early
digest capture and final comparison; that transformation changes provenance
checks while retaining the native multiplier computation and exclusive output
write. Fresh reports bind the repaired script instead of rewriting historical
evidence.

The regression runs the native operator and transpilation checks from a
temporary probe copy, edits that copy during its first transpilation, and
requires the source guard to reject report creation. An unchanged run must
reproduce the retained multiplier results, and a repeated output path must
preserve its existing bytes. Run both interpreter modes:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONWARNINGS=error "$PYTHON" \
  results/local_compute/n21_shared_predicate/check_probe.py
PYTHONDONTWRITEBYTECODE=1 PYTHONWARNINGS=error PYTHONOPTIMIZE=1 "$PYTHON" \
  results/local_compute/n21_shared_predicate/check_probe.py
```

`SHA256SUMS` binds the scripts, historical source archive, report, and note:

```sh
(cd results/local_compute/n21_shared_predicate && sha256sum -c SHA256SUMS)
```

## Limits and next admission gate

The candidate remains an exploratory in-memory construction. Production
synthesis retains the existing implementation. The bounded operator
computation supplies numerical evidence, not a formal proof. The endpoint
checks bind the transformation to the observed native KG24 structure. The
scratch contract requires an initial zero.

The reported counts omit physical connectivity, routing, scheduling,
calibrated noise, and classical feed-forward latency. The probe establishes
neither N21 statistical admission nor hardware accuracy. Production admission
requires a reviewed implementation, full-register and mutation tests, matched
routed compilation, and fresh CPU Aer noise evaluation. QPU submission retains
the separate user-approval requirement.

The probe constructs no IBM service, submits no jobs, and performs no Aer shot
simulation. The probe builds and installs no system packages.
