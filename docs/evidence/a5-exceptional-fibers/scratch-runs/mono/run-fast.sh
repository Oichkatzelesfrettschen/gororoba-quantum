#!/bin/sh
# Same-sign X monomial ladder on the float64 batched echelon: one run per (degree, order), memory-capped.
set -u
cd ~/a5/gq-main
export PATH="$HOME/a5env/bin:$PATH" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
out=~/a5/fast
mkdir -p "$out"
for spec in "6 26" "6 28" "7 29" "7 31" "8 32" "8 34"; do
  set -- $spec
  name=xm-nm-p32009-d$1-n$2
  /usr/bin/time -v systemd-run --user --scope -q -p MemoryMax=40G -p MemorySwapMax=0 \
    ~/a5env/bin/python ~/a5/mono/fast_ladder.py --degree "$1" --order "$2" --threads 24 \
    --out "$out/$name.json" > "$out/$name.log" 2>&1
  echo "$name rc=$?" >> "$out/summary"
done
touch "$out/done"
