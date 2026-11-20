#!/bin/sh
# Rerun of two fiber-map records after the parallel fit dispatch and the nonzero-image check; outputs must equal fpm2.
set -u
cd ~/a5/gq-main
export PATH="$HOME/a5env/bin:$PATH" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
out=~/a5/fpm4
mkdir -p "$out"
for spec in "x-same 32009" "e8 32029"; do
  set -- $spec
  name=fiber-plucker-map-$1-p$2
  ~/a5env/bin/python docs/evidence/a5-exceptional-fibers/kernel-limits/fiber_plucker_map.py "$1" --prime "$2" --fit 320 --held-out 40 --out "$out/$name.json" > "$out/$name.log" 2>&1
  echo "$name rc=$? same=$(cmp -s "$out/$name.json" ~/a5/fpm2/$name.json && echo yes || echo no)" >> "$out/summary"
done
touch "$out/done"
