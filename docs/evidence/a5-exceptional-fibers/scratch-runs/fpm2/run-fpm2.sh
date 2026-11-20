#!/bin/sh
# Fiber-to-Grassmannian fits with the mutation arm and verdict: one run per (header sign, family, prime).
set -u
cd ~/a5/gq-main
export PATH="$HOME/a5env/bin:$PATH" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
out=~/a5/fpm2
mkdir -p "$out"
for sign in "" plus; do
  for family in x x-same iso w8 e8; do
    for prime in 32009 32029; do
      name=fiber-plucker-map-$family${sign:+-$sign}-p$prime
      /usr/bin/time -v ~/a5env/bin/python docs/evidence/a5-exceptional-fibers/kernel-limits/fiber_plucker_map.py \
        "$family" ${sign:+--plus} --prime "$prime" --fit 320 --held-out 40 --out "$out/$name.json" > "$out/$name.log" 2>&1
      echo "$name rc=$?" >> "$out/summary"
    done
  done
done
touch "$out/done"
