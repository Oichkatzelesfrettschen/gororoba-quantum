"""Sweep every least-squares backend of fp_backends.py over its own settings, one capped child per run.

Each configuration runs in a child process under a memory cap, serially, REPEATS times; precision is deterministic per
configuration, and the fastest solve of the repeats is its time. The cap is a systemd user scope
(`-p MemoryMax=... -p MemorySwapMax=0`) where a probe reads the limits back from the scope's cgroup, otherwise
RLIMIT_AS on Linux and macOS, and nothing on native Windows; its size is min(8 GiB, 0.6 x physical memory). Thread and
worker counts follow the host: 1, 2, 4, ... up to the CPU count, plus the CPU count itself, never above it. A
configuration the host cannot run (x87 rows off x86, quaddtype rows without the wheel or with QuadBLAS disabled) is
written as a row with a `skipped` reason. Each row carries the host record of fp_host.py, the memory-cap record, the
load average before each run and the five input digests of the ensemble producer, so rows from different hosts
compare.

usage: "$PYTHON" fp_sweep.py fp-inputs.npz sweep.jsonl [REPEATS] --host-label LABEL
           [--quick] [--idle-wait] [--idle-timeout S] [--cap auto|systemd|rlimit|none] [--timeout S]
           [--only SUBSTRING] [--dry-run]
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import signal
import subprocess
import sys
import tempfile
from collections.abc import Iterable
from pathlib import Path
from typing import Any, NamedTuple

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "gororoba_quantum"))

import fp_host  # noqa: E402

from parallel import workers  # noqa: E402

QUICK_THREADS = 4


class Config(NamedTuple):
    label: str
    selector: str
    env: dict[str, str]
    needs: str | None  # "+"-joined capabilities of the configuration: "x87", "quad", "quadblas" or "scipy"


def blas_env(threads: int) -> dict[str, str]:
    """The BLAS thread variables of one row: OpenBLAS everywhere, Accelerate's variable where macOS reads it."""
    out = {"OPENBLAS_NUM_THREADS": str(threads)}
    if sys.platform == "darwin":
        out["VECLIB_MAXIMUM_THREADS"] = str(threads)
    return out


def configs(cpus: int, quick: bool) -> list[Config]:
    """Every configuration of the sweep for a host with cpus usable CPUs. The full grid sweeps each thread-like axis
    over the ladder 1, 2, 4, ... cpus; quick keeps one thread count (min(cpus, 4)) per backend family, one refinement
    step count (2) and arb at 128 bits."""
    ladder = [min(cpus, QUICK_THREADS)] if quick else fp_host.thread_ladder(cpus)
    single = blas_env(1)
    out: list[Config] = []
    for th in ladder:
        out.append(Config(f"float64 pinv, OpenBLAS threads {th}", "pinv", blas_env(th), None))
        out.append(Config(f"float64 numpy lstsq, OpenBLAS threads {th}", "QR lstsq", blas_env(th), None))
    for driver, th in itertools.product(("gelsd", "gelsy", "gelss"), ladder):
        env = {**blas_env(th), "FP_LSTSQ_DRIVER": driver}
        out.append(Config(f"float64 scipy lstsq {driver}, OpenBLAS threads {th}", "scipy", env, "scipy"))
    for steps in (2,) if quick else (1, 2, 3):
        env = {**single, "FP_REFINE_STEPS": str(steps)}
        out.append(Config(f"float64 pinv + {steps} x87 refinement steps", "refinement", env, "x87"))
    for w in ladder:
        env = {**single, "FP_WORKERS": str(w)}
        out.append(Config(f"x87 Householder, {w} worker processes", "x87 80-bit Householder", env, "x87"))
    out.append(Config("x87 normal equations (Cholesky)", "x87 80-bit normal", dict(single), "x87"))
    for backend, th in itertools.product(("sleef", "longdouble"), ladder):
        env = {**single, "FP_QUAD_BACKEND": backend, "FP_QUAD_THREADS": str(th)}
        needs = "quad+quadblas" if backend == "sleef" else "quad+quadblas+x87"
        stem = f"backend {backend}, QuadBLAS threads {th}"
        out.append(Config(f"binary128 Householder, {stem}", "binary128 quaddtype Householder", env, needs))
        out.append(Config(f"binary128 normal equations, {stem}", "binary128 normal", env, needs))
    for prec, th in itertools.product((128,) if quick else (64, 128, 192, 256), ladder):
        env = {**single, "FP_ARB_PREC": str(prec), "FP_FLINT_THREADS": str(th)}
        out.append(Config(f"arb normal equations, {prec} bits, FLINT threads {th}", "arb normal", env, None))
    return out


def skip_reason(config: Config, status: dict[str, str | None]) -> str | None:
    """The recorded reason a configuration cannot run on this host, or None."""
    for need in (config.needs or "").split("+"):
        if need and status.get(need):
            return status[need]
    return None


def child_environment(extra: dict[str, str]) -> dict[str, str]:
    env = {**os.environ, **extra}
    if sys.platform.startswith("linux"):
        env.setdefault("MALLOC_ARENA_MAX", "2")
        env.setdefault("GLIBC_TUNABLES", "glibc.rtld.optional_static_tls=4096")
    return env


def child_command(cap: dict, wall: int, inputs: str, out: Path, selector: str) -> list[str]:
    cmd = [sys.executable, "-u", str(HERE / "fp_backends.py"), inputs, str(out), "--backends", selector]
    if cap["mechanism"] != "systemd":
        return cmd
    scope = ["systemd-run", "--user", "--scope", "-q"]
    for prop in (f"MemoryMax={cap['bytes']}", "MemorySwapMax=0", f"RuntimeMaxSec={wall + 60}"):
        scope += ["-p", prop]
    return [*scope, *cmd]


def kill_tree(proc: subprocess.Popen) -> None:
    """Kill the child and every process it started: the process group on POSIX, taskkill /T on Windows."""
    if os.name == "posix":
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except OSError:
            proc.kill()
    else:
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True, check=False)
        proc.kill()


def run_one(inputs: str, selector: str, env: dict[str, str], cap: dict, wall: int, workdir: Path) -> dict:
    handle, name = tempfile.mkstemp(suffix=".json", dir=workdir)
    os.close(handle)
    out = Path(name)
    load = fp_host.load_average()
    preexec = fp_host.preexec_rlimit(cap["bytes"]) if cap["mechanism"] == "rlimit" else None
    proc = subprocess.Popen(
        child_command(cap, wall, inputs, out, selector),
        env=child_environment(env),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=os.name == "posix",
        preexec_fn=preexec,
    )
    try:
        stdout, stderr = proc.communicate(timeout=wall)
        returncode = proc.returncode
    except subprocess.TimeoutExpired:
        kill_tree(proc)
        stdout, stderr = proc.communicate()
        returncode = 124
    row: dict = {"load_before": load[0] if load else None, "load_average_before": load, "returncode": returncode}
    if returncode == 0 and out.exists() and out.stat().st_size:
        report = json.loads(out.read_text(encoding="utf-8"))
        backends = report["backends"]
        row["result"] = next(iter(backends.values())) if backends else {"error": "no backend matched"}
        row["reference_seconds"] = report["reference"]["solve_seconds"]
        row["knobs"] = report["knobs"]
    else:
        tail = fp_host.scrub((stderr or stdout)[-600:])
        row["result"] = {"error": tail or f"exit {returncode} with no output (timeout 124, signal 128+N)"}
    out.unlink(missing_ok=True)
    return row


def collect_row(config: Config, runs: Iterable[dict], waits: list[dict], repeats: int, common: dict) -> dict:
    runs = list(runs)
    ok = [r for r in runs if "error" not in r["result"]]
    row: dict = {
        "config": config.label,
        "env": config.env,
        "repeats": repeats,
        "load_before": [r["load_before"] for r in runs],
        "load_average_before": [r["load_average_before"] for r in runs],
        "returncodes": [r["returncode"] for r in runs],
        "failed_repeats": [
            {"returncode": r["returncode"], "error": r["result"]["error"]} for r in runs if "error" in r["result"]
        ],
        "idle_wait": waits or None,
        **common,
    }
    if ok:
        best = min(ok, key=lambda r: r["result"]["solve_seconds"])
        row.update(
            {
                "solve_seconds_min": best["result"]["solve_seconds"],
                "solve_seconds_all": [r["result"]["solve_seconds"] for r in ok],
                "knobs": best["knobs"],
                **{k: v for k, v in best["result"].items() if k not in ("seconds", "solve_seconds")},
            }
        )
    else:
        row["error"] = runs[0]["result"]["error"]
    return row


def parse(argv: list[str]) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", help="fp-inputs.npz written by fp_export.py")
    ap.add_argument("out", help="JSON-lines file; finished configurations are skipped on a rerun")
    ap.add_argument("repeats", nargs="?", type=int, default=2, help="runs per configuration (quick forces 1)")
    ap.add_argument("--host-label", required=True, help="hostname-free label recorded in every row")
    ap.add_argument("--quick", action="store_true", help="one thread count per backend family, one repeat")
    ap.add_argument("--idle-wait", action="store_true", help="start each run only below 0.5 x CPU count load")
    ap.add_argument("--idle-timeout", type=float, default=3600.0, help="seconds an idle wait may last before exit 3")
    ap.add_argument("--cap", choices=("auto", "systemd", "rlimit", "none"), default="auto")
    ap.add_argument("--timeout", type=int, default=900, help="wall seconds per run")
    ap.add_argument("--only", default=None, help="run only configurations whose label contains this text")
    ap.add_argument("--dry-run", action="store_true", help="print the grid, the skips and the cap, then exit")
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse(sys.argv[1:] if argv is None else argv)
    problem = fp_host.label_error(args.host_label)
    if problem:
        print(problem, file=sys.stderr)
        return 2
    try:
        import flint  # noqa: F401
    except ImportError as exc:
        print(f"python-flint is required (the arb reference runs in every child): {exc}", file=sys.stderr)
        return 2
    repeats = 1 if args.quick else args.repeats
    cpus = min(os.cpu_count() or 1, workers())
    inputs = str(Path(args.inputs).resolve())
    data = fp_host.load_inputs(inputs)
    digests = fp_host.input_digests(data)
    provenance = fp_host.provenance_of(data)
    producer = (provenance or {}).get("producer_inputs_sha256")
    status: dict[str, str | None] = {
        "x87": fp_host.x87_status(),
        "quad": fp_host.quad_status(),
        "quadblas": fp_host.quadblas_status(),
        "scipy": fp_host.scipy_status(),
    }
    cap = fp_host.choose_cap(args.cap)
    if cap.get("failed"):
        print(f"memory cap '{args.cap}' failed its probe: {cap['tried']}", file=sys.stderr)
        return 2
    host = fp_host.host_record(args.host_label)
    host["cpus_used"] = cpus
    host["thread_ladder"] = fp_host.thread_ladder(cpus)
    grid = [c for c in configs(cpus, args.quick) if args.only is None or args.only in c.label]
    common: dict[str, Any] = {
        "host": host,
        "mode": "quick" if args.quick else "full",
        "cap": cap,
        "inputs_sha256": digests,
        "inputs_provenance": {
            "npz": provenance,
            "matches_producer_digests": None if producer is None else producer == digests,
        },
    }
    print(
        f"host {args.host_label}: {cpus} CPUs, ladder {host['thread_ladder']}, cap {cap['mechanism']} "
        f"{cap['bytes'] // fp_host.MIB} MiB (enforced {cap['enforced']}), {len(grid)} configurations, "
        f"{repeats} repeat(s)",
        flush=True,
    )
    for need, reason in status.items():
        if reason:
            print(f"skip {need} rows: {reason}", flush=True)
    if args.dry_run:
        for c in grid:
            print(c.label, f"SKIP: {skip_reason(c, status)}" if skip_reason(c, status) else "", flush=True)
        return 0
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # A row counts as finished only for its own host and mode, and a skipped row is measured again once its
    # capability is present.
    key = (host["label"], common["mode"])
    done = set()
    if out_path.exists():
        rows = [json.loads(line) for line in out_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        done = {
            row["config"]
            for row in rows
            if "skipped" not in row and ((row.get("host") or {}).get("label"), row.get("mode")) == key
        }
    with tempfile.TemporaryDirectory(prefix="fp-sweep-") as tmp, out_path.open("a", encoding="utf-8") as sink:
        for config in grid:
            if config.label in done:
                continue
            reason = skip_reason(config, status)
            if reason:
                sink.write(json.dumps({"config": config.label, "env": config.env, "skipped": reason, **common}) + "\n")
                sink.flush()
                print(config.label, "-> skipped:", reason[:80], flush=True)
                continue
            runs, waits = [], []
            for _ in range(repeats):
                if args.idle_wait:
                    wait = fp_host.wait_for_idle(os.cpu_count() or 1, args.idle_timeout, log=print)
                    waits.append(wait)
                    if wait["supported"] and not wait["reached"]:
                        print(f"load stayed above {wait['threshold']:g}; stopping, rerun resumes", flush=True)
                        return 3
                runs.append(run_one(inputs, config.selector, config.env, cap, args.timeout, Path(tmp)))
            row = collect_row(config, runs, waits, repeats, common)
            sink.write(json.dumps(row) + "\n")
            sink.flush()
            print(
                config.label,
                "->",
                row.get("solve_seconds_min"),
                row.get("bits_correct_on_scores"),
                row.get("error", "")[:80],
                flush=True,
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
