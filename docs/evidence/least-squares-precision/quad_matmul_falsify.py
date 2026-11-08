"""Falsification run for the numpy-quaddtype matmul defects on one machine, printed as one JSON object.

Each case multiplies small-integer matrices, whose products are exact in float64 and in binary128, so the float64
product is an exact oracle. A case passes when the quad product equals it exactly (or, for an empty inner dimension,
when it returns the zeros numpy returns). Contiguous copies of the same operands are the control: a defect is a
failing view case whose contiguous control passes.

usage: python quad_matmul_falsify.py
"""

from __future__ import annotations

import json
import os
import platform
import sys
from collections.abc import Callable

import numpy as np
import numpy_quaddtype as nq
from numpy_quaddtype import QuadPrecDType

Q = QuadPrecDType()


def cpu_model() -> str:
    try:
        with open("/proc/cpuinfo", encoding="utf-8") as handle:
            for line in handle:
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or platform.machine()


def optional(read: Callable[[], object]) -> object:
    """A build fact the wheel may not provide (the Windows wheel disables QuadBLAS), recorded rather than required."""
    try:
        return read()
    except Exception as exc:
        return f"{type(exc).__name__}: {exc}"


def check(left64: np.ndarray, right64: np.ndarray, left_q: np.ndarray, right_q: np.ndarray) -> dict[str, object]:
    """The quad product of the views and of their contiguous copies, each against the exact float64 product."""
    truth = left64 @ right64
    out: dict[str, object] = {
        "left": [list(left_q.shape), list(left_q.strides), bool(left_q.flags.c_contiguous)],
        "right": [list(right_q.shape), list(right_q.strides), bool(right_q.flags.c_contiguous)],
    }
    for label, (a, b) in {
        "view": (left_q, right_q),
        "contiguous": (np.ascontiguousarray(left_q), np.ascontiguousarray(right_q)),
    }.items():
        try:
            got = np.asarray(a @ b, dtype=np.float64)
            out[label] = bool(np.array_equal(got, truth))
            if not out[label]:
                out[f"{label}_first"] = [float(v) for v in np.ravel(got)[:3]]
                out["expected_first"] = [float(v) for v in np.ravel(truth)[:3]]
        except Exception as exc:  # the defect under test may raise
            out[label] = f"{type(exc).__name__}: {exc}"
    return out


BASE64 = np.arange(48.0).reshape(8, 6)
BASE_Q = BASE64.astype(Q)


CASES: dict[str, Callable[[np.ndarray], tuple[np.ndarray, np.ndarray]]] = {
    "column-slice vector @ sub-block (reported)": lambda m: (m[2:, 1], m[2:, 1:]),
    "sub-block.T @ column-slice vector": lambda m: (m[2:, 1:].T, m[2:, 1]),
    "row-reversed matrix @ matrix": lambda m: (m[::-1, :4], m[:4, ::-1]),
    "every-other-row vector @ matrix": lambda m: (m[::2, 0], m[::2, 1:]),
    "transpose @ matrix": lambda m: (m.T, m),
    "sub-block @ sub-block.T": lambda m: (m[1:5, 1:5], m[1:5, 1:5].T),
    "contiguous rows @ contiguous rows (control)": lambda m: (m[:6], np.ascontiguousarray(m[:6].T)),
}


def main() -> int:
    report: dict[str, object] = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
        "cpu": cpu_model(),
        "numpy": np.__version__,
        "numpy_quaddtype_file": os.path.dirname(nq.__file__),
        "quadblas": optional(nq.get_quadblas_version),
        "threads": optional(nq.get_num_threads),
        "cases": {},
    }
    for name, make in CASES.items():
        report["cases"][name] = check(*make(BASE64), *make(BASE_Q))  # type: ignore[index]
    empty = {}
    for label, (a, b) in {"vector (0,) @ (0, 2)": ((0,), (0, 2)), "matrix (3, 0) @ (0, 2)": ((3, 0), (0, 2))}.items():
        expected = np.ones(a) @ np.ones(b)
        try:
            got = np.ones(a, dtype=Q) @ np.ones(b, dtype=Q)
            empty[label] = bool(np.array_equal(np.asarray(got, dtype=np.float64), expected))
        except Exception as exc:
            empty[label] = f"{type(exc).__name__}: {exc}"
    report["empty_inner_dimension"] = empty
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
