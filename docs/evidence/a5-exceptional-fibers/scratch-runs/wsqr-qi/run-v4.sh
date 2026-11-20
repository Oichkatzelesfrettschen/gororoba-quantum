set -u
O=$HOME/a5/wsqr-qi; PATH=$HOME/a5env/bin:$PATH; export PATH
( while :; do echo "$(date +%T) $(uptime | sed 's/.*average: //') $(ps -C Singular -o rss= | sort -n | tail -1) $(free -m | awk '/Mem/{print $3}')" >> $O/v4-mem.log; sleep 30; done ) & S=$!
nice -n 5 python -B docs/evidence/a5-kernel-attachments/weight_slice_quadric_rings.py --out $O/v4.json --steps $O/steps-v3 > $O/v4.log 2>&1
echo "exit=$?" > $O/v4.done; kill $S
