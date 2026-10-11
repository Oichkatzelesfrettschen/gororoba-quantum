#!/bin/sh
set -eu

: "${ROCQ_BIN:?Set ROCQ_BIN to the Rocq executable from the intended toolchain}"
: "${PROOF_SOURCE_ROOT:?Set PROOF_SOURCE_ROOT to the checkout proofs directory}"
: "${PROOF_SOURCE_SHA256:?Set PROOF_SOURCE_SHA256 to the expected source hash manifest}"
PROOF_PROBE_ROOT="${PROOF_PROBE_ROOT:-$(mktemp -d /tmp/cayley-dickson-proof-source.XXXXXX)}"
ROCQ_CHECKER_BIN="${ROCQ_CHECKER_BIN:-$(dirname "$ROCQ_BIN")/rocqchk}"

mkdir -p "$PROOF_PROBE_ROOT/theories" "$PROOF_PROBE_ROOT/verified"
"$ROCQ_BIN" --version > "$PROOF_PROBE_ROOT/toolchain-version.log"
"$ROCQ_CHECKER_BIN" --version >> "$PROOF_PROBE_ROOT/toolchain-version.log"
printf '%s\n' 'compile_warnings=+all' 'compiler_warning_diagnostics=reject' \
    > "$PROOF_PROBE_ROOT/warning-policy.log"

cat > "$PROOF_PROBE_ROOT/sign-source-order.txt" <<'SOURCES'
theories/Prelude.v
theories/CayleyDicksonAlgebra.v
theories/Sedenion.v
theories/M3IsAssociator.v
theories/CDSignHalfStep.v
verified/C1636_Cariow2013SedenionSchedule.v
verified/C958_ZDGraphTopology.v
verified/C1474_FuelAdequacy.v
SOURCES

cat > "$PROOF_PROBE_ROOT/higher-source-order.txt" <<'SOURCES'
theories/OctonionNorm.v
theories/CDLinearLemmas.v
theories/SedenionAssociator.v
theories/Pathion.v
theories/HigherCD.v
verified/C1455_AssociatorTrilinear.v
verified/C1470_PathionTrilinearity.v
verified/C1471_HigherCDTrilinearity.v
SOURCES

cp "$PROOF_SOURCE_SHA256" "$PROOF_PROBE_ROOT/expected-source-sha256.txt"
awk '
    NF != 2 || length($1) != 64 || $1 ~ /[^0-9a-f]/ ||
        $2 !~ /^(theories|verified)\/[^/]+\.v$/ { exit 1 }
    { print $2 }
' "$PROOF_PROBE_ROOT/expected-source-sha256.txt" \
    > "$PROOF_PROBE_ROOT/expected-source-paths.unsorted.txt"
sort "$PROOF_PROBE_ROOT/expected-source-paths.unsorted.txt" \
    > "$PROOF_PROBE_ROOT/expected-source-paths.txt"
cat "$PROOF_PROBE_ROOT/sign-source-order.txt" \
    "$PROOF_PROBE_ROOT/higher-source-order.txt" | sort \
    > "$PROOF_PROBE_ROOT/audited-source-paths.txt"
cmp "$PROOF_PROBE_ROOT/expected-source-paths.txt" \
    "$PROOF_PROBE_ROOT/audited-source-paths.txt"
(
    cd "$PROOF_SOURCE_ROOT"
    sha256sum --strict -c "$PROOF_PROBE_ROOT/expected-source-sha256.txt"
) > "$PROOF_PROBE_ROOT/checkout-source-hash-check.log"

for source_order in sign-source-order.txt higher-source-order.txt; do
    while IFS= read -r proof_source; do
        cp "$PROOF_SOURCE_ROOT/$proof_source" "$PROOF_PROBE_ROOT/$proof_source"
    done < "$PROOF_PROBE_ROOT/$source_order"
done

cd "$PROOF_PROBE_ROOT"
sha256sum --strict -c expected-source-sha256.txt > copied-source-hash-check.log
: > source-sha256.txt
for source_order in sign-source-order.txt higher-source-order.txt; do
    while IFS= read -r proof_source; do
        sha256sum "$proof_source" >> source-sha256.txt
    done < "$source_order"
done

: > fresh-compilation.log
while IFS= read -r proof_source; do
    "$ROCQ_BIN" compile -q -w +all \
        -R theories OpenGororoba -R verified OpenGororobaVerified \
        "$proof_source" >> fresh-compilation.log 2>&1
    if grep -nE '(^|[[:space:]])[Ww]arning:' fresh-compilation.log; then
        printf '%s\n' 'Compiler warning diagnostic rejected' >&2
        exit 1
    fi
    printf '%s compiled\n' "$proof_source"
done < sign-source-order.txt

"$ROCQ_CHECKER_BIN" -silent -o \
    -R theories OpenGororoba -R verified OpenGororobaVerified \
    OpenGororoba.CDSignHalfStep \
    OpenGororobaVerified.C1636_Cariow2013SedenionSchedule \
    OpenGororobaVerified.C958_ZDGraphTopology \
    OpenGororobaVerified.C1474_FuelAdequacy \
    > fresh-kernel-check.log 2>&1

"$ROCQ_BIN" repl -quiet \
    -R theories OpenGororoba -R verified OpenGororobaVerified \
    > source-assumptions.log 2>&1 <<'ROCQ'
From OpenGororoba Require Import CDSignHalfStep.
From OpenGororobaVerified Require Import C1636_Cariow2013SedenionSchedule C958_ZDGraphTopology C1474_FuelAdequacy.
Print Assumptions cd_sign_fuel_lo_lo.
Print Assumptions cd_sign_fuel_lo_hi.
Print Assumptions cd_sign_fuel_hi_lo.
Print Assumptions cd_sign_fuel_hi_hi.
Print Assumptions C1636_cariow2013_sedenion_mul_eq.
Print Assumptions zd_edge_formula.
Print Assumptions zd_edges_at_16.
Print Assumptions zd_graph_three_components.
Print Assumptions fuel_adequate_64.
Quit.
ROCQ

: > higher-cd-compilation.log
while IFS= read -r proof_source; do
    "$ROCQ_BIN" compile -q -w +all \
        -R theories OpenGororoba -R verified OpenGororobaVerified \
        "$proof_source" >> higher-cd-compilation.log 2>&1
    if grep -nE '(^|[[:space:]])[Ww]arning:' higher-cd-compilation.log; then
        printf '%s\n' 'Compiler warning diagnostic rejected' >&2
        exit 1
    fi
    printf '%s compiled\n' "$proof_source"
done < higher-source-order.txt

"$ROCQ_BIN" repl -quiet \
    -R theories OpenGororoba -R verified OpenGororobaVerified \
    > higher-cd-assumptions.log 2>&1 <<'ROCQ'
From OpenGororobaVerified Require Import C1471_HigherCDTrilinearity.
Print Assumptions cd4096_assoc_trilinear.
Print Assumptions cd65536_assoc_trilinear.
Quit.
ROCQ

if grep -nE '(^|[[:space:]])(Error:|Fatal Error:)' \
    source-assumptions.log higher-cd-assumptions.log; then
    exit 1
fi

printf 'proof_probe_root=%s\n' "$PROOF_PROBE_ROOT"
