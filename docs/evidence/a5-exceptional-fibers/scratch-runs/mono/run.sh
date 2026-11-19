#!/bin/sh
# Monomial ladder of the same-sign X fiber cone: one run per (degree, order), each in a memory-capped scope.
set -u
cd ~/a5/gq-main
export PATH="$HOME/a5env/lib/python3.13/site-packages/sage_wheels/bin:$HOME/a5env/bin:$PATH" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
out=~/a5/mono
for spec in "6 26" "6 28" "7 29" "7 31"; do
  set -- $spec
  name=xm-nm-p32009-d$1-n$2
  /usr/bin/time -v systemd-run --user --scope -q -p MemoryMax=40G -p MemorySwapMax=0 \
    ~/a5env/bin/python docs/evidence/a5-exceptional-fibers/monomial-ladder/x_same_ladder.py \
    --slug xm-nm --prime 32009 --degree "$1" --order "$2" --out "$out/$name.json" > "$out/$name.log" 2>&1
  echo "$name rc=$?" >> "$out/summary"
done
touch "$out/done"
