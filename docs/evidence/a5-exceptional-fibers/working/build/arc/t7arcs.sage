# Order-1 arcs on the normalization of chart t7 = 1 of the E8-bar -> VB strict transform at p = 32009.
# Falsification test of the inference that chart t7 adds nothing over chart t1: at base points (t1:t3:t5:1) of P(L)
# with t1 != 0, the leading G-vector F of every order-1 arc must lie in V(P2); an F outside V(P2), or in V(P1),
# falsifies it. Base points are fixed small integers (no seed); the normalization fiber over each point is solved over
# GF(p^2) so that both branches are found whether or not they are rational.
# usage: sage t7arcs.sage NORD [plane]  (plane: base points with t1 = 0, the stratum chart t1 cannot see, and the
# point t1 = t3 = t5 = 0 that only chart t7 holds)
import re, sys
p = 32009
K = GF(p ^ 2, 'a')
names = ['T1', 'T2', 'T3', 'T4', 'h', 't1', 't2', 't3', 't4', 't5', 't6', 't8']
R = PolynomialRing(K, names)
g = dict(zip(names, R.gens()))
txt = open('chart_t7_norid_1.txt').read().strip().replace('\n', '')
N = [R(x) for x in re.sub(r'T\((\d+)\)', r'T\1', txt).split(',')]
dep_names = ['T1', 'T2', 'T3', 'T4', 't2', 't4', 't6', 't8']
free_names = ['t1', 't3', 't5']
Rg = PolynomialRing(K, ['t%d' % i for i in range(1, 9)])
Gl = [Rg(x) for x in open('G.txt').read().strip().replace('\n', '').split(',')]
ys = PolynomialRing(K, ['y%d' % i for i in range(1, 11)])
Pr = [[ys(re.sub(r'y\((\d+)\)', r'y\1', x)) for x in open(fn).read().strip().split(',')]
      for fn in ['primeP1.txt', 'primeP2.txt']]
Sr = PolynomialRing(K, 's')
s = Sr.gen()


def tr(f, n):
    return Sr(f.list()[:n + 1])


def ev(f, x, n):
    out = Sr.zero()
    pw = {}
    for e, c in f.dict().items():
        term = Sr(c)
        for i in range(len(e)):
            if e[i]:
                key = (i, e[i])
                if key not in pw:
                    r = Sr.one()
                    for _ in range(e[i]):
                        r = tr(r * x[i], n)
                    pw[key] = r
                term = tr(term * pw[key], n)
        out += term
    return tr(out, n)


def base_points(v1, v3, v5):
    """Points of the normalization over the P(L) point (v1:v3:v5:1), h = 0."""
    fix = {g['h']: 0, g['t1']: v1, g['t2']: 0, g['t3']: v3, g['t4']: -v3, g['t5']: v5, g['t6']: v5, g['t8']: 0}
    RT = PolynomialRing(K, ['T1', 'T2', 'T3', 'T4'])
    I = RT.ideal([RT(f.subs(fix)) for f in N])
    if I.dimension() != 0:
        return None, I.dimension()
    pts = []
    for sol in I.variety():
        x = [Sr(0)] * 12
        for j, n in enumerate(['T1', 'T2', 'T3', 'T4']):
            x[j] = Sr(sol[RT.gen(j)])
        x[4] = s
        x[5] = Sr(v1)
        x[6] = Sr(0)
        x[7] = Sr(v3)
        x[8] = Sr(-v3)
        x[9] = Sr(v5)
        x[10] = Sr(v5)
        x[11] = Sr(0)
        pts.append(x)
    return pts, 0


def select_relations(x):
    """Greedy choice of 8 relations whose Jacobian in the dependent coordinates is invertible at x."""
    depg = [g[n] for n in dep_names]
    rows, chosen = [], []
    for i, f in enumerate(N):
        row = [ev(f.derivative(v), x, 0)[0] for v in depg]
        if Matrix(K, rows + [row]).rank() > len(rows):
            rows.append(row)
            chosen.append(i)
        if len(rows) == 8:
            return chosen, Matrix(K, rows)
    return None, Matrix(K, rows)


def lift(x, NORD):
    chosen, M0 = select_relations(x)
    if chosen is None:
        return None, M0.rank()
    Fs = [N[i] for i in chosen]
    Mi = M0.inverse()
    idx = [names.index(n) for n in dep_names]
    for n in range(1, NORD + 1):
        res = vector(K, [ev(f, x, n)[n] for f in Fs])
        corr = -Mi * res
        for b, i in enumerate(idx):
            x[i] = x[i] + corr[b] * s ^ n
    return x, 8


def lead(x, NORD):
    # original coordinates t_j = s * tt_j with tt7 = 1; names order: h at 4, t1..t6 at 5..10, t8 at 11
    tt = [tr(s * x[5 + j], NORD + 1) for j in range(6)] + [s, tr(s * x[11], NORD + 1)]
    ser = [ev(G, tt, NORD + 1) for G in Gl]
    nz = [f.valuation() for f in ser if f != 0]
    if not nz:
        return None, None
    nu = min(nz)
    return nu, [f[nu] for f in ser]


NORD = int(sys.argv[1])
pts = [(1, 2, 3), (2, 5, 7), (3, 1, 4), (5, 9, 2), (7, 3, 11), (4, 6, 1), (11, 13, 17), (6, 2, 9), (1, 1, 1), (9, 4, 5)]
if len(sys.argv) > 2 and sys.argv[2] == 'plane':
    pts = [(0, 2, 3), (0, 5, 7), (0, 1, 4), (0, 9, 2), (0, 1, 1), (0, 3, 0), (0, 0, 5), (0, 0, 0)]
if len(sys.argv) > 2 and sys.argv[2] == 'apex':
    pts = [(0, 0, 0)]
stats = {'arcs': 0, 'inP1': 0, 'inP2': 0, 'neither': 0}
for (v1, v3, v5) in pts:
    bp, d = base_points(K(v1), K(v3), K(v5))
    if bp is None:
        print('point', (v1, v3, v5), 'fiber dimension', d)
        continue
    print('point', (v1, v3, v5), 'branches', len(bp))
    for br, x in enumerate(bp):
        x, rk = lift(list(x), NORD)
        if x is None:
            print('  branch', br, 'jacobian rank', rk, '(singular point of the normalization)')
            continue
        resid = sum(1 for f in N if ev(f, x, NORD) != 0)
        nu, Fv = lead(x, NORD)
        if nu is None:
            print('  branch', br, 'resid_eq_nonzero', resid, 'G vanishes through order', NORD + 1)
            continue
        inP = [all(pg(*Fv) == 0 for pg in Pp) for Pp in Pr]
        stats['arcs'] += 1
        stats['inP1'] += inP[0]
        stats['inP2'] += inP[1]
        stats['neither'] += (not inP[0] and not inP[1])
        print('  branch', br, 'resid_eq_nonzero', resid, 'nu', nu, 'inP1,P2', inP, 'F', [str(c) for c in Fv])
        sys.stdout.flush()
print('SUMMARY', stats)
