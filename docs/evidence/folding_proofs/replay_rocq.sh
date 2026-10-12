#!/bin/sh
# Replay the pinned sign-code proof closure without using cached proof objects.
set -eu

mode="${1:-verified}"
case "$mode" in
    verified|--probe-deprecation) ;;
    *) printf '%s\n' 'usage: replay_rocq.sh [verified|--probe-deprecation]' >&2; exit 2 ;;
esac
if [ "$#" -gt 1 ]; then
    printf '%s\n' 'replay_rocq.sh accepts at most one mode argument' >&2
    exit 2
fi
: "${GOROROBA_ROOT:?Set GOROROBA_ROOT to the inspected open_gororoba checkout}"
ROCQ="${ROCQ:-rocq}"
evidence_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
source_root=$(CDPATH='' cd -- "$GOROROBA_ROOT" && pwd)
version=$("$ROCQ" --version)
expected_version=$(printf '%s\n' 'The Rocq Prover, version 9.1.1' 'compiled with OCaml 5.4.0')
if [ "$version" != "$expected_version" ]; then
    printf '%s\n' 'The retained proof receipt requires Rocq 9.1.1 compiled with OCaml 5.4.0; set ROCQ to that executable.' >&2
    exit 1
fi
(cd "$source_root" && sha256sum -c "$evidence_dir/source_hashes.sha256" >/dev/null)
proof_tmp=$(mktemp -d "${TMPDIR:-/tmp}/gororoba-folding-proof.XXXXXXXX")
trap 'find "$proof_tmp" -depth -delete' 0
trap 'exit 1' HUP INT TERM
mkdir "$proof_tmp/theories" "$proof_tmp/verified"
for proof_name in GF2Algebra SignCodeProjection SchreierSignCode SignCodeCardinality BooleanCochainFiltration; do
    cp "$source_root/proofs/theories/$proof_name.v" "$proof_tmp/theories/"
done
cp "$source_root/proofs/verified/C881_GF2CubicMinDegree.v" "$proof_tmp/verified/"
cp "$evidence_dir/assumptions.v" "$proof_tmp/"
cd "$proof_tmp"
printf '%s\n' "$version"
compile_proof() {
    proof_source="$1"
    if ! "$ROCQ" compile -q -w +all -Q theories OpenGororoba \
        -Q verified OpenGororobaVerified "$proof_source" >compile.log 2>&1; then
        cat compile.log >&2
        return 1
    fi
    if grep -n '[Ww]arning:' compile.log; then
        return 1
    fi
    printf 'compile_pass %s\n' "$proof_source"
}
for proof_name in GF2Algebra SignCodeProjection SchreierSignCode SignCodeCardinality BooleanCochainFiltration; do
    compile_proof "theories/$proof_name.v"
done
compile_proof verified/C881_GF2CubicMinDegree.v
compile_proof assumptions.v
if [ "$(grep -xc 'Closed under the global context' compile.log)" -ne 7 ]; then
    printf '%s\n' 'The seven named theorems require globally closed assumption reports.' >&2
    exit 1
fi
cat compile.log
"$ROCQ" check -silent -o -Q theories OpenGororoba -Q verified OpenGororobaVerified \
    OpenGororoba.SignCodeProjection OpenGororoba.SchreierSignCode \
    OpenGororoba.SignCodeCardinality OpenGororoba.BooleanCochainFiltration \
    OpenGororobaVerified.C881_GF2CubicMinDegree >kernel-check.log 2>&1
cat kernel-check.log
for required_line in \
    '* Axioms: <none>' \
    '* Constants/Inductives relying on type-in-type: <none>' \
    '* Constants/Inductives relying on unsafe (co)fixpoints: <none>' \
    '* Inductives whose positivity is assumed: <none>'; do
    if ! grep -Fqx "$required_line" kernel-check.log; then
        printf 'Missing kernel receipt: %s\n' "$required_line" >&2
        exit 1
    fi
done
if grep -n '[Ww]arning:' kernel-check.log; then
    exit 1
fi
printf '%s\n' 'kernel_check_pass'
if [ "$mode" = '--probe-deprecation' ]; then
    cp "$source_root/proofs/theories/HomotopyTransferAssociator.v" theories/
    compile_proof theories/HomotopyTransferAssociator.v
fi
