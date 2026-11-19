set -u
D=$HOME/a5/wsqr-qi/diag
uptime > $D/load
python -B $D/diag.py $D > $D/regen.log 2>&1 || { echo regen-fail > $D/done; exit; }
n=$(cat $D/n 2>/dev/null || cat $D/xm-N-.n)
sed -e "s/NVARS/$n/" -e "s#POLYS#$D/xm-N-.polys.txt#" $D/greedy.sing > $D/greedy-run.sing
timeout -k 30 2400 prlimit --as=8589934592 Singular -q --no-warn --no-rc $D/greedy-run.sing > $D/greedy.log 2>&1
echo "exit=$?" > $D/done
