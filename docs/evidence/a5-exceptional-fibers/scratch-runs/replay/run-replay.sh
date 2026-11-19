#!/bin/sh
# v8 replay of the A5 fiber manifest (32 of 33 entries; E8-N--32029-d4-N15 needs a 91 GiB cap and stays out),
# started after both N = 17 units finish so no replay scope shares RAM with an N = 17 product stage.
set -eu
export PATH="$HOME/a5env/bin:$HOME/a5env/lib/python3.13/site-packages/sage_wheels/bin:$PATH" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 MALLOC_ARENA_MAX=2
export GOROROBA_PARALLEL_DIR="$HOME/a5/gq"
R="$HOME/a5/replay"
cd "$R/a5-exceptional-fibers"
while systemctl --user is-active -q a5-v11-e8nm-n17 || systemctl --user is-active -q a5-v11-e8nm-n17-p2; do sleep 300; done
echo "$(date -u +%FT%TZ) start" >> "$R/events"
while read -r id; do
  [ -n "$id" ] || continue
  if python replay/fiber_replay.py run "$R/out/$id" --budget-gb 50 --only "$id" > "$R/log-$id.txt" 2>&1; then
    echo "$(date -u +%FT%TZ) ok $id" >> "$R/events"
  else
    echo "$(date -u +%FT%TZ) fail $? $id" >> "$R/events"
  fi
done < "$HOME/a5/replay-ids.txt"
echo "$(date -u +%FT%TZ) done" >> "$R/events"
