#!/bin/sh
# Engine v13 (slimgb export) quotient-mode ranks of E8-bar -> VB degree 7, raw, one cell per argument
# DIR:STEM:D:N:P (header DIR/STEM.sing), all cells at once on the Windows workstation. Each record is written to
# out/<tag>.json.part and renamed only after a zero exit, so an interrupted cell never reads as finished; each exit
# goes to out/cells.events. Memory: --max-gb 12 per cell bounds the engine's selected-array estimate only, so four
# cells declare 48 GiB of the 52.5 GB budget while the Singular export and total resident memory stay uncapped; the
# measured peak of a degree-7 cell is 3.5 GiB (out/*.time). Cells of one header, prime and N share an export
# directory, which the engine locks for one process, so the script refuses two such cells in one call. Exits
# nonzero when any cell fails.
set -eu
if [ "$#" -gt 4 ]; then echo "at most four cells (52.5 GB budget at --max-gb 12)" >&2; exit 2; fi
exports=$(for cell in "$@"; do printf '%s\n' "$cell" | awk -F: '{print $2 "-p" $5 "-n" $4}'; done | sort | uniq -d)
if [ -n "$exports" ]; then echo "cells share an export directory, run them in sequence: $exports" >&2; exit 2; fi
export PATH="$HOME/a5env/bin:$PATH" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 MALLOC_ARENA_MAX=2
export GOROROBA_PARALLEL_DIR="$HOME/a5/gq" GOROROBA_WORKERS=4
export SINGULAR="$HOME/a5env/lib/python3.13/site-packages/sage_wheels/bin/Singular"
PYTHON=$HOME/a5env/bin/python
cd "$HOME/a5/engine/v13"
mkdir -p out
ev=out/cells.events
for cell in "$@"; do
  (
    IFS=: read -r dir stem d n p <<CELL
$cell
CELL
    tag=$(printf %s "$stem" | tr -d -)_d${d}_n${n}_p${p}
    if [ -s "out/$tag.json" ]; then exit 0; fi
    echo "$(date -u +%FT%TZ) start $tag" >> "$ev"
    rc=0
    /usr/bin/time -f "wall %e s maxrss %M KiB" -o "out/$tag.time" \
      timeout 86400 "$PYTHON" fiber_rank_v13.py "$dir/$stem.sing" "$d" "$n" --quotient \
      --export-dir "$HOME/a5/exports/$stem-p$p-n$n-v13" --export-chunks 5 --dense-tables-gb 0 --max-gb 12 \
      > "out/$tag.json.part" 2> "out/$tag.err" < /dev/null || rc=$?
    [ "$rc" -eq 0 ] && mv "out/$tag.json.part" "out/$tag.json"
    echo "$(date -u +%FT%TZ) exit $rc $tag" >> "$ev"
    exit "$rc"
  ) &
  pids="${pids:-} $!"
done
fail=0
for pid in $pids; do wait "$pid" || fail=1; done
exit "$fail"
