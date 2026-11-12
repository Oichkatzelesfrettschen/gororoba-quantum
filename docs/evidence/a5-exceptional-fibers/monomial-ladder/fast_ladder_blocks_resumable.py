"""The block ladder of fast_ladder_blocks.py with a verified checkpoint manifest.

    $PYTHON docs/evidence/a5-exceptional-fibers/monomial-ladder/fast_ladder_blocks_resumable.py --slug xm-nm \
        --prime 32009 --degree 8 --order 34 [--batch 1024] [--threads N] [--out record.json] [--checkpoint DIR]

The arithmetic, storage rules and echelon engine are those of fast_ladder_blocks.py, whose bytes stay fixed because
the retained order-34 record binds them by digest; this module imports BlockEchelon from it and replaces only the
ladder driver. With --checkpoint the two spaces of every finished degree are saved as uint16 arrays and the manifest
of ladder_checkpoint.py is rewritten atomically after the arrays. The header the manifest binds holds the engine,
slug, prime, order, degree, batch, block, the sha256 of every producer file (this module, ladder_checkpoint.py,
fast_ladder_blocks.py, fast_ladder.py, the slice-ring module, plucker_limits.py and parallel.py) and the model data:
generator count, generator order, variable count, offsets, the sha256 of the generator terms at the top order and of
both starting spaces. A resume compares that header and every array's dtype, shape and sha256 with the checkpoint
and stops on any difference, so a resumed record carries arrays produced by the sources and inputs its own header
names.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import scipy
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[3] / "gororoba_quantum"))

import fast_ladder as fl  # noqa: E402
import fast_ladder_blocks as fb  # noqa: E402
import ladder_checkpoint as ck  # noqa: E402

import parallel  # noqa: E402


def producer_digests(root: Path, name: str) -> dict[str, str]:
    """sha256 of every source file whose bytes decide the arrays of a ladder."""
    paths = {f"{n}.py": HERE / f"{n}.py" for n in ("fast_ladder_blocks_resumable", "ladder_checkpoint")}
    paths |= {f"{n}.py": HERE / f"{n}.py" for n in ("fast_ladder_blocks", "fast_ladder", name)}
    paths["plucker_limits.py"] = root / "docs/evidence/a5-exceptional-fibers/kernel-limits/plucker_limits.py"
    paths["parallel.py"] = Path(parallel.__file__)
    return {key: hashlib.sha256(path.read_bytes()).hexdigest() for key, path in paths.items()}


def generators_sha256(lad: Any, model: dict[str, Any], order: int) -> str:
    """sha256 of the generator terms of the model at the largest truncation order, in the model's order."""
    terms = [
        [[list(key), sorted([list(e), c] for e, c in lad.plain(poly).items())] for key, poly in sorted(blocks.items())]
        for blocks in model["blocks"](order)
    ]
    return hashlib.sha256(json.dumps(terms, separators=(",", ":")).encode()).hexdigest()


def model_digest(model: dict[str, Any], initial: dict[str, np.ndarray], generators: str) -> dict[str, Any]:
    """The model data a ladder starts from: shape parameters, both starting spaces and the generator terms."""
    return {
        "generators": int(model["count"]),
        "generators_sha256": generators,
        "generator_order": int(model["low"]),
        "nvars": int(model["nvars"]),
        "offsets": [int(o) for o in model["offsets"]],
        "initial_sha256": {key: ck.array_sha256(initial[key]) for key in ck.KEYS},
        "initial_shape": {key: list(initial[key].shape) for key in ck.KEYS},
    }


def ladder(
    root: Path, slug: str, prime: int, degree: int, order: int, batch: int, out: Path | None, checkpoint: Path | None
) -> dict[str, Any]:
    started = time.time()
    if prime >= 1 << 15:
        raise SystemExit(f"p = {prime}: the float64 bound holds for p < 2^15")
    name = "e8_ladder" if slug.startswith("e8") else "x_same_ladder"
    lad = fl.load(root, name)
    model = (fl.e8_model if slug.startswith("e8") else fl.x_model)(lad, slug, prime, order)
    low = model["low"]
    start = order - low * degree
    if start < 2:
        raise SystemExit(f"order {order} is below {low * degree + 2}")
    first_source = fl.Space(model["nvars"], start, model["offsets"])
    initial = {
        key: np.array([first_source.vector(b) for b in model["basis"](start, key == "B")]).astype(np.uint16)
        for key in ck.KEYS
    }
    header: dict[str, Any] = {
        "engine": "float64-batched-echelon, block storage, verified checkpoints",
        "slug": slug,
        "prime": prime,
        "order": order,
        "degree": degree,
        "batch": batch,
        "block": fb.BLOCK,
        "source_sha256": producer_digests(root, name),
        "model": model_digest(model, initial, generators_sha256(lad, model, order)),
    }
    record: dict[str, Any] = {
        **{k: header[k] for k in ("slug", "prime", "order", "degree")},
        "generators": model["count"],
        "generator_order": low,
        "engine": header["engine"],
        "source_sha256": header["source_sha256"],
        "model_sha256": header["model"]["initial_sha256"],
        "versions": {"torch": torch.__version__, "numpy": np.__version__, "scipy": scipy.__version__},
        "batch": batch,
        "block": fb.BLOCK,
        "threads": torch.get_num_threads(),
        "rows": [],
        "complete": False,
    }

    def write() -> None:
        record["seconds"] = round(time.time() - started, 1)
        record["peak_gib"] = fb.peak_gib()
        if out:
            out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")

    stem = ck.stem_of(slug, prime, order, degree)
    manifest: dict[str, Any] = {}
    resumed = 0
    spaces = initial
    if checkpoint:
        checkpoint.mkdir(parents=True, exist_ok=True)
        resumed, loaded, rows, manifest = ck.resume_point(checkpoint, stem, header)
        if resumed:
            spaces = loaded
            record["rows"] = rows
            record["resumed_after_degree"] = resumed
    first = resumed + 1
    source = fl.Space(model["nvars"], start + low * resumed, model["offsets"])
    fb.say(
        event="start", slug=slug, prime=prime, order=order, degree=degree, first_degree=first, peak_gib=fb.peak_gib()
    )
    write()
    for d in range(first, degree + 1):
        current = start + low * d
        target = fl.Space(model["nvars"], current, model["offsets"])
        if target.size >= fl.EXACT_COLUMNS:
            raise SystemExit(f"{target.size} columns at order {current}: the bound holds below {fl.EXACT_COLUMNS}")
        jobs = [
            ({key: lad.plain(poly) for key, poly in blocks.items()}, source, target)
            for blocks in model["blocks"](current)
        ]
        maps = [fl.tensor(m) for m in parallel.ordered_map(fl.sparse_map, jobs, min_items=2)]
        row = {"degree": d, "order": current, "columns": target.size, "map_nnz": int(sum(m._nnz() for m in maps))}
        fb.say(event="maps", **row, peak_gib=fb.peak_gib(), seconds=round(time.time() - started, 1))
        for key in ck.KEYS:
            echelon = fb.BlockEchelon(target.size, prime)
            space = spaces[key]
            for index, matrix in enumerate(maps):
                for begin in range(0, len(space), batch):
                    wide = torch.from_numpy(space[begin : begin + batch].astype(np.float64))
                    echelon.insert((matrix @ wide.T).T.contiguous())
                fb.say(
                    event="map",
                    degree=d,
                    space=key,
                    map=index + 1,
                    maps=len(maps),
                    rank=echelon.rank,
                    peak_gib=fb.peak_gib(),
                    seconds=round(time.time() - started, 1),
                )
            row[key] = echelon.rank
            spaces[key] = echelon.compact()
            del echelon, space
        row["r"] = row["A"] - row["B"]
        row["seconds"] = round(time.time() - started, 1)
        fb.say(event="degree", **row, peak_gib=fb.peak_gib())
        record["rows"].append(row)
        if checkpoint:
            ck.save_degree(checkpoint, stem, manifest, d, spaces, record["rows"])
        write()
        source = target
    record["complete"] = True
    write()
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--slug", default="xm-nm")
    parser.add_argument("--prime", type=int, default=32009)
    parser.add_argument("--degree", type=int, required=True)
    parser.add_argument("--order", type=int, required=True)
    parser.add_argument("--batch", type=int, default=1024)
    parser.add_argument("--threads", type=int, default=0)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    sys.path.insert(0, str(root / "gororoba_quantum"))
    sys.path.insert(0, str(root / "docs/evidence/a5-exceptional-fibers/kernel-limits"))
    if args.threads:
        torch.set_num_threads(args.threads)
    record = ladder(root, args.slug, args.prime, args.degree, args.order, args.batch, args.out, args.checkpoint)
    fb.say(event="done", rows=record["rows"], peak_gib=record["peak_gib"], seconds=record["seconds"])


if __name__ == "__main__":
    main()
