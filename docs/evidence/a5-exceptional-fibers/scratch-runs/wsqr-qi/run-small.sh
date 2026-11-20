#!/bin/sh
set -u
OUT=$HOME/a5/wsqr-qi
PATH=$HOME/a5env/bin:$PATH; export PATH
uptime > $OUT/small.load
nice -n 5 timeout -k 30 5400 python -B docs/evidence/a5-kernel-attachments/weight_slice_quadric_rings.py --out $OUT/small.json --steps $OUT/steps --cells xm:N- > $OUT/small.log 2>&1
echo "exit=$?" > $OUT/small.done
