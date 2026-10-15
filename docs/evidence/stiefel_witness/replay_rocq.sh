#!/bin/sh
# Replay the A_6 Stiefel witness certificate against open_gororoba's cd_sign_fuel.
set -eu

if [ "$#" -ne 0 ]; then
    printf '%s\n' 'usage: replay_rocq.sh' >&2
    exit 2
fi
: "${GOROROBA_ROOT:?Set GOROROBA_ROOT to the open_gororoba checkout named in source_hashes.sha256}"
ROCQ="${ROCQ:-rocq}"
evidence_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
repository_root=$(CDPATH='' cd -- "$evidence_dir/../../.." && pwd)
version=$("$ROCQ" --version)
if [ "$version" != "$(cat "$evidence_dir/toolchain.txt")" ]; then
    printf '%s\n' 'The witness replay requires the recorded Rocq and OCaml versions.' >&2
    exit 1
fi
(cd "$evidence_dir" && sha256sum --strict -c SHA256SUMS >/dev/null)
(cd "$GOROROBA_ROOT" && sha256sum --strict -c "$evidence_dir/source_hashes.sha256" >/dev/null)
(cd "$repository_root" && sha256sum --strict -c "$evidence_dir/repo_sources.sha256" >/dev/null)
proof_tmp=$(mktemp -d "${TMPDIR:-/tmp}/quantum-stiefel-witness.XXXXXXXX")
trap 'find "$proof_tmp" -depth -delete' 0
trap 'exit 1' HUP INT TERM
mkdir -p "$proof_tmp/proofs/verified" "$proof_tmp/proofs/quantum"
cp "$GOROROBA_ROOT/proofs/verified/C1474_FuelAdequacy.v" "$proof_tmp/proofs/verified/"
cp "$repository_root/proofs/StiefelWitnessInvertible.v" "$proof_tmp/proofs/quantum/"
cp "$evidence_dir/assumptions.v" "$proof_tmp/proofs/"
(cd "$proof_tmp" && sha256sum --strict -c "$evidence_dir/source_hashes.sha256" >/dev/null)
(
    cd "$proof_tmp/proofs"
    paths="-R verified OpenGororobaVerified -Q quantum GororobaQuantum"
    # shellcheck disable=SC2086
    "$ROCQ" compile -q -w @all $paths verified/C1474_FuelAdequacy.v > C1474.compile.txt 2>&1
    # shellcheck disable=SC2086
    "$ROCQ" compile -q -w @all $paths quantum/StiefelWitnessInvertible.v > witness.compile.txt 2>&1
    # shellcheck disable=SC2086
    "$ROCQ" compile -q -w @all $paths assumptions.v > assumptions.txt 2>&1
    # shellcheck disable=SC2086
    "$ROCQ" check -silent -o $paths GororobaQuantum.StiefelWitnessInvertible > kernel.txt 2>&1
) || {
    cat "$proof_tmp/proofs/"*.txt >&2
    exit 1
}
if grep -n '[Ww]arning:' "$proof_tmp/proofs/"*.txt; then exit 1; fi
for output in C1474.compile.txt witness.compile.txt assumptions.txt kernel.txt; do
    cmp "$proof_tmp/proofs/$output" "$evidence_dir/$output"
done
printf '%s\n' 'A_6 Stiefel witness: compile, kernel, assumptions, and source identities pass.'
