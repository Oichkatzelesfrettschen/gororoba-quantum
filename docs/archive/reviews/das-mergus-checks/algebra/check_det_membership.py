"""Independent check of the dimension-32 determinant/membership claims (G.P4, G.P5, G.P7),
the universal Stiefel inclusion (G10) and the A_6 control, with mutation controls.

Method: randomized exact polynomial identity testing. det L_y is computed from cd_core
signs with flint; the companion's C_z, transport and Pfaffian code is not used.
"""

import json
import sys

import flint
from common import (
    RNG, cabs2, cadd, cdiv, cdot, cmul, cneg, invariants, lmat, nullity, rgauss, rint, sign, y_from_z, z_from_y,
)

out = {}
rng = RNG(22315)  # ANU QRNG docs/evidence/anu_qrng/draw-2026-10-25T095947Z.json index 5


def rhs(y, perm=None):
    z = z_from_y(y)
    if perm is not None:
        z = [(flint.fmpq(y[k]), flint.fmpq(y[16 + perm[k]])) for k in range(1, 16)]
    inv = invariants(z)
    return inv["N"] ** 4 * (cabs2(inv["Q"]) * cabs2(inv["G"])) ** 2, inv


# 1. det L_y == N^4 |Q G|^4 at random doubly-pure integer points (large range)
ok = 0
trials = 30
for _ in range(trials):
    y = [flint.fmpq(0)] * 32
    for k in list(range(1, 16)) + list(range(17, 32)):
        y[k] = rint(rng, -10**6, 10**6)
    d = lmat(32, y).det()
    r, _ = rhs(y)
    ok += d == r
out["det_identity_random_doubly_pure"] = {"trials": trials, "agree": ok, "coord_range": "[-1e6,1e6]",
                                           "schwartz_zippel_per_point": "deg 32 / 2000001 < 1.6e-5"}

# 1b. small-range points to also hit low-rank events
ok = 0
for _ in range(200):
    y = [flint.fmpq(0)] * 32
    for k in list(range(1, 16)) + list(range(17, 32)):
        y[k] = rint(rng, -1, 1)
    d = lmat(32, y).det()
    r, _ = rhs(y)
    ok += d == r
out["det_identity_small_range"] = {"trials": 200, "agree": ok}

# 2. mutation controls (each should break agreement)
muts = {}
# 2a. flip one structure constant e_3 e_5 (and only that ordered pair)
bad = 0
for _ in range(10):
    y = [flint.fmpq(0)] * 32
    for k in list(range(1, 16)) + list(range(17, 32)):
        y[k] = rint(rng, -50, 50)
    bad += lmat(32, y, mutate={(3, 5)}).det() != rhs(y)[0]
muts["flip_sign_e3e5"] = {"trials": 10, "disagree": bad}
# 2b. permute the pairing y_16+k: swap partners of k=1 and k=2
perm = {k: k for k in range(1, 16)}
perm[1], perm[2] = 2, 1
bad = 0
for _ in range(10):
    y = [flint.fmpq(0)] * 32
    for k in list(range(1, 16)) + list(range(17, 32)):
        y[k] = rint(rng, -50, 50)
    bad += lmat(32, y).det() != rhs(y, perm)[0]
muts["swap_pairing_k1_k2"] = {"trials": 10, "disagree": bad}
# 2c. replace mu^2 by -mu^2 in Q
bad = 0
for _ in range(10):
    y = [flint.fmpq(0)] * 32
    for k in list(range(1, 16)) + list(range(17, 32)):
        y[k] = rint(rng, -50, 50)
    z = z_from_y(y)
    inv = invariants(z)
    mu2 = cmul(z[7], z[7])
    Qm = cadd(inv["Q"], cneg(cmul((flint.fmpq(2), flint.fmpq(0)), mu2)))
    Gm = cadd(cmul(Qm, Qm), cneg(cmul((flint.fmpq(4), flint.fmpq(0)), inv["Delta"])))
    bad += lmat(32, y).det() != inv["N"] ** 4 * (cabs2(Qm) * cabs2(Gm)) ** 2
muts["Q_with_minus_mu2"] = {"trials": 10, "disagree": bad}
out["det_identity_mutations"] = muts

# 3. purity reduction G.P7: L_{e16} anticommutes with L_d for every basis d != 0,16
J = lmat(32, [flint.fmpq(int(i == 16)) for i in range(32)])
anti = 0
for k in range(1, 32):
    if k == 16:
        continue
    Ld = lmat(32, [flint.fmpq(int(i == k)) for i in range(32)])
    anti += (J * Ld + Ld * J) == flint.fmpq_mat(32, 32)
out["e16_anticommutes_with_30_units"] = anti
# random points with y0 or y16 nonzero are invertible
inv_ok = 0
for _ in range(20):
    y = [rint(rng, -2, 2) for _ in range(32)]
    y[0] = rint(rng, 1, 3) if rng.random() < 0.5 else flint.fmpq(0)
    y[16] = rint(rng, 1, 3) if y[0] == 0 else y[16]
    inv_ok += lmat(32, y).det() != 0
out["nonpure_points_invertible"] = {"trials": 20, "invertible": inv_ok}
# ... including points that sit on Q=0 in their doubly pure part (strongest test)
inv_ok = 0
z0 = [(flint.fmpq(1), flint.fmpq(0)), (flint.fmpq(0), flint.fmpq(1))] + [(flint.fmpq(0), flint.fmpq(0))] * 13


def stiefel_point(rng, lo=-6, hi=6):
    while True:
        w = [rgauss(rng, lo, hi) for _ in range(15)]
        Qw = cdot(w, w)
        if Qw != (0, 0):
            break
    t = cdiv(cneg(cmul((flint.fmpq(2), flint.fmpq(0)), cdot(z0, w))), Qw)
    return [cadd(a, cmul(t, b)) for a, b in zip(z0, w)]


for _ in range(10):
    y = y_from_z(stiefel_point(rng))
    y[16] = flint.fmpq(1, 7)
    inv_ok += lmat(32, y).det() != 0
out["stiefel_plus_e16_invertible"] = {"trials": 10, "invertible": inv_ok}

# 4. universal Stiefel inclusion: random Gaussian-rational points on Q=0 (stereographic)
nul = []
for _ in range(40):
    z = stiefel_point(rng)
    inv = invariants(z)
    if inv["Q"] != (0, 0):
        sys.exit("stiefel point construction failed")
    y = y_from_z(z)
    # real Stiefel check: |p|=|q|, <p,q>=0
    p, q = y[1:16], y[17:32]
    if sum(a * a for a in p) != sum(b * b for b in q) or sum(a * b for a, b in zip(p, q)) != 0:
        sys.exit("not a real Stiefel point")
    nul.append(nullity(lmat(32, y)))
out["stiefel_random_nullities"] = {k: nul.count(k) for k in sorted(set(nul))}

# 4b. mutation: same Stiefel points with one sign flipped in the table
nm = []
for _ in range(10):
    y = y_from_z(stiefel_point(rng))
    nm.append(nullity(lmat(32, y, mutate={(3, 5)})))
out["stiefel_mutated_table_nullities"] = {k: nm.count(k) for k in sorted(set(nm))}

# 4c. A_6 analogue control: random Stiefel points in dimension 64 should be invertible generically
n64 = []
for _ in range(3):
    # p, q pure in A_5 with |p|=|q|, p.q=0, via complex stereographic in C^31
    z0b = [(flint.fmpq(1), flint.fmpq(0)), (flint.fmpq(0), flint.fmpq(1))] + [(flint.fmpq(0), flint.fmpq(0))] * 29
    w = [rgauss(rng) for _ in range(31)]
    t = cdiv(cneg(cmul((flint.fmpq(2), flint.fmpq(0)), cdot(z0b, w))), cdot(w, w))
    z = [cadd(a, cmul(t, b)) for a, b in zip(z0b, w)]
    y = [flint.fmpq(0)] * 64
    for k in range(1, 32):
        y[k], y[32 + k] = z[k - 1]
    n64.append(nullity(lmat(64, y)))
out["a6_random_stiefel_nullities"] = n64

# 5. G=0 points (exact family): u=(3,4,0..), n=(4,-3,12,0..)*(1/1) Gaussian scaling, v = alpha u + n
#    sqrt(Delta) = 65 for alpha arbitrary; choose alpha=2i -> mu^2 = 130-25-25*alpha^2-169 = 36
F = flint.fmpq
c0 = (F(0), F(0))
u = [(F(3), F(0)), (F(4), F(0))] + [c0] * 5
n = [(F(4), F(0)), (F(-3), F(0)), (F(12), F(0))] + [c0] * 4
alpha = (F(0), F(2))
v = [cadd(cmul(alpha, a), b) for a, b in zip(u, n)]
mu = (F(6), F(0))
z = u + [mu] + v
inv = invariants(z)
y = y_from_z(z)
out["G_zero_exact_point"] = {"Q": [str(inv["Q"][0]), str(inv["Q"][1])], "G": [str(inv["G"][0]), str(inv["G"][1])],
                             "nullity": nullity(lmat(32, y))}

print(json.dumps(out, indent=1, default=str))
