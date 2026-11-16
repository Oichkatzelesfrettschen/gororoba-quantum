#!/bin/sh
set -u
BASE=$HOME/work/e8np-d2
REPO=$HOME/src/gororoba-quantum
PYTHON=$HOME/.cache/gororoba-quantum/ci-py3.14.7/bin/python3
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 PYTHONDONTWRITEBYTECODE=1
while [ ! -f "$BASE/EXIT" ]; do sleep 30; done
cd "$REPO" || exit 2
{ echo "HEAD $(git rev-parse HEAD) dirty=$(git status --short | wc -l)"; echo "driver $(cat "$BASE/EXIT")"; } > "$BASE/post.log"
if [ "$(cat "$BASE/EXIT")" = "EXIT 0" ]; then
  "$PYTHON" -B "$BASE/post_check.py" "$BASE/e8-np/d2/relations-upto-d2.rel" "$BASE/e8-np/d2/receipt-d2.json" >> "$BASE/post.log" 2>&1
  echo "POST_EXIT $?" >> "$BASE/post.log"
else
  echo "POST_EXIT skipped" >> "$BASE/post.log"
fi
echo done > "$BASE/post.done"
