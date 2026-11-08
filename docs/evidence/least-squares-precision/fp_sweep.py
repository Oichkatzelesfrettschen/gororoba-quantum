"""Sweep every least-squares backend of fp_backends.py over its own settings, one capped scope per run.

Each configuration runs as `systemd-run --user --scope -p MemoryMax=8G -p MemorySwapMax=0`, serially, REPEATS times;
precision is deterministic per configuration, and the fastest solve of the repeats is its time. Every row records the
load average before the run, because other sessions share the CPU.

usage: python fp_sweep.py fp-inputs.npz sweep.jsonl [REPEATS]
"""

from __future__ import annotations

import itertools
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def configs() -> list[tuple[str, str, dict[str, str]]]:
    """(label, --backends selector, environment) for every configuration of the sweep."""
    out: list[tuple[str, str, dict[str, str]]] = []
    for th in (1, 2, 4, 6, 10):
        out.append((f"float64 pinv, OpenBLAS threads {th}", "pinv", {"OPENBLAS_NUM_THREADS": str(th)}))
        out.append((f"float64 numpy lstsq, OpenBLAS threads {th}", "QR lstsq", {"OPENBLAS_NUM_THREADS": str(th)}))
    for driver, th in itertools.product(("gelsd", "gelsy", "gelss"), (1, 4, 10)):
        out.append(
            (
                f"float64 scipy lstsq {driver}, OpenBLAS threads {th}",
                "scipy",
                {"OPENBLAS_NUM_THREADS": str(th), "FP_LSTSQ_DRIVER": driver},
            )
        )
    for steps in (1, 2, 3):
        out.append(
            (
                f"float64 pinv + {steps} x87 refinement steps",
                "refinement",
                {"OPENBLAS_NUM_THREADS": "1", "FP_REFINE_STEPS": str(steps)},
            )
        )
    for workers in (1, 2, 4, 6, 8, 10):
        out.append(
            (
                f"x87 Householder, {workers} worker processes",
                "x87 80-bit Householder",
                {"OPENBLAS_NUM_THREADS": "1", "FP_WORKERS": str(workers)},
            )
        )
    out.append(("x87 normal equations (Cholesky)", "x87 80-bit normal", {"OPENBLAS_NUM_THREADS": "1"}))
    for backend, th in itertools.product(("sleef", "longdouble"), (1, 4, 10)):
        out.append(
            (
                f"binary128 Householder, backend {backend}, QuadBLAS threads {th}",
                "binary128 quaddtype Householder",
                {"OPENBLAS_NUM_THREADS": "1", "FP_QUAD_BACKEND": backend, "FP_QUAD_THREADS": str(th)},
            )
        )
        out.append(
            (
                f"binary128 normal equations, backend {backend}, QuadBLAS threads {th}",
                "binary128 normal",
                {"OPENBLAS_NUM_THREADS": "1", "FP_QUAD_BACKEND": backend, "FP_QUAD_THREADS": str(th)},
            )
        )
    for prec, th in itertools.product((64, 128, 192, 256), (1, 4, 10)):
        out.append(
            (
                f"arb normal equations, {prec} bits, FLINT threads {th}",
                "arb normal",
                {"OPENBLAS_NUM_THREADS": "1", "FP_ARB_PREC": str(prec), "FP_FLINT_THREADS": str(th)},
            )
        )
    return out


def run_one(inputs: str, selector: str, env: dict[str, str]) -> dict:
    with tempfile.NamedTemporaryFile(suffix=".json", dir=HERE / "sweep-runs", delete=False) as handle:
        out = Path(handle.name)
    cmd = [
        "systemd-run",
        "--user",
        "--scope",
        "-q",
        "-p",
        "MemoryMax=8G",
        "-p",
        "MemorySwapMax=0",
        "-p",
        "RuntimeMaxSec=960",
        "env",
        "MALLOC_ARENA_MAX=2",
        "GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096",
        *(f"{k}={v}" for k, v in env.items()),
        "timeout",
        "-k",
        "10",
        "900",
        sys.executable,
        "-u",
        str(HERE / "fp_backends.py"),
        inputs,
        str(out),
        "--backends",
        selector,
    ]
    load = os.getloadavg()[0]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    row: dict = {"load_before": load, "returncode": proc.returncode}
    if proc.returncode == 0 and out.exists() and out.stat().st_size:
        report = json.loads(out.read_text())
        backends = report["backends"]
        row["result"] = next(iter(backends.values())) if backends else {"error": "no backend matched"}
        row["reference_seconds"] = report["reference"]["solve_seconds"]
    else:
        row["result"] = {"error": (proc.stderr or proc.stdout)[-600:]}
    out.unlink(missing_ok=True)
    return row


def main() -> int:
    inputs, out_path = sys.argv[1], Path(sys.argv[2])
    repeats = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    (HERE / "sweep-runs").mkdir(exist_ok=True)
    done = set()
    if out_path.exists():
        done = {json.loads(line)["config"] for line in out_path.read_text().splitlines() if line.strip()}
    with out_path.open("a") as sink:
        for label, selector, env in configs():
            if label in done:
                continue
            runs = [run_one(inputs, selector, env) for _ in range(repeats)]
            ok = [r for r in runs if "error" not in r["result"]]
            row = {"config": label, "env": env, "repeats": len(runs), "load_before": [r["load_before"] for r in runs]}
            if ok:
                best = min(ok, key=lambda r: r["result"]["solve_seconds"])
                row.update(
                    {
                        "solve_seconds_min": best["result"]["solve_seconds"],
                        "solve_seconds_all": [r["result"]["solve_seconds"] for r in ok],
                        **{k: v for k, v in best["result"].items() if k not in ("seconds", "solve_seconds")},
                    }
                )
            else:
                row["error"] = runs[0]["result"]["error"]
            sink.write(json.dumps(row) + "\n")
            sink.flush()
            print(
                label,
                "->",
                row.get("solve_seconds_min"),
                row.get("bits_correct_on_scores"),
                row.get("error", "")[:80],
                flush=True,
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
