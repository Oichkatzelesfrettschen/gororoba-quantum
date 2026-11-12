"""The ladder of fast_ladder.py with block storage: the same ranks at about half the peak memory, resumable.

    $PYTHON docs/evidence/a5-exceptional-fibers/monomial-ladder/fast_ladder_blocks.py --slug xm-nm --prime 32009 \
        --degree 8 --order 34 [--batch 1024] [--threads N] [--out record.json] [--checkpoint DIR]

The arithmetic is that of fast_ladder.py (float64 batches reduced against a reduced row echelon form, exact for
p < 2^15 and fewer than 2^17 columns); the models, sparse maps and leaf echelon are imported from it. Three storage
rules differ. The echelon form is a list of row blocks of BLOCK rows, so it grows by allocating a block and never by
copying itself. A finished space A_d or B_d is kept as uint16 (entries are below p < 2^15) and widened to float64 one
batch at a time. With --checkpoint the two spaces of every finished degree are saved as uint16 arrays, and a later
run with the same arguments resumes after the highest degree whose two files are present.

Reduction against the blocks one after another equals reduction against the whole form: the form is reduced, so a
row of one block is zero in the pivot columns of every other block, and subtracting a block leaves the batch's
entries in the other blocks' pivot columns unchanged.

Every step prints one JSON line to stdout (space, map index, rank, resident memory, seconds), and --out is rewritten
after every degree, so a run that stops early leaves its finished rows and its last position.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import resource
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

import parallel  # noqa: E402

BLOCK = 2048


def peak_gib() -> float:
    """Peak resident memory of this process in GiB (ru_maxrss is in kB on Linux)."""
    return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20, 2)


class BlockEchelon:
    """A reduced row echelon form held as row blocks of at most BLOCK rows."""

    LEAF = fl.Echelon.LEAF

    def __init__(self, columns: int, prime: int) -> None:
        self.prime = prime
        self.columns = columns
        self.blocks: list[torch.Tensor] = []
        self.pivots: list[torch.Tensor] = []
        self.fill = 0
        self.rank = 0

    def _views(self) -> list[tuple[torch.Tensor, torch.Tensor]]:
        out = []
        for i, (block, pivots) in enumerate(zip(self.blocks, self.pivots, strict=True)):
            rows = self.fill if i == len(self.blocks) - 1 else BLOCK
            out.append((block[:rows], pivots[:rows]))
        return out

    def reduce(self, batch: torch.Tensor) -> torch.Tensor:
        """Reduces the batch in place; one remainder per block keeps every value below 2^47."""
        for rows, pivots in self._views():
            if len(rows):
                batch.addmm_(batch[:, pivots], rows, alpha=-1).remainder_(self.prime)
        return batch.remainder_(self.prime)

    def append(self, new: torch.Tensor, new_pivots: torch.Tensor) -> None:
        if not len(new_pivots):
            return
        for rows, _ in self._views():
            if len(rows):
                rows.addmm_(rows[:, new_pivots], new, alpha=-1).remainder_(self.prime)
        done = 0
        while done < len(new_pivots):
            if not self.blocks or self.fill == BLOCK:
                self.blocks.append(torch.zeros((BLOCK, self.columns), dtype=torch.float64))
                self.pivots.append(torch.zeros(BLOCK, dtype=torch.int64))
                self.fill = 0
            take = min(BLOCK - self.fill, len(new_pivots) - done)
            self.blocks[-1][self.fill : self.fill + take] = new[done : done + take]
            self.pivots[-1][self.fill : self.fill + take] = new_pivots[done : done + take]
            self.fill += take
            done += take
        self.rank += len(new_pivots)

    def insert(self, batch: torch.Tensor) -> None:
        batch = self.reduce(batch)
        batch = batch[batch.any(dim=1)]
        if not len(batch):
            return
        local = fl.Echelon(self.columns, self.prime, capacity=len(batch))
        for begin in range(0, len(batch), self.LEAF):
            chunk = local.reduce(batch[begin : begin + self.LEAF].clone())
            chunk = chunk[chunk.any(dim=1)]
            if len(chunk):
                local.append(*fl.leaf_rref(chunk, self.prime))
        self.append(local.rows, local.pivots)

    def compact(self) -> np.ndarray:
        """The rows as one uint16 array; each block is released as it is copied."""
        out = np.empty((self.rank, self.columns), dtype=np.uint16)
        at = 0
        views = self._views()
        self.blocks, self.pivots = [], []
        while views:
            rows, _ = views.pop(0)
            out[at : at + len(rows)] = rows.numpy().astype(np.uint16)
            at += len(rows)
            del rows
        return out


def say(**fields: Any) -> None:
    print(json.dumps(fields), flush=True)


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
    record: dict[str, Any] = {
        "slug": slug,
        "prime": prime,
        "order": order,
        "degree": degree,
        "generators": model["count"],
        "generator_order": low,
        "engine": "float64-batched-echelon, block storage",
        "source_sha256": {
            f"{n}.py": hashlib.sha256((HERE / f"{n}.py").read_bytes()).hexdigest()
            for n in ("fast_ladder_blocks", "fast_ladder", name)
        },
        "versions": {"torch": torch.__version__, "numpy": np.__version__, "scipy": scipy.__version__},
        "batch": batch,
        "block": BLOCK,
        "threads": torch.get_num_threads(),
        "rows": [],
        "complete": False,
    }

    def write() -> None:
        record["seconds"] = round(time.time() - started, 1)
        record["peak_gib"] = peak_gib()
        if out:
            out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")

    def saved(d: int, key: str) -> Path | None:
        return checkpoint / f"{slug}-p{prime}-n{order}-deg{degree}-d{d}-{key}.npy" if checkpoint else None

    first = 1
    spaces: dict[str, np.ndarray] = {}
    if checkpoint:
        checkpoint.mkdir(parents=True, exist_ok=True)
        rows_file = checkpoint / f"{slug}-p{prime}-n{order}-deg{degree}-rows.json"
        for d in range(degree, 0, -1):
            files = [saved(d, key) for key in ("A", "B")]
            if all(f is not None and f.exists() for f in files) and rows_file.exists():
                spaces = {key: np.load(f) for key, f in zip(("A", "B"), files, strict=True) if f is not None}
                record["rows"] = [r for r in json.loads(rows_file.read_text()) if r["degree"] <= d]
                record["resumed_after_degree"] = d
                first = d + 1
                break
    source = fl.Space(model["nvars"], start + low * (first - 1), model["offsets"])
    if first == 1:
        spaces = {
            key: np.array([source.vector(b) for b in model["basis"](start, key == "B")]).astype(np.uint16)
            for key in ("A", "B")
        }
    say(event="start", slug=slug, prime=prime, order=order, degree=degree, first_degree=first, peak_gib=peak_gib())
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
        say(event="maps", **row, peak_gib=peak_gib(), seconds=round(time.time() - started, 1))
        for key in ("A", "B"):
            echelon = BlockEchelon(target.size, prime)
            space = spaces[key]
            for index, matrix in enumerate(maps):
                for begin in range(0, len(space), batch):
                    wide = torch.from_numpy(space[begin : begin + batch].astype(np.float64))
                    echelon.insert((matrix @ wide.T).T.contiguous())
                say(
                    event="map",
                    degree=d,
                    space=key,
                    map=index + 1,
                    maps=len(maps),
                    rank=echelon.rank,
                    peak_gib=peak_gib(),
                    seconds=round(time.time() - started, 1),
                )
            row[key] = echelon.rank
            spaces[key] = echelon.compact()
            del echelon, space
        row["r"] = row["A"] - row["B"]
        row["seconds"] = round(time.time() - started, 1)
        say(event="degree", **row, peak_gib=peak_gib())
        record["rows"].append(row)
        if checkpoint:
            for key in ("A", "B"):
                path = saved(d, key)
                if path is not None:
                    np.save(path, spaces[key])
            rows_file.write_text(json.dumps(record["rows"]) + "\n", encoding="utf-8")
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
    say(event="done", rows=record["rows"], peak_gib=record["peak_gib"], seconds=record["seconds"])


if __name__ == "__main__":
    main()
