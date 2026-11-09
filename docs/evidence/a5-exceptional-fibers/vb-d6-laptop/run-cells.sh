#!/bin/sh
# Engine v11 quotient-mode ranks, raw, one cell per argument DIR:STEM:D:N:P (header DIR/STEM.sing), in order; each
# exit goes to out/cells.events and the runner exits with the first nonzero engine status. Memory: --max-gb 30 (the
# laptop budget is 36 GiB), 8 workers.
set -eu
export PATH="$HOME/a5env/bin:$PATH" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 MALLOC_ARENA_MAX=2
export GOROROBA_PARALLEL_DIR="$HOME/a5/gq" GOROROBA_WORKERS=8
export SINGULAR="$HOME/a5env/lib/python3.13/site-packages/sage_wheels/bin/Singular"
PYTHON=$HOME/a5env/bin/python
cd "$HOME/a5/engine/v11"
ev=out/cells.events
for cell in "$@"; do
    IFS=: read -r dir stem d n p <<CELL
$cell
CELL
    tag=$(printf %s "$stem" | tr -d -)_d${d}_n${n}_p${p}
    if [ -s "out/$tag.json" ]; then continue; fi
    echo "$(date -u +%FT%TZ) start $tag" >> "$ev"
    rc=0
    /usr/bin/time -f "wall %e s maxrss %M KiB" -o "out/$tag.time" \
        timeout 43200 "$PYTHON" fiber_rank_v11.py "$dir/$stem.sing" "$d" "$n" --quotient \
        --export-dir "$HOME/a5/exports/$stem-p$p-n$n-v11" --export-chunks 5 --dense-tables-gb 0 --max-gb 30 \
        > "out/$tag.json" 2> "out/$tag.err" < /dev/null || rc=$?
    echo "$(date -u +%FT%TZ) exit $rc $tag" >> "$ev"
    [ "$rc" -eq 0 ] || exit "$rc"
done
