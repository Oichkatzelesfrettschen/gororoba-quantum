# Box-kite case generator: handoff

`scripts/box_kite_cases.py` generates family (a) of
[experiment-program.md](experiment-program.md) for the QX emulator (backend
type 1, 10 qubits, 2048 shots) from `docs/evidence/box_kite_census/census.json`.

## Done

- Census reading and checks: `load_census`, `census_rows`, `pair_phases`
  (g(L,L') = (c0 + d0)/2, g(U,U') = s t (c0 - d0)/2, g(L,U') = t (c1 + d1)/2,
  g(U,L') = s (c1 - d1)/2), and `validate_census`, which checks phase
  agreement across the four sign rows of a pair, the kite sign products, the
  edge zero_signs and strut P = 1/2, P and 1 - P from the coefficients, the
  coherences, the row counts and four-label rows. No sign comes from cd_core.
- Builders:
  - `full_design_b` wraps `designs.lcu_witness` and inserts a Z after the
    selector's first H when x_sign = -1.
  - `two_label_select` uses local Z gates, then CNOT; when the phase product
    is -1 it uses Sdag(d), CNOT, S(d), Sdag(a).
  - `reduced_lcu`.
  - `reduced_cross_control` uses an identity diagonal, then CNOT(a->d) and
    CNOT(a->w). The census carries no phases for four-label rows.
- Checks before emission:
  - `check_select` compares each SELECT unitary to its two-label restriction,
    global phase included.
  - `check_amplitudes` requires the full Design B state from lcu_witness to
    reproduce c0, c1, d0, d1 / (2 sqrt2), and the selector P to match the
    census.
  - `verify_circuit` parses every emitted .cq back and requires each packed
    selector's marginal to equal its census P.
  - All three run through `parallel.ordered_map`.
- `emit(circuit, place, dialect="qx")` writes cQASM 3.0. Rz angles snap to
  multiples of pi/64, and full Design B compiles at optimization level 0.
  `parse_cqasm` reads the output back.
- `pack` places 2 full, 5 reduced or 3 cross-kite replicas per circuit.
- `qx_backend` handles catalogue admission.
- `finish` writes batches of at most `HARDWARE_BATCH_CIRCUITS` = 3 circuits,
  one sub-family per batch, named batch-000 onward.
- `validate_series`, `series("a", "qx")`, and `--write`, `--check` and
  `--self-test`.

## Stubbed, not started

The following belong to a later pass: families (d) and (e)
(`associator_walk`, `controlled_w_*`, `coherence_settings`),
`ry_diagnostic_ladder`, the tuna and ry dialects (`DIALECTS` holds only
"qx"), `twin()`, `analyze`, and `replay`.

## Generated cases

The cases were written to `results/quantum_inspire/cases/box_kite_a_qx/`:
1133 files, 7.0 MB, 284 batches and 848 circuits.

| Sub-family | Replicas | Circuits | Batches |
|---|---|---|---|
| full_within_kite | 840 | 420 | 140 |
| reduced_within_kite | 840 | 168 | 56 |
| full_cross_kite (with fixture) | 169 | 85 | 29 |
| reduced_cross_kite (with fixture) | 169 | 57 | 19 |
| full_nonkite | 168 | 84 | 28 |
| reduced_nonkite | 168 | 34 | 12 |

The series has 1010 P = 1/2 replicas. Batches hold 3 circuits rather than the
5 that section 5 of the program assumes, so the program's batch column (84,
34, 17, 12, 17, 7) needs updating to 140, 56, 29, 19, 28, 12.
`check_qi_platform_retention.py` asserts this cap on every manifest.

## Checks

| Check | Result |
|---|---|
| `--write results/quantum_inspire/cases` | `box-kite cases: 1133 files written` |
| `--check results/quantum_inspire/cases` (normal) | `box-kite cases: 1133 files match their regeneration` |
| `--self-test` (normal and `-O`) | `... contracts pass; 21 mutations rejected` |
| `check_qi_platform_retention.py` (normal) | `Ran 45 tests in 206.014s` / `OK` |
| `uvx ruff@0.14.11 check`, `format --check` | `All checks passed!`, `1 file already formatted` |
| `mypy ../scripts/box_kite_cases.py` (from gororoba_quantum/) | `Success: no issues found in 1 source file` |
| `--check` under `-O` | not run (host shutdown) |
| `GOROROBA_WORKERS=1 --check` (serial equals pooled) | not run (host shutdown) |
| `check_qi_platform_retention.py -O` | not run (host shutdown) |

## Next steps

1. Run `"$PYTHON" -B -O -W error scripts/box_kite_cases.py --check results/quantum_inspire/cases`,
   `GOROROBA_WORKERS=1 "$PYTHON" -B -W error scripts/box_kite_cases.py --check results/quantum_inspire/cases`
   and `"$PYTHON" -B -O -W error scripts/check_qi_platform_retention.py`.
2. Add gates for `--check` and `--self-test` (normal and -O) to
   `ci/gates.json`, and add the script to the ruff, format and mypy gate
   lists. The `--check` run takes about 2.3 min on the build host, so it
   probably belongs in the `full` tier. The retention gate now walks 284 more
   manifests and took 206 s.
3. Update the batch counts in section 5 of experiment-program.md.
4. Build the next pass: (d1)-(d3), (e), the Ry ladder, the tuna and ry
   dialects, `twin()` and `analyze`.
