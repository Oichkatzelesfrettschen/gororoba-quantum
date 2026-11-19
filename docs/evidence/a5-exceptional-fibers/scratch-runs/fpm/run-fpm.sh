#!/bin/sh
# Fiber-to-Grassmannian fits: one run per (family, prime).
set -u
cd ~/a5/gq-main
export PATH="$HOME/a5env/bin:$PATH" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
out=~/a5/fpm
mkdir -p "$out"
for family in x x-same iso w8 e8; do
  for prime in 32009 32029; do
    name=fiber-plucker-map-$family-p$prime
    /usr/bin/time -v ~/a5env/bin/python docs/evidence/a5-exceptional-fibers/kernel-limits/fiber_plucker_map.py \
      "$family" --prime "$prime" --fit 320 --held-out 40 --out "$out/$name.json" > "$out/$name.log" 2>&1
    echo "$name rc=$?" >> "$out/summary"
  done
done
touch "$out/done"
