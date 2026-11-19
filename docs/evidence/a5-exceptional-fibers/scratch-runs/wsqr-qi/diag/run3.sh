set -u
D=$HOME/a5/wsqr-qi/diag; PATH=$HOME/a5env/bin:$PATH; export PATH
sed -e "s/NVARS/24/" -e "s#POLYS#$D/cell.polys.txt#" $D/chart.sing > $D/chart-run.sing
( while :; do echo "$(date +%T) $(ps -C Singular -o rss= | sort -n | tail -1) $(free -m | awk '/Mem/{print $3}')" >> $D/mem3.log; sleep 10; done ) & S=$!
timeout -k 30 1500 prlimit --as=8589934592 Singular -q --no-warn --no-rc $D/chart-run.sing > $D/chart.log 2>&1
echo "exit=$?" > $D/done3; kill $S
