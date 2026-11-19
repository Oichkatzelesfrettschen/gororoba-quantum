#!/bin/sh
# E8-bar -> N- ladder: find the truncation order at which degree 3 reaches 225 and degree 4 reaches 495.
set -u
cd ~/a5/gq-main
export PATH="$HOME/a5env/bin:$PATH" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
out=~/a5/e8close
mkdir -p "$out"
for spec in "3 14" "3 16" "3 18" "4 18" "4 20" "3 20" "4 22"; do
  set -- $spec
  name=e8-nm-p32009-d$1-n$2
  /usr/bin/time -v systemd-run --user --scope -q -p MemoryMax=44G -p MemorySwapMax=0 \
    ~/a5env/bin/python ~/a5/mono/fast_ladder2.py --slug e8-nm --prime 32009 --degree "$1" --order "$2" --threads 28 \
    --out "$out/$name.json" > "$out/$name.log" 2>&1
  echo "$name rc=$?" >> "$out/summary"
done
touch "$out/done"
