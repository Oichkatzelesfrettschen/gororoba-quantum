#!/bin/sh
# The quadric ideal of E8-bar -> VB along the boost at sample values of w and, with the argument generic, over
# F_32029(w); run from the repository root with Singular on PATH and sympy and python-flint in $PYTHON.
# Exits nonzero unless every point shows the retained invariants and one normal form, the bases before the frame
# differ between points, and (generic) the normal form over the function field is that same one.
set -eu
PYTHON=${PYTHON:-python3}
export PYTHON PYTHONDONTWRITEBYTECODE=1
D=docs/evidence/a5-exceptional-fibers/working/runs/e8-vb-boost-family-p32029
POINTS="1 2 3 2/3 5 7 11 -3 1/4 1000 12345 9115"
one() { # tag: the gates on one log
  grep -q '^RESULT done 1$' "$D/bf-$1.log"
  if grep -q '^ *?' "$D/bf-$1.log"; then
    echo "run_boost: Singular error line in bf-$1.log" >&2
    exit 1
  fi
  grep -q '^RESULT k_generators 21 dim 4 mult 7$' "$D/bf-$1.log"
  grep -q '^RESULT k_numerator 1,0,-21,70,-105,84,-35,6,0$' "$D/bf-$1.log"
  [ "$(grep '^RESULT prime' "$D/bf-$1.log" | sort | tr '\n' ';')" = 'RESULT prime 4 3 4;RESULT prime 4 4 3;RESULT prime_count 2;' ]
  for line in 'adjugate_identity 1' 'pivot_pfaffian_at_origin_nonzero 1' 'selected_count 10' 'germ_component_count 1' \
    'germ_dimension 4' 'candidate_count 21' 'normal_form_size 21'; do
    grep -q "^RESULT $line\$" "$D/bf-$1.log"
  done
  grep -q '^RESULT radical 1$' "$D/bf-$1.log"
  grep -q '^RESULT frame_consistent 1$' "$D/bf-$1.log"
  grep -q '^RESULT frame_determinant_nonzero 1$' "$D/bf-$1.log"
}
tag() { echo "w$1" | tr '/-' 'dm'; }
: > "$D/normal-forms.txt"
# shellcheck disable=SC2086
"$PYTHON" "$D/boost_family.py" --run "$D" $POINTS > /dev/null
for v in $POINTS; do
  t=$(tag "$v")
  one "$t"
  echo "$t $(grep '^NORMALFORM' "$D/bf-$t.log" | sha256sum | cut -c1-64) $(grep '^KBASIS' "$D/bf-$t.log" | sha256sum | cut -c1-64)" >> "$D/normal-forms.txt"
done
grep -q '^RESULT schur_matches_retained 1$' "$D/bf-w1.log"
[ "$(cut -d' ' -f2 "$D/normal-forms.txt" | sort -u | wc -l)" = 1 ]
[ "$(cut -d' ' -f3 "$D/normal-forms.txt" | sort -u | wc -l)" -gt 1 ]
if [ "${1:-}" = generic ]; then
  "$PYTHON" "$D/boost_family.py" --run "$D" generic > /dev/null
  one generic
  [ "$(grep '^NORMALFORM' "$D/bf-generic.log" | sha256sum | cut -c1-64)" = "$(head -n 1 "$D/normal-forms.txt" | cut -d' ' -f2)" ]
  grep '^KBASIS' "$D/bf-generic.log" | grep -q w
  echo "run_boost generic: PASS"
fi
echo "run_boost: PASS"
