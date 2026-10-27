"""Descriptive ablation of the case-2 excitation term on the four high-bound paths (no QPU).

Variants: V0 zero; V1 path-max upper bound, leading X on every qubit (the retained rule);
V2 per-qubit upper bound, leading X; V3 per-qubit point estimate, leading X;
V4 split: history-dependent point (x_history - prep0) as leading X, history-independent
(prep0 - e10) as terminal e10; V5 all point excess as terminal e10, no leading X.
Centers swap the retained incoherent shift for the variant's; half-widths are the retained ones.
"""

import copy
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path.cwd()
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import primorial_cover_noise as noise  # noqa: E402
import primorial_probe_case as ppc  # noqa: E402
from qiskit_aer.noise import pauli_error  # noqa: E402

import calibration_snapshot  # noqa: E402
import dynamic_density  # noqa: E402
import parallel  # noqa: E402
import primorial_tomography as tomo  # noqa: E402

E = ROOT / "docs/evidence/primorial_cover/case2"
SNAP = json.loads((E / "stage1-snapshot.json").read_text())
DEC = json.loads((E / "stage1-decision.json").read_text())
FAL = json.loads((E / "stage2-falsification.json").read_text())
EXC = json.loads((ROOT / "results/live/2026-10-26T215024.737181Z/state-prep-excess.json").read_text())
PATHS = [[58, 71, 72], [15, 19, 35], [100, 101, 102], [132, 133, 134]]
KEYS = ("01", "02")


def with_vector(circuit, eps):
    out = circuit.copy_empty_like()
    for qubit in dynamic_density._active(circuit):
        e = eps.get(qubit, 0.0)
        if e > 0:
            out.append(pauli_error([("X", e), ("I", 1 - e)]).to_instruction(), [out.qubits[qubit]])
    for item in circuit.data:
        out.append(item)
    return out


VIEWS: dict[str, object] = {}


def compile_item(item):
    """One (snapshot, logical, path) arm -> its compile_arm circuit; each process builds a snapshot's view once."""
    snapshot, logical, path = item
    key = hashlib.sha256(json.dumps(snapshot, sort_keys=True).encode()).hexdigest()
    if key not in VIEWS:
        VIEWS[key] = calibration_snapshot.snapshot_backend(snapshot)
    return noise.compile_arm(VIEWS[key], logical, path)


def law(item):
    snapshot, meta, logical, compiled, eps = item
    expected = noise.ideal_law(logical)
    excited = with_vector(compiled, eps)
    values = ppc.snapshot_laws.outcome_law(snapshot, excited, "CPU")
    return {**meta, "ideal": [round(float(v), 12) for v in expected], "law": [float(v) for v in values]}


def fit(rows):
    exact = tomo.coefficients(tomo.cost_table("gap88"))
    recovered = tomo.gradient_analysis(rows, "gap88")["null_subtracted"]["recovered_coefficients"]
    return {k: float(recovered[k] - exact[k]) for k in KEYS}


def shifts(variants):
    """variants: name -> per path, (per-qubit leading-X dict, per-qubit terminal e10 additions).

    Every (variant, path) unit is independent, so compilation, the noisy laws and the fits each run as one
    order-preserving map over all units.
    """
    logical = [
        (m, c)
        for m, c in noise.arms()
        if (m["family"] == "gradient" and m["cost"] in ("gap88", "null")) or m["family"] == "readout3"
    ]
    units = []
    for name, variant in variants.items():
        for path, (lead, term) in zip(PATHS, variant, strict=True):
            snap = copy.deepcopy(SNAP)
            for q, add in term.items():
                snap["qubits"][q]["e10"] = snap["qubits"][q]["e10"] + add
            units.append((name, path, lead, snap))
    compiled = parallel.ordered_map(
        compile_item, [(snap, c, path) for _, path, _, snap in units for _, c in logical], min_items=1
    )
    items = [
        (snap, m, c, compiled[u * len(logical) + a], lead)
        for u, (_, _, lead, snap) in enumerate(units)
        for a, (m, c) in enumerate(logical)
    ]
    laws = parallel.ordered_map(law, items, min_items=1)
    blocks = [laws[u * len(logical) : (u + 1) * len(logical)] for u in range(len(units))]
    fits = parallel.ordered_map(fit, blocks, min_items=1)
    out: dict[str, list] = {name: [] for name in variants}
    for (name, _, _, _), row in zip(units, fits, strict=True):
        out[name].append(row)
    return out


def q(qubit):
    row = EXC["qubits"][str(qubit)]
    p0 = row["fractions"]["prep0_2e-05s"]
    xh = row["fractions"]["x_history_2e-05s"]
    e10, e01 = row["model_readout"]["prob_meas1_prep0"], row["model_readout"]["prob_meas0_prep1"]
    b = min(p0, e10)
    return {
        "upper": float(row["eps"]["2e-05s"]),
        "point": max(0.0, (xh - b) / (1 - e01 - b)),
        "hd": max(0.0, (xh - p0) / (1 - e01 - p0)),
        "hi": max(0.0, p0 - e10),
    }


def main():
    per = {qq: q(qq) for p in PATHS for qq in p}
    pmax = {tuple(p): e for p, e in zip(DEC["paths"], DEC["prep_excitation"], strict=True)}
    variants = {
        "V0 zero": [({}, {}) for p in PATHS],
        "V1 path-max upper X": [({qq: pmax[tuple(p)] for qq in p}, {}) for p in PATHS],
        "V2 per-qubit upper X": [({qq: per[qq]["upper"] for qq in p}, {}) for p in PATHS],
        "V3 per-qubit point X": [({qq: per[qq]["point"] for qq in p}, {}) for p in PATHS],
        "V4 split X+e10": [({qq: per[qq]["hd"] for qq in p}, {qq: per[qq]["hi"] for qq in p}) for p in PATHS],
        "V5 all terminal e10": [({}, {qq: per[qq]["point"] for qq in p}) for p in PATHS],
    }
    retained = {tuple(r["path"]): r for r in FAL["paths"]}
    results = shifts(variants)
    base = results["V1 path-max upper X"]
    report = {"per_qubit": per, "variants": {}}
    for name, rows in results.items():
        report["variants"][name] = []
        for p, row, b1 in zip(PATHS, rows, base, strict=True):
            r = retained[tuple(p)]
            cells = {}
            for k in KEYS:
                lo, hi = r["bands"][k]
                half = (hi - lo) / 2
                center = (lo + hi) / 2 - b1[k] + row[k]
                cells[k] = {
                    "shift": round(row[k], 5),
                    "center": round(center, 5),
                    "observed": round(r["observed_bias"][k], 5),
                    "dev_half_widths": round((r["observed_bias"][k] - center) / half, 2),
                }
            report["variants"][name].append({"path": p, **cells})
            print(name, p, {k: (cells[k]["center"], cells[k]["dev_half_widths"]) for k in KEYS})
    Path(sys.argv[1]).write_text(json.dumps(report, indent=1) + "\n")


if __name__ == "__main__":
    main()
