set -u
D=$HOME/a5/wsqr-qi/diag; PATH=$HOME/a5env/bin:$PATH; export PATH
python -B $D/diag2.py $D w8 N- > $D/regen2.log 2>&1 || { echo regen-fail > $D/done2; exit; }
n=$(cat $D/cell.n)
sed -e "s/NVARS/$n/" -e "s#POLYS#$D/cell.polys.txt#" $D/greedy3.sing > $D/greedy3-run.sing
timeout -k 30 2400 prlimit --as=8589934592 Singular -q --no-warn --no-rc $D/greedy3-run.sing > $D/greedy3.log 2>&1
echo "exit=$?" > $D/done2
