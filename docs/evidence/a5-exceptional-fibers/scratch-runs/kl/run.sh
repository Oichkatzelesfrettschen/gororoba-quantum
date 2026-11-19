#!/bin/sh
set -u
export PATH=$HOME/a5env/lib/python3.13/site-packages/sage_wheels/bin:$PATH
export PYTHON=$HOME/a5env/bin/python
cd $HOME/a5/gq-repo
for fam in e8 x; do
  $PYTHON docs/evidence/a5-exceptional-fibers/kernel-limits/plucker_limits.py $fam --out $HOME/a5/kl/$fam-result.json > $HOME/a5/kl/$fam.log 2>&1
  echo "$fam rc=$?" >> $HOME/a5/kl/done.txt
done
echo finished >> $HOME/a5/kl/done.txt
