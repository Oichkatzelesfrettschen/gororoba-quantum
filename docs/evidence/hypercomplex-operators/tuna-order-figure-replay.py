"""Replay a retained Tuna order figure by its decoded pixels and its metadata.

The figure producers encode PNG through Pillow, which deflates with the system
libz.so.1: zlib-ng in compat mode on one host and zlib 1.3.1 on the Ubuntu
runners compress identical pixels into different bytes. A replay therefore runs
the unchanged producer into a temporary directory and requires the decoded RGBA
pixels, the image size and mode and the PNG text chunks to equal the retained
figure's, and every metadata field except png_sha256 to equal the retained
metadata. The retained metadata's png_sha256 binds the retained figure file
itself, so the PNG and JSON bytes keep the digest the producer recorded.

Usage: "$PYTHON" -B -W error docs/evidence/hypercomplex-operators/tuna-order-figure-replay.py
    [--producer PATH --summary PATH --figure PATH]
"""

import argparse
import copy
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from PIL import Image

root = Path(__file__).resolve().parents[3]
EVIDENCE = "docs/evidence/hypercomplex-operators"


def decoded(png: bytes) -> tuple[str, tuple[int, int], dict[str | tuple[int, int], Any], bytes]:
    """The image mode, size, text chunks and raw pixel bytes of an encoded PNG."""
    with Image.open(io.BytesIO(png)) as image:
        image.load()
        return image.mode, image.size, dict(image.info), image.tobytes()


def compare(retained_png: bytes, retained_metadata: dict[str, Any], fresh_png: bytes, fresh: dict[str, Any]) -> None:
    """Raise unless the fresh rendering reproduces the retained figure and metadata."""
    if hashlib.sha256(retained_png).hexdigest() != retained_metadata.get("png_sha256"):
        raise ValueError("retained metadata png_sha256 differs from the retained figure")
    if decoded(fresh_png) != decoded(retained_png):
        raise ValueError("fresh rendering differs from the retained figure pixels")
    unbound = {key: value for key, value in retained_metadata.items() if key != "png_sha256"}
    if unbound != {key: value for key, value in fresh.items() if key != "png_sha256"}:
        raise ValueError("fresh metadata differs from the retained metadata")


def mutations(retained_png: bytes, retained_metadata: dict[str, Any], fresh_png: bytes, fresh: dict[str, Any]) -> int:
    """Require compare() to reject a changed pixel, metadata field and figure binding."""
    mode, size, info, pixels = decoded(fresh_png)
    changed_pixels = bytearray(pixels)
    changed_pixels[len(changed_pixels) // 2] ^= 0xFF
    buffer = io.BytesIO()
    Image.frombytes(mode, size, bytes(changed_pixels)).save(buffer, format="PNG", pnginfo=None)
    edited_field = copy.deepcopy(fresh)
    edited_field["summary_sha256"] = "0" * 64
    unbound = copy.deepcopy(retained_metadata)
    unbound["png_sha256"] = "0" * 64
    cases = [
        (retained_png, retained_metadata, buffer.getvalue(), fresh),
        (retained_png, retained_metadata, fresh_png, edited_field),
        (retained_png, unbound, fresh_png, fresh),
    ]
    for case in cases:
        try:
            compare(*case)
        except ValueError:
            continue
        raise ValueError("a corrupted figure replay passed comparison")
    return len(cases)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--producer", default=f"{EVIDENCE}/tuna-order-analysis-bound-probabilities.py")
    parser.add_argument(
        "--summary", default="results/quantum_inspire/runs/tuna17-quaternion-order-noise/pilot-summary.json"
    )
    parser.add_argument("--figure", default=f"{EVIDENCE}/tuna-order-analysis-bound-probabilities.png")
    arguments = parser.parse_args()
    figure = root / arguments.figure
    retained_png = figure.read_bytes()
    retained_metadata = json.loads(figure.with_suffix(".json").read_bytes())
    with tempfile.TemporaryDirectory() as scratch:
        output = Path(scratch) / figure.name
        subprocess.run(
            [sys.executable, "-B", "-W", "error", str(root / arguments.producer)]
            + ["--summary", arguments.summary, "--output", str(output)],
            cwd=root,
            env=os.environ,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        fresh_png = output.read_bytes()
        fresh = json.loads(output.with_suffix(".json").read_bytes())
    compare(retained_png, retained_metadata, fresh_png, fresh)
    rejected = mutations(retained_png, retained_metadata, fresh_png, fresh)
    print(f"{arguments.figure}: pixels and metadata replayed; {rejected} corruptions rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
