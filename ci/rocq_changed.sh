#!/bin/sh
# Usage: rocq_changed.sh < PATHS
# Exit 0 when a path on stdin (one per line) belongs to the Rocq replay: the
# proof sources, a replay bundle, the replay driver, a pin, or the workflow.
# Exit 1 when none does.
set -eu

while IFS= read -r path; do
  case "$path" in
  proofs/* | \
    docs/evidence/c881_exhaustive/* | \
    docs/evidence/folding_proofs/* | \
    docs/evidence/formal_certificates/* | \
    docs/evidence/stiefel_witness/* | \
    docs/evidence/rocq_kaggle_replay/* | \
    scripts/rocq_kaggle_replay.py | \
    ci/open_gororoba.pin | \
    ci/fetch_open_gororoba.sh | \
    ci/rocq_toolchain.pin | \
    ci/install_rocq.sh | \
    ci/rocq_changed.sh | \
    .github/workflows/ci.yml)
    exit 0
    ;;
  esac
done
exit 1
