#!/bin/sh
export PATH=$HOME/a5env/lib/python3.13/site-packages/sage_wheels/bin:$PATH
cd $HOME/a5/gq-repo
$HOME/a5env/bin/python docs/evidence/a5-exceptional-fibers/kernel-limits/vb_limit_span.py --out $HOME/a5/kl/vb-result.json > $HOME/a5/kl/vb.log 2>&1
echo "vb rc=$?" > $HOME/a5/kl/vb-done.txt
