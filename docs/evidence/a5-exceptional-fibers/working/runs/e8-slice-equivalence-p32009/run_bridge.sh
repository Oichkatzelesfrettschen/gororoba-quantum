#!/bin/sh
# slice_bridge.py and its Singular verification on the two E8-bar cells; run from the repository root.
# Exits nonzero unless both cells print "BRIDGE VERDICT cell CELL PASS".
set -eu
D=docs/evidence/a5-exceptional-fibers/working/runs/e8-slice-equivalence-p32009
K=docs/evidence/a5-exceptional-fibers/working/runs/e8-rees-fibers-v2-kcompare-p32009
PYTHON=${PYTHON:-python3}
export PYTHON PYTHONDONTWRITEBYTECODE=1
for c in e8-nm e8-np; do
  {
    "$PYTHON" --version
    "$PYTHON" -c 'import flint, numpy; print("python-flint", flint.__version__, "numpy", numpy.__version__)'
    sha256sum "$D/slice_bridge.py" "$K/KA-$c.sing" "$K/KH-$c.sing"
  } > "$D/bridge-$c.log" 2>&1
  /usr/bin/time -v -o "$D/bridge-$c.time" "$PYTHON" "$D/slice_bridge.py" "$c" "$K/KA-$c.sing" "$K/KH-$c.sing" \
    "$D/bridge-$c.json" >> "$D/bridge-$c.log" 2>&1
  echo "EXIT 0" >> "$D/bridge-$c.log"
  sed -i "s#$HOME[^ \"]*/venv#VENV#g; s#$HOME#~#g" "$D/bridge-$c.time"
  "$PYTHON" "$D/bridge_verify.py" "$c" "$D/bridge-$c.json" "$K/KA-$c.sing" "$K/KH-$c.sing" \
    "$D/bridge-verify-$c.sing" >> "$D/bridge-$c.log" 2>&1
  {
    Singular --version < /dev/null | head -n 1
    sha256sum "$D/bridge-verify-$c.sing"
  } > "$D/bridge-verify-$c.log"
  Singular -q --no-warn "$D/bridge-verify-$c.sing" < /dev/null >> "$D/bridge-verify-$c.log" 2>&1
  grep -q "^BRIDGE VERDICT cell $c PASS$" "$D/bridge-verify-$c.log"
done
echo "run_bridge: PASS"
