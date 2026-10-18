# Folding and sign-code proof evidence

The bundle retains source identities, seven explicit assumption queries, fresh compiler/kernel receipts, and exact rational counterexamples. The [source audit](../../notes/open_gororoba_folding_proofs.md) states the mathematical scope. The files contain source and receipts; Rocq proof objects belong to temporary replay storage.

## Exact counterexamples

From the repository root, use the selected Python interpreter:

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
PYTHONDONTWRITEBYTECODE=1 PYTHONWARNINGS=error \
  "$PYTHON" docs/evidence/folding_proofs/fold_projection_counterexamples.py | \
  cmp - docs/evidence/folding_proofs/fold_projection_counterexamples.json
PYTHONDONTWRITEBYTECODE=1 PYTHONWARNINGS=error \
  "$PYTHON" -O docs/evidence/folding_proofs/fold_projection_counterexamples.py | \
  cmp - docs/evidence/folding_proofs/fold_projection_counterexamples.json
```

The script derives its repository root from its own path. Its explicit runtime checks remain active under `-O`. The multiplication uses `Fraction`; `rank_charts.rank_certificate` independently checks a nonzero pivot and full kernel basis. The two witnesses demonstrate information loss under fold-average and the missing scalar-half constraints in an equal-norm/orthogonality-only predicate.

## Rocq replay

Set `GOROROBA_ROOT` to an `open_gororoba` checkout with the source bytes in `source_hashes.sha256`, which pin commit `7d95d228db6be8a5b2f613430f04f2385d6ae48a`. The script verifies all listed source hashes before copying the proof closure into a freshly created temporary directory.

The retained receipt requires the build in `toolchain.txt`, **Rocq 9.3.0 compiled with OCaml 5.5.1**, with independently released Stdlib 9.2.0. The replay compares both version lines before checking source hashes or creating proof objects. `ROCQ` defaults to `rocq` and accepts an executable path for a selected installation; any other build fails admission (`check_compiler_gate.py`).

```sh
export GOROROBA_ROOT
ROCQ="${ROCQ:-rocq}" sh docs/evidence/folding_proofs/replay_rocq.sh
```

`replay_rocq.sh` compiles all proof bodies with `-q -w +all`, requires seven globally closed assumption queries, and runs the independent kernel checker. Its cleanup removes only its own freshly created temporary directory. It never reads cached sister-repository proof objects. `rocq_replay.log` is its complete stdout, and a second run reproduces it byte for byte.

The independent import probe uses the same compiler and warning policy:

```sh
ROCQ="${ROCQ:-rocq}" sh docs/evidence/folding_proofs/replay_rocq.sh --probe-deprecation
```

It returns exit 1 under Rocq 9.3.0, as under 9.2 and 9.1.1: the transitive `Stdlib.ZArith.ZArith_base` library carries a deprecation, now tagged `deprecated-transitive-library-file-since-Stdlib-9.0`. `homotopy_import_deprecation.log` retains the diagnostic with its machine-specific installation prefix replaced by `<ROCQ_PREFIX>`, and `verification_receipt.json` records the original diagnostic hash and the redaction. The failure remains distinct from the successful sign-code closure.

Fresh Rocq 9.3.0 compilation and independent kernel checking reproduce all seven closed assumption reports. The raw replay log preserves the additional kernel list of inductives relying on indices not mattering. Stdlib 9.2.0 permits Rocq 9.3.0; the toolchain upgrade leaves every source hash and the external commit pin unchanged.

The pin moved from the audited commit `abbf13c` to `7d95d228` because `SchreierSignCode.v` at `abbf13c` fails under Rocq 9.2 (`bad-template-constraint` in `cube_equal_spec`), which open_gororoba's merged re-proof repairs. Four pinned sources differ between the two commits: `SchreierSignCode.v`, `C881_GF2CubicMinDegree.v`, `crates/algebra_analysis/src/stiefel.rs` and `crates/algebra_analysis/src/exact_annihilator.rs`. The re-pin establishes compilation and kernel replay of the closure at `7d95d228` only. The [source audit](../../notes/open_gororoba_folding_proofs.md) and its line locators describe `abbf13c`, and `history/abbf13c-rocq-9.1.1/` keeps that commit's hashes, the Rocq 9.1.1 receipt and logs, and the initial audit's individual `assumptions.log` and `kernel-check.log`.

The deprecated `ZArith_base` import in `HomotopyTransferAssociator.v` remains an open_gororoba follow-up.
