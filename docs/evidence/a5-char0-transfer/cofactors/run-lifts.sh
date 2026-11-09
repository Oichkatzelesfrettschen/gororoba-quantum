#!/bin/sh
# Modular lift of the X- -> N- degree-2 relations at both split primes, one prime at a time (each about 16.5 GB),
# each capped at 3600 s and 24 GiB by its own systemd scope.
set -eu
cd "$(dirname "$0")"
for p in 32029 32009; do
  systemd-run --user --scope --quiet -p MemoryMax=24G -p MemorySwapMax=0 -p RuntimeMaxSec=3600 \
    /usr/bin/time -v -o "lift-xm-nm-p$p.time" Singular -q --no-rc "lift-xm-nm-p$p.sing" > "lift-xm-nm-p$p.log" 2>&1 || true
done
echo "lifts done"
