"""Wall-clock rows of the exact branching ghost sweep on one host, each row's laws held against numpy's.

Every row sweeps every audited run at the full (c, r) grid through
scripts/ghost_error_scale_branching.py ``sweep_runs``:

- ``numpy``: complex128 over the process pool, the reference;
- ``torch-cuda-complex128`` and ``torch-cuda-complex64``: plans built in the
  pool, then uploaded one group at a time, evolved and sampled on the GPU;
- with two or more GPUs, ``process-complex128``, one sweep process over
  every run with every worker, and ``split-complex128``, one sweep process
  per GPU (CUDA_VISIBLE_DEVICES) over half the runs, balanced by isa.qpy
  bytes, each with half the workers. Both time interpreter start, imports,
  warmup and the sweep, from the first start to the last exit.

Prediction for the split row: preparation and export are CPU work, and the
two processes share the host's CPUs, so they finish no sooner than one
process, within 5 percent (split wall >= 0.95 of the process wall).

``--require-gpu NAME --gpus N`` runs before any row: torch must list N CUDA
devices whose names contain NAME and finish a complex128 matmul on each
within GPU_TOLERANCE of numpy. Otherwise the entry writes the failure to
``--out`` and exits 3, so a kernel that lands without its GPUs stops before
it times the CPU.

Each row records its wall seconds, the sweep's phase seconds, the warmup,
the load averages and nvidia-smi readings before and after, and per run the
best points of both estimators and the largest entry difference between the
row's laws and numpy's. The record is rewritten after every row, so a
cut-off kernel keeps each finished row. ``--check FILE...`` recomputes every
derived field from the raw ones and requires the complex128 rows to agree
with numpy within LAW_TOLERANCE["complex128"].
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ghost_error_scale_branching as sweep  # noqa: E402
import ghost_run  # noqa: E402
import numpy as np  # noqa: E402

import aer_resources  # noqa: E402
import branch_dm  # noqa: E402
import parallel  # noqa: E402

SCHEMA = "ghost-branching-benchmark-v1"
LAW_TOLERANCE = {"complex128": 1e-10, "complex64": 1e-6}
GPU_TOLERANCE = 1e-10
SPLIT_PREDICTION = 0.95
# environment() adds the installed GPU Aer build and its CUDA distributions.
DISTRIBUTIONS = ("numpy", "scipy", "qiskit", "qiskit-aer", "torch")
require = ghost_run.require


def nvidia_smi() -> list[dict[str, str]] | None:
    """Per GPU: index, name, utilization, memory used and total, driver; None without nvidia-smi."""
    fields = "index,name,utilization.gpu,memory.used,memory.total,driver_version"
    try:
        out = subprocess.run(
            ["nvidia-smi", f"--query-gpu={fields}", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    except OSError, subprocess.CalledProcessError:
        return None
    names = fields.split(",")
    return [dict(zip(names, (v.strip() for v in line.split(",")), strict=True)) for line in out.splitlines() if line]


def reading() -> dict[str, Any]:
    return {
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "loadavg": list(os.getloadavg()),
        "gpus": nvidia_smi(),
    }


def host() -> dict[str, Any]:
    """The machine and the package versions the rows ran under."""
    model = None
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.is_file():
        model = next(
            (
                line.split(":", 1)[1].strip()
                for line in cpuinfo.read_text().splitlines()
                if line.startswith("model name")
            ),
            None,
        )
    versions: dict[str, str | None] = {}
    for name in (*DISTRIBUTIONS, *aer_resources.gpu_aer_distributions()):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    torch = branch_dm.load_torch()
    gpus = nvidia_smi()
    return {
        "python": platform.python_version(),
        "cpu_model": model,
        "available_cpus": parallel.available_cpus(),
        "workers": parallel.workers(),
        "versions": versions,
        "torch_cuda": None if torch is None else torch.version.cuda,
        "driver": gpus[0]["driver_version"] if gpus else None,
    }


def gpu_check(name: str, count: int) -> dict[str, Any]:
    """torch's CUDA devices and a complex128 matmul on each against numpy; failures empty when all hold."""
    failures: list[str] = []
    torch = branch_dm.load_torch()
    devices: list[str] = []
    gaps: list[float] = []
    if torch is None:
        failures.append("torch is not importable")
    elif not torch.cuda.is_available():
        failures.append("torch.cuda.is_available() is False")
    else:
        devices = [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]
        if len(devices) < count:
            failures.append(f"torch lists {len(devices)} CUDA devices; {count} required")
        for i, device in enumerate(devices):
            if name not in device:
                failures.append(f"cuda:{i} is {device!r}, not {name!r}")
            rng = np.random.default_rng(i)
            a = rng.standard_normal((64, 64)) + 1j * rng.standard_normal((64, 64))
            on = torch.as_tensor(a, device=f"cuda:{i}")
            gaps.append(float(np.max(np.abs((on @ on).cpu().numpy() - a @ a))))
            if gaps[-1] > GPU_TOLERANCE:
                failures.append(f"cuda:{i} complex128 matmul differs from numpy by {gaps[-1]}")
    return {"name": name, "count": count, "devices": devices, "matmul_gap": gaps, "failures": failures}


def best_points(result: dict[str, Any]) -> dict[str, Any]:
    if "skipped" in result:
        return {"skipped": result["skipped"]}
    return {"best": result["best"], "sampled_best": result["sampled_best"]}


def law_gaps(laws: dict[tuple[str, str], np.ndarray], reference: dict[tuple[str, str], np.ndarray]) -> dict[str, float]:
    """Per run, the largest entry difference between the row's laws and the reference's."""
    require(set(laws) == set(reference), "a row's groups differ from the numpy row's")
    gaps: dict[str, float] = {}
    for key, law in laws.items():
        gap = float(np.max(np.abs(np.asarray(law, dtype=float) - reference[key])))
        gaps[key[0]] = max(gaps.get(key[0], 0.0), gap)
    return gaps


def in_process_row(
    name: str, runs: list[str], index: dict[str, Any], engine: str, dtype: str
) -> tuple[dict[str, Any], dict[tuple[str, str], np.ndarray], list[dict[str, Any]]]:
    device = "cpu" if engine == "numpy" else "cuda"
    warm = sweep.warmup(sweep.make_backend(engine, device, dtype))
    laws: dict[tuple[str, str], np.ndarray] = {}
    before = reading()
    clock = time.perf_counter()
    results, seconds = sweep.sweep_runs(runs, index, engine, device, dtype, laws=laws)
    wall = time.perf_counter() - clock
    row = {
        "row": name,
        "engine": engine,
        "device": device,
        "dtype": dtype,
        "workers": parallel.workers(),
        "warmup_seconds": warm,
        "wall_seconds": round(wall, 3),
        "seconds": seconds,
        "before": before,
        "after": reading(),
        "runs": {result["run"]: best_points(result) for result in results},
    }
    return row, laws, results


def halves(runs: list[str]) -> list[list[str]]:
    """runs over two processes, largest isa.qpy first onto the lighter half."""
    sizes = {run: (ROOT / run / "isa.qpy").stat().st_size if (ROOT / run / "isa.qpy").is_file() else 0 for run in runs}
    out: list[list[str]] = [[], []]
    loads = [0, 0]
    for run in sorted(runs, key=lambda r: (-sizes[r], r)):
        j = 0 if loads[0] <= loads[1] else 1
        out[j].append(run)
        loads[j] += sizes[run]
    return [sorted(half) for half in out]


def process_row(
    name: str, groups: list[tuple[list[str], str | None, int]], scratch: Path
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    """Sweep processes started together, one per (runs, CUDA_VISIBLE_DEVICES, workers); wall to the last exit."""
    before = reading()
    clock = time.perf_counter()
    procs = []
    for k, (runs, visible, workers) in enumerate(groups):
        env = dict(os.environ, GOROROBA_WORKERS=str(workers))
        if visible is not None:
            env["CUDA_VISIBLE_DEVICES"] = visible
        out = scratch / f"{name}-{k}.json"
        argv = [sys.executable, "-B", str(ROOT / "scripts/ghost_error_scale_branching.py"), "--runs", ",".join(runs)]
        argv += ["--engine", "torch", "--device", "cuda", "--dtype", "complex128", "--out", str(out)]
        procs.append(
            (out, subprocess.Popen(argv, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True))
        )
    records = {}
    processes = []
    for out, proc in procs:
        _, stderr = proc.communicate()
        require(proc.returncode == 0, f"{name}: a sweep process exited {proc.returncode}: {stderr[-1500:]}")
        record = json.loads(out.read_text(encoding="utf-8"))
        processes.append(
            {
                "seconds": record["seconds"],
                "warmup_seconds": record["warmup_seconds"],
                "runs": [r["run"] for r in record["runs"]],
            }
        )
        records.update({r["run"]: r for r in record["runs"]})
    wall = time.perf_counter() - clock
    row = {
        "row": name,
        "engine": "torch",
        "device": "cuda",
        "dtype": "complex128",
        "processes": [dict(p, cuda_visible_devices=g[1], workers=g[2]) for p, g in zip(processes, groups, strict=True)],
        "wall_seconds": round(wall, 3),
        "before": before,
        "after": reading(),
        "runs": {run: best_points(record) for run, record in records.items()},
    }
    return row, records


def strip(result: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in result.items() if key != "seconds"}


def derive(record: dict[str, Any]) -> dict[str, Any]:
    """Every derived field of the record from its raw rows."""
    rows = {row["row"]: row for row in record["rows"]}
    reference = rows.get("numpy")
    derived: dict[str, Any] = {}
    for name, row in rows.items():
        out: dict[str, Any] = {}
        if reference is not None:
            out["speedup_vs_numpy"] = round(reference["wall_seconds"] / row["wall_seconds"], 3)
            out["best_matches_numpy"] = all(row["runs"][run] == reference["runs"][run] for run in reference["runs"])
        if "law_gap" in row:
            gap = max(row["law_gap"].values(), default=0.0)
            out["max_abs_law_minus_numpy"] = gap
            out["laws_agree"] = gap <= LAW_TOLERANCE[row["dtype"]]
        derived[name] = out
    if "split-complex128" in rows and "process-complex128" in rows:
        ratio = rows["split-complex128"]["wall_seconds"] / rows["process-complex128"]["wall_seconds"]
        derived["split-complex128"]["split_over_process"] = round(ratio, 3)
        derived["split-complex128"]["prediction_holds"] = ratio >= SPLIT_PREDICTION
    return derived


def check(path: Path) -> str:
    record = json.loads(path.read_text(encoding="utf-8"))
    require(record.get("schema") == SCHEMA, f"{path}: schema {record.get('schema')!r}")
    if record.get("gpu_check") is not None:
        require(not record["gpu_check"]["failures"], f"{path}: the GPU check failed: {record['gpu_check']['failures']}")
    require(record["derived"] == derive(record), f"{path}: derived fields differ from the raw rows")
    for name, out in record["derived"].items():
        row = next(r for r in record["rows"] if r["row"] == name)
        if row["dtype"] == "complex128" and "laws_agree" in out:
            require(out["laws_agree"], f"{path}: {name} laws differ from numpy by {out['max_abs_law_minus_numpy']}")
        require(
            row.get("records_equal_in_process", True),
            f"{path}: {name} records differ from the in-process complex128 row",
        )
        if row["device"] == "cuda":
            require(
                bool(record["gpu_check"] and record["gpu_check"]["devices"]), f"{path}: {name} names no CUDA device"
            )
    names = [row["row"] for row in record["rows"]]
    return f"{path}: {len(names)} rows ({', '.join(names)}), derived fields reproduced"


def write(out: Path, record: dict[str, Any]) -> None:
    record["derived"] = derive(record)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path)
    parser.add_argument("--runs", default="all", help="run directories, comma separated, or all")
    parser.add_argument("--rows", default="numpy,torch-cuda-complex128,torch-cuda-complex64,process,split")
    parser.add_argument("--require-gpu", metavar="NAME", help="stop unless torch lists --gpus devices named NAME")
    parser.add_argument("--gpus", type=int, default=1)
    parser.add_argument("--check", type=Path, nargs="+", metavar="FILE")
    args = parser.parse_args()
    if args.check:
        for path in args.check:
            print(check(path))
        return 0
    require(args.out is not None, "--out is required")
    record: dict[str, Any] = {"schema": SCHEMA, "host": host(), "gpu_check": None, "rows": []}
    record["prediction"] = {"split_over_process_at_least": SPLIT_PREDICTION}
    wanted = args.rows.split(",")
    gpu_rows = [row for row in wanted if row != "numpy"]
    if args.require_gpu:
        record["gpu_check"] = gpu_check(args.require_gpu, args.gpus)
        if record["gpu_check"]["failures"]:
            write(args.out, record)
            print(json.dumps(record["gpu_check"]), file=sys.stderr)
            return 3
    elif gpu_rows:
        torch = branch_dm.load_torch()
        count = torch.cuda.device_count() if torch is not None and torch.cuda.is_available() else 0
        record["gpu_check"] = gpu_check("", max(1, count))
        require(not record["gpu_check"]["failures"], f"GPU rows need CUDA: {record['gpu_check']['failures']}")
    index = json.loads(ghost_run.INDEX.read_text(encoding="utf-8"))
    runs = ghost_run.audited_runs() if args.runs == "all" else args.runs.split(",")
    record["runs"] = runs
    write(args.out, record)

    reference: dict[tuple[str, str], np.ndarray] = {}
    single: list[dict[str, Any]] = []
    if "numpy" in wanted:
        row, reference, _ = in_process_row("numpy", runs, index, "numpy", "complex128")
        record["rows"].append(row)
        write(args.out, record)
    for dtype in ("complex128", "complex64"):
        name = f"torch-cuda-{dtype}"
        if name not in wanted:
            continue
        row, laws, results = in_process_row(name, runs, index, "torch", dtype)
        if reference:
            row["law_gap"] = law_gaps(laws, reference)
        if dtype == "complex128":
            single = results
        record["rows"].append(row)
        write(args.out, record)
    gpus = len(record["gpu_check"]["devices"]) if record["gpu_check"] else 0
    if gpus >= 2 and ("process" in wanted or "split" in wanted):
        workers = parallel.workers()
        layouts: list[tuple[str, list[tuple[list[str], str | None, int]]]] = [
            ("process-complex128", [(runs, None, workers)]),
            ("split-complex128", [(half, str(k), max(1, workers // 2)) for k, half in enumerate(halves(runs))]),
        ]
        with tempfile.TemporaryDirectory() as scratch:
            for name, groups in layouts:
                if name.split("-")[0] not in wanted:
                    continue
                row, records = process_row(name, groups, Path(scratch))
                if single:
                    row["records_equal_in_process"] = all(strip(records[r["run"]]) == strip(r) for r in single)
                record["rows"].append(row)
                write(args.out, record)
    print(json.dumps({row["row"]: row["wall_seconds"] for row in record["rows"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
