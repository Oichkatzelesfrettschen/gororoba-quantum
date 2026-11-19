set -u
OUT=$HOME/a5/wsqr-qi
PATH=$HOME/a5env/bin:$PATH; export PATH
uptime > $OUT/full.load
nice -n 5 python -B docs/evidence/a5-kernel-attachments/weight_slice_quadric_rings.py --out $OUT/full.json --steps $OUT/steps-full > $OUT/full.log 2>&1
echo "exit=$?" > $OUT/full.done
