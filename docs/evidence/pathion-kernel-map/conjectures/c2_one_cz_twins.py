"""C2 decider, template-context controls: coin-fixed twins of b0 and the 6-CZ blocks under every mechanism of c2_tuna_mech.py.

A coin-fixed twin is the routed template with the coin's Hadamard removed and the coin prepared in |0> or |1> (one X for
|1>): every other instruction, the CZ count and the schedule of the other qubits are byte-identical
(scripts/qi_pathion_one_cz_null_cases.py, coin_fixed). The twin pair's contrast t is P(s = 0) of the coin-1 twin minus that
of the coin-0 twin; the base circuit's contrast s is the arm contrast of the coin read. Models: the c3_mech2, c3_depol and
c3_zz simulators on the routed circuits (X-axis error after every X90 and X gate, CZ phase, T1, gate depolarizing, coupler
ZZ), and two sized readout models (a selector 1 read as 0 when the coin reads 1, x 0.0362; a selector flip when q12 reads
0, x 0.036) on top of the bracket product readout of the coin series' b0 batch. Base circuits contract toward the uniform
law over 32 outcomes with the per-CZ retention that gives b0 its observed raw visibility 0.44; a twin contracts toward the
uniform law over the outcomes that carry its coin value, since its coin is classical. Coherent models are sized by the
X-axis angle that gives b0's base circuit +0.0164.

Section 3 fixes the data qubit d1 (the role q12 holds in the 6-CZ blocks) instead of the coin. b0 has no such variant:
the first single-qubit run on the qubit that starts d0 holds four gates, the data Hadamard mixed with later rotations, so
fixing d0 changes the gate sequence. Section 4 replays the over-rotation about each axis, on the pulse gates X90 and X (the admitted set) or on every single-qubit gate
(reported outside the admitted set: cqasm.md lists Rz as native on Tuna-17, so the hypothesis that Rz is a frame change, which
would exempt it from pulse errors, is unverified), before and after the gate in time, sized to b0
where an angle up to 0.15 rad reaches it.
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
from scipy.linalg import expm
from scipy.optimize import brentq

cc = importlib.import_module("qi_pathion_coset_coin_cases")
blk = importlib.import_module("qi_pathion_coset_block_cases")
oc = importlib.import_module("qi_pathion_one_cz_null_cases")

OBS_B0 = 0.0164
DROPOUT = 0.0362
FLIP = 0.036
EPS_LIMIT = 0.15
RHO = 0.505 ** (1.0 / D.T["b0"]["cz"])
SELECTOR, COIN = oc.SELECTOR, oc.COIN
REGION = oc.reference()["region"]
PLACE = dict(enumerate(REGION))
SIGMA = {
    "x": np.array([[0, 1], [1, 0]], complex),
    "y": np.array([[0, -1j], [1j, 0]]),
    "z": np.array([[1, 0], [0, -1]], complex),
}
LOW = oc.LOW_NAMES


def register(name: str, circuit, entry: dict, directory: Path) -> None:
    path = directory / f"{name}.cq"
    path.write_text(cc.circuit_text(circuit, PLACE, oc.NQUBITS, f"// {name}"), encoding="utf-8")
    D.T[name] = dict(
        roles=entry["roles"],
        counts=np.zeros(32),
        ideal=blk.ideal_of_record(circuit),
        ideal_c=entry.get("ideal_c", np.zeros(8)),
        cz=entry["cz"],
        batch="batch-02",
        cq=path,
        basis=None,
        operand=None,
    )


def p_selector0(name: str, law: np.ndarray) -> float:
    raw = D.matrix_for(name) @ law
    return float(sum(raw[i] for i in range(32) if not (i >> SELECTOR) & 1))


def arm_contrast(name: str, law: np.ndarray) -> float:
    raw = D.matrix_for(name) @ law
    plus, minus = raw[16:], raw[:16]
    plus, minus = plus / plus.sum(), minus / minus.sum()
    return float(plus[:8].sum() - minus[:8].sum())


def contract_uniform(name: str, law: np.ndarray) -> np.ndarray:
    retention = RHO ** D.T[name]["cz"]
    return retention * law + (1 - retention) / 32


def contract_coin(name: str, law: np.ndarray) -> np.ndarray:
    retention = RHO ** D.T[name]["cz"]
    return retention * law + (1 - retention) * oc.coin_mask(D.T[name]["ideal"])


def q12_bit(name: str) -> int:
    return oc.KEYS.index(next(k for k, q in D.T[name]["roles"].items() if q == 12))


def readout_models(kind: str):
    if kind == "dropout":
        return lambda name, law: oc.selector_dropout(COIN, 1, DROPOUT) @ law
    return lambda name, law: oc.selector_flip(q12_bit(name), 0, FLIP) @ law


def contrasts(base: str, laws: dict[str, np.ndarray], contract: bool) -> tuple[float, float]:
    """(s, t) of a template from the laws of its base circuit and of its coin-0 and coin-1 twins."""
    s_law = contract_uniform(base, laws["base"]) if contract else laws["base"]
    p = [
        p_selector0(
            f"{base}_coin{v}", contract_coin(f"{base}_coin{v}", laws[f"coin{v}"]) if contract else laws[f"coin{v}"]
        )
        for v in (1, 0)
    ]
    return arm_contrast(base, s_law), p[0] - p[1]


def simulate_axis(name: str, eps: float, axis: str, after: str, order: str) -> np.ndarray:
    """32-outcome law of the routed circuit with a rotation of `eps` about `axis` added to every X90 and X gate
    (after == "x90x") or to every single-qubit gate (after == "all"), applied before or after the gate in time."""
    psi = np.zeros(32, complex)
    psi[0] = 1.0
    error = expm(-0.5j * eps * SIGMA[axis])
    for opname, angle, qs in Z.parse(D.T[name]["cq"]):
        if opname == "CZ":
            psi = M.embed(np.diag([1, 1, 1, -1]).astype(complex), qs) @ psi
            continue
        hit = bool(eps) and (opname in ("X90", "X") if after == "x90x" else True)
        if hit and order == "before":
            psi = M.embed(error, qs) @ psi
        psi = M.embed(Z.gate(opname, angle), qs) @ psi
        if hit and order == "after":
            psi = M.embed(error, qs) @ psi
    prob = np.abs(psi) ** 2
    out = np.zeros(32)
    roles = D.T[name]["roles"]
    for state in range(32):
        bits = [(state >> (4 - i)) & 1 for i in range(5)]
        j = 0
        for k, key in enumerate(oc.KEYS):
            j |= bits[Z.LOC[roles[key]]] << k
        out[j] += prob[state]
    return out


def main() -> None:
    tmp = tempfile.TemporaryDirectory()
    directory = Path(tmp.name)
    plan = oc.series_plan()["templates"]
    for name in oc.TEMPLATES:
        register(f"{name}", plan[name]["circuit"], plan[name], directory)
        for value in (0, 1):
            twin = oc.twin_entry(name, value)
            register(f"{name}_coin{value}", twin["circuit"], twin, directory)
    for name in LOW:
        for value in (0, 1):
            circuit, removed = oc.fixed_qubit(plan[name]["circuit"], 1, value)
            register(f"{name}_d1_{value}", circuit, plan[name], directory)
    print("1. Coin-fixed twins: gates removed, CZ count and ideal laws")
    for name in oc.TEMPLATES:
        for value in (0, 1):
            twin = oc.twin_entry(name, value)
            ideal = D.T[f"{name}_coin{value}"]["ideal"]
            digest = hashlib.sha256((directory / f"{name}_coin{value}.cq").read_bytes()).hexdigest()[:10]
            print(
                f"  {name} coin {value}: removed {twin['removed']}, CZ {twin['cz']} (template {plan[name]['cz']}), "
                f"ideal coin read {sum(ideal[i] for i in range(32) if (i >> COIN) & 1):.3f}, "
                f"ideal P(s=0) {sum(ideal[i] for i in range(32) if not (i >> SELECTOR) & 1):.4f}, "
                f"file {digest}"
            )

    # Over-rotation angle that gives b0's base circuit +0.0164 (contracted), X axis after every X90 and X gate.
    def b0_response(eps: float) -> float:
        return arm_contrast("b0", contract_uniform("b0", simulate_axis("b0", eps, "x", "x90x", "after")))

    grid = np.linspace(0.0, EPS_LIMIT, 31)
    values = [b0_response(e) - OBS_B0 for e in grid]
    index = next(i for i in range(30) if values[i] * values[i + 1] < 0)
    eps_star = float(brentq(lambda e: b0_response(e) - OBS_B0, grid[index], grid[index + 1]))
    print(
        f"\n2. Mechanisms: raw selector contrast of the base circuit (s) and of the coin-twin pair (t); X-axis angle "
        f"{eps_star:.4f} rad sized to b0"
    )
    models: dict[str, dict[str, tuple[float, float]]] = {}
    for base in oc.TEMPLATES:
        names = {"base": base, "coin0": f"{base}_coin0", "coin1": f"{base}_coin1"}

        def laws_of(function, names=names):
            return {key: function(n) for key, n in names.items()}

        entries = {
            "ideal, bracket readout only": (laws_of(lambda n: D.T[n]["ideal"]), True),
            f"X-axis error {eps_star:.4f} rad after X90 and X": (
                laws_of(lambda n: simulate_axis(n, eps_star, "x", "x90x", "after")),
                True,
            ),
            "CZ phase +0.06 rad": (laws_of(lambda n: M.simulate(n, dcz=0.06)), True),
            "T1 12 us": (laws_of(lambda n: M.simulate(n, T1=12e-6)), False),
            "T1 25 us": (laws_of(lambda n: M.simulate(n, T1=25e-6)), False),
            "gate depolarizing p2 0.03": (laws_of(lambda n: DP.simulate(n, 0.03)), False),
            "ZZ coupler table x1": (laws_of(lambda n: Z.law_of(n, 1.0)[0]), False),
        }
        for label, (laws, contract) in entries.items():
            models.setdefault(label, {})[base] = contrasts(base, laws, contract)
        for label, kind in (
            (f"selector dropout when the coin reads 1, x {DROPOUT}", "dropout"),
            (f"selector flip when q12 reads 0, x {FLIP}", "flip"),
        ):
            fn = readout_models(kind)
            s_law = fn(base, contract_uniform(base, D.T[base]["ideal"]))
            twin_p = [
                p_selector0(
                    f"{base}_coin{v}",
                    fn(f"{base}_coin{v}", contract_coin(f"{base}_coin{v}", D.T[f"{base}_coin{v}"]["ideal"])),
                )
                for v in (1, 0)
            ]
            models.setdefault(label, {})[base] = (arm_contrast(base, s_law), twin_p[0] - twin_p[1])
    print(f"  {'mechanism':56s} " + "  ".join(f"{n:>17s}" for n in oc.TEMPLATES))
    for label, per in models.items():
        print(f"  {label:56s} " + "  ".join(f"{per[n][0]:+.4f} / {per[n][1]:+.4f}  " for n in oc.TEMPLATES))
    print("  (each cell: base s / twin t; k8 and k12 equal k4 to four decimals)")
    # Separation at the planned shots: pooled standard errors of the series design.
    design = oc.design()["pooled_se"]
    se_b0_base, se_twin = design["b0_base"], design["twin"]
    se_k_base, se_k_twin = design["base"] / np.sqrt(3), design["twin"] / np.sqrt(3)
    se_m = 1 / np.sqrt(1 / se_k_base**2 + 1 / se_k_twin**2)
    over = f"X-axis error {eps_star:.4f} rad after X90 and X"
    drop = f"selector dropout when the coin reads 1, x {DROPOUT}"
    flip = f"selector flip when q12 reads 0, x {FLIP}"
    print(
        f"\n   planned pooled standard errors: b0 base {se_b0_base:.5f}, twin {se_twin:.5f}; 6-CZ base {se_k_base:.5f}, twin {se_k_twin:.5f}, combined {se_m:.5f}"
    )
    print(
        "   separation of mechanisms in standard errors (6-CZ combined m, 6-CZ base c, 6-CZ twin d, b0 base-twin gap):"
    )
    for a, b, la, lb in (
        (over, drop, "over-rotation", "dropout"),
        (over, flip, "over-rotation", "q12 flip"),
        (drop, flip, "dropout", "q12 flip"),
    ):
        ma = (models[a]["k4"][0] / se_k_base**2 + models[a]["k4"][1] / se_k_twin**2) * se_m**2
        mb = (models[b]["k4"][0] / se_k_base**2 + models[b]["k4"][1] / se_k_twin**2) * se_m**2
        gap_a = models[a]["b0"][0] - models[a]["b0"][1]
        gap_b = models[b]["b0"][0] - models[b]["b0"][1]
        print(
            f"     {la:14s} vs {lb:9s}: m {abs(ma - mb) / se_m:5.1f}  c {abs(models[a]['k4'][0] - models[b]['k4'][0]) / se_k_base:5.1f}  "
            f"d {abs(models[a]['k4'][1] - models[b]['k4'][1]) / se_k_twin:5.1f}  b0 gap {abs(gap_a - gap_b) / np.hypot(se_b0_base, se_twin):5.1f}"
        )
    print(
        "   kept: the 6-CZ base and twin contrasts (they separate the dropout from the over-rotation and the q12 flip);"
    )
    print("   the b0 twin is kept as a control only: every modeled mechanism gives it the base value, so it separates")
    print("   no pair of modeled mechanisms, and it exposes an offset that needs the coin superposition (gap > 0).")
    print("   no twin separates the over-rotation from the q12 flip: both give the 6-CZ blocks zero.")

    print(
        "\n3. Data-qubit-fixed variants of the 6-CZ blocks (d1, the role q12 holds): P(s = 0) with d1 = 0 minus d1 = 1"
    )
    for label, fn in (
        ("ideal", lambda n, law: law),
        ("dropout", lambda n, law: oc.selector_dropout(COIN, 1, DROPOUT) @ law),
        ("q12 flip", lambda n, law: oc.selector_flip(q12_bit(n), 0, FLIP) @ law),
    ):
        diff = p_selector0("k4_d1_0", fn("k4_d1_0", D.T["k4_d1_0"]["ideal"])) - p_selector0(
            "k4_d1_1", fn("k4_d1_1", D.T["k4_d1_1"]["ideal"])
        )
        print(
            f"   {label:9s}: {diff:+.4f} ({abs(diff) / np.sqrt(0.5 / oc.BATCH_SHOTS):.2f} se at {oc.BATCH_SHOTS} shots per variant)"
        )
    print(
        "   the q12 flip leaves P(s = 0) at 1/2 for either d1, so these variants do not separate it from the over-rotation;"
    )
    print("   they are not built. b0 has no data-fixed variant: its first run on d0's starting qubit has four gates.")

    print("\n4. Over-rotation robustness: angle sized to b0 (+0.0164 contracted), 6-CZ response at that angle")
    print(f"   {'axis':4s} {'gates':6s} {'order':6s}  {'eps*':>8s}  {'b0 s':>8s}  {'k4 s':>8s}  {'k4 t':>8s}")
    bounds = []
    for axis in "xyz":
        for after in ("x90x", "all"):
            for order in ("before", "after"):
                grid = np.linspace(-EPS_LIMIT, EPS_LIMIT, 61)

                def f(e: float, axis=axis, after=after, order=order) -> float:
                    return (
                        arm_contrast("b0", contract_uniform("b0", simulate_axis("b0", e, axis, after, order))) - OBS_B0
                    )

                vals = [f(e) for e in grid]
                roots = [float(brentq(f, grid[i], grid[i + 1])) for i in range(60) if vals[i] * vals[i + 1] < 0]
                if not roots:
                    top = max(vals) + OBS_B0
                    print(
                        f"   {axis:4s} {after:6s} {order:6s}  no angle within +-{EPS_LIMIT} reaches b0 (largest {top:+.4f})"
                    )
                    continue
                for root in roots:
                    s_b0 = arm_contrast("b0", contract_uniform("b0", simulate_axis("b0", root, axis, after, order)))
                    s_k = arm_contrast("k4", contract_uniform("k4", simulate_axis("k4", root, axis, after, order)))
                    p = [
                        p_selector0(
                            f"k4_coin{v}",
                            contract_coin(f"k4_coin{v}", simulate_axis(f"k4_coin{v}", root, axis, after, order)),
                        )
                        for v in (1, 0)
                    ]
                    bounds.append((abs(s_k), abs(p[0] - p[1]), axis, after, order, root))
                    print(
                        f"   {axis:4s} {after:6s} {order:6s}  {root:+8.4f}  {s_b0:+8.4f}  {s_k:+8.4f}  {p[0] - p[1]:+8.4f}"
                    )
    admitted = [b for b in bounds if b[3] == "x90x"]
    print(
        f"   admitted set: the pulse gates X90 and X (hypothesis: Rz is a frame change; cqasm.md lists it native, so unverified); {len(admitted)} sized models, max |k4 s| "
        f"{max(b[0] for b in admitted):.4f}, max |k4 t| {max(b[1] for b in admitted):.4f}; the rows after every "
        f"single-qubit gate lie outside it (largest |k4 s| {max(b[0] for b in bounds):.4f}, |k4 t| {max(b[1] for b in bounds):.4f})"
    )
    tmp.cleanup()


if __name__ == "__main__":
    main()
