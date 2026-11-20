#!/bin/sh
# Local test at 0 of the swap t4<->t5, t6<->t7 (signs ++++ and ----) on the E8-bar -> N- slice; one Singular each.
set -eu
S="$HOME/a5env/lib/python3.13/site-packages/sage_wheels/bin/Singular"
cd "$HOME/a5/blockswap"
for t in "++++" "----"; do
  ( rc=0; timeout 21600 "$S" -q --no-rc "local-e8-nm-$t.sing" > "local-e8-nm-$t.log" 2>&1 < /dev/null || rc=$?; echo "exit $rc" >> "local-e8-nm-$t.log" ) &
done
wait
echo done > e8.done
