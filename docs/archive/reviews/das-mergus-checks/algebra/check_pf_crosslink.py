"""Cross-link with registry claim a5-stiefel-pfaffian-reduction: det_C(L_a + i R_b) vs (N Q G)^2."""
import json, random
import sympy as sp
from sympy.polys.matrices import DomainMatrix
from sympy import QQ_I
from common import sign
rng = random.Random(13924)  # ANU QRNG docs/evidence/anu_qrng/draw-2026-10-25T095947Z.json index 2
res = []
for _ in range(8):
    p = [0] + [rng.randint(-9, 9) for _ in range(15)]
    q = [0] + [rng.randint(-9, 9) for _ in range(15)]
    M = [[0] * 16 for _ in range(16)]
    for r in range(16):
        for c in range(16):
            k = r ^ c
            M[r][c] = sp.Integer(p[k] * sign(16, k, c)) + sp.I * sp.Integer(q[k] * sign(16, c, k))
    d = DomainMatrix([[QQ_I.from_sympy(x) for x in row] for row in M], (16, 16), QQ_I).det()
    d = QQ_I.to_sympy(d)
    z = [sp.Integer(p[k]) + sp.I * q[k] for k in range(1, 16)]
    u, mu, v = z[:7], z[7], z[8:]
    dot = lambda a, b: sum(x * y for x, y in zip(a, b))
    U, V0, W = dot(u, u), dot(v, v), dot(u, v)
    Q = U + mu**2 + V0
    G = Q**2 - 4 * (U * V0 - W**2)
    N = sum(p[k]**2 + q[k]**2 for k in range(1, 16))
    cands = {"(NQG)^2": (N * Q * G) ** 2, "(N conj(QG))^2": (N * sp.conjugate(Q * G)) ** 2}
    res.append({k: str(sp.nsimplify(sp.expand(d / v_))) for k, v_ in cands.items()})
print(json.dumps(res, indent=1))
