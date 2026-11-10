"""Exact nullity of L_y at Q(i)-rational points of V = {z'' = lam z', z.z = 0}, z = p + i q, p0 = q0 = 0."""
import random, sys
from fractions import Fraction as F
sys.path.insert(0, "~/Projects/IBMQuantum/scripts")
import flint
import rank_locus_padic_lift as L

class G:  # Gaussian rational a + b i
    def __init__(s, a, b=0): s.a, s.b = F(a), F(b)
    def __add__(s, o): o = o if isinstance(o, G) else G(o); return G(s.a + o.a, s.b + o.b)
    __radd__ = __add__
    def __sub__(s, o): o = o if isinstance(o, G) else G(o); return G(s.a - o.a, s.b - o.b)
    def __mul__(s, o): o = o if isinstance(o, G) else G(o); return G(s.a*o.a - s.b*o.b, s.a*o.b + s.b*o.a)
    __rmul__ = __mul__
    def __neg__(s): return G(-s.a, -s.b)
    def inv(s): n = s.a*s.a + s.b*s.b; return G(s.a/n, -s.b/n)
    def __truediv__(s, o): o = o if isinstance(o, G) else G(o); return s * o.inv()

I = G(0, 1)
def rnd(rng): return G(rng.randint(-5, 5), rng.randint(-5, 5))

def point(rng, on_quadric=True):
    lam = rnd(rng); mu = rnd(rng)
    while (1 + lam*lam).a == 0 and (1 + lam*lam).b == 0: lam = rnd(rng)
    w = [None, None] + [rnd(rng) for _ in range(5)]
    target = (-(mu*mu)) / (1 + lam*lam)
    rest = G(0)
    for v in w[2:]: rest = rest + v*v
    c = target - rest
    A = rnd(rng)
    while A.a == 0 and A.b == 0: A = rnd(rng)
    w[0] = (A + c / A) / 2
    w[1] = (A - c / A) / (2 * I)
    if not on_quadric: mu = mu + 1
    z = [G(0)] * 16
    for k in range(7):
        z[1 + k] = w[k]; z[9 + k] = lam * w[k]
    z[8] = mu
    y = [zz.a for zz in z] + [zz.b for zz in z]
    return y

def nullity(y):
    return 32 - L.fmpq(L.left(y)).rank()

rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
on = [nullity(point(rng)) for _ in range(20)]
off = [nullity(point(rng, on_quadric=False)) for _ in range(5)]
print("on V:", on)
print("off the quadric z.z = 0:", off)
