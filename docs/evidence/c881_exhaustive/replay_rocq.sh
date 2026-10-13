#!/bin/sh
# Replay the complete finite separating-degree proof from its audited sources.
set -eu

if [ "$#" -ne 0 ]; then
    printf '%s\n' 'usage: replay_rocq.sh' >&2
    exit 2
fi
: "${GOROROBA_ROOT:?Set GOROROBA_ROOT to the latest audited open_gororoba checkout}"
ROCQ="${ROCQ:-rocq}"
evidence_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
version=$("$ROCQ" --version)
if [ "$version" != "$(cat "$evidence_dir/toolchain.txt")" ]; then
    printf '%s\n' 'C881 replay requires the recorded Rocq and OCaml versions.' >&2
    exit 1
fi
(cd "$evidence_dir" && sha256sum --strict -c SHA256SUMS >/dev/null)
(cd "$GOROROBA_ROOT" && sha256sum --strict -c "$evidence_dir/source_hashes.sha256" >/dev/null)
proof_tmp=$(mktemp -d "${TMPDIR:-/tmp}/quantum-c881-exhaustive.XXXXXXXX")
trap 'find "$proof_tmp" -depth -delete' 0
trap 'exit 1' HUP INT TERM
mkdir -p "$proof_tmp/proofs/theories" "$proof_tmp/proofs/verified"
cp "$GOROROBA_ROOT/proofs/theories/GF2Algebra.v" "$proof_tmp/proofs/theories/"
cp "$GOROROBA_ROOT/proofs/verified/C881_GF2CubicMinDegree.v" "$proof_tmp/proofs/verified/"
cp "$evidence_dir/assumptions.v" "$proof_tmp/proofs/"
(cd "$proof_tmp" && sha256sum --strict -c "$evidence_dir/source_hashes.sha256" >/dev/null)
(
    cd "$proof_tmp/proofs"
    "$ROCQ" compile -q -w @all -R theories OpenGororoba -R verified OpenGororobaVerified \
        theories/GF2Algebra.v > GF2Algebra.compile.txt 2>&1
    "$ROCQ" compile -q -w @all -R theories OpenGororoba -R verified OpenGororobaVerified \
        verified/C881_GF2CubicMinDegree.v > C881.compile.txt 2>&1
    "$ROCQ" compile -q -w @all -R theories OpenGororoba -R verified OpenGororobaVerified \
        assumptions.v > assumptions.txt 2>&1
    "$ROCQ" check -silent -o -R theories OpenGororoba -R verified OpenGororobaVerified \
        OpenGororobaVerified.C881_GF2CubicMinDegree > kernel.txt 2>&1
) || {
    cat "$proof_tmp/proofs/"*.txt >&2
    exit 1
}
if rg -n '[Ww]arning:' "$proof_tmp/proofs/"*.txt; then exit 1; fi
for output in GF2Algebra.compile.txt C881.compile.txt assumptions.txt kernel.txt; do
    cmp "$proof_tmp/proofs/$output" "$evidence_dir/$output"
done
(cd "$GOROROBA_ROOT" && sha256sum --strict -c "$evidence_dir/source_hashes.sha256" >/dev/null)
printf '%s\n' 'C881 exhaustive coefficient proof: compile, kernel, assumptions, and source identities pass.'
