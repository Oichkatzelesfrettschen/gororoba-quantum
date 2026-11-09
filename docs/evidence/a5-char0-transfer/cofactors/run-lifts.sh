#!/bin/sh
# Modular lift of the X- -> N- degree-2 relations at both split primes, one prime at a time (each about 16.5 GB),
# each capped at 3600 s and 24 GiB by its own systemd scope. Singular takes stdin from /dev/null; each prime's exit
# status lands in lift-xm-nm-p<p>.status, and the script exits nonzero when either lift fails.
set -eu
cd "$(dirname "$0")"
fail=0
for p in 32029 32009; do
  rc=0
  systemd-run --user --scope --quiet -p MemoryMax=24G -p MemorySwapMax=0 -p RuntimeMaxSec=3600 \
    /usr/bin/time -v -o "lift-xm-nm-p$p.time" Singular -q --no-rc "lift-xm-nm-p$p.sing" \
    < /dev/null > "lift-xm-nm-p$p.log" 2>&1 || rc=$?
  echo "$rc" > "lift-xm-nm-p$p.status"
  [ "$rc" -eq 0 ] || fail=1
done
exit "$fail"
