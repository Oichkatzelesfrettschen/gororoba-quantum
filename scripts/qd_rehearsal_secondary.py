"""Secondary and exploratory analyses of the single-chip teleportation rehearsal on qpu:belenos.

docs/design/ascella-belenos-entanglement-teleportation.md, section "Secondary analyses of job-00", preregisters the
three analyses; none of them enters the verdict of qd_teleportation_rehearsal.analyze_results. A run's cases.json
names its job, and the job's Request supplies the layout, the request parts and the anchor read of every analysis.

- record_state compares the three-click samples a run returned with the samples it requested. Every iteration
  stops at its max_shots, so a chip near the anchor state returns its 900 samples per iteration and a chip in the
  state the held platform record describes returns almost none.
- in_situ_fit estimates HOM, g2 and the uniform transmittance scale T from the category mix of the returned
  three-click events (correct, wrong, and the five rejection reasons of qd_teleportation_rehearsal.classify), by
  maximum likelihood over a fixed grid of Perceval's noise model, once with the job's anchor read's t_out profile and
  once with the profile of the run's platform-before read.
- cd_lens is exploratory. It maps each event whose clicks lie on the eight logical modes to the basis element e_i
  of a Cayley-Dickson algebra, i the click pattern with logical mode b on bit b, and asks whether the Cayley-Dickson
  sign table (cd_core.cd_sign, checked against cd_core.cd_multiply on every basis pair) separates the run from the
  noise model more than sign tables of the same support and commutation (an identity, units squaring to -1,
  distinct units anticommuting) that form no algebra.

Usage:
  "$PYTHON" scripts/qd_rehearsal_secondary.py RUN [--check]
"""

from __future__ import annotations

import itertools
import json
import math
import sys
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import qd_teleportation_rehearsal as rehearsal  # noqa: E402
from bdsc_certificate import close  # noqa: E402
from qd_network_protocol import ProtocolError, decode_bit  # noqa: E402
from qd_platform import write_json  # noqa: E402

import cd_core  # noqa: E402
from parallel import ordered_map  # noqa: E402

OUTPUT = "secondary-analysis.json"
CATEGORIES = ("correct", "wrong", *rehearsal.REJECTIONS)
# record_state classes: the returned share of the requested samples at or above NEAR_ANCHOR, at or below DEGRADED.
NEAR_ANCHOR = 0.5
DEGRADED = 0.01
HOM_GRID = tuple(round(0.70 + 0.02 * k, 2) for k in range(15))
G2_GRID = tuple(round(0.02 * k, 2) for k in range(13))
T_GRID = tuple(10.0 ** (-4.0 + 0.25 * k) for k in range(13))
# Half the 95 % chi-square quantile of one degree of freedom: the profile-likelihood interval of each parameter.
PROFILE_DROP = 1.92
FIT_MIN_SAMPLES = 100
CD_DIMENSIONS = (64, 128, 256)
CONTROLS = 999
# Index 0 of the ANU QRNG draw docs/evidence/anu_qrng/draw-2026-10-26T014202Z.json, registered in
# docs/evidence/qrng_seeds/allocations.json: the generator of every control sign table, drawn before any map.
CONTROL_SEED = 64095
CD_FLAG = 0.01
CONTROL_CHUNK = 37


# ---------------------------------------------------------------- record state


def record_state(manifest: Mapping[str, Any], results: Mapping[str, Any]) -> dict[str, Any]:
    """The returned share of the requested three-click samples and its preregistered class."""
    requested = manifest["max_samples"]
    entries = results.get("iterations") or []
    returned = sum(entry["samples"] for entry in entries if "counts" in entry)
    share = returned / requested
    state = "near-anchor" if share >= NEAR_ANCHOR else "degraded-as-recorded" if share <= DEGRADED else "intermediate"
    return {
        "requested_samples": requested,
        "returned_samples": returned,
        "returned_share": share,
        "counted_iterations": sum(1 for entry in entries if "counts" in entry),
        "partial": results.get("partial") is True,
        "state": state,
        "rule": f"near-anchor at a share >= {NEAR_ANCHOR}, degraded-as-recorded at <= {DEGRADED}, else intermediate",
    }


# ---------------------------------------------------------------- in-situ fit


def category(label: str, basis: str, clicks: Sequence[int], layout: Sequence[int]) -> str | None:
    """The fit category of a click vector of input `label` under the case's layout, or None below three clicks."""
    outcome, pattern, raw = rehearsal.classify(clicks, layout)
    if outcome == "below":
        return None
    if outcome != "accepted" or pattern is None or raw is None:
        return outcome
    x, z = rehearsal.frames()[pattern]
    return "correct" if decode_bit(basis, raw, x, z) == rehearsal.expected_bit(label) else "wrong"


def category_probabilities(
    item: tuple[dict[str, Any], dict[str, Any], float, float, list[list[float]], list[float], tuple[int, ...]],
) -> list[list[list[float]]]:
    """[profile][T][category] probabilities of one setting at (HOM, g2), conditioned on three clicks or more."""
    setting, circuit, hom, g2, profiles, scales, layout = item
    photons = rehearsal.photon_distribution(setting, circuit, hom, g2)
    out: list[list[list[float]]] = []
    for t_out in profiles:
        rows: list[list[float]] = []
        for scale in scales:
            mass = dict.fromkeys(CATEGORIES, 0.0)
            clicks = rehearsal.detected_clicks(photons, rehearsal.detection_efficiency(t_out, scale))
            for vector, probability in clicks.items():
                name = category(setting["label"], setting["basis"], vector, layout)
                if name is not None:
                    mass[name] += probability
            total = sum(mass.values())
            rows.append([mass[name] / total if total > 0.0 else 0.0 for name in CATEGORIES])
        out.append(rows)
    return out


def category_table(
    settings: Sequence[dict[str, Any]],
    circuit: dict[str, Any],
    profiles: Sequence[Sequence[float]],
    homs: Sequence[float] = HOM_GRID,
    g2s: Sequence[float] = G2_GRID,
    scales: Sequence[float] = T_GRID,
    *,
    layout: Sequence[int],
) -> np.ndarray:
    """Model category probabilities indexed [input, HOM, g2, profile, T, category]; one process per grid cell."""
    items = [
        (dict(setting), dict(circuit), hom, g2, [list(p) for p in profiles], list(scales), tuple(layout))
        for setting in settings
        for hom in homs
        for g2 in g2s
    ]
    cells = ordered_map(category_probabilities, items, min_items=1)
    shape = (len(settings), len(homs), len(g2s), len(profiles), len(scales), len(CATEGORIES))
    return np.asarray(cells, dtype=np.float64).reshape(shape)


def observed_categories(manifest: Mapping[str, Any], results: Mapping[str, Any]) -> np.ndarray:
    """Counts indexed [input, category] in manifest order; an uncounted iteration leaves its input's row zero."""
    settings = manifest["settings"]
    layout = tuple(manifest["layout"]["chip_modes"])
    counts = np.zeros((len(settings), len(CATEGORIES)), dtype=np.int64)
    for entry in results.get("iterations") or []:
        if "counts" not in entry:
            continue
        index = rehearsal.bound_setting(settings, entry)
        setting = settings[index]
        for key, count in entry["counts"].items():
            name = category(setting["label"], setting["basis"], rehearsal.event_vector(key), layout)
            if name is None:
                raise ProtocolError(f"event {key} carries fewer than {rehearsal.MIN_CLICKS} clicks")
            counts[index, CATEGORIES.index(name)] += count
    return counts


def pooled_fidelity(probabilities: np.ndarray) -> float | None:
    """Pooled conditional fidelity sum(correct) / sum(correct + wrong) over inputs of a [input, category] array."""
    correct = float(probabilities[:, CATEGORIES.index("correct")].sum())
    accepted = correct + float(probabilities[:, CATEGORIES.index("wrong")].sum())
    return correct / accepted if accepted > 0.0 else None


def fit_from_table(
    counts: np.ndarray,
    table: np.ndarray,
    homs: Sequence[float] = HOM_GRID,
    g2s: Sequence[float] = G2_GRID,
    scales: Sequence[float] = T_GRID,
) -> dict[str, Any]:
    """Grid maximum likelihood of [input, category] counts under a [input, HOM, g2, T, category] model table.

    A cell whose model assigns zero probability to an observed category has log-likelihood minus infinity. Each
    parameter's interval spans the grid values whose profile log-likelihood lies within PROFILE_DROP of the
    maximum. The deviance compares the best cell with the saturated multinomial of each input, and the model's
    pooled fidelity pools the best cell's expected counts, so it weights each input by its observed samples."""
    rows = counts.sum(axis=1) > 0
    n = counts[rows].astype(np.float64)
    q = table[rows]
    with np.errstate(divide="ignore", invalid="ignore"):
        terms = np.where(n[:, None, None, None, :] > 0, n[:, None, None, None, :] * np.log(q), 0.0)
    log_likelihood = terms.sum(axis=(0, 4))
    best = np.unravel_index(int(np.argmax(log_likelihood)), log_likelihood.shape)
    peak = float(log_likelihood[best])
    if not math.isfinite(peak):
        return {"status": "no grid cell assigns the observed categories positive probability"}
    names = (("hom", homs, (1, 2)), ("g2", g2s, (0, 2)), ("transmittance", scales, (0, 1)))
    estimate: dict[str, Any] = {}
    for position, (name, grid, others) in enumerate(names):
        profile = log_likelihood.max(axis=others)
        inside = [grid[k] for k in range(len(grid)) if profile[k] >= peak - PROFILE_DROP]
        estimate[name] = {
            "estimate": grid[int(best[position])],
            "interval": [min(inside), max(inside)],
            "at_grid_edge": best[position] in (0, len(grid) - 1),
        }
    expected = n.sum(axis=1, keepdims=True) * q[:, best[0], best[1], best[2], :]
    with np.errstate(divide="ignore", invalid="ignore"):
        deviance = 2.0 * float(np.where(n > 0, n * np.log(n / expected), 0.0).sum())
    return {
        "status": "fitted",
        "parameters": estimate,
        "log_likelihood": peak,
        "deviance": deviance,
        "degrees_of_freedom": int(n.shape[0] * (len(CATEGORIES) - 1) - 3),
        "model_pooled_fidelity": pooled_fidelity(expected),
        "observed_pooled_fidelity": pooled_fidelity(n),
    }


def profile_of(catalogue_path: Path) -> list[float]:
    catalogue = json.loads(catalogue_path.read_text(encoding="utf-8"))
    return rehearsal.read_perfs(catalogue)[0]


def in_situ_fit(manifest: Mapping[str, Any], results: Mapping[str, Any], run: Path) -> dict[str, Any]:
    """The grid fit under the job's anchor t_out profile (primary) and the run's platform-before profile."""
    request = rehearsal.JOBS[manifest["job"]].request
    counts = observed_categories(manifest, results)
    total = int(counts.sum())
    record: dict[str, Any] = {
        "categories": list(CATEGORIES),
        "counts": counts.tolist(),
        "grid": {"hom": list(HOM_GRID), "g2": list(G2_GRID), "transmittance": list(T_GRID)},
    }
    if total < FIT_MIN_SAMPLES:
        record["status"] = f"{total} three-click samples, below the {FIT_MIN_SAMPLES} the fit needs"
        return record
    profiles = {"anchor": profile_of(ROOT / request.anchor_read)}
    before = run / rehearsal.BEFORE / "catalogue.json"
    if before.is_file():
        profiles["platform_before"] = profile_of(before)
    else:
        record["platform_before"] = (
            f"{rehearsal.BEFORE}/catalogue.json is absent (a --simulate run); anchor profile only"
        )
    settings, circuit = rehearsal.request_parts(request)
    table = category_table(settings, circuit, list(profiles.values()), layout=request.layout)
    record["status"] = "fitted"
    record["fits"] = {name: fit_from_table(counts, table[:, :, :, k]) for k, name in enumerate(profiles)}
    return record


# ---------------------------------------------------------------- exploratory Cayley-Dickson lens


def basis_index(clicks: Sequence[int], dim: int, layout: Sequence[int]) -> int | None:
    """e_i of a click vector: logical mode b on bit b of i; None for a click off the logical modes or above dim."""
    flags = [1 if count else 0 for count in clicks]
    if sum(flags[mode] for mode in layout) != sum(flags):
        return None
    index = sum(flags[mode] << bit for bit, mode in enumerate(layout))
    return index if index < dim else None


def lens_vectors(
    distributions: Sequence[Mapping[tuple[int, ...], float]], dim: int, layout: Sequence[int]
) -> np.ndarray | None:
    """[input, dim] normalized vectors of the events that map into dim, or None when an input has none."""
    out = np.zeros((len(distributions), dim), dtype=np.float64)
    for k, distribution in enumerate(distributions):
        for vector, weight in distribution.items():
            index = basis_index(vector, dim, layout)
            if index is not None:
                out[k, index] += weight
        total = out[k].sum()
        if total <= 0.0:
            return None
        out[k] /= total
    return out


def sign_row(item: tuple[int, int]) -> list[int]:
    """Row i of the Cayley-Dickson sign table, each entry required to match cd_core.cd_multiply on basis pairs."""
    dim, i = item
    left = cd_core.basis(dim, i)
    row = []
    for j in range(dim):
        sign = cd_core.cd_sign(dim, i, j)
        product = cd_core.cd_multiply(dim, left, cd_core.basis(dim, j))
        target = i ^ j
        if any((value != 0.0) != (k == target) for k, value in enumerate(product)) or product[target] != sign:
            raise ProtocolError(f"cd_sign({dim}, {i}, {j}) = {sign} departs from cd_multiply")
        row.append(sign)
    return row


def cd_signs(dim: int) -> np.ndarray:
    """The declared map onto cd_core: e_i e_j = cd_sign(dim, i, j) e_(i xor j), checked on every basis pair."""
    return np.asarray(ordered_map(sign_row, [(dim, i) for i in range(dim)], min_items=1), dtype=np.int8)


def control_tables(seed: int, dims: Sequence[int], count: int) -> dict[int, np.ndarray]:
    """Sign tables with the Cayley-Dickson support and commutation that form no algebra.

    e_0 is the identity, every other e_i squares to -1 and distinct imaginary units anticommute, as in every
    Cayley-Dickson algebra; each sign above the diagonal among the imaginary units is independent, drawn from one
    generator in dimension order, and its transpose takes the opposite sign."""
    generator = np.random.default_rng(seed)
    tables: dict[int, np.ndarray] = {}
    for dim in dims:
        upper = np.triu_indices(dim - 1, k=1)
        draws = generator.integers(0, 2, size=(count, len(upper[0])), dtype=np.int8) * 2 - 1
        signs = np.ones((count, dim, dim), dtype=np.int8)
        rows, cols = upper[0] + 1, upper[1] + 1
        signs[:, rows, cols] = draws
        signs[:, cols, rows] = -draws
        diagonal = np.arange(1, dim)
        signs[:, diagonal, diagonal] = -1
        tables[dim] = signs
    return tables


def product(u: np.ndarray, v: np.ndarray, signs: np.ndarray, xor: np.ndarray) -> np.ndarray:
    """u * v under the sign table: (u * v)_(i xor j) collects signs[i, j] u_i v_j."""
    return np.bincount(xor.ravel(), weights=(np.outer(u, v) * signs).ravel(), minlength=len(u))


def separation(item: tuple[np.ndarray, np.ndarray, np.ndarray]) -> list[float]:
    """For each table of a chunk: the sum over input pairs a < b of |x_a * x_b - y_a * y_b|."""
    tables, x, y = item
    dim = x.shape[1]
    xor = np.bitwise_xor.outer(np.arange(dim), np.arange(dim))
    pairs = list(itertools.combinations(range(x.shape[0]), 2))
    out = []
    for signs in tables:
        out.append(
            float(
                sum(np.linalg.norm(product(x[a], x[b], signs, xor) - product(y[a], y[b], signs, xor)) for a, b in pairs)
            )
        )
    return out


def lens_dimension(dim: int, x: np.ndarray, y: np.ndarray, controls: np.ndarray) -> dict[str, Any]:
    """The Cayley-Dickson separation, the controls' separations and the percentile rank of the former."""
    algebra = separation((cd_signs(dim)[None, :, :], x, y))[0]
    chunks = [(controls[k : k + CONTROL_CHUNK], x, y) for k in range(0, len(controls), CONTROL_CHUNK)]
    values = [value for chunk in ordered_map(separation, chunks, min_items=1) for value in chunk]
    exceed = sum(1 for value in values if value >= algebra)
    return {
        "cayley_dickson": algebra,
        "control_median": float(np.median(values)),
        "control_quantiles": [float(np.quantile(values, q)) for q in (0.01, 0.5, 0.99)],
        "percentile": (1 + exceed) / (len(values) + 1),
    }


def model_distribution(
    item: tuple[dict[str, Any], dict[str, Any], rehearsal.Variant],
) -> dict[tuple[int, ...], float]:
    """One setting's click distribution under a noise variant, conditioned on three clicks or more."""
    setting, circuit, variant = item
    photons = rehearsal.photon_distribution(setting, circuit, variant.hom, variant.g2)
    clicks = rehearsal.detected_clicks(photons, variant.transmission)
    return {vector: p for vector, p in clicks.items() if sum(vector) >= rehearsal.MIN_CLICKS}


def model_distributions(request: rehearsal.Request) -> list[dict[tuple[int, ...], float]]:
    """The anchor noise variant's distribution of each setting in manifest order, one process per setting."""
    settings, circuit = rehearsal.request_parts(request)
    variant = next(v for v in rehearsal.variants(request) if v.name == "anchor per-mode transmission")
    return ordered_map(model_distribution, [(dict(s), dict(circuit), variant) for s in settings], min_items=1)


def observed_distributions(
    manifest: Mapping[str, Any], results: Mapping[str, Any]
) -> list[dict[tuple[int, ...], float]]:
    settings = manifest["settings"]
    out: list[dict[tuple[int, ...], float]] = [{} for _ in settings]
    for entry in results.get("iterations") or []:
        if "counts" not in entry:
            continue
        index = rehearsal.bound_setting(settings, entry)
        for key, count in entry["counts"].items():
            vector = rehearsal.event_vector(key)
            out[index][vector] = out[index].get(vector, 0.0) + float(count)
    return out


def cd_lens(
    observed: Sequence[Mapping[tuple[int, ...], float]],
    model: Callable[[], Sequence[Mapping[tuple[int, ...], float]]],
    layout: Sequence[int],
    seed: int = CONTROL_SEED,
    count: int = CONTROLS,
    dims: Sequence[int] = CD_DIMENSIONS,
) -> dict[str, Any]:
    """The exploratory lens over every dimension; the controls are drawn before any map, and `model` runs only
    when some dimension holds an event of every input."""
    tables = control_tables(seed, dims, count)
    reference: Sequence[Mapping[tuple[int, ...], float]] | None = None
    record: dict[str, Any] = {
        "label": "exploratory; outside the verdict and the evidence registry",
        "seed": seed,
        "controls": count,
        "dimensions": {},
    }
    available = []
    for dim in dims:
        x = lens_vectors(observed, dim, layout)
        if x is not None and reference is None:
            reference = model()
        y = None if x is None or reference is None else lens_vectors(reference, dim, layout)
        if x is None or y is None:
            record["dimensions"][str(dim)] = {"status": "an input has no event inside this dimension"}
            continue
        record["dimensions"][str(dim)] = {"status": "computed", **lens_dimension(dim, x, y, tables[dim])}
        available.append(record["dimensions"][str(dim)]["percentile"])
    flagged = bool(available) and len(available) == len(dims) and all(p <= CD_FLAG for p in available)
    record["flag"] = "algebra-specific separation" if flagged else "no algebra-specific separation"
    record["rule"] = f"flag when the percentile is at or below {CD_FLAG} in every dimension"
    return record


# ---------------------------------------------------------------- command


def analyze(run: Path, replay: bool = False) -> int:
    """Write RUN/secondary-analysis.json once, or with `replay` require the retained one to equal a fresh run of the
    three analyses within bdsc_certificate.close's tolerance."""
    manifest = json.loads((run / "cases.json").read_text(encoding="utf-8"))
    results = json.loads((run / "results.json").read_text(encoding="utf-8"))
    request = rehearsal.JOBS[manifest["job"]].request
    record: dict[str, Any] = {
        "schema": "qd-teleportation-secondary-v1",
        "design": rehearsal.DESIGN,
        "record_state": record_state(manifest, results),
        "in_situ_fit": in_situ_fit(manifest, results, run),
        "cd_lens": cd_lens(
            observed_distributions(manifest, results), lambda: model_distributions(request), request.layout
        ),
    }
    if replay:
        retained = json.loads((run / OUTPUT).read_text(encoding="utf-8"))
        close(json.loads(json.dumps(record)), retained, f"{run.name}/{OUTPUT}")
        print(f"{run.name}: {OUTPUT} replays")
        return 0
    write_json(run / OUTPUT, record, exclusive=True)
    state = record["record_state"]
    print(
        f"{run.name}: {state['returned_samples']} of {state['requested_samples']} samples ({state['state']}); "
        f"fit {record['in_situ_fit']['status']}; Cayley-Dickson lens: {record['cd_lens']['flag']}"
    )
    return 0


def main(argv: list[str]) -> int:
    if len(argv) in (1, 2) and argv[1:] in ([], ["--check"]):
        return analyze(Path(argv[0]), argv[1:] == ["--check"])
    raise ValueError(f"usage: qd_rehearsal_secondary.py RUN [--check], not {argv}")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
