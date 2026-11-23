#!/bin/sh
# The y-degree-1 blocks of the Rees ideal of E8-bar at N- at three values of s2 and over the function field in s2,
# modulo 32009 and 32029. Run from the repository root with Singular on PATH. Exits nonzero unless every unit ends
# without a Singular error line and reads 75 occupied blocks and 32 minimal generators in 11 bidegrees with the
# retained distribution.
set -eu
PYTHON=${PYTHON:-python3}
export PYTHON PYTHONDONTWRITEBYTECODE=1
D=docs/evidence/a5-exceptional-fibers/working/runs/e8-nm-rees-generic-blocks
WANT='4,2:2 5,1:1 5,2:6 5,3:6 5,4:1 6,2:3 6,3:5 6,4:3 7,3:2 7,4:2 8,4:1 '
sing() { # stem
  rc=0
  Singular -q --no-warn --no-rc "$D/$1.sing" > "$D/$1.log" < /dev/null || rc=$?
  echo "EXIT $rc" >> "$D/$1.log"
  if grep -q '^ *?' "$D/$1.log"; then
    echo "run_blocks: Singular error line in $1.log" >&2
    exit 1
  fi
  [ "$rc" -eq 0 ]
  grep -q '^RESULT done 1$' "$D/$1.log"
}
for pr in "32009 10754" "32029 9115"; do
  p=${pr% *}
  i=${pr#* }
  sed "s/@P@/$p/g; s/@I@/$i/g" "$D/stage_a.tmpl" > "$D/stageA-p$p.sing"
  sing "stageA-p$p"
  for v in 7013 21890 3567 generic; do
    "$PYTHON" "$D/gen_blocks.py" "$p" "$i" "$v" "$D/stageA-p$p.log" > "$D/deg1-p$p-$v.sing"
    sing "deg1-p$p-$v"
    grep -q '^RESULT occupied_blocks = 75$' "$D/deg1-p$p-$v.log"
    grep -q '^RESULT minimal_new_generators_total = 32$' "$D/deg1-p$p-$v.log"
    grep -q '^RESULT blocks_where_kernel_module_count_differs_from_rankE = 0$' "$D/deg1-p$p-$v.log"
    got=$(grep -E 'minimal_new [1-9]' "$D/deg1-p$p-$v.log" | sed 's/RESULT block1 //; s/ = N.*minimal_new /:/; s/ qK.*//' | tr '\n' ' ')
    [ "$got" = "$WANT" ]
  done
done
echo "run_blocks: ok"
