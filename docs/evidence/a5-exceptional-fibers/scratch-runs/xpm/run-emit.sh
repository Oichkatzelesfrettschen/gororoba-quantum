#!/bin/sh
set -eu
export PATH="$HOME/a5env/bin:$HOME/a5env/lib/python3.13/site-packages/sage_wheels/bin:$PATH" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 GOROROBA_PARALLEL_DIR="$HOME/a5/gq"
cd "$HOME/a5/xpm"
for pr in "32009 10754" "32029 9115"; do
  set -- $pr
  python docs/evidence/a5-kernel-attachments/fiber_inputs.py emit --prime $1 --root $2 --slug xp-nm --slug xm-np --out "$HOME/a5/xpm/out" > emit-$1.log 2>&1 && echo "exit 0 $1" >> events || echo "exit $? $1" >> events
done
echo done >> events
