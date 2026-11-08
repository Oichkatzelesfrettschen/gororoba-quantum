#!/bin/sh
# usage: sh cell.sh TAG LIMIT D N [WRAP_OPTS...]   engine flags of the W8 degree-6 case at the given d, N
set -eu
tag=$1; limit=$2; d=$3; n=$4; shift 4
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/../../.." && pwd)
E=docs/evidence/a5-exceptional-fibers
H=$E/working/build/inputs/p32009-r10754/w8-nm.sing
REC=$E/working/distribute/out/a5-w8-receipt-p1/w8_p1/d2/receipt-d2.json
SINGULAR=${SINGULAR:-$(ls "$HOME"/.cache/gororoba-quantum/venv-passagemath-singular/lib/python3*/site-packages/sage_wheels/bin/Singular)}
export SINGULAR
cd "$root"
exec sh "$here/run.sh" "$tag" "$limit" "$@" -- "$H" "$d" "$n" --quotient --k2-receipt "$REC" \
    --export-dir "${EXPORT_DIR:-$here/exports/n$n}" --export-chunks 5 --dense-tables-gb 0 --singular "$SINGULAR" ${ENGINE_EXTRA:-}
