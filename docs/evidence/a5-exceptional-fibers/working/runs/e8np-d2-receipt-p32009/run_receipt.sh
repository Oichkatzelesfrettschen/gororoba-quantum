#!/bin/sh
# direct degree-2 receipt of E8-bar -> N+ at p = 32009 (i = 10754), calibrated on X- -> N- first.
set -u
BASE=$HOME/work/e8np-d2
REPO=$HOME/src/gororoba-quantum
PYTHON=$HOME/.cache/gororoba-quantum/ci-py3.14.7/bin/python3
export PYTHON GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
cd "$REPO" || { echo "EXIT 2 no repo" > "$BASE/EXIT"; exit 2; }
echo "HEAD $(git rev-parse HEAD) dirty=$(git status --short | wc -l)" > "$BASE/run.log"
"$PYTHON" --version >> "$BASE/run.log" 2>&1; Singular --version </dev/null | head -n 1 >> "$BASE/run.log"
INP=docs/evidence/a5-exceptional-fibers/working/build/inputs/p32009-r10754
sha256sum "$INP/xm-nm.sing" "$INP/e8-np.sing" >> "$BASE/run.log"
echo "START calibration $(date -u +%FT%TZ)" >> "$BASE/run.log"
taskset -c 3 /usr/bin/time -v -o "$BASE/calib.time" "$PYTHON" docs/evidence/a5-kernel-attachments/fiber_cone_driver.py --header "$INP/xm-nm.sing" --degree 2 --out "$BASE/calib-xm-nm/d2" --prime 32009 --memory-gib 4 --timeout 1800 > "$BASE/calib.log" 2>&1
rc=$?
echo "calibration driver rc $rc" >> "$BASE/run.log"
got=$(sha256sum "$BASE/calib-xm-nm/d2/relations-upto-d2.rel" 2>/dev/null | cut -d' ' -f1)
want=596c48a75c5101f4aeca9da7cd89888f5270abf628aa6f1567160f778e583245
echo "CALIBRATION xm-nm relations sha256 $got want $want" >> "$BASE/run.log"
if [ "$rc" != 0 ] || [ "$got" != "$want" ]; then echo "EXIT 3 calibration failed" > "$BASE/EXIT"; exit 3; fi
echo "CALIBRATION PASS" >> "$BASE/run.log"
echo "START e8-np $(date -u +%FT%TZ)" >> "$BASE/run.log"
taskset -c 3 /usr/bin/time -v -o "$BASE/e8-np.time" "$PYTHON" docs/evidence/a5-kernel-attachments/fiber_cone_driver.py --header "$INP/e8-np.sing" --degree 2 --out "$BASE/e8-np/d2" --prime 32009 --memory-gib 12 --timeout 14400 > "$BASE/e8-np.log" 2>&1
rc=$?
echo "END e8-np rc $rc $(date -u +%FT%TZ)" >> "$BASE/run.log"
echo "EXIT $rc" > "$BASE/EXIT"
exit $rc
