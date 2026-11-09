"""Host probe for fp_sweep.py: memory cap, thread ladder, capability checks, load wait and per-row host metadata.

Everything here reads the running host and writes nothing. The host record carries no hostname, user name or path:
the label comes from the caller, and a library path from threadpoolctl or numpy's build configuration is dropped.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np

GIB = 1 << 30
MIB = 1 << 20
CAP_CEILING = 8 * GIB
CAP_FRACTION = 0.6
# RLIMIT_AS counts reserved address space, and OpenBLAS reserves its buffers at import: numpy fails to import below
# about 1 GiB of it, so the address-space cap never drops under this floor
RLIMIT_FLOOR = 2 * GIB
X86_MACHINES = frozenset({"x86_64", "amd64", "i386", "i686", "x86"})
PACKAGES = ("numpy", "scipy", "python-flint", "numpy-quaddtype", "threadpoolctl", "mpmath")


def label_error(label: str) -> str | None:
    """The reason a host label is unusable, or None: it must be non-empty and carry neither this host's name nor a
    path separator, so a published row never names the machine."""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", label):
        return "a host label starts with a letter or digit and holds only letters, digits, '.', '_' and '-'"
    names = {socket.gethostname().lower(), socket.gethostname().split(".")[0].lower()}
    if any(len(n) >= 3 and n in label.lower() for n in names):
        return "the host label contains this machine's hostname"
    return None


def scrub(text: str) -> str:
    """text with the home directory, the repository root, the temporary directory, the interpreter prefix and the
    hostname replaced by placeholders, for stderr tails kept in evidence rows."""
    root = Path(__file__).resolve().parents[3]
    pairs = [
        (str(root), "<repo>"),
        (str(Path.home()), "~"),
        (os.path.realpath(sys.prefix), "<prefix>"),
        (sys.prefix, "<prefix>"),
        (os.path.realpath(sys.base_prefix), "<base-prefix>"),
        (os.path.realpath(os.environ.get("TMPDIR", "/tmp")), "<tmp>"),
        (socket.gethostname(), "<host>"),
    ]
    for old, new in sorted(pairs, key=lambda p: -len(p[0])):
        if len(old) >= 3:
            text = text.replace(old, new).replace(old.replace("\\", "/"), new)
    return text


# ------------------------------------------------------------------ memory and threads


def mem_total_bytes() -> int | None:
    """Physical memory, bounded by the cgroup v2 limit when the process sits in a limited cgroup."""
    total: int | None = None
    if sys.platform == "win32":
        import ctypes

        class MemoryStatus(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        kernel32 = ctypes.WinDLL("kernel32")
        status = MemoryStatus()
        status.dwLength = ctypes.sizeof(MemoryStatus)
        if kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            total = int(status.ullTotalPhys)
    else:
        try:
            total = int(os.sysconf("SC_PHYS_PAGES")) * int(os.sysconf("SC_PAGE_SIZE"))
        except Exception:  # an unknown sysconf name raises ValueError, a failing call OSError
            total = None
        limit = Path("/sys/fs/cgroup/memory.max")
        try:
            text = limit.read_text(encoding="ascii").strip()
            if text.isdigit() and total is not None:
                total = min(total, int(text))
        except OSError:
            pass
    return total


def cap_bytes(total: int | None) -> int:
    """min(8 GiB, 0.6 x physical memory), rounded down to a whole MiB; 8 GiB when the memory is unknown."""
    if total is None:
        return CAP_CEILING
    return max(MIB, min(CAP_CEILING, int(CAP_FRACTION * total)) // MIB * MIB)


def thread_ladder(cpus: int) -> list[int]:
    """1, 2, 4, ... up to cpus, plus cpus itself when it is not a power of two; nothing above cpus."""
    out = {1}
    step = 2
    while step <= cpus:
        out.add(step)
        step *= 2
    out.add(max(1, cpus))
    return sorted(out)


# ------------------------------------------------------------------ load


def load_average() -> list[float] | None:
    """The 1, 5 and 15 minute load averages, or None where the OS has none (native Windows)."""
    if not hasattr(os, "getloadavg"):
        return None
    try:
        return [float(v) for v in os.getloadavg()]
    except OSError:
        return None


def wait_for_idle(cpus: int, timeout: float, poll: float = 15.0, log: Callable[[str], None] | None = None) -> dict:
    """Block until the 1 minute load average is below 0.5 x cpus. Returns the wait record; "reached" is False when
    timeout seconds passed first, and "supported" is False where the OS reports no load average."""
    threshold = 0.5 * cpus
    start = time.monotonic()
    if load_average() is None:
        return {"supported": False, "threshold": threshold, "waited_seconds": 0.0, "load_at_release": None}
    while True:
        load = load_average()
        waited = time.monotonic() - start
        if load is not None and load[0] < threshold:
            return {
                "supported": True,
                "reached": True,
                "threshold": threshold,
                "waited_seconds": waited,
                "load_at_release": load[0],
            }
        if waited >= timeout:
            return {
                "supported": True,
                "reached": False,
                "threshold": threshold,
                "waited_seconds": waited,
                "load_at_release": load[0] if load else None,
            }
        if log is not None and int(waited) % 60 < poll:
            log(f"idle wait: load {load[0] if load else None} >= {threshold:g}, waited {waited:.0f} s")
        time.sleep(poll)


# ------------------------------------------------------------------ capabilities


def x87_status() -> str | None:
    """None when this host does x87 80-bit arithmetic, else the reason the x87 configurations skip."""
    machine = platform.machine().lower()
    nmant = int(np.finfo(np.longdouble).nmant)
    if machine not in X86_MACHINES:
        return f"x87 80-bit arithmetic needs an x86 CPU; platform.machine() is {platform.machine()}"
    if nmant != 63:
        return f"numpy.longdouble is not 80-bit x87 (nmant {nmant}, expected 63)"
    return None


def quad_status() -> str | None:
    """None when numpy-quaddtype imports and builds its SLEEF dtype, else the reason the quaddtype rows skip."""
    try:
        import numpy_quaddtype as nq

        nq.QuadPrecDType(backend="sleef")
    except Exception as exc:  # any import or construction failure means no usable wheel
        return f"numpy-quaddtype unavailable: {type(exc).__name__}: {scrub(str(exc))[:200]}"
    return None


def scipy_status() -> str | None:
    try:
        import scipy.linalg  # noqa: F401
    except ImportError as exc:
        return f"scipy unavailable: {scrub(str(exc))[:200]}"
    return None


# ------------------------------------------------------------------ memory cap


def preexec_rlimit(nbytes: int) -> Callable[[], None]:
    """A preexec_fn that sets the child's RLIMIT_AS soft limit to nbytes (hard limit kept)."""

    def apply() -> None:
        import resource

        _, hard = resource.getrlimit(resource.RLIMIT_AS)
        resource.setrlimit(resource.RLIMIT_AS, (nbytes, hard))

    return apply


RLIMIT_PROBE = (
    "import mmap, resource, sys\n"
    "import numpy\n"
    "soft = resource.getrlimit(resource.RLIMIT_AS)[0]\n"
    "try:\n"
    "    mmap.mmap(-1, int(sys.argv[1]) + (256 << 20))\n"
    "    refused = False\n"
    "except (OSError, ValueError, MemoryError):\n"
    "    refused = True\n"
    "print(soft, refused)\n"
)


def probe_rlimit(nbytes: int) -> dict:
    """Run a child under RLIMIT_AS = nbytes: report whether the soft limit took and whether an anonymous mapping
    256 MiB above the cap is refused (an accepted but unenforced limit leaves it mapped)."""
    if os.name != "posix":
        return {"ok": False, "reason": "RLIMIT_AS needs a POSIX host"}
    try:
        proc = subprocess.run(
            [sys.executable, "-c", RLIMIT_PROBE, str(nbytes)],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
            preexec_fn=preexec_rlimit(nbytes),
        )
    except Exception as exc:  # setrlimit refusal surfaces here as SubprocessError
        return {"ok": False, "reason": f"RLIMIT_AS child failed: {type(exc).__name__}: {scrub(str(exc))[:200]}"}
    parts = proc.stdout.split()
    if proc.returncode != 0 or len(parts) != 2:
        return {"ok": False, "reason": f"RLIMIT_AS probe exit {proc.returncode}: {scrub(proc.stderr)[-200:]}"}
    took, refused = int(parts[0]) == nbytes, parts[1] == "True"
    if not took:
        return {"ok": False, "reason": f"RLIMIT_AS soft limit reads {parts[0]}, not {nbytes}"}
    return {
        "ok": True,
        "enforced": refused,
        "reason": "setrlimit accepted; a mapping above the cap is " + ("refused" if refused else "not refused"),
    }


SYSTEMD_PROBE = (
    'p=$(sed -n "s/^0:://p" /proc/self/cgroup); '
    'echo "$(cat "/sys/fs/cgroup$p/memory.max") $(cat "/sys/fs/cgroup$p/memory.swap.max")"'
)


def probe_systemd(nbytes: int) -> dict:
    """Run a trial user scope with MemoryMax and MemorySwapMax=0 and read the limits back from the scope's cgroup:
    systemd accepts the properties without a delegated memory controller, so only the readback proves the cap."""
    if not sys.platform.startswith("linux"):
        return {"ok": False, "reason": "systemd scopes need Linux"}
    if shutil.which("systemd-run") is None:
        return {"ok": False, "reason": "systemd-run is not installed"}
    cmd = ["systemd-run", "--user", "--scope", "-q", "-p", f"MemoryMax={nbytes}", "-p", "MemorySwapMax=0"]
    try:
        proc = subprocess.run(
            [*cmd, "sh", "-c", SYSTEMD_PROBE],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
            stdin=subprocess.DEVNULL,
        )
    except Exception as exc:
        return {"ok": False, "reason": f"systemd-run failed: {type(exc).__name__}: {scrub(str(exc))[:200]}"}
    if proc.returncode != 0:
        return {"ok": False, "reason": f"no user systemd manager answers: {scrub(proc.stderr.strip())[-200:]}"}
    parts = proc.stdout.split()
    if parts != [str(nbytes), "0"]:
        return {"ok": False, "reason": f"scope accepted but memory.max/memory.swap.max read {parts} (not enforced)"}
    return {"ok": True, "enforced": True, "reason": "scope memory.max and memory.swap.max read back as requested"}


def choose_cap(request: str) -> dict:
    """The memory-cap mechanism for this host: request is auto, systemd, rlimit or none. auto prefers a systemd user
    scope (probed by readback), then RLIMIT_AS on Linux and macOS, and runs uncapped on native Windows."""
    total = mem_total_bytes()
    nbytes = cap_bytes(total)
    record: dict[str, Any] = {"requested": request, "bytes": nbytes, "mem_total_bytes": total, "tried": {}}
    order = {"auto": ["systemd", "rlimit"], "systemd": ["systemd"], "rlimit": ["rlimit"], "none": []}[request]
    for mech in order:
        limit = max(nbytes, RLIMIT_FLOOR) if mech == "rlimit" else nbytes
        result = probe_systemd(limit) if mech == "systemd" else probe_rlimit(limit)
        record["tried"][mech] = result
        if result["ok"]:
            record.update(mechanism=mech, enforced=result["enforced"], swap_max_zero=mech == "systemd")
            record.update(nominal_bytes=nbytes, bytes=limit)
            return record
    record.update(mechanism="none", enforced=False, swap_max_zero=False, nominal_bytes=nbytes)
    if request in ("systemd", "rlimit"):
        record["failed"] = True
    elif request == "auto":
        record["reason"] = (
            "native Windows has no per-process address-space or cgroup limit here; documented uncapped run"
            if sys.platform == "win32"
            else "no mechanism passed its probe"
        )
    else:
        record["reason"] = "uncapped run requested"
    return record


# ------------------------------------------------------------------ host record


def cpu_model() -> str:
    machine = platform.machine()
    if sys.platform.startswith("linux"):
        try:
            for line in Path("/proc/cpuinfo").read_text(encoding="utf-8", errors="replace").splitlines():
                key = line.split(":", 1)[0].strip().lower()
                if key in ("model name", "hardware", "cpu model") and ":" in line:
                    return line.split(":", 1)[1].strip()
        except OSError:
            pass
        if shutil.which("lscpu"):
            out = subprocess.run(["lscpu"], capture_output=True, text=True, check=False, env={"LC_ALL": "C"}).stdout
            for line in out.splitlines():
                if line.startswith("Model name:"):
                    return line.split(":", 1)[1].strip()
    elif sys.platform == "darwin":
        out = subprocess.run(
            ["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True, check=False
        ).stdout.strip()
        if out:
            return out
    elif sys.platform == "win32":
        import winreg

        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as key:
                return str(winreg.QueryValueEx(key, "ProcessorNameString")[0]).strip()
        except OSError:
            pass
    return platform.processor() or machine


def os_info() -> dict:
    out: dict[str, Any] = {"system": platform.system(), "release": platform.release()}
    if sys.platform.startswith("linux"):
        out["wsl"] = "microsoft" in platform.release().lower()
        try:
            for line in Path("/etc/os-release").read_text(encoding="utf-8").splitlines():
                if line.startswith("PRETTY_NAME="):
                    out["distribution"] = line.split("=", 1)[1].strip().strip('"')
        except OSError:
            pass
    elif sys.platform == "darwin":
        out["mac_ver"] = platform.mac_ver()[0]
    elif sys.platform == "win32":
        out["win32_ver"] = " ".join(v for v in platform.win32_ver()[:2] if v)
    return out


def cpu_flags() -> dict:
    """The CPU feature subset numpy's runtime dispatch sees (numpy.__cpu_features__), where numpy names it."""
    features: dict[str, bool] = {}
    for modname in ("numpy._core._multiarray_umath", "numpy.core._multiarray_umath"):
        try:
            module = __import__(modname, fromlist=["__cpu_features__"])
            features = dict(module.__cpu_features__)
            break
        except Exception:  # a numpy without the private module or attribute
            continue
    if not features:
        return {"source": "unavailable", "flags": None}
    pick = lambda *names: any(features.get(n, False) for n in names)  # noqa: E731
    return {
        "source": "numpy.__cpu_features__",
        "flags": {
            "avx2": pick("AVX2"),
            "avx512f": pick("AVX512F"),
            "avx512dq": pick("AVX512DQ"),
            "avx512vl": pick("AVX512VL"),
            "fma": pick("FMA3", "NEON_VFPV4"),
            "neon": pick("NEON"),
            "asimd": pick("ASIMD"),
            "sse3": pick("SSE3"),
        },
    }


def numpy_info() -> dict:
    """numpy's SIMD baseline and dispatch lists and the BLAS it was built against (names and versions only)."""
    out: dict[str, Any] = {"version": np.__version__}
    try:
        config = np.show_config(mode="dicts")
    except TypeError:
        return {**out, "simd": None, "build_blas": None, "note": "numpy.show_config has no dicts mode"}
    if not isinstance(config, dict):
        return {**out, "simd": None, "build_blas": None}
    simd = config.get("SIMD Extensions", {})
    out["simd"] = {
        "baseline": list(simd.get("baseline", [])),
        "found": list(simd.get("found", [])),
        "not_found": list(simd.get("not found", [])),
    }
    blas = config.get("Build Dependencies", {}).get("blas", {})
    out["build_blas"] = {k: blas.get(k) for k in ("name", "version", "openblas configuration")}
    return out


def blas_runtime() -> dict:
    """The BLAS and OpenMP libraries loaded into this process, through threadpoolctl; the library path is dropped.
    Call after numpy and scipy are imported, since threadpoolctl lists only libraries already mapped."""
    try:
        from threadpoolctl import threadpool_info
    except ImportError:
        return {"threadpoolctl": None, "libraries": None, "reason": "threadpoolctl is not installed"}
    keep = ("user_api", "internal_api", "version", "architecture", "threading_layer", "num_threads")
    libs = [{k: entry.get(k) for k in keep} for entry in threadpool_info()]
    return {"threadpoolctl": importlib.metadata.version("threadpoolctl"), "libraries": libs}


def package_versions() -> dict:
    out: dict[str, str | None] = {}
    for name in PACKAGES:
        try:
            out[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            out[name] = None
    return out


def flint_info() -> dict:
    import flint

    return {"python_flint": flint.__version__, "flint": getattr(flint, "__FLINT_VERSION__", None)}


def host_record(label: str) -> dict:
    """The per-row host description. Import scipy first so threadpoolctl sees its BLAS too."""
    try:
        import scipy.linalg  # noqa: F401
    except ImportError:
        pass
    cpus = os.cpu_count() or 1
    return {
        "label": label,
        "machine": platform.machine(),
        "os": os_info(),
        "cpu_model": cpu_model(),
        "cpu_count": cpus,
        "cpu_flags": cpu_flags(),
        "python": {"version": platform.python_version(), "implementation": platform.python_implementation()},
        "numpy": numpy_info(),
        "blas": blas_runtime(),
        "flint": flint_info(),
        "packages": package_versions(),
        "longdouble_nmant": int(np.finfo(np.longdouble).nmant),
    }


# ------------------------------------------------------------------ input digests


def sha256_array(array: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def input_digests(d: dict) -> dict[str, str]:
    """The five `arithmetic.inputs_sha256` digests of the ensemble producer (prediction_balls in
    scripts/ascella_cz_ensemble_case.py), rebuilt from the arrays of fp-inputs.npz: the producer hashes the complex
    ideal Choi vector (the npz keeps its real part) and the point rates stacked with the transposed replicates."""
    return {
        "design_matrix": sha256_array(d["a"]),
        "rate_observables": sha256_array(d["obs"]),
        "hermitian_basis": sha256_array(d["basis"]),
        "ideal_choi_vector": sha256_array(np.asarray(d["v"], dtype=np.complex128)),
        "observed_rate_columns": sha256_array(np.column_stack([d["f"], d["batch"].T])),
    }


def load_inputs(path: str) -> dict:
    with np.load(path) as data:
        return {k: data[k] for k in data.files}


def provenance_of(d: dict) -> dict | None:
    """The exporter record stored in the npz by fp_export.py, if present."""
    raw = d.get("provenance")
    return json.loads(str(raw)) if raw is not None else None
