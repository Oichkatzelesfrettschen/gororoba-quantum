import resource
import time

import numpy as np
from flint import ctx
from numpy_flint_arb import allow_input
from numpy_flint_arb import np as xp

if __name__ == "__main__":
    ctx.prec = 128
    for m, n in ((12, 6), (24, 12), (48, 24), (96, 48)):
        # deterministic entries: memory, not the values, is what scales with the side
        a = (np.add.outer(np.arange(m), 3 * np.arange(n)) % 7 + 1.0) / 8
        t0 = time.perf_counter()
        with allow_input(interval=True, float=True):
            aa = xp.asarray(a)
        at = xp.linalg.matrix_transpose(aa)
        normal = xp.linalg.matmul(at, aa)
        peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
        print(
            f"{m}x{n}: matmul {time.perf_counter() - t0:.2f}s peak RSS {peak:.0f} MiB result shape {np.shape(normal)}",
            flush=True,
        )
