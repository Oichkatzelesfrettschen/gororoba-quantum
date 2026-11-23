#!/bin/sh
# degree-2 receipt of E8-bar -> N+ at p = 32009, root of -1 = 21255, calibrated on X- -> N- first.
set -u
BASE=$HOME/a5-ff/out/e8np-d2-r21255
REPO=$HOME/a5-ff/repo
PYTHON=$HOME/venvs/a5/bin/python
export PYTHON GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 PYTHONDONTWRITEBYTECODE=1
mkdir -p "$BASE"
cd "$REPO" || { echo "EXIT 2 no repo" > "$BASE/EXIT"; exit 2; }
echo "SOURCE commit 78c5e5c3a1eca10cb68389c6a6b722233eb2dc87 (rsync copy, no git metadata)" > "$BASE/run.log"
"$PYTHON" --version >> "$BASE/run.log" 2>&1; Singular --version </dev/null | head -n 1 >> "$BASE/run.log"
CAL=docs/evidence/a5-exceptional-fibers/working/build/inputs/p32009-r10754
INP=docs/evidence/a5-exceptional-fibers/working/build/inputs/p32009-r21255
sha256sum "$CAL/xm-nm.sing" "$INP/e8-np.sing" >> "$BASE/run.log"
echo "START calibration $(date -u +%FT%TZ)" >> "$BASE/run.log"
/usr/bin/time -v -o "$BASE/calib.time" "$PYTHON" docs/evidence/a5-kernel-attachments/fiber_cone_driver.py --header "$CAL/xm-nm.sing" --degree 2 --out "$BASE/calib-xm-nm/d2" --prime 32009 --memory-gib 4 --timeout 1800 > "$BASE/calib.log" 2>&1 </dev/null
rc=$?
echo "calibration driver rc $rc" >> "$BASE/run.log"
got=$(sha256sum "$BASE/calib-xm-nm/d2/relations-upto-d2.rel" 2>/dev/null | cut -d' ' -f1)
want=596c48a75c5101f4aeca9da7cd89888f5270abf628aa6f1567160f778e583245
echo "CALIBRATION xm-nm relations sha256 $got want $want" >> "$BASE/run.log"
if [ "$rc" != 0 ] || [ "$got" != "$want" ]; then echo "EXIT 3 calibration failed" > "$BASE/EXIT"; exit 3; fi
echo "CALIBRATION PASS" >> "$BASE/run.log"
echo "START e8-np $(date -u +%FT%TZ)" >> "$BASE/run.log"
/usr/bin/time -v -o "$BASE/e8-np.time" "$PYTHON" docs/evidence/a5-kernel-attachments/fiber_cone_driver.py --header "$INP/e8-np.sing" --degree 2 --out "$BASE/e8-np/d2" --prime 32009 --memory-gib 12 --timeout 21600 > "$BASE/e8-np.log" 2>&1 </dev/null
rc=$?
echo "END e8-np rc $rc $(date -u +%FT%TZ)" >> "$BASE/run.log"
echo "EXIT $rc" > "$BASE/EXIT"
exit $rc
