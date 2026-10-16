"""TPU probe: which JAX backend a Kaggle session exposes, and a density-matrix replay on it when it is a TPU.

The probe records the installed jax, jaxlib and libtpu distributions, every
device of every JAX backend, and whether ``jax.devices("tpu")`` succeeds. On
a TPU it replays a fixed 3-qubit program (H, RY, a CX on non-adjacent
qubits, amplitude damping) as local unitary and Kraus contractions on the
density matrix, with ``Precision.HIGHEST`` matmuls in complex64, and compares
the result with the same program applied in numpy complex128. Local
operators follow Qiskit's little-endian order: qubit q is bit q of the basis
index, and qargs[0] is the least significant local bit.

The output states where the replay ran from the result array's devices, not
from the session's accelerator label.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

GAMMA = 0.17
THETA = 0.37


def program() -> list[tuple[tuple[int, ...], np.ndarray]]:
    """(qargs, Kraus operators) in application order; a unitary is a rank-1 channel."""
    h = np.array([[1, 1], [1, -1]], dtype=np.complex128) / np.sqrt(2)
    c, s = np.cos(THETA / 2), np.sin(THETA / 2)
    ry = np.array([[c, -s], [s, c]], dtype=np.complex128)
    # Local basis index = control + 2 * target for qargs (control, target).
    cx = np.zeros((4, 4), dtype=np.complex128)
    for control in (0, 1):
        for target in (0, 1):
            cx[control + 2 * (target ^ control), control + 2 * target] = 1
    damping = np.array([[[1, 0], [0, np.sqrt(1 - GAMMA)]], [[0, np.sqrt(GAMMA)], [0, 0]]], dtype=np.complex128)
    return [((0,), h[None]), ((2,), ry[None]), ((0, 2), cx[None]), ((2,), damping)]


def full_operator(n: int, qargs: tuple[int, ...], local: np.ndarray) -> np.ndarray:
    """Embed a local operator on qargs into the n-qubit space (reference path only)."""
    dim = 2**n
    out = np.zeros((dim, dim), dtype=np.complex128)
    for col in range(dim):
        local_col = sum(((col >> q) & 1) << k for k, q in enumerate(qargs))
        rest = col & ~sum(1 << q for q in qargs)
        for local_row in range(2 ** len(qargs)):
            row = rest | sum(((local_row >> k) & 1) << q for k, q in enumerate(qargs))
            out[row, col] += local[local_row, local_col]
    return out


def reference(n: int) -> np.ndarray:
    rho = np.zeros((2**n, 2**n), dtype=np.complex128)
    rho[0, 0] = 1
    for qargs, kraus in program():
        rho = sum(full_operator(n, qargs, k) @ rho @ full_operator(n, qargs, k).conj().T for k in kraus)
    return rho


def replay(n: int, device: Any) -> tuple[Any, float, float]:
    """The program on device with JAX, embedding operators as dense matrices (adequate at n = 3)."""
    import jax
    import jax.numpy as jnp

    operators = [
        jax.device_put(np.stack([full_operator(n, qargs, k) for k in kraus]).astype(np.complex64), device)
        for qargs, kraus in program()
    ]
    rho0 = jax.device_put(np.eye(2**n, dtype=np.complex64)[:, :1] @ np.eye(2**n, dtype=np.complex64)[:1], device)
    highest = jax.lax.Precision.HIGHEST

    @jax.jit
    def evolve(rho: Any, ops: list[Any]) -> Any:
        for kraus in ops:
            rho = jnp.sum(
                jnp.matmul(
                    jnp.matmul(kraus, rho, precision=highest), jnp.conj(jnp.swapaxes(kraus, 1, 2)), precision=highest
                ),
                axis=0,
            )
        return rho

    start = time.perf_counter()
    result = evolve(rho0, operators).block_until_ready()
    cold = time.perf_counter() - start
    start = time.perf_counter()
    result = evolve(rho0, operators).block_until_ready()
    warm = time.perf_counter() - start
    return result, cold, warm


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out: dict[str, Any] = {"schema": "tpu-probe-v1", "python": platform.python_version()}
    versions: dict[str, str | None] = {}
    for name in ("jax", "jaxlib", "libtpu", "libtpu-nightly", "jax-cuda12-plugin"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    out["versions"] = versions
    try:
        import jax
    except ImportError as failure:
        out["jax_import"] = f"{type(failure).__name__}: {failure}"
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
        return 0
    out["default_backend"] = jax.default_backend()
    out["devices"] = [
        {"platform": d.platform, "kind": getattr(d, "device_kind", None), "id": d.id} for d in jax.devices()
    ]
    try:
        tpus = jax.devices("tpu")
        out["tpu_devices"] = [str(d) for d in tpus]
    except RuntimeError as failure:
        tpus = []
        out["tpu_devices"] = f"RuntimeError: {failure}"
    if tpus:
        n = 3
        result, cold, warm = replay(n, tpus[0])
        error = float(np.max(np.abs(np.asarray(result) - reference(n))))
        out["replay"] = {
            "qubits": n,
            "result_platforms": sorted({d.platform for d in result.devices()}),
            "max_abs_error_vs_numpy_complex128": error,
            "cold_seconds": round(cold, 4),
            "warm_seconds": round(warm, 6),
        }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(out), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
