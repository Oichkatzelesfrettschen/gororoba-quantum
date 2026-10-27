"""Bit fingerprints of the numerical kernels the measurement-sequence nulls run, under each dispatch configuration.

A batched null splits its replicates across hosts only when every host returns the same bits for the same inputs.
NumPy selects float64 exp/power loops by CPU feature (AVX-512 hosts take their own loops) and OpenBLAS selects a
matmul kernel by core type, so each configuration below runs in a fresh interpreter whose environment pins or frees
those choices before NumPy loads. Inputs are deterministic grids, so the digests compare across hosts directly.

Usage: "$PYTHON" scripts/numerics_fingerprint.py --out FILE
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIGURATIONS = {
    "default": {},
    "numpy-no-avx512": {"NPY_DISABLE_CPU_FEATURES": "X86_V4 AVX512_ICL AVX512_SPR"},
    "openblas-haswell": {"OPENBLAS_CORETYPE": "Haswell"},
    "both-pinned": {"NPY_DISABLE_CPU_FEATURES": "X86_V4 AVX512_ICL AVX512_SPR", "OPENBLAS_CORETYPE": "Haswell"},
}


def digest(values) -> str:
    import numpy as np

    return hashlib.sha256(np.ascontiguousarray(np.asarray(values, dtype=float)).tobytes()).hexdigest()


def kernels() -> dict[str, str]:
    """sha256 of each kernel's float64 output bytes over fixed grids."""
    import numpy as np
    from scipy.linalg import expm
    from scipy.stats import chi2

    sys.path.insert(0, str(ROOT / "gororoba_quantum"))
    import measurement_sequence_analysis as msa
    import msq_successor_analysis as sa

    out: dict[str, str] = {}
    x = -np.linspace(0.0, 50.0, 100003)
    out["np_exp"] = digest(np.exp(x))
    out["math_exp"] = digest([math.exp(v) for v in x])
    base = 1.0 + np.linspace(0.0, 5.0, 100003)
    k = np.linspace(0.25, 1000.0, 100003)
    out["np_power"] = digest(base ** (-k))
    out["math_pow"] = digest([math.pow(b, -kk) for b, kk in zip(base.tolist(), k.tolist(), strict=True)])
    index = np.arange(4096 * 16, dtype=float).reshape(4096, 4, 4)
    a, b = np.sin(index * 0.37) * 0.5, np.cos(index * 0.11) * 0.5
    out["matmul_stack"] = digest(a @ b)
    out["matmul_single"] = digest([a[i] @ b[i] for i in range(256)])
    out["matrix_power_16"] = digest(np.linalg.matrix_power(a @ b * 0.6, 16))
    gens = []
    for t1 in np.linspace(50e-6, 400e-6, 16):
        for t2 in np.linspace(20e-6, 300e-6, 16):
            om = (math.pi / 2) / 36e-9
            gens.append(
                np.array([[-1 / t2, 0, 0, 0], [0, -1 / t2, -om, 0], [0, om, -1 / t1, 1 / t1], [0, 0, 0, 0]]) * 36e-9
            )
    out["expm_stack"] = digest(expm(np.array(gens)))
    out["chi2_sf"] = digest([chi2.sf(s, d) for s in np.linspace(0.1, 60.0, 200) for d in (1, 2, 3, 4, 8)])
    gate = (0.0005, 36e-9, 1.0, 0.0, 0.0)
    out["corrected_z"] = digest(
        [
            msa.corrected_z(arm, n, t1, 150e-6, 2e-6, 0.001, gate, 0.98)
            for arm in ("measure", "delay", "unitary", "settle")
            for n in (2, 4, 8, 16)
            for t1 in np.linspace(80e-6, 350e-6, 12)
        ]
    )
    delays = [0.0, 20e-6, 50e-6, 100e-6, 200e-6, 400e-6]
    fits = []
    for t_true in np.linspace(80e-6, 300e-6, 6):
        for shape in (0.5, 4.0, 64.0, math.inf):
            y = [1 - 2 * float(sa.survival(np.array([d]), float(t_true), shape)[0]) for d in delays]
            y = [v + 1e-3 * math.sin(7.0 * i + t_true * 1e4) for i, v in enumerate(y)]
            fit = sa.fit_gamma_rate(delays, y, [1e6] * len(delays))
            fits += [fit["t_s"], fit["shape"] if math.isfinite(fit["shape"]) else -1.0, fit["chi2"]]
    out["fit_gamma_rate"] = digest(fits)
    return out


def environment() -> dict[str, object]:
    import numpy as np
    import scipy
    from threadpoolctl import threadpool_info

    runtime = np.show_runtime.__module__
    features = [name for name, on in np._core._multiarray_umath.__cpu_features__.items() if on]
    return {
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "glibc": " ".join(platform.libc_ver()),
        "machine": platform.machine(),
        "processor": next(
            (
                line.split(":", 1)[1].strip()
                for line in Path("/proc/cpuinfo").read_text().splitlines()
                if line.startswith("model name")
            ),
            "",
        ),
        "cpu_features": sorted(features),
        "blas": [
            {key: info.get(key) for key in ("internal_api", "version", "architecture")} for info in threadpool_info()
        ],
        "runtime_module": runtime,
        "env": {key: os.environ.get(key) for key in ("NPY_DISABLE_CPU_FEATURES", "OPENBLAS_CORETYPE")},
    }


def child() -> int:
    print(json.dumps({"environment": environment(), "kernels": kernels()}))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path)
    parser.add_argument("--child", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.child:
        return child()
    if args.out is None:
        parser.error("--out is required")
    result = {}
    for name, extra in CONFIGURATIONS.items():
        env = {**os.environ, "OPENBLAS_NUM_THREADS": "1", **extra}
        done = subprocess.run(
            [sys.executable, "-B", __file__, "--child"], env=env, capture_output=True, text=True, check=False
        )
        if done.returncode != 0:
            result[name] = {"error": done.stderr[-2000:]}
            continue
        result[name] = json.loads(done.stdout.strip().splitlines()[-1])
        result[name]["stderr"] = done.stderr[-2000:]
    args.out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
