#!/bin/sh
# Laptop queue for engine v7: lane A (E8-bar -> N- degree 4, then X- degree 5) under the exclusive memory lock,
# lane B (E8-bar -> VB degree 5) under a shared lock of its own. Headers are the p32009-r10754 build headers.
set -u
cd "$HOME/a5/engine" || exit 1
export PATH="$HOME/a5env/bin:$PATH" PYTHON="$HOME/a5env/bin/python"
export SINGULAR="$HOME/a5env/lib/python3.13/site-packages/sage_wheels/bin/Singular"
export GOROROBA_PARALLEL_DIR="$HOME/a5/gq" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 MALLOC_ARENA_MAX=2
H=v7in
(
  flock .mem.lock sh ladder-v7.sh e8nm_d4_v7.jsonl 495 "$H/e8-nm.sing" 4 --quotient -- 12 13 14 15 16
  [ -e xm_d5_skip ] || flock .mem.lock sh ladder-v7.sh xm_d5_v7.jsonl 417 "$H/xm-nm.sing" 5 --quotient -- 19 20 21
) &
a=$!
flock -s .vb.lock sh ladder-v7.sh vb_d5_v7.jsonl 266 "$H/e8-vb.sing" 5 --quotient --max-gb 8 -- 16 17 18 &
b=$!
wait "$a"; wait "$b"
date -u +%FT%TZ > queue4.done
