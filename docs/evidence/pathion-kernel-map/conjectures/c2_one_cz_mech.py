"""C2 decider check: selector contrast and N_hat of the low-CZ null blocks (coset 4, 8, 12 of e1 + e17) beside the retained b0
under every mechanism of c2_tuna_mech.py, on routed Tuna-17 circuits that end on b0's physical qubits.

Two routings of each low-CZ block are read, both from scripts/qi_pathion_one_cz_null_cases.py (--select repeats the search):
"roles" keeps b0's whole role map (d0 q12, d1 q4, d2 q11, selector q8, coin q2); "_sc" keeps only the selector on q8 and the
coin on q2. The mechanism simulators are c3_mech2 (X90 over-rotation, CZ phase, T1), c3_depol (gate depolarizing) and c3_zz
(coupler ZZ), which read their circuit and role map from c3_data.T, so each block enters T under its own name; the readout
is the bracket of the coin series' b0 batch, whose qubits and roles every block shares.

Two selector readout families sit on top of the bracket product readout and a per-CZ contraction fixed by b0's observed
visibility. "flip" flips the selector (q8) with probability x when a source qubit reads 1 (or 0), through c3_corr.flip_matrix.
"dropout" reads a true selector 1 as 0 with probability x when the source reads 1 (or 0): with the source the coin (q2) it is
an arm-asymmetric readout, which no block's routing can remove. x is sized so that b0 reads the observed selector contrast;
each (family, source, state) that reaches it is a model, and its prediction for every block is the number the decider
compares with an over-rotation.

Decision gate (brief of the one-CZ null case): over-rotation (uncontracted, an upper bound of its magnitude) must give a
selector contrast of at most 0.004 on every block while every sized correlated-readout model gives at least 0.012.
"""

import hashlib
import importlib
import tempfile
from pathlib import Path

import c3_data as D
import c3_depol as DP
import c3_mech2 as M
import c3_zz as Z
import numpy as np
from c3_corr import flip_matrix
from scipy.optimize import brentq

cc = importlib.import_module("qi_pathion_coset_coin_cases")
oc = importlib.import_module("qi_pathion_one_cz_null_cases")
pcb = importlib.import_module("pathion_coset_block")

OBS_SELECTOR = 0.0164
OVER_ROTATION_LIMIT = 0.004
READOUT_FLOOR = 0.012
EPS = 0.03
SELECTOR = oc.KEYS.index("selector")
REGION = oc.reference()["region"]
PLACE = dict(enumerate(REGION))


def register(name: str, entry: dict, path: Path) -> None:
    path.write_text(cc.circuit_text(entry["circuit"], PLACE, oc.NQUBITS, f"// {name}"), encoding="utf-8")
    D.T[name] = dict(
        roles=entry["roles"],
        counts=np.zeros(32),
        ideal=entry["ideal"],
        ideal_c=entry["ideal_c"],
        cz=entry["cz"],
        batch="batch-02",
        cq=path,
        basis=None,
        operand=None,
    )


def stats(name: str, law: np.ndarray) -> tuple[float, float, float]:
    """(V, selector contrast, N_hat) of a 32-outcome law through b0's bracket readout, as c2_tuna_mech.stats."""
    sign = np.sign(D.T[name]["ideal_c"])
    raw = D.matrix_for(name) @ law
    plus, minus = raw[16:], raw[:16]
    plus, minus = plus / plus.sum(), minus / minus.sum()
    c = pcb.output_contrast(plus, minus)
    v = float(np.mean(c * sign))
    return v, float(plus[:8].sum() - minus[:8].sum()), float(c.sum() / 2 / v)


# Per-CZ retention that takes b0 (21 CZ) to the observed raw visibility 0.44 through its readout, as c2_tuna_mech.py
RHO = 0.505 ** (1.0 / D.T["b0"]["cz"])


def contracted(name: str, law: np.ndarray) -> np.ndarray:
    retention = RHO ** D.T[name]["cz"]
    return retention * law + (1 - retention) / law.size


def source_bit(name: str, qubit: int) -> int:
    roles = D.T[name]["roles"]
    return oc.KEYS.index(next(k for k, q in roles.items() if q == qubit))


def dropout_matrix(source: int, state: int, x: float) -> np.ndarray:
    """32x32 stochastic matrix: a true selector 1 reads 0 with probability x when bit `source` of the state is `state`."""
    matrix = np.eye(32)
    for s in range(32):
        if (s >> SELECTOR) & 1 and (s >> source) & 1 == state:
            matrix[s, s] -= x
            matrix[s ^ (1 << SELECTOR), s] += x
    return matrix


def correlated_law(name: str, family: str, qubit: int, state: int, x: float) -> np.ndarray:
    source = source_bit(name, qubit)
    if family == "flip":
        extra = flip_matrix(source, SELECTOR, x if state == 0 else 0.0, x if state == 1 else 0.0)
    else:
        extra = dropout_matrix(source, state, x)
    return extra @ contracted(name, D.T[name]["ideal"])


def size_model(family: str, qubit: int, state: int) -> float | None:
    """x in (0, 0.5] at which b0 reads the observed selector contrast, None when no such x exists."""

    def gap(x: float) -> float:
        return stats("b0", correlated_law("b0", family, qubit, state, x))[1] - OBS_SELECTOR

    return float(brentq(gap, 1e-6, 0.5)) if gap(1e-6) * gap(0.5) < 0 else None


def main() -> None:
    tmp = tempfile.TemporaryDirectory()
    rows: dict[str, dict] = {}
    for mode, suffix in (("roles", ""), ("selector_coin", "_sc")):
        for block, _ in oc.LOW_CZ:
            entry = oc.routed(mode, block)
            register(block + suffix, entry, Path(tmp.name) / f"{block}{suffix}.cq")
            rows[block + suffix] = entry
    names = ["b0", *rows]
    print("routed blocks on the retained b0 qubits (region q2, q4, q8, q11, q12)")
    print(f"  b0   replay of the retained compile  cz {D.T['b0']['cz']}  roles {D.T['b0']['roles']}")
    for name, entry in rows.items():
        print(
            f"  {name:7s} cz {entry['cz']:2d}  roles {entry['roles']}  draw index {entry['draw_index']}  "
            f"initial layout {entry['initial_layout']}  ideal selector contrast {'0' if abs(entry['ideal_selector_contrast']) < 1e-9 else 'nonzero'}"
        )
    print(f"observed b0 raw selector contrast {OBS_SELECTOR:+.4f} +- 0.0039; per-CZ retention {RHO:.4f}")
    table: dict[str, dict[str, tuple[float, float, float]]] = {n: {} for n in names}
    for name in names:
        mechanisms = (
            ("ideal, bracket readout only", D.T[name]["ideal"]),
            ("contraction to V=0.44 + bracket readout", contracted(name, D.T[name]["ideal"])),
            ("gate Pauli depolarizing p2=0.03", DP.simulate(name, 0.03)),
            ("gate depolarizing p2=0.02 + T1 25 us", DP.simulate(name, 0.02, T1=25e-6)),
            ("T1 12 us", M.simulate(name, T1=12e-6)),
            ("T1 25 us", M.simulate(name, T1=25e-6)),
            ("X90 over-rotation +0.03", M.simulate(name, eps=EPS)),
            ("X90 over-rotation -0.03", M.simulate(name, eps=-EPS)),
            ("X90 over-rotation +0.03 with contraction", contracted(name, M.simulate(name, eps=EPS))),
            ("CZ phase +0.06 rad", M.simulate(name, dcz=0.06)),
            ("CZ phase -0.06 rad", M.simulate(name, dcz=-0.06)),
            ("ZZ coupler table x1", Z.law_of(name, 1.0)[0]),
        )
        for label, law in mechanisms:
            table[name][label] = stats(name, law)
    models = []
    for family in ("flip", "dropout"):
        for qubit in sorted(set(REGION) - {8}):
            for state in (1, 0):
                x = size_model(family, qubit, state)
                if x is not None:
                    models.append((family, qubit, state, x))
    for family, qubit, state, x in models:
        label = f"selector readout, {family} on q8 when q{qubit} = {state}, x {x:.4f}"
        for name in names:
            table[name][label] = stats(name, correlated_law(name, family, qubit, state, x))
    for name in names:
        print(f"{name}  (cz {D.T[name]['cz']}, ideal c {np.round(D.T[name]['ideal_c'], 3)[:2]}...)")
        for label, (v, sel, n) in table[name].items():
            print(f"  {label:70s} V {v:.3f}  selector contrast {sel:+.4f}  N_hat {n:+.4f}")
    print(
        f"decision gate per routing and model: over-rotation at most {OVER_ROTATION_LIMIT} in magnitude on every block "
        f"(sign and size of EPS = {EPS} rad), the model at least {READOUT_FLOOR} on every block"
    )
    over = ("X90 over-rotation +0.03", "X90 over-rotation -0.03")
    for mode, suffix in (("roles", ""), ("selector_coin", "_sc")):
        blocks = [f"{b}{suffix}" for b, _ in oc.LOW_CZ]
        worst = max(abs(table[b][label][1]) for b in blocks for label in over)
        print(f"  {mode}: max |selector| under over-rotation {worst:.4f}")
        for family, qubit, state, x in models:
            label = f"selector readout, {family} on q8 when q{qubit} = {state}, x {x:.4f}"
            floor = min(table[b][label][1] for b in blocks)
            verdict = (
                "discriminates" if worst <= OVER_ROTATION_LIMIT and floor >= READOUT_FLOOR else "does not discriminate"
            )
            print(f"    {label}: min selector over the blocks {floor:+.4f} -> {verdict}")
    print("over-rotation response of every distinct routed circuit that meets the roles pin (search of --select)")
    seen: dict[str, tuple[str, int, float]] = {}
    for block, _ in oc.LOW_CZ:
        for _cz, draw_index, layout, seed, final in oc.search_table()[block]:
            if not oc.pinned("roles", final):
                continue
            entry = oc.entry_of(block, oc.compile_pinned(block, layout, seed), seed, draw_index, layout)
            text = oc.template_text(block, entry)
            body = "\n".join(line for line in text.splitlines() if not line.startswith("//"))
            key = block + hashlib.sha256(body.encode()).hexdigest()
            if key in seen:
                continue
            path = Path(tmp.name) / f"cand{len(seen)}.cq"
            register(f"cand{len(seen)}", entry, path)
            response = max(
                abs(stats(f"cand{len(seen)}", M.simulate(f"cand{len(seen)}", eps=e))[1]) for e in (EPS, -EPS)
            )
            seen[key] = (block, entry["cz"], response)
    for block, _ in oc.LOW_CZ:
        distinct = [v for v in seen.values() if v[0] == block]
        print(
            f"  {block}: {len(distinct)} distinct circuits, CZ {sorted({r[1] for r in distinct})}, "
            f"max |selector| under +-{EPS} rad over-rotation: min {min(r[2] for r in distinct):.4f}, "
            f"max {max(r[2] for r in distinct):.4f}"
        )
    tmp.cleanup()


if __name__ == "__main__":
    main()
