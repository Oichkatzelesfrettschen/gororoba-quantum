"""Cost per stage of Echelon.insert's marshaling path at given (rows, free) sizes, with the engine's own statements.

Usage: microbench.py ROWS FREE

Random residues mod 32009; one pass of the lines 325-331 sequence of fiber_rank_v11.Echelon.insert.
Prints seconds per statement and peak RSS growth, to scale the closure transient and time to degree-6 sizes.
"""

import resource
import sys
import time

import flint
import numpy as np

rows, free, p = int(sys.argv[1]), int(sys.argv[2]), 32009
rng = np.random.default_rng(12345)
Y = rng.integers(0, p, size=(rows, free)).astype(np.float64)
t = time.time()
Z = Y.astype(np.int64)
t_astype = time.time() - t
t = time.time()
L = Z.ravel().tolist()
t_tolist = time.time() - t
t = time.time()
M = flint.nmod_mat(Z.shape[0], Z.shape[1], L, p)
t_ctor = time.time() - t
del L
t = time.time()
R, rk = M.rref()
t_rref = time.time() - t
t = time.time()
E = R.entries()
t_entries = time.time() - t
t = time.time()
ints = [int(x) for x in E]
t_int = time.time() - t
del E
t = time.time()
Rn = np.array(ints, dtype=np.float64).reshape(Z.shape)[:rk]
t_np = time.time() - t
print(
    {
        "rows": rows,
        "free": free,
        "rank": rk,
        "entries": rows * free,
        "astype_s": round(t_astype, 2),
        "tolist_s": round(t_tolist, 2),
        "nmod_mat_s": round(t_ctor, 2),
        "rref_s": round(t_rref, 2),
        "entries_s": round(t_entries, 2),
        "int_list_s": round(t_int, 2),
        "np_array_s": round(t_np, 2),
        "maxrss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024,
    }
)
