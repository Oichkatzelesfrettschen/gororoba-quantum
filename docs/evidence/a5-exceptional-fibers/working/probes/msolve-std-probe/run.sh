#!/bin/sh
set -eu
cd "$(dirname "$0")"
/usr/bin/time -v msolve -t 4 -g 1 -v 2 -f jm11.ms -o msolve11.lead > msolve11.log 2> msolve11.time &
/usr/bin/time -v Singular -q --no-rc sing11.sing < /dev/null > sing11.log 2> sing11.time &
wait
echo done > done
