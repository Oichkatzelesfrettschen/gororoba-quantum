"""Independent exact checks of the stratum constructions in chapter 3 (G.29/G.37, G14, G16,
G.I9, G.I10/G.I11, G.50-G.56) and the chapter-5 sedenion characteristic polynomials.
All nullities come from cd_core signs through flint exact ranks.
"""

import json
import sys

import flint
from common import (
    RNG, REPO, cadd, cdiv, cdot, cmul, cneg, invariants, lmat, mul, nullity, rgauss, rint, rmat, y_from_z, z_from_y,
)

F = flint.fmpq
C0 = (F(0), F(0))
rng = RNG(7190)  # ANU QRNG docs/evidence/anu_qrng/draw-2026-10-25T095947Z.json index 6
out = {}


def cs(x):
    return (F(x), F(0))


def isotropic(n, rng):
    z0 = [cs(1), (F(0), F(1))] + [C0] * (n - 2)
    while True:
        w = [rgauss(rng) for _ in range(n)]
        if cdot(w, w) != C0:
            break
    t = cdiv(cneg(cmul(cs(2), cdot(z0, w))), cdot(w, w))
    return [cadd(a, cmul(t, b)) for a, b in zip(z0, w)]


def scale(c, vec):
    return [cmul(c, a) for a in vec]


def oct_cross(a, b):
    """Imaginary octonion product restricted to Im: (a b)_k for k=1..7, a,b in C^7 (Gaussian)."""
    res = [C0] * 7
    for i in range(7):
        for j in range(7):
            if a[i] != C0 and b[j] != C0:
                k = (i + 1) ^ (j + 1)
                if k:
                    res[k - 1] = cadd(res[k - 1], cmul(cs(sign_oct(i + 1, j + 1)), cmul(a[i], b[j])))
    return res


def sign_oct(p, q):
    from common import sign
    return sign(8, p, q)


# --- V regular (12), S+- (16) ---
nV = []
for _ in range(15):
    w = [rgauss(rng) for _ in range(7)]
    qw = cdot(w, w)
    tau = rgauss(rng)
    tau2 = cmul(tau, tau)
    den = cadd(qw, tau2)
    if den == C0 or qw == C0:
        continue
    lam = cmul((F(0), F(1)), cdiv(cadd(qw, cneg(tau2)), den))
    mu = cdiv(cmul((F(0), F(2)), cmul(qw, tau)), den)
    z = w + [mu] + scale(lam, w)
    if invariants(z)["Q"] != C0:
        sys.exit("V chart failed")
    nV.append(nullity(lmat(32, y_from_z(z))))
out["V_rational_chart_nullities"] = {k: nV.count(k) for k in set(nV)}
nS = []
for sgn in (1, -1):
    for _ in range(5):
        w = isotropic(7, rng)
        z = w + [C0] + scale((F(0), F(sgn)), w)
        nS.append(nullity(lmat(32, y_from_z(z))))
out["S_pm_nullities"] = {k: nS.count(k) for k in set(nS)}
# control: isotropic w but v = 2i w (not +-i) -> regular point of V, expect 12
nSc = []
for _ in range(3):
    w = isotropic(7, rng)
    z = w + [C0] + scale((F(0), F(2)), w)
    nSc.append(nullity(lmat(32, y_from_z(z))))
out["V_isotropic_w_lambda_2i_control"] = nSc

# --- Z component (G14): mu=0, a=u+iv, b=u-iv isotropic -> nullity >= 8 ---
nZ = []
for _ in range(15):
    a, b = isotropic(7, rng), isotropic(7, rng)
    u = [cmul(cs(F(1, 2)), cadd(x, y)) for x, y in zip(a, b)]
    v = [cdiv(cadd(x, cneg(y)), (F(0), F(2))) for x, y in zip(a, b)]
    z = u + [C0] + v
    inv = invariants(z)
    if not (inv["U"] == inv["V0"] and inv["W"] == C0):
        sys.exit("Z construction failed")
    nZ.append(nullity(lmat(32, y_from_z(z))))
out["Z_random_nullities"] = {k: nZ.count(k) for k in set(nZ)}


# --- nullity-8 incidence chart (G16) ---
def rational_unit_s6(rng):
    t = [F(rng.randint(-9, 9), rng.randint(1, 5)) for _ in range(6)]
    s = sum(x * x for x in t)
    return [(1 - s) / (1 + s)] + [2 * x / (1 + s) for x in t]


n8, n8mix, checks = [], [], []
for _ in range(15):
    w = rational_unit_s6(rng)
    r = [F(rng.randint(-5, 5)) for _ in range(7)]
    dot = sum(x * y for x, y in zip(r, w))
    a = [x - dot * y for x, y in zip(r, w)]
    wc = [cs(x) for x in w]
    ac = [cs(x) for x in a]
    wxa = oct_cross(wc, ac)
    nvec = [cadd(x, cmul((F(0), F(1)), y)) for x, y in zip(ac, wxa)]
    u = [cmul((F(0), F(1)), x) for x in wc]  # U = -1
    m = F(rng.randint(2, 9), rng.randint(1, 4))
    lam = cs((m * m - 1) / (2 * m))
    mu = cs((m * m + 1) / (2 * m))
    c = rgauss(rng)
    if c == C0:
        c = cs(1)
    v = [cadd(cmul(lam, x), y) for x, y in zip(u, nvec)]
    z = scale(c, u + [mu] + v)
    inv = invariants(z)
    uxn = oct_cross(u, nvec)
    checks.append(inv["Q"] == C0 and uxn == nvec)
    n8.append(nullity(lmat(32, y_from_z(z))))
    # control: mix eigenspaces, n' = n + (b - i w x b)
    r2 = [F(rng.randint(-5, 5)) for _ in range(7)]
    d2 = sum(x * y for x, y in zip(r2, w))
    b = [cs(x - d2 * y) for x, y in zip(r2, w)]
    wxb = oct_cross(wc, b)
    nmix = [cadd(cadd(x, y), cneg(cmul((F(0), F(1)), q))) for x, y, q in zip(nvec, b, wxb)]
    # keep Q=0: n'.n' may be nonzero; solve mu' over Q(i) only if square -> skip, use mu from equation if possible
    vm = [cadd(cmul(lam, x), y) for x, y in zip(u, nmix)]
    zm = u + [mu] + vm
    n8mix.append((invariants(zm)["Q"] == C0, nullity(lmat(32, y_from_z(zm)))))
out["incidence_chart_points_valid"] = sum(checks)
out["incidence_chart_nullities"] = {k: n8.count(k) for k in set(n8)}
out["eigenspace_mixed_control_(Q==0,nullity)"] = n8mix

# --- G.I9 ---
def basisvec(idx, coeffs=None):
    y = [F(0)] * 32
    for i, cf in zip(idx, coeffs or [1] * len(idx)):
        y[i] = F(cf)
    return y


y8 = basisvec([1, 10, 25, 27])
y4 = basisvec([1, 10, 25, 28])
out["G.I9"] = {}
for name, y in (("y8", y8), ("y4", y4)):
    inv = invariants(z_from_y(y))
    out["G.I9"][name] = {"Q": str(inv["Q"]), "G": str(inv["G"]), "Delta": str(inv["Delta"]),
                         "nullity": nullity(lmat(32, y))}

# --- characteristic polynomials (G.I11), (G.50a): exact at 40 rational parameters ---
R = flint.fmpq_poly([0, 1])


def chk_charpoly(build, formula, values):
    ok = 0
    for t in values:
        cp = lmat(32, build(t)).charpoly()
        ok += cp == formula(F(t))
    return ok


vals = [F(k, 3) for k in range(-20, 20)]


def build_I10(t):
    y = basisvec([1, 25])
    y[10] += t
    y[27] += t
    return y


def form_I11(t):
    r2 = R * R
    return (R ** 8 * (r2 + 4 * t * t) ** 2 * (r2 + 2 * t * t + 2) ** 4 * (r2 + 4 * t * t + 4) ** 2
            * (r2 * r2 + 4 * r2 * t * t + 8 * r2 + 16) ** 2)


def build_50(e):
    y = basisvec([1, 10, 18, 25], [1, -1, 1, 1])
    y[9] += e
    y[26] += e
    return y


def form_50a(e):
    r2 = R * R
    return (R ** 12 * (r2 + 4 * e * e) ** 2 * (r2 + 2 * e * e + 4) ** 4 * (r2 + 4 * e * e + 8) ** 2
            * (r2 + 4 * e * e + 16) ** 2)


out["charpoly_G.I11_agree_of_40"] = chk_charpoly(build_I10, form_I11, vals)
out["charpoly_G.50a_agree_of_40"] = chk_charpoly(build_50, form_50a, vals)
# mutation: drop the factor-2 in (r^2+2t^2+2) -> must fail
out["charpoly_G.I11_mutated_agree_of_40"] = chk_charpoly(
    build_I10, lambda t: form_I11(t) * (R * R + 2 * t * t + 3) ** 4 / (R * R + 2 * t * t + 2) ** 4, vals[:5])
out["path_I10_nullity_t0_t1"] = [nullity(lmat(32, build_I10(F(0)))), nullity(lmat(32, build_I10(F(1))))]
out["path_50_nullity_e0_e1"] = [nullity(lmat(32, build_50(F(0)))), nullity(lmat(32, build_50(F(1))))]

# --- sector identities G.51-G.54 ---
b = [F(0)] * 32
c = [F(0)] * 32
for i, s in ((7, 1), (12, -1), (20, -1), (31, -1)):
    b[i] = F(s, 2)
for i, s in ((5, 1), (14, -1), (22, -1), (29, -1)):
    c[i] = F(s, 2)
x = build_50(F(0))
d = basisvec([9, 26])
Lx, Ld = lmat(32, x), lmat(32, d)
colb, colc = flint.fmpq_mat(32, 1, b), flint.fmpq_mat(32, 1, c)
d0 = basisvec([7, 20])
out["G.52"] = {
    "Lx b = 0": Lx * colb == flint.fmpq_mat(32, 1), "Lx c = 0": Lx * colc == flint.fmpq_mat(32, 1),
    "Ld b = 2c": Ld * colb == 2 * colc, "Ld c = -2b": Ld * colc == -2 * colb,
    "Lx d0 = Ld d0 = 0": (Lx * flint.fmpq_mat(32, 1, d0) == flint.fmpq_mat(32, 1)) and (Ld * flint.fmpq_mat(32, 1, d0) == flint.fmpq_mat(32, 1)),
    "R b = c (index ^ 2)": [b[i ^ 2] for i in range(32)] == c,
}

# --- chapter 5 spectral identities on real sedenions (Schwartz-Zippel, 20 points) ---
ok_L = ok_C = 0
for _ in range(20):
    zr = [F(0)] + [rint(rng, -1000, 1000) for _ in range(15)]
    zz = [(zr[k], F(0)) for k in range(1, 16)]
    inv = invariants(zz)
    Q, De = inv["Q"][0], inv["Delta"][0]
    r2Q = R * R + Q
    L = lmat(16, zr)
    ok_L += L.charpoly() == r2Q ** 4 * (r2Q * r2Q - 4 * De) ** 2
    Rm = rmat(16, zr)
    Cfull = (L - Rm) * F(1, 2)
    Cz = flint.fmpq_mat(15, 15, [Cfull[i, j] for i in range(1, 16) for j in range(1, 16)])
    ok_C += Cz.charpoly() == R * r2Q ** 3 * (r2Q * r2Q - 4 * De) ** 2
out["ch5_charpoly_L_agree_of_20"] = ok_L
out["ch5_charpoly_C_agree_of_20"] = ok_C

print(json.dumps(out, indent=1, default=str))
