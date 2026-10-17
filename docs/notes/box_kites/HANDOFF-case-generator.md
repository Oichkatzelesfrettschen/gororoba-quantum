# Box-kite case generator: handoff

`scripts/box_kite_cases.py` generates, from
`docs/evidence/box_kite_census/census.json`, the case directories of
[experiment-program.md](experiment-program.md) sections 4(a), (d), (e), (f)
and (g), and `scripts/box_kite_qx_sweep.py` runs the exhaustive families on
qxelarator. Nothing has been submitted to any backend.

## State

| Case directory (results/quantum_inspire/cases/) | Backend | Batches | Circuits | Replicas | Shots per circuit | Shots |
|---|---|---|---|---|---|---|
| box_kite_a_qx (smoke set) | QX | 2 | 6 | 15 | 2048 | 12288 |
| box_kite_tuna_pre | Tuna-17 | 1 | 3 (1 diagnostic) | -- | 4096 | 12288 |
| box_kite_tuna_t0 | Tuna-17 | 3 | 9 (3 witness) | 9 | 16384 | 147456 |
| box_kite_tuna_t1 | Tuna-17 | 2 | 6 (2 witness) | 6 | 4096 | 24576 |
| box_kite_tuna_coherence | Tuna-17 | 2 | 6 (2 witness) | 6 | 4096 | 24576 |
| box_kite_tuna_walk | Tuna-17 | 3 | 9 (3 witness) | 6 | 4096 | 36864 |
| box_kite_tuna_twins_qx | QX | 5 | 11 | 27 | 2048 | 22528 |
| box_kite_ry_ladder | Ry | 1 | 3 | -- | 1024 | 3072 |
| box_kite_ry_smoke | Ry | 2 | 6 | 12 | 1024 | 6144 |
| box_kite_de_qx (smoke representatives) | QX | 2 | 4 | 7 | 2048 | 8192 |

The counts are `--summary` output. The exhaustive families are generated in
memory and not retained as case files: family a, `series("a", "qx")`, 848
circuits, 2354 replicas (1010 at P = 1/2) in 284 batches, byte-identical to
the 1133 files the tree held before, which `git rm` removed; family de,
`series_de()`, 149 circuits and 281 replicas (d1 42, d2 105, d3 16, e 118)
in 51 batches, each circuit checked by state vector against its census
value.

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
- Ry: the retained construct probe (results/quantum_inspire/ry_probe_analysis.json)
  already names the cause of the failed program: any bit register fails,
  and a measure statement fails compilation. The ladder residue is R1
  (qubit[9]), R2 (comment line) and R9 (teleport.cq bare, read by its
  sha256); R8 adds nothing and is not generated. The probe's single H is not
  R4 (H H); R4 is not generated because H and its composition with CNOT
  already completed. The Ry smoke subset declares qubit[9], so R1 gates it.
- (d)/(e): controlled W_ij from designs' left multiplications as controlled
  sign diagonals and CNOTs (the `.control()` form cost 306 CNOT per block,
  this one about 90); d3 a 9-qubit diagonal over (j, k); (e) predictions
  from census coefficients through `pauli_expectation`.
- Kaggle: `scripts/kaggle_run.py` gains the `qx-emulator` pin group
  (`qxelarator==0.10.0`). A locally built kernel (no push) bundles the
  entry, its import closure, the three `--include` files and the kernel
  files in a 539016-byte run.py, below KERNEL_SOURCE_LIMIT (1000000).
- Gates core-420 (`--check`), core-421 (`--self-test`) and core-422 (sweep
  `--self-test`), each in normal and optimized mode, from the range the
  orchestrator assigned (core-420 to core-429).

## Checks

| Command | Result |
|---|---|
| `"$PYTHON" -B -O -W error scripts/box_kite_cases.py --check results/quantum_inspire/cases` (previous generator, 1133 files) | `1133 files match their regeneration`, 10.0 s |
| `GOROROBA_WORKERS=1 "$PYTHON" -B -W error scripts/box_kite_cases.py --check ...` (previous generator) | `1133 files match their regeneration`, 17.2 s |
| `"$PYTHON" -B -O -W error scripts/check_qi_platform_retention.py` (previous cases) | `Ran 54 tests` / `OK`; 345 batch subtests, 284 of them box_kite_a_qx |
| `series("a", "qx")` against the 1133 retained files, under `$PYTHON` and `$QI_PYTHON` (qiskit 2.3.1) | 0 mismatches each |
| `series_de()` (all 149 circuits through `verify_text`) | passes, 26 s on 12 workers |
| `--check results/quantum_inspire/cases`, normal, `-O`, `GOROROBA_WORKERS=1` | `89 files match their regeneration` |
| `--self-test`, normal and `-O` | `... contracts pass; 44 mutations rejected` |
| `"$PYTHON" -B -W error scripts/check_qi_platform_retention.py` | `Ran 54 tests` / `OK` |
| `qi_zero_divisor_cases.py --check` and `--self-test` (core-348, after `readout_circuits` was factored out) | `18 files match`; `17 mutations rejected` |
| `"$QI_PYTHON" scripts/qi_toolchain_check.py`, then `"$PYTHON" -B -W error scripts/qi_toolchain_check.py --check` (core-368) | `227 circuits, 0 failing, 27 with a compiled gate sequence change`; `227 circuits match` |
| toolchain record, box-kite circuits | every Tuna and twin circuit keeps its gate sequence; the QX full Design B and (d)/(e) circuits differ only in Rz printed at 8 digits; the Ry circuits change under the Ry decomposition passes, as the retained probe's do |
| `box_kite_qx_sweep.py --self-test`, normal and `-O` (core-422) | `synthetic records of families a and de replay; 18 mutations rejected` |
| `"$QI_PYTHON" -B -W error scripts/box_kite_qx_sweep.py --run SCRATCH --family a --limit 12` | `28 circuits, 72 replicas, 72 checks, pass` |
| `"$PYTHON" -B -W error scripts/box_kite_qx_sweep.py --replay SCRATCH/family-a.json --bind --require-pass` | `28 circuits, 72 replicas, 72 checks, max abs z 2.740039, pass` |
| `"$QI_PYTHON" ... --run SCRATCH --family de --limit 2`, then `"$PYTHON" ... --replay SCRATCH/family-de.json --bind --require-pass` | `5 circuits, 8 replicas, 10 checks, pass` in 652.5 s; replay `max abs z 2.43068, pass` |
| qxelarator time per circuit at 256 shots | d1 0.09 s, d2 10.9 s, d3 13.9 s, e 0.05 s: it re-simulates every shot; at 2048 shots the 3 dense circuits of the limited run took about 215 s each |
| `"$QI_PYTHON" -B -W error scripts/box_kite_qx_sweep.py --emulate` over the Tuna, twin and QX smoke directories (identical Tuna bytes) | `46 circuits, 97 checks, pass`; readout-0 all 0, readout-1 all 1, every deterministic replica exact |
| `--emulate` over box_kite_ry_ladder and box_kite_ry_smoke (measure appended for qxelarator only) | `9 circuits, 33 checks, pass` |
| `kaggle_run.py self-test` | passes |
| `uvx ruff@0.14.11 check` and `format --check` (core-000, core-001, core-002) | `All checks passed!`; every file formatted |
| `mypy` on box_kite_cases.py, box_kite_qx_sweep.py, qi_zero_divisor_cases.py | `Success: no issues found` |
| core-039 (full mypy command) on this host | 25 errors, 24 in scripts/cd_phase_degree.py and 1 at scripts/kaggle_run.py:427 (requests stubs absent on the host); both files' lines are unchanged from main, so CI is the authority for this gate |
| full Kaggle sweep (both families) | not run: it runs on a Kaggle CPU kernel, which the orchestrator pushes |

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
    scripts/box_kite_qx_sweep.py -- --run docs/evidence/box_kite_qx_sweep
```

The catalogue and the coupler analysis are read at import by
box_kite_cases.py and qi_zero_divisor_cases.py. Expected cost: family a
about 0.2 s per circuit, family de about 15000 CPU-seconds (69 dense d2 and
d3 circuits at about 215 s each), so about an hour on the kernel's 4 CPUs,
inside the CPU session limit. After
`collect`, docs/evidence/box_kite_qx_sweep/family-a.json and family-de.json
hold the kernel's records (both pass), and gate core-423 replays them:

```sh
"$PYTHON" -B -W error scripts/box_kite_qx_sweep.py --replay docs/evidence/box_kite_qx_sweep/family-a.json --bind --require-pass && "$PYTHON" -B -W error scripts/box_kite_qx_sweep.py --replay docs/evidence/box_kite_qx_sweep/family-de.json --bind --require-pass && "$PYTHON" -B -O -W error scripts/box_kite_qx_sweep.py --replay docs/evidence/box_kite_qx_sweep/family-a.json --bind --require-pass && "$PYTHON" -B -O -W error scripts/box_kite_qx_sweep.py --replay docs/evidence/box_kite_qx_sweep/family-de.json --bind --require-pass
```

`--bind` regenerates the circuits on the CI runner and requires every
sha256 and every replica's checks to equal the record's, so a Kaggle-side
qiskit difference fails the gate instead of entering the record silently.
CI cannot install the cp313-only qxelarator, so the gate re-derives every
verdict from the retained counts and re-checks every prediction by state
vector through `--bind`, and nothing resamples.

## Analysis

`scripts/box_kite_analysis.py` analyzes and replays every Tuna-17 stage
(pre, T0, T1, coherence, walk) and both Ry stages from retained run
directories, with the thresholds each manifest carries; gate core-424 runs
its synthetic self-test. experiment-program.md section 4(g), **Analysis**,
gives the commands and rules, and section 7 the preregistration points the
owner decides (the T1 twist allowance reads T0 at CZ depth 5; the bright
floor reads CZ depth 1 only).
