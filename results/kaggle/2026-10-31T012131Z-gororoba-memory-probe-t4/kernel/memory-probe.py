"""Kaggle accelerator memory probe: CPU-only numpy/scipy, VRAM-only CuPy, managed-memory oversubscription past VRAM,
and pageable host memory accessed from the GPU when the device reports HMM support. Writes probe.json."""
import json, os, subprocess, sys, time

out = {}
def mem_available_gib():
    """Headroom under the container's cgroup memory limit; /proc/meminfo reports the host and overstates it."""
    try:
        lim = open("/sys/fs/cgroup/memory.max").read().strip()
        cur = int(open("/sys/fs/cgroup/memory.current").read())
        if lim != "max":
            return (int(lim) - cur) / 2**30
    except OSError:
        pass
    for line in open("/proc/meminfo"):
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) / 2**20
    return 0.0
def save():
    json.dump(out, open("/kaggle/working/probe.json", "w"), indent=1)

out["nvidia_smi"] = subprocess.run(["nvidia-smi", "-q"], capture_output=True, text=True).stdout
out["mem_total_gib"] = round(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 2**30, 2)
out["cpu_count"] = os.cpu_count()

import numpy as np, scipy, scipy.linalg
rng = np.random.default_rng(20261031)
a = rng.standard_normal((4096, 4096)); b = rng.standard_normal((4096, 4096))
t = time.time(); c = a @ b; out["cpu_matmul_4096_s"] = round(time.time() - t, 3)
t = time.time(); scipy.linalg.lu_factor(a); out["cpu_lu_4096_s"] = round(time.time() - t, 3)
out["cpu_versions"] = {"numpy": np.__version__, "scipy": scipy.__version__}
save()

try:
    import cupy as cp
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "cupy-cuda12x"], check=False)
    import cupy as cp
dev = cp.cuda.Device(0)
free, total = cp.cuda.runtime.memGetInfo()
out["gpu"] = {"name": cp.cuda.runtime.getDeviceProperties(0)["name"].decode(), "vram_total_gib": round(total / 2**30, 2),
              "vram_free_gib": round(free / 2**30, 2), "cupy": cp.__version__}
# cudaDevAttrPageableMemoryAccess = 88, cudaDevAttrConcurrentManagedAccess = 89
out["gpu"]["pageable_memory_access"] = cp.cuda.runtime.deviceGetAttribute(88, 0)
out["gpu"]["concurrent_managed_access"] = cp.cuda.runtime.deviceGetAttribute(89, 0)
ga = cp.asarray(a, dtype=cp.float32); gb = cp.asarray(b, dtype=cp.float32)
ga @ gb; dev.synchronize()
t = time.time(); ga @ gb; dev.synchronize(); out["gpu_matmul_4096_f32_s"] = round(time.time() - t, 4)
del ga, gb; cp.get_default_memory_pool().free_all_blocks()
# VRAM-only ceiling: grow device allocations in 1 GiB steps until refusal.
blocks = []
try:
    while True:
        blocks.append(cp.empty(2**28, dtype=cp.float32))
except cp.cuda.memory.OutOfMemoryError:
    pass
out["vram_alloc_ceiling_gib"] = len(blocks)
del blocks; cp.get_default_memory_pool().free_all_blocks()
del a, b, c
save()

# Managed memory past VRAM: each size runs in its own process, so host backing freed at exit cannot leak into the next
# step; the guard requires cgroup headroom of the full array plus 2 GiB, since evicted managed pages live on the host.
STEP = r"""
import json, sys, time, cupy as cp
gib = int(sys.argv[1]); dev = cp.cuda.Device(0)
cp.cuda.set_allocator(cp.cuda.MemoryPool(cp.cuda.malloc_managed).malloc)
t = time.time(); x = cp.ones(gib * 2**28, dtype=cp.float32); dev.synchronize(); f = time.time() - t
t = time.time(); s = float(x.sum()); dev.synchronize(); u = time.time() - t
t = time.time(); x *= 2; s2 = float(x.sum()); dev.synchronize(); w = time.time() - t
print(json.dumps({"fill_s": round(f, 2), "sum_s": round(u, 2), "scale_sum_s": round(w, 2), "sum_ok": s == gib * 2**28 and s2 == 2 * s}))
"""
steps = []
out["managed_oversubscription"] = steps
out["cgroup_headroom_gib_before_managed"] = round(mem_available_gib(), 2)
for gib in (4, 8, 12, 14, 16, 18, 20, 22, 24, 26):
    head = mem_available_gib()
    if head < gib + 2:
        steps.append({"gib": gib, "skipped": f"cgroup headroom {head:.1f} GiB"}); save(); break
    r = subprocess.run([sys.executable, "-c", STEP, str(gib)], capture_output=True, text=True, timeout=1800)
    row = {"gib": gib, "rc": r.returncode, "headroom_gib_before": round(head, 1)}
    try:
        row.update(json.loads(r.stdout.strip().splitlines()[-1]))
    except (IndexError, ValueError):
        row["stderr"] = r.stderr[-300:]
    steps.append(row); save()
    if r.returncode != 0:
        break
cp.cuda.set_allocator(cp.get_default_memory_pool().malloc)
save()

# HMM: a kernel reads plain numpy (malloc) memory through its host pointer; valid only with pageable memory access.
if out["gpu"]["pageable_memory_access"]:
    h = np.ones(2**28, dtype=np.float32)
    mem = cp.cuda.UnownedMemory(h.ctypes.data, h.nbytes, h)
    view = cp.ndarray(h.shape, dtype=cp.float32, memptr=cp.cuda.MemoryPointer(mem, 0))
    t = time.time(); s = float(view.sum()); dev.synchronize()
    out["hmm_pageable"] = {"gib": 1, "sum_s": round(time.time() - t, 3), "sum_ok": s == 2**28}
else:
    out["hmm_pageable"] = "unsupported: cudaDevAttrPageableMemoryAccess = 0 (needs the open kernel module with HMM, or ATS)"
save()
print(json.dumps({k: v for k, v in out.items() if k != "nvidia_smi"}, indent=1))
