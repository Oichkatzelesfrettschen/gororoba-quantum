# Box-kite case generator: handoff

`scripts/box_kite_cases.py` generates, from
`docs/evidence/box_kite_census/census.json`, the case directories of
[experiment-program.md](experiment-program.md) sections 4(a) and 4(g), and
`scripts/box_kite_qx_sweep.py` runs the exhaustive family (a) on qxelarator.
Nothing has been submitted to any backend.

## State

| Case directory (results/quantum_inspire/cases/) | Backend | Batches | Circuits | Replicas | Shots per circuit | Shots |
|---|---|---|---|---|---|---|
| box_kite_a_qx (smoke set) | QX | 2 | 6 | 15 | 2048 | 12288 |
| box_kite_tuna_t0 | Tuna-17 | 3 | 9 (3 witness) | 9 | 16384 | 147456 |
| box_kite_tuna_t1 | Tuna-17 | 2 | 6 (2 witness) | 6 | 4096 | 24576 |
| box_kite_tuna_coherence | Tuna-17 | 2 | 6 (2 witness) | 6 | 4096 | 24576 |
| box_kite_tuna_walk | Tuna-17 | 3 | 9 (3 witness) | 6 | 4096 | 36864 |
| box_kite_tuna_twins_qx | QX | 4 | 10 | 27 | 2048 | 20480 |

The counts are `--summary` output. The exhaustive family (a), 848 circuits,
2354 replicas (1010 at P = 1/2) in 284 batches, is generated in memory by
`series("a", "qx")` and no longer retained as case files; its bytes equal
the 1133 files the tree held before, which `git rm` removed.

- Smoke selection: the first census row per `SMOKE_PATTERNS` predicate, with
  the predicate text in each replica's `selection` field. The x_sign = -1
  and y_sign = -1 patterns select edge rows, because on a strut a dropped Z
  still reads P = 1/2; the reduced encoding also carries the two sign
  variants and the fixture, which fill its circuits at no extra circuit.
- Tuna-17: the T0 Latin square (y_sign -1 on pair == batch), T1 rows on
  fixed pairs with twist pairs sharing a batch, coherence X and Y settings,
  and the two walks plus the omit-last control, as program section 4(g)
  states. The twist (1,10)(4,15) of kite 3 to (4,10)(1,15) of kite 6 is
  `census:kites[2].twists[0]`; `check_twist` requires it.
- Kaggle: `scripts/kaggle_run.py` gains the `qx-emulator` pin group
  (`qxelarator==0.10.0`). A locally built kernel (no push) bundles the entry,
  its import closure, the three `--include` files and the kernel files in a
  525124-byte run.py, below KERNEL_SOURCE_LIMIT (1000000).

## Checks

| Command | Result |
|---|---|
| `"$PYTHON" -B -O -W error scripts/box_kite_cases.py --check results/quantum_inspire/cases` (previous generator, 1133 files) | `1133 files match their regeneration`, 10.0 s |
| `GOROROBA_WORKERS=1 "$PYTHON" -B -W error scripts/box_kite_cases.py --check ...` (previous generator) | `1133 files match their regeneration`, 17.2 s |
| `"$PYTHON" -B -O -W error scripts/check_qi_platform_retention.py` (previous cases) | `Ran 54 tests` / `OK`; 345 batch subtests, 284 of them box_kite_a_qx |
| `series("a", "qx")` against the 1133 retained files, under `$PYTHON` and `$QI_PYTHON` (qiskit 2.3.1) | 0 mismatches each |
| `--check results/quantum_inspire/cases`, normal, `-O`, `GOROROBA_WORKERS=1` | `68 files match their regeneration` |
| `--self-test`, normal and `-O` | `... contracts pass; 36 mutations rejected` |
| `"$PYTHON" -B -W error scripts/check_qi_platform_retention.py` | `Ran 54 tests` / `OK` |
| `qi_zero_divisor_cases.py --check` and `--self-test` (core-348, after `readout_circuits` was factored out) | `18 files match`; `17 mutations rejected` |
| `"$QI_PYTHON" scripts/qi_toolchain_check.py`, then `"$PYTHON" -B -W error scripts/qi_toolchain_check.py --check` (core-368) | `214 circuits, 0 failing, 15 with a compiled gate sequence change`; `214 circuits match` |
| toolchain record, box-kite circuits | every Tuna and twin circuit keeps its gate sequence; the 4 full Design B smoke circuits differ only in Rz printed at 8 digits |
| `box_kite_qx_sweep.py --self-test`, normal and `-O` (core-377) | `synthetic 848-circuit record replays; 8 mutations rejected` |
| `"$QI_PYTHON" -B -W error scripts/box_kite_qx_sweep.py --run SCRATCH --limit 12` | `28 circuits, 72 replicas, pass` in 9.0 s; record 25992 bytes |
| `"$PYTHON" -B -W error scripts/box_kite_qx_sweep.py --replay SCRATCH --bind --require-pass` | `28 circuits, 72 replicas, max abs z 2.740039, pass` |
| `"$QI_PYTHON" -B -W error scripts/box_kite_qx_sweep.py --emulate` over the six directories (identical Tuna bytes, twins, smoke set) | `46 circuits, 97 checks, pass`; readout-0 all 0, readout-1 all 1, every deterministic replica exact |
| `kaggle_run.py self-test` | passes |
| `uvx ruff@0.14.11 check` and `format --check` (core-000, core-001, core-002) | `All checks passed!`; `213 files already formatted` |
| `mypy` on box_kite_cases.py, box_kite_qx_sweep.py, qi_zero_divisor_cases.py | `Success: no issues found` |
| core-039 (full mypy command) on this host | 25 errors, 24 in scripts/cd_phase_degree.py and 1 at scripts/kaggle_run.py:427 (requests stubs absent on the host); both files' lines are unchanged from main |
| full Kaggle sweep (848 circuits) | not run: the exhaustive sweep runs on a Kaggle CPU kernel, which the orchestrator pushes |

Under `-W error` qxelarator 0.10.0 crashes the interpreter at shutdown
(SWIG builtin types without `__module__`); box_kite_qx_sweep.py filters
exactly those DeprecationWarnings at import, which its spawned workers
inherit.

## Kaggle sweep and its gate

Push (orchestrator), on a CPU machine and without `--ci-env`, since
qxelarator ships cp313 wheels only:

```sh
"$PYTHON" scripts/kaggle_run.py push --slug box-kite-qx-sweep --with qx-emulator \
    --include docs/evidence/box_kite_census/census.json \
    --include docs/evidence/quantum_inspire/catalogue.json \
    --include results/quantum_inspire/coupler_zz_tuna_17_analysis.json \
    scripts/box_kite_qx_sweep.py -- --run docs/evidence/box_kite_qx_sweep/record.json
```

The catalogue and the coupler analysis are read at import by
box_kite_cases.py and qi_zero_divisor_cases.py. After `collect`, retain the
record at docs/evidence/box_kite_qx_sweep/record.json and add the gate
(free numbers: core-378, core-384, core-388 onward):

```sh
"$PYTHON" -B -W error scripts/box_kite_qx_sweep.py --replay docs/evidence/box_kite_qx_sweep/record.json --bind --require-pass && "$PYTHON" -B -O -W error scripts/box_kite_qx_sweep.py --replay docs/evidence/box_kite_qx_sweep/record.json --bind --require-pass
```

`--bind` regenerates the 848 circuits on the CI runner and requires every
sha256 to equal the record's, so a Kaggle-side qiskit difference fails the
gate instead of entering the record silently.

## Not started

- (d1)-(d3) controlled-W circuits and (e) full-encoding coherence settings,
  their QX smoke representatives and their Kaggle sweep.
- The ry dialect, the Ry ladder residue (R1, R2, R8, R9; the retained
  `ry_probe` cases of `scripts/qi_ry_probe_cases.py` already cover R0, R3,
  R4, R5, R6 and R7) and the Ry smoke subset.
- `analyze` and its replay for the Tuna-17 stages.
