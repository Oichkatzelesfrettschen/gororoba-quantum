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

Set `GOROROBA_ROOT` to an `open_gororoba` checkout with the source bytes in `source_hashes.sha256`. The audited commit is `abbf13cada78d9b106fc610a36f6eea54567ecfc`. The script verifies all listed source hashes before copying the proof closure into a freshly created temporary directory.

The retained receipt requires **Rocq 9.1.1**; the audit uses its OCaml 5.4.0 build. `ROCQ` defaults to `rocq` and accepts an executable path for a selected installation. An incompatible compiler version fails admission.

```sh
export GOROROBA_ROOT
ROCQ="${ROCQ:-rocq}" sh docs/evidence/folding_proofs/replay_rocq.sh
```

`replay_rocq.sh` compiles all proof bodies with `-q -w +all`, requires seven globally closed assumption queries, and runs the independent kernel checker. Its cleanup removes only its own freshly created temporary directory. It never reads cached sister-repository proof objects. `rocq_replay.log` retains the complete successful stdout; `assumptions.log` and `kernel-check.log` retain the initial audit's individual outputs.

The independent import probe uses the same compiler and warning policy:

```sh
ROCQ="${ROCQ:-rocq}" sh docs/evidence/folding_proofs/replay_rocq.sh --probe-deprecation
```

The recorded environment returns exit 1 for that probe because the transitive `Stdlib.ZArith.ZArith_base` library carries a deprecation. `homotopy_import_deprecation.log` retains the diagnostic with its machine-specific installation prefix replaced by `<ROCQ_PREFIX>`. `verification_receipt.json` records the original diagnostic hash and the redaction. The failure remains distinct from the successful sign-code closure. The script propagates an import failure; an installation with repaired library imports can return success without altering the historical receipt.

The source audit identifies a separate sister-repository follow-up for stale Stiefel prose, C881 proof-scope wording, and the deprecated import path. The present bundle owns evidence and replay only.
