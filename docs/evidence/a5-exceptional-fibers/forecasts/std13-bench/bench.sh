#!/bin/sh
# Same std (J + m^13, E8-bar -> N- header p32009) under Ubuntu's Singular 4.3.2 and the passagemath 4.4.1 build.
set -eu
cd "$HOME/a5"
P="$HOME/pmvenv/lib/python3.12/site-packages/sage_wheels/bin/Singular"
( timeout 7200 Singular -q --no-rc std13.sing < /dev/null 2>&1 | grep STD13 > bench-ubuntu.txt || true ) &
( timeout 7200 "$P" -q --no-rc std13.sing < /dev/null 2>&1 | grep STD13 > bench-pm.txt || true ) &
wait
echo done > bench.done
