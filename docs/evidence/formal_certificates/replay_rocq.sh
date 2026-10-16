#!/bin/sh
# Recheck source certificates with the recorded compiler and assumption receipts.
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
(cd "$evidence_dir" && sha256sum --strict -c SHA256SUMS >/dev/null)
(cd "$repository_root" && sha256sum --strict -c "$evidence_dir/source_hashes.sha256" >/dev/null)
proof_tmp=$(mktemp -d "${TMPDIR:-/tmp}/quantum-formal-certificates.XXXXXXXX")
trap 'find "$proof_tmp" -depth -delete' 0
trap 'exit 1' HUP INT TERM
printf '%s\n' "$version"
for proof_name in FoldAverageDescent TerminalChannelSeparation TerminalChannelSeparationReal; do
    cp "$repository_root/proofs/$proof_name.v" "$proof_tmp/"
    (
        cd "$proof_tmp"
        "$ROCQ" compile -q -w @all "$proof_name.v" > "$proof_name.compile.txt" 2>&1 &&
            "$ROCQ" check -silent -o "$proof_name" > "$proof_name.kernel.txt" 2>&1
    ) || {
        cat "$proof_tmp/$proof_name.compile.txt" >&2
        if [ -f "$proof_tmp/$proof_name.kernel.txt" ]; then
            cat "$proof_tmp/$proof_name.kernel.txt" >&2
        fi
        exit 1
    }
    if grep -n '[Ww]arning:' "$proof_tmp/$proof_name.compile.txt" "$proof_tmp/$proof_name.kernel.txt"; then
        exit 1
    fi
    cmp "$proof_tmp/$proof_name.compile.txt" "$evidence_dir/$proof_name.compile.txt"
    cmp "$proof_tmp/$proof_name.kernel.txt" "$evidence_dir/$proof_name.kernel.txt"
    printf 'compile_kernel_assumptions_pass %s\n' "$proof_name"
done
