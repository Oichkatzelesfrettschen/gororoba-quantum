#!/bin/sh
# Evaluate the sedenion product table of the Rocq integer pair tower and compare it with tower_table.txt.
set -eu

if [ "$#" -ne 0 ]; then
    printf '%s\n' 'usage: rocq_tower_table.sh' >&2
    exit 2
fi
ROCQ="${ROCQ:-rocq}"
evidence_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
repository_root=$(CDPATH='' cd -- "$evidence_dir/../../.." && pwd)
toolchain="$repository_root/docs/evidence/cd-tower-basis-sign/toolchain.txt"
version=$("$ROCQ" --version)
if [ "$version" != "$(cat "$toolchain")" ]; then
    printf '%s\n' 'Set ROCQ to the Rocq executable that docs/evidence/cd-tower-basis-sign/toolchain.txt records.' >&2
    exit 1
fi
table_tmp=$(mktemp -d "${TMPDIR:-/tmp}/quantum-sedenion-table.XXXXXXXX")
trap 'find "$table_tmp" -depth -delete' 0
trap 'exit 1' HUP INT TERM
cp "$repository_root/proofs/CdImaginarySumConference.v" "$repository_root/proofs/CdTowerBasisSign.v" \
    "$evidence_dir/TowerTable.v" "$table_tmp/"
(
    cd "$table_tmp"
    "$ROCQ" compile -q -w @all CdImaginarySumConference.v > compile.txt 2>&1 &&
        "$ROCQ" compile -q -w @all -Q . '' CdTowerBasisSign.v >> compile.txt 2>&1 &&
        "$ROCQ" compile -q -w @all -Q . '' TowerTable.v > table.txt 2>> compile.txt
) || {
    cat "$table_tmp/compile.txt" >&2
    exit 1
}
if [ -s "$table_tmp/compile.txt" ]; then
    cat "$table_tmp/compile.txt" >&2
    exit 1
fi
cmp "$table_tmp/table.txt" "$evidence_dir/tower_table.txt"
printf '%s\n' 'tower_table_pass TowerTable'
