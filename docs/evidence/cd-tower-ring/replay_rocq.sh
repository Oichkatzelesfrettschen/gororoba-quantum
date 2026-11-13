#!/bin/sh
# Recompile the commutative-ring tower, its Gaussian-integer and Zmod 5 instances and the bridge to the ordered-domain tower, and compare the receipts.
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
proof_tmp=$(mktemp -d "${TMPDIR:-/tmp}/quantum-cd-tower-ring.XXXXXXXX")
trap 'find "$proof_tmp" -depth -delete' 0
trap 'exit 1' HUP INT TERM
cp "$repository_root/proofs/CdTwistedProduct.v" "$repository_root/proofs/CdTowerRing.v" \
    "$repository_root/proofs/CdTowerDomain.v" "$repository_root/proofs/CdTowerRingDomain.v" \
    "$evidence_dir/assumptions.v" "$proof_tmp/"
printf '%s\n' "$version"
(
    cd "$proof_tmp"
    "$ROCQ" compile -q -w @all -Q . '' CdTwistedProduct.v > compile.txt 2>&1 &&
        "$ROCQ" compile -q -w @all -Q . '' CdTowerRing.v >> compile.txt 2>&1 &&
        "$ROCQ" compile -q -w @all -Q . '' CdTowerDomain.v >> compile.txt 2>&1 &&
        "$ROCQ" compile -q -w @all -Q . '' CdTowerRingDomain.v >> compile.txt 2>&1 &&
        "$ROCQ" compile -q -w @all -Q . '' assumptions.v > assumptions.txt 2>&1 &&
        "$ROCQ" check -silent -Q . '' -o CdTowerRing CdTowerRingDomain > kernel.txt 2>&1
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
printf '%s\n' 'compile_kernel_assumptions_pass CdTowerRing'
