#!/bin/sh
# Usage: run_kcompare_v2.sh SINGULAR LIMIT_SECONDS CELL...  Runs kcmp-CELL.sing (written by kcompare.py prepare or
# kcompare_v2.py prepare), one Singular process per cell in turn. A log is never overwritten; each log opens with the tool
# version and the script digest, a timing file follows, and the last line is EXIT rc. A cell passes when Singular exits
# 0 and its log holds, as whole lines, the verdict "KCMP RESULT cell CELL equal 1 control_drop_unequal 1
# control_added_unequal 1" (both known-bad controls read unequal) and the terminal line "KCMP DONE cell CELL"; Singular
# exits 0 on SIGTERM, so a killed run is told apart by the missing terminal line. kcompare.done carries one block per
# cell (the CELL line and the KCMP, SPAN lines) and the line KCOMPARE ALL DONE when every cell passed and the exit
# status is 0. The first cell that fails ends the run with kcompare.failed (its CELL line, the lines it printed and one
# FAIL line) and exit status 1; kcompare.failed and kcompare.done never both exist.
set -eu
cd "$(dirname "$0")"
bin=$1; limit=$2; shift 2
[ -e kcompare.done ] && { echo "refuse: kcompare.done exists" >&2; exit 2; }
[ -e kcompare.failed ] && { echo "refuse: kcompare.failed exists" >&2; exit 2; }
for n in "$@"; do
  [ -e "kcmp-$n.log" ] && { echo "refuse: kcmp-$n.log exists" >&2; exit 2; }
done
for n in "$@"; do
  { "$bin" --version </dev/null | head -n 1; sha256sum "kcmp-$n.sing"; } > "kcmp-$n.log" 2>&1
  rc=0
  /usr/bin/time -v -o "kcmp-$n.time" timeout -k 30 "$limit" "$bin" -q --no-rc "kcmp-$n.sing" </dev/null >> "kcmp-$n.log" 2>&1 || rc=$?
  echo "EXIT $rc" >> "kcmp-$n.log"
  block=$(echo "CELL $n EXIT $rc"; grep -E '^(KCMP RESULT|SPAN RESULT|KCMP DONE)' "kcmp-$n.log" || true)
  why=
  if [ "$rc" -ne 0 ]; then
    why="Singular exited $rc"
  elif ! grep -Fxq "KCMP RESULT cell $n equal 1 control_drop_unequal 1 control_added_unequal 1" "kcmp-$n.log"; then
    why="the verdict line with equal and both controls unequal is missing"
  elif ! grep -Fxq "KCMP DONE cell $n" "kcmp-$n.log"; then
    why="the terminal line KCMP DONE is missing"
  fi
  if [ -n "$why" ]; then
    { echo "$block"; echo "FAIL cell $n: $why"; } >> kcompare.done.part
    mv kcompare.done.part kcompare.failed
    echo "FAIL cell $n: $why" >&2
    exit 1
  fi
  echo "$block" >> kcompare.done.part
done
echo "KCOMPARE ALL DONE" >> kcompare.done.part
mv kcompare.done.part kcompare.done
