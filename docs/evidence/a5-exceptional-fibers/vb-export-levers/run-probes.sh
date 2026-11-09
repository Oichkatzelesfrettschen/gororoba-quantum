#!/bin/sh
# Times std(J + m^N) for E8-bar -> VB at p = 32009 under four global-ordering variants; each run is capped at 3600 s
# by its own systemd scope (RuntimeMaxSec kills the whole cgroup), N = 15 first, then N = 16.
set -eu
cd "$(dirname "$0")"
for N in 15 16; do
  for v in base noredtail slimgb incremental; do
    systemd-run --user --scope --quiet -p MemoryMax=8G -p MemorySwapMax=0 -p RuntimeMaxSec=3600 \
      /usr/bin/time -v -o "vb-n$N-$v.time" Singular -q --no-rc "vb-n$N-$v.sing" > "vb-n$N-$v.log" 2>&1 &
  done
  wait
done
echo "probes done"
