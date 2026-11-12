"""Checkpoint manifest of a block ladder: save each finished degree, verify before a resume.

The manifest `<stem>-manifest.json` holds the header of the run (a JSON object the caller builds: engine, slug, prime,
order, degree, batch, block, producer digests and a digest of the model data) and, for each finished degree, the rows
so far plus the dtype, shape and sha256 of both saved uint16 arrays. `resume_point` takes the highest degree the
manifest lists, compares the manifest header with the header of the current run field by field, and compares each
array's dtype, shape and sha256 with the loaded bytes before the array is returned. A difference raises SystemExit
naming the field. A checkpoint file with no manifest, or a manifest that names a missing file, is refused as well.
The module needs numpy only; fast_ladder_blocks_resumable.py builds the header and drives the ladder.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

MANIFEST_SCHEMA = "fast-ladder-blocks-checkpoint-v1"
KEYS = ("A", "B")


def array_sha256(array: np.ndarray) -> str:
    """sha256 of the C-order bytes of the array."""
    return hashlib.sha256(np.ascontiguousarray(array)).hexdigest()


def stem_of(slug: str, prime: int, order: int, degree: int) -> str:
    return f"{slug}-p{prime}-n{order}-deg{degree}"


def array_file(checkpoint: Path, stem: str, d: int, key: str) -> Path:
    return checkpoint / f"{stem}-d{d}-{key}.npy"


def differing_field(expected: Any, found: Any, path: str = "header") -> str | None:
    """The dotted path of the first field in which two JSON values differ, or None."""
    if isinstance(expected, dict) and isinstance(found, dict):
        for key in sorted(set(expected) | set(found)):
            if key not in expected or key not in found:
                return f"{path}.{key}"
            inner = differing_field(expected[key], found[key], f"{path}.{key}")
            if inner is not None:
                return inner
        return None
    return None if expected == found else path


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    scratch = path.with_name(path.name + ".tmp")
    scratch.write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    scratch.replace(path)


def save_degree(
    checkpoint: Path, stem: str, manifest: dict[str, Any], d: int, spaces: dict[str, np.ndarray], rows: list[Any]
) -> None:
    """Saves both spaces of degree d, then records them in the manifest."""
    entry: dict[str, Any] = {"rows": json.loads(json.dumps(rows))}
    for key in KEYS:
        np.save(array_file(checkpoint, stem, d, key), spaces[key])
        entry[key] = {
            "file": array_file(checkpoint, stem, d, key).name,
            "dtype": str(spaces[key].dtype),
            "shape": list(spaces[key].shape),
            "sha256": array_sha256(spaces[key]),
        }
    manifest["degrees"][str(d)] = entry
    write_manifest(checkpoint / f"{stem}-manifest.json", manifest)


def resume_point(
    checkpoint: Path, stem: str, header: dict[str, Any]
) -> tuple[int, dict[str, np.ndarray], list[Any], dict[str, Any]]:
    """Verifies the checkpoint of a run against its header and returns (degree, spaces, rows, manifest).

    Degree 0 with empty spaces means a fresh start. Every refusal raises SystemExit naming the differing field.
    """
    manifest_path = checkpoint / f"{stem}-manifest.json"
    fresh: dict[str, Any] = {"schema": MANIFEST_SCHEMA, "header": header, "degrees": {}}
    if not manifest_path.exists():
        stray = sorted(p.name for p in checkpoint.glob(f"{stem}-*"))
        if stray:
            raise SystemExit(f"checkpoint refused: {stray[0]} has no manifest {manifest_path.name}")
        return 0, {}, [], fresh
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise SystemExit(f"checkpoint refused: manifest.schema is {manifest.get('schema')!r}, not {MANIFEST_SCHEMA!r}")
    field = differing_field(header, manifest.get("header"))
    if field is not None:
        raise SystemExit(f"checkpoint refused: {field} differs between this run and the manifest")
    degrees = manifest.get("degrees", {})
    if not degrees:
        return 0, {}, [], manifest
    d = max(int(k) for k in degrees)
    entry = degrees[str(d)]
    spaces: dict[str, np.ndarray] = {}
    for key in KEYS:
        meta = entry[key]
        path = array_file(checkpoint, stem, d, key)
        if meta["file"] != path.name or not path.exists():
            raise SystemExit(f"checkpoint refused: {path.name} is missing or misnamed in the manifest")
        array = np.load(path, allow_pickle=False)
        for name, value in (("dtype", str(array.dtype)), ("shape", list(array.shape)), ("sha256", array_sha256(array))):
            if value != meta[name]:
                raise SystemExit(
                    f"checkpoint refused: {path.name} {name} is {value}, the manifest records {meta[name]}"
                )
        spaces[key] = array
    return d, spaces, list(entry["rows"]), manifest
