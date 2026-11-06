"""Compare the Singular quotient exports of two fiber_rank engines byte for byte.

Usage: export_equality.py ENGINE_A ENGINE_B HEADER N

Both engines' QUOTIENT_SCRIPT run on the same header and N; every exported file (qB, qM1..qMn, qG) must have the same
sha256. Prints one JSON line and exits 0 when all files match, 1 otherwise.
"""

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def load(path: str, name: str):  # noqa: ANN201
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def export(mod, header: str, N: int, singular: str) -> tuple[dict[str, str], float]:  # noqa: ANN001
    p, names = mod.parse_header(header)[:2]
    text = mod.header_text(header)
    with tempfile.TemporaryDirectory() as out:
        script = mod.QUOTIENT_SCRIPT.format(p=p, names=",".join(names), J=text["J"], G=text["G"], N=N, d=0, out=out)
        path = os.path.join(out, "q.sing")
        Path(path).write_text(script)
        t = time.time()
        res = subprocess.run(
            [singular, "-q", "--no-rc", path], stdin=subprocess.DEVNULL, capture_output=True, text=True, check=True
        )
        if "RESULT quotient" not in res.stdout or any(ln.startswith("? ") for ln in res.stdout.splitlines()):
            raise RuntimeError("Singular export failed: " + res.stdout[-500:] + res.stderr[-500:])
        files = sorted(f for f in os.listdir(out) if f.startswith("q") and f.endswith(".txt"))
        return {f: hashlib.sha256(Path(out, f).read_bytes()).hexdigest() for f in files}, time.time() - t


def main() -> int:
    if len(sys.argv) != 5:
        print(__doc__, file=sys.stderr)
        return 2
    a, b, header, N = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
    singular = os.environ.get("SINGULAR", "Singular")
    ha, ta = export(load(a, "engine_a"), header, N, singular)
    hb, tb = export(load(b, "engine_b"), header, N, singular)
    differing = sorted(f for f in set(ha) | set(hb) if ha.get(f) != hb.get(f))
    sha = {e: hashlib.sha256(Path(e).read_bytes()).hexdigest()[:16] for e in (a, b)}
    rec = {
        "check": "quotient-export-equality",
        "engine_a": sha[a],
        "engine_b": sha[b],
        "header_sha256_16": hashlib.sha256(Path(header).read_bytes()).hexdigest()[:16],
        "N": N,
        "files": len(ha),
        "differing": differing,
        "seconds_a": round(ta, 1),
        "seconds_b": round(tb, 1),
    }
    print(json.dumps(rec))
    return 0 if not differing and ha else 1


if __name__ == "__main__":
    sys.exit(main())
