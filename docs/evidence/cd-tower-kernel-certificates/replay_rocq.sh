#!/bin/sh
# Recompile the kernel-certificate files of the commutative-ring tower with the twelve canonical points and the Zmod 7 instance, and compare the receipts.
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
proof_tmp=$(mktemp -d "${TMPDIR:-/tmp}/quantum-cd-tower-kernel-certificates.XXXXXXXX")
trap 'find "$proof_tmp" -depth -delete' 0
trap 'exit 1' HUP INT TERM
cp "$repository_root/proofs/CdTwistedProduct.v" "$repository_root/proofs/CdTowerRing.v" \
    "$repository_root/proofs/CdTowerRingBasis.v" "$repository_root/proofs/CdTowerRingBaseChange.v" \
    "$repository_root/proofs/CdTowerKernelCertificate.v" "$repository_root/proofs/CdTowerCanonicalKernels.v" \
    "$evidence_dir/assumptions.v" "$evidence_dir/statements.v" "$proof_tmp/"
printf '%s\n' "$version"
(
    cd "$proof_tmp"
    "$ROCQ" compile -q -w @all -Q . '' CdTwistedProduct.v > compile.txt 2>&1 &&
        "$ROCQ" compile -q -w @all -Q . '' CdTowerRing.v >> compile.txt 2>&1 &&
        "$ROCQ" compile -q -w @all -Q . '' CdTowerRingBasis.v >> compile.txt 2>&1 &&
        "$ROCQ" compile -q -w @all -Q . '' CdTowerRingBaseChange.v >> compile.txt 2>&1 &&
        "$ROCQ" compile -q -w @all -Q . '' CdTowerKernelCertificate.v >> compile.txt 2>&1 &&
        "$ROCQ" compile -q -w @all -Q . '' CdTowerCanonicalKernels.v >> compile.txt 2>&1 &&
        "$ROCQ" compile -q -w @all -Q . '' assumptions.v > assumptions.txt 2>&1 &&
        "$ROCQ" compile -q -w @all -Q . '' statements.v > statements.txt 2>&1 &&
        "$ROCQ" check -silent -Q . '' -o CdTowerKernelCertificate CdTowerCanonicalKernels > kernel.txt 2>&1
) || {
    for log in compile.txt assumptions.txt statements.txt kernel.txt; do
        if [ -f "$proof_tmp/$log" ]; then
            cat "$proof_tmp/$log" >&2
        fi
    done
    exit 1
}
# Mutation control: with the coordinate -1 of the W8 point replaced by 1 the first kernel vector is no longer
# annihilated, so the compile of the mutant has to exit nonzero at j = 0 of W8_vectors_annihilated.
sed '/^Definition W8_point /s/(-1)/1/' "$proof_tmp/CdTowerCanonicalKernels.v" \
    > "$proof_tmp/CdTowerCanonicalKernelsMutant.v"
if cmp -s "$proof_tmp/CdTowerCanonicalKernels.v" "$proof_tmp/CdTowerCanonicalKernelsMutant.v"; then
    printf '%s\n' 'The mutation matched no line of CdTowerCanonicalKernels.v.' >&2
    exit 1
fi
if (cd "$proof_tmp" && "$ROCQ" compile -q -w @all -Q . '' CdTowerCanonicalKernelsMutant.v > mutant.txt 2>&1); then
    printf '%s\n' 'The sign-flipped mutant of the W8 point compiled.' >&2
    exit 1
fi
annihilated_line=$(grep -n '^Lemma W8_vectors_annihilated ' "$proof_tmp/CdTowerCanonicalKernelsMutant.v" | cut -d: -f1)
failure_line=$((annihilated_line + 2))
if ! grep -q "^File \"./CdTowerCanonicalKernelsMutant.v\", line $failure_line," "$proof_tmp/mutant.txt" ||
    ! grep -q '^Hj : (0 < 8)%nat$' "$proof_tmp/mutant.txt"; then
    printf '%s\n' 'The mutant failed somewhere other than j = 0 of W8_vectors_annihilated:' >&2
    cat "$proof_tmp/mutant.txt" >&2
    exit 1
fi
if grep -n '[Ww]arning:' "$proof_tmp/compile.txt" "$proof_tmp/assumptions.txt" "$proof_tmp/statements.txt" \
    "$proof_tmp/kernel.txt"; then
    exit 1
fi
if [ -s "$proof_tmp/compile.txt" ]; then
    cat "$proof_tmp/compile.txt" >&2
    exit 1
fi
cmp "$proof_tmp/assumptions.txt" "$evidence_dir/assumptions.txt"
cmp "$proof_tmp/statements.txt" "$evidence_dir/statements.txt"
cmp "$proof_tmp/kernel.txt" "$evidence_dir/kernel.txt"
printf '%s\n' 'compile_kernel_assumptions_pass CdTowerCanonicalKernels' 'mutant_rejected W8_vectors_annihilated j = 0'
