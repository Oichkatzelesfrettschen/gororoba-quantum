"""Nested multinomial log-linear test of a setting-specific change between two runs of identical circuits.

Counts n[r, s, m] hold run r in {A, B}, setting s and detector mode m. Three nested models of the table, each fixed
by margins:

- homogeneity: the two runs share every setting's mode distribution (margins run x setting and setting x mode);
- common factor: the runs differ by one factor per mode shared by all settings, the no-three-factor-interaction
  model (margins run x mode, run x setting and setting x mode), fitted by iterative proportional fitting;
- saturated: every run and setting has its own mode distribution.

The deviance of the common-factor model against the saturated one is the likelihood-ratio test of a setting-specific
change; its Pearson counterpart on the same fit is the calibration check for sparse cells. The degrees of freedom
are the cell count minus the rank of the log-linear design, so a mode absent from a setting costs nothing.
"""

from __future__ import annotations

from typing import Any

import numpy as np

MAX_SWEEPS = 5000
RELATIVE_TOLERANCE = 1e-12


def fit_common_factor(n: np.ndarray) -> tuple[np.ndarray, int]:
    """Maximum-likelihood fit of the no-three-factor-interaction model by iterative proportional fitting.

    n has axes (run, setting, mode). Cells of a setting whose two runs both read zero in a mode stay structurally
    zero. Returns the fitted counts and the number of sweeps; a table that does not converge raises, so a stalled
    fit never enters a p-value.
    """
    present = n.sum(axis=0) > 0
    fit = np.where(present[None, :, :], 1.0, 0.0) * np.ones_like(n)
    run_mode = n.sum(axis=1)
    run_setting = n.sum(axis=2)
    setting_mode = n.sum(axis=0)
    scale = max(1.0, float(n.sum()))
    for sweep in range(1, MAX_SWEEPS + 1):
        current = fit.sum(axis=1)
        fit *= np.where(current[:, None, :] > 0, run_mode[:, None, :] / np.maximum(current[:, None, :], 1e-300), 0.0)
        current = fit.sum(axis=2)
        fit *= np.where(current[:, :, None] > 0, run_setting[:, :, None] / np.maximum(current[:, :, None], 1e-300), 0.0)
        current = fit.sum(axis=0)
        fit *= np.where(
            current[None, :, :] > 0, setting_mode[None, :, :] / np.maximum(current[None, :, :], 1e-300), 0.0
        )
        gap = max(
            float(np.abs(fit.sum(axis=1) - run_mode).max()),
            float(np.abs(fit.sum(axis=2) - run_setting).max()),
            float(np.abs(fit.sum(axis=0) - setting_mode).max()),
        )
        if gap <= RELATIVE_TOLERANCE * scale:
            return fit, sweep
    raise RuntimeError(f"iterative proportional fitting did not converge in {MAX_SWEEPS} sweeps")


def design_rank(present: np.ndarray, with_run_mode: bool) -> tuple[int, int]:
    """(cells, rank) of the log-linear design over the present (setting, mode) cells of both runs."""
    settings, modes = present.shape
    index: dict[tuple[str, int, int], int] = {}
    rows: list[list[int]] = []
    for run in range(2):
        for s in range(settings):
            for m in range(modes):
                if not present[s, m]:
                    continue
                keys = [("rs", run, s), ("sm", s, m)]
                if with_run_mode:
                    keys.append(("rm", run, m))
                rows.append([index.setdefault(key, len(index)) for key in keys])
    design = np.zeros((len(rows), len(index)))
    for i, columns in enumerate(rows):
        design[i, columns] = 1.0
    return len(rows), int(np.linalg.matrix_rank(design))


def nested_residual(
    a: np.ndarray, b: np.ndarray, min_total: int = 200, exclude: tuple[int, ...] = ()
) -> dict[str, Any]:
    """Setting-specific change between runs a and b (settings x modes counts), by deviance and Pearson of the fit.

    The settings kept are those where both runs hold at least min_total clicks, the modes those with a click in
    some kept setting, matching the selection of the generalized Cochran-Mantel-Haenszel statistic.
    """
    modes = a.shape[1]
    allowed = np.array([m not in exclude for m in range(modes)])
    a, b = a * allowed, b * allowed
    keep = [i for i in range(a.shape[0]) if a[i].sum() >= min_total and b[i].sum() >= min_total]
    cols = np.flatnonzero((a[keep] + b[keep]).sum(axis=0) > 0)
    table = np.stack([a[keep][:, cols], b[keep][:, cols]])
    fit, sweeps = fit_common_factor(table)
    positive = table > 0
    deviance = 2.0 * float((table[positive] * np.log(table[positive] / fit[positive])).sum())
    cells_fit = fit > 0
    pearson = float((((table - fit) ** 2)[cells_fit] / fit[cells_fit]).sum())
    present = table.sum(axis=0) > 0
    cells, rank_common = design_rank(present, with_run_mode=True)
    _, rank_homogeneous = design_rank(present, with_run_mode=False)
    return {
        "deviance": deviance,
        "pearson": pearson,
        "dof": cells - rank_common,
        "homogeneity_dof": cells - rank_homogeneous,
        "settings": len(keep),
        "modes": int(len(cols)),
        "sweeps": sweeps,
    }
