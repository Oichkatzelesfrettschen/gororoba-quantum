#!/bin/sh
# Usage: run_kcompare.sh SINGULAR LIMIT_SECONDS CELL...  Runs kcmp-CELL.sing (written by kcompare.py prepare), one
# Singular process per cell in turn. A log is never overwritten; each log opens with the tool version and the script
# digest, a timing file follows, and the last line is EXIT rc. kcompare.done carries one RESULT line per cell and the
# line KCOMPARE ALL DONE when every cell ran.
set -eu
cd "$(dirname "$0")"
bin=$1; limit=$2; shift 2
[ -e kcompare.done ] && { echo "refuse: kcompare.done exists" >&2; exit 2; }
for n in "$@"; do
  [ -e "kcmp-$n.log" ] && { echo "refuse: kcmp-$n.log exists" >&2; exit 2; }
  { "$bin" --version </dev/null | head -n 1; sha256sum "kcmp-$n.sing"; } > "kcmp-$n.log" 2>&1
  rc=0
  /usr/bin/time -v -o "kcmp-$n.time" timeout -k 30 "$limit" "$bin" -q --no-rc "kcmp-$n.sing" </dev/null >> "kcmp-$n.log" 2>&1 || rc=$?
  echo "EXIT $rc" >> "kcmp-$n.log"
  { echo "CELL $n EXIT $rc"; grep -E '^(KCMP RESULT|SPAN RESULT|KCMP DONE)' "kcmp-$n.log" || true; } >> kcompare.done.part
done
echo "KCOMPARE ALL DONE" >> kcompare.done.part
mv kcompare.done.part kcompare.done
