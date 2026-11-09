#!/bin/sh
# Run the Singular comparisons of the restricted W8 ideal J against each A_4 zero-divisor ideal.
# usage: sh run.sh WORKDIR [FAMILY STAGE]  (default: the controls, then every family and stage, JOBS at a time)
# The Pfaffian ideals PA and PAp are regenerated into WORKDIR by a5_w8_a4_restriction.py --work WORKDIR.
set -eu

HERE=$(cd "$(dirname "$0")" && pwd)
WORK=${1:?usage: run.sh WORKDIR [FAMILY STAGE]}
mkdir -p "$WORK"
SINGULAR=${SINGULAR:-$(ls "$HOME"/.cache/gororoba-quantum/venv-passagemath-singular/lib/python3*/site-packages/sage_wheels/bin/Singular)}
MEM=${MEM:-24G}
LIMIT=${LIMIT:-7200}
JOBS=${JOBS:-1}
export MALLOC_ARENA_MAX=2
have_bus() { [ -S "${XDG_RUNTIME_DIR:-/nonexistent}/bus" ]; }
if have_bus; then
    CAP_NOTE="cgroup MemoryMax, MemorySwapMax=0"
else
    CAP_NOTE="prlimit --as: per-process address space, not resident memory"
fi
# capped GIB CMD...: a cgroup scope (MemoryMax, no swap) where the user bus answers, else prlimit --as, which caps
# each process's virtual address space; a process pool under it can hold several times GIB of resident memory.
capped() {
    gib=${1%G}; shift
    if have_bus; then
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
    echo "memory cap $MEM ($CAP_NOTE), wall cap ${LIMIT} s"
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
  # The stages are independent Singular processes (each recomputes only std(J)); JOBS of them run at once, each under
  # its own MEM cap, so JOBS x MEM must fit the host. Every stage runs even after a failure (the PB stage-4
  # decomposition is known to reach its wall cap); the runner then exits with the first nonzero stage status.
  first=0 pids="" n=0
  for item in "controls 1" "PB 1" "PB 2" "PB 3" "PB 4" "PA 1" "PA 2" "PA 3" "PA 4" "PAp 1" "PAp 2" "PAp 3" "PAp 4"; do
    # shellcheck disable=SC2086
    run_one $item &
    pids="$pids $!" n=$((n + 1))
    if [ "$n" -ge "$JOBS" ]; then
      for pid in $pids; do rc=0; wait "$pid" || rc=$?; [ "$first" -ne 0 ] || first=$rc; done
      pids="" n=0
    fi
  done
  for pid in $pids; do rc=0; wait "$pid" || rc=$?; [ "$first" -ne 0 ] || first=$rc; done
  exit "$first"
fi
