#!/bin/sh
# Recompile the point-indicator proof on its four dependencies and compare its receipts.
set -eu

if [ "$#" -ne 0 ]; then
    printf '%s\n' 'usage: replay_rocq.sh' >&2
    exit 2
fi
ROCQ="${ROCQ:-rocq}"
evidence_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
repository_root=$(CDPATH='' cd -- "$evidence_dir/../../.." && pwd)
version=$("$ROCQ" --version)
if [ "$version" != "$(cat "$evidence_dir/toolchain.txt")" ]; then
    printf '%s\n' 'Set ROCQ to the Rocq executable recorded in toolchain.txt.' >&2
    exit 1
fi
proof_tmp=$(mktemp -d "${TMPDIR:-/tmp}/quantum-cd-associator-point-indicators.XXXXXXXX")
trap 'find "$proof_tmp" -depth -delete' 0
trap 'exit 1' HUP INT TERM
cp "$repository_root/proofs/CdImaginarySumConference.v" "$repository_root/proofs/CdTowerBasisSign.v" \
    "$repository_root/proofs/CdSignRowAnf.v" "$repository_root/proofs/CdAssociatorAnf.v" \
    "$repository_root/proofs/CdAssociatorPointIndicators.v" "$evidence_dir/assumptions.v" "$proof_tmp/"
printf '%s\n' "$version"
(
    cd "$proof_tmp"
    "$ROCQ" compile -q -w @all CdImaginarySumConference.v > compile.txt 2>&1 &&
        "$ROCQ" compile -q -w @all -Q . '' CdTowerBasisSign.v >> compile.txt 2>&1 &&
        "$ROCQ" compile -q -w @all -Q . '' CdSignRowAnf.v >> compile.txt 2>&1 &&
        "$ROCQ" compile -q -w @all -Q . '' CdAssociatorAnf.v >> compile.txt 2>&1 &&
        "$ROCQ" compile -q -w @all -Q . '' CdAssociatorPointIndicators.v >> compile.txt 2>&1 &&
        "$ROCQ" compile -q -w @all -Q . '' assumptions.v > assumptions.txt 2>&1 &&
        "$ROCQ" check -silent -Q . '' -o CdAssociatorPointIndicators > kernel.txt 2>&1
) || {
    for log in compile.txt assumptions.txt kernel.txt; do
        if [ -f "$proof_tmp/$log" ]; then
            cat "$proof_tmp/$log" >&2
        fi
    done
    exit 1
}
if grep -n '[Ww]arning:' "$proof_tmp/compile.txt" "$proof_tmp/assumptions.txt" "$proof_tmp/kernel.txt"; then
    exit 1
fi
if [ -s "$proof_tmp/compile.txt" ]; then
    cat "$proof_tmp/compile.txt" >&2
    exit 1
fi
cmp "$proof_tmp/assumptions.txt" "$evidence_dir/assumptions.txt"
cmp "$proof_tmp/kernel.txt" "$evidence_dir/kernel.txt"
printf '%s\n' 'compile_kernel_assumptions_pass CdAssociatorPointIndicators'
