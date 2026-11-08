"""C2 (b): exact check of what an arm-symmetric readout map does to the ideal null block (ideal laws of record, Fez k0)."""

import importlib

import numpy as np
from c2_data import load_ibm

pcb = importlib.import_module("pathion_coset_block")

cnt, rec = load_ibm("fez")
G = rec["groups"][0]
ip = np.array(next(m for m in G["members"] if m["name"] == "cmap_e1pe17_k0_plus")["ideal"], float)
im = np.array(next(m for m in G["members"] if m["name"] == "cmap_e1pe17_k0_minus")["ideal"], float)
# QRNG seed: docs/evidence/anu_qrng/draw-2026-10-25T015224Z.json index 7
rng = np.random.default_rng(9346)
mx_sel = mx_sumc = 0.0
signs = []
for _ in range(5000):
    M = np.array([[1.0]])
    for _q in range(4):
        e01, e10 = rng.uniform(0, 0.1, 2)
        M = np.kron(np.array([[1 - e01, e10], [e01, 1 - e10]]), M)
    p, m = M @ ip, M @ im
    sel = p[:8].sum() - m[:8].sum()
    sc = pcb.output_contrast(p, m).sum()
    mx_sel = max(mx_sel, abs(sel))
    mx_sumc = max(mx_sumc, abs(sc))
    signs.append(np.sign(sc) * np.sign(sum(0 for _ in [0]) + 1))
    # symmetric flips (e01 == e10) as the special case
sym = []
for _ in range(2000):
    e = rng.uniform(0, 0.1, 4)
    M = np.array([[1.0]])
    for q in range(4):
        M = np.kron(np.array([[1 - e[q], e[q]], [e[q], 1 - e[q]]]), M)
    sym.append(abs(pcb.output_contrast(M @ ip, M @ im).sum()))
print(
    f"product-form asymmetric readout, 5000 draws (e01, e10 in [0, 0.1]): max |selector contrast| {mx_sel:.1e}; max |sum_y c(y)| {mx_sumc:.3f}"
)
print(f"product-form SYMMETRIC readout (e01 = e10 per qubit), 2000 draws: max |sum_y c(y)| {max(sym):.1e}")
# sign of the offset against e10 - e01 for the calibrated placed qubits of replica 0
pq = G["placed_qubit_calibration"]
M = np.array([[1.0]])
for q in (26, 37, 24, 25):  # clbit 0..3 order from the replica map
    r = pq[str(q)]
    e01, e10 = r["prob_meas1_prep0"], r["prob_meas0_prep1"]
    M = np.kron(np.array([[1 - e01, e10], [e01, 1 - e10]]), M)
print(
    f"replica-0 calibrated readout: sum c {pcb.output_contrast(M @ ip, M @ im).sum():+.4f}, selector {((M @ ip)[:8].sum() - (M @ im)[:8].sum()):+.1e}"
)
