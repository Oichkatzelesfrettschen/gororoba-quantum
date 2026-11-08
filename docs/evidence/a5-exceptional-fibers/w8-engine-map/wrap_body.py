"""Instrumented, non-editing wrapper around fiber_rank_v11.py.

Usage: wrap.py TAG OUTDIR [--tracemalloc] [--keep-blocks B,B] -- ENGINE_ARGS...
Imports the engine from ENGINE (path in env FIBER_ENGINE), patches module-level functions and Echelon.insert to mark
stages, samples RSS (this process, and the process tree including Singular children) every 0.5 s, resets the kernel
peak-RSS counter (VmHWM) at each stage start, and writes OUTDIR/TAG.stages.json, TAG.rss.tsv, TAG.inserts.json and the
engine's stdout JSON to TAG.json.
--keep-blocks drops rows inserted into every other character block (an invalid computation: a probe of block coupling).
"""
import importlib.util
import json
import os
import sys
import threading
import time
import tracemalloc

import psutil

tag, outdir = sys.argv[1], sys.argv[2]
rest = sys.argv[3:]
use_tm = "--tracemalloc" in rest
keep = None
if "--keep-blocks" in rest:
    i = rest.index("--keep-blocks")
    keep = {int(x) for x in rest[i + 1].split(",")}
    del rest[i : i + 2]
cache = None
if "--products-cache" in rest:
    i = rest.index("--products-cache")
    cache = rest[i + 1]
    del rest[i : i + 2]
use_split = "--split" in rest
if use_split:
    rest.remove("--split")
use_prof = "--cprofile" in rest
if use_prof:
    rest.remove("--cprofile")
stop_after = None
if "--stop-after" in rest:
    i = rest.index("--stop-after")
    stop_after = rest[i + 1]
    del rest[i : i + 2]
rest = [a for a in rest if a != "--tracemalloc"]
sep = rest.index("--")
engine_args = rest[sep + 1 :]
os.makedirs(outdir, exist_ok=True)

spec = importlib.util.spec_from_file_location("fiber_rank_v11", os.environ["FIBER_ENGINE"])
E = importlib.util.module_from_spec(spec)
sys.modules["fiber_rank_v11"] = E
spec.loader.exec_module(E)

proc = psutil.Process()
T0 = time.time()
state = {"phase": "start", "t": T0, "hwm0": 0}
stages = []  # dicts
phase_tree_peak: dict[str, int] = {}
lock = threading.Lock()


def vmhwm_kib() -> int:
    with open("/proc/self/status") as f:
        for ln in f:
            if ln.startswith("VmHWM"):
                return int(ln.split()[1])
    return 0


hwm_max: dict[str, int] = {}
self_rss_max: dict[str, int] = {}


def fold() -> int:
    """Fold the kernel peak-RSS counter into the running per-phase maximum (before every reset)."""
    v = vmhwm_kib()
    with lock:
        ph = state["phase"]
        hwm_max[ph] = max(hwm_max.get(ph, 0), v)
    return v


def reset_hwm() -> None:
    fold()
    try:
        with open("/proc/self/clear_refs", "w") as f:
            f.write("5")
    except OSError:
        pass


def tree_rss() -> int:
    tot = 0
    try:
        procs = [proc] + proc.children(recursive=True)
    except psutil.Error:
        procs = [proc]
    for p in procs:
        try:
            tot += p.memory_info().rss
        except psutil.Error:
            pass
    return tot


def set_phase(name: str) -> None:
    now = time.time()
    with lock:
        prev = state["phase"]
        rec = {
            "phase": prev,
            "start_s": round(state["t"] - T0, 2),
            "wall_s": round(now - state["t"], 2),
            "self_hwm_kib": max(hwm_max.get(prev, 0), vmhwm_kib()),
            "self_rss_sampled_max_kib": self_rss_max.get(prev, 0),
            "tree_peak_kib": phase_tree_peak.get(prev, 0) // 1024,
        }
        if use_tm:
            cur, peak = tracemalloc.get_traced_memory()
            rec["tracemalloc_peak_mib"] = round(peak / 2**20, 1)
            rec["tracemalloc_cur_mib"] = round(cur / 2**20, 1)
            tracemalloc.reset_peak()
        stages.append(rec)
        events.write(json.dumps({"stage": rec}) + "\n")
        events.flush()
        try:
            with open("/proc/self/clear_refs", "w") as cf:
                cf.write("5")
        except OSError:
            pass
        state["phase"], state["t"] = name, now


events = open(os.path.join(outdir, tag + ".events.jsonl"), "w")
rss_log = open(os.path.join(outdir, tag + ".rss.tsv"), "w")
rss_log.write("t_s\tphase\tself_rss_kib\ttree_rss_kib\tbytes_in_W_kib\n")
echelons: list = []
stop = threading.Event()


def sampler() -> None:
    while not stop.is_set():
        tr = tree_rss()
        ph = state["phase"]
        with lock:
            phase_tree_peak[ph] = max(phase_tree_peak.get(ph, 0), tr)
            self_rss_max[ph] = max(self_rss_max.get(ph, 0), proc.memory_info().rss // 1024)
        w = sum(getattr(e, "B").nbytes for e in echelons) // 1024
        rss_log.write(f"{time.time() - T0:.1f}\t{ph}\t{proc.memory_info().rss // 1024}\t{tr // 1024}\t{w}\n")
        rss_log.flush()
        stop.wait(0.5)


def wrap(name: str, enter: str, leave: str):
    orig = getattr(E, name)

    def f(*a, **k):
        set_phase(enter)
        try:
            return orig(*a, **k)
        finally:
            set_phase(leave)

    f.__name__ = name
    setattr(E, name, f)


wrap("representatives", "representatives", "pre-export")
wrap("quotient_data", "export", "setup")
wrap("block_tables", "block_tables", "gvecs")
wrap("order_walk", "order_walk", "pre-products")
import pickle

orig_bp = E.block_products


def bp(gvecs, gchar, one_pos, walk, lay, d, p, wanted=None):
    """block_products, with an optional on-disk memo of its return value (wrapper checkpoint, E unedited)."""
    set_phase("products")
    try:
        if cache and os.path.exists(cache):
            with open(cache, "rb") as f:
                return pickle.load(f)
        out = orig_bp(gvecs, gchar, one_pos, walk, lay, d, p, wanted)
        if cache:
            set_phase("products-save")
            with open(cache + ".part", "wb") as f:
                pickle.dump(out, f, protocol=5)
            os.replace(cache + ".part", cache)
        return out
    finally:
        set_phase("stack")
        if stop_after == "products":
            events.write(json.dumps({"stop_after": "products"}) + "\n")
            events.flush()
            raise SystemExit(0)


E.block_products = bp

gen_calls = []
orig_gb = E.generator_blocks


def gb(g, chi, one_pos, walk, lay, p):
    t = time.time()
    reset_hwm()
    r0 = proc.memory_info().rss
    out = orig_gb(g, chi, one_pos, walk, lay, p)
    rec = {"chi": chi, "s": round(time.time() - t, 2), "bytes": sum(v.nbytes for v in out.values()),
           "hwm_minus_rss0_mib": round((fold() * 1024 - r0) / 2**20, 1)}
    gen_calls.append(rec)
    events.write(json.dumps({"gen": rec}) + "\n")
    events.flush()
    return out


E.generator_blocks = gb

orig_init = E.Echelon.__init__


def init(self, ncols, p):
    orig_init(self, ncols, p)
    echelons.append(self)
    self.blk = len(echelons) - 1


E.Echelon.__init__ = init
orig_insert = E.Echelon.insert
ins_log = []
closure_started = [False]


def insert(self, X, chunk):
    if not closure_started[0]:
        closure_started[0] = True
        set_phase("closure+final")
    if keep is not None and self.blk not in keep:
        return orig_insert(self, X[:0], chunk)
    t = time.time()
    reset_hwm()
    r0 = proc.memory_info().rss
    rank0 = len(self.piv)
    out = orig_insert(self, X, chunk)
    rec = (self.blk, len(X), self.ncols, rank0, len(self.piv), round(time.time() - t, 3),
           (fold() * 1024 - r0) // 2**20)
    ins_log.append(rec)
    events.write(json.dumps({"ins": rec}) + "\n")
    events.flush()
    return out


E.Echelon.insert = insert

split = {"ctor_s": 0.0, "rref_s": 0.0, "entries_s": 0.0, "matmul_s": 0.0, "ctor_entries": 0, "rref_calls": 0,
         "rref_rows": 0, "rref_cols": 0, "rref_flop_rc2": 0, "matmul_flop": 0, "entries_n": 0}
if use_split:
    real_flint = E.flint

    class RProxy:
        def __init__(self, r):
            self.r = r

        def entries(self):
            t = time.time()
            out = self.r.entries()
            split["entries_s"] += time.time() - t
            split["entries_n"] += len(out)
            return out

        def __getitem__(self, k):
            return self.r[k]

        def __getattr__(self, n):
            return getattr(self.r, n)

    class MProxy:
        def __init__(self, m, rows, cols):
            self.m, self.rows, self.cols = m, rows, cols

        def rref(self):
            t = time.time()
            r, rk = self.m.rref()
            split["rref_s"] += time.time() - t
            split["rref_calls"] += 1
            split["rref_rows"] += self.rows
            split["rref_cols"] += self.cols
            split["rref_flop_rc2"] += self.rows * self.rows * self.cols
            return RProxy(r), rk

        def __setitem__(self, k, v):
            self.m[k] = v

        def __getitem__(self, k):
            return self.m[k]

        def __getattr__(self, n):
            return getattr(self.m, n)

    class FlintProxy:
        def nmod_mat(self, rows, cols, *a):
            t = time.time()
            m = real_flint.nmod_mat(rows, cols, *a)
            split["ctor_s"] += time.time() - t
            split["ctor_entries"] += rows * cols
            return MProxy(m, rows, cols)

        def __getattr__(self, n):
            return getattr(real_flint, n)

    E.flint = FlintProxy()
    orig_emm = E.exact_mod_matmul

    def emm(A, B, p):
        t = time.time()
        out = orig_emm(A, B, p)
        split["matmul_s"] += time.time() - t
        split["matmul_flop"] += 2 * A.shape[0] * A.shape[1] * B.shape[1]
        return out

    E.exact_mod_matmul = emm
if use_tm:
    tracemalloc.start()
reset_hwm()
import signal


prof = None


def on_term(signum, frame):
    if prof is not None:
        prof.disable()
        import pstats

        with open(os.path.join(outdir, tag + ".prof.txt"), "w") as pf:
            pstats.Stats(prof, stream=pf).sort_stats("tottime").print_stats(25)
    set_phase("terminated")
    events.write(json.dumps({"terminated": signum, "t": round(time.time() - T0, 1)}) + "\n")
    events.flush()
    os._exit(143)


signal.signal(signal.SIGTERM, on_term)
th = threading.Thread(target=sampler, daemon=True)
th.start()
sys.argv = ["fiber_rank_v11.py", *engine_args]
import contextlib
import io

buf = io.StringIO()
rc = 0
try:
    with contextlib.redirect_stdout(buf):
        if use_prof:
            import cProfile
            import pstats

            global_prof = cProfile.Profile()
            prof = global_prof
            try:
                prof.runcall(E.main)
            finally:
                with open(os.path.join(outdir, tag + ".prof.txt"), "w") as pf:
                    pstats.Stats(prof, stream=pf).sort_stats("tottime").print_stats(25)
        else:
            E.main()
except SystemExit as e:
    rc = e.code if isinstance(e.code, int) else 1
    print("SystemExit:", e.code, file=sys.stderr)
set_phase("end")
stop.set()
th.join()
rss_log.close()
open(os.path.join(outdir, tag + ".json"), "w").write(buf.getvalue())
final_w = [{"blk": e.blk, "rows": int(e.B.shape[0]), "cols": int(e.ncols), "bytes": int(e.B.nbytes)} for e in echelons]
rec = {
    "tag": tag, "args": engine_args, "rc": rc, "tracemalloc": use_tm, "keep_blocks": sorted(keep) if keep else None,
    "total_wall_s": round(time.time() - T0, 1), "stages": stages, "generator_blocks_calls": gen_calls,
    "final_echelons": final_w, "n_inserts": len(ins_log), "split": split,
    "tree_peak_kib_overall": max(phase_tree_peak.values(), default=0) // 1024,
}
open(os.path.join(outdir, tag + ".stages.json"), "w").write(json.dumps(rec, indent=1))
open(os.path.join(outdir, tag + ".inserts.json"), "w").write(json.dumps(ins_log))
os._exit(rc) if False else None
sys.exit(rc)
