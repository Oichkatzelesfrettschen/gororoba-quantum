"""What the GPU entry environment holds, printed as one JSON line; kernel_main.gpu_interpreter runs it as the entry.

argv[1] is a JSON list of distribution names. The report gives each name's
installed version, the distributions whose files install the imported
qiskit_aer/__init__.py, Aer's available devices, numpy's build
configuration, and one seeded Bell circuit run on the GPU without and with
cuStateVec_enable, each with the device and cuStateVec_enable its result
metadata reports or the error it raised, and every sys.path entry outside
the venv, the standard library and this script's directory.
"""

from __future__ import annotations

import importlib.metadata
import json
import pathlib
import sys
import sysconfig
from typing import Any


def owners(module_file: str) -> list[str]:
    init = pathlib.Path(module_file).resolve()
    return sorted(
        {
            dist.metadata["Name"]
            for dist in importlib.metadata.distributions()
            for item in dist.files or ()
            if item.as_posix() == "qiskit_aer/__init__.py"
            and pathlib.Path(str(dist.locate_file(item))).resolve() == init
        }
    )


def foreign_paths() -> list[str]:
    """sys.path entries that are neither under the venv's prefix, the standard library, nor this script's directory."""
    stdlib = pathlib.Path(sysconfig.get_paths()["stdlib"]).resolve()
    allowed = {stdlib, stdlib / "lib-dynload", pathlib.Path(__file__).resolve().parent}
    prefix = pathlib.Path(sys.prefix).resolve()
    found = []
    for entry in sys.path:
        path = pathlib.Path(entry or ".").resolve()
        if path in allowed or path.is_relative_to(prefix) or path.suffix == ".zip" and not path.exists():
            continue
        found.append(entry)
    return found


def bell_runs() -> dict[str, dict[str, Any]]:
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator

    bell = QuantumCircuit(2)
    bell.h(0)
    bell.cx(0, 1)
    bell.measure_all()
    runs: dict[str, dict[str, Any]] = {}
    for label, options in (("gpu", {}), ("custatevec", {"cuStateVec_enable": True, "batched_shots_gpu": False})):
        try:
            result = AerSimulator(device="GPU", **options).run(bell, shots=256, seed_simulator=7).result()
        except Exception as error:  # a missing CUDA library or device raises here
            runs[label] = {"error": f"{type(error).__name__}: {error}"}
            continue
        metadata = result.results[0].metadata
        runs[label] = {
            "success": bool(result.success),
            "device": metadata.get("device"),
            "cuStateVec_enable": metadata.get("cuStateVec_enable"),
            "counts": dict(sorted(result.get_counts().items())),
        }
    return runs


def main() -> int:
    import numpy
    import qiskit_aer
    from qiskit_aer import AerSimulator

    installed: dict[str, str | None] = {}
    for name in json.loads(sys.argv[1]):
        try:
            installed[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            installed[name] = None
    report = {
        "python": sys.version.split()[0],
        "installed": installed,
        "qiskit_aer_version": qiskit_aer.__version__,
        "qiskit_aer_owners": owners(str(qiskit_aer.__file__)),
        "devices": list(AerSimulator().available_devices()),
        "foreign_paths": foreign_paths(),
        "numpy": json.loads(json.dumps(numpy.show_config(mode="dicts") or {}, default=str)),
        "runs": bell_runs(),
    }
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
