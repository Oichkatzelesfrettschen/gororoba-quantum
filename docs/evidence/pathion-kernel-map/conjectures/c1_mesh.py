"""Compiled-mesh extraction and vectorized single-photon propagation for the Ascella coset-block runs.

Each iteration's result_fields.computed_circuit is the circuit the service compiled and ran: a 12-mode rectangular mesh
of BS.Rx (theta near 1.45 rad, the chip's own coupler angles) and PS elements. A single photon from mode 0 leaves in
mode m with probability |U[m, 0]|^2; the functions here evaluate that column for batches of perturbed parameters.
"""

import json
import sys
from pathlib import Path

import numpy as np
from perceval.serialization import deserialize

ROOT = Path(__file__).resolve().parents[4]
PAIRS = ROOT / "results/quandela/runs/2026-11-07T003204Z-qpu_ascella-ascella_pathion_coset_block_pairs-job-00"
FOUR = ROOT / "results/quandela/runs/2026-11-06T215343Z-qpu_ascella-ascella_pathion_four_term_blocks-job-00"
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))


def extract(run: Path):
    """Topology (kind, lo-mode) list, BS thetas and PS phases per iteration."""
    results = json.loads((run / "results.json").read_bytes())
    topo = None
    thetas, phis, perf = [], [], []
    for entry in results["iterations"]:
        circ = deserialize(entry["result_fields"]["computed_circuit"])
        this, th, ph = [], [], []
        for rng, comp in circ._components:
            kind = type(comp).__name__
            this.append((kind, rng[0]))
            params = comp.get_parameters(all_params=True)
            if kind == "BS":
                th.append(float(params[0]))
                if comp._convention.name != "Rx":
                    raise ValueError("BS convention is not Rx")
            else:
                ph.append(float(params[0]))
        if topo is None:
            topo = this
        elif topo != this:
            raise ValueError("topology differs between iterations")
        thetas.append(th)
        phis.append(ph)
        perf.append(entry["result_fields"]["physical_perf"])
    return topo, np.array(thetas), np.array(phis), np.array(perf)


def cached(run: Path, name: str):
    f = HERE / f"mesh_{name}.npz"
    if not f.exists():
        topo, th, ph, perf = extract(run)
        np.savez(f, kinds=np.array([k for k, _ in topo]), lo=np.array([m for _, m in topo]), th=th, ph=ph, perf=perf)
    d = np.load(f)
    return d["kinds"], d["lo"], d["th"], d["ph"], d["perf"]


def propagate(kinds, lo, th, ph, dph=None, dth=None, modes=12):
    """Probability vectors (batch, 12) of a photon from mode 0. th (nBS,), ph (nPS,); dph (batch, nPS), dth (batch, nBS)."""
    batch = 1 if dph is None and dth is None else (dph if dph is not None else dth).shape[0]
    amp = np.zeros((batch, modes), dtype=complex)
    amp[:, 0] = 1.0
    ib = ip = 0
    for kind, m in zip(kinds, lo, strict=True):
        if kind == "BS":
            t = th[ib] + (0.0 if dth is None else dth[:, ib])
            ib += 1
            c, s = np.cos(t / 2), 1j * np.sin(t / 2)
            a, b = amp[:, m].copy(), amp[:, m + 1].copy()
            amp[:, m] = c * a + s * b
            amp[:, m + 1] = s * a + c * b
        else:
            p = ph[ip] + (0.0 if dph is None else dph[:, ip])
            ip += 1
            amp[:, m] *= np.exp(1j * p)
    return np.abs(amp) ** 2


if __name__ == "__main__":
    import perceval as pcvl  # noqa: F401

    for run, name in ((PAIRS, "pairs"), (FOUR, "four")):
        k, lo, th, ph, perf = cached(run, name)
        print(name, th.shape, ph.shape)
    k, lo, th, ph, perf = cached(PAIRS, "pairs")
    cases = json.loads((PAIRS / "cases.json").read_bytes())
    err = 0
    for i, s in enumerate(cases["settings"]):
        p = propagate(k, lo, th[i], ph[i])[0]
        err = max(
            err,
            np.abs(
                p - np.array(s["operator"]["real"])[:, 0] ** 2 - np.array(s["operator"]["imaginary"])[:, 0] ** 2
            ).max(),
        )
    print("max |P_compiled - P_ideal|", err)
