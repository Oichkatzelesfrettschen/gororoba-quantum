"""C3: Walsh decomposition of the corrected misfit m(y) over the three bin bits: the coefficient of each character with its se."""

import numpy as np
from c3_data import T, matrix_for, ratio_of, se_ratio

names = ("ba", "bb", "b0")
chars = {"d0": (1,), "d1": (2,), "d2": (4,), "d0d1": (1, 2), "d0d2": (1, 4), "d1d2": (2, 4), "d0d1d2": (1, 2, 4)}
print(
    "Walsh coefficient (m = mean + sum coef * product of (+-1 for bit)); coefficient +- se; sign convention +1 when the bit is 1"
)
tab = {}
for n in names:
    sign = np.sign(T[n]["ideal_c"])
    cor, V, _ = ratio_of(T[n]["counts"], sign, matrix_for(n))
    se = se_ratio(T[n]["counts"], sign, matrix_for(n))
    m = cor - 1
    out = {}
    for lab, bits in chars.items():
        chi = np.array([np.prod([1 if (y & b) else -1 for b in bits]) for y in range(8)])
        out[lab] = (float(np.mean(m * chi)), float(np.sqrt((se**2).sum()) / 8))
    tab[n] = out
for lab in chars:
    print(
        f"{lab:7s} "
        + "   ".join(
            f"{n}: {tab[n][lab][0]:+.3f} +- {tab[n][lab][1]:.3f} (z {tab[n][lab][0] / tab[n][lab][1]:+.1f})"
            for n in names
        )
    )
