#!/bin/sh
# Rerun the three kernel-limit records with the patched scripts and compare each with the retained record.
set -u
cd ~/a5/gq-kl
out=~/a5/kl-out; mkdir -p "$out"; rm -f "$out/done"; : > "$out/summary.txt"
export PATH="$HOME/a5env/lib/python3.13/site-packages/sage_wheels/bin:$HOME/a5env/bin:$PATH" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
K=docs/evidence/a5-exceptional-fibers/kernel-limits
run() { t0=$(date +%s); ~/a5env/bin/python "$@" > "$out/$name.log" 2>&1; echo "$name rc=$? seconds=$(( $(date +%s) - t0 ))" >> "$out/summary.txt"; }
name=x; run $K/plucker_limits.py x --out "$out/x-opposite-result.json"
name=e8; run $K/plucker_limits.py e8 --out "$out/e8-result.json"
name=vb; run $K/vb_limit_span.py --out "$out/vb-limit-span-result.json"
for f in x-opposite-result e8-result vb-limit-span-result; do if cmp -s "$out/$f.json" "$K/$f.json"; then echo "$f identical to retained"; else echo "$f DIFFERS from retained"; fi; done >> "$out/summary.txt"
touch "$out/done"
