"""Compare the symbolic limit vectors of the N+ target (this directory) with those of the N- target at the same prime.

usage: twist_compare.py NM_DIR OUT.json
For the first-order family (limits E^2 F, polynomials in W, R, S, Z, E) the test is: N+ coordinate j equals eps_j times the
N- coordinate j with E -> 1/E, cleared by E^d.  For the order-5 family (parameters W, R, S, Z, E1) the test is: N+ coordinate j
equals eps_j times the N- coordinate j after a common sign change of the parameters.  All 21 coordinates of both families are
tested; the result lists, per family, how many coordinates satisfy the relation.
"""
import itertools
import json
import sys

sys.path.insert(0, '.')
import symfam as SF

P = SF.P
nm, outf = sys.argv[1], sys.argv[2]


def load(d, tag):
    return SF.load_fj(open('%s/fam/fam_%s.log' % (d, tag)).read())


def neg(poly):
    return {k: (-v) % P for k, v in poly.items()}


def inv_e(poly, d):
    out = {}
    for ex, c in poly.items():
        if ex[4] > d:
            return None
        out[ex[:4] + (d - ex[4],)] = c
    return out


def flip(poly, signs):
    out = {}
    for ex, c in poly.items():
        s = 1
        for e, sg in zip(ex, signs):
            if sg == -1 and e % 2:
                s = -s
        out[ex] = (c * s) % P
    return out


res = {}
for tag in ['p2_first_order_n2', 'near_e-1_j2_a2_b1_c1_d1_n5']:
    a, b = load('.', tag), load(nm, tag)   # a: N+ (this directory), b: N-
    coords = sorted(set(a) | set(b))
    rec = dict(coordinates=len(coords), only_one_side_nonzero=[j for j in coords if (j in a) != (j in b)])
    per = {}
    if tag.startswith('p2'):
        for j in coords:
            hit = None
            if j in a and j in b:
                for d in range(0, 8):
                    t = inv_e(b[j], d)
                    if t is None:
                        continue
                    if a[j] == t:
                        hit = (+1, d)
                        break
                    if a[j] == neg(t):
                        hit = (-1, d)
                        break
            per[j] = hit
        rec['relation'] = 'N+_j(E) = eps_j E^d_j N-_j(1/E)'
        rec['matching_coordinates'] = sorted(j for j, h in per.items() if h)
        rec['failing_coordinates'] = sorted(j for j, h in per.items() if not h)
        rec['eps_d'] = {str(j): h for j, h in per.items()}
    else:
        common = None
        for j in coords:
            ok = set()
            if j in a and j in b:
                for signs in itertools.product([1, -1], repeat=5):
                    t = flip(b[j], signs)
                    if a[j] == t or a[j] == neg(t):
                        ok.add(signs)
            per[j] = ok
            common = ok if common is None else common & ok
        rec['relation'] = 'N+_j = eps_j N-_j under a common sign change of (W, R, S, Z, E1)'
        rec['common_sign_changes'] = sorted(common)
        rec['matching_coordinates'] = sorted(j for j in coords if per[j])
        rec['failing_coordinates'] = sorted(j for j in coords if not per[j])
    res[tag] = rec
print(json.dumps(res, indent=1))
json.dump(res, open(outf, 'w'), indent=1)
