#!/bin/sh
# The y-degree-1 blocks of the Rees ideal of E8-bar at N- at three values of s2 and over the function field in s2,
# modulo 32009 and 32029. Run from the repository root with Singular on PATH. Writes into OUT (default a rerun/
# directory beside this script) and leaves the retained logs alone. Exits nonzero unless every unit ends without a
# Singular error line, reads 75 occupied blocks and 32 minimal generators in the retained 11 bidegrees, and its
# RESULT lines equal those of the retained log apart from the timing and memory lines.
# The two stage-A units run first, then the eight block units, each set through gororoba_quantum/run_commands.py
# (parallel.ordered_map): GOROROBA_WORKERS caps the units running at once (default the available CPUs), and each
# unit compares against its own retained log and writes its own comparison file. A unit is
# "sh run_blocks.sh unit stageA P I" or "sh run_blocks.sh unit deg1 P I V".
set -eu
PYTHON=${PYTHON:-python3}
export PYTHON PYTHONDONTWRITEBYTECODE=1
D=docs/evidence/a5-exceptional-fibers/working/runs/e8-nm-rees-generic-blocks
OUT=${OUT:-$D/rerun}
export OUT
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
if [ "${1:-}" = unit ]; then
  case "$2" in
    stageA) # P I
      p=$3
      i=$4
      sed "s/@P@/$p/g; s/@I@/$i/g" "$D/stage_a.tmpl" > "$OUT/stageA-p$p.sing"
      sing "stageA-p$p"
      grep -E '^(JGEN|GGEN|RESULT)' "$D/stageA-p$p.log" > "$OUT/stageA-p$p.want"
      grep -E '^(JGEN|GGEN|RESULT)' "$OUT/stageA-p$p.log" | cmp -s - "$OUT/stageA-p$p.want"
      ;;
    deg1) # P I V
      p=$3
      i=$4
      v=$5
      "$PYTHON" "$D/gen_blocks.py" "$p" "$i" "$v" "$OUT/stageA-p$p.log" > "$OUT/deg1-p$p-$v.sing"
      sing "deg1-p$p-$v"
      grep -q '^RESULT occupied_blocks = 75$' "$OUT/deg1-p$p-$v.log"
      grep -q '^RESULT minimal_new_generators_total = 32$' "$OUT/deg1-p$p-$v.log"
      grep -q '^RESULT blocks_where_kernel_module_count_differs_from_rankE = 0$' "$OUT/deg1-p$p-$v.log"
      got=$(grep -E 'minimal_new [1-9]' "$OUT/deg1-p$p-$v.log" | sed 's/RESULT block1 //; s/ = N.*minimal_new /:/; s/ qK.*//' | tr '\n' ' ')
      [ "$got" = "$WANT" ]
      facts "$D/deg1-p$p-$v.log" > "$OUT/deg1-p$p-$v.want"
      facts "$OUT/deg1-p$p-$v.log" | cmp -s - "$OUT/deg1-p$p-$v.want"
      ;;
    *) echo "run_blocks: unknown unit $2" >&2; exit 2 ;;
  esac
  exit 0
fi
mkdir -p "$OUT"
me=$0
"$PYTHON" gororoba_quantum/run_commands.py "sh $me unit stageA 32009 10754" "sh $me unit stageA 32029 9115"
# the function-field units take 19 minutes each and start first
"$PYTHON" gororoba_quantum/run_commands.py \
  "sh $me unit deg1 32009 10754 generic" "sh $me unit deg1 32029 9115 generic" \
  "sh $me unit deg1 32009 10754 7013" "sh $me unit deg1 32029 9115 7013" \
  "sh $me unit deg1 32009 10754 21890" "sh $me unit deg1 32029 9115 21890" \
  "sh $me unit deg1 32009 10754 3567" "sh $me unit deg1 32029 9115 3567"
echo "run_blocks: ok"
