#!/bin/sh
# Recompile the basis, base-change and order-three-map files of the commutative-ring tower with their Z[sqrt 3] and Zmod 11 instances, and compare the receipts.
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
proof_tmp=$(mktemp -d "${TMPDIR:-/tmp}/quantum-cd-tower-ring-base-change.XXXXXXXX")
trap 'find "$proof_tmp" -depth -delete' 0
trap 'exit 1' HUP INT TERM
cp "$repository_root/proofs/CdTwistedProduct.v" "$repository_root/proofs/CdTowerRing.v" \
    "$repository_root/proofs/CdTowerRingBasis.v" "$repository_root/proofs/CdTowerRingBaseChange.v" \
    "$repository_root/proofs/CdTowerOrderThreeMap.v" \
    "$evidence_dir/assumptions.v" "$evidence_dir/images.v" "$proof_tmp/"
printf '%s\n' "$version"
(
    cd "$proof_tmp"
    "$ROCQ" compile -q -w @all -Q . '' CdTwistedProduct.v > compile.txt 2>&1 &&
        "$ROCQ" compile -q -w @all -Q . '' CdTowerRing.v >> compile.txt 2>&1 &&
        "$ROCQ" compile -q -w @all -Q . '' CdTowerRingBasis.v >> compile.txt 2>&1 &&
        "$ROCQ" compile -q -w @all -Q . '' CdTowerRingBaseChange.v >> compile.txt 2>&1 &&
        "$ROCQ" compile -q -w @all -Q . '' CdTowerOrderThreeMap.v >> compile.txt 2>&1 &&
        "$ROCQ" compile -q -w @all -Q . '' assumptions.v > assumptions.txt 2>&1 &&
        "$ROCQ" compile -q -w @all -Q . '' images.v > images.txt 2>&1 &&
        "$ROCQ" check -silent -Q . '' -o CdTowerRingBasis CdTowerRingBaseChange CdTowerOrderThreeMap \
            > kernel.txt 2>&1
) || {
    for log in compile.txt assumptions.txt images.txt kernel.txt; do
        if [ -f "$proof_tmp/$log" ]; then
            cat "$proof_tmp/$log" >&2
        fi
    done
    exit 1
}
# Mutation control: with the sign of the r3 term of the first half of source_psi2 flipped, the 256-pair check
# images_basis_check has to fail, so the compile of the mutant has to exit nonzero inside that proof.
sed 's/(TA.scale k Root3Integers.r3 (im (snd x)))/(TA.scale k (Root3Integers.opp Root3Integers.r3) (im (snd x)))/' \
    "$proof_tmp/CdTowerOrderThreeMap.v" > "$proof_tmp/CdTowerOrderThreeMapMutant.v"
if cmp -s "$proof_tmp/CdTowerOrderThreeMap.v" "$proof_tmp/CdTowerOrderThreeMapMutant.v"; then
    printf '%s\n' 'The mutation matched no line of CdTowerOrderThreeMap.v.' >&2
    exit 1
fi
if (cd "$proof_tmp" && "$ROCQ" compile -q -w @all -Q . '' CdTowerOrderThreeMapMutant.v > mutant.txt 2>&1); then
    printf '%s\n' 'The sign-flipped mutant of source_psi2 compiled.' >&2
    exit 1
fi
if ! grep -q '^Hi : 1 < 16$' "$proof_tmp/mutant.txt" || ! grep -q '^Hj : 8 < 16$' "$proof_tmp/mutant.txt"; then
    printf '%s\n' 'The mutant failed somewhere other than the basis pair (1, 8) of images_basis_check:' >&2
    cat "$proof_tmp/mutant.txt" >&2
    exit 1
fi
if grep -n '[Ww]arning:' "$proof_tmp/compile.txt" "$proof_tmp/assumptions.txt" "$proof_tmp/images.txt" \
    "$proof_tmp/kernel.txt"; then
    exit 1
fi
if [ -s "$proof_tmp/compile.txt" ]; then
    cat "$proof_tmp/compile.txt" >&2
    exit 1
fi
cmp "$proof_tmp/assumptions.txt" "$evidence_dir/assumptions.txt"
cmp "$proof_tmp/images.txt" "$evidence_dir/images.txt"
cmp "$proof_tmp/kernel.txt" "$evidence_dir/kernel.txt"
printf '%s\n' 'compile_kernel_assumptions_pass CdTowerOrderThreeMap' 'mutant_rejected images_basis_check pair (1, 8)'
