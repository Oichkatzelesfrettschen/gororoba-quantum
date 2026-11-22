#!/bin/sh
# Pfaffian identity of the Schur numerator W of the E8-bar Rees scripts; run from the repository root.
# Each script is the retained run script cut after its matrices (lines 3 to 145 over Q(i), 1 to 157 modulo 32009)
# followed by a tail of this directory.
set -u
D=docs/evidence/a5-exceptional-fibers/working/runs/e8-pfaffian-schur-identity
S=docs/evidence/a5-exceptional-fibers/working/runs/e8-rees-fibers-v2-p32009
for c in nm np; do
  {
    echo 'LIB "matrix.lib"; LIB "linalg.lib";'
    echo 'ring r=(0,i),(s1,s2,s3,s4,s5,s6,s7,s8,s9),dp; minpoly=i^2+1; option(redSB);'
    sed -n 3,145p "$S/e8-$c-p.v2-u-full.sing"
    cat "$D/tail-qi-$c.sing"
  } > "$D/pfaffian-schur-$c-qi.sing"
  {
    sed -n 1,157p "$S/e8-$c-p.v2-u-full.sing"
    cat "$D/tail-p32009-$c.sing"
  } > "$D/pfaffian-schur-$c-p32009.sing"
done
for f in pfaffian-schur-nm-qi pfaffian-schur-np-qi pfaffian-schur-nm-p32009 pfaffian-schur-np-p32009; do
  {
    Singular --version < /dev/null | head -n 1
    sha256sum "$D/$f.sing" "$S/e8-nm-p.v2-u-full.sing" "$S/e8-np-p.v2-u-full.sing"
  } > "$D/$f.log"
  /usr/bin/time -v -o "$D/$f.time" Singular -q "$D/$f.sing" < /dev/null >> "$D/$f.log" 2>&1
  echo "RC $?" >> "$D/$f.log"
  sed -i "s#$HOME#~#g" "$D/$f.time"
done
