#!/bin/sh
# Run the Singular comparisons of the restricted W8 ideal J against each A_4 zero-divisor ideal.
# usage: sh run.sh WORKDIR [FAMILY STAGE]  (default: the controls, then every family and stage, serially)
# The Pfaffian ideals PA and PAp are regenerated into WORKDIR by a5_w8_a4_restriction.py --work WORKDIR.
set -eu

HERE=$(cd "$(dirname "$0")" && pwd)
WORK=${1:?usage: run.sh WORKDIR [FAMILY STAGE]}
mkdir -p "$WORK"
SINGULAR=${SINGULAR:-$(ls "$HOME"/.cache/gororoba-quantum/venv-passagemath-singular/lib/python3*/site-packages/sage_wheels/bin/Singular)}
MEM=${MEM:-24G}
LIMIT=${LIMIT:-7200}
export MALLOC_ARENA_MAX=2
# capped GIB CMD...: a cgroup scope (MemoryMax, no swap) where the user bus answers, else an address-space limit.
capped() {
    gib=${1%G}; shift
    if [ -S "${XDG_RUNTIME_DIR:-/nonexistent}/bus" ]; then
        systemd-run --user --scope -q -p MemoryMax="${gib}G" -p MemorySwapMax=0 "$@"
    else
        prlimit --as=$((gib * 1073741824)) "$@"
    fi
}

run_one() {
  fam=$1
  stage=$2
  log="$HERE/log_${fam}_stage${stage}.txt"
  drv="$WORK/drv_${fam}_${stage}.sing"
  if [ "$fam" = PB ]; then ideal="$HERE/ideal_PB.sing"; else ideal="$WORK/ideal_${fam}.sing"; fi
  if [ "$fam" = controls ]; then
    {
      printf '< "%s/ring.sing";\n< "%s/ideal_J.sing";\n< "%s/ideal_PB.sing";\n' "$HERE" "$HERE" "$HERE"
      printf '< "%s/ideal_Jsign.sing";\n< "%s/ideal_Jnopure.sing";\n< "%s/controls.sing";\n' "$HERE" "$HERE" "$HERE"
    } > "$drv"
  else
    {
      printf '< "%s/ring.sing";\n< "%s/ideal_J.sing";\n< "%s";\nint stage = %s;\n< "%s/compare.sing";\n' \
        "$HERE" "$HERE" "$ideal" "$stage" "$HERE"
    } > "$drv"
  fi
  {
    echo "family $fam stage $stage"
    echo "binary Singular (passagemath venv)"
    "$SINGULAR" -v -q --execute 'quit;' < /dev/null | head -1
    echo "memory cap $MEM (cgroup MemoryMax, MemorySwapMax=0), wall cap ${LIMIT} s"
    date -u +%Y-%m-%dT%H:%M:%SZ
  } > "$log"
  set +e
  capped "$MEM" timeout -k 10 "$LIMIT" /usr/bin/time -v "$SINGULAR" -q --no-warn "$drv" < /dev/null >> "$log" 2>&1
  status=$?
  set -e
  echo "exit status $status" >> "$log"
  date -u +%Y-%m-%dT%H:%M:%SZ >> "$log"
  return "$status"
}

if [ $# -ge 3 ]; then
  run_one "$2" "$3"
else
  # Every stage runs even after a failure (the PB stage-4 decomposition is known to reach its wall cap); the runner
  # then exits with the first nonzero stage status.
  first=0
  run_one controls 1 || first=$?
  for fam in PB PA PAp; do
    for stage in 1 2 3 4; do
      rc=0
      run_one "$fam" "$stage" || rc=$?
      [ "$first" -ne 0 ] || first=$rc
    done
  done
  exit "$first"
fi
