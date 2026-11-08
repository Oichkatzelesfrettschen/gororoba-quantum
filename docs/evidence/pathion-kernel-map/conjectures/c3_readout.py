"""C3: map logical bits to physical qubits, locate the shared structure of the failing bins, and test product-form readout."""

from typing import Any

import numpy as np
from c3_data import BRACKETS, T, matrix_for, ratio_of, se_ratio

print("== final layout (logical bit -> physical qubit at measurement) ==")
for n in ("ba", "bb", "b0", "xor_ba"):
    print(f"{n:7s} {T[n]['roles']}  cz {T[n]['cz']} operand {T[n]['operand']} basis {T[n]['basis']}")
# couplers used by CZs
import re

for n in ("ba", "bb", "b0", "xor_ba"):
    pairs: dict[Any, Any] = {}
    for line in T[n]["cq"].read_text().splitlines():
        m = re.match(r"CZ q\[(\d+)\], q\[(\d+)\]", line)
        if m:
            e = tuple(sorted(map(int, m.groups())))
            pairs[e] = pairs.get(e, 0) + 1
    print(f"{n:7s} CZ per physical edge: {pairs}")
print(
    "brackets (e01, e10), batch-00:",
    {q: tuple(round(x, 3) for x in v) for q, v in BRACKETS["batch-00"].items() if q in (2, 4, 8, 11, 12)},
)

obs = {}
print("\n== observed raw and corrected misfit m(y) = ratio*sign - 1 per bin (bin y = d0 + 2 d1 + 4 d2) ==")
for n in ("ba", "bb", "b0"):
    sign = np.sign(T[n]["ideal_c"])
    raw, Vr, _ = ratio_of(T[n]["counts"], sign)
    cor, Vc, _ = ratio_of(T[n]["counts"], sign, matrix_for(n))
    sr, sc = se_ratio(T[n]["counts"], sign), se_ratio(T[n]["counts"], sign, matrix_for(n))
    obs[n] = dict(raw=raw, cor=cor, se_raw=sr, se_cor=sc, Vr=Vr, Vc=Vc)
    print(
        f"{n}: raw m {np.round(raw - 1, 3)} (se ~{sr.mean():.3f}); corrected m {np.round(cor - 1, 3)} (se ~{sc.mean():.3f}); V raw {Vr:.3f} corrected {Vc:.3f}"
    )
    for lab, bit in (("d0", 0), ("d1", 1), ("d2", 2)):
        hi = np.array([(y >> bit) & 1 for y in range(8)], bool)
        d = (cor - 1)[hi].mean() - (cor - 1)[~hi].mean()
        se = np.sqrt((sc[hi] ** 2).sum() + (sc[~hi] ** 2).sum()) / 4
        dr = (raw - 1)[hi].mean() - (raw - 1)[~hi].mean()
        print(
            f"    split by bin bit {lab} (physical qubit {T[n]['roles'][lab]}): corrected {d:+.3f} +- {se:.3f} (z {d / se:+.1f}); raw {dr:+.3f}"
        )
    for lab in ("d0", "d1", "d2"):
        q = T[n]["roles"][lab]
        print(
            f"    logical {lab} on q{q}: e01 {BRACKETS[T[n]['batch']][q][0]:.3f} e10 {BRACKETS[T[n]['batch']][q][1]:.3f}",
            end=";",
        )
    print()

print(
    "\n== product-form readout model: ideal coin law contracted toward uniform, then the bracket misassignment of the five qubits =="
)
chi_raw = chi_cor = 0.0
for n in ("ba", "bb", "b0"):
    sign = np.sign(T[n]["ideal_c"])
    M = matrix_for(n)
    best: Any = None
    for rho in np.linspace(0.2, 1.0, 161):
        law = M @ (rho * T[n]["ideal"] + (1 - rho) / 32)
        r, V, _ = ratio_of(law * 1e6, sign)
        if best is None or abs(V - obs[n]["Vr"]) < abs(best[1] - obs[n]["Vr"]):
            best = (rho, V, r)
    rho, V, r = best
    z = (obs[n]["raw"] - r) / obs[n]["se_raw"]
    chi = float((z**2).sum())
    chi_raw += chi
    print(
        f"{n}: contraction rho {rho:.3f} (V {V:.3f} vs observed {obs[n]['Vr']:.3f}); predicted raw m {np.round(r - 1, 3)}; observed - predicted {np.round(obs[n]['raw'] - r, 3)}; chi2 {chi:.1f} on 8 bins (7 dof after V)"
    )
print(
    f"total raw chi2 over three templates {chi_raw:.1f} (24 bins, 21 dof); a corrected-ratio of exactly 1 would be the prediction of the corrected statistic: chi2 of corrected m {sum(float((((obs[n]['cor'] - 1) / obs[n]['se_cor']) ** 2).sum()) for n in ('ba', 'bb', 'b0')):.1f}"
)
