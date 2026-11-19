#!/bin/sh
# Engine v9 at E8-bar -> N- degree 4, N = 15 on the laptop, from the export rescued from the serial v7 run.
# Once every v9 table and the generator file exist, stop the serial lane (ladder shell first, with KILL so its TERM
# trap cannot let it continue to N = 16; then time, python and Singular), so a single products stage runs.
set -eu
cd "$HOME/a5/engine"
export PATH="$HOME/a5env/bin:$PATH" PYTHON="$HOME/a5env/bin/python"
export SINGULAR="$HOME/a5env/lib/python3.13/site-packages/sage_wheels/bin/Singular"
export GOROROBA_PARALLEL_DIR="$HOME/a5/gq" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 MALLOC_ARENA_MAX=2
export GOROROBA_WORKERS=25
ex=$HOME/a5/exports/e8nm-p32009-n15-v9
out=$HOME/a5/engine/v9
log=$out/e8nm_d4_n15.events
mkdir -p "$ex" "$out"
for f in "$HOME"/a5/exports/e8nm-p32009-n15/q*; do
  [ -e "$ex/${f##*/}" ] || cp "$f" "$ex/"
done
note() { printf '%s %s\n' "$(date -u +%FT%TZ)" "$*" >> "$log"; }
note "start; adopted: $(cd "$ex" && ls q* | tr '\n' ' ')"
/usr/bin/time -f "wall %e s maxrss %M KiB" -o "$out/e8nm_d4_n15.time" \
  "$PYTHON" fiber_rank_v9.py v7in/e8-nm.sing 4 15 --quotient --export-dir "$ex" --adopt-export --export-chunks 3 \
  > "$out/e8nm_d4_n15.json" 2> "$out/e8nm_d4_n15.err" &
v9=$!
done_tables() {
  for k in 1 2 3 4 5 6 7 8 9; do [ -e "$ex/qM$k.txt" ] || return 1; done
  [ -e "$ex/qG.txt" ]
}
stopped=0
while kill -0 "$v9" 2>/dev/null; do
  if [ "$stopped" = 0 ] && done_tables; then
    if ps -o args= -p 10405 2>/dev/null | grep -q "ladder-v7.sh e8nm_d4_v7.jsonl"; then
      kill -KILL 10405
      for pid in $(pgrep -f "fiber_rank_v7.py v7in/e8-nm.sing 4 15" || true) $(pgrep -f "/tmp/tmplqzy1aif/q.sing" || true); do
        kill -TERM "$pid" 2>/dev/null || true
      done
      note "v9 tables complete; serial lane stopped"
    else
      note "v9 tables complete; serial ladder already gone"
    fi
    systemctl --user stop a5-export-rescue-n15 2>/dev/null || true
    stopped=1
  fi
  sleep 30
done
wait "$v9" && note "v9 exit 0" || note "v9 exit $?"
