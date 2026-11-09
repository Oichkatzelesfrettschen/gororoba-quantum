#!/bin/sh
# Times std(J + m^N) for E8-bar -> VB at p = 32009 under four global-ordering variants; each run is capped at 3600 s
# by its own systemd scope (RuntimeMaxSec kills the whole cgroup), N = 15 first, then N = 16. Singular reads a
# non-terminal stdin, so every call takes /dev/null; each child's exit status lands in <tag>.status.
set -eu
cd "$(dirname "$0")"
for N in 15 16; do
  for v in base noredtail slimgb incremental; do
    (
      rc=0
      systemd-run --user --scope --quiet -p MemoryMax=8G -p MemorySwapMax=0 -p RuntimeMaxSec=3600 \
        /usr/bin/time -v -o "vb-n$N-$v.time" Singular -q --no-rc "vb-n$N-$v.sing" \
        < /dev/null > "vb-n$N-$v.log" 2>&1 || rc=$?
      echo "$rc" > "vb-n$N-$v.status"
    ) &
  done
  wait
done
for f in vb-n1[56]-*.status; do printf '%s %s\n' "$f" "$(cat "$f")"; done
