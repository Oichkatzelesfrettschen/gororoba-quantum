#!/bin/sh
# The y-degree-1 blocks of the Rees ideal of E8-bar at N- at three values of s2 and over the function field in s2,
# modulo 32009 and 32029. Run from the repository root with Singular on PATH. Writes into OUT (default a rerun/
# directory beside this script) and leaves the retained logs alone. Exits nonzero unless every unit ends without a
# Singular error line, reads 75 occupied blocks and 32 minimal generators in the retained 11 bidegrees, and its
# RESULT lines equal those of the retained log apart from the timing and memory lines.
set -eu
PYTHON=${PYTHON:-python3}
export PYTHON PYTHONDONTWRITEBYTECODE=1
D=docs/evidence/a5-exceptional-fibers/working/runs/e8-nm-rees-generic-blocks
OUT=${OUT:-$D/rerun}
mkdir -p "$OUT"
WANT='4,2:2 5,1:1 5,2:6 5,3:6 5,4:1 6,2:3 6,3:5 6,4:3 7,3:2 7,4:2 8,4:1 '
facts() { # log: the RESULT lines that do not depend on the run
  grep '^RESULT' "$1" | grep -v -e '_ms' -e 'vmhwm_kb' | sed 's/ ms_span.*//'
}
sing() { # stem
  rc=0
  Singular -q --no-warn --no-rc "$OUT/$1.sing" > "$OUT/$1.log" < /dev/null || rc=$?
  echo "EXIT $rc" >> "$OUT/$1.log"
  if grep -q '^ *?' "$OUT/$1.log"; then
    echo "run_blocks: Singular error line in $1.log" >&2
    exit 1
  fi
  [ "$rc" -eq 0 ]
  grep -q '^RESULT done 1$' "$OUT/$1.log"
}
for pr in "32009 10754" "32029 9115"; do
  p=${pr% *}
  i=${pr#* }
  sed "s/@P@/$p/g; s/@I@/$i/g" "$D/stage_a.tmpl" > "$OUT/stageA-p$p.sing"
  sing "stageA-p$p"
  grep -E '^(JGEN|GGEN|RESULT)' "$D/stageA-p$p.log" > "$OUT/stageA.want"
  grep -E '^(JGEN|GGEN|RESULT)' "$OUT/stageA-p$p.log" | cmp -s - "$OUT/stageA.want"
  for v in 7013 21890 3567 generic; do
    "$PYTHON" "$D/gen_blocks.py" "$p" "$i" "$v" "$OUT/stageA-p$p.log" > "$OUT/deg1-p$p-$v.sing"
    sing "deg1-p$p-$v"
    grep -q '^RESULT occupied_blocks = 75$' "$OUT/deg1-p$p-$v.log"
    grep -q '^RESULT minimal_new_generators_total = 32$' "$OUT/deg1-p$p-$v.log"
    grep -q '^RESULT blocks_where_kernel_module_count_differs_from_rankE = 0$' "$OUT/deg1-p$p-$v.log"
    got=$(grep -E 'minimal_new [1-9]' "$OUT/deg1-p$p-$v.log" | sed 's/RESULT block1 //; s/ = N.*minimal_new /:/; s/ qK.*//' | tr '\n' ' ')
    [ "$got" = "$WANT" ]
    facts "$D/deg1-p$p-$v.log" > "$OUT/facts.want"
    facts "$OUT/deg1-p$p-$v.log" | cmp -s - "$OUT/facts.want"
  done
done
echo "run_blocks: ok"
