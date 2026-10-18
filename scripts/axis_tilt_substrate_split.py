"""Solve and resimulation shares of the axis_tilt_plus_mean contrast moves between two BLAS substrates.

atlas_coherent_families.lane_fit builds each lane's design from simulated
fringe responses, solves every leave-one-edge-out fold by np.linalg.lstsq,
and resimulates the held-out edge at the fold solution
(atlas_coherent_families.Resimulate); the resulting predicted_log_ratio
vector is what core-329 compares, normwise, against the retained record
within max(CHECK_TOLERANCE, eps kappa_fold^2 max|vector|). Two substrates,
S and T, change both stages: the design and offsets the solve reads, and the
statevector arithmetic of the resimulation.

``--capture OUT`` runs on one interpreter. For lane 4 of each backend it
captures the fit_models arguments (lsq_conditioning_study.capture_lane),
keeps every family's fitted slope block and the measured offsets, solves
each fold of axis_tilt_plus_mean, and resimulates the held-out edge at that
solution (cell ``own``). With ``--other CAPTURE``, the capture of the other
substrate, it also resimulates on this substrate:

- ``other_solution``: the other substrate's fold solution;
- ``other_problem``: this substrate's lstsq of the other substrate's fold
  design and offsets;
- ``other_design``: this substrate's lstsq of the other substrate's fold
  design with this substrate's offsets.

``--combine A B --out RECORD`` joins two captures made with ``--other``
pointing at each other, requires each to name the other's own solutions bit
for bit, and writes the record: both substrates' identities, designs,
offsets, solutions and resimulated log ratios (the witness) and the summary
recomputed from them. With S the base substrate and T the other, per fold:

- full move: own_T - own_S;
- solve share: other_solution_S - own_S (T's solution, S's resimulation);
- problem share: other_problem_S - own_S (T's design and offsets, S's lstsq);
- design share: other_design_S - own_S (T's slope block alone);
- resimulation share: other_solution_T - own_S (S's solution, T's
  resimulation);
- interaction: full - solve - resimulation.

The summary reads each share as a fraction of core-329's contrast tolerance,
the core-329 margin of each substrate's own vector against the retained
atlas record, the relative 2-norm design differences of the slope block per
fold and over every identified lane-4 model, and the random-direction move
lsq_conditioning_study retains at its worst perturbation scaled linearly to
the measured slope-block difference of the same fold.

``--check RECORD`` binds the atlas record by sha256, requires every retained
slope block and offset vector to round to the atlas lane's nine-decimal
slopes and six-decimal offsets, requires each retained own solution to equal
this host's lstsq of its retained fold problem within the backward-stable
forward-error bound m n eps (kappa + kappa^2 rho) normwise, requires the
scaled-move inputs to equal the lsq_conditioning record's resimulation
summary, and recomputes the summary from the witness. Shares, margins and
fractions follow from retained floats by exact subtraction and division, so
they compare exactly; 2-norm design differences compare within
CONDITION_RELATIVE. ``--self-test`` requires --check to reject corrupted
records. docs/evidence/lsq_conditioning/README.md states the prediction and
its falsifier.
"""

from __future__ import annotations

import argparse
import copy
import json
import platform
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import atlas_coherent_families as acf  # noqa: E402
import lsq_conditioning_study as lsq  # noqa: E402
import numpy as np  # noqa: E402
import scipy  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "axis-tilt-substrate-split-v1"
CAPTURE_SCHEMA = "axis-tilt-substrate-capture-v1"
SOURCE = lsq.SOURCE
STUDY = ROOT / "docs/evidence/lsq_conditioning/result.json"
MODEL = lsq.RESIMULATED_MODEL
LANE = lsq.BRIDGE_LANE
BACKENDS = tuple(lsq.MOVED)
CELLS = ("own", "other_solution", "other_problem", "other_design")
EPS = lsq.EPS
DIGITS = 4
# Fields computed through a 2-norm (an SVD) keep nine digits and compare
# within CONDITION_RELATIVE, the relative roundoff an SVD carries across
# LAPACK builds; every other summary field follows from retained floats by
# subtraction and division and compares exactly.
NORM_DIGITS = lsq.CONDITION_DIGITS
NORM_KEYS = frozenset(
    {
        "slope_block_fold_difference",
        "slope_block_full_difference",
        "family_block_difference",
        "all_models_difference_max",
        "all_models_difference_median",
        "study_move_scaled_to_measured",
        "design_share_over_scaled",
    }
)
require = lsq.require
sig = lsq.sig


def environment() -> dict[str, Any]:
    """Interpreter, numpy, scipy, qiskit and BLAS identity, with mapped BLAS and LAPACK libraries by basename."""
    import qiskit

    config = np.show_config(mode="dicts")["Build Dependencies"]
    libraries: list[str] = []
    try:
        maps = Path("/proc/self/maps").read_text(encoding="utf-8").splitlines()
        names = {Path(line.split()[-1]).name for line in maps if "/" in line}
        libraries = sorted(n for n in names if any(k in n.lower() for k in ("blas", "lapack", "flame", "blis")))
    except OSError:
        pass
    return {
        "python": platform.python_version(),
        "machine": platform.machine(),
        "processor": cpu_model(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "qiskit": qiskit.__version__,
        "blas": {k: config["blas"].get(k) for k in ("name", "version", "openblas configuration")},
        "lapack": {k: config["lapack"].get(k) for k in ("name", "version")},
        "mapped_libraries": libraries,
    }


def cpu_model() -> str | None:
    try:
        for line in Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines():
            if line.startswith("model name"):
                return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return None


def model_design(blocks: dict[str, Any], offsets: Sequence[float], name: str) -> np.ndarray:
    families, constant = acf.MODELS[name]
    n = len(offsets)
    parts = [np.array(blocks[f], dtype=float).reshape(n, -1) for f in families]
    return np.hstack(parts + ([np.ones((n, 1))] if constant else []))


class FoldLstsq:
    """np.linalg.lstsq of one fold problem."""

    def __call__(self, item: tuple[np.ndarray, np.ndarray]) -> list[float]:
        design, data = item
        return [float(v) for v in np.linalg.lstsq(design, data, rcond=None)[0]]


def fold_problems(design: np.ndarray, data: np.ndarray) -> list[tuple[np.ndarray, np.ndarray]]:
    n = len(data)
    return [(design[[k for k in range(n) if k != h]], data[[k for k in range(n) if k != h]]) for h in range(n)]


def capture(other: dict[str, Any] | None) -> dict[str, Any]:
    """This substrate's lane-4 capture and resimulated cells, against the other substrate's capture when given."""
    out: dict[str, Any] = {"schema": CAPTURE_SCHEMA, "environment": environment(), "backends": {}}
    for backend in BACKENDS:
        captured = lsq.capture_lane(backend, LANE)
        offsets = np.asarray(captured["measured"]["offset"], dtype=float)
        blocks = {f: captured["responses"][f]["fitted"].tolist() for f in acf.SINGLE}
        design = model_design(blocks, offsets.tolist(), MODEL)
        problems = {"own": fold_problems(design, offsets)}
        if other is not None:
            theirs = other["backends"][backend]
            their_design = model_design(theirs["blocks"], theirs["offsets"], MODEL)
            their_offsets = np.array(theirs["offsets"], dtype=float)
            problems["other_problem"] = fold_problems(their_design, their_offsets)
            problems["other_design"] = fold_problems(their_design, offsets)
        labels = [(cell, h) for cell in problems for h in range(len(offsets))]
        solved = parallel.ordered_map(FoldLstsq(), [problems[cell][h] for cell, h in labels])
        solutions: dict[str, list[list[float]]] = {cell: [] for cell in problems}
        for (cell, _), solution in zip(labels, solved, strict=True):
            solutions[cell].append(solution)
        if other is not None:
            solutions["other_solution"] = other["backends"][backend]["solutions"]["own"]
        families, _ = acf.MODELS[MODEL]
        columns = [c for f in families for c in captured["fitted_columns"][f]]
        order = [cell for cell in CELLS if cell in solutions]
        items = []
        for cell in order:
            for h, values in enumerate(solutions[cell]):
                base = captured["bases"][h]
                errors = acf.errors_of(columns, np.array(values[: len(columns)]))
                items.append((captured["prepared"][h], errors, base["contrast"], base["phase"]))
        simulated = parallel.ordered_map(acf.Resimulate(), items, min_items=2)
        n = len(offsets)
        ratios = {cell: [float(r) for _, r in simulated[k * n : (k + 1) * n]] for k, cell in enumerate(order)}
        out["backends"][backend] = {
            "blocks": blocks,
            "offsets": offsets.tolist(),
            "solutions": {cell: solutions[cell] for cell in order if cell != "other_solution"},
            "log_ratios": ratios,
        }
        if other is not None:
            out["backends"][backend]["other_own_sha256"] = solutions_digest(solutions["other_solution"])
    return out


def solutions_digest(solutions: list[list[float]]) -> str:
    """sha256 of fold solutions as JSON, whose float repr round-trips every float64."""
    return lsq.sha256_bytes(json.dumps(solutions).encode())


def relative_difference(a: np.ndarray, b: np.ndarray) -> float:
    """||b - a||_2 / ||a||_2."""
    return float(np.linalg.norm(b - a, 2) / np.linalg.norm(a, 2))


def shares(base: dict[str, Any], other: dict[str, Any]) -> dict[str, list[float]]:
    """Per-fold contrast moves from the base substrate's own resimulation (module docstring)."""
    mine, theirs = base["log_ratios"], other["log_ratios"]
    own = mine["own"]
    full = [b - a for a, b in zip(own, theirs["own"], strict=True)]
    solve = [b - a for a, b in zip(own, mine["other_solution"], strict=True)]
    resim = [b - a for a, b in zip(own, theirs["other_solution"], strict=True)]
    return {
        "full": full,
        "solve": solve,
        "problem": [b - a for a, b in zip(own, mine["other_problem"], strict=True)],
        "design": [b - a for a, b in zip(own, mine["other_design"], strict=True)],
        "resimulation": resim,
        "interaction": [f - v - r for f, v, r in zip(full, solve, resim, strict=True)],
    }


def margin(vector: Sequence[float], retained: Sequence[float], tolerance: float) -> float | None:
    """core-329's normwise contrast margin: tolerance over the largest difference from the retained vector.

    fit_models writes each prediction rounded to six decimals, and compare()
    reads that rounded value; None marks a vector that reproduces exactly.
    """
    worst = max(abs(round(v, 6) - r) for v, r in zip(vector, retained, strict=True))
    return sig(tolerance / worst, DIGITS) if worst else None


def summary(substrates: list[dict[str, Any]], source: dict[str, Any], study_moves: dict[str, Any]) -> dict[str, Any]:
    """Shares, tolerance fractions, core-329 margins and design differences from the two substrates' witnesses."""
    lanes = {(lane["backend"], lane["lane"]): lane for lane in source["lanes"]}
    out: dict[str, Any] = {}
    for backend in BACKENDS:
        lane = lanes[backend, LANE]
        model = lane["models"][MODEL]
        retained = [float(v) for v in model["contrast"]["predicted_log_ratio"]]
        tolerance = max(acf.CHECK_TOLERANCE, EPS * float(model["fold_condition_max"]) ** 2 * max(map(abs, retained)))
        s, t = (sub["backends"][backend] for sub in substrates)
        n = len(retained)
        width = lsq.mutable_columns(MODEL, model_design(s["blocks"], s["offsets"], MODEL).shape[1])
        designs = [model_design(sub["blocks"], sub["offsets"], MODEL) for sub in (s, t)]
        folds = [fold_problems(d, np.array(sub["offsets"])) for d, sub in zip(designs, (s, t), strict=True)]
        slope_fold = [relative_difference(folds[0][h][0][:, :width], folds[1][h][0][:, :width]) for h in range(n)]
        all_models: list[tuple[float, str]] = []
        for name, entry in lane["models"].items():
            if "unidentified" in entry or not acf.MODELS[name][0]:
                continue
            a, b = (model_design(sub["blocks"], sub["offsets"], name) for sub in (s, t))
            all_models.append((relative_difference(a, b), f"{name} full"))
            for h in range(n):
                keep = [k for k in range(n) if k != h]
                all_models.append((relative_difference(a[keep], b[keep]), f"{name} fold {h}"))
        family_difference = {
            f: sig(relative_difference(np.array(s["blocks"][f]), np.array(t["blocks"][f])), NORM_DIGITS)
            for f in acf.SINGLE
            if np.size(s["blocks"][f])
        }

        moved = lsq.MOVED[backend]
        study = study_moves[backend]
        per_unit = [m / lsq.PERTURBATION for m in study["moves"]]
        bases = {}
        for label, (base, other) in (("s", (s, t)), ("t", (t, s))):
            split = shares(base, other)
            bases[label] = {
                "moves": {k: [sig(v, DIGITS) for v in vs] for k, vs in split.items()},
                "max_over_tolerance": {k: sig(max(map(abs, vs)) / tolerance, DIGITS) for k, vs in split.items()},
                "moved_prediction_over_tolerance": {
                    k: sig(abs(vs[moved]) / tolerance, DIGITS) for k, vs in split.items()
                },
            }
        design_moved = abs(shares(s, t)["design"][moved])
        scaled = per_unit[moved] * slope_fold[moved]
        out[backend] = {
            "moved_prediction": moved,
            "contrast_tolerance": sig(tolerance, 9),
            "retained": retained,
            "core329_margin": {
                "s": margin(s["log_ratios"]["own"], retained, tolerance),
                "t": margin(t["log_ratios"]["own"], retained, tolerance),
            },
            "slope_block_fold_difference": [sig(v, NORM_DIGITS) for v in slope_fold],
            "slope_block_full_difference": sig(
                relative_difference(designs[0][:, :width], designs[1][:, :width]), NORM_DIGITS
            ),
            "offsets_max_difference": sig(
                max(abs(a - b) for a, b in zip(s["offsets"], t["offsets"], strict=True)), DIGITS
            ),
            "family_block_difference": family_difference,
            "all_models_difference_max": sig(max(all_models)[0], NORM_DIGITS),
            "all_models_difference_argmax": max(all_models)[1],
            "all_models_difference_median": sig(float(np.median([v for v, _ in all_models])), NORM_DIGITS),
            "study_move_at_perturbation": study["moves"][moved],
            "study_move_scaled_to_measured": sig(scaled, NORM_DIGITS),
            "design_share_over_scaled": sig(design_moved / scaled, NORM_DIGITS) if scaled else None,
            "base_s": bases["s"],
            "base_t": bases["t"],
        }
    return out


def study_inputs() -> dict[str, Any]:
    """The lsq_conditioning record's per-fold moves at its worst perturbation, per backend."""
    record = json.loads(STUDY.read_text(encoding="utf-8"))
    require(float(record["constants"]["perturbation"]) == lsq.PERTURBATION, f"{STUDY}: perturbation differs")
    return {b: {"moves": record["resimulation"][b]["summary"]["moves"]} for b in BACKENDS}


def combine(s: dict[str, Any], t: dict[str, Any]) -> dict[str, Any]:
    for capture_record, label in ((s, "first"), (t, "second")):
        require(
            capture_record.get("schema") == CAPTURE_SCHEMA, f"{label} capture schema {capture_record.get('schema')}"
        )
        for backend in BACKENDS:
            cells = set(capture_record["backends"][backend]["log_ratios"])
            require(cells == set(CELLS), f"{label} capture {backend} lacks a cell; capture with --other")
    witness = [{"environment": sub["environment"], "backends": sub["backends"]} for sub in (s, t)]
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    study = study_inputs()
    check_witness(witness, source)
    return {
        "schema": SCHEMA,
        "source": {"path": SOURCE.relative_to(ROOT).as_posix(), "sha256": lsq.sha256_bytes(SOURCE.read_bytes())},
        "study_inputs": study,
        "substrates": witness,
        "summary": summary(witness, source, study),
    }


def substrate_kind(environment: dict[str, Any]) -> str | None:
    """The BLAS build a capture ran on, read from the libraries its process mapped."""
    mapped = [name.lower() for name in environment.get("mapped_libraries", [])]
    if any(name.startswith(("libblis", "libflame")) for name in mapped):
        return "aocl"
    if any("openblas" in name for name in mapped) and "openblas" in str(environment["blas"].get("name")):
        return "openblas"
    return None


def fold_solution_error(
    problem: tuple[np.ndarray, np.ndarray], retained: Sequence[float], fresh: Any
) -> tuple[float, float]:
    """A retained and a fresh lstsq of one fold: their relative gap and the bound m n eps (kappa + kappa^2 rho)."""
    a, b = problem
    singular = np.linalg.svd(a, compute_uv=False)
    kappa = float(singular[0] / singular[-1])
    xs = np.array(retained, dtype=float)
    rho = float(np.linalg.norm(b - a @ xs) / (singular[0] * np.linalg.norm(xs)))
    m, p = a.shape
    bound = m * p * EPS * (kappa + kappa * kappa * rho)
    return float(np.linalg.norm(np.array(fresh) - xs) / np.linalg.norm(xs)), bound


SHARED_ENVIRONMENT = ("python", "machine", "processor", "numpy", "scipy", "qiskit")


def check_witness(witness: list[dict[str, Any]], source: dict[str, Any]) -> None:
    """Each substrate's capture rounds to the atlas lane; every solved cell is this host's lstsq within roundoff.

    The first capture ran on AOCL and the second on OpenBLAS, by the libraries
    each process mapped, so a same-substrate pair never reads as the split.
    Both ran on one CPU model, interpreter and numpy, scipy and qiskit release
    (SHARED_ENVIRONMENT), so BLAS and LAPACK are the only recorded difference.
    """
    require(len(witness) == 2, "the record holds two substrates")
    kinds = [substrate_kind(sub["environment"]) for sub in witness]
    require(kinds == ["aocl", "openblas"], f"the captures ran on {kinds}, not AOCL then OpenBLAS")
    for key in SHARED_ENVIRONMENT:
        values = [sub["environment"].get(key) for sub in witness]
        require(values[0] is not None and values[0] == values[1], f"the captures differ in {key}: {values}")
    lanes = {(lane["backend"], lane["lane"]): lane for lane in source["lanes"]}
    for k, sub in enumerate(witness):
        other = witness[1 - k]
        for backend in BACKENDS:
            lane, mine = lanes[backend, LANE], sub["backends"][backend]
            n = len(lane["measured_offset_rad"])
            require(set(mine["log_ratios"]) == set(CELLS), f"substrate {k} {backend}: cells differ")
            require(all(len(v) == n for v in mine["log_ratios"].values()), f"substrate {k} {backend}: fold count")
            require([round(float(v), 6) for v in mine["offsets"]] == lane["measured_offset_rad"], "offsets miss atlas")
            for family in acf.SINGLE:
                rounded = [[round(float(v), 9) for v in row] for row in mine["blocks"][family]]
                require(
                    rounded == lane["fitted_slopes"][family], f"substrate {k} {backend} {family}: slopes miss atlas"
                )
            require(
                mine["other_own_sha256"] == solutions_digest(other["backends"][backend]["solutions"]["own"]),
                f"substrate {k} {backend}: other_solution is not substrate {1 - k}'s own solution",
            )
            theirs = other["backends"][backend]
            own_offsets = np.array(mine["offsets"], dtype=float)
            their_design = model_design(theirs["blocks"], theirs["offsets"], MODEL)
            cells = {
                "own": fold_problems(model_design(mine["blocks"], mine["offsets"], MODEL), own_offsets),
                "other_problem": fold_problems(their_design, np.array(theirs["offsets"], dtype=float)),
                "other_design": fold_problems(their_design, own_offsets),
            }
            labels = [(cell, h) for cell in cells for h in range(n)]
            fresh = parallel.ordered_map(FoldLstsq(), [cells[cell][h] for cell, h in labels])
            for (cell, h), solved in zip(labels, fresh, strict=True):
                error, bound = fold_solution_error(cells[cell][h], mine["solutions"][cell][h], solved)
                require(error <= bound, f"substrate {k} {backend} fold {h}: {cell} solution {error:.2e} > {bound:.2e}")


def compare_summary(retained: Any, fresh: Any, path: str, norm: bool = False) -> None:
    """Exact agreement, except NORM_KEYS fields, which agree within CONDITION_RELATIVE."""
    if isinstance(retained, dict):
        require(isinstance(fresh, dict) and set(retained) == set(fresh), f"{path}: keys differ")
        for key in retained:
            compare_summary(retained[key], fresh[key], f"{path}.{key}", norm or key in NORM_KEYS)
    elif isinstance(retained, list):
        require(isinstance(fresh, list) and len(retained) == len(fresh), f"{path}: lengths differ")
        for k, (a, b) in enumerate(zip(retained, fresh, strict=True)):
            compare_summary(a, b, f"{path}[{k}]", norm)
    elif norm and isinstance(retained, float):
        require(isinstance(fresh, float), f"{path}: {retained!r} against {fresh!r}")
        require(abs(retained - fresh) <= lsq.CONDITION_RELATIVE * abs(retained), f"{path}: {retained} against {fresh}")
    else:
        require(retained == fresh, f"{path}: {retained!r} against {fresh!r}")


def check(record: dict[str, Any]) -> dict[str, Any]:
    require(record.get("schema") == SCHEMA, f"schema {record.get('schema')}, expected {SCHEMA}")
    require(record["source"]["sha256"] == lsq.sha256_bytes(SOURCE.read_bytes()), f"{SOURCE}: sha256 differs")
    require(record["study_inputs"] == study_inputs(), f"{STUDY}: resimulation moves differ from the record")
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    check_witness(record["substrates"], source)
    fresh = summary(record["substrates"], source, record["study_inputs"])
    compare_summary(record["summary"], fresh, "summary")
    return fresh


def self_test(path: Path) -> int:
    record = json.loads(path.read_text(encoding="utf-8"))
    check(record)
    backend = BACKENDS[0]
    corruptions = {
        "log ratio": lambda r: r["substrates"][0]["backends"][backend]["log_ratios"]["other_solution"].__setitem__(
            0, r["substrates"][0]["backends"][backend]["log_ratios"]["other_solution"][0] + 1e-9
        ),
        "slope": lambda r: r["substrates"][1]["backends"][backend]["blocks"]["axis_tilt"][0].__setitem__(0, 0.5),
        "solution": lambda r: r["substrates"][1]["backends"][backend]["solutions"]["own"][0].__setitem__(0, 1.0),
        "cross solution": lambda r: r["substrates"][0]["backends"][backend]["solutions"]["other_problem"][
            0
        ].__setitem__(0, 1.0),
        "substrate": lambda r: r["substrates"][1].__setitem__("environment", r["substrates"][0]["environment"]),
        "shared environment": lambda r: r["substrates"][1]["environment"].__setitem__("numpy", "0.0.0"),
        "summary": lambda r: r["summary"][backend]["base_s"]["max_over_tolerance"].__setitem__("solve", 0.0),
        "study input": lambda r: r["study_inputs"][backend]["moves"].__setitem__(0, 0.0),
    }
    for label, corrupt in corruptions.items():
        bad = copy.deepcopy(record)
        corrupt(bad)
        try:
            check(bad)
        except SystemExit:
            continue
        raise SystemExit(f"self-test: --check accepted a corrupted {label}")
    print(f"self-test passed: {len(corruptions)} corruptions rejected")
    return 0


def report(record: dict[str, Any]) -> None:
    names = [f"{e['blas']['name']} {e['blas']['version']}" for e in (s["environment"] for s in record["substrates"])]
    for backend, entry in record["summary"].items():
        h = entry["moved_prediction"]
        moves = entry["base_s"]["moves"]
        print(
            f"{backend} [{h}] base {names[0]} vs {names[1]}: full {moves['full'][h]:.3g} solve {moves['solve'][h]:.3g}"
            f" design {moves['design'][h]:.3g} resimulation {moves['resimulation'][h]:.3g};"
            f" core-329 margins {entry['core329_margin']}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--capture", type=Path)
    parser.add_argument("--other", type=Path)
    parser.add_argument("--combine", type=Path, nargs=2)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--self-test", type=Path)
    args = parser.parse_args()
    if args.self_test:
        return self_test(args.self_test)
    if args.check:
        retained = json.loads(args.check.read_text(encoding="utf-8"))
        report({**retained, "summary": check(retained)})
        print(f"{args.check}: summary reproduced")
        return 0
    if args.capture:
        other = json.loads(args.other.read_text(encoding="utf-8")) if args.other else None
        args.capture.parent.mkdir(parents=True, exist_ok=True)
        args.capture.write_text(json.dumps(capture(other)) + "\n", encoding="utf-8")
        return 0
    require(args.combine is not None and args.out is not None, "--capture, --combine with --out, or --check")
    first, second = (json.loads(p.read_text(encoding="utf-8")) for p in args.combine)
    record = combine(first, second)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    report(record)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
