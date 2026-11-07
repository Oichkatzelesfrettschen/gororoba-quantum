#!/bin/sh
# Iso -> N- sliced blowup chart, junk-component saturation, p = 32009, beside the W8 engine on the same FX4:
# passagemath Singular 4.4.1, one thread, 55 GB memory scope, 22 h limit, RSS sampled every 60 s.
set -eu
cd "$HOME/a5iso"
SING=$(ls "$HOME"/pmvenv/lib/python3*/site-packages/sage_wheels/bin/Singular)
( while :; do echo "$(date -u +%FT%TZ) $(ps -o rss= -C Singular | awk '{s+=$1} END {print s}')" >> rss.txt; sleep 60; done ) &
sampler=$!
rc=0
/usr/bin/time -v timeout 79200 "$SING" -q --no-rc chart-ckpt.sing > chart.log 2> chart.err < /dev/null || rc=$?
kill "$sampler" 2>/dev/null || true
echo "$(date -u +%FT%TZ) iso slice-junk exit $rc" >> events
