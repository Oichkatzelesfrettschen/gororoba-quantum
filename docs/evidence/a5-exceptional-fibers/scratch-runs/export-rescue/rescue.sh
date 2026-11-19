#!/bin/sh
# Copy each finished file of a Singular quotient export (q.sing, qB, qM1..qMn, qG) out of the engine's
# temporary directory while it exists; a file is copied once its size and mtime hold across 2 s, and again if
# they change later. On exit it writes SHA256SUMS of the copies.
set -eu
src=$1
dst=$2
mkdir -p "$dst"
log=$dst/rescue.log
while [ -d "$src" ]; do
  for f in "$src"/q*; do
    [ -f "$f" ] || continue
    b=${f##*/}
    s1=$(stat -c %s.%Y "$f" 2>/dev/null) || continue
    [ "$(cat "$dst/.$b.stamp" 2>/dev/null || true)" = "$s1" ] && continue
    sleep 2
    s2=$(stat -c %s.%Y "$f" 2>/dev/null) || continue
    [ "$s1" = "$s2" ] || continue
    cp "$f" "$dst/$b.part" || continue
    mv "$dst/$b.part" "$dst/$b"
    printf '%s\n' "$s2" > "$dst/.$b.stamp"
    printf '%s copied %s size.mtime %s\n' "$(date -u +%FT%TZ)" "$b" "$s2" >> "$log"
  done
  sleep 5
done
printf '%s source removed\n' "$(date -u +%FT%TZ)" >> "$log"
cd "$dst" && sha256sum q* > SHA256SUMS
