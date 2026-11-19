#!/bin/sh
# Truncated fiber-rank ladder: for each N, rank of the degree-d targets in k[t]/(J + m*P_d + m^N).
# The products and generators are cut below degree N (jet) before std, which leaves the ideal unchanged
# modulo m^N and keeps every polynomial inside the finite space of monomials of degree < N.
# The rank is a lower bound on h_d, nondecreasing in N, and equals h_d for N large (Krull intersection in the
# localization; the quotient I^d/mI^d is killed by m). A rank equal to the K2 count certifies h_d; a rank below
# it certifies nothing. A rank is recorded only after Singular exits 0 and writes its RESULT lines.
# Usage: ladder2.sh JOBDIR PRIME STEP_TIMEOUT_S N...
set -eu
PYTHON=${PYTHON:-python3}
RANK=$(cd "$(dirname "$0")/../probes" && pwd)/rank_nf.py
d=$1; p=$2; to=$3; shift 3
cd "$d"
log=ladder2.log
printf 'input sha256 %s\n' "$(sha256sum input.sing previous-relations.rel | awk '{print $1}' | tr '\n' ' ')" >> "$log"
for N in "$@"; do
  in="j$N.sing"; nf="jnf$N.txt"; out="jout$N.log"
  [ -e "$nf" ] && mv "$nf" "$nf.stale"
  sed -e "s/ideal sQ=std(Q);/Q=jet(Q,$((N-1))),maxideal($N); ideal sQ=std(Q);/" -e '/write(":w sq.txt",sQ);/d' \
      -e "s/ideal N=reduce(P,sQ); write(\":w nf\.txt\",N);/ideal N=reduce(jet(P,$((N-1))),sQ); write(\":w $nf\",N);/" input.sing > "$in"
  grep -q "maxideal($N)" "$in" && grep -q "jet(P,$((N-1)))" "$in" || { echo "N=$N sed did not apply" >> "$log"; exit 3; }
  rc=0
  /usr/bin/time -f "N=$N wall %e s maxrss %M KiB" -o "jtime$N.log" timeout -k 30 "$to" Singular -q --no-rc --cpus=1 "$in" > "$out" 2>&1 || rc=$?
  cat "jtime$N.log" >> "$log"; grep RESULT "$out" >> "$log" || :
  if [ "$rc" -ne 0 ] || ! grep -q "RESULT reduce_ms" "$out" || [ ! -s "$nf" ]; then
    echo "N=$N singular exit $rc; no rank recorded" >> "$log"; continue
  fi
  echo "N=$N $("$PYTHON" "$RANK" "$nf" "$p") nf_sha256 $(sha256sum "$nf" | cut -c1-16)" >> "$log"
done
