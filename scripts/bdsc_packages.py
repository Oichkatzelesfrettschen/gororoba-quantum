"""Package cross-checks of the dark-subspace certificate: hypercomplex, hyprat, python-flint, sympy and Perceval.

Each package re-derives part of docs/evidence/bdsc/target.json and bank.json
through its own arithmetic; cd_core stays the specification, and a package
result enters only through the identity map onto it that
docs/evidence/algebra_packages/tables.json already certifies.

- Algebra. python-hypercomplex (cayley_dickson_algebra(4, Fraction)) and
  hyprat (mu = -1) form L_int = L_(e1 + e10) column by column from exact
  products, so E0 = L_int^T L_int / 4 and x w_j = 0 for the four kernel
  vectors come from each package's own multiplication.
- Exact linear algebra. python-flint fmpq_mat gives rank E0 = 12,
  rank(E0 - I/2) = 8, rank(E0 - I) = 12, E0 (2 E0 - I)(E0 - I) = 0 and the
  characteristic polynomial x^4 (x - 1/2)^8 (x - 1)^4; with E0 W_K = 0 and
  rank W_K = 4 the kernel is exactly span W_K. sympy, over Q(sqrt2), checks
  U24^T U24 = I and the selected compression = E0 symbolically.
- Optics. Perceval builds U24 natively as PERM_in, twelve BS.H on wire
  pairs (2j, 2j + 1) and PERM_out, with no phase shifter: on each output
  pair the target block is BS.H itself, rows ordered (A_j, D_j) or (D_j,
  A_j) by the kernel pair's sign. SLOS then sends one photon from the source
  wire through a Householder preparation unitary and the native circuit for
  every bank and pilot setting, three ways: lossless; under NoiseModel
  transmittance with min_detected_photons 1 (uniform loss is scalar
  acceptance, so the conditional share is the ideal); and with LC loss
  components on chosen output modes, whose conditional share must equal
  Tr(G rho) / Tr(D rho) from bdsc.acceptance. A NoiseModel g2 run records
  the accepted multi-photon share.
- Processing. Perceval 1.3.1's DetectorBalancing runs the computation as
  probs, divides each state by its detection probability and converts back
  through probs_to_sample_count, which perturbs each probability by a
  normal draw, clips at 0, renormalizes and rounds. A seeded run of that
  conversion at p = 1e-4 and 10^4 samples reads the zero-count frequency
  against the binomial (1 - p)^n and the mean count against n p; the gap
  falsifies Bernoulli trials for converted counts, and the clip at 0 biases
  a small probability upward.

--write OUT runs every package (build host) and writes the record; --check
OUT replays it with numpy alone (shares against the exact ideals and the
acceptance model, the conversion against the binomial) and re-derives it
live wherever every package imports.

Usage: "$PYTHON" scripts/bdsc_packages.py (--write OUT | --check OUT)
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import random
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
import bdsc_certificate as cert  # noqa: E402

import bdsc  # noqa: E402
import parallel  # noqa: E402

SCHEMA = "bdsc-packages-v1"
TARGET = ROOT / "docs/evidence/bdsc/target.json"
BANK = ROOT / "docs/evidence/bdsc/bank.json"
PACKAGES = ("perceval", "hypercomplex", "hyprat", "flint", "sympy")
SHARE_TOLERANCE = 1e-9
TRANSMITTANCE = 0.0289
G2 = 0.01
INDISTINGUISHABILITY = 0.942
# Relative output efficiencies for the LC run: a 2 % ladder over mode index mod 5 touches every output pair role.
LC_EFFICIENCY = tuple(1.0 - 0.02 * (m % 5) for m in range(cert.MODES))
CONVERSION_P = 1e-4
CONVERSION_COUNT = 10_000
CONVERSION_DRAWS = 20_000
CONVERSION_SEED = 20261020
CONVERSION_Z_MIN = 6.0


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def versions() -> dict[str, str]:
    from importlib import metadata

    names = {
        "perceval": "perceval-quandela",
        "hypercomplex": "hypercomplex",
        "hyprat": "hyprat",
        "flint": "python-flint",
        "sympy": "sympy",
    }
    return {key: metadata.version(dist) for key, dist in names.items()}


def available() -> bool:
    try:
        for name in PACKAGES:
            importlib.import_module(name)
    except ImportError:
        return False
    return True


# --- algebra -------------------------------------------------------------------------------


def unit_vector(index: int) -> list[Fraction]:
    return [Fraction(int(i == index)) for i in range(bdsc.DIM)]


def x_coefficients() -> list[Fraction]:
    return [Fraction(int(i in bdsc.X_LABELS)) for i in range(bdsc.DIM)]


def package_products() -> dict[str, Any]:
    """Callables (left, right) -> coefficient list for each exact package."""
    import hypercomplex
    import hyprat

    sedenion = hypercomplex.cayley_dickson_algebra(4, Fraction)

    def hc(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
        return [Fraction(c) for c in (sedenion(*left) * sedenion(*right)).coefficients()]

    def hr(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
        return [Fraction(c) for c in (hyprat.Hy.from_array(left) * hyprat.Hy.from_array(right)).to_array()]

    return {"hypercomplex": hc, "hyprat": hr}


def algebra_entry(product: Any, frame: list[dict[str, Any]]) -> dict[str, Any]:
    x = x_coefficients()
    columns = [product(x, unit_vector(q)) for q in range(bdsc.DIM)]
    lint = [[columns[c][r] for c in range(bdsc.DIM)] for r in range(bdsc.DIM)]
    effect = [[x / 4 for x in row] for row in cert.fmul(cert.ftranspose(lint), lint)]
    kernel = {
        f["name"]: all(v == 0 for v in product(x, [Fraction(w) for w in f["w"]])) for f in frame if f["block"] == "A"
    }
    return {"E0": cert.fractions_text(effect), "kernel_annihilated": kernel}


def flint_entry(effect: list[list[Fraction]], frame: list[dict[str, Any]]) -> dict[str, Any]:
    import flint

    n = bdsc.DIM

    def mat(rows: list[list[Fraction]]) -> Any:
        return flint.fmpq_mat(
            len(rows), len(rows[0]), [flint.fmpq(v.numerator, v.denominator) for row in rows for v in row]
        )

    e = mat(effect)
    eye = mat([[Fraction(int(i == j)) for j in range(n)] for i in range(n)])
    half = mat([[Fraction(int(i == j), 2) for j in range(n)] for i in range(n)])
    w_k = mat([[Fraction(f["w"][i]) for f in frame if f["block"] == "A"] for i in range(n)])
    x = flint.fmpq_poly([0, 1])
    expected = x**4 * (x - flint.fmpq(1, 2)) ** 8 * (x - 1) ** 4
    minimal = e * (e * 2 - eye) * (e - eye)
    return {
        "rank_E0": int(e.rank()),
        "rank_E0_minus_half": int((e - half).rank()),
        "rank_E0_minus_one": int((e - eye).rank()),
        "rank_W_K": int(w_k.rank()),
        "E0_W_K_zero": all(v == 0 for v in (e * w_k).entries()),
        "minimal_polynomial_annihilates": all(v == 0 for v in minimal.entries()),
        "charpoly_matches": e.charpoly() == expected,
        "charpoly": [str(c) for c in e.charpoly().coeffs()],
    }


def sympy_entry(target: dict[str, Any]) -> dict[str, Any]:
    import sympy

    root = sympy.sqrt(2)
    u = sympy.Matrix([[sympy.Rational(a) + sympy.Rational(b) * root for a, b in row] for row in target["U24"]])
    mask = sympy.diag(*[int(m in target["selected_modes"]) for m in range(cert.MODES)])
    compression = (u.T * mask * u)[: bdsc.DIM, : bdsc.DIM].applyfunc(sympy.nsimplify)
    effect = sympy.Matrix([[sympy.Rational(v) for v in row] for row in target["E0"]])
    eigen = {str(k): int(v) for k, v in effect.eigenvals().items()}
    return {
        "unitary": (u.T * u).applyfunc(sympy.expand) == sympy.eye(cert.MODES),
        "compression_equals_E0": (compression - effect).is_zero_matrix,
        "eigenvalues": dict(sorted(eigen.items())),
    }


# --- optics --------------------------------------------------------------------------------


def native_permutations(target: dict[str, Any]) -> tuple[list[int], list[int]]:
    """PERM_in (logical index -> wire) and PERM_out (wire -> output mode) around twelve BS.H on (2j, 2j + 1)."""
    a, d = target["selected_modes"], target["complement_modes"]
    p_in = [0] * cert.MODES
    p_out = [0] * cert.MODES
    for j, (left, right, sign) in enumerate(bdsc.KERNEL_PAIRS):
        p_in[left], p_in[right] = 2 * j, 2 * j + 1
        p_out[2 * j], p_out[2 * j + 1] = (d[j], a[j]) if sign > 0 else (a[j], d[j])
    for j, label in enumerate(bdsc.MIDDLE_LABELS):
        wire = 8 + 2 * j
        p_in[label], p_in[bdsc.DIM + j] = wire, wire + 1
        p_out[wire], p_out[wire + 1] = a[4 + j], d[4 + j]
    return p_in, p_out


def householder(v: np.ndarray, wire: int) -> np.ndarray:
    """A unitary whose column `wire` is v up to a global phase."""
    e = np.zeros(cert.MODES, dtype=complex)
    e[wire] = 1
    phase = v[wire] / abs(v[wire]) if abs(v[wire]) > 0 else 1.0
    u = e - v / phase
    if np.linalg.norm(u) < 1e-15:
        return np.eye(cert.MODES, dtype=complex) * phase
    return np.asarray(phase * (np.eye(cert.MODES) - 2 * np.outer(u, u.conj()) / np.vdot(u, u)))


def native_circuit(p_in: list[int], p_out: list[int]) -> Any:
    import perceval as pcvl

    native = pcvl.Circuit(cert.MODES).add(0, pcvl.PERM(p_in))
    for wire in range(0, cert.MODES, 2):
        native.add(wire, pcvl.BS.H())
    return native.add(0, pcvl.PERM(p_out))


OpticsItem = tuple[str, np.ndarray, list[int], list[int], int, list[int]]


def _optics_setting(item: OpticsItem) -> dict[str, Any]:
    """SLOS shares of one setting: lossless, uniform NoiseModel loss, per-mode LC loss and NoiseModel g2."""
    import perceval as pcvl

    name, psi, p_in, p_out, source, selected = item
    photon = [0] * cert.MODES
    photon[source] = 1
    v = np.zeros(cert.MODES, dtype=complex)
    v[: bdsc.DIM] = psi
    prep = pcvl.Unitary(pcvl.Matrix(householder(v, source)))
    circuit = pcvl.Circuit(cert.MODES).add(0, prep).add(0, native_circuit(p_in, p_out))

    def share(processor: Any, filtered: bool) -> tuple[float, float, float]:
        processor.with_input(pcvl.BasicState(photon))
        if filtered:
            processor.min_detected_photons_filter(1)
        result = pcvl.algorithm.Sampler(processor).probs()
        dist = result["results"]
        sel = sum(float(p) for state, p in dist.items() if any(state[m] >= 1 for m in selected))
        multi = sum(float(p) for state, p in dist.items() if state.n > 1)
        return sel, multi, float(result["global_perf"])

    lc = pcvl.Processor("SLOS", circuit)
    for mode, eta in enumerate(LC_EFFICIENCY):
        if eta < 1:
            lc.add(mode, pcvl.LC(1 - eta))
    g2_noise = pcvl.NoiseModel(g2=G2, indistinguishability=INDISTINGUISHABILITY)
    sel_ideal, _, _ = share(pcvl.Processor("SLOS", circuit), False)
    sel_lossy, _, perf_lossy = share(
        pcvl.Processor("SLOS", circuit, noise=pcvl.NoiseModel(transmittance=TRANSMITTANCE)), True
    )
    sel_lc, _, perf_lc = share(lc, True)
    sel_g2, multi_g2, _ = share(pcvl.Processor("SLOS", circuit, noise=g2_noise), True)
    return {
        "setting": name,
        "selected_ideal": round(sel_ideal, 15),
        "selected_uniform_loss": round(sel_lossy, 15),
        "uniform_loss_perf": round(perf_lossy, 15),
        "selected_lc": round(sel_lc, 15),
        "lc_acceptance": round(perf_lc, 15),
        "selected_g2": round(sel_g2, 15),
        "multi_photon_g2": round(multi_g2, 15),
    }


def optics_entry(target: dict[str, Any]) -> dict[str, Any]:
    u = cert.numeric_unitary([[(Fraction(a), Fraction(b)) for a, b in row] for row in target["U24"]])
    p_in, p_out = native_permutations(target)
    native_error = float(np.max(np.abs(np.array(native_circuit(p_in, p_out).compute_unitary()) - u)))
    source = target["source_mode"]
    selected = target["selected_modes"]
    model = bdsc.acceptance(u, selected, LC_EFFICIENCY)
    states = [(s.name, bdsc.state(s)) for s in bdsc.bank()] + [(s["name"], s["state"]) for s in bdsc.pilot_settings()]
    items: list[OpticsItem] = [(name, psi, p_in, p_out, source, selected) for name, psi in states]
    rows = parallel.ordered_map(_optics_setting, items)
    for row, (_, psi) in zip(rows, states, strict=True):
        predicted = float(np.real(np.conj(psi) @ model["G"] @ psi) / np.real(np.conj(psi) @ model["D"] @ psi))
        row["selected_lc_predicted"] = round(predicted, 15)
    return {
        "native": {"perm_in": p_in, "perm_out": p_out, "beam_splitters": "BS.H on (2j, 2j + 1), j = 0..11"},
        "native_max_error": native_error,
        "source_mode": source,
        "transmittance": TRANSMITTANCE,
        "g2": G2,
        "indistinguishability": INDISTINGUISHABILITY,
        "lc_efficiency": list(LC_EFFICIENCY),
        "settings": rows,
    }


def conversion_entry() -> dict[str, Any]:
    """Zero-count frequency of Perceval's probs_to_sample_count against the binomial at one small p."""
    import perceval as pcvl
    from perceval.utils.conversion import probs_to_sample_count

    np.random.seed(CONVERSION_SEED)
    random.seed(CONVERSION_SEED)
    selected, other = pcvl.BasicState([1, 0]), pcvl.BasicState([0, 1])
    dist = pcvl.BSDistribution()
    dist[selected] = CONVERSION_P
    dist[other] = 1 - CONVERSION_P
    zeros = 0
    total = 0
    for _ in range(CONVERSION_DRAWS):
        counts = probs_to_sample_count(dist, count=CONVERSION_COUNT)
        k = int(counts[selected]) if selected in counts else 0
        zeros += k == 0
        total += k
    return {
        "p": CONVERSION_P,
        "count": CONVERSION_COUNT,
        "draws": CONVERSION_DRAWS,
        "seed": CONVERSION_SEED,
        "zero_draws": zeros,
        "selected_total": total,
    }


def source_entry() -> dict[str, Any]:
    import perceval

    base = Path(perceval.__file__).parent
    files = (
        "runtime/error_mitigation/detector_balancing.py",
        "runtime/error_mitigation/abstract_mitigation.py",
        "utils/conversion.py",
    )
    return {name: hashlib.sha256((base / name).read_bytes()).hexdigest() for name in files}


def record() -> dict[str, Any]:
    target = json.loads(TARGET.read_text(encoding="utf-8"))
    effect = cert.target_effect()
    frame = cert.integer_frame()
    products = package_products()
    return {
        "schema": SCHEMA,
        "target_sha256": target["target_sha256"],
        "versions": versions(),
        "algebra": {name: algebra_entry(product, frame) for name, product in products.items()},
        "flint": flint_entry(effect, frame),
        "sympy": sympy_entry(target),
        "optics": optics_entry(target),
        "conversion": conversion_entry(),
        "perceval_sources_sha256": source_entry(),
    }


# --- replay --------------------------------------------------------------------------------


def binomial_zero_z(entry: dict[str, Any]) -> tuple[float, float]:
    """Binomial P(k = 0) and the z score of the recorded zero frequency against it."""
    p0 = (1 - entry["p"]) ** entry["count"]
    se = math.sqrt(p0 * (1 - p0) / entry["draws"])
    return p0, (entry["zero_draws"] / entry["draws"] - p0) / se


def replay(data: dict[str, Any]) -> dict[str, Any]:
    target = json.loads(TARGET.read_text(encoding="utf-8"))
    bank = json.loads(BANK.read_text(encoding="utf-8"))
    require(data["schema"] == SCHEMA and data["target_sha256"] == target["target_sha256"], "record identity differs")
    for name, entry in data["algebra"].items():
        require(entry["E0"] == target["E0"], f"{name}: E0 differs from the target")
        require(all(entry["kernel_annihilated"].values()), f"{name}: a kernel vector survives x w")
    fl = data["flint"]
    require(
        (fl["rank_E0"], fl["rank_E0_minus_half"], fl["rank_E0_minus_one"], fl["rank_W_K"]) == (12, 8, 12, 4),
        "flint ranks differ from the spectrum {0^4, (1/2)^8, 1^4}",
    )
    require(fl["E0_W_K_zero"] and fl["minimal_polynomial_annihilates"] and fl["charpoly_matches"], "flint identities")
    sy = data["sympy"]
    require(sy["unitary"] and sy["compression_equals_E0"], "sympy identities")
    require(sy["eigenvalues"] == {"0": 4, "1": 4, "1/2": 8}, f"sympy eigenvalues {sy['eigenvalues']}")
    optics = data["optics"]
    require(optics["native_max_error"] < 1e-12, "the native circuit differs from U24")
    require(optics["source_mode"] == target["source_mode"], "source mode differs")
    u = cert.numeric_unitary([[(Fraction(a), Fraction(b)) for a, b in row] for row in target["U24"]])
    model = bdsc.acceptance(u, target["selected_modes"], optics["lc_efficiency"])
    ideal = {row["setting"]: float(Fraction(row["ideal_selected"])) for row in bank["settings"]}
    pilot = bdsc.pilot_probabilities(bdsc.ideal_effect())
    states = {s.name: bdsc.state(s) for s in bdsc.bank()} | {s["name"]: s["state"] for s in bdsc.pilot_settings()}
    require(
        sorted(r["setting"] for r in optics["settings"]) == sorted(states), "optics settings differ from bank and pilot"
    )
    worst = {"ideal": 0.0, "uniform_loss": 0.0, "lc": 0.0, "lc_acceptance": 0.0}
    multi = 0.0
    for row in optics["settings"]:
        name = row["setting"]
        psi = states[name]
        expected = ideal.get(name, pilot.get(name))
        require(expected is not None, f"{name}: no ideal")
        lc = float(np.real(np.conj(psi) @ model["G"] @ psi) / np.real(np.conj(psi) @ model["D"] @ psi))
        accept = float(np.real(np.conj(psi) @ model["D"] @ psi))
        worst["ideal"] = max(worst["ideal"], abs(row["selected_ideal"] - expected))
        worst["uniform_loss"] = max(worst["uniform_loss"], abs(row["selected_uniform_loss"] - expected))
        worst["lc"] = max(worst["lc"], abs(row["selected_lc"] - lc), abs(row["selected_lc_predicted"] - lc))
        worst["lc_acceptance"] = max(worst["lc_acceptance"], abs(row["lc_acceptance"] - accept))
        require(abs(row["uniform_loss_perf"] - optics["transmittance"]) < SHARE_TOLERANCE, f"{name}: perf")
        multi = max(multi, row["multi_photon_g2"])
    for key, value in worst.items():
        require(value < SHARE_TOLERANCE, f"Perceval {key} share deviates by {value}")
    p0, z = binomial_zero_z(data["conversion"])
    require(abs(z) >= CONVERSION_Z_MIN, f"converted counts read binomial (z = {z:.2f})")
    return {
        "settings": len(optics["settings"]),
        "worst_share_error": worst,
        "max_multi_photon_g2": multi,
        "binomial_zero": p0,
        "converted_zero": data["conversion"]["zero_draws"] / data["conversion"]["draws"],
        "conversion_z": z,
        "converted_mean": data["conversion"]["selected_total"] / data["conversion"]["draws"],
        "binomial_mean": data["conversion"]["p"] * data["conversion"]["count"],
    }


def close(a: Any, b: Any, path: str = "") -> None:
    cert.close(a, b, path)


def write(out: Path) -> None:
    require(available(), f"bdsc packages need every one of {PACKAGES}")
    data = record()
    replay(data)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {out}")


def check(out: Path) -> None:
    data = json.loads(out.read_text(encoding="utf-8"))
    summary = replay(data)
    if available():
        installed = versions()
        require(installed == data["versions"], f"installed packages {installed} differ from the record; rewrite it")
        close(record(), data, "packages")
        mode = "live re-derivation matches"
    else:
        mode = "replayed without the package stack"
    print(
        f"bdsc packages: {summary['settings']} Perceval settings within {SHARE_TOLERANCE}; converted zero frequency "
        f"{summary['converted_zero']:.4f} against binomial {summary['binomial_zero']:.4f} "
        f"(z {summary['conversion_z']:.1f}), "
        f"mean {summary['converted_mean']:.4f} against {summary['binomial_mean']:.4f}; {mode}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", type=Path)
    group.add_argument("--check", type=Path)
    args = parser.parse_args()
    if args.write:
        write(args.write)
    else:
        check(args.check)
    return 0


if __name__ == "__main__":
    sys.exit(main())
