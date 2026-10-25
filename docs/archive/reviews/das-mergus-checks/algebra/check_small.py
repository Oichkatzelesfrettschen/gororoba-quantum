"""Independent exact checks of chapter-2, chapter-5 and chapter-6 statements, from cd_core signs."""

import itertools
import json
from fractions import Fraction

import numpy as np
import sys
from pathlib import Path

from assoc_items import Lm, TWO, ascent, octonion_assoc, row_max
from common import RNG, sign

sys.path.insert(0, str(Path(__file__).resolve().parents[5] / "gororoba_quantum"))
from parallel import ordered_map  # noqa: E402


def main() -> None:
    out = {}
    Fr = Fraction


    def vec(D, terms):
        v = [Fr(0)] * D
        for i, c in terms:
            v[i] += Fr(c)
        return v


    def mul(D, a, b):
        o = [Fr(0)] * D
        for i, x in enumerate(a):
            if x:
                for j, y in enumerate(b):
                    if y:
                        o[i ^ j] += sign(D, i, j) * x * y
        return o


    def sub(a, b):
        return [x - y for x, y in zip(a, b)]


    def n2(a):
        return sum(x * x for x in a)


    # ---- sedenion associator witness (Theorem 5.3) ----
    a = vec(16, [(1, 1), (10, 1)])
    b = vec(16, [(4, 1), (15, 1)])
    c = vec(16, [(2, 1), (9, -1)])
    ab, bc = mul(16, a, b), mul(16, b, c)
    assoc = sub(mul(16, ab, c), mul(16, a, bc))
    ratio2 = n2(assoc) / (n2(a) * n2(b) * n2(c))
    out["assoc_witness"] = {"ab": {i: str(x) for i, x in enumerate(ab) if x}, "bc": {i: str(x) for i, x in enumerate(bc) if x},
                            "assoc": {i: str(x) for i, x in enumerate(assoc) if x}, "ratio_squared": str(ratio2)}
    c2 = vec(16, [(2, 1), (9, 1)])
    assoc2 = sub(mul(16, ab, c2), mul(16, a, mul(16, b, c2)))
    out["assoc_witness_mutation_c=e2+e9_ratio_squared"] = str(n2(assoc2) / (n2(a) * n2(b) * n2(c2)))
    # exhaustive over two-term unit-coefficient elements of form e_i +- e_j for an independent maximum
    # Two-term units: 240 rows of the exhaustive associator norm, pooled.
    best = max(ordered_map(row_max, list(range(len(TWO)))))
    out["assoc_max_over_two_term_units_spectral"] = best
    # Random ascent, never above 4: restart k takes child k of the QRNG seed's
    # SeedSequence, and child 200 draws the octonion control's inputs first.
    children = np.random.SeedSequence(55842).spawn(201)  # ANU QRNG docs/evidence/anu_qrng/draw-2026-10-25T095947Z.json index 3
    out["assoc_random_ascent_max"] = max(ordered_map(ascent, children[:200]))
    out["kappa4_at_e1+e10_squared"] = float(np.linalg.norm(Lm(np.array([0, 1] + [0] * 8 + [1] + [0] * 5) / np.sqrt(2)), 2) ** 2)
    # Octonion control: max over units in octonions <= 2.
    triples = list(np.random.default_rng(children[200]).normal(size=(2000, 3, 8)))
    out["octonion_assoc_random_max"] = max(ordered_map(octonion_assoc, triples))

    # ---- fold-average (chapter 6) ----
    D = 8


    def inc(x):
        return x + x


    def p(xx):
        return [(xx[k] + xx[8 + k]) / 2 for k in range(8)]


    def m2(x, y):
        return p(mul(16, inc(x), inc(y)))


    def r(xx):
        px = inc(p(xx))
        return [s - t for s, t in zip(xx, px)]


    e = [vec(8, [(k, 1)]) for k in range(8)]
    out["m2_equals_opposite_product_all_64"] = all(m2(e[i], e[j]) == mul(8, e[j], e[i]) for i in range(8) for j in range(8))
    t = sub(m2(m2(e[1], e[2]), e[4]), m2(e[1], m2(e[2], e[4])))
    out["m2_assoc_1_2_4"] = {i: str(x) for i, x in enumerate(t) if x}


    def T3(x, y, zv):
        return sub(p(mul(16, r(mul(16, inc(x), inc(y))), inc(zv))), p(mul(16, inc(x), r(mul(16, inc(y), inc(zv))))))


    sc = im = bad = 0
    for i, j, k in itertools.permutations(range(1, 8), 3):
        tv = T3(e[i], e[j], e[k])
        nz = [(q, x) for q, x in enumerate(tv) if x]
        if len(nz) != 1 or abs(nz[0][1]) != 2:
            bad += 1
        elif nz[0][0] == 0:
            sc += 1
        else:
            im += 1
    out["T3_210_triples"] = {"scalar": sc, "imaginary": im, "not_single_coeff_2": bad}
    ok = okmut = 0
    for i, j, k in itertools.product(range(8), repeat=3):
        x, y, zv = e[i], e[j], e[k]
        lhs = sub(m2(m2(x, y), zv), m2(x, m2(y, zv)))
        big = sub(mul(16, mul(16, inc(x), inc(y)), inc(zv)), mul(16, inc(x), mul(16, inc(y), inc(zv))))
        rhs = sub(p(big), T3(x, y, zv))
        ok += lhs == rhs
        okmut += lhs == [-q for q in T3(x, y, zv)]
    out["assoc_decomposition_512"] = {"holds": ok, "mutation_drop_p_assoc_holds": okmut}
    out["coefficient_extension_zd"] = mul(16, vec(16, [(3, 1), (10, 1)]), vec(16, [(6, 1), (15, -1)])) == [0] * 16


    # ---- chapter 2: ANF degree machinery ----
    def anf(tt, n):
        a = list(tt)
        for i in range(n):
            for x in range(1 << n):
                if x >> i & 1:
                    a[x] ^= a[x ^ (1 << i)]
        return a


    def deg(tt, n):
        a = anf(tt, n)
        return max((bin(x).count("1") for x in range(1 << n) if a[x]), default=-1)


    def phi(Dd, p_, q_):
        return 0 if sign(Dd, p_, q_) == 1 else 1


    res42 = True
    res45 = True
    res416 = True
    lead = True
    for n in range(2, 7):
        Dd = 1 << n
        for m in range(1, Dd):
            f = [phi(Dd, m, x) for x in range(Dd)]
            res42 &= deg(f, n) == n - 1
            if n >= 3:
                a_ = anf(f, n)
                for j in range(n):
                    mono = (Dd - 1) ^ (1 << j)
                    lead &= a_[mono] == (m >> j & 1)
            h = [phi(Dd, x, m) for x in range(Dd)]
            bl = m.bit_length()
            exp = 1 if (m & (m - 1)) == 0 else max(1, bl - 2)
            res45 &= deg(h, n) == exp
            s = [(-1) ** hh for hh in h]
            for zz in range(Dd):
                if bin(zz & m).count("1") % 2 == 0:
                    res416 &= sum(s[x] * (-1) ** bin(zz & x).count("1") for x in range(Dd)) == 0
    out["thm4.2_degree_n2..6"] = res42
    out["thm4.2_leading_layer_n3..6"] = lead
    out["prop4.5_right_degree_n2..6"] = res45
    out["eq4.16_fourier_zero_n2..6"] = res416


    def g(Dd, i, j, x):
        return (phi(Dd, j, x) + phi(Dd, i, j ^ x) + phi(Dd, i ^ j, x) + phi(Dd, i, j)) % 2


    cens = {}
    ok43 = True
    for n in (3, 4, 5, 6):
        Dd = 1 << n
        for i in range(1, Dd):
            for j in range(i + 1, Dd):
                d = deg([g(Dd, i, j, x) for x in range(Dd)], n)
                ok43 &= d == max(1, max(i, j).bit_length() - 2)
                if n == 6:
                    cens[d] = cens.get(d, 0) + 1
    out["thm4.3_assoc_degree_n3..6"] = ok43
    out["census_n6"] = cens
    out["census_formula"] = {"N_d(d=2..4)": [3 * 2**d * (2 ** (d + 1) - 1) for d in (2, 3, 4)],
                             "top_n8": 3 * 256 * 254 // 8, "fraction_D256": str(Fr(3 * 256, 4 * 255))}
    # Prop 5 and Walsh
    ok5 = okc = okw = True
    for n in range(3, 9):
        Dd, k = 1 << n, n - 2
        for m in range(1 << k):
            i = (1 << (n - 1)) + m
            j = i + (1 << (n - 2))
            gv = [g(Dd, i, j, x) for x in range(Dd)]
            for x in range(Dd):
                zlow, tbit = x & ((1 << k) - 1), x >> (n - 1)
                exp = (tbit + (zlow == m)) % 2 if m else int(zlow != 0)
                ok5 &= gv[x] == exp
            a_ = anf(gv, n)
            cnt = sum(a_)
            w_ = bin(m).count("1")
            okc &= cnt == ((1 + 2 ** (k - w_)) if m else 2**k - 1)
            # Walsh: amplitude at (s, b', t')
            amp = {}
            for sidx in range(Dd):
                amp[sidx] = Fr(sum((-1) ** (gv[x] + bin(x & sidx).count("1")) for x in range(Dd)), Dd)
            for sidx, val in amp.items():
                s_low, bp, tp = sidx & ((1 << k) - 1), sidx >> k & 1, sidx >> (n - 1)
                if m:
                    expv = (Fr(int(s_low == 0)) - Fr(2, 2**k) * (-1) ** bin(s_low & m).count("1")) if (bp == 0 and tp == 1) else 0
                else:
                    expv = (-Fr(int(s_low == 0)) + Fr(2, 2**k)) if (bp == 0 and tp == 0) else 0
                okw &= val == expv
    out["prop5_formula_n3..8"] = ok5
    out["eq5.2_monomial_counts"] = okc
    out["prop6.1_walsh_n3..8"] = okw
    k = 6
    out["n8_overlap_tracedist2_central"] = [str(1 - Fr(2, 2**k)), str(1 - (1 - Fr(2, 2**k)) ** 2), str((1 - Fr(2, 2**k)) ** 2)]


    # group order |G_n| by BFS for n=3,4
    def gorder(n):
        Dd = 1 << n
        gens = [tuple((sign(Dd, m, x), m ^ x) for x in range(Dd)) for m in range(Dd)]

        def compose(A, B):  # A after B
            return tuple((B[x][0] * A[B[x][1]][0], A[B[x][1]][1]) for x in range(Dd))
        seen = {gens[0]}
        frontier = [gens[0]]
        while frontier:
            nf = []
            for X in frontier:
                for Gm in gens:
                    Y_ = compose(Gm, X)
                    if Y_ not in seen:
                        seen.add(Y_)
                        nf.append(Y_)
            frontier = nf
        return len(seen)


    out["group_order_n2_n3_n4"] = [gorder(2), gorder(3), gorder(4)]
    out["group_order_formula_n3_n4"] = [2 ** (3 + 4), 2 ** (4 + 8)]

    # conference
    okc = True
    for n in range(1, 7):
        Dd = 1 << n
        Wm = np.zeros((Dd, Dd))
        for rr in range(Dd):
            for s_ in range(1, Dd):
                Wm[rr ^ s_, rr] += sign(Dd, rr, s_)
        okc &= np.array_equal(Wm.T, -Wm) and np.array_equal(Wm @ Wm, -(Dd - 1) * np.eye(Dd))
    out["conference_D2..64"] = okc
    # anticommuting pairs in dim 16
    L = [np.array([[sign(16, m, q) if (m ^ q) == rr else 0 for q in range(16)] for rr in range(16)]) for m in range(16)]
    anti = sum(1 for i in range(1, 16) for j in range(i + 1, 16) if not (L[i] @ L[j] + L[j] @ L[i]).any())
    out["dim16_anticommuting_pairs"] = [anti, 105 - anti]
    # Gram spectrum, Delta, pure embedding
    La = L[1] + L[10]
    ev = np.round(np.linalg.eigvalsh(La.T @ La), 9)
    out["gram_e1+e10"] = sorted(set(ev.tolist()))
    Gn = La.T @ La / 2
    out["Delta_e1+e10"] = float(np.trace(Gn @ Gn) / 16 - 1)
    rg = RNG(20108)  # ANU QRNG docs/evidence/anu_qrng/draw-2026-10-25T095947Z.json index 4
    emb_ok = True
    for _ in range(5):
        av = [rg.randint(-3, 3) for _ in range(16)]
        A16 = sum(av[m] * L[m] for m in range(16))
        a32 = av + [0] * 16
        L32 = np.zeros((32, 32))
        for pp in range(32):
            if a32[pp]:
                for q in range(32):
                    L32[pp ^ q, q] += a32[pp] * sign(32, pp, q)
        e16 = np.sort(np.linalg.eigvalsh(A16.T @ A16))
        e32 = np.sort(np.linalg.eigvalsh(L32.T @ L32))
        emb_ok &= np.allclose(np.sort(np.concatenate([e16, e16])), e32)
    out["pure_embedding_spectrum_doubles"] = emb_ok
    # convention discriminator
    Dd = 16
    Ls_ = sum(L[m] for m in range(1, 16))
    Rs = np.zeros((16, 16))
    for rr in range(16):
        for s_ in range(1, 16):
            Rs[rr ^ s_, rr] += sign(16, rr, s_)
    psi = np.zeros(16)
    psi[0] = psi[1] = 1 / np.sqrt(2)
    out["discriminator_out3_right_left"] = [float(((np.eye(16) + Rs) / 4 @ psi)[3] ** 2), float(((np.eye(16) + Ls_) / 4 @ psi)[3] ** 2)]
    # E0 Pauli decomposition, little-endian (qubit b = bit b)
    X = np.array([[0, 1], [1, 0]])
    Yp = np.array([[0, -1j], [1j, 0]])
    Z = np.diag([1, -1])
    I2 = np.eye(2)


    def word(ops):  # ops[q] for q=0..3, little-endian: kron(q3,q2,q1,q0)
        return np.kron(np.kron(np.kron(ops[3], ops[2]), ops[1]), ops[0])


    E0 = La.T @ La / 4
    Tm = word([Yp, X, I2, Yp])
    pred = np.eye(16) / 2 - (np.eye(16) - word([I2, I2, Z, I2])) @ Tm / 4
    out["E0_pauli_identity"] = bool(np.allclose(E0, pred))
    Pk = (np.eye(16) - word([I2, I2, Z, I2])) @ (np.eye(16) + Tm) / 4
    w_, V_ = np.linalg.eigh(La.T @ La)
    Pker = V_[:, np.abs(w_) < 1e-9] @ V_[:, np.abs(w_) < 1e-9].T
    out["kernel_projector_identity"] = bool(np.allclose(Pk, Pker))

    # D14 projection counts
    roots = []
    for i in range(14):
        for j in range(i + 1, 14):
            for si in (1, -1):
                for sj in (1, -1):
                    rv = [0] * 14
                    rv[i], rv[j] = si, sj
                    roots.append(rv)
    proj = [tuple(rv[:3]) for rv in roots]
    from collections import Counter
    cnt = Counter(proj)
    same = sum(c_ * (c_ - 1) // 2 for c_ in cnt.values())
    mom = np.array(roots).T @ np.array(roots)
    out["D14"] = {"roots": len(roots), "distinct_proj": len(cnt), "origin": cnt[(0, 0, 0)],
                  "axial": sorted({c_ for k_, c_ in cnt.items() if sum(map(abs, k_)) == 1}),
                  "outer": sorted({c_ for k_, c_ in cnt.items() if sum(map(abs, k_)) == 2}),
                  "same_pairs": same, "fraction": str(Fr(same, len(roots) * (len(roots) - 1) // 2)),
                  "second_moment_52I": bool(np.array_equal(mom, 52 * np.eye(14)))}
    # Hilbert series coefficients and degree-2/3 ideal dimension
    coef = []
    for mm in range(6):
        from math import comb
        coef.append(comb(mm + 7, 7) + 7 * (comb(mm + 6, 7) if mm >= 1 else 0) + 6 * (comb(mm + 5, 7) if mm >= 2 else 0))
    out["hilbert_coeffs"] = coef
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
