"""C2 (c) on the Tuna b0 circuit (the null block e1+e17, coset 0, same block as IBM k0): selector contrast and N_hat of the
raw coin law under each mechanism, through the bracket readout."""

import importlib
from typing import Any

import c3_depol as D
import c3_mech2 as M
import c3_zz as Z
import numpy as np
from c3_data import T, matrix_for

pcb = importlib.import_module("pathion_coset_block")

n = "b0"
sign = np.sign(T[n]["ideal_c"])
Mp = matrix_for(n)


def stats(law):
    raw = Mp @ law
    plus, minus = raw[16:], raw[:16]
    plus, minus = plus / plus.sum(), minus / minus.sum()
    c = pcb.output_contrast(plus, minus)
    V = float(np.mean(c * sign))
    sel = float(plus[:8].sum() - minus[:8].sum())
    return V, sel, c.sum() / 2 / V


obs_sel = 0.0164
obs_N = 0.1537
print("observed raw: selector contrast +0.0164 +- 0.0039, N_hat +0.154 +- 0.033, V 0.442")
rows: list[Any] = []
for lab, law in (
    ("ideal, bracket readout only", T[n]["ideal"]),
    ("contraction to V=0.44 + bracket readout", 0.505 * T[n]["ideal"] + 0.495 / 32),
    ("gate Pauli depolarizing p2=0.03", D.simulate(n, 0.03)),
    ("gate depolarizing p2=0.02 + T1 25 us", D.simulate(n, 0.02, T1=25e-6)),
    ("T1 12 us", M.simulate(n, T1=12e-6)),
    ("T1 25 us", M.simulate(n, T1=25e-6)),
    ("X90 over-rotation +0.03", M.simulate(n, eps=0.03)),
    ("X90 over-rotation -0.03", M.simulate(n, eps=-0.03)),
    ("CZ phase +0.06 rad", M.simulate(n, dcz=0.06)),
    ("CZ phase -0.06 rad", M.simulate(n, dcz=-0.06)),
    ("ZZ coupler table x1", Z.law_of(n, 1.0)[0]),
    ("ZZ coupler table x-1", Z.law_of(n, -1.0)[0]),
    ("ZZ coupler table x10", Z.law_of(n, 10.0)[0]),
):
    V, sel, N = stats(law)
    print(f"{lab:44s} V {V:.3f}  selector contrast {sel:+.4f}  N_hat {N:+.4f}")
# pair-symmetric combination: contraction plus errors
print("depolarizing p2=0.03 followed by a residual contraction to the observed V:")
law = D.simulate(n, 0.03)
V, sel, N = stats(np.clip(law, 0, None))
