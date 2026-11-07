"""C1 mechanism: static (config-independent) shifter errors fitted on one slot orientation and predicted on the other.

Observation model per iteration i: counts_i ~ Multinomial(N_i, q_i), q_im proportional to eta_m P_im(phi + delta) + b_m,
P from the compiled mesh. delta variants: none; static additive offset per shifter (126, ridge); static gain per shifter
(126, ridge); one global gain; one global coupler-angle shift. Fit on the iterations of one orientation (plus anchors and
darks, which carry both), score on the sign/null levels of the other orientation (held out)."""

from pathlib import Path

import numpy as np
from c1_common import MIRROR, an, mirror_table, observed_rows, rows_from_probs, settings, signed_diffs
from c1_mesh import PAIRS, cached, propagate
from scipy.optimize import least_squares

from parallel import ordered_map

HERE = Path(__file__).resolve().parent

kinds, lo, TH, PH, PERF = cached(PAIRS, "pairs")
ROWS = observed_rows()
C = np.array([r["port_counts"] for r in ROWS], float)
N = C.sum(1)
ORI = np.array([s["orientation"] for s in settings])
ROLE = np.array([s["role"] for s in settings])
NPS, NBS = PH.shape[1], TH.shape[1]
CFG = list(range(52))  # config used for the counts of iteration i (identity unless shuffled)
SIG_PRIOR = {"offset": 0.05, "gain": 0.02}
COMMON = np.array(an.mode_efficiency_fit(ROWS, settings))


def n_params(model):
    return {"none": 0, "offset": NPS, "gain": NPS, "gain1": 1, "theta1": 1}[model]


def probs(model, x, i):
    """P of the compiled config CFG[i] for a batch of model parameters x (B, n)."""
    i = CFG[i]
    B = x.shape[0]
    if model == "none":
        return propagate(kinds, lo, TH[i], PH[i], dph=np.zeros((B, NPS)))
    if model == "offset":
        return propagate(kinds, lo, TH[i], PH[i], dph=x)
    if model == "gain":
        return propagate(kinds, lo, TH[i], PH[i], dph=x * PH[i][None, :])
    if model == "gain1":
        return propagate(kinds, lo, TH[i], PH[i], dph=x[:, :1] * PH[i][None, :])
    if model == "theta1":
        return propagate(kinds, lo, TH[i], PH[i], dph=np.zeros((B, NPS)), dth=np.repeat(x[:, :1], NBS, axis=1))
    raise ValueError(model)


def q_of(model, x, a, c, i):
    """Mode probabilities q (B, 12) from model params x, log-efficiency a (12), log-background c (12)."""
    P = probs(model, x, i)
    w = np.exp(a)[None, :] * P + 1e-4 * np.exp(c)[None, :]
    return w / w.sum(1, keepdims=True)


def unpack(model, theta):
    n = n_params(model)
    return theta[:n], theta[n : n + 12], theta[n + 12 : n + 24]


def residual(theta, model, train):
    x, a, c = unpack(model, theta)
    out = []
    for i in train:
        q = q_of(model, x[None, :], a, c, i)[0]
        e = N[i] * q
        out.append((C[i] - e) / np.sqrt(np.maximum(e, 1.0) + 1.0))
    reg = [x / SIG_PRIOR.get(model, 0.1), 0.01 * a, 0.3 * c]
    return np.concatenate(out + reg)


def jac(theta, model, train):
    n = n_params(model)
    m = len(theta)
    base = residual(theta, model, train)
    # batched finite differences over parameters: x-parameters through the batch propagate, a and c analytically-cheap loops
    h = 1e-6
    thetas = np.repeat(theta[None, :], m, axis=0)
    thetas[np.arange(m), np.arange(m)] += h
    X = thetas[:, :n]
    A = thetas[:, n : n + 12]
    Cc = thetas[:, n + 12 :]
    pieces = []
    for i in train:
        if n:
            P = probs(model, X, i)
        else:
            P = np.repeat(probs("none", np.zeros((1, 0)), i), m, axis=0)
        w = np.exp(A) * P + 1e-4 * np.exp(Cc)
        q = w / w.sum(1, keepdims=True)
        e = N[i] * q
        pieces.append((C[i][None, :] - e) / np.sqrt(np.maximum(e, 1.0) + 1.0))
    reg = np.concatenate([X / SIG_PRIOR.get(model, 0.1), 0.01 * A, 0.3 * Cc], axis=1)
    full = np.concatenate([*pieces, reg], axis=1)
    return ((full - base[None, :]) / h).T


def fit(task):
    global CFG
    model, train_mode, perm = task
    CFG = list(range(52)) if perm is None else list(perm)
    if train_mode == "o0":
        train = [i for i in range(52) if ORI[i] == 0 or ROLE[i] in ("anchor", "dark")]
    elif train_mode == "o1":
        train = [i for i in range(52) if ORI[i] == 1 or ROLE[i] in ("anchor", "dark")]
    else:
        train = list(range(52))
    theta0 = np.concatenate([np.zeros(n_params(model)), np.log(COMMON).tolist() + [0, 0, 0], np.zeros(12)])
    sol = least_squares(residual, theta0, jac=jac, args=(model, train), method="trf", max_nfev=60, x_scale=1.0)
    x, a, c = unpack(model, sol.x)
    CFG = list(range(52))
    P = np.array([q_of(model, x[None, :], a, c, i)[0] for i in range(52)])
    # held-out score on sign/null readings of the orientation not in train
    rows = rows_from_probs(P)
    keys, d_model, tb_model, _ = signed_diffs(rows)
    return {
        "model": model,
        "train": train_mode,
        "perm": perm,
        "P": P,
        "x": x,
        "nfev": sol.nfev,
        "cost": float(sol.cost),
        "train_n": len(train),
    }


def levels_of(rows):
    t, _ = mirror_table(rows)
    return {(k, o): t[k][o][2] for k in t for o in (0, 1)}


def main():
    obs = levels_of(ROWS)
    tasks = [(m, t, None) for m in ("none", "gain1", "theta1", "offset", "gain") for t in ("o0", "o1", "all")]
    out = ordered_map(fit, tasks, min_items=1)
    keys = sorted({k for k, _ in obs})
    d_obs = np.array([obs[(k, 0)] - obs[(k, 1)] for k in keys])
    print(
        "model  train  cost  | held-out rms of level residual (obs - model) on the unseen orientation; corr(d_obs, d_pred_holdout)"
    )
    results = {}
    for o in out:
        lev = levels_of(rows_from_probs(o["P"]))
        res = {}
        for ho in (0, 1):
            r = np.array([obs[(k, ho)] - lev[(k, ho)] for k in keys])
            res[ho] = r
        train = o["train"]
        if train == "o0":
            held = 1
        elif train == "o1":
            held = 0
        else:
            held = None
        # predicted d where the held-out orientation level is replaced by the model prediction
        if held is None:
            rms_in = np.sqrt(np.mean(np.r_[res[0], res[1]] ** 2))
            txt = f"in-sample level rms {rms_in:.4f}"
            dpred = np.array([lev[(k, 0)] - lev[(k, 1)] for k in keys])
            corr = np.corrcoef(d_obs, dpred)[0, 1]
            txt += f"; corr(d_obs, d_model) {corr:+.3f}; |d_model| max {abs(dpred).max():.4f}; failing flagged {(abs(dpred) > MIRROR).sum()}"
        else:
            rms_h = np.sqrt(np.mean(res[held] ** 2))
            rms_t = np.sqrt(np.mean(res[1 - held] ** 2))
            dpred = np.array([(obs[(k, 0)] - lev[(k, 1)]) if held == 1 else (lev[(k, 0)] - obs[(k, 1)]) for k in keys])
            dmod = np.array([lev[(k, 0)] - lev[(k, 1)] for k in keys])
            corr = np.corrcoef(d_obs, dmod)[0, 1]
            txt = f"train level rms {rms_t:.4f}; HELD-OUT level rms {rms_h:.4f}; corr(d_obs, d_model) {corr:+.3f}; model |d| max {abs(dmod).max():.4f}; flags {(abs(dmod) > MIRROR).sum()} (failing flagged {((abs(dmod) > MIRROR) & (abs(d_obs) > MIRROR)).sum()}/9)"
        results[(o["model"], train)] = txt
        print(f"{o['model']:7s} {train:4s} cost {o['cost']:9.1f} nfev {o['nfev']:3d} | {txt}", flush=True)
    np.savez(HERE / "c1_static.npz", **{f"{o['model']}_{o['train']}": o["P"] for o in out})


if __name__ == "__main__":
    main()
