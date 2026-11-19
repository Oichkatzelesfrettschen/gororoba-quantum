#!/bin/sh
# Degree-3 membership-receipt cost probe for E8-bar -> N- at p = 32009: normal forms of the 225 K2-standard cubic
# products modulo std(J + m S) and their exact rank (must be 225, zero relations); Singular capped at 24 GiB.
set -eu
export PATH="$HOME/a5env/bin:$HOME/a5env/lib/python3.13/site-packages/sage_wheels/bin:$PATH" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 MALLOC_ARENA_MAX=2
export GOROROBA_PARALLEL_DIR="$HOME/a5/gq"
PYTHON=$HOME/a5env/bin/python
cd "$HOME/a5/rcpt"
echo "$(date -u +%FT%TZ) start d=3" >> events
if /usr/bin/time -f "wall %e s maxrss %M KiB" -o time-d3 "$PYTHON" docs/evidence/a5-kernel-attachments/fiber_cone_driver.py \
    --header in/e8-nm.sing --degree 3 --previous-relations in/relations-upto-d2.rel --out out-d3 --prime 32009 \
    --memory-gib 24 --timeout 21600 > driver-d3.log 2>&1; then
    echo "$(date -u +%FT%TZ) exit 0 d=3" >> events
else
    echo "$(date -u +%FT%TZ) exit $? d=3" >> events
fi
