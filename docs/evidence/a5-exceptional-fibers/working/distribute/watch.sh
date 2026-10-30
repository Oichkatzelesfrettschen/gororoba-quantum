#!/bin/sh
# Poll the distributed kernels until each ends or the deadline passes; download each output once.
set -eu
D=$1; DEADLINE=$(( $(date +%s) + $2 )); shift 2
LOG=$D/watch.log; fails=0; child=
cleanup() { [ -n "$child" ] && kill "$child" 2>/dev/null || true; }
trap cleanup EXIT; trap 'exit 130' INT TERM HUP
while :; do
  left=0
  for k in "$@"; do
    [ -e "$D/out/$k/.done" ] && continue
    left=$((left + 1))
    s=$(timeout -k 10 60 kaggle kernels status "probablyeric/$k" 2>&1 | tail -1) || { fails=$((fails + 1)); continue; }
    fails=0
    case "$s" in
      *COMPLETE*|*ERROR*|*CANCEL*)
        mkdir -p "$D/out/$k"
        timeout -k 10 600 kaggle kernels output "probablyeric/$k" -p "$D/out/$k" >/dev/null 2>&1 || true
        echo "$(date -u +%FT%TZ) $k $s" >> "$LOG"; : > "$D/out/$k/.done" ;;
    esac
  done
  [ "$left" -eq 0 ] && { tail -n "$#" "$LOG"; exit 0; }
  [ "$fails" -ge 10 ] && { echo "poll failures"; exit 3; }
  [ "$(date +%s)" -ge "$DEADLINE" ] && { echo "deadline; $left left"; tail -n 6 "$LOG" 2>/dev/null || true; exit 2; }
  sleep 600 & child=$!; wait "$child"; child=
done
